import unittest
from unittest.mock import patch
from types import SimpleNamespace as NS

from dongle_go.transport import CommandRejected, TransportError
from dongle_go.usb_transport import USBATTransport, enumerate_ports


class Timeout(Exception):
    pass


class Interface(list):
    bAlternateSetting = 0
    bInterfaceClass = 255
    bInterfaceSubClass = 0
    bInterfaceProtocol = 0
    bInterfaceNumber = 2

    def __init__(self, addresses=(3, 132)):
        super().__init__(NS(bEndpointAddress=a, bmAttributes=2) for a in addresses)


class Device:
    bus, address, idVendor, idProduct = 1, 2, 0x2CA3, 0x4006

    def __init__(self, chunks):
        self.chunks = list(chunks)
        self.writes = []
        self.interfaces = [Interface()]
        self.short = False

    def get_active_configuration(self):
        return self.interfaces

    def read(self, endpoint, size, timeout):
        if not self.writes or not self.chunks:
            raise Timeout()
        return self.chunks.pop(0)

    def write(self, endpoint, data, timeout):
        self.writes.append((endpoint, data))
        return len(data) - int(self.short)


class USBTests(unittest.TestCase):
    def setup_transport(self, chunks=()):
        device = Device(chunks)
        events = []
        core = NS(find=lambda **kw: [device], USBTimeoutError=Timeout)
        util = NS(claim_interface=lambda *a: events.append('claim'),
                  release_interface=lambda *a: events.append('release'),
                  dispose_resources=lambda *a: events.append('dispose'))
        ticks = iter(i / 100 for i in range(100000))
        transport = USBATTransport('usb://1/2', usb_core=core, usb_util=util,
                                   timeout=.2, clock=lambda: next(ticks))
        return transport, device, events, core

    def test_discovery_does_not_read_serial_number(self):
        _, _, _, core = self.setup_transport()
        self.assertEqual(enumerate_ports(usb_core=core), [dict(port='usb://1/2',
            candidate=True, vid=0x2CA3, pid=0x4006, serial_number=None)])

    def test_fragmented_exchange_and_cleanup(self):
        t, d, events, _ = self.setup_transport([b'ATI\r\nEG25\r\nO', b'K\r\n'])
        with t:
            self.assertEqual(t.query('ATI'), ['EG25'])
        self.assertEqual(d.writes, [(3, b'ATI\r')])
        self.assertEqual(events, ['claim', 'release', 'dispose'])

    def test_unknown_diagnostic_and_ambiguous_interfaces_never_probed(self):
        for interfaces in ([Interface((1, 129))], [Interface(), Interface()]):
            t, d, events, _ = self.setup_transport()
            d.interfaces = interfaces
            with self.assertRaisesRegex(TransportError, 'unknown or ambiguous'):
                with t:
                    pass
            self.assertEqual(d.writes, [])
            self.assertNotIn('claim', events)

    def test_nonvendor_interface_never_probed(self):
        t, d, _, _ = self.setup_transport()
        d.interfaces[0].bInterfaceClass = 2
        with self.assertRaises(TransportError):
            with t:
                pass
        self.assertFalse(d.writes)

    def test_writes_and_arbitrary_commands_disabled(self):
        t, d, _, _ = self.setup_transport()
        with t:
            for action in (lambda: t.set_usbnet(1), t.reboot,
                           lambda: t.query('ATI\rAT+CFUN=1,1')):
                with self.assertRaises(TransportError):
                    action()
        self.assertFalse(d.writes)

    def test_failures_poison_channel(self):
        for chunks, message in [([b'partial'], 'timed out'),
                                ([b'x' * 33000], 'size limit')]:
            t, d, events, _ = self.setup_transport(chunks)
            with t:
                with self.assertRaisesRegex(TransportError, message):
                    t.query('ATI')
                with self.assertRaisesRegex(TransportError, 'reopening'):
                    t.query('ATI')
            self.assertEqual(len(d.writes), 1)
            self.assertIn('release', events)

    def test_command_rejection_does_not_poison(self):
        for response in (b'ERROR\r\n', b'+CME ERROR: 10\r\n'):
            t, d, _, _ = self.setup_transport([response])
            with t:
                with self.assertRaises(CommandRejected):
                    t.query('AT+CPIN?')
                self.assertFalse(t.poisoned)
            self.assertEqual(len(d.writes), 1)

    def test_bundled_backend_used_for_discovery_and_open(self):
        _, d, _, core = self.setup_transport()
        calls, backend = [], object()
        core.find = lambda **kw: calls.append(kw) or [d]
        util = NS(claim_interface=lambda *a: None, release_interface=lambda *a: None,
                  dispose_resources=lambda *a: None)
        with patch('dongle_go.usb_transport._modules', return_value=(core, util, backend)):
            enumerate_ports()
            with USBATTransport('usb://1/2'):
                pass
        self.assertEqual(len(calls), 2)
        self.assertTrue(all(c['backend'] is backend for c in calls))

    def test_injection_does_not_load_usb_dependencies(self):
        t, _, _, core = self.setup_transport()
        with patch('dongle_go.usb_transport._modules', side_effect=AssertionError('loaded')):
            enumerate_ports(usb_core=core)
            with t:
                self.assertFalse(t.supports_configuration)

    def test_short_write(self):
        t, d, _, _ = self.setup_transport()
        d.short = True
        with t, self.assertRaisesRegex(TransportError, 'Incomplete'):
            t.query('ATI')

    def test_exclusive_open_and_release(self):
        t, _, _, _ = self.setup_transport()
        second, _, _, _ = self.setup_transport()
        with t:
            with self.assertRaisesRegex(TransportError, 'already in use'):
                second.__enter__()
        with second:
            pass

    def test_busy_drain_is_bounded_without_write(self):
        t, d, _, _ = self.setup_transport()
        calls = []
        d.read = lambda *a, **kw: calls.append(1) or b'URC\r\n'
        with t, self.assertRaisesRegex(TransportError, 'busy'):
            t.query('ATI')
        self.assertEqual(len(calls), 8)
        self.assertFalse(d.writes)

    def test_bad_address_and_timeout(self):
        for address in ('usb://a/2', '/dev/ttyUSB0', 'usb://1/2/3'):
            with self.assertRaises(TransportError):
                USBATTransport(address)
        for timeout in (0, -1, float('nan'), float('inf')):
            with self.assertRaises(TransportError):
                USBATTransport('usb://1/2', timeout=timeout)


if __name__ == '__main__':
    unittest.main()
