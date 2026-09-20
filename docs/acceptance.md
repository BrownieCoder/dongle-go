# Release acceptance / 交付验收

**Current result: NOT ACCEPTED / 当前结论：未通过交付验收。**

The firmware allowlist is empty. No physical-device matrix row has passed. Unit tests and a demo cannot establish hardware compatibility, successful recovery, destination-specific connectivity or beginner usability. / 固件白名单为空，尚无真机矩阵通过记录。单元测试与演示不能证明硬件兼容、恢复成功、目标设备联网或小白可用性。

The physical dongle is not yet available; the owner will run hardware acceptance when it arrives. This postpones those checks, not the acceptance requirements. The factory USB transport is currently read-only; its software tests cannot qualify configuration support. / 真机尚未到位，由设备所有者在到货后进行硬件验收。这是延后测试，不是豁免验收；出厂 USB 通道当前只读，其软件测试不能证明配置功能可用。

## Required deliverables / 必须交付

- Public GitHub repository with source, license, installation instructions and reproducible verification. Public visibility and URLs must be verified after publication. / 公开 GitHub 仓库、源码、许可证、安装与复现验证说明；发布后核实可见性及链接。
- Chinese and English beginner guides, troubleshooting and nine-panel meme tutorials. Inspect both generated images for text accuracy, order, legibility and consistency with real UI. / 中英文小白教程、排障和九宫格 meme 教程；检查图中文字、顺序、可读性及界面一致性。
- Beginner-installable macOS and Windows builds, with actual launch checks on their target operating systems. CI success alone is insufficient. / 小白可安装的 macOS、Windows 构建，需在目标系统真实启动，不能仅凭 CI 成功。
- Explicit distinction between setup computer and destination device. iPad configuration happens on Mac/Windows; experimental destinations must not appear as supported production configurations. / 区分配置电脑与上网设备；iPad 先用电脑配置，实验性目标不能混入正式支持列表。
- Three separate independent engineer reviews and closure/retest evidence for findings. / 三名不同独立工程师审核，问题需有修复与复测证据。

## Scorecard / 评分表

Each reviewer independently scores all categories from current evidence and cites files, commands, artifacts or physical test records. Scores are not targets to fabricate. **Every review must reach at least 95/100, with zero open P0/P1 issues.** Missing evidence earns no credit for the affected criteria. / 每人独立评分并引用证据，不能为了达标编造分数。**每位均需 ≥95/100，且没有未解决的 P0/P1。** 缺少证据的项目不得给分。

| Category / 类别 | Points / 分值 | Required evidence / 必要证据 |
| --- | ---: | --- |
| Correct configuration and destination compatibility / 配置与目标兼容 | 25 | Physical model/firmware/OS records; actual USB data route; exact allowed profiles / 真机型号、固件、系统、USB 实际路由与白名单配置 |
| Recovery and failure containment / 恢复与故障控制 | 25 | Device-bound original settings; disconnect and restore tests; no unrelated device writes / 绑定设备的原配置、断连与恢复实测、不误写其他设备 |
| Beginner experience / 小白体验 | 20 | New-user run on both desktop OS families, actionable errors and accurate status / 两类桌面系统的新用户操作、有效排障和准确状态 |
| Engineering quality and privacy / 工程与隐私 | 20 | Code review, meaningful automated tests, dependency and redaction checks / 代码审核、有效测试、依赖与脱敏检查 |
| Bilingual docs and distribution / 双语文档与分发 | 10 | Verified public repository, runnable installers, both tutorials visually checked / 公开仓库核验、安装包可运行、双语教程视觉检查 |

P0: critical data/security/device integrity failure. P1: primary workflow unusable, unsafe or falsely reported as successful for a supported configuration. P2: meaningful defect with a reasonable workaround. / P0：严重数据、安全或设备完整性问题；P1：支持组合的主流程不可用、不安全或假报成功；P2：存在合理绕行方式的重要缺陷。

## Real hardware matrix / 真机矩阵

Record the exact dongle model, USB VID/PID, firmware revision, host OS/build, app revision, SIM carrier (without subscriber identifiers), cable/power path and expected USB mode for every row. / 每行记录确切型号、USB VID/PID、固件、系统版本、程序版本、运营商（不含用户标识）、线材和供电、预期 USB 模式。

| Setup computer / 配置电脑 | Destination / 上网设备 | Required scenarios / 必测场景 | Status / 状态 |
| --- | --- | --- | --- |
| Apple Silicon Mac | Same Mac / 同一 Mac | First setup; 10 cold reconnects; reboot; 5 sleep/wake cycles; SIM missing; no signal; restore / 首次配置、10 次冷插拔、重启、5 次睡眠唤醒、无卡、无信号、恢复 | Not tested / 未测 |
| Intel Mac | Same Mac / 同一 Mac | Same scenarios if claiming Intel support / 宣称支持 Intel 时同上 | Not tested; not supported yet / 未测，暂不支持承诺 |
| Windows 11 x64 | Same PC / 同一电脑 | Above plus clean-machine driver installation and standard-user launch / 同上，加全新系统驱动安装与普通用户启动 | Not tested / 未测 |
| Windows 10 or ARM Windows | Same PC / 同一电脑 | Separate OS/architecture qualification before claiming support / 声明支持前按系统及架构单独认证 | Not tested; not supported yet / 未测，暂不支持承诺 |
| Apple Silicon Mac | USB-C iPad, exact model/iPadOS / 确切型号与 iPadOS | Setup on Mac; transfer; actual data route; 10 reconnects; lock/wake; power; return and restore on Mac / Mac 配置、转接、实际流量、10 次拔插、锁屏唤醒、供电、回 Mac 恢复 | Not tested; experimental / 未测，实验性 |
| Windows 11 x64 | USB-C iPad, exact model/iPadOS / 确切型号与 iPadOS | Separate transfer/recovery test for Windows setup path / Windows 配置路径单独测试转接及恢复 | Not tested; experimental / 未测，实验性 |

Also test unplugging before/during/after configuration, a wrong/unsupported module, two connected modules, a busy serial port, malformed replies, operation timeout, unrelated internet routes and a mismatched recovery snapshot. Hardware tests must document whether an interrupted write changed persistent settings. / 还需测配置前中后拔线、不支持模块、双模块、串口占用、异常响应、超时、其他网络干扰及备份不匹配；中断写入需确认是否改变持久配置。

An “Online” claim needs evidence that internet traffic uses the dongle; successful AT commands or another active Wi-Fi connection are insufficient. Restore must be demonstrated on the same physical device and firmware. / “已联网”必须证明流量经过模块，AT 成功或其他 Wi-Fi 可用均不足；恢复需在同一真机与固件上验证。

## Review records / 审核记录

| Independent reviewer / 独立审核人 | Score / 分数 | Open P0/P1 / 未关闭问题 | Evidence / 证据 | Result / 结论 |
| --- | --- | --- | --- | --- |
| Engineer 1 | Pending / 待评 | Pending / 待查 | Pending / 待提交 | Not accepted / 未通过 |
| Engineer 2 | Pending / 待评 | Pending / 待查 | Pending / 待提交 | Not accepted / 未通过 |
| Engineer 3 | Pending / 待评 | Pending / 待查 | Pending / 待提交 | Not accepted / 未通过 |

Hardware gaps cannot be waived by averaging scores. Re-review the final revision after fixes. Record the public commit/tag, artifact checksums and reviewer evidence together before calling the project a mature MVP. / 不得用平均分豁免真机缺口；修复后复审最终版本；成熟 MVP 结论需绑定公开提交或标签、构建校验值及审核证据。
