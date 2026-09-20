# Verification evidence / 验证证据

Date: 2026-09-20. Tested application/source commit: `296a0460ea465416d6b41e76313047dfd8c144c7`. Later documentation-only commits preserve the reviewed implementation.

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

## Independent software reviews

| Engineer | Scope | Final score | Open P0/P1 |
| --- | --- | ---: | ---: |
| [1](reviews/engineer-1.md) | GUI/localization/distribution, excluding own USB implementation | 97/100 | 0 |
| [2](reviews/engineer-2.md) | Core/transport/recovery; no implementation role | 96/100 | 0 |
| [3](reviews/engineer-3.md) | Product/bilingual/distribution; no implementation role | 96/100 | 0 |

Reviewers initially rejected or withheld approval, reproduced issues, and re-reviewed fixes and actual CI evidence. These scores use the explicitly scoped [software rubrics](software-review.md); they do not replace the original overall hardware-dependent [acceptance gate](acceptance.md).

## Still unproven / 尚未证明

The physical dongle has been ordered but is not available. No hardware profile is approved; real setup remains locked. Factory USB transport is read-only. No cellular internet route, physical rollback, Windows 11 clean-machine driver flow, iPad behavior, novice trial, formal signing/notarization or full binary-license replacement audit has passed. The project is a public development preview, **not an accepted mature MVP**.

中文：软件阶段三位独立审核分别为 97、96、96 分；Windows/macOS 打包程序已实际启动并完成模拟自测。真实模块、运营商网络、Windows 11 驱动和 iPad 均未验收。硬件到货后按真机矩阵补测，不能把软件分数当成完整交付分数。
