import tempfile
import subprocess
import sys
import os
from unittest.mock import patch
import unittest
from pathlib import Path

from dongle_go.core import CoreError, DEMO_PORT, DongleService, _LOCK, hardware_ports, hardware_transport
from dongle_go.profiles import Profile
from dongle_go.transport import CommandRejected, TransportError


class FakeModem:
    supports_configuration = True
    mode = 0
    fail_set = False
    fail_reboot = False
    no_sim = False
    reboots = 0
    def __init__(self, port):
        self.port = port
    def __enter__(self):
        return self
    def __exit__(self, *_):
        pass
    def query(self, command):
        if command == 'AT+CPIN?' and type(self).no_sim:
            raise CommandRejected('Module rejected the command.')
        return {'ATI': ['Manufacturer: QUECTEL'], 'AT+CGMM': ['EG25'],
                'AT+CGMR': ['FW1'], 'AT+CPIN?': ['+CPIN: READY'],
                'AT+CEREG?': ['+CEREG: 0,1'], 'AT+CGREG?': ['+CGREG: 0,0'],
                'AT+QCFG="usbnet"': [f'+QCFG: "usbnet",{type(self).mode}'],
                'AT+CGDCONT?': ['+CGDCONT: 1,"IP","private.apn"']}[command]
    def set_usbnet(self, mode):
        if type(self).fail_set:
            raise TransportError('Rejected')
        type(self).mode = mode
    def reboot(self):
        type(self).reboots += 1
        if type(self).fail_reboot:
            raise TransportError('Disconnected')


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'recovery.json'
        FakeModem.mode, FakeModem.fail_set, FakeModem.fail_reboot = 0, False, False
        FakeModem.no_sim, FakeModem.reboots = False, 0
        self.port = {'port': 'mock0', 'serial_number': 'unique', 'candidate': True,
                     'vid': 0x2ca3, 'pid': 0x4006, 'interface': 'AT'}
        self.profile = Profile('test', 'Manufacturer: QUECTEL', 'EG25', 'FW1',
                               {'mac': 1, 'ipad': 1, 'windows': 3}, 'TEST FIXTURE',
                               vid=0x2ca3, pid=0x4006, at_interfaces=('AT',))

    def service(self, verified=False, **kwargs):
        return DongleService(transport_factory=FakeModem, port_provider=lambda: [self.port],
                             profiles=(self.profile,) if verified else (),
                             snapshot_path=self.path, **kwargs)

    def test_demo_never_calls_hardware(self):
        def forbidden(*args):
            self.fail('demo touched hardware')
        service = DongleService(True, transport_factory=forbidden, port_provider=forbidden)
        self.assertTrue(service.apply(DEMO_PORT, 'mac')['configured'])
        self.assertFalse(service.apply(DEMO_PORT, 'mac')['internet_verified'])
        self.assertTrue(service.restore(DEMO_PORT)['restored'])
        self.assertEqual(service.inspect(DEMO_PORT)['usbnet'], 0)

    def test_unknown_firmware_rejects_without_snapshot_or_write(self):
        service = self.service()
        self.assertFalse(service.inspect('mock0')['supported'])
        with self.assertRaises(CoreError) as error:
            service.apply('mock0', 'mac')
        self.assertEqual(error.exception.code, 'unsupported')
        self.assertEqual(FakeModem.mode, 0)
        self.assertFalse(self.path.exists())

    def test_profile_exact_firmware(self):
        self.profile = Profile('test', 'Manufacturer: QUECTEL', 'EG25', 'FW2', {'mac': 1}, 'fixture')
        with self.assertRaises(CoreError):
            self.service(True).apply('mock0', 'mac')

    def test_configure_and_restore_after_process_restart(self):
        result = self.service(True).apply('mock0', 'mac')
        self.assertTrue(result['configured'])
        self.assertFalse(result['internet_verified'])
        self.assertNotIn('private.apn', self.path.read_text())
        if os.name != 'nt':
            self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        self.assertTrue(self.service(True).restore('mock0')['restored'])
        self.assertEqual(FakeModem.mode, 0)

    def test_reboot_failure_preserves_recovery_and_never_success(self):
        FakeModem.fail_reboot = True
        service = self.service(True)
        with self.assertRaises(CoreError):
            service.apply('mock0', 'mac')
        self.assertTrue(self.path.exists())
        FakeModem.fail_reboot = False
        service.restore('mock0')
        self.assertEqual(FakeModem.mode, 0)

    def test_wrong_device_restore_rejected(self):
        service = self.service(True)
        service.apply('mock0', 'mac')
        self.port['serial_number'] = 'different'
        with self.assertRaises(CoreError) as error:
            service.restore('mock0')
        self.assertEqual(error.exception.code, 'identity_mismatch')

    def test_bounded_reconnect_missing_device(self):
        now = [0.0]
        service = self.service(True, clock=lambda: now[0],
                               sleep=lambda delay: now.__setitem__(0, now[0] + delay),
                               reconnect_timeout=1)
        with self.assertRaises(CoreError) as error:
            service._reconnect(dict(self.port, serial_number='missing'), 1)
        self.assertEqual(error.exception.code, 'reconnect_failed')
        self.assertLessEqual(now[0], 1)

    def test_single_operation_lock(self):
        _LOCK.acquire()
        try:
            with self.assertRaises(CoreError) as error:
                DongleService(True).inspect(DEMO_PORT)
            self.assertEqual(error.exception.code, 'busy')
        finally:
            _LOCK.release()

    def test_diagnostic_does_not_return_apn(self):
        result = self.service().inspect('mock0')
        self.assertTrue(result['apn_configured'])
        self.assertNotIn('private.apn', str(result))

    def test_missing_sim_is_diagnosable(self):
        FakeModem.no_sim = True
        self.assertEqual(self.service(True).inspect('mock0')['sim'], 'UNKNOWN')
        with self.assertRaises(CoreError) as error:
            self.service(True).apply('mock0', 'mac')
        self.assertEqual(error.exception.code, 'sim_not_ready')

    def test_profile_matches_usb_identity(self):
        self.port['vid'] = 1234
        with self.assertRaises(CoreError) as error:
            self.service(True).apply('mock0', 'mac')
        self.assertEqual(error.exception.code, 'unsupported')

    def test_repeat_apply_keeps_original_baseline(self):
        service = self.service(True)
        service.apply('mock0', 'mac')
        baseline = self.path.read_text()
        self.service(True).apply('mock0', 'windows')
        self.assertEqual(baseline, self.path.read_text())
        self.service(True).restore('mock0')
        self.assertEqual(FakeModem.mode, 0)

    def test_same_mode_still_reboots(self):
        FakeModem.mode = 1
        self.service(True).apply('mock0', 'mac')
        self.assertEqual(FakeModem.reboots, 1)

    def test_reconnect_selects_verified_at_interface(self):
        service = self.service(True)
        gps = dict(self.port, port='gps0', interface='GPS')
        service._ports = lambda: [gps, self.port]
        result = service.apply('mock0', 'mac')
        self.assertEqual(result['state']['port'], 'mock0')

    @unittest.skipIf(os.name == 'nt', 'Creating symlinks can require Windows administrator rights')
    def test_symlink_snapshot_temporary_never_overwrites_target(self):
        victim = Path(self.temp.name) / 'important'
        victim.write_text('keep me')
        self.path.with_suffix('.tmp').symlink_to(victim)
        with self.assertRaises(CoreError) as error:
            self.service(True).apply('mock0', 'mac')
        self.assertEqual(error.exception.code, 'snapshot_failed')
        self.assertEqual(victim.read_text(), 'keep me')
        self.assertEqual(FakeModem.mode, 0)

    def test_cross_process_lock(self):
        code = ('import sys; from dongle_go.core import DongleService; '
                's=DongleService(snapshot_path=sys.argv[1]); '
                'ctx=s._operation(); ctx.__enter__(); '
                'print("locked",flush=True); sys.stdin.readline(); ctx.__exit__(None,None,None)')
        child = subprocess.Popen([sys.executable, '-c', code, str(self.path)],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(), 'locked')
            with self.assertRaises(CoreError) as error:
                self.service(True).inspect('mock0')
            self.assertEqual(error.exception.code, 'busy')
        finally:
            child.communicate('\n', timeout=5)
        self.assertTrue(self.service(True).inspect('mock0')['supported'])

    def test_usb_and_serial_discovery_are_combined(self):
        with patch('dongle_go.core.enumerate_ports', return_value=[self.port]), \
             patch('dongle_go.usb_transport.enumerate_ports', return_value=[{'port': 'usb://1/2'}]):
            self.assertEqual(len(hardware_ports()), 2)

    def test_missing_usb_backend_does_not_hide_serial(self):
        with patch('dongle_go.core.enumerate_ports', return_value=[self.port]), \
             patch('dongle_go.usb_transport.enumerate_ports', side_effect=TransportError('missing')):
            self.assertEqual(hardware_ports(), [self.port])

    def test_transport_routes_by_protocol(self):
        from dongle_go.transport import ATTransport
        from dongle_go.usb_transport import USBATTransport
        self.assertIsInstance(hardware_transport('usb://1/2'), USBATTransport)
        self.assertIsInstance(hardware_transport('COM3'), ATTransport)

    def test_readonly_transport_rejected_even_with_profile(self):
        class ReadOnly(FakeModem):
            supports_configuration = False
        service = self.service(True)
        service._transport = ReadOnly
        with self.assertRaises(CoreError) as error:
            service.apply('mock0', 'mac')
        self.assertEqual(error.exception.code, 'read_only_transport')
        self.assertFalse(self.path.exists())

    def test_invalid_existing_snapshot_blocks_all_writes(self):
        import json
        self.service(True).apply('mock0', 'mac')
        saved = json.loads(self.path.read_text())
        for invalid in ('broken', 99, None, True):
            saved['usbnet'] = invalid
            self.path.write_text(json.dumps(saved))
            FakeModem.mode = 0
            with self.assertRaises(CoreError) as error:
                self.service(True).apply('mock0', 'mac')
            self.assertEqual(error.exception.code, 'invalid_snapshot')
            self.assertEqual(FakeModem.mode, 0)

    def test_invalid_original_mode_never_writes(self):
        FakeModem.mode = 99
        with self.assertRaises(CoreError) as error:
            self.service(True).apply('mock0', 'mac')
        self.assertEqual(error.exception.code, 'invalid_response')
        self.assertEqual(FakeModem.mode, 99)
        self.assertFalse(self.path.exists())

    def test_port_replacement_before_write_is_rejected(self):
        calls = [0]
        def enter(modem):
            calls[0] += 1
            if calls[0] == 2:
                self.port['serial_number'] = 'replacement'
            return modem
        with patch.object(FakeModem, '__enter__', enter):
            with self.assertRaises(CoreError) as error:
                self.service(True).apply('mock0', 'mac')
        self.assertEqual(error.exception.code, 'identity_mismatch')
        self.assertEqual(FakeModem.mode, 0)

    def test_same_port_changed_firmware_before_write_is_rejected(self):
        original_query = FakeModem.query
        calls = [0]
        def query(modem, command):
            if command == 'AT+CGMR':
                calls[0] += 1
                if calls[0] == 2:
                    return ['different firmware']
            return original_query(modem, command)
        with patch.object(FakeModem, 'query', query):
            with self.assertRaises(CoreError) as error:
                self.service(True).apply('mock0', 'mac')
        self.assertEqual(error.exception.code, 'identity_mismatch')
        self.assertEqual(FakeModem.mode, 0)

    def test_successful_restore_retires_baseline(self):
        service = self.service(True)
        service.apply('mock0', 'mac')
        service.restore('mock0')
        self.assertFalse(self.path.exists())
        self.assertFalse(service.status()['recovery_available'])

    def test_failed_snapshot_save_cleans_only_own_temporary(self):
        with patch('dongle_go.core.json.dump', side_effect=OSError('disk full')):
            with self.assertRaises(CoreError) as error:
                self.service(True).apply('mock0', 'mac')
        self.assertEqual(error.exception.code, 'snapshot_failed')
        self.assertFalse(self.path.with_suffix('.tmp').exists())
        self.assertEqual(FakeModem.mode, 0)
        self.assertTrue(self.service(True).apply('mock0', 'mac')['configured'])

    @unittest.skipIf(os.name == 'nt', 'Directory fsync is POSIX-specific')
    def test_directory_sync_failure_prevents_device_write(self):
        with patch.object(DongleService, '_sync_directory', side_effect=OSError('sync failure')):
            with self.assertRaises(CoreError) as error:
                self.service(True).apply('mock0', 'mac')
        self.assertEqual(error.exception.code, 'snapshot_failed')
        self.assertEqual(FakeModem.mode, 0)


if __name__ == '__main__':
    unittest.main()
