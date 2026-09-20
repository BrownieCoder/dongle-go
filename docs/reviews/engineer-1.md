# Independent review 1 — GUI, localization, packaging

Reviewer: compatibility_research agent. Date: 2026-09-20.

## Scope and independence

Reviewed `src/dongle_go/app.py`, `src/dongle_go/i18n.py`, `tests/test_app.py`, `scripts/build.py`, `scripts/launcher.py`, `pyproject.toml`, and `.github/workflows/ci.yml`. These were authored by other engineers. The review does **not** score this reviewer's USB backend, research documents, or hardware-validation template.

This review distinguishes software evidence from hardware readiness. Hardware has not been exercised and receives no passing score here.

## Initial findings

1. **P2: Recovery errors are misclassified.** `error_key` uses substring matching: both `snapshot_failed` and `invalid_snapshot` become `no_snapshot`. Users are told there is no saved configuration even when one exists but is unreadable or invalid. Use explicit mappings with distinct save/read/recovery-pending guidance; verify all known error codes.
2. **P2: Discovery help describes only serial devices.** The empty-list explanation refers to no supported serial connection after native USB discovery was added. Update both languages to describe USB and serial paths without implying USB discovery is absent.
3. **P2: Packaged execution is not verified by CI.** Building an archive does not prove bundled Tk/libusb imports or the packaged executable start. Add a bounded hardware-free smoke command, invoke the packaged binary on both desktop runners, and validate its result before uploading artifacts.

These findings were sent to the parent engineer for correction. The reviewer did not modify the reviewed implementation.

## Positive observations

- Device operations run off Tk's main thread and results are marshalled through a queue.
- Target changes invalidate setup readiness; busy states disable input; normal close waits for ongoing operations.
- Unexpected exceptions do not expose raw device responses in the GUI.
- Demo and unverified internet outcomes are clearly distinguished; iPad is not reported online from desktop configuration.
- Build dependencies are pinned, checksums are generated, CI has read-only repository permission, and builds do not automatically publish releases.

## Evidence and initial score

Static review completed. Running `.venv/bin/python -m unittest discover -s tests -p test_app.py -v` failed at import because that local Python runtime lacks `_tkinter`; no GUI test actually ran under that runtime. This is an environment limitation, not a claim that the test assertions failed. CI and packaged execution evidence are pending.

| Software category | Initial score |
|---|---:|
| State flow and write-state UI | 24/25 |
| Bilingual guidance and error accuracy | 19/25 |
| Privacy and permission handling | 24/25 |
| Packaging and executable verification | 18/25 |
| Total | **85/100 — not approved** |

Score applies only to this scope. It is not a hardware-compatibility score and not an MVP-completion claim. Re-review is required after fixes and executable evidence.
