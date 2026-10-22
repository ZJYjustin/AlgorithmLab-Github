# Visual Studio 2022 安装包修复

修复日期：2026-10-23。公开版 VSIX 版本 0.2.1；使用旧 tracer 的本地版对应修复包为 0.1.1。

## 用户遇到的问题

界面显示“调用的目标发生了异常”。本机 VSIX 安装日志的内层异常为：

```text
Microsoft.VisualStudio.ExtensionManager.InvalidExtensionPackageException:
The file is not a valid VSIX package.
```

失败发生在读扩展包阶段，与 Python 虚拟环境、算法代码和 C++ 编译器无关。

## 原因和修改

旧构建脚本把扩展文件与两个 XML 文件直接压成 ZIP。该文件能被 ZIP 工具和 OPC 读取，但缺少现代 VSIX 所需的 catalog.json、manifest.json，不能被 Visual Studio 安装器接受。
新版由 Microsoft.VSSDK.BuildTools 17.14.2142 的 VsixUtil 任务生成安装包，同时保留文件负载的正确相对路径。

SDK 包的官方来源：
https://www.nuget.org/packages/Microsoft.VSSDK.BuildTools/17.14.2142

固定 NuGet 包的 SHA256：
`92526da94f2834b9ad48d8bed80edae83f522e73640ce40259366e917f1ef6b2`

源码中的 package_vsix.py 会验证必要元数据和负载路径。两个新增测试防止再次交付只有 XML 的普通 ZIP，以及运行时目录前缀重复的包。

## 验证范围

- 旧包由本机 Visual Studio 2022 ExtensionEngine 的 InstallableExtensionImpl 构造读取时被拒绝。
- 修复后的本地版和公开版包，由同一读取器成功读取。
- SDK 构建阶段启用了清单校验，未使用 noValidate。
- 读取成功证明扩展包格式可识别，不代表已经完成用户安装或在 IDE 内显示工具条。

## 安装

关闭 Visual Studio 后，双击对应修复版 VSIX，在安装器中选择 Visual Studio 2022 并完成安装。
重新打开编辑器，打开已保存的 .c 或 .cpp 文件后，检查代码区顶部是否出现 Algorithm Lab 工具条。
保留现有 Python、C++ 环境；不需要为了这个打包错误重新安装开发环境。

来源：[Microsoft 关于现代 VSIX 清单的说明](https://learn.microsoft.com/en-us/archive/msdn-magazine/2017/august/visual-studio-creating-extensions-for-multiple-visual-studio-versions)。
