# Beginner guide

[简体中文](getting-started.zh-CN.md) · English

**This is a development preview. The flow below describes the intended physical-device workflow; it is not a claim that your dongle is supported.** Use a demo only to explore the interface: simulated success does not configure hardware or prove internet access.

The current factory USB backend performs read-only diagnostics. It does not configure, reset or reboot a dongle and does not install a Windows USB driver. If no compatible driver is available, stop at diagnosis and wait for a validated workflow.

## 1. Prepare your SIM and cable

Use a physical SIM with an active data plan. Insert it according to the dongle’s instructions while the dongle is unplugged. Use a data-capable USB cable. For the first attempt, connect directly to the computer rather than through a hub.

## 2. Pick the device that will use the internet

- **Mac:** configure and use the dongle on the Mac.
- **Windows:** configure and use it on the Windows PC. USB driver availability is part of compatibility testing; never install an unsigned driver from an unknown tutorial.
- **USB-C iPad:** configuration must happen on a Windows PC or Mac first. After configuration, the dongle moves to the iPad. iPadOS compatibility and available USB power must be checked separately.

## 3. Connect and check compatibility

The app must identify the supported module before offering a configuration action. A USB device name by itself is insufficient to prove compatibility. If the module is unsupported or identification is incomplete, stop and follow the diagnostic guidance. Do not select an unrelated serial device to make detection pass.

## 4. Configure USB internet

The intended button is **Set up internet**. A configuration may briefly disconnect and reconnect the dongle. Keep the cable connected while the operation is in progress. Do not run another modem-management tool at the same time.

“Configuration saved” and “Online” are different results. A SIM problem, weak signal, network settings or USB power can prevent internet access after a successful configuration.

## 5. Confirm internet access on the destination device

Do not treat a working browser on your home Wi-Fi as proof that the dongle works. Check that the destination OS has a USB network connection and that traffic uses it. During formal acceptance, disconnect other internet connections and verify mobile-data traffic. This may consume your plan’s data.

For iPad, connect the configured dongle and check Settings for an Ethernet entry. Its appearance alone does not prove internet access. If it never appears, return to the computer for diagnosis; do not repeat unknown configuration commands on the iPad.

## 6. Verify everyday use

Before relying on the dongle, test unplugging and reconnecting it, rebooting the computer and waking it from sleep. iPad needs its own reconnection test. A single successful setup is not sufficient for the mature-MVP acceptance gate.

If a step fails, use [troubleshooting](troubleshooting.md). The public release must include a validated recovery procedure before it can be recommended to beginners.
