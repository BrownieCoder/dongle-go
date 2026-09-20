# Independent modern UI review 1

Reviewer: compatibility_research agent. Date: 2026-09-20. Scope: `ui.py`, `app.py`, `i18n.py`, and `tests/test_app.py`. Reviewer did not author these files and did not change their implementation. Hardware and the reviewer-authored USB transport are excluded.

## Initial findings

1. **P2 — Readonly combo boxes lose keyboard selection.** CustomTkinter's combo implementation binds its arrow to mouse clicks. Neither language nor port selector adds Up/Down/Return selection behavior. Independent live probe focused the language entry and generated Down then Return: value remained English, and its Down binding was empty. Keyboard-only users cannot select another dongle or language.
2. **P2 — Keyboard focus can move outside the visible scroll area.** At an actual 780×620 window, with the task canvas at the top, focusing Help produced button root Y=776 against canvas top=169 and height=528 (bottom=697). Canvas yview remained `(0.0, 0.7447108603667136)`. Focus was offscreen with no auto-reveal behavior.

These findings were sent to the implementing engineer before completion. Both must be fixed and regression-tested before approval.

## Evidence and retained behavior

Independently ran `.venv-tk/bin/python -m unittest discover -s tests -p test_app.py -v` with GUI access: **4/4 passed**. This covers demo configuration/recovery, language text changes through direct calls, target-change invalidation, unknown firmware disabling setup, and empty device selection. It does not cover real keyboard combo behavior or offscreen focus, hence the additional live probes.

Static inspection confirms disabled action state remains tied to busy/readiness, background operations still use the event queue, target buttons invalidate readiness, status text retains the distinction between configuration and verified networking, and the workspace has vertical scrolling. No evidence of hardware behavior changed is claimed.

## Initial score

| Category | Score |
|---|---:|
| Preserved state and operation behavior | 25/25 |
| Keyboard and focus behavior | 16/25 |
| Bilingual text and status accuracy | 24/25 |
| Small-window reachability and verification | 20/25 |
| Total | **85/100 — not approved** |

Additional minor observation: focused selected target uses the same green border as unfocused selection, so those states are not visually distinct. Re-review requires corrected keyboard selectors and automatic focus visibility. This score is for UI software only, not hardware compatibility or mature-MVP completion.

## Independent re-review after fixes

Inspected `KeyboardComboBox` Up/Down bindings, disabled-state checks and selection callbacks, FocusIn-triggered reveal for every task-area control, and the distinct amber focus border. Independently reran the actual-window keyboard probe: Down changes language from English to Chinese. At 780×620, focusing Help now scrolls the canvas automatically.

An additional reviewer-authored temporary probe exercised actual Tk key events and assertions, without modifying implementation or repository tests:

- Module Down selection changes the port and invalidates setup readiness.
- Disabled module selection ignores Up; disabled target activation changes nothing.
- Enabled Space activates the iPad target.
- Help receives visible focus in the scrolled viewport; the measured one-pixel lower-edge rounding is within the probe's two-pixel tolerance.
- At 780×620 the hero is hidden; at 1060×790 it returns. The task controls remain available.

Both live probes exited successfully. The original four regression tests had independently passed on the modern view before the focused fixes. These probes provide separate evidence for the two behaviors those original tests missed. No hardware was accessed.

**Both P2 findings and the focus-color observation are resolved. Final UI-only review: 96/100 — approved.** Breakdown: preserved state behavior 25/25; keyboard/focus 24/25; bilingual status 24/25; small-window reachability/verification 23/25. Remaining deductions reflect lack of a full screen-reader/high-DPI audit and the need to retain these new keyboard scenarios in the automated suite. This UI verdict does not certify the newly packaged Windows/macOS distributions, real hardware, or completion of the mature MVP; their independent gates still apply.
