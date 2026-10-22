# 版本记录

## 0.2.1

- 修复 Visual Studio 扩展被安装器判定为无效 VSIX 包的问题。
- 改用官方 Microsoft.VSSDK.BuildTools 生成现代 VSIX 元数据，包含 catalog.json 和 manifest.json。
- 核对运行时负载的相对路径，新增两项打包回归检查。
- 通过本机 Visual Studio 2022 的 InstallableExtensionImpl 读取检查；未把读取成功等同于已经安装或 IDE 已加载。
- PyCharm 插件版本和运行引擎接口不变。

## 0.2.0

- 整理公开发布目录，排除上游 tracer、网页源码副本及依赖它们的旧插件二进制。
- 新增独立的 Python 记录模块 algorithm_lab.py；公开示例使用新 API。
- C++ 示例改用本项目自己的 C/C++ 记录头文件。
- 移除构建脚本中的个人安装目录，增加 MIT、来源说明、迁移说明和 CI。
- 保留普通 Python 逐行记录、离线回放以及两个 IDE 的可选启动入口。

## 本地研究版 0.1.1

- 修复 PyCharm CodeSource 位置为空导致无法定位运行目录的问题。
- 修复所选 Python 解释器未传递给执行子进程的问题。

旧本地研究版仅作为开发过程背景，不包含在此仓库分发包中。
