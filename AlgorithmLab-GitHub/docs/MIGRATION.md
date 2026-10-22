# 从本地研究版迁移到公开整理版

0.1.1 是用户已安装并使用的本地版本，带有上游的两个 tracer 库。0.2.0 为公开分发整理，移除了这些组件。
你的旧安装目录和原项目文件没有被本次整理修改。只阅读手册不需要更新插件。

公开版 Python 示例的导入改为：

```python
from algorithm_lab import ArrayView, MatrixView, Journal, step
```

| 本地研究版 | 公开版 |
| --- | --- |
| `Array1DTracer(title)` 然后 `set(values)` | `ArrayView(title, values)` |
| `Array2DTracer(title)` 然后 `set(matrix)` | `MatrixView(title, matrix)` |
| `LogTracer(title)` | `Journal(title)` |
| `view.patch(i, value)` | `view.update(i, value)` |
| `view.set(values)` | `view.replace(values)` |
| `matrix.selectRow(i, 0, last)` | `matrix.focus_row(i)` |
| `matrix.deselectRow(...)` | `matrix.clear_focus()` |
| `view.depatch(...)` | `view.clear_updates()` |
| `log.println(text)` | `log.write(text)` |
| `Tracer.delay(explicit_line)` | `step()` 自动获取调用行 |

旧版 C++ 示例也需替换为公开版 `examples/banker.cpp`，使用 `algorithm_lab_c.h`。
普通 Python 的逐行模式保持不变。请成套使用公开版示例、运行器和插件；0.2.0 不提供 `algorithm_visualizer` 兼容包。
