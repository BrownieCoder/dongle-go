# Third-party notices

Dongle Go is independent of DJI, Quectel, Apple and Microsoft. Hardware names describe compatibility research; no trademark rights are granted. Original application code is MIT licensed. No DJOneHub/VoHive PolyForm Noncommercial code is incorporated. Protocol references are recorded in [compatibility.md](docs/compatibility.md).

The following notices apply to runtime components and generated desktop distributions. Complete upstream texts are in [licenses/](licenses/README.md); keep that directory with every binary distribution.

| Component | Version / source | License and included text |
| --- | --- | --- |
| Python | Build CI selects 3.12; reference text from CPython 3.12.10 | PSF License Agreement and historical licenses; [full text](licenses/Python-3.12-LICENSE.txt) |
| Tcl | Reference text from 8.6.16; actual bundled version must be inventoried | Tcl BSD-style terms; [full text](licenses/Tcl-license.terms) |
| Tk | Reference text from 8.6.16; actual bundled version must be inventoried | Tk BSD-style terms; [full text](licenses/Tk-license.terms) |
| pyserial | 3.5 | BSD-3-Clause; [full text](licenses/pyserial-LICENSE.txt) |
| PyUSB | 1.3.1 | BSD-3-Clause; [full text](licenses/pyusb-LICENSE.txt) |
| libusb-package Python wrapper | 1.0.26.3 | Apache-2.0; [full text](licenses/libusb-package-LICENSE.txt) |
| libusb shared library | 1.0.26; upstream source commit `ba698478afc3d3a72644eef9fc4cd24ce8383a4c` | LGPL-2.1-or-later; [full text](licenses/libusb-COPYING.txt) and corresponding source in `licenses/` |
| PyInstaller | 6.16.0 | GPL-2.0-or-later with bootloader exception; Apache-2.0 runtime hooks; full upstream terms, exceptions and license texts in [COPYING](licenses/PyInstaller-COPYING.txt) |
| zlib in PyInstaller bootloader, when included | Version follows the PyInstaller bootloader build | zlib license; [full text](licenses/PyInstaller-zlib-LICENSE.txt) |

The libusb-package README calls libusb “GPLv2,” but the actual embedded submodule's COPYING and library source headers specify LGPL-2.1-or-later. This inventory follows those source files, not the inaccurate README shorthand. See the immutable source links in [license provenance](licenses/README.md).

Dongle Go uses libusb as a shared library through PyUSB. There are no Dongle Go modifications to libusb. The corresponding libusb source and libusb-package build wrapper are included with these notices. Their archive names and hashes are in [licenses/README.md](licenses/README.md). Preserve the ability to replace the shared library with a compatible modified build; no project restriction prohibits modification or reverse engineering to debug modifications of that library. Binary publication still requires checking the produced bundle's actual library path and replacement behavior, and ensuring the included source corresponds to the shipped binary. A source link alone is not a completed distribution audit.

Before publication, inventory the actual packaged Python/Tcl/Tk versions and any additional bundled native libraries, refresh their applicable license notices, and verify the complete `licenses/` folder and corresponding sources are present in each ZIP. The reference notices here do not certify every possible Python distributor's dependency bundle.

Windows manufacturer drivers are not included or redistributed. Obtain drivers only from their manufacturer; do not disable driver signature enforcement. Generated comic assets were created for this project with OpenAI ImageGen; their prompts and visual review record are in [assets.md](docs/assets.md).
