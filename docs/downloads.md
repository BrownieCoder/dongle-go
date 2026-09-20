# Download the development preview / 下载开发预览

**These are runnable diagnostic previews, not hardware-approved one-click internet tools. Real configuration is locked until physical qualification. / 可运行的诊断预览，尚非真机验收通过的一键上网工具；真实配置仍锁定。**

The following packages were built from commit `296a0460ea465416d6b41e76313047dfd8c144c7`. CI unpacked and launched each package and completed all eight hardware-free GUI smoke checks. / 以下构建均经 CI 解压、实际启动，并完成八项无硬件界面验证。

| Your computer / 你的电脑 | Download / 下载 |
| --- | --- |
| Apple Silicon Mac (M-series) / M 系列 Mac | [macOS ARM64 preview](https://github.com/BrownieCoder/dongle-go/actions/runs/35503009255/artifacts/10603145795) |
| Windows x64 / 64 位 Windows | [Windows X64 preview](https://github.com/BrownieCoder/dongle-go/actions/runs/35503009255/artifacts/10602717786) |

**GitHub sign-in is required for Actions artifact downloads.** These temporary artifacts can expire; the [Actions page](https://github.com/BrownieCoder/dongle-go/actions) holds newer runs and the repository retains reproducible build instructions. No stable release or automatic updater is provided yet. / **Actions 下载需要登录 GitHub**，临时产物可能过期；可在 Actions 页面查找更新构建。当前没有正式稳定版或自动更新。

## Open it / 怎么打开

1. Download the package matching your computer. GitHub wraps the distribution ZIP in an artifact ZIP; extract both layers completely. / 下载对应系统文件，将 GitHub 外层 ZIP 和内部软件 ZIP 完整解压。
2. On Mac, open `package/Dongle Go.app`. On Windows, open `Dongle Go/Dongle Go.exe`, keeping its adjacent `_internal` folder. Python installation is not required for these packages. / Mac 打开 `package/Dongle Go.app`；Windows 打开 `Dongle Go/Dongle Go.exe`，保留旁边的 `_internal` 文件夹，无需安装 Python。
3. Use the top-right language selector. Connect a module, select the final device, and click **Check connection / 检查连接**. Current unvalidated firmware stays read-only. / 右上角可切换语言，连接模块、选择最终设备、点击检查；未验收固件只做诊断。

These builds are unsigned or ad-hoc signed, not Apple-notarized or Windows Authenticode-signed. OS trust prompts may appear. Verify the source and checksum; do not turn off system security or driver signature enforcement. If policy blocks the app, stop and use an approved development environment. / 当前未做正式签名或公证，系统可能提示无法验证发布者。请核对来源与校验值，不要关闭系统防护或驱动签名验证；组织策略禁止时应停止并使用获准的开发环境。

For a no-hardware demo, use the [source instructions](../README.md#run-the-development-preview) with `--demo`. Packaged executables also accept `--demo` when launched from a terminal. / 没有硬件时可按源码说明运行 `--demo`，打包程序也接受此参数。

## Checksums / 校验值

SHA-256 values refer to the **inner distribution ZIP**, not GitHub's outer artifact ZIP. / SHA-256 对应内部软件 ZIP，不是 GitHub 外层 ZIP。

```text
243ae727c690d10b01d2ffd096bef427154b214354f091b9c75fcaedba1c513d  Dongle-Go-Darwin-arm64-preview.zip
ee1ec5b2923adf54e33869c35a4513b2b6a8d3ff7ca895d4f1201328b31a98d7  Dongle-Go-Windows-AMD64-preview.zip
```

macOS: `shasum -a 256 FILE.zip`. Windows PowerShell: `Get-FileHash FILE.zip -Algorithm SHA256`.
