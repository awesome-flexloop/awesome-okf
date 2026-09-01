---
type: concept
title: "索引与切片"
description: "NumPy的基本切片、布尔索引、花式索引机制，np.where条件选择、np.take沿轴提取，以及索引的视图/副本行为"
tags: [numpy, indexing, slicing, boolean-indexing, fancy-indexing, where, take]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: ndarray-source
    resource: /references/ndarray-source.md
    title: "NumPy ndarray与数组创建API源码"
---

# 索引与切片

NumPy 提供了比 Python list 更丰富的索引机制，包括基本切片、布尔索引和花式索引（fancy indexing）。掌握这些索引方式是高效使用 NumPy 的关键。

## 1. 基本切片（Basic Slicing）

基本切片是 Python list 切片的扩展，支持多维。基本切片返回**视图**（view），不复制数据。

### 一维切片

语法：`a[start:stop:step]`

```python
import numpy as np

a = np.arange(10)  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

a[2:5]     # [2, 3, 4] — 从索引2到5（不含5）
a[:5]      # [0, 1, 2, 3, 4] — 从开头到5
a[5:]      # [5, 6, 7, 8, 9] — 从5到结尾
a[::2]     # [0, 2, 4, 6, 8] — 每隔一个取
a[::-1]    # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0] — 反转
a[-3:]     # [7, 8, 9] — 最后3个
a[1:7:2]   # [1, 3, 5] — 从1到7，步长2
```

### 多维切片

多维数组可以对每个维度分别切片，用逗号分隔：

```python
a = np.array([[0, 1, 2, 3],
              [4, 5, 6, 7],
              [8, 9, 10, 11]])

a[0, 1]        # 1 — 第0行第1列（标量）
a[0]           # [0, 1, 2, 3] — 第0行（一维数组）
a[:, 1]        # [1, 5, 9] — 第1列
a[:2, 1:3]     # [[1, 2], [5, 6]] — 前两行、1-2列
a[::2, ::2]    # [[0, 2], [8, 10]] — 每隔一行取一行，每隔一列取一列
a[0, :]        # [0, 1, 2, 3] — 第0行（等价于a[0]）
```

### 使用 newaxis 插入维度

`np.newaxis`（即 `None`）可以在切片中插入新维度 [F-016]：

```python
a = np.array([1, 2, 3])  # shape (3,)
a[:, np.newaxis]  # shape (3, 1)
# [[1],
#  [2],
#  [3]]

a[np.newaxis, :]  # shape (1, 3)
# [[1, 2, 3]]
```

### 省略号（Ellipsis）

`...`（即Python的`Ellipsis`对象）可以替代多个冒号，表示"剩余所有维度"：

```python
a = np.zeros((3, 4, 5, 6))
a[0, ...]      # 等价于 a[0, :, :, :]，shape (4, 5, 6)
a[..., 2]      # 等价于 a[:, :, :, 2]，shape (3, 4, 5)
a[0, ..., 2]   # 等价于 a[0, :, :, 2]，shape (4, 5)
```

## 2. 布尔索引（Boolean Indexing）

使用布尔数组作为索引，选择对应位置为True的元素。布尔索引返回**副本**（copy）。

### 基本用法

```python
a = np.array([1, -2, 3, -4, 5])

a[a > 0]   # [1, 3, 5] — 选择正数
a[a < 0]   # [-2, -4] — 选择负数
a[a % 2 == 0]  # [-2, -4] — 选择偶数

# 组合条件
a[(a > 0) & (a < 4)]  # [1, 3] — 注意用&、|、~，不用and/or/not
a[(a < 0) | (a > 4)]  # [-2, -4, 5]
a[~(a > 0)]           # [-2, -4] — 非正数
```

### 多维布尔索引

```python
a = np.array([[1, 2, 3], [4, 5, 6]])
mask = a > 3
print(mask)
# [[False False False]
#  [ True  True  True]]
a[mask]  # [4, 5, 6] — 返回一维数组
```

### 布尔索引用于赋值

```python
a = np.array([1, -2, 3, -4, 5])
a[a < 0] = 0  # 将负数替换为0
print(a)  # [1, 0, 3, 0, 5]

# 使用where参数也可以实现条件赋值
np.where(a > 0, a, 0)  # 不修改原数组，返回新数组
```

## 3. 花式索引（Fancy Indexing）

花式索引使用整数数组或列表作为索引，选择指定位置的元素。花式索引返回**副本**（copy）。

### 一维花式索引

```python
a = np.array([10, 20, 30, 40, 50])

a[[0, 2, 4]]      # [10, 30, 50] — 选择指定索引
a[[4, 0, 2]]      # [50, 10, 30] — 可以改变顺序
a[[0, 0, 1, 1]]   # [10, 10, 20, 20] — 可以重复选择
```

### 多维花式索引

```python
a = np.arange(12).reshape(3, 4)
# [[ 0  1  2  3]
#  [ 4  5  6  7]
#  [ 8  9 10 11]]

# 使用两个索引数组：行索引和列索引配对
a[[0, 1, 2], [1, 2, 3]]  # [1, 6, 11]
# 选择 (0,1), (1,2), (2,3) 三个位置

# 选择多行（列取全部）
a[[0, 2]]  # [[0,1,2,3], [8,9,10,11]] — 第0行和第2行

# 使用np.ix_创建开放网格
rows = [0, 2]
cols = [1, 3]
a[np.ix_(rows, cols)]
# [[1, 3],
#  [9, 11]]
# 等价于 rows × cols 的笛卡尔积
```

### 使用 np.ix_ 进行多维度花式选择

`np.ix_` 将一维索引数组转换为可广播的形状，从而实现多维度交叉选择：

```python
a = np.arange(20).reshape(4, 5)
# 选择第0、2行和第1、3列的交叉点
rows = np.array([0, 2])
cols = np.array([1, 3])
a[np.ix_(rows, cols)]
# [[ 1,  3],
#  [11, 13]]
```

## 4. np.where：条件选择

`np.where` 是条件选择的核心函数，有两种用法：

### 用法1：返回满足条件的索引

```python
a = np.array([1, -2, 3, -4, 5])
np.where(a > 0)
# (array([0, 2, 4]),) — 返回满足条件的索引元组

a = np.array([[1, -2], [3, -4]])
np.where(a > 0)
# (array([0, 1]), array([0, 0]))
# (行索引, 列索引)，即位置(0,0)和(1,0)
```

### 用法2：条件选择值（类似三元表达式）

```python
a = np.array([1, -2, 3, -4, 5])
np.where(a > 0, a, 0)  # [1, 0, 3, 0, 5]
# 语法：np.where(condition, x, y)
# condition为True取x，为False取y

# x和y也可以是标量
np.where(a > 0, 1, -1)  # [1, -1, 1, -1, 1]
```

## 5. np.take：沿轴提取元素

`np.take` 沿指定轴从数组中提取元素 [F-020]，功能类似于花式索引但更明确地指定轴：

```python
a = np.array([[1, 2, 3], [4, 5, 6]])

# 不指定axis时，数组先被展平
np.take(a, [0, 2, 4])  # [1, 3, 5]

# 指定axis
np.take(a, [0, 2], axis=1)  # 沿列轴取第0和2列
# [[1, 3],
#  [4, 6]]
np.take(a, [1], axis=0)  # 沿行轴取第1行
# [[4, 5, 6]]
```

`take` 的 `mode` 参数控制越界索引的处理 [F-020]：
- `'raise'`（默认）：抛出错误
- `'wrap'`：环绕（索引取模）
- `'clip'`：裁剪到范围

```python
a = np.array([1, 2, 3, 4, 5])
np.take(a, [0, 5, 6], mode='clip')  # [1, 5, 5]
np.take(a, [0, 5, 6], mode='wrap')  # [1, 1, 2]
```

## 6. 索引类型对比

| 索引类型 | 示例 | 返回类型 | 视图/副本 |
|---------|------|---------|----------|
| 基本切片 | `a[1:4]`, `a[:, 2]` | 数组子集 | **视图** |
| 整数索引 | `a[2]`, `a[0, 1]` | 标量或子数组 | 标量/视图 |
| 布尔索引 | `a[a > 0]` | 一维数组 | **副本** |
| 花式索引 | `a[[0,2]]`, `a[[0],[1]]` | 数组 | **副本** |
| newaxis | `a[:, None]` | 增加维度的数组 | 视图 |

## 7. 其他索引工具

### np.nonzero：非零元素索引

```python
a = np.array([0, 1, 0, 2, 3])
np.nonzero(a)  # (array([1, 3, 4]),) — 等价于 np.where(a != 0)
a.nonzero()    # 数组方法版本
```

### np.argwhere：返回非零/满足条件的坐标

```python
a = np.array([[0, 1], [2, 0]])
np.argwhere(a > 0)
# [[0, 1],
#  [1, 0]]
# 返回形状为(N, ndim)的数组，每行是一个坐标
```

### np.diag 和 np.diagonal：对角线

```python
a = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
np.diag(a)      # [1, 5, 9] — 主对角线
np.diag(a, 1)   # [2, 6] — 主对角线上方第1条
np.diag(a, -1)  # [4, 8] — 主对角线下方第1条
a.diagonal()    # 数组方法版本
```

### np.indices：生成网格索引

```python
row_idx, col_idx = np.indices((3, 4))
# row_idx: [[0,0,0,0],[1,1,1,1],[2,2,2,2]]
# col_idx: [[0,1,2,3],[0,1,2,3],[0,1,2,3]]
```

### flatnonzero、argmax、argmin

```python
a = np.array([0, 5, 0, 3, 8])
np.flatnonzero(a)  # [1, 3, 4] — 展平后的非零索引
np.argmax(a)       # 4 — 最大值的索引
np.argmin(a)       # 0 — 最小值的索引（第一个0）
```

## 8. 索引赋值

可以使用各种索引方式进行赋值操作：

```python
a = np.zeros((3, 3))

# 切片赋值
a[0, :] = 1           # 第0行全设为1
a[:, 1] = 2           # 第1列全设为2

# 布尔赋值
a[a > 1] = 99         # 大于1的元素设为99

# 花式索引赋值
a[[0, 2], [0, 2]] = [10, 30]  # (0,0)=10, (2,2)=30

# 使用np.put（类似take的赋值版本）
np.put(a, [0, 4, 8], [100, 500, 900])
```

## 相关概念

- [ndarray多维数组](01-ndarray.md) — 视图与副本的内存行为
- [广播规则](04-broadcasting.md) — 索引中的newaxis与广播
- [基础数组操作](../examples/basic-array-ops.md) — 索引实践
