# 接口迁移

当前公开接口使用 `algorithm_lab`，不提供 `algorithm_visualizer` 兼容模块。
依赖早期 tracer API 的 Python 示例需修改导入和记录调用。

```python
from algorithm_lab import ArrayView, MatrixView, Journal, step
```

| 早期接口 | 当前接口 |
| --- | --- |
| `Array1DTracer(title)` 后调用 `set(values)` | `ArrayView(title, values)` |
| `Array2DTracer(title)` 后调用 `set(matrix)` | `MatrixView(title, matrix)` |
| `LogTracer(title)` | `Journal(title)` |
| `view.patch(i, value)` | `view.update(i, value)` |
| `view.set(values)` | `view.replace(values)` |
| `matrix.selectRow(i, 0, last)` | `matrix.focus_row(i)` |
| `matrix.deselectRow(...)` | `matrix.clear_focus()` |
| `view.depatch(...)` | `view.clear_updates()` |
| `log.println(text)` | `log.write(text)` |
| `Tracer.delay(explicit_line)` | `step()`，默认记录调用行号 |

C++ 示例使用 `include/algorithm_lab_c.h`，完整用法见 `examples/banker.cpp`。
普通 Python 的逐行模式无须添加记录接口。
