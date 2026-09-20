# Contributing / 参与开发

Use Python 3.12 with Tk. Install with `python -m pip install -e '.[build]'`, then run `python -m unittest discover -s tests -v` and `python scripts/check_docs.py`. Linux GUI tests require a display or `xvfb-run -a`.

Keep demo independent of every hardware API. Never approve a hardware profile using only unit tests, USB IDs or a marketing model name. Publish exact, redacted physical validation evidence using [the matrix](docs/hardware-validation.md). Unsupported firmware remains read-only. Do not add automatic VID/PID rewrites, unsigned driver installation, SIM PIN guessing or traffic-route claims based on unrelated Wi-Fi.

Real-device changes need a narrowly verified transport/profile, a durable recovery record, bounded operations and a hardware-bound reconnect check. No raw modem responses, SIM identifiers, device serials, APN values or personal logs in issues. Synthetic fixtures must stay clearly labeled.

中文：使用带 Tk 的 Python 3.12。演示模式不得调用硬件；新增真实配置必须附精确型号、固件、接口及目标系统的脱敏实测记录。单元测试不能替代真机验收。不要提交 SIM 标识、设备序列号、APN 或私人日志。
