# Algorithm Lab

本地运行的算法可视化学习工具，支持 Python 执行过程记录，以及 Python、C、C++ 的数组、矩阵和日志回放。

程序先执行并生成记录，再由浏览器播放。播放器支持暂停、前进、后退、进度跳转和速度调整。

## 快速开始

需要 Python 3.10 或更新版本。Python 运行器仅使用标准库，无须安装额外的 pip 依赖。

```sh
python lab.py examples/banker.py
python lab.py examples/plain_python.py --mode lines
```

运行结束后自动打开浏览器。默认报告保存在 `reports/`。

银行家示例实现安全性检查，默认安全序列为 `P1 → P3 → P4 → P0 → P2`，最终 `Work = [10, 5, 7]`。

## 支持的模式

| 模式 | 适用代码 | 显示内容 |
| --- | --- | --- |
| Python 逐行记录 | 普通 Python 脚本 | 即将执行的行、函数名和局部变量 |
| Python 算法动画 | 调用 `algorithm_lab` 的脚本 | 数组、矩阵、更新标记和日志 |
| C/C++ 算法动画 | 调用 `algorithm_lab_c.h` 的单源文件 | 数组、矩阵和日志 |

C/C++ 编译入口需要 Windows、Visual Studio 2022 和“使用 C++ 的桌面开发”工作负载：

```sh
python lab.py examples/banker.cpp
```

## 添加动画记录

```python
from algorithm_lab import ArrayView, Journal, step

values = [3, 1, 2]
view = ArrayView('数组', values)
log = Journal('过程')
step()

values[0] = 7
view.update(0, values[0])
log.write('更新下标 0')
step()
```

保存为 `demo.py` 后，通过 `python lab.py demo.py` 启动。`step()` 会复制当前展示状态并记录调用行号。

## IDE 集成

`plugins/` 提供 PyCharm 2025.2.x 和 Visual Studio 2022 x64 的可选启动入口。
通过插件菜单或工具条的“可视化当前文件”启动；IDE 普通运行按钮不会自动启动可视化。
插件可以在 IDE 的插件管理页面停用或卸载。

插件从源码构建，输出到 `dist/`。构建命令、安装步骤和环境要求见 [构建与安装](docs/BUILDING.md)。

## 文档

- [使用指南](docs/USAGE.md)：运行参数、记录接口和示例。
- [实现原理](docs/ARCHITECTURE.md)：执行、记录、生成报告和播放流程。
- [构建与安装](docs/BUILDING.md)：两个 IDE 入口和 VSIX 打包。
- [接口迁移](docs/MIGRATION.md)：早期 tracer 接口与当前接口的对应关系。
- [验证方法](docs/TESTING.md)：本地测试、原生编译和 IDE 加载检查。
- [离线银行家演示](docs/demo-banker.html)：下载 HTML 后用浏览器打开。

## 限制

- 执行后回放，不支持运行中断点、修改变量或附加进程。
- 普通 Python 追踪仅覆盖当前源文件和当前线程，最多记录 4000 帧；变量内容会截断。
- C/C++ 需要显式记录语句；暂不支持多源文件工程、工程自定义链接参数和变量自动追踪。
- C/C++ 编译入口目前存在中文路径编码问题，请使用英文目录和文件名。
- 暂不支持交互式标准输入和图、树专用渲染。
- 代码以本机权限执行；报告包含源代码和文件路径，分享前应检查内容。

## 参与开发

```sh
python -m unittest discover -s tests -v
```

贡献要求见 [CONTRIBUTING](CONTRIBUTING.md)，版本变化见 [CHANGELOG](CHANGELOG.md)。

## 来源与许可

项目设计受到 [Algorithm Visualizer](https://github.com/algorithm-visualizer/algorithm-visualizer) 启发，与其无官方隶属关系。
当前运行器、记录接口和播放器通过 AI 辅助开发，采用 [MIT License](LICENSE)。
第三方工具与分发范围见 [THIRD_PARTY](THIRD_PARTY.md)。
