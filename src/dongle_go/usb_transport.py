"""Original bounded, read-only factory-DJI USB AT transport.

Protocol references and qualification limits are in docs/compatibility.md.
No endpoint sweep, USB reset, driver detach, or configuration write is used.
"""
import math
import re
import threading
import time

from .transport import READ_COMMANDS, CommandRejected, TransportError

DJI_ID = (0x2CA3, 0x4006)
_LOCK = threading.Lock()
_OPEN_PORTS = set()


def _modules():
    try:
        import usb.core
        import usb.util
        import libusb_package
        backend = libusb_package.get_libusb1_backend()
        if backend is None:
            raise TransportError('Bundled libusb backend is unavailable.')
        return usb.core, usb.util, backend
    except ImportError as exc:
        raise TransportError('Install pyusb and libusb to inspect USB hardware.') from exc


def enumerate_ports(*, usb_core=None) -> list[dict]:
    if usb_core is None:
        core, _, backend = _modules()
        options = {'backend': backend}
    else:
        core, options = usb_core, {}
    try:
        devices = core.find(find_all=True, idVendor=DJI_ID[0], idProduct=DJI_ID[1], **options)
        return [{'port': f'usb://{d.bus}/{d.address}', 'candidate': True,
                 'vid': d.idVendor, 'pid': d.idProduct, 'serial_number': None}
                for d in devices if isinstance(d.bus, int) and isinstance(d.address, int)]
    except Exception as exc:
        raise TransportError('USB discovery unavailable; check libusb and permissions.') from exc


def _at_interface(device):
    candidates = []
    for interface in device.get_active_configuration():
        signature = (interface.bAlternateSetting, interface.bInterfaceClass,
                     interface.bInterfaceSubClass, interface.bInterfaceProtocol)
        if signature != (0, 0xFF, 0, 0):
            continue
        endpoints = list(interface)
        bulk = [(e.bEndpointAddress, e.bmAttributes & 3) for e in endpoints
                if e.bmAttributes & 3 == 2]
        other = [e for e in endpoints if e.bmAttributes & 3 != 2]
        if (sorted(bulk) == [(0x03, 2), (0x84, 2)] and len(other) <= 1
                and all(e.bmAttributes & 3 == 3 and e.bEndpointAddress & 0x80 for e in other)):
            candidates.append(interface.bInterfaceNumber)
    if len(candidates) != 1:
        raise TransportError('USB AT descriptor is unknown or ambiguous; no commands sent.')
    return candidates[0]


class USBATTransport:
    supports_configuration = False

    def __init__(self, port, *, timeout=3.0, clock=time.monotonic,
                 usb_core=None, usb_util=None):
        if not re.fullmatch(r'usb://[0-9]+/[0-9]+', port):
            raise TransportError('Invalid USB device address.')
        if not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
            raise TransportError('Invalid USB timeout.')
        self.port, self.timeout, self.clock = port, timeout, clock
        self.core, self.util = usb_core, usb_util
        self.backend_options = {}
        self.device, self.interface = None, None
        self.claimed = self.reserved = self.poisoned = False
        self.exchange_lock = threading.Lock()

    def __enter__(self):
        with _LOCK:
            if self.port in _OPEN_PORTS:
                raise TransportError('USB device is already in use.')
            _OPEN_PORTS.add(self.port)
            self.reserved = True
        try:
            if self.core is None or self.util is None:
                self.core, self.util, backend = _modules()
                self.backend_options = {'backend': backend}
            bus, address = map(int, self.port.removeprefix('usb://').split('/'))
            matches = [d for d in self.core.find(find_all=True, idVendor=DJI_ID[0],
                                               idProduct=DJI_ID[1], **self.backend_options)
                       if (d.bus, d.address) == (bus, address)]
            if len(matches) != 1:
                raise TransportError('Selected USB device is no longer available.')
            self.device = matches[0]
            self.interface = _at_interface(self.device)
            self.util.claim_interface(self.device, self.interface)
            self.claimed = True
            return self
        except Exception as exc:
            self.__exit__(None, None, None)
            if isinstance(exc, TransportError):
                raise
            raise TransportError('Cannot claim USB AT interface; check permissions or competing apps.') from exc

    def __exit__(self, *_):
        try:
            if self.device is not None and self.claimed:
                self.util.release_interface(self.device, self.interface)
        finally:
            try:
                if self.device is not None:
                    self.util.dispose_resources(self.device)
            finally:
                self.device = None
                self.claimed = False
                if self.reserved:
                    with _LOCK:
                        _OPEN_PORTS.discard(self.port)
                    self.reserved = False

    def set_usbnet(self, value):
        raise TransportError('This USB transport supports read-only diagnostics, not configuration writes.')

    def reboot(self):
        raise TransportError('This USB transport supports read-only diagnostics, not reboot.')

    def query(self, command):
        if command not in READ_COMMANDS:
            raise TransportError('Unsupported diagnostic command.')
        with self.exchange_lock:
            if self.device is None or self.poisoned:
                raise TransportError('USB transport is closed or requires reopening.')
            try:
                return self._exchange(command)
            except CommandRejected:
                raise
            except Exception as exc:
                self.poisoned = True
                if isinstance(exc, TransportError):
                    raise
                raise TransportError('USB communication failed; reconnect the module.') from exc

    def _exchange(self, command):
        # Drain only this exact AT channel; never allow endless unsolicited input.
        for _ in range(8):
            try:
                data = self.device.read(0x84, 1024, timeout=20)
                if not data:
                    break
            except self.core.USBTimeoutError:
                break
        else:
            raise TransportError('USB AT channel is busy; no command sent.')
        deadline = self.clock() + self.timeout
        payload = (command + '\r').encode('ascii')
        count = self.device.write(0x03, payload, timeout=max(1, int(self.timeout * 1000)))
        if count != len(payload):
            raise TransportError('Incomplete USB command write; reconnect the module.')
        pending, lines, size = b'', [], 0
        while self.clock() < deadline:
            remaining = deadline - self.clock()
            if remaining <= 0:
                break
            try:
                chunk = bytes(self.device.read(0x84, 1024,
                    timeout=max(1, min(200, int(remaining * 1000)))))
            except self.core.USBTimeoutError:
                continue
            size += len(chunk)
            if size > 32768:
                raise TransportError('Module response exceeds the safe size limit.')
            pending += chunk
            while b'\n' in pending:
                raw, pending = pending.split(b'\n', 1)
                line = raw.decode('ascii', errors='replace').strip()
                if not line or line == command:
                    continue
                if line == 'OK':
                    return lines
                if line == 'ERROR' or re.fullmatch(r'\+CM[ES] ERROR:.*', line):
                    raise CommandRejected('Module rejected the command.')
                lines.append(line)
        raise TransportError('USB response timed out; reopen before retrying.')
