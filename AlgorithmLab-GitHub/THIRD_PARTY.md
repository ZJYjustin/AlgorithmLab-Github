# 来源与分发边界

## 项目关系

Algorithm Lab Local 的设计受到 [Algorithm Visualizer](https://github.com/algorithm-visualizer/algorithm-visualizer) 启发。
本项目不是 Algorithm Visualizer 官方插件，没有使用其品牌图像或标识。本项目通过 AI 辅助编写和整理，不能将“AI 辅助”当作第三方代码自动获得授权的依据。

## 本公开包包含什么

- 本项目编写的运行器、普通 Python 追踪器、离线播放器、命令回放逻辑、C/C++ 记录头文件和 IDE 启动器。
- 为公开版新编写的 `algorithm_lab.py`，直接保存状态快照，不导入或复制上游 Python tracer 文件。
- 使用上述记录层的教学示例、测试和说明。
- 开源许可文本 MIT。该许可覆盖本公开包中有权授权的项目内容，不改变任何外部组件的权利。

## 本公开包排除了什么

| 原本地研究组件 | 核查范围 | 本次处理 |
| --- | --- | --- |
| algorithm-visualizer 网页源码 | 提供的快照含 MIT LICENSE | 不分发整份网页项目，仅保留链接与设计致谢 |
| tracers.py | 提供快照中未找到明确许可证 | 不包含其文件、补丁或绑定它的旧安装包 |
| tracers.cpp | 提供快照中未找到明确许可证 | 不包含其文件、补丁或绑定它的旧安装包 |
| nlohmann/json | 旧本地版使用 v3.6.1，含 MIT LICENSE | 公开版 C/C++ 改用自有输出接口，不再依赖 |
| IDE SDK 与 Python | 由各自发行方提供 | 只在用户本机使用，不包含其二进制文件 |
| Microsoft.VSSDK.BuildTools | 官方 NuGet 版本 17.14.2142 | 构建时下载并校验，不随项目源码或插件负载分发 |

核查日期为 2026-10-22；核查快照提交：

- algorithm-visualizer：`18de2edf6b629e843ee4bcedfa2208d22b253f0f`
- tracers.py：`62193206d4e173b86f6714946bacae900b8d5c7d`
- tracers.cpp：`66a24e212c1be88d0771a5a19901d27a5ddaf307`

“快照中未找到许可证”不是对上游永久授权状态的判断。如果以后要加入这些库，应先核实对应版本授权并保留所需声明。

## 发布说明

公开托管不等于任意再分发授权。GitHub 官方说明，没有许可证时默认版权规则适用；MIT 允许再分发，但要求保留版权和许可声明。
本次通过排除授权不明确的组件来降低分发风险，不承诺已经排除所有可能的权利争议，也不替代具体法律意见。

参考：

- [GitHub Licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- [OSI MIT License](https://opensource.org/license/mit)
