# Dongle Go

简体中文 · [English](README.md)

**让支持的大疆一代 4G 模块，更容易变成 USB 上网卡。**

目标很简单：插好模块，检查是否支持，点一下完成上网配置。这里的“上网卡”需要通过 USB 连接设备，**模块不会因此直接变成无线 Wi-Fi 热点**。

> **当前是开发预览，尚未通过真机验收。** 目前没有任何硬件与系统组合完成真机兼容性验证。请不要仅凭本项目购买模块。“成熟 MVP”需要三位独立工程师分别达到 95/100 分，并完成[真机验收](docs/acceptance.md)；软件模拟通过不等于硬件可用。

![九宫格小白教程](assets/tutorial-zh.png)

## 先准备这几样

- 大疆**第一代** 4G 模块，内部为兼容的移远 EG25-G。外观相似或第二代产品不代表支持。
- 已开通流量的实体 SIM 卡。
- 一根能传输**数据**的 USB 线，仅充电的线不行。
- 用于首次配置的 Windows 电脑或 Mac。真实设备兼容性仍待验证。

## 你想让哪台设备上网？

| 最后使用流量的设备 | 在哪里配置 | 当前状态 |
| --- | --- | --- |
| Mac | 在这台 Mac 上配置 | 实现目标，待真机验证 |
| Windows 电脑 | 在这台电脑上配置 | 实现目标，待驱动和真机验证 |
| USB-C iPad | 先在 Windows / Mac 配置，再接到 iPad | 实验性目标，需单独验证 iPadOS、供电和拔插恢复 |
| Lightning iPad、安卓、Linux、路由器 | 暂无支持流程 | 不在首版验收范围 |

**iPad 是配置后使用模块的设备，不能直接运行本项目的电脑配置程序。** Mac 能上网不代表 iPad 一定能用；外接模块也不等于把 Wi-Fi 版 iPad 改成了内置蜂窝版。

## 运行开发预览

目前还没有通过真机验收的小白安装包。源码运行建议使用带 Tkinter 的 Python 3.12（固定版本的 USB 二进制依赖提供 CPython 3.11–3.13 wheel，尚无 3.14 wheel）；这是开发者预览，尚不是最终的“两步使用”体验。在项目目录创建环境：macOS 用 `python3 -m venv .venv`；Windows 用 `py -3.12 -m venv .venv`。

macOS 用 `source .venv/bin/activate` 激活环境；Windows PowerShell 用 `.venv\Scripts\Activate.ps1`。然后运行：

```sh
python -m pip install -e .
python -m dongle_go --demo
```

演示使用模拟设备，不会配置真实模块。如需真实设备诊断，运行不带 `--demo` 的 `python -m dongle_go`。**当前已验证固件白名单为空，因此真实配置仍被禁止。** 真实诊断通过选定的串口或严格匹配的出厂 USB 接口（`2ca3:4006`）查询身份与状态。出厂 USB 路径只读，不能配置或重启模块；界面支持识别不等于真机验证通过。请只选择要操作的模块。Windows 需要现有的兼容 USB 驱动，程序不会安装或替换驱动。

界面提供**检查连接**、**一键开通上网**和**恢复原配置**，可以选择 Mac、Windows、iPad 作为目标。可以选择，不代表该组合已通过兼容验证。macOS / Windows 安装包需要目标系统与真机验收后才能正式发布。

真机到位后再开展硬件验收。在此之前，这个预览只用于体验界面、自动化验证及有限的设备诊断。

## 从这里开始

- [小白教程](docs/getting-started.zh-CN.md)：需要准备什么、怎么理解操作步骤。
- [遇到问题怎么办](docs/troubleshooting.zh-CN.md)：找不到模块、SIM 无法使用、不能联网时的下一步。
- [验收标准](docs/acceptance.md)：独立审核评分与真机测试矩阵。

产品的主要动作是**一键开通上网**，不是“刷固件”。配置可能改变模块的 USB 接口模式，并让模块短暂断开重连。刷写固件、修改 IMEI、绕过运营商限制、解锁大疆内置 eSIM 均不属于本项目功能。

## 使用前了解

你仍需要有效的 SIM 套餐、可用信号和足够的供电。软件不能代替运营商开卡，也不能在没有信号的地方提供网络。真实联网测试可能消耗套餐流量。在公开 issue 中不要粘贴 SIM 标识、电话号码、短信、密码或未经脱敏的诊断信息。

## 技术背景

兼容性研究参考[社区 USB 配置项目](https://github.com/wlzh/dji-4g-vohive-mac)、[DJOneHub](https://github.com/ZenGeekLabs/DJOneHub) 和 [4G Connect](https://github.com/WongLoki/4G-Connect)。这些是独立项目，其功能不代表 Dongle Go 已经通过验证。本项目与大疆、移远不存在官方关联。
