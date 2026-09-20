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

## Independent re-review

Reviewed working-tree fixes against HEAD `296a0460ea465416d6b41e76313047dfd8c144c7`. All three initial findings have implementation fixes: explicit error-code mappings distinguish save/read/missing recovery cases; discovery strings include USB and serial; CI unpacks distribution archives and runs the actual executable with a bounded simulation-only smoke check. The smoke path explicitly forces demo mode and loads the bundled libusb backend without enumerating hardware.

The reviewer independently executed:

- `.venv-tk/bin/python -m unittest discover -s tests -p test_app.py -v`: **4/4 passed**, using real Tk widgets.
- `.venv-tk/bin/python -m unittest discover -s tests -p test_i18n.py -v`: **4/4 passed**, including AST coverage of known core error codes.
- `.venv-tk/bin/python scripts/smoke_bundle.py`: **8/8 packaged macOS checks passed** after unpacking the actual ZIP. Report confirms `hardware_accessed: false` and `internet_verified: false`.

The earlier missing-Tk runtime limitation is resolved by `.venv-tk`. This proves macOS packaged demo behavior, not Windows executable behavior or cellular connectivity.

| Software category | Re-review score |
|---|---:|
| State flow and write-state UI | 25/25 |
| Bilingual guidance and error accuracy | 24/25 |
| Privacy and permission handling | 24/25 |
| Packaging and executable verification | 21/25 |
| Total | **94/100 — Windows executable verification pending** |

No unresolved P1/P2 implementation issue remains in this review scope. Windows CI execution evidence is still required for cross-platform packaging approval; a configured workflow alone does not prove it passed. Remaining minor limits include generic transport-error remediation and no comprehensive keyboard/screen-reader usability audit. Hardware remains untested regardless of software score.

## Final software verdict

Independently queried GitHub with `gh run view 35503009255 --repo BrownieCoder/dongle-go --json headSha,conclusion,jobs,url`. The [run](https://github.com/BrownieCoder/dongle-go/actions/runs/35503009255) completed successfully for exact commit `296a0460ea465416d6b41e76313047dfd8c144c7`.

- [Windows job 106058002047](https://github.com/BrownieCoder/dongle-go/actions/runs/35503009255/job/106058002047): native tests, documentation checks, desktop build, and launch of the unpacked application all **success**.
- [macOS job 106058002074](https://github.com/BrownieCoder/dongle-go/actions/runs/35503009255/job/106058002074): native tests, documentation checks, desktop build, and launch of the unpacked application all **success**.
- [Linux job 106058002012](https://github.com/BrownieCoder/dongle-go/actions/runs/35503009255/job/106058002012): virtual-display tests and documentation checks **success**; desktop packaging correctly skipped.

This resolves the remaining Windows executable verification deduction. Final category scores: state flow **25/25**, bilingual guidance **24/25**, privacy **24/25**, packaging/executable verification **24/25**. **Final software review: 97/100 — approved for a development preview within the reviewed scope.** The remaining three points reflect generic transport remediation, incomplete accessibility auditing, and unsigned/unnotarized distribution friction, rather than unresolved critical/high defects.

This approval does **not** establish hardware compatibility, real cellular networking, Windows client-device driver behavior, iPad usability, or completion of the mature MVP objective. Those remain separately gated on actual hardware evidence. No self-authored USB/backend code was scored in this review.
