# 漫画 UI 独立审查：工程师 3

2026-09-20。审查者未参与实现，仅修改本报告。范围：新版 `app.py`、`ui.py`、`i18n.py`、GUI 测试、依赖与资源打包、资产及许可说明。硬件配置与真机网络验收不在本轮通过结论内。

**最终软件评分 96/100，通过本轮漫画 UI 软件审查；硬件仍未验收。** 初审 94 分与待补证据保留在下文；末节记录新版分发 CI 独立核实结果。旧版纯 Tk UI 的 CI 未被用于替代本轮新增 CustomTkinter/Pillow/PNG 资产验证。

## 独立发现及修复复验

首次直接运行新版 6 项 GUI 测试，4 项通过、2 项失败：

1. 小窗口焦点滚动后，Help 底部实际 Y=700，测试允许最大 Y=699。建议对滚动留出边距，避免边缘裁切。实现者增加 8px 余量后复验通过，没有通过扩大测试容差掩盖问题。
2. 键盘语言切换断言仍要求标题包含“模块”，但新版中文标题为“准备好，一起连接。”；这是过时测试断言。改为与翻译表目标文案比较后复验通过。

同时发现新依赖许可证已经落盘，但清单和出处记录尚未更新；已反馈并复核修复。CustomTkinter 5.2.2、Pillow 11.3.0、darkdetect 0.8.0 和 packaging 的许可证清单已补。Pillow 完整 wheel notice 包含 native 库条款。实际平台包仍需要与其真实组件核对，不能由本地版本外推所有发布产物。

## 直接执行的验证

- `.venv-tk/bin/python -m unittest discover -s tests -p test_app.py -v`：修复后 **6/6 通过**。经授权使用 macOS 窗口服务、真实 CTk 根窗口与事件循环，所有设备服务模拟，无硬件访问。
- `.venv-tk/bin/python -m unittest discover -s tests -p test_i18n.py -v`：**4/4 通过**。
- `.venv-tk/bin/python scripts/check_docs.py`：通过。

真实 GUI 测试覆盖检查/模拟配置/恢复、双语切换、目标变化撤销 ready、未知固件禁用配置、空列表处理、只读选择器键盘循环、禁用控件拒绝键盘动作，以及 780×620 小窗口中焦点进入 Help 后自动显示。

## 安全、状态和资源判断

UI 布局拆到 ModernView，后台操作仍通过工作线程和 Queue，Tk 主线程负责渲染。忙时目标按钮与设备选择器禁用，目标选择方法另有 busy 防护；换目标撤销 ready。重设计没有替换核心设备识别、固件白名单、恢复与互斥实现，`core.py` 指纹与上一轮一致。

模拟完成、准备配置、待目标设备验证分别显示不同标题，配置成功不显示已验证联网。只读 USB 和空固件白名单边界保持。绿色完成图标代表当前软件步骤完成，其相邻文案仍明确互联网待验证。模式 chip 常驻顶部；小屏隐藏插画侧栏，任务区可滚动，操作不依赖漫画内容。

新版 CTk/Pillow 版本在 `pyproject.toml` 固定。PNG 声明为 Python package data，运行时从模块相邻 assets 读取；PyInstaller 收集 `customtkinter` 及 `dongle_go` 数据，符合轮子安装与冻结路径。图标以本地 Pillow 绘制，没有远程资源加载。字体按系统可用项回退，中英文用户文案在翻译表中，品牌装饰文字保留英文不影响操作。

新增 FocusButton/KeyboardComboBox 使用 CTk 私有 `_canvas`、`_entry`，滚动使用 `_parent_canvas`；在固定版本可用，但依赖升级必须运行键盘与焦点回归。未验证读屏、Windows DPI 缩放或完整辅助功能矩阵，不声称这些已通过。

## 当前评分

| 类别 | 分数 | 依据与保留 |
|---|---:|---|
| 产品正确性 | 29/30 | UI 状态门禁与后台隔离保留；没有穷举平台与时序异常。 |
| 易用与双语 | 24/25 | 新视觉、清晰动作层级、双语、键盘和小窗回归通过；真实新手及辅助技术尚未验收。 |
| 分发可靠 | 22/25 | 依赖/资源/许可接入代码完整；新版冻结包与 CI 结果尚待核实。 |
| 测试与文档 | 19/20 | 直接执行 6 项 GUI 和 4 项翻译检查、文档检查；不替代设备场景验证。 |
| 合计 | **94/100** | 无本轮发现的未解决 P0/P1；等待新版产物证据。 |

## 审核指纹

- `app.py`: `ba8071a70267d53458f26b1629f3380c0759c16b06ba5c806ff345df0614ef8e`
- `ui.py`: `5f77f857db4438c128ef00bdbaed8e777da8ebe9b5bbaec1242e6ef8b0b85123`
- `i18n.py`: `ac5809a9fe4c76791a1ded35c94c84a8c9ec464bd3ace27deebcb3f62fc66b94`
- `core.py`: `d780d845f1f3c5a74c96dd331b4e15f1a98de5acb7f069cfd4237c55f048a210`
- `scripts/build.py`: `8377739bcd3b8292620a0c80f727dd56b0d6325d8ae371ea80f4fa7534245a67`

**硬件尚未验收，软件 UI 分数不能用于宣称真机兼容或成熟 MVP 完成。**

## 新版分发证据与最终签核

独立执行 `gh run view 35504437091 --repo BrownieCoder/dongle-go --json headSha,status,conclusion,jobs,url`，核实 [新版 CI](https://github.com/BrownieCoder/dongle-go/actions/runs/35504437091) 已完整结束，三平台均 `success`，对应提交 `9003c9c11b0eb934c9bca3931e794b0814e56280`。通过 `git diff` 确认本次审核的源码、依赖、构建及 GUI 测试与该提交无差异。

- [Windows job 106061745294](https://github.com/BrownieCoder/dongle-go/actions/runs/35504437091/job/106061745294)：原生测试、构建、解压 ZIP 后启动 smoke、报告与分发产物上传成功。
- [macOS job 106061745313](https://github.com/BrownieCoder/dongle-go/actions/runs/35504437091/job/106061745313)：上述对应步骤全部成功。
- [Linux job 106061745171](https://github.com/BrownieCoder/dongle-go/actions/runs/35504437091/job/106061745171)：虚拟显示下测试及文档检查成功；不因此声明有 Linux 安装包。

读取主代理下载的两平台 CI smoke JSON，均为 `ok: true`，完整包含 8 项：真实窗口、serial/USB 导入、bundled libusb、模拟检查/配置/恢复、语言切换，且 `hardware_accessed` 与 `internet_verified` 均为 false。下载报告与 checksum 属于 CI 证据复核，没有被写成审查者亲自操作 Windows 桌面。

CI 记录的分发 SHA-256：

```text
24adba50bcab175d4f733f751e1967c74d904f68980b550c5bf0213d157bd83a  Dongle-Go-Windows-AMD64-preview.zip
1e4023b3a7e469a387ff9c2bb63824fd13069eac657a9c7107a9536f4490c686  Dongle-Go-Darwin-arm64-preview.zip
```

**最终：产品正确性 29/30 + 易用与双语 24/25 + 分发可靠 24/25 + 测试与文档 19/20 = 96/100。** 新版双平台冻结包运行证据补齐分发 2 分；其余扣分保留。无本轮发现的未关闭 P0/P1，焦点显示、过时测试断言和依赖清单问题已关闭。

签核限于所列提交的开发预览软件。仍未覆盖消费者系统签名/公证、读屏、多 DPI、真实新手试用及 Windows 11 干净系统驱动体验；真机与 iPad 目标设备验收继续待后续完成。
