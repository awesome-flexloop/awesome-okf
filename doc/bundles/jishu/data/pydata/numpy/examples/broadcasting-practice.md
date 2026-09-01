---
type: example
title: "广播实战"
description: "NumPy广播机制的实际应用：外积计算、数据中心化、距离矩阵、归一化等高频模式"
tags: [numpy, broadcasting, outer-product, centering, distance-matrix, normalization]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: ufunc-source
    resource: /references/ufunc-source.md
    title: "NumPy ufunc通用函数系统源码"
---

# 广播实战

本示例展示 NumPy 广播机制在实际数据处理中的高频应用模式。

## 1. 外积计算

外积是广播最经典的应用之一：列向量 × 行向量 = 矩阵。

```python
import numpy as np

# === 乘法外积 ===
x = np.array([1, 2, 3])
y = np.array([4, 5, 6, 7])

# 方法1：使用newaxis
outer_mul = x[:, np.newaxis] * y[np.newaxis, :]
# 等价于 x[:, None] * y
print("乘法外积:")
print(outer_mul)
# [[ 4  5  6  7]
#  [ 8 10 12 14]
#  [12 15 18 21]]
print()

# 方法2：np.outer（仅乘法）
print("np.outer:")
print(np.outer(x, y))
print()

# === 外和（加法外积）===
outer_add = x[:, np.newaxis] + y
print("加法外积:")
print(outer_add)
# [[ 5  6  7  8]
#  [ 6  7  8  9]
#  [ 7  8  9 10]]
print()

# === 任意二元ufunc的outer方法 ===
# np.maximum.outer 取最大值
outer_max = np.maximum.outer(x, y)
print("maximum外积:")
print(outer_max)
# [[4 5 6 7]
#  [4 5 6 7]
#  [4 5 6 7]]
print()

# np.subtract.outer 计算差值
outer_diff = np.subtract.outer(x, y)
print("减法外积（x[i]-y[j]）:")
print(outer_diff)
# [[-3 -2 -1 -0]
#  [-4 -3 -2 -1]
#  [-5 -4 -3 -2]]
```

## 2. 数据中心化（去均值）

机器学习中常见的预处理步骤：将数据按列（或行）减去均值，使数据围绕0分布。

```python
# === 二维数据：5个样本，3个特征 ===
rng = np.random.default_rng(42)
data = rng.standard_normal((5, 3))
print("原始数据:")
print(data)
print("列均值:", data.mean(axis=0))
print()

# === 按列中心化（每列减列均值）===
col_mean = data.mean(axis=0)  # shape (3,)
centered_cols = data - col_mean  # 广播: (5,3) - (3,) → (5,3)
print("按列中心化后（列均值应为≈0）:")
print("列均值:", centered_cols.mean(axis=0))
print()

# === 按行中心化（每行减行均值）===
row_mean = data.mean(axis=1)  # shape (5,)
# 错误方式（广播失败）：
# centered_rows = data - row_mean  # ValueError! (5,3) vs (5,)

# 正确方式：用newaxis将行均值变为列向量
centered_rows = data - row_mean[:, np.newaxis]  # (5,3) - (5,1) → (5,3)
print("按行中心化后（行均值应为≈0）:")
print("行均值:", centered_rows.mean(axis=1))
print()

# === Z-score标准化（减均值，除以标准差）===
col_std = data.std(axis=0)
z_scored = (data - col_mean) / col_std
print("Z-score标准化后（均值≈0，标准差≈1）:")
print("列均值:", z_scored.mean(axis=0))
print("列std:", z_scored.std(axis=0))
```

## 3. 距离矩阵

计算两组点之间所有点对的距离，是广播在实际应用中的经典案例。

```python
# === 欧氏距离矩阵 ===
# points1: m个d维点，shape (m, d)
# points2: n个d维点，shape (n, d)
# 输出: m×n距离矩阵

points1 = np.array([[0, 0], [1, 0], [0, 1], [1, 1]], dtype=float)  # 4个2D点
points2 = np.array([[0.5, 0.5], [2, 2]], dtype=float)              # 2个2D点

# 利用广播：(m, 1, d) - (1, n, d) → (m, n, d)
diff = points1[:, np.newaxis, :] - points2[np.newaxis, :, :]
dist_sq = np.sum(diff ** 2, axis=-1)  # (m, n)
dist = np.sqrt(dist_sq)

print("欧氏距离矩阵:")
print(dist)
# 4个点到2个中心点的距离
print()

# 验证：点[0,0]到点[0.5,0.5]的距离应为 sqrt(0.25+0.25)=sqrt(0.5)≈0.707
print("验证 dist[0,0]:", dist[0, 0], "≈√0.5:", np.sqrt(0.5))
print()

# === 同一组点的距离矩阵（对称矩阵）===
def pairwise_dist(points):
    """计算一组点内所有点对的欧氏距离"""
    diff = points[:, np.newaxis, :] - points[np.newaxis, :, :]
    return np.sqrt(np.sum(diff ** 2, axis=-1))

pts = np.array([[0, 0], [1, 0], [0, 1]])
dist_matrix = pairwise_dist(pts)
print("3x3距离矩阵（对称，对角线为0）:")
print(dist_matrix)
# [[0. 1. 1.]
#  [1. 0. 1.414...]
#  [1. 1.414... 0.]]
print()

# === Manhattan距离（L1距离）===
diff_l1 = np.abs(points1[:, np.newaxis, :] - points2[np.newaxis, :, :])
manhattan_dist = np.sum(diff_l1, axis=-1)
print("Manhattan距离矩阵:")
print(manhattan_dist)
```

## 4. 创建网格与评估函数

广播可以方便地在二维网格上评估二元函数：

```python
# === 在网格上计算函数值 ===
# 创建坐标网格
x = np.linspace(-2, 2, 5)
y = np.linspace(-2, 2, 3)

# 使用newaxis广播
xx = x[np.newaxis, :]  # (1, 5)
yy = y[:, np.newaxis]  # (3, 1)

# 在网格上计算 f(x,y) = x^2 + y^2
z = xx**2 + yy**2
print("网格坐标:")
print("xx:", xx)
print("yy:")
print(yy)
print("z = x^2 + y^2:")
print(z)
# shape: (3, 5) — yy广播到(3,5), xx广播到(3,5)
print()

# 使用meshgrid（等价方法）
XX, YY = np.meshgrid(x, y, indexing='xy')
Z = XX**2 + YY**2
print("meshgrid结果相同:", np.allclose(z, Z))
print()

# === 高斯函数在网格上 ===
x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
XX, YY = np.meshgrid(x, y)
gaussian = np.exp(-(XX**2 + YY**2) / 2)
print("高斯函数网格 shape:", gaussian.shape)  # (100, 100)
print("最大值（中心）:", gaussian.max())       # ≈1.0
```

## 5. 批量运算（向量与矩阵）

广播简化了批量线性代数运算。

```python
# === 批量向量-矩阵乘法 ===
# 将多个向量乘以同一个矩阵
matrix = np.array([[1, 2], [3, 4]], dtype=float)  # (2, 2)
vectors = np.array([[1, 0], [0, 1], [1, 1]], dtype=float)  # 3个向量，shape (3, 2)

# 方法：vectors @ matrix → (3, 2) @ (2, 2) = (3, 2)
# matmul自动处理批量维度
results = vectors @ matrix
print("批量向量-矩阵乘法结果:")
print(results)
print()

# === 广播实现缩放 ===
# 对每列用不同的缩放因子
data = np.ones((4, 3))
scales = np.array([2, 3, 4])  # 每列的缩放因子
scaled = data * scales  # (4,3) * (3,) → (4,3)
print("列缩放:")
print(scaled)
# [[2. 3. 4.]
#  [2. 3. 4.]
#  [2. 3. 4.]
#  [2. 3. 4.]]
print()

# 对每行用不同缩放因子
row_scales = np.array([1, 10, 100, 1000])
row_scaled = data * row_scales[:, np.newaxis]  # (4,3) * (4,1) → (4,3)
print("行缩放:")
print(row_scaled)
# [[1. 1. 1.]
#  [10. 10. 10.]
#  [100. 100. 100.]
#  [1000. 1000. 1000.]]
```

## 6. 条件赋值与掩码操作

结合布尔索引和广播实现复杂的条件操作。

```python
# === where条件选择 ===
a = np.array([[1, -2, 3], [-4, 5, -6]])
print("原始:")
print(a)

# 将负数替换为0（不修改原数组）
result = np.where(a > 0, a, 0)
print("负数置0:")
print(result)
print()

# 使用广播进行条件填充
threshold = np.array([2, 3, 1])  # 每列不同阈值
mask = a > threshold[np.newaxis, :]
print("各列超过阈值:")
print(mask)
print()

# === 多维广播条件 ===
# 对3D数据应用2D掩码
data3d = np.arange(24).reshape(2, 3, 4)
mask2d = np.array([[True, False, True, False],
                   [False, True, False, True],
                   [True, False, True, False]])
# 广播到2个batch
masked = np.where(mask2d[np.newaxis, :, :], data3d, -1)
print("3D数据广播2D掩码 shape:", masked.shape)
```

## 7. 广播的stride=0验证

广播在底层通过stride=0实现"虚拟复制"，不占用额外内存：

```python
a = np.array([[1], [2], [3]])  # shape (3, 1), col vector
b = np.broadcast_to(a, (3, 4))
print("广播后形状:", b.shape)
print("广播后strides:", b.strides)  # (8, 0) — 第二维stride为0！
print("广播后数据:")
print(b)
# 注意：b是只读的（b.flags.writeable = False）
print("是否可写:", b.flags.writeable)
print()

# stride=0意味着沿第二维移动不前进内存，所有列共享同一数据
# 修改a会影响b（因为共享数据）
a[0, 0] = 99
print("修改a后b也改变:")
print(b)  # 第一行全变99
```

## 广播诊断技巧

当广播出错时，以下步骤有助于诊断：

```python
# 1. 打印所有数组的shape
def check_broadcast(*shapes):
    """检查形状是否可以广播，返回输出形状"""
    return np.broadcast_shapes(*shapes)

try:
    print(check_broadcast((2, 3), (4,)))  # 应该失败
except ValueError as e:
    print("广播错误:", e)  # 3 vs 4 不兼容

print(check_broadcast((2, 3), (3,)))    # → (2, 3)
print(check_broadcast((3, 1), (1, 4)))  # → (3, 4)
print(check_broadcast((2, 3, 4), (3, 1)))  # → (2, 3, 4)
```

## 相关概念

- [广播规则](../concepts/04-broadcasting.md) — 广播的4条规则详解
- [ufunc通用函数](../concepts/03-ufunc.md) — ufunc方法（outer、reduce等）
- [索引与切片](../concepts/05-indexing.md) — newaxis在索引中的使用
- [基础数组操作](basic-array-ops.md) — 数组基础操作
