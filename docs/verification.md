# Verification evidence / 验证证据

Date: 2026-09-20. Tested application/source commit: `296a0460ea465416d6b41e76313047dfd8c144c7`. This section records the original implementation; see the UI update below for the current build.

## Automated and packaged execution

[GitHub run 35503009255](https://github.com/BrownieCoder/dongle-go/actions/runs/35503009255) completed with **success** on all three jobs:

- macOS 15 ARM64: unit/real-Tk tests, documentation checks, PyInstaller build, ZIP extraction, actual `.app` execution.
- Windows Server 2022 x64: unit/real-Tk tests, documentation checks, PyInstaller build, ZIP extraction, actual `.exe` execution. Windows-specific skips for POSIX permission/symlink operations do not constitute Windows physical-device validation.
- Ubuntu 24.04: tests under Xvfb and documentation checks; no Linux desktop package or hardware support claim.

Local Python.org 3.12.4 / macOS ARM64: **56 tests passed** using real Tk widgets and simulated transports. The local default Homebrew Python lacked Tk; that environment failure was resolved by using the Tk-equipped runtime, not by skipping GUI tests.

Both CI smoke artifacts were downloaded and inspected. Each reports:

```json
{"ok":true,"demo":true,"hardware_accessed":false,"internet_verified":false,
 "checks":["tk_window","serial_import","usb_import","bundled_libusb",
           "demo_check","demo_apply","demo_restore","language_switch"],"error":null}
```

Both distribution SHA-256 values were recomputed after downloading and matched their separately uploaded checksum artifacts. See [downloads](downloads.md). Images were inspected for nine panels, accurate bilingual captions, target-device distinctions and the preview disclaimer. Relative documentation links passed `python scripts/check_docs.py`.

## Still unproven / 尚未证明

The physical dongle has been ordered but is not available. No hardware profile is approved; real setup remains locked. Factory USB transport is read-only. No cellular internet route, physical rollback, Windows 11 clean-machine driver flow, iPad behavior, novice trial, formal signing/notarization or full binary-license replacement audit has passed. The project is a public development preview, **not an accepted mature MVP**.

中文：Windows/macOS 打包程序已实际启动并完成模拟自测。真实模块、运营商网络、Windows 11 驱动和 iPad 均未验收。硬件到货后按真机矩阵补测，软件测试不能替代硬件验收。

## Illustrated UI update / 漫画界面更新

Application commit: `9003c9c11b0eb934c9bca3931e794b0814e56280`. [CI run 35504437091](https://github.com/BrownieCoder/dongle-go/actions/runs/35504437091) passed on macOS 15, Windows Server 2022 and Ubuntu 24.04. macOS and Windows both rebuilt, unpacked and launched the new desktop package; downloaded smoke reports each show all eight checks passed, hardware_accessed=false and internet_verified=false.

Local macOS: 58 tests passed, including six real CTk tests covering keyboard selection, disabled actions and compact-window focus visibility. Local packaged ZIP also passed all eight smoke checks. The actual packaged Chinese and English interfaces and keyboard-driven check/apply demonstration were visually inspected. Updated download checksum values are taken from this run's checksum artifacts.

Physical hardware acceptance remains pending. / 真机验收仍待完成。

## Current downloadable packages

[Build 35504671243](https://github.com/BrownieCoder/dongle-go/actions/runs/35504671243), commit `b9828bc`, passed all three platform jobs. Both downloadable ZIPs were downloaded and their SHA-256 hashes recomputed against the checksum artifacts. Each packaged-app report contains eight passing simulation checks; hardware and internet verification remain false. See [downloads](downloads.md) for the matching artifacts.
