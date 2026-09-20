"""Unpack the actual distribution ZIP and launch its executable without hardware."""
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import zipfile

root = Path(__file__).resolve().parents[1]
archives = list((root / 'dist').glob('Dongle-Go-*-preview.zip'))
if len(archives) != 1:
    raise SystemExit('Expected exactly one platform distribution archive.')
with tempfile.TemporaryDirectory(prefix='dongle-go-smoke-') as temp:
    folder = Path(temp)
    if platform.system() == 'Darwin':
        subprocess.run(['ditto', '-x', '-k', str(archives[0]), str(folder)], check=True)
        executables = list(folder.glob('**/Dongle Go.app/Contents/MacOS/Dongle Go'))
    else:
        with zipfile.ZipFile(archives[0]) as archive:
            archive.extractall(folder)
        executables = list(folder.glob('**/Dongle Go.exe'))
    if len(executables) != 1:
        raise SystemExit('Packaged executable is missing or ambiguous.')
    report = folder / 'smoke.json'
    subprocess.run([str(executables[0]), '--smoke-test', str(report)], check=True,
                   timeout=45, cwd=folder)
    data = json.loads(report.read_text(encoding='utf-8'))
    expected = {'tk_window', 'serial_import', 'usb_import', 'bundled_libusb',
                'demo_check', 'demo_apply', 'demo_restore', 'language_switch'}
    if data.get('ok') is not True or set(data.get('checks', ())) != expected:
        raise SystemExit('The packaged app did not pass all smoke checks.')
    output = root / 'dist' / 'smoke-report.json'
    shutil.copy2(report, output)
    print(json.dumps(data, indent=2))
