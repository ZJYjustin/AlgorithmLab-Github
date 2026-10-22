# 使用指南

## 启动方式

在仓库根目录运行：

```sh
python lab.py examples/banker.py
python lab.py examples/plain_python.py --mode lines
python lab.py examples/banker.c
python lab.py examples/banker.cpp
```

普通 Python 脚本默认使用逐行记录；导入当前记录接口的脚本在自动模式下使用算法动画。
直接运行示例脚本不负责生成 HTML，应通过 `lab.py` 或 IDE 可视化入口启动。

## 命令行参数

| 参数 | 含义 |
| --- | --- |
| `--mode auto` | 自动选择逐行记录或算法动画，默认值 |
| `--mode lines` | 强制显示 Python 逐行记录 |
| `--output replay.html` | 指定报告路径 |
| `--timeout 30` | 设置程序执行时限，单位为秒，默认 20 秒 |
| `--no-browser` | 生成报告后不自动打开浏览器 |
| `--json` | 同时输出可检查的 JSON 记录 |

`--` 之后的参数传递给目标程序。例如：

```sh
python lab.py demo.py --no-browser -- --size 5
```

## Python 记录接口

```python
from algorithm_lab import ArrayView, MatrixView, Journal, step
```

| 接口 | 用途 |
| --- | --- |
| `ArrayView(title, values)` | 创建一维数组视图 |
| `MatrixView(title, matrix)` | 创建二维矩阵视图 |
| `Journal(title)` | 创建日志面板 |
| `view.update(index, value)` | 更新数组中的一个元素 |
| `matrix.update(row, column, value)` | 更新矩阵中的一个元素 |
| `view.replace(values)` | 替换展示数据 |
| `matrix.focus_row(row)` | 标记矩阵的一行 |
| `view.clear_focus()` | 清除选中标记 |
| `view.clear_updates()` | 清除更新标记 |
| `log.write(text)` | 添加一条日志 |
| `step()` | 复制当前面板状态并形成一帧 |

算法数据与展示数据分离。修改普通列表后，还需要调用视图更新接口；历史帧不会随原始列表变化。

## C/C++ 记录接口

```cpp
#include "algorithm_lab_c.h"

int main() {
    int values[] = {3, 1, 2};
    lab_create("array", "Array1DTracer", "数组");
    lab_array1d("array", values, 3);
    lab_step(__LINE__);
    values[0] = 7;
    lab_array1d("array", values, 3);
    lab_step(__LINE__);
    return 0;
}
```

运行器会自动添加 `include/` 搜索路径。普通 IDE 构建需要自行配置附加包含目录。
记录头文件适用于单翻译单元示例；文件中的静态状态不用于跨多个源文件共享记录。
`lab_array2d` 写入矩阵，`lab_row` 切换行标记，`lab_log` 添加日志。

## 播放器

打开生成的 HTML 后，可播放、暂停、前后单步、拖动进度并调整速度。
Python 逐行模式中，高亮行表示即将执行，该帧变量属于执行该行之前的状态。
算法动画模式中，一帧对应 `step()` 或 `lab_step(__LINE__)` 调用时的状态。
后退只切换记录画面，不撤销程序产生的文件写入等操作。

## 银行家示例

默认输入的安全序列为 `[1, 3, 4, 0, 2]`，最终工作向量为 `[10, 5, 7]`。
将初始可用资源改为 `[0, 0, 0]` 可观察无法找到完整安全序列的情况。
示例仅实现安全性检查，尚未实现完整的资源请求试分配流程；不安全状态不等于已发生死锁。
