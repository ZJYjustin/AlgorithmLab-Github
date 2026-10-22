# 构建与安装

## 构建环境

- Windows 与 Python 3.10 或更新版本。
- PyCharm 2025.2.x，安装目录包含 JBR 编译工具和 IDE 库。
- Visual Studio 2022 x64，以及“使用 C++ 的桌面开发”工作负载。

当前脚本构建两个 IDE 入口时都需要指定 PyCharm 安装目录；`--only pycharm` 可只构建 PyCharm 插件。

```sh
python build_plugins.py --pycharm "C:\IDE\PyCharm" --only pycharm
python build_plugins.py --pycharm "C:\IDE\PyCharm" --visual-studio "C:\IDE\VS2022"
```

上述路径为示例占位，需替换为实际安装目录。源码和 C/C++ 测试文件暂应保存在英文路径下。
构建中间文件位于 `.build/`，安装包位于 `dist/`。
PyCharm 插件版本为 0.2.0，Visual Studio 插件版本为 0.2.1。

## VSIX 构建工具

Visual Studio 打包使用 [Microsoft.VSSDK.BuildTools 17.14.2142](https://www.nuget.org/packages/Microsoft.VSSDK.BuildTools/17.14.2142)。
首次构建从官方 NuGet 下载到 `.tools/`，并检查固定 SHA256：

```text
92526da94f2834b9ad48d8bed80edae83f522e73640ce40259366e917f1ef6b2
```

离线构建可通过 `--vssdk-home` 或 `VSSDK_BUILDTOOLS_HOME` 指定已解压工具目录。
SDK 只用于构建，不进入插件运行时负载。

`package_vsix.py` 调用官方 `VsixUtil` 任务生成清单和包元数据，并检查 `catalog.json`、`manifest.json`、扩展清单和运行时路径。
仅把 DLL 和 XML 压缩成 ZIP 不能替代这一过程。

## PyCharm 安装

1. 在 Settings → Plugins 中选择“从磁盘安装插件”。
2. 选择 `dist/AlgorithmLab-PyCharm-0.2.0.zip`，按提示重启。
3. 打开已保存的 Python 文件，通过 Tools → Algorithm Lab 使用可视化入口。
4. 如有需要，通过“设置 Python 解释器”指定本机 `python.exe`。

## Visual Studio 安装

1. 关闭 Visual Studio，运行 `dist/AlgorithmLab-VisualStudio2022-0.2.1.vsix`。
2. 按安装器提示选择目标 Visual Studio 2022 实例。
3. 重新打开 IDE，打开已保存的 `.c` 或 `.cpp` 文件。
4. 使用编辑区顶部的 Algorithm Lab 工具条，必要时先设置 Python 解释器。

取消工具条勾选可关闭当前编辑窗口入口；IDE 插件管理页面可停用或卸载整个扩展。

## 安装失败排查

若安装器显示“调用的目标发生了异常”，通过安装日志查看内层异常。
`InvalidExtensionPackageException` 表示扩展包读取失败，应先检查包格式和清单。
如果安装成功但入口不出现，应检查目标 IDE 版本、扩展启用状态、文件类型和加载日志。
包格式检查通过不能代替 IDE 内实际加载与执行检查。
