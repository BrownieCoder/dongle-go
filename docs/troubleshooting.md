# Troubleshooting

[简体中文](troubleshooting.zh-CN.md) · English

The current build is a development preview with an empty firmware allowlist. Real configuration is intentionally unavailable until exact firmware versions pass hardware validation. The demo does not change this.

| What you see | What to do |
| --- | --- |
| Factory USB access unavailable | Confirm the app has its bundled libusb library. Close competing apps. A compatible existing Windows driver is required; do not replace drivers with Zadig or disable driver signing as a beginner workaround. This path remains diagnostics-only. |
| No module detected | Reconnect directly to the computer. Try a known data cable and another USB port. Detection alone cannot tell whether the cable is charge-only. |
| Unsupported module or firmware | Stop. Do not change device IDs or substitute a model to bypass the check. Report only the non-sensitive model/firmware details requested by maintainers. |
| Serial access denied or port busy | Close other modem tools. Reconnect and run Check connection. Do not grant broad administrator permissions as a default fix. |
| SIM missing or locked | Unplug before checking physical SIM seating. Resolve a PIN lock through your carrier or a supported device; repeated incorrect PIN attempts can lock the SIM further. |
| Configured but no internet | Check SIM activation/data balance, reception and carrier settings. A saved configuration is not an online result. |
| A website works, but dongle status is unclear | Your Wi-Fi or another connection may be carrying traffic. Use the destination OS’s network status and the hardware acceptance procedure to verify the actual route. |
| Module disconnects during setup | A short reconnect can be expected when USB mode changes. Follow the app’s status; if it times out, check the connection instead of repeatedly starting configuration. |
| iPad has no Ethernet entry | Check data cable and power; confirm the module works on its setup computer. iPad compatibility remains experimental. |
| Stops working after sleep/reboot | This is a compatibility failure, not a successful acceptance result. Record OS version, module firmware and the exact sequence; keep private identifiers out of reports. |

## Restoring settings

Use **Restore settings** only when the app has a usable snapshot for the connected module. Never use a snapshot belonging to another dongle. A restore button is not proof that restoration works on your firmware: recovery must pass physical-device testing before release. If recovery cannot be completed, stop and report the failure rather than trying unrelated AT commands.

## Asking for help

Include your OS version, app version, destination device, which step failed and the visible error. Remove phone numbers, ICCID/IMSI, IMEI, SMS, SIM PINs, passwords and tokens from screenshots or logs. Never post a raw configuration backup in a public issue. Maintain a private copy of the original diagnostic evidence if needed.
