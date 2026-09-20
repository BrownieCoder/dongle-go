# UI 重设计独立复审：工程师 2

2026-09-20；审核者未参与 UI 实现。本轮只编写本报告，没有修改实现或测试文件。

**当前复审软件评分 96/100，无本轮发现的未关闭 P0/P1/P2。** 这是代码、控件交互与软件故障隔离评分；不代表 Windows 本机、真机兼容或成熟 MVP 交付验收通过。

## 范围

完整阅读新 ui.py、迁移后的 app.py、i18n.py、测试、依赖与构建差异，并核对 core.py、transport.py、usb_transport.py 与前次复审指纹一致。重点检查控件迁移后是否改变 ready/busy 门禁、操作线程、关闭行为、未知固件处理及 demo 隔离。

## 独立执行证据

1. `PYTHONPATH=src:tests .venv-tk/bin/python -m unittest test_core test_transport test_usb_transport test_i18n -v`：**52 项通过**。
2. `PYTHONPATH=src:tests .venv-tk/bin/python -m unittest test_app -v`：请求提升权限访问 macOS 窗口服务，**4 项真实 CTk GUI 测试通过**。覆盖 demo 检查/配置/恢复、中英切换、变更目标撤销 ready、未知固件禁用写入、空设备列表清空选择。
3. 另外亲自运行真实 CTk 窗口下的独立故障注入脚本：用 threading.Event 暂停 service.plan，记录工作线程 ID，调用两次操作并尝试切换目标、关闭窗口、切换语言，随后释放工作线程。全部断言通过：
   - service.plan 工作线程与 Tk 主线程不同。
   - 忙时刷新、检查、配置、恢复、三个目标按钮、设备选择框均禁用。
   - 第二次 `_run` 不启动额外操作，目标不会改变。
   - 忙时关闭弹提示且不销毁窗口。
   - 忙时切中文保留 working 状态；完成后恢复 ready。
   - 在已经 ready 的状态下注入 unsupported 错误，会撤销 ready、禁用配置、显示 unknown，原始错误正文不进入界面。
   - 空闲时关闭正常退出。

以上 GUI 使用真实 CustomTkinter 控件与事件循环，设备服务为模拟；没有访问、枚举或配置硬件。没有把源程序启动当作安装包验收。

## 审核判断

控件外观移至 ModernView 后，配置仍必须经过 core.plan 与 core.apply 两次受保护检查。UI 的 ready 标志不会绕过固件白名单；核心单操作锁、设备身份复核及恢复持久化代码保持原样。按钮 invoke 与键盘入口保留 disabled 限制；目标按钮入口显式拒绝忙时切换。

后台 worker 只执行服务调用并向 Queue 写结果，状态和控件更新继续在 Tk 主线程的 `_poll` 中进行。语言切换只重绘文本，不重新触发硬件操作。工作中关闭不终止 daemon 工作线程；用户必须等操作完成后才能由正常关闭入口销毁窗口。发生错误会撤销 ready，不显示原始响应或路径。

新状态标题区分演示完成、准备配置与下一步设备验证；configured、iPad 和恢复结果不会被新 UI 改写成已验证真实联网。顶部模式标识与底部边界说明仍在。demo 构造路径和烟雾测试路径均使用模拟服务，核心隔离测试继续通过。

## 评分与限制

| 类别 | 得分 | 说明 |
|---|---:|---|
| 正确性 | 34/35 | 迁移后的状态、门禁与目标选择无回归；Windows 控件与 OS 集成未在本轮独立运行，保留 1 分 |
| 恢复与操作安全 | 25/25 | 原核心校验保持，忙时操作与关闭保护经独立阻塞注入验证；不将真机恢复计入软件分 |
| 测试 | 23/25 | 52 项非 GUI、4 项真实 GUI及独立并发/关闭脚本；完整多 OS/DPI 与辅助技术矩阵未执行，扣 2 分 |
| 维护性 | 14/15 | UI 与操作控制分离，依赖固定；FocusButton 依赖 CTk 私有 `_canvas`，升级需要专项回归，扣 1 分 |
| 总计 | **96/100** | 软件代码与交互范围 |

未亲自验收 Windows 安装包、所有屏幕/DPI 和键盘/读屏完整矩阵；未将其他审核者的视觉结果写作自身证据。真机尚未完成验收，默认已验证配置白名单为空、USB 通道仍只读。整体成熟 MVP 状态仍需由真机、目标系统与分发验收共同确定。

## 版本指纹

- app.py：`ba8071a70267d53458f26b1629f3380c0759c16b06ba5c806ff345df0614ef8e`
- ui.py：`79013647f2ac10a4e4d3a7be8013ee1c9a726d6b3e8a67fefec63bbd2fe06b34`
- core.py：`d780d845f1f3c5a74c96dd331b4e15f1a98de5acb7f069cfd4237c55f048a210`
- transport.py：`470bf0850f8d12212f503d2b5f6f4933181b12f9079ffa25c475860405f943b4`
- usb_transport.py：`0aea3acd2598fec31826fbb64bf38bdd8bb647569ee6d4628492a5cd8d870119`
