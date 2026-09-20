# Compatibility research / 兼容性研究

Research date / 研究日期: 2026-09-20. **No hardware combination is qualified by this document. 本文不代表任何组合已通过实机验证。**

## Product decision / 产品决策

The setup computer and the eventual internet device are different inputs. Default to this computer, but offer an explicit iPad target. Configure a supported USB network profile, not firmware flashing. / 配置电脑与最终上网设备是两个不同信息。默认给当前电脑使用，另设明确的 iPad 目标。本项目配置 USB 网络模式，不刷写固件。

| Target / 目标 | Candidate route / 候选路线 | Compatibility factors / 兼容条件 |
|---|---|---|
| macOS | ECM with OS DHCP / ECM 与系统 DHCP | Firmware, OS, architecture, cold plug, wake / 固件、系统、架构、冷插及唤醒 |
| Windows | ECM with vendor signed driver; investigate MBIM separately / ECM 配厂商签名驱动，另研究 MBIM | DJI USB ID binding, driver redistribution, clean-machine install, data connection / DJI 身份匹配、驱动分发、干净系统安装及拨号 |
| iPad | Configure on a desktop, then attach to iPad / 电脑配置后连接 iPad | Exact model/iPadOS, power, cold plug, real traffic / 具体型号与系统、供电、冷插及真实流量 |
| Linux | ECM with OS networking / ECM 与系统网络管理 | Permissions, competing modem manager, distribution / 权限、管理程序占用、发行版 |

Windows support must remain a project goal, but ECM is not a universal inbox-driver path. Microsoft lists MBIM, RNDIS and Windows 11 NCM. A Quectel support response explicitly requires an ECM driver for EG25-G on Windows. Do not disable driver signature enforcement or silently replace composite-device drivers. / Windows 是项目目标，但 ECM 不意味着通用免驱。微软列出 MBIM、RNDIS 和 Windows 11 NCM；移远技术支持明确要求 Windows EG25-G ECM 驱动。不得关闭驱动签名校验，或静默替换复合设备驱动。[Microsoft](https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/supported-usb-classes), [Quectel support](https://forums.quectel.com/t/help-with-ecm-mode-and-usbnet-with-eg25-g/34641), [vendor downloads](https://www.quectel.com/product/lte-eg25-g/)

## Evidence boundaries / 证据边界

- Quectel's guide maps network mode 1 to ECM and 2 to MBIM for the listed families; ECM establishes data internally and the host uses DHCP. This is not proof that every DJI-customized firmware preserves that mapping. Do not add generic dialing commands such as QNETDEVCTL without profile-specific proof. / 移远资料中的 1 为 ECM、2 为 MBIM，ECM 内部拨号、主机 DHCP；不能外推至所有 DJI 定制固件，也不能盲加拨号命令。[Vendor guide, §5.5](https://forums.quectel.com/uploads/short-url/ad1Nvyh6EolQIYjR1eY8hvH8OIZ.pdf)
- Community research contradicts itself about mode numbers and macOS compatibility. Resolve by descriptors and hardware observations, not by majority vote or cycling through unknown modes. / 社区对模式数值及 macOS 兼容性存在冲突，须由描述符和真机结果解决，不能试遍模式。[Conflicting research](https://github.com/CdricZhang/dji-cellular-as-modem/blob/main/RESEARCH_NOTES.md), [DJOneHub](https://github.com/ZenGeekLabs/DJOneHub)
- Some modules require a software reboot after a cold plug before macOS gets a network interface. iPad cannot depend on a desktop helper to repair that state. / 部分模块冷插后需要软重启才出现网卡，iPad 不能依赖电脑助手恢复。[4G Connect](https://github.com/WongLoki/4G-Connect)
- Apple's generic USB Ethernet support does not qualify this particular module. / Apple 支持 USB 以太网，不代表此模块已兼容。[Apple support](https://support.apple.com/en-ie/108894)
- Direct USB AT access can avoid rewriting USB VID/PID. Persistently changing USB composition is not a normal prerequisite and must not be performed automatically. Endpoint examples differ between projects. / 直接 USB AT 通信可避免重写 VID/PID。持久更改接口组合不是默认前提；不同项目端点例子也不同。[EG25-G Toolset](https://github.com/hey1874/eg25g-toolset)

## Backend design proposal / USB 后端设计建议

Keep an original transport implementation behind `query`, `set_usbnet`, and `reboot` operations. Discover serial ports where available; add a libusb bulk backend for macOS factory devices without serial drivers. / 以独立原创传输层实现查询、切换和重启；有串口时发现串口，无串口的 Mac 原厂设备使用 libusb bulk 后端。

USB IDs are discovery hints, never write authorization. Match device model and complete firmware to a qualified profile. Match USB interface/endpoint descriptors to a validated transport signature; if ambiguous, stop. Do not send AT probes across arbitrary vendor interfaces: they might be diagnostic, ADB, or QMI interfaces. / USB ID 仅用于发现，不授予写入权限。写入前精确匹配型号和完整固件；接口端点须匹配经验证的传输签名，歧义即停止，不能向任意厂商接口尝试 AT。

Use bounded reads, command deadlines, response-size limits, per-device exclusivity, and deterministic resource release. Do not reset USB configuration or detach a network driver merely to discover a device. Treat a timeout after a write as uncertain state; re-read before any retry. Re-enumeration must match the same physical device and never select another connected modem. / 限制读取大小及时间，设备互斥并可靠释放资源。发现时不重置配置、不移除网络驱动；写入超时后视为状态未知，重读再决定，重枚举必须绑定原设备。

Read only the information needed for compatibility and SIM readiness. Never include IMEI, IMSI, ICCID, serial numbers, phone numbers, or raw AT transcripts in public reports. A successful DHCP lease is not internet proof; only a request demonstrably routed through the module can establish that. Desktop completion for an iPad target must say “Ready for iPad verification”, not “iPad is online”. / 只读兼容性及 SIM 就绪所需信息，不公开设备/卡片标识或原始 AT 记录。DHCP 不等于上网，必须证明流量经过模块；给 iPad 配置完成不能显示 iPad 已联网。

## Licensing / 许可证

### USB implementation provenance / USB 实现溯源

The original Python backend in `usb_transport.py` consulted [4G Connect `usbat.go`, commit `2b0b7d476bc75f02252cc8904cf6b927282a365d`](https://github.com/WongLoki/4G-Connect/blob/2b0b7d476bc75f02252cc8904cf6b927282a365d/usbat.go), under [MIT](https://github.com/WongLoki/4G-Connect/blob/2b0b7d476bc75f02252cc8904cf6b927282a365d/LICENSE), for USB bulk AT framing and device identity facts. Its endpoint-sweeping algorithm is deliberately not used. [EG25-G Toolset, commit `17c69cca5ba28f6233652804cc644387c12f68e9`](https://github.com/hey1874/eg25g-toolset/blob/17c69cca5ba28f6233652804cc644387c12f68e9/eg25g.py), whose README declares MIT, identifies OUT `0x03` and IN `0x84` as AT endpoints. No noncommercial implementation was copied. / Python 后端为原创；参考 MIT 项目的 bulk AT 协议事实，不采用遍历端口探测，也未复制非商业代码。

The current read-only backend accepts only factory `2ca3:4006`, alternate setting zero, vendor interface class/subclass/protocol `ff/00/00`, exactly bulk endpoints `03/84`, and at most one interrupt-IN endpoint. Unknown or ambiguous descriptors stop before any AT command. This is a deliberately narrow candidate signature, not a hardware qualification claim. This backend does not implement configuration writes or reboot. Enumeration returns a bus/address reference and does not retrieve the USB serial string. / 当前只读后端限制上述精确候选描述符；未知或歧义即停止。该接口只支持诊断，配置及重启均禁用；枚举不读取 USB 序列号。

DJOneHub/VoHive-derived code uses PolyForm Noncommercial, so copying it into an MIT project is inappropriate. 4G Connect's current independent implementation is MIT, but its historic v0.1.x releases have different terms. libusb uses LGPL; include its notices and comply with the exact shipped version. Vendor driver redistribution requires its own license check. / DJOneHub/VoHive 衍生代码采用非商业许可，不能复制后声明 MIT。4G Connect 当前独立实现为 MIT，但历史版本不同；libusb 为 LGPL，须随发行遵守对应版本许可；厂商驱动分发需单独核对。[DJOneHub license](https://github.com/ZenGeekLabs/DJOneHub/blob/main/LICENSE), [4G Connect notices](https://github.com/WongLoki/4G-Connect/blob/main/THIRD_PARTY_NOTICES.md)
