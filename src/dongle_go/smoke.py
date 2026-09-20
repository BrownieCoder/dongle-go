"""Packaged-app self-check: load dependencies and exercise a real Tk demo flow."""
import json
from pathlib import Path
import time


def schedule(app, output):
    destination = Path(output)
    started = time.monotonic()
    step = 0
    checks = []

    def finish(ok, error=None):
        report = {'ok': ok, 'demo': True, 'hardware_accessed': False,
                  'internet_verified': False, 'checks': checks, 'error': error}
        destination.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        app.smoke_passed = ok
        app.closed = True
        app.root.destroy()

    def tick():
        nonlocal step
        try:
            if time.monotonic() - started > 15:
                finish(False, 'timeout')
                return
            if app.last_error:
                finish(False, app.last_error)
                return
            if not app.busy and app.port.get():
                if step == 0:
                    # Load the packaged backend, but never enumerate or open hardware.
                    import serial
                    import usb.core
                    import libusb_package
                    backend = libusb_package.get_libusb1_backend()
                    if backend is None:
                        raise RuntimeError('missing bundled libusb')
                    checks.extend(['tk_window', 'serial_import', 'usb_import', 'bundled_libusb'])
                    app.check()
                    step = 1
                elif step == 1:
                    if not app.ready:
                        raise RuntimeError('demo did not become ready')
                    checks.append('demo_check')
                    app.apply()
                    step = 2
                elif step == 2:
                    if app.status_key != 'demo_done':
                        raise RuntimeError('demo apply failed')
                    checks.append('demo_apply')
                    app.restore()
                    step = 3
                elif step == 3:
                    if app.service.inspect(app.port.get())['usbnet'] != 0:
                        raise RuntimeError('demo restore failed')
                    checks.append('demo_restore')
                    app.lang.set('中文')
                    app.change_language()
                    checks.append('language_switch')
                    finish(True)
                    return
            app.root.after(100, tick)
        except Exception as exc:
            finish(False, type(exc).__name__)

    app.smoke_passed = False
    app.root.after(250, tick)
