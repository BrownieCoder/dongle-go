"""Bounded serial AT exchanges. Response bodies are never logged."""
import re
import math
import threading
import time

USB_CANDIDATES = {(0x2CA3, 0x4006), (0x2C7C, 0x0125)}
READ_COMMANDS = frozenset({'ATI', 'AT+CGMM', 'AT+CGMR', 'AT+CPIN?',
                           'AT+CEREG?', 'AT+CGREG?', 'AT+QCFG="usbnet"', 'AT+CGDCONT?'})


class TransportError(Exception):
    pass


class CommandRejected(TransportError):
    """A complete ERROR terminator: command failed but framing is synchronized."""
    pass


def enumerate_ports() -> list[dict]:
    try:
        from serial.tools import list_ports
    except ImportError as exc:
        raise TransportError('Install pyserial to inspect hardware.') from exc
    return [{'port': p.device, 'vid': p.vid, 'pid': p.pid,
             'serial_number': p.serial_number,
             'interface': p.interface,
             'candidate': (p.vid, p.pid) in USB_CANDIDATES}
            for p in list_ports.comports() if (p.vid, p.pid) in USB_CANDIDATES]


class ATTransport:
    supports_configuration = True

    def __init__(self, port: str, *, factory=None, timeout: float = 3.0,
                 clock=time.monotonic):
        if not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
            raise TransportError('Invalid serial timeout.')
        self.port, self.timeout, self.clock = port, timeout, clock
        self.factory = factory
        self.serial = None
        self.poisoned = False
        self.exchange_lock = threading.Lock()

    def __enter__(self):
        if self.factory is None:
            try:
                import serial
            except ImportError as exc:
                raise TransportError('Install pyserial to inspect hardware.') from exc
            self.factory = serial.Serial
        try:
            self.serial = self.factory(self.port, baudrate=115200,
                                       timeout=min(.2, self.timeout), write_timeout=self.timeout)
        except Exception as exc:
            raise TransportError('Cannot open the selected serial port.') from exc
        return self

    def __exit__(self, *_):
        if self.serial is not None:
            try:
                self.serial.close()
            finally:
                self.serial = None

    def query(self, command: str) -> list[str]:
        if command not in READ_COMMANDS:
            raise TransportError('Unsupported diagnostic command.')
        return self._exchange(command)

    def set_usbnet(self, value: int) -> list[str]:
        if type(value) is not int or not 0 <= value <= 5:
            raise TransportError('Invalid USB network mode.')
        return self._exchange(f'AT+QCFG="usbnet",{value}')

    def reboot(self) -> list[str]:
        return self._exchange('AT+CFUN=1,1')

    def _exchange(self, command: str) -> list[str]:
        with self.exchange_lock:
            if self.serial is None or self.poisoned:
                raise TransportError('Serial transport is closed or requires reopening.')
            try:
                return self._exchange_locked(command)
            except CommandRejected:
                raise
            except Exception as exc:
                self.poisoned = True
                if isinstance(exc, TransportError):
                    raise
                raise TransportError('Serial communication failed; state may be uncertain.') from exc

    def _exchange_locked(self, command: str) -> list[str]:
        deadline, lines, size, pending = self.clock() + self.timeout, [], 0, b''
        try:
            self.serial.reset_input_buffer()
            payload = (command + '\r').encode('ascii')
            if self.serial.write(payload) != len(payload):
                raise TransportError('Incomplete serial command write; reopen before retrying.')
            while self.clock() < deadline:
                chunk = self.serial.read(256)
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
        except TransportError:
            raise
        except Exception as exc:
            raise TransportError('Serial communication failed; state may be uncertain.') from exc
        raise TransportError('Module response timed out; state may be uncertain.')
