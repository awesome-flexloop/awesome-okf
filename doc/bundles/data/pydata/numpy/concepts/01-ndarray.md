---
type: concept
title: "ndarray多维数组"
description: "ndarray的内存布局（C/F顺序）、shape/strides/dtype核心属性、视图与副本机制、flags标志位详解"
tags: [numpy, ndarray, memory-layout, strides, view, copy, flags]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: ndarray-source
    resource: /references/ndarray-source.md
    title: "NumPy ndarray与数组创建API源码"
  - id: dtype-source
    resource: /references/dtype-source.md
    title: "NumPy dtype与数值类型系统源码"
---

# ndarray 多维数组

ndarray（N-dimensional array，N维数组）是 NumPy 的核心数据结构。它在 C 层实现（`_multiarray_umath` 扩展模块）[F-011]，Python 层通过 `numpy.ndarray` 类暴露。理解 ndarray 的内存布局和核心属性是掌握 NumPy 的基础。

## ndarray 的核心属性

每个 ndarray 对象包含以下关键属性：

### shape：数组形状

`shape` 是一个整数元组，表示每个维度的大小。例如：

```python
import numpy as np

a = np.array([[1, 2, 3], [4, 5, 6]])
print(a.shape)  # (2, 3) — 2行3列

b = np.zeros((3, 4, 5))
print(b.shape)  # (3, 4, 5) — 三维数组

# 标量（0维数组）
c = np.array(42)
print(c.shape)  # () — 空元组
```

### ndim：维度数

`ndim` 等于 `len(shape)`，即数组的轴数（axis count）：

```python
a = np.array([[1, 2], [3, 4]])
print(a.ndim)  # 2

b = np.array([1, 2, 3])
print(b.ndim)  # 1
```

### size：元素总数

`size` 等于 `shape` 中所有维度大小的乘积：

```python
a = np.zeros((3, 4))
print(a.size)  # 12 (= 3 * 4)
```

### dtype：数据类型

`dtype` 描述数组中元素的类型，决定了每个元素占用的字节数和解释方式。详见 [dtype数据类型系统](02-dtype-system.md)。

```python
a = np.array([1, 2, 3], dtype=np.float64)
print(a.dtype)  # float64
```

### itemsize：每个元素的字节大小

`itemsize` 等于 `dtype.itemsize`，即每个元素占用的字节数：

```python
np.array([1, 2], dtype=np.int32).itemsize   # 4
np.array([1, 2], dtype=np.float64).itemsize # 8
np.array([1, 2], dtype=np.complex128).itemsize # 16
```

### nbytes：总字节数

`nbytes = size * itemsize`，即数组数据占用的总字节数：

```python
a = np.zeros((3, 4), dtype=np.float64)
print(a.nbytes)  # 96 (= 12 * 8)
```

## 内存布局：strides 与存储顺序

### strides：步幅元组

`strides` 是 NumPy 内存布局的核心概念。它是一个整数元组，表示在每个维度上**移动到下一个元素需要跳过的字节数**。

理解 strides 是理解 NumPy 数组性能和"零拷贝"视图的关键：

```python
# C顺序（行优先）的2x3 float64数组
a = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float64, order='C')
print(a.strides)  # (24, 8)
# 行方向：移动1行需要跳过3个元素×8字节=24字节
# 列方向：移动1列需要跳过1个元素×8字节=8字节

# F顺序（列优先）的2x3 float64数组
b = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float64, order='F')
print(b.strides)  # (8, 16)
# 行方向：移动1行只需跳过1个元素×8字节=8字节
# 列方向：移动1列需要跳过2个元素×8字节=16字节
```

### C顺序 vs Fortran顺序

NumPy 支持两种主要的内存存储顺序 [F-041]：

| 顺序 | 别名 | 说明 | 典型应用 |
|------|------|------|---------|
| **C顺序** | 行优先（row-major） | 最后一个维度的索引变化最快 | C语言默认，NumPy默认 |
| **Fortran顺序** | 列优先（column-major） | 第一个维度的索引变化最快 | Fortran、MATLAB、某些BLAS/LAPACK调用 |

```python
# 创建时指定顺序
a = np.array([[1, 2], [3, 4]], order='C')  # 默认
b = np.array([[1, 2], [3, 4]], order='F')  # Fortran顺序

# 检查连续性
print(a.flags['C_CONTIGUOUS'])  # True
print(b.flags['F_CONTIGUOUS'])  # True

# 特殊情况
c = np.array([1, 2, 3])  # 一维数组同时是C和F连续的
print(c.flags['C_CONTIGUOUS'])  # True
print(c.flags['F_CONTIGUOUS'])  # True [F-041]
```

`order` 参数在 `zeros`、`ones`、`empty`、`array` 等创建函数中支持以下值：
- `'C'`：C顺序
- `'F'`：Fortran顺序
- `'A'`：如果输入是Fortran连续则保持F，否则C
- `'K'`：保持输入的内存布局（默认，如 `empty_like` 中）[F-013]

## flags：数组标志位

`flags` 属性是一个字典-like 对象，描述数组的内存状态 [F-041][F-042]：

| 标志 | 值 | 含义 |
|------|-----|------|
| `C_CONTIGUOUS` | 0x0001 | 数据按C顺序（行优先）连续存储 |
| `F_CONTIGUOUS` | 0x0002 | 数据按Fortran顺序（列优先）连续存储 |
| `OWNDATA` | 0x0004 | 数组拥有自己的内存（视图为False） |
| `ALIGNED` | 0x0100 | 数据和步幅在适当的边界上对齐 |
| `WRITEABLE` | 0x0400 | 数组可写入（False时只读） |
| `WRITEBACKIFCOPY` | 0x2000 | 数组是其他数组的写回副本 |

```python
a = np.array([[1, 2, 3], [4, 5, 6]])
print(a.flags)
#   C_CONTIGUOUS : True
#   F_CONTIGUOUS : False
#   OWNDATA : True
#   WRITEABLE : True
#   ALIGNED : True
#   WRITEBACKIFCOPY : False
```

常用的检查方法：
```python
a.flags.c_contiguous    # 是否C连续
a.flags.f_contiguous    # 是否F连续
a.flags.owndata         # 是否拥有数据
a.flags.writeable       # 是否可写
a.flags.aligned         # 是否对齐
```

## 视图（View）与副本（Copy）

这是 NumPy 中最容易引发 Bug 的概念之一。理解两者的区别至关重要。

### 视图（View）—— 浅拷贝

视图是与原数组**共享数据内存**的新数组对象。修改视图会影响原数组，反之亦然。创建视图的操作包括：

- 切片（基本切片，非花式索引）：`a[1:3]`
- `reshape()`（当形状兼容时）
- `ravel()`（当数组连续时）
- `view()` 方法
- 转置（`T` 属性）：不移动数据，仅交换 strides

```python
a = np.array([1, 2, 3, 4, 5])
b = a[1:4]  # b是a的视图
b[0] = 99
print(a)  # [ 1 99  3  4  5] — a也被修改了！
print(b.flags.owndata)  # False — b不拥有数据
```

判断一个数组是否为视图：检查 `base` 属性。如果 `base is None`，则数组拥有自己的数据（是副本或原始数组）；否则 `base` 指向它所查看的数组。

```python
a = np.array([1, 2, 3])
b = a[1:]
print(b.base is a)  # True — b查看a的数据
```

### 副本（Copy）—— 深拷贝

副本是拥有**独立数据内存**的新数组。修改副本不会影响原数组。创建副本的操作包括：

- 花式索引（fancy indexing）：`a[[0, 2]]`
- 布尔索引：`a[a > 0]`
- `copy()` 方法
- `flatten()` 方法
- 某些 `astype()` 调用（类型转换时）
- 无法返回视图时的 `reshape()`（需要复制）

```python
a = np.array([1, 2, 3, 4, 5])
b = a[[0, 2, 4]]  # 花式索引创建副本
b[0] = 99
print(a)  # [1 2 3 4 5] — a未被修改
print(b.flags.owndata)  # True
```

### 显式控制：copy() 与 view()

```python
a = np.array([1, 2, 3])
b = a.copy()  # 显式创建副本
c = a.view()  # 显式创建视图
```

### 常见陷阱

1. **切片赋值 vs 切片拷贝**：
```python
a = np.array([1, 2, 3])
b = a[1:]    # 视图，修改b影响a
b = a[1:].copy()  # 副本，安全
```

2. **reshape可能返回视图或副本**：通常返回视图，但在非连续数组上可能需要复制。

3. **转置是视图**：`a.T` 不复制数据，修改转置数组会修改原数组。

## 数据类型与内存

ndarray 的数据在内存中以连续字节块存储（除非是不连续的视图）。每个元素按 `dtype` 的定义解释：

```python
# float64数组：每个元素8字节
a = np.array([1.0, 2.0, 3.0], dtype=np.float64)
print(a.itemsize)  # 8
print(a.nbytes)    # 24

# int32数组：每个元素4字节
b = np.array([1, 2, 3], dtype=np.int32)
print(b.itemsize)  # 4
print(b.nbytes)    # 12
```

### data 属性

`data` 属性是一个 Python buffer 对象，指向数组数据的起始内存位置。通常不需要直接使用，它主要用于与 C 扩展交互。

## 创建 ndarray 的基本方式

```python
# 从Python列表创建
np.array([1, 2, 3])                # 一维数组
np.array([[1, 2], [3, 4]])         # 二维数组
np.array([1, 2, 3], dtype=np.float64)  # 指定类型

# 创建指定形状的数组
np.zeros((2, 3))      # 全0
np.ones((2, 3))       # 全1
np.empty((2, 3))      # 未初始化（最快，值不确定）
np.full((2, 3), 7)    # 填充指定值
np.eye(3)             # 单位矩阵
np.identity(3)        # 单位矩阵 [F-015]

# 按序列创建
np.arange(10)         # [0,1,...,9]
np.linspace(0, 1, 5)  # [0., 0.25, 0.5, 0.75, 1.]
```

更多数组创建方法详见 [数组创建](06-array-creation.md)。

## ndarray 常用方法

| 方法 | 说明 |
|------|------|
| `reshape(shape)` | 改变形状（返回视图） |
| `flatten()` | 展平为一维（返回副本） |
| `ravel()` | 展平为一维（尽可能返回视图） |
| `transpose()` / `T` | 转置（返回视图） |
| `squeeze()` | 移除长度为1的维度 |
| `copy()` | 创建副本 |
| `astype(dtype)` | 类型转换（默认返回副本） |
| `sum(axis)` | 求和 |
| `mean(axis)` | 求均值 |
| `max()` / `min()` | 最大/最小值 |
| `argmax()` / `argmin()` | 最大/最小值索引 |
| `dot(other)` | 点积 |
| `fill(value)` | 填充值 |
| `sort()` | 原地排序 |
| `argsort()` | 排序索引 |

## 相关概念

- [NumPy简介](00-introduction.md) — NumPy的定位与核心能力
- [dtype数据类型系统](02-dtype-system.md) — 深入理解dtype
- [ufunc通用函数](03-ufunc.md) — 对ndarray执行向量化运算
- [广播规则](04-broadcasting.md) — 不同形状数组的运算规则
- [索引与切片](05-indexing.md) — 访问和修改数组元素
- [NumPy ndarray与数组创建API源码](/references/ndarray-source.md) — 源码信源
