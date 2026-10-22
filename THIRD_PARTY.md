# 来源与第三方工具

## 设计来源

Algorithm Lab 的设计受到 [Algorithm Visualizer](https://github.com/algorithm-visualizer/algorithm-visualizer) 启发。
本项目与其无官方隶属关系，不使用其品牌图像或标识。

当前仓库使用项目自身的 Python 快照接口和 C/C++ 记录头文件。
不分发 Algorithm Visualizer 网页代码、`tracers.py`、`tracers.cpp` 或依赖这些组件的早期插件二进制。

## 外部构建与运行工具

| 工具 | 用途 | 分发方式 |
| --- | --- | --- |
| Python | 执行运行器与测试 | 由使用者独立安装 |
| PyCharm / JBR | 构建和加载 PyCharm 入口 | 使用本机安装，不随源码或插件运行时分发 |
| Visual Studio 2022 / MSVC | 构建扩展及编译 C/C++ 示例 | 使用本机安装，不随源码或插件运行时分发 |
| Microsoft.VSSDK.BuildTools 17.14.2142 | 生成 VSIX 清单及包元数据 | 构建时从官方 NuGet 获取，不打入运行时负载 |

Microsoft.VSSDK.BuildTools 的固定版本、下载来源和哈希见 [构建说明](docs/BUILDING.md)。

## 项目许可

仓库项目代码和文档采用根目录的 [MIT License](LICENSE)。
项目通过 AI 辅助开发。外部工具遵循各自许可，不因使用本项目而改变。
新增第三方组件时，应保留其来源、版本和所需许可声明。
