# License provenance and corresponding source

These are complete upstream license files, not summaries. Downloaded on 2026-09-20 from official project repositories or published PyPI archives. The project has not changed these texts.

| Local file | Exact upstream source |
| --- | --- |
| Python-3.12-LICENSE.txt | [CPython v3.12.10 LICENSE](https://github.com/python/cpython/blob/v3.12.10/LICENSE) |
| Tcl-license.terms | [Tcl core-8-6-16](https://github.com/tcltk/tcl/blob/core-8-6-16/license.terms) |
| Tk-license.terms | [Tk core-8-6-16](https://github.com/tcltk/tk/blob/core-8-6-16/license.terms) |
| pyserial-LICENSE.txt | `LICENSE.txt` from [pyserial 3.5 PyPI sdist](https://pypi.org/project/pyserial/3.5/#files) |
| pyusb-LICENSE.txt | `LICENSE` from [PyUSB 1.3.1 PyPI sdist](https://pypi.org/project/pyusb/1.3.1/#files) |
| libusb-package-LICENSE.txt | `.dist-info/licenses/LICENSE` from [libusb-package 1.0.26.3 PyPI wheel](https://pypi.org/project/libusb-package/1.0.26.3/#files) |
| libusb-COPYING.txt | [libusb v1.0.26 COPYING](https://github.com/libusb/libusb/blob/v1.0.26/COPYING), byte-identical to the included source commit's COPYING |
| PyInstaller-COPYING.txt | `COPYING.txt` from [PyInstaller 6.16.0 PyPI sdist](https://pypi.org/project/pyinstaller/6.16.0/#files) |
| PyInstaller-zlib-LICENSE.txt | [PyInstaller v6.16.0 bootloader/zlib/LICENSE](https://github.com/pyinstaller/pyinstaller/blob/v6.16.0/bootloader/zlib/LICENSE) |

## Included corresponding source

- `libusb-source-ba698478.tar.gz`: [libusb source at ba698478afc3d3a72644eef9fc4cd24ce8383a4c](https://github.com/libusb/libusb/tree/ba698478afc3d3a72644eef9fc4cd24ce8383a4c), the submodule referenced by libusb-package v1.0.26.3. Includes library source, build scripts and upstream licenses.
- `libusb-package-source-1.0.26.3.tar.gz`: [libusb-package v1.0.26.3](https://github.com/pyocd/libusb-package/tree/v1.0.26.3), including packaging/build scripts. GitHub archives omit submodule contents: extract the separate libusb source into this wrapper's `src/libusb` directory when rebuilding. Follow the wrapper README and its platform-specific build configuration.

The package's Python wrapper is Apache-2.0; the embedded C library headers and COPYING specify LGPL-2.1-or-later. See [libusb/core.c](https://github.com/libusb/libusb/blob/ba698478afc3d3a72644eef9fc4cd24ce8383a4c/libusb/core.c). The wrapper README's GPLv2 wording does not match those source licenses.

Keep the library dynamically loaded and replaceable. The exact replacement location depends on the frozen platform bundle; inspect the actual `libusb_package` library path before publication, document it in the release, and test replacement with a compatible rebuild. The public project source permits modification; no additional restriction prohibits debugging modifications of the LGPL library.

## SHA-256 integrity record

```text
dcf75fdb959db1e3b41c0f8505069d2ece781b5ec6b3d0a4d30975cfc6580245  PyInstaller-COPYING.txt
0f854f426019c475697e17f1b0fa638270f6e700bc756d9bfe50d17268bd3281  PyInstaller-zlib-LICENSE.txt
3b2f81fe21d181c499c59a256c8e1968455d6689d269aa85373bfb6af41da3bf  Python-3.12-LICENSE.txt
c0a69a2bfd757361ec7e6143973b103c90409316b49e9c88db26ad6388e79f16  Tcl-license.terms
2cde822b93ca16ae535c954b7dfe658b4ad10df2a193628d1b358f1765e8b198  Tk-license.terms
5df07007198989c622f5d41de8d703e7bef3d0e79d62e24332ee739a452af62a  libusb-COPYING.txt
a6cba85bc92e0cff7a450b1d873c0eaa2e9fc96bf472df0247a26bec77bf3ff9  libusb-package-LICENSE.txt
c83823b244bb153a0bb8d1e1d86cd4553d354dd6fbfc87ed2aae8d3a3acd6df8  libusb-package-source-1.0.26.3.tar.gz
4c626d89ebd984778684a9da3a215958300aa9c3a3f34f0baff6ba0dbb526110  libusb-source-ba698478.tar.gz
f91cb9813de6a5b142b8f7f2dede630b5134160aedaeaf55f4d6a7e2593ca3f3  pyserial-LICENSE.txt
03e39fdcee9c18f2f9d0c3500a993ddeac050695eb81070ea41347587c76a7fe  pyusb-LICENSE.txt
```

Reference Python/Tcl/Tk versions are not a claim that every build bundles these exact versions. Release audit must inventory actual runtime/native dependencies and refresh notices when they differ.

## Modern desktop UI dependencies
The CustomTkinter 5.2.2, Pillow 11.3.0, darkdetect 0.8.0 and packaging 26.3 license files were copied verbatim from the installed distributions' dist-info metadata. Pillow's full wheel notice includes its bundled native dependency notices.
