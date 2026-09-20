# Hardware qualification / 真机验收

**Test report template / 测试报告模板。** No scores, passes, or supported-profile entries may be inferred from this template. / 不得从模板推断通过、分数或支持配置。

Create one redacted report for each exact firmware × target OS × architecture combination. Cite reports from enabled profiles. Record failures as well as successes. / 每个固件、目标系统、架构组合独立建脱敏报告，并由启用配置引用；失败也必须记录。

## Report metadata / 报告信息

| Field / 字段 | Value / 值 |
|---|---|
| Tester and date / 测试者与日期 | — |
| Application version and commit / 程序版本与提交 | — |
| Module model and full firmware / 模块型号及完整固件 | — |
| USB IDs and interface descriptors / USB 身份及接口描述符 | — |
| Configuration computer, OS build, architecture / 配置电脑与系统架构 | — |
| Target device, OS build / 目标设备与系统 | — |
| Cable, hub, power arrangement / 线材、扩展坞与供电 | — |
| Operator, SIM type (no identifiers) / 运营商与卡类型（无标识） | — |
| Signed driver version/source/license, if relevant / 签名驱动版本来源许可 | — |
| Previous mode and restore method / 原模式及恢复方法 | — |

Never publish SIM identifiers, phone numbers, device serials, IMEI, account data, or raw transcripts. / 不公开卡片标识、电话号码、序列号、IMEI、账户或原始通信记录。

## Required cases / 必测项目

For each case record result (PASS/FAIL/NOT RUN), repetitions, timestamps, redacted evidence, and defect reference. / 每项记录通过/失败/未测、次数、时间、脱敏证据及缺陷编号。

| Case / 项目 | Minimum evidence / 最低证据 | Result / 结果 |
|---|---|---|
| Clean first setup / 首次配置 | Fresh supported device to target internet; full UI path / 全流程 | — |
| Actual egress / 真实出口 | Disable competing Wi-Fi/Ethernet or prove module-bound route and successful traffic / 隔离其他网络或证明绑定模块出口 | — |
| Cold power-off and reconnect / 断电重插 | 10 cycles, automatic recovery time each / 10 次，逐次恢复时间 | — |
| Computer restart / 电脑重启 | 10 cycles / 10 次 | — |
| Sleep/wake / 休眠唤醒 | 10 cycles / 10 次 | — |
| iPad target / iPad 目标 | Exact iPad model/OS, cold plug, real traffic, sustained power / 型号系统、冷插、流量、供电 | — |
| Windows clean install / Windows 干净系统 | Signed driver install, app setup, connect, uninstall / 签名驱动安装至卸载 | — |
| No SIM, PIN, no registration / 无卡、PIN、未注册 | Accurate actionable messages, no PIN guessing / 清晰提示，不猜 PIN | — |
| Unknown firmware and wrong device / 未知固件及错误设备 | No configuration writes / 无配置写入 | — |
| Multiple modems / 多模块 | Explicit selection; same device after re-enumeration / 明确选择且重连不串设备 | — |
| Busy interface / 接口占用 | Clear failure without driver takeover / 提示失败，不抢驱动 | — |
| Unplug during operation / 操作中拔出 | Bounded failure, no false success / 有界失败，不假成功 | — |
| Write rejection / 写入拒绝 | Stop before dependent writes; accurate state / 停止后续操作、状态准确 | — |
| Write timeout / 写入超时 | Uncertain-state handling and readback / 未知状态与重读 | — |
| Restore previous mode / 恢复原模式 | Verified readback and target behavior / 重读及行为验证 | — |
| Privacy / 隐私 | Logs/export/screenshots checked for identifiers / 日志导出截图检查 | — |
| Sustained connection / 持续连接 | At least 60 minutes with reconnect observations / 至少 60 分钟并记录重连 | — |

## Release decision / 发布决策

Unit tests and CI cannot establish hardware compatibility. A release requires evidence for every supported combination and no unresolved critical or high-severity defects. / 单元测试和 CI 不能证明硬件兼容；发布需要每个支持组合的真机证据，且没有未解决的严重或高优先级缺陷。

Until the relevant rows have evidence, label the combination unverified and keep configuration writes disabled for it. Publishing source code does not enable unsupported configurations. / 证据补齐前该组合标为未验证并关闭写入；公开源码不代表已开放不支持的配置。
