# 验证方法

## 自动检查

```sh
python -m unittest discover -s tests -v
```

运行器测试覆盖 Python 逐行与动画模式、算法结果、异常、超时、HTML 转义和 C/C++ 记录。
VSIX 回归测试覆盖必要包元数据与运行时负载路径。
原生编译检查在具备 MSVC 的 Windows 环境运行；不满足环境要求时跳过。

## 示例验收

```sh
python lab.py examples/banker.py --no-browser --json --output reports/banker.html
```

默认银行家示例的预期安全序列为 `[1, 3, 4, 0, 2]`，最终 Work 为 `[10, 5, 7]`。
将初始可用资源改为全零后，不应产生完整安全序列。
手动打开 HTML，检查播放、暂停、前后单步、进度和日志。

## IDE 验收

构建后分别在目标 IDE 中检查安装、入口显示、解释器设置、示例执行和停用功能。
包可读取、源码可编译和 IDE 成功加载属于不同检查项目。
GitHub Actions 的 Python 测试不能替代 Windows 原生编译与 IDE 加载检查。

## 持续集成

`.github/workflows/tests.yml` 在 Ubuntu 上配置 Python 3.10、3.12、3.14 测试。
实际结果以仓库 Actions 运行记录为准。工作流不安装商业 IDE，也不执行插件界面验收。
