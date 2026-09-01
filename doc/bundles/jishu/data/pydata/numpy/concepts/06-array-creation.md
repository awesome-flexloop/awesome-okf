---
type: concept
title: "数组创建"
description: "NumPy数组创建函数全览：array/asarray、arange/linspace/logspace/geomspace、zeros/ones/empty/full、fromfunction/fromiter/frombuffer、random随机数"
tags: [numpy, array-creation, arange, linspace, zeros, ones, empty, random, fromfunction]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: ndarray-source
    resource: /references/ndarray-source.md
    title: "NumPy ndarray与数组创建API源码"
---

# 数组创建

NumPy 提供了丰富的数组创建函数，可以从 Python 序列、数值范围、已知形状、函数、文件等多种来源创建数组。

## 1. 从现有数据创建

### np.array()

`np.array()` 是最基本的数组创建函数，从 Python 列表、元组或其他序列创建 ndarray：

```python
import numpy as np

# 从列表创建
np.array([1, 2, 3])                # array([1, 2, 3])
np.array([[1, 2], [3, 4]])         # 二维数组
np.array([1, 2, 3], dtype=float)   # 指定类型
np.array([1, 2, 3], ndmin=2)       # 至少2维 → [[1, 2, 3]]

# 从元组创建
np.array((1, 2, 3))

# 注意：np.array默认推断类型
np.array([1, 2, 3]).dtype          # int64（或int32，平台相关）
np.array([1.0, 2, 3]).dtype        # float64（混合类型提升）
```

### np.asarray()

`np.asarray()` 将输入转换为数组，但如果输入已经是 ndarray 且不需要类型转换，则返回原数组（不复制）：

```python
a = np.array([1, 2, 3])
b = np.asarray(a)
print(b is a)  # True — 不复制

c = np.asarray(a, dtype=float)
print(c is a)  # False — 类型不同，创建新数组
```

### np.asanyarray()

`np.asanyarray()` 类似于 `asarray()`，但保留 ndarray 的子类（如 masked array 或 matrix）。

### np.ascontiguousarray() / np.asfortranarray()

确保数组为C顺序或Fortran顺序连续内存：

```python
a = np.array([[1, 2], [3, 4]], order='F')
np.ascontiguousarray(a)  # 返回C顺序副本（如果需要）
np.asfortranarray(a)     # 返回F顺序数组
```

## 2. 按数值范围创建

### np.arange()

`np.arange([start,] stop[, step, dtype=None])` 创建等差序列，类似Python的 `range()` 但返回ndarray：

```python
np.arange(10)           # [0, 1, 2, ..., 9] — 0到9
np.arange(2, 10)        # [2, 3, ..., 9] — 2到9
np.arange(0, 10, 2)     # [0, 2, 4, 6, 8] — 步长2
np.arange(0, 1, 0.1)    # [0., 0.1, 0.2, ..., 0.9] — 浮点数步长
np.arange(10, dtype=float)  # 指定类型
```

> **注意**：浮点数步长可能导致终点包含问题，推荐对浮点数使用 `linspace`。

### np.linspace()

`np.linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=None, axis=0)` [F-015] 创建指定数量的等间隔样本：

```python
np.linspace(0, 1, 5)
# [0.  , 0.25, 0.5 , 0.75, 1.  ] — 5个点，包含端点

np.linspace(0, 1, 5, endpoint=False)
# [0. , 0.2, 0.4, 0.6, 0.8] — 不包含端点

x, step = np.linspace(0, 10, 5, retstep=True)
# x = [0., 2.5, 5., 7.5, 10.], step = 2.5

# 多维linspace（start和stop可以是数组）
np.linspace([0, 0], [1, 10], 3)
# [[ 0. ,  0. ],
#  [ 0.5,  5. ],
#  [ 1. , 10. ]]
```

### np.logspace()

`np.logspace(start, stop, num=50, endpoint=True, base=10, dtype=None)` 创建对数等间隔序列：

```python
np.logspace(0, 3, 4)        # [1., 10., 100., 1000.] — 10^0到10^3
np.logspace(0, 3, 4, base=2) # [1., 2., 4., 8.] — 2^0到2^3
```

### np.geomspace()

`np.geomspace(start, stop, num=50, endpoint=True, dtype=None)` 创建几何级数（等比数列）[F-015]：

```python
np.geomspace(1, 1000, 4)
# [1., 10., 100., 1000.] — 等比数列，公比10
```

## 3. 按形状创建（填充值）

### np.zeros()

`np.zeros(shape, dtype=float, order='C')` 创建全0数组 [F-015]：

```python
np.zeros(5)              # [0., 0., 0., 0., 0.] — 默认float64
np.zeros((2, 3))         # 2行3列全0
np.zeros((2, 3), dtype=int)  # 指定类型
np.zeros(3, order='F')   # Fortran顺序
```

### np.ones()

`np.ones(shape, dtype=None, order='C')` 创建全1数组 [F-015]：

```python
np.ones(3)               # [1., 1., 1.]
np.ones((2, 3), dtype=int)  # 2×3全1整数数组
```

### np.empty()

`np.empty(shape, dtype=float, order='C')` 创建**未初始化**的数组（值不确定，包含内存中的随机数据）：

```python
np.empty(3)    # array([..., ..., ...]) — 值未定义！
```

`empty` 比 `zeros` 稍快，因为不初始化内存。只有当你确定会填充所有元素时才使用它。

### np.full()

`np.full(shape, fill_value, dtype=None, order='C')` 创建填充指定值的数组 [F-015]：

```python
np.full(3, 7)           # [7, 7, 7]
np.full((2, 3), 3.14)   # 2×3全为π
np.full(3, True)        # [True, True, True]
```

## 4. _like 函数（仿照创建）

这些函数创建与给定数组具有相同形状和类型的新数组：

### np.zeros_like()

```python
a = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.int32)
np.zeros_like(a)         # 同形状同类型的全0数组
np.zeros_like(a, dtype=float)  # 覆盖类型
```

### np.ones_like()

```python
np.ones_like(a)  # 同形状同类型的全1数组
```

### np.empty_like()

```python
np.empty_like(a, order='K', subok=True, shape=None)  # [F-013]
```

`empty_like` 参数：
- `order`：'C'、'F'、'A'、'K'（默认'K'，匹配原型布局）
- `subok`：默认True，保留子类类型
- `shape`：可选，覆盖结果形状
- `device`：Array API互操作性 [F-013]

### np.full_like()

```python
np.full_like(a, 99)  # 同形状，填充99
```

## 5. 特殊矩阵

### np.eye()

`np.eye(N, M=None, k=0, dtype=float)` 创建单位矩阵：

```python
np.eye(3)          # 3×3单位矩阵
# [[1., 0., 0.],
#  [0., 1., 0.],
#  [0., 0., 1.]]

np.eye(3, 4)       # 3×4矩阵，主对角线为1
np.eye(3, k=1)     # 主对角线上方偏移1的对角线为1
# [[0., 1., 0.],
#  [0., 0., 1.],
#  [0., 0., 0.]]
```

### np.identity()

`np.identity(n, dtype=None)` 创建方阵单位矩阵 [F-015]：

```python
np.identity(3)  # 等价于np.eye(3)
```

### np.diag()

创建对角矩阵或提取对角线：

```python
np.diag([1, 2, 3])  # 对角矩阵
# [[1, 0, 0],
#  [0, 2, 0],
#  [0, 0, 3]]

np.diag([1, 2, 3], k=1)  # 偏移1
```

### np.tri()

创建下三角矩阵（含对角线为1）：

```python
np.tri(3)
# [[1., 0., 0.],
#  [1., 1., 0.],
#  [1., 1., 1.]]
```

## 6. 从函数或迭代器创建

### np.fromfunction()

`np.fromfunction(function, shape, *, dtype=float, **kwargs)` 通过对每个坐标调用函数来创建数组 [F-015]：

```python
np.fromfunction(lambda i, j: i + j, (3, 3))
# [[0., 1., 2.],
#  [1., 2., 3.],
#  [2., 3., 4.]]
# i是行索引矩阵，j是列索引矩阵

np.fromfunction(lambda i: i * 2, (5,))
# [0., 2., 4., 6., 8.]
```

### np.fromiter()

`np.fromiter(iterable, dtype, count=-1)` 从可迭代对象创建数组：

```python
np.fromiter(range(5), dtype=int)  # [0, 1, 2, 3, 4]
np.fromiter((x**2 for x in range(5)), dtype=float)  # [0., 1., 4., 9., 16.]
```

### np.frombuffer()

`np.frombuffer(buffer, dtype=float, count=-1, offset=0)` 从字节缓冲区创建数组（零拷贝）：

```python
import struct
data = struct.pack('fff', 1.0, 2.0, 3.0)
np.frombuffer(data, dtype=np.float32)  # array([1., 2., 3.], dtype=float32)
```

### np.fromfile() / np.fromstring()

从文件或字符串读取数据创建数组（二进制或文本格式）。

## 7. 网格创建

### np.mgrid 和 np.ogrid

```python
# np.mgrid返回密集网格（广播后的完整数组）
x, y = np.mgrid[0:3, 0:3]
# x: [[0,0,0],[1,1,1],[2,2,2]]
# y: [[0,1,2],[0,1,2],[0,1,2]]

# np.ogrid返回开放网格（可广播的数组）
x, y = np.ogrid[0:3, 0:3]
# x: [[0],[1],[2]] shape (3,1)
# y: [[0,1,2]] shape (1,3)
```

### np.meshgrid()

```python
x = np.array([1, 2, 3])
y = np.array([4, 5])
xx, yy = np.meshgrid(x, y)
# xx: [[1,2,3],[1,2,3]]
# yy: [[4,4,4],[5,5,5]]
```

### np.indices()

`np.indices(dimensions, dtype=int, sparse=False)` 返回网格索引数组 [F-015]：

```python
row, col = np.indices((3, 4))
# row: [[0,0,0,0],[1,1,1,1],[2,2,2,2]]
# col: [[0,1,2,3],[0,1,2,3],[0,1,2,3]]
```

### np.c_ 和 np.r_

```python
np.r_[1:4, 0, 4]       # [1, 2, 3, 0, 4] — 行拼接
np.c_[[1,2,3], [4,5,6]]  # [[1,4],[2,5],[3,6]] — 列拼接
```

## 8. 随机数创建

NumPy 的随机数系统在 `numpy.random` 模块中。NumPy 1.17+ 推荐使用新的 `Generator` API 而非旧的 `RandomState`。

### 使用 default_rng() 创建Generator

```python
from numpy.random import default_rng

rng = default_rng(42)  # 种子为42（可复现）

rng.random((3, 4))         # [0,1)均匀分布
rng.integers(0, 10, (3,)) # 整数[0,10)
rng.standard_normal((3,))  # 标准正态分布
rng.normal(0, 1, (3,))     # 指定均值和标准差的正态分布
rng.uniform(0, 5, (3,))    # [0,5)均匀分布
```

### 随机数组创建

```python
# 使用新API
from numpy.random import default_rng
rng = default_rng()

rng.random((2, 3))       # [0,1)均匀随机
rng.permutation(10)      # 0-9的随机排列
rng.choice([1,2,3], 5)   # 从序列中随机选择（可重复）
```

## 9. 创建函数的通用参数

大多数创建函数支持以下参数：

| 参数 | 说明 | 常见取值 |
|------|------|---------|
| `dtype` | 数据类型 | `np.int32`, `np.float64`, `np.complex128`等 |
| `order` | 内存顺序 | `'C'`（行优先，默认）, `'F'`（列优先） |
| `device` | 设备（Array API） | `None`（CPU）, `'cpu'` |
| `like` | 参考数组（NEP-18） | 支持`__array_function__`的数组对象 |

## 相关概念

- [ndarray多维数组](01-ndarray.md) — 数组对象的结构和属性
- [dtype数据类型系统](02-dtype-system.md) — 选择正确的dtype
- [广播规则](04-broadcasting.md) — 理解mgrid/ogrid的广播原理
- [基础数组操作](../examples/basic-array-ops.md) — 创建数组后的基本操作
