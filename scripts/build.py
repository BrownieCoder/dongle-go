"""Build an unsigned/ad-hoc signed preview locally; never publish automatically."""
import hashlib
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
system = platform.system()
if system not in ('Darwin', 'Windows'):
    raise SystemExit('Desktop packages are currently built on macOS and Windows.')
subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
                '--windowed', '--collect-all', 'libusb_package', '--collect-all', 'customtkinter',
                '--collect-data', 'dongle_go', '--name', 'Dongle Go', '--paths', str(root / 'src'),
                '--distpath', str(root / 'dist'), '--workpath', str(root / 'build'),
                '--specpath', str(root / 'build'),
                '--osx-bundle-identifier', 'org.donglego.preview',
                str(root / 'scripts' / 'launcher.py')], check=True, cwd=root, env=dict(os.environ, PYINSTALLER_CONFIG_DIR=str(root / 'build' / 'pyinstaller-cache')))
name = f'Dongle-Go-{system}-{platform.machine()}-preview'
bundle = root / 'dist' / ('Dongle Go.app' if system == 'Darwin' else 'Dongle Go')
# Documentation and licenses accompany the app in the ZIP, not hidden in a binary.
stage = root / 'build' / 'package'
if stage.exists():
    shutil.rmtree(stage)
stage.mkdir(parents=True)
shutil.copytree(bundle, stage / bundle.name, symlinks=True)
for item in ('README.md', 'README.zh-CN.md', 'LICENSE', 'THIRD_PARTY_NOTICES.md'):
    shutil.copy2(root / item, stage / item)
for item in ('docs', 'assets', 'licenses'):
    shutil.copytree(root / item, stage / item)
archive = root / 'dist' / f'{name}.zip'
if system == 'Darwin':
    subprocess.run(['ditto', '-c', '-k', '--sequesterRsrc', '--keepParent', str(stage), str(archive)], check=True)
else:
    shutil.make_archive(str(archive.with_suffix('')), 'zip', stage)
checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
archive.with_suffix('.zip.sha256').write_text(f'{checksum}  {archive.name}\n', encoding='utf-8')
print(archive)
