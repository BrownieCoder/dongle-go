"""Conservative setup workflow: inspect, qualify, snapshot, apply, re-inspect."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import threading
import time

from .profiles import VERIFIED_PROFILES, Profile, match_profile
from .transport import ATTransport, CommandRejected, TransportError, enumerate_ports

_LOCK = threading.Lock()
TARGETS = ('mac', 'windows', 'ipad')
DEMO_PORT = 'demo://dongle'


def hardware_ports():
    """Keep a working discovery backend usable if the other driver is absent."""
    from .usb_transport import enumerate_ports as usb_ports
    ports, errors = [], []
    for discover in (enumerate_ports, usb_ports):
        try:
            ports.extend(discover())
        except TransportError as exc:
            errors.append(exc)
    if len(errors) == 2:
        raise TransportError('Serial and USB discovery unavailable; check installed drivers.')
    return ports


def hardware_transport(port):
    if port.startswith('usb://'):
        from .usb_transport import USBATTransport
        return USBATTransport(port)
    return ATTransport(port)


class CoreError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class DongleService:
    def __init__(self, demo=False, *, transport_factory=hardware_transport,
                 port_provider=hardware_ports, profiles=VERIFIED_PROFILES,
                 snapshot_path=None, reconnect_timeout=25, clock=time.monotonic,
                 sleep=time.sleep):
        self.demo = bool(demo)
        self._transport, self._ports, self._profiles = transport_factory, port_provider, profiles
        self._path = Path(snapshot_path) if snapshot_path else Path.home() / '.dongle-go' / 'recovery.json'
        self._timeout, self._clock, self._sleep = reconnect_timeout, clock, sleep
        self._snapshot = None
        self._demo_mode = 0

    @contextmanager
    def _operation(self):
        if not _LOCK.acquire(blocking=False):
            raise CoreError('busy', 'Another operation is already running.')
        handle = None
        try:
            if not self.demo:
                try:
                    self._path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                    handle = os.fdopen(os.open(self._path.with_suffix('.lock'),
                                              os.O_RDWR | os.O_CREAT | getattr(os, 'O_NOFOLLOW', 0), 0o600), 'r+b')
                    if os.name == 'nt':
                        import msvcrt
                        handle.seek(0)
                        if not handle.read(1):
                            handle.write(b'0')
                            handle.flush()
                        handle.seek(0)
                        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError as exc:
                    raise CoreError('busy', 'Cannot acquire the application device lock.') from exc
            yield
        except TransportError as exc:
            raise CoreError('transport', str(exc)) from exc
        finally:
            if handle is not None:
                handle.close()
            _LOCK.release()

    def ports(self):
        if self.demo:
            return [{'port': DEMO_PORT, 'candidate': True, 'demo': True,
                     'vid': None, 'pid': None, 'serial_number': 'SIMULATED'}]
        try:
            return self._ports()
        except TransportError as exc:
            raise CoreError('transport', str(exc)) from exc

    def status(self):
        return {'demo': self.demo, 'recovery_available': self._snapshot is not None or
                (not self.demo and self._path.exists()), 'hardware_profiles': len(self._profiles)}

    def _port(self, port):
        matches = [p for p in self.ports() if p['port'] == port]
        if len(matches) != 1:
            raise CoreError('port_missing', 'Select a currently connected candidate module.')
        return matches[0]

    def _inspect(self, port):
        info = self._port(port)
        if self.demo:
            return dict(info, manufacturer='DEMO', model='SIMULATED EG25', firmware='DEMO-1',
                        sim='READY', registered=True, usbnet=self._demo_mode,
                        apn_configured=True, supported=True, internet_verified=False)
        with self._transport(port) as modem:
            return self._read_state(info, modem)

    def _read_state(self, info, modem):
        ati = modem.query('ATI')
        model = '\n'.join(modem.query('AT+CGMM'))
        firmware = '\n'.join(modem.query('AT+CGMR'))
        try:
            sim_lines = modem.query('AT+CPIN?')
        except CommandRejected:
            sim_lines = []
        registrations = []
        for command in ('AT+CEREG?', 'AT+CGREG?'):
            try:
                registrations.extend(modem.query(command))
            except CommandRejected:
                pass
        mode_lines = modem.query('AT+QCFG="usbnet"')
        apns = modem.query('AT+CGDCONT?')
        manufacturer = next((s for s in ati if s.startswith('Manufacturer:')), ati[0] if ati else '')
        sim = next((s.split(':', 1)[1].strip() for s in sim_lines if s.startswith('+CPIN:')), 'UNKNOWN')
        modes = [re.fullmatch(r'\+QCFG:\s*"usbnet",\s*(\d+)', s) for s in mode_lines]
        modes = [int(m.group(1)) for m in modes if m]
        if len(modes) != 1 or not 0 <= modes[0] <= 5:
            raise CoreError('invalid_response', 'Cannot read the current USB network mode safely.')
        registered = any(re.match(r'\+C(?:E|G)REG:\s*\d+,\s*[15](?:,|$)', s) for s in registrations)
        profile = match_profile(manufacturer, model, firmware, self._profiles,
                                vid=info.get('vid'), pid=info.get('pid'), interface=info.get('interface'))
        return dict(info, manufacturer=manufacturer, model=model, firmware=firmware,
                    sim=sim, registered=registered, usbnet=modes[0],
                    apn_configured=any(re.match(r'\+CGDCONT:\s*\d+,"[^"]+","[^"]+"', s) for s in apns),
                    supported=profile is not None, internet_verified=False)

    def inspect(self, port):
        with self._operation():
            return self._inspect(port)

    def _plan(self, port, target):
        if target not in TARGETS:
            raise CoreError('invalid_target', 'Choose mac, windows, or ipad.')
        state = self._inspect(port)
        profile = (Profile('demo', 'DEMO', 'SIMULATED EG25', 'DEMO-1',
                           {'mac': 1, 'ipad': 1, 'windows': 3}, 'simulation', False)
                   if self.demo else match_profile(state['manufacturer'], state['model'],
                                                   state['firmware'], self._profiles,
                                                   vid=state.get('vid'), pid=state.get('pid'),
                                                   interface=state.get('interface')))
        if profile is None or target not in profile.usbnet:
            raise CoreError('unsupported', 'This exact hardware/firmware/target has not been verified.')
        if not self.demo and not getattr(self._transport(port), 'supports_configuration', False):
            raise CoreError('read_only_transport', 'This hardware connection supports diagnostics only.')
        if state['sim'] != 'READY':
            raise CoreError('sim_not_ready', 'Insert an active SIM and unlock its PIN externally.')
        if not self.demo and not state.get('serial_number'):
            raise CoreError('identity_missing', 'A stable USB serial number is required for safe recovery.')
        mode = profile.usbnet[target]
        if type(mode) is not int or not 0 <= mode <= 5:
            raise CoreError('invalid_profile', 'The verified profile contains an invalid mode.')
        return {'target': target, 'current_mode': state['usbnet'], 'desired_mode': mode,
                'change_required': mode != state['usbnet'], 'reboot_required': profile.requires_reboot,
                'profile': profile.name, 'state': state, 'demo': self.demo,
                'internet_verified': False}

    def plan(self, port, target):
        with self._operation():
            return self._plan(port, target)

    def _save(self, state):
        previous = self._snapshot
        if previous is None and not self.demo and self._path.exists():
            previous = self._load_snapshot()
        if previous is not None:
            self._validate_snapshot(previous)
            if not self._same(state, previous):
                raise CoreError('recovery_pending', 'A different module has a saved recovery baseline.')
            self._snapshot = previous
            return
        snapshot = {k: state.get(k) for k in
                    ('serial_number', 'manufacturer', 'model', 'firmware', 'vid', 'pid', 'interface', 'usbnet')}
        snapshot['schema'] = 1
        self._validate_snapshot(snapshot)
        if not self.demo:
            owned_temporary = None
            temporary = self._path.with_suffix('.tmp')
            try:
                self._path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                with os.fdopen(os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                                      getattr(os, 'O_NOFOLLOW', 0), 0o600), 'w') as handle:
                    st = os.fstat(handle.fileno())
                    owned_temporary = (st.st_dev, st.st_ino)
                    json.dump(snapshot, handle)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary, self._path)
                self._sync_directory()
            except OSError as exc:
                raise CoreError('snapshot_failed', 'Cannot save recovery state; no changes were made.') from exc
            finally:
                if owned_temporary is not None:
                    try:
                        st = temporary.lstat()
                        if (st.st_dev, st.st_ino) == owned_temporary and not temporary.is_symlink():
                            temporary.unlink()
                    except OSError:
                        pass
        self._snapshot = snapshot

    def _sync_directory(self):
        if os.name != 'nt':
            fd = os.open(self._path.parent, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
            try:
                os.fsync(fd)
            finally:
                os.close(fd)

    def _validate_snapshot(self, snapshot):
        required = {'schema', 'serial_number', 'manufacturer', 'model', 'firmware',
                    'vid', 'pid', 'interface', 'usbnet'}
        valid = isinstance(snapshot, dict) and set(snapshot) == required
        if valid:
            valid = (type(snapshot['schema']) is int and snapshot['schema'] == 1
                     and type(snapshot['usbnet']) is int and 0 <= snapshot['usbnet'] <= 5
                     and all(isinstance(snapshot[k], str) and 0 < len(snapshot[k]) <= 512
                             for k in ('serial_number', 'manufacturer', 'model', 'firmware')))
        if valid and not self.demo:
            valid = (all(type(snapshot[k]) is int and 0 <= snapshot[k] <= 65535
                         for k in ('vid', 'pid'))
                     and isinstance(snapshot['interface'], str) and bool(snapshot['interface']))
        if not valid:
            raise CoreError('invalid_snapshot', 'Recovery data is incomplete or invalid; no write allowed.')

    def _same(self, state, original):
        return all(state.get(k) == original.get(k) for k in
                   ('serial_number', 'manufacturer', 'model', 'firmware', 'vid', 'pid', 'interface'))

    def _load_snapshot(self):
        try:
            with os.fdopen(os.open(self._path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)), 'r') as handle:
                payload = handle.read(8193)
                if len(payload) > 8192:
                    raise ValueError('Oversized snapshot')
                snapshot = json.loads(payload)
            self._validate_snapshot(snapshot)
            return snapshot
        except (OSError, ValueError) as exc:
            raise CoreError('invalid_snapshot', 'Cannot safely read the recovery snapshot.') from exc

    def _reconnect(self, original, mode):
        deadline = self._clock() + self._timeout
        while self._clock() < deadline:
            candidates = [p for p in self.ports() if p.get('serial_number') == original['serial_number']
                          and all(p.get(k) == original.get(k) for k in ('vid', 'pid', 'interface'))]
            if len(candidates) == 1:
                try:
                    state = self._inspect(candidates[0]['port'])
                    if self._same(state, original) and state['usbnet'] == mode:
                        return state
                except (CoreError, TransportError):
                    pass
            self._sleep(.5)
        raise CoreError('reconnect_failed', 'Module did not return with the expected configuration; use recovery.')

    def _change(self, port, mode, reboot, original):
        if self.demo:
            self._demo_mode = mode
            return self._inspect(port)
        with self._transport(port) as modem:
            # Verify through the SAME open handle that will receive the write.
            # Reusing a COM/device path after unplugging is not device identity.
            info = dict(self._port(port))
            state = self._read_state(info, modem)
            fresh = self._port(port)
            if (not self._same(state, original)
                    or any(fresh.get(k) != info.get(k) for k in ('serial_number', 'vid', 'pid', 'interface'))):
                raise CoreError('identity_mismatch', 'Device identity changed before the write.')
            if state['usbnet'] != original['usbnet']:
                raise CoreError('state_changed', 'USB settings changed during the operation; check again.')
            modem.set_usbnet(mode)
            if reboot:
                modem.reboot()
        return self._reconnect(original, mode)

    def apply(self, port, target):
        with self._operation():
            plan = self._plan(port, target)
            if plan['change_required'] or plan['reboot_required']:
                self._save(plan['state'])
                state = self._change(port, plan['desired_mode'], plan['reboot_required'], plan['state'])
            else:
                state = plan['state']
            return {'configured': True, 'internet_verified': False, 'demo': self.demo,
                    'target': target, 'state': state, 'recovery_available': self._snapshot is not None}

    def restore(self, port):
        with self._operation():
            snapshot = self._snapshot
            if snapshot is None and not self.demo:
                if self._path.exists():
                    snapshot = self._load_snapshot()
            if not isinstance(snapshot, dict):
                raise CoreError('no_snapshot', 'No recovery snapshot is available.')
            self._validate_snapshot(snapshot)
            current = self._inspect(port)
            if not self._same(current, snapshot):
                raise CoreError('identity_mismatch', 'Recovery belongs to a different module or firmware.')
            profile = match_profile(current['manufacturer'], current['model'], current['firmware'], self._profiles,
                                    vid=current.get('vid'), pid=current.get('pid'), interface=current.get('interface'))
            if not self.demo and profile is None:
                raise CoreError('unsupported', 'Recovery requires a verified hardware profile.')
            if not self.demo and not getattr(self._transport(port), 'supports_configuration', False):
                raise CoreError('read_only_transport', 'This hardware connection supports diagnostics only.')
            mode = snapshot.get('usbnet')
            if type(mode) is not int or not 0 <= mode <= 5:
                raise CoreError('invalid_snapshot', 'The recovery mode is invalid.')
            state = self._change(port, mode, profile.requires_reboot if profile else False, current)
            if not self.demo:
                try:
                    self._path.unlink(missing_ok=True)
                    self._sync_directory()
                except OSError as exc:
                    raise CoreError('snapshot_cleanup_failed', 'Restored settings, but could not retire recovery file.') from exc
            self._snapshot = None
            return {'restored': True, 'demo': self.demo, 'state': state, 'internet_verified': False}
