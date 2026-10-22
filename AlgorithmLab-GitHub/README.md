# Algorithm Lab Local

在本地观察自己写的 Python、C、C++ 教学代码。普通 Python 可以逐行回看变量；添加记录接口后，可以播放矩阵、数组和日志动画。

本项目由学习需求出发，在 AI 辅助下实现和整理。设计受到 [Algorithm Visualizer](https://github.com/algorithm-visualizer/algorithm-visualizer) 启发，与其没有官方隶属关系。
当前版本为 **0.2.1 公开整理版**（修复 Visual Studio 安装包；PyCharm 入口仍为 0.2.0），使用本项目自己的 `algorithm_lab.py` 和纯 C/C++ 记录头文件，不包含上游 `tracers.py`、`tracers.cpp` 或网页项目的代码副本。

## 先运行一次

需要 Python 3.10 或更新版本；Python 部分只使用标准库，无须 pip 安装依赖。

```sh
python lab.py examples/banker.py
python lab.py examples/plain_python.py --mode lines
```

运行完成后会自动在浏览器打开回放页面，支持播放、暂停、上一步、下一步、进度拖动和速度调整。
[银行家算法演示页](docs/demo-banker.html) 可以下载后用浏览器离线打开；GitHub 默认显示 HTML 源码，点击网页链接不等于已部署 GitHub Pages。

银行家算法默认得到 `P1 → P3 → P4 → P0 → P2`，最终 `Work = [10, 5, 7]`。
把 `examples/banker.py` 的 `available = [3, 3, 2]` 改成 `[0, 0, 0]` 再运行，就会得到不安全状态。
不安全不等于已经死锁；示例实现安全性检查，尚未实现完整的资源请求试分配流程。

## 两种模式

| 入口 | 用途 | 呈现方式 |
| --- | --- | --- |
| 可视化当前文件 / 默认 auto | 代码包含本项目记录接口 | 数组、矩阵、选中标记和日志 |
| Python 逐行模式 / `--mode lines` | 普通 Python 或希望看每行变量 | 行高亮、函数名和局部变量 |

两者都是执行完成后的回放。播放速度不会改变程序运行速度；回退不会撤销文件写入等副作用。

## 添加自己的动画

```python
from algorithm_lab import ArrayView, Journal, step

values = [3, 1, 2]
view = ArrayView('数组', values)
log = Journal('过程')
step()

values[0] = 7
view.update(0, values[0])
log.write('把下标 0 更新为 7')
step()
```

将代码保存在项目中，通过 `python lab.py your_file.py` 运行。`step()` 自动记录调用处的行号。
在 `lab.py` 入口之外直接运行脚本时，若脚本不在仓库根目录，需要自行配置项目搜索路径；直接运行不会自动启动播放器。

## C 和 C++

第一版 C/C++ 编译入口面向 Windows 和 Visual Studio 2022，需要“使用 C++ 的桌面开发”工作负载。

```sh
python lab.py examples/banker.c
python lab.py examples/banker.cpp
```

示例使用 `include/algorithm_lab_c.h`，只依赖 C 标准库，不包含 nlohmann/json 或 libcurl。
这是单源文件教学入口，尚不读取复杂工程的链接参数，也不自动获取任意 C/C++ 变量。

## IDE 插件

两个 IDE 入口共用同一份运行器，浏览器负责播放界面。源码在 `plugins/`，不随仓库分发 IDE SDK 或 Python 解释器。

在 Windows 上构建 PyCharm 插件：

```sh
python build_plugins.py --pycharm "YOUR_PYCHARM_INSTALLATION" --only pycharm
```

同时构建 Visual Studio 扩展：

```sh
python build_plugins.py --pycharm "YOUR_PYCHARM_INSTALLATION" --visual-studio "YOUR_VS2022_INSTALLATION"
```

将占位目录替换为本机真实安装目录。输出在 `dist/`。
Visual Studio 打包使用 Microsoft.VSSDK.BuildTools 17.14.2142，首次构建会从官方 NuGet 下载并校验后保存在 `.tools/`。
也可以用 `--vssdk-home` 指定已解压的该工具包目录。工具只用于构建，不进入扩展负载或源码上传包。
0.2.1 起使用微软 SDK 生成必需的 `catalog.json` 与 `manifest.json`，不再把普通 ZIP 当作 VSIX 交付。排查说明见 [VSIX 安装修复](docs/VSIX_INSTALL_FIX.md)。
PyCharm 版本范围限定 2025.2.x；Visual Studio 扩展限定 2022 x64。其他版本尚未验证。

PyCharm 中用“从磁盘安装插件”安装 ZIP，重启后选择 Tools → Algorithm Lab。普通绿色运行按钮不会自动触发本插件。
首次运行可以通过“设置 Python 解释器”选择本机 `python.exe`，也可以选择项目 `.venv` 的解释器。
Visual Studio 安装 VSIX 后，在支持的源文件编辑区上方使用工具条。复选框可关闭当前窗口入口；插件管理页面可停用整个扩展。

## 阅读源码

1. `examples/banker.py`：算法逻辑与记录语句。
2. `algorithm_lab.py`：用数据视图和 `step()` 生成快照。
3. `worker.py`：子进程执行 Python，记录逐行变量或导出动画快照。
4. `lab.py`：选模式、启动进程、限制时间、生成 HTML。
5. `protocol.py`：把 C/C++ 记录命令还原成画面。
6. `viewer.html`：播放控件、代码高亮、矩阵与日志渲染。
7. `plugins/`：编辑器按钮如何启动 `lab.py`。

学习手册见 `docs/AlgorithmLab学习手册.pdf`；版本迁移见 [MIGRATION](docs/MIGRATION.md)，发布步骤见 [PUBLISHING](docs/PUBLISHING.md)。
手册介绍 0.2.0 的总体架构；Visual Studio 打包方式以本次修复说明和当前构建脚本为准。

## 验证

```sh
python -m unittest discover -s tests -v
```

原生编译检查仅在具备 MSVC 的 Windows 环境运行；其他平台会跳过这些检查。IDE 插件需要本机安装 IDE 后构建和验证，CI 不代表插件已通过所有版本兼容性审核。

## 限制

- 先执行后回放，不是实时调试器；不能在运行中暂停、修改变量或附加进程。
- Python 普通追踪仅覆盖当前文件和当前线程；最多记录 4000 步，变量内容会截断。
- 暂不支持交互式 stdin、多文件 C/C++ 工程和图树专用渲染。
- 运行代码具有本机执行权限，不是安全沙箱；请只运行自己信任的代码。
- 报告包含源代码和文件路径，分享前检查是否有私人内容。

## 许可与来源

本公开包的代码与文档采用 [MIT License](LICENSE)，署名为 Algorithm Lab contributors，包含 AI 辅助开发说明。
上游项目和分发边界见 [THIRD_PARTY](THIRD_PARTY.md)。不要把旧本地研究版的 `vendor/`、`source-reference/` 或旧插件 ZIP/VSIX 混入这个公开仓库。
