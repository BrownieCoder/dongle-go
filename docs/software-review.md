# Software review and hardware acceptance / 软件审查与硬件验收

These are separate gates. The user confirmed on 2026-09-20 that the dongle is ordered but has not arrived; physical validation will be performed in a later round. That permits publishing a clearly labeled development preview. It does **not** turn an empty hardware profile list into one-click production support or establish mature-MVP acceptance.

Three different engineers review work they did not implement. Engineer 1 reviews GUI/distribution outside their USB implementation. Engineers 2 and 3 are fresh reviewers with no implementation role. Each software score is scoped to its stated rubric and evidence; all must reach 95/100 with no open P0/P1 for software sign-off. The unchanged overall [acceptance rubric](acceptance.md) still requires real hardware and beginner trials.

| Review | Software scope | Rubric |
| --- | --- | --- |
| [Engineer 1](reviews/engineer-1.md) | GUI, state, packaging, CI; excludes own USB code | See signed review |
| [Engineer 2](reviews/engineer-2.md) | Core, transport, recovery, tests | Correctness 35 + recovery/safety 25 + tests 25 + maintainability 15 |
| [Engineer 3](reviews/engineer-3.md) | Product UX, bilingual guides, distribution | Product correctness 30 + beginner/bilingual UX 25 + distribution 25 + tests/docs 20 |

中文：用户已确认硬件尚未到货，真机验收留到后续；当前可以公开开发预览。软件分数不替代整体交付分数，不能宣传“成熟 MVP 已全部通过”。三位工程师的软件审查分别保留范围、量表、问题和复测证据。
