---
okf_version: "0.2"
type: example
title: NumPy 基础数组操作
description: 从创建数组、索引切片、广播运算到线性代数的常见NumPy操作速查
tags: [numpy, array, basics, tutorial]
generated: { by: reference_agent/trae-glm, at: 2026-08-22T14:35:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T14:40:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: numpy-multiarray
    resource: /references/core-init.md
    title: NumPy 核心模块
---

# NumPy 基础数组操作

## 数组创建

```python
import numpy as np

# 从列表创建
a = np.array([1, 2, 3], dtype=np.float64)

# 特殊数组
np.zeros((3, 4))          # 3×4全零矩阵
np.ones((2, 3))           # 2×3全一矩阵
np.empty((2, 2))          # 未初始化（速度最快）
np.full((3, 3), 7)        # 填充指定值
np.eye(3)                 # 3×3单位矩阵

# 序列
np.arange(0, 10, 2)       # [0, 2, 4, 6, 8]
np.linspace(0, 1, 5)      # [0., 0.25, 0.5, 0.75, 1.]
np.logspace(0, 2, 3)      # [1., 10., 100.]

# 随机
np.random.seed(42)
np.random.rand(3, 3)      # [0,1)均匀分布
np.random.randn(3, 3)     # 标准正态分布
np.random.randint(0, 10, size=(2, 3))  # 随机整数
```

## 索引与切片

```python
a = np.arange(12).reshape(3, 4)
# [[ 0  1  2  3]
#  [ 4  5  6  7]
#  [ 8  9 10 11]]

a[0, 1]        # 1 — 基本索引
a[:, 0]        # [0, 4, 8] — 第一列
a[1:, :2]      # 右下角2×2
a[a > 5]       # 布尔索引: [6, 7, 8, 9, 10, 11]
a[[0, 2]]      # 花式索引: 第0行和第2行
```

## 广播运算

```python
a = np.array([[1, 2, 3], [4, 5, 6]])
b = np.array([10, 20, 30])
c = a + b      # b被广播: [[11, 22, 33], [14, 25, 36]]

# 标量广播
a * 2          # 所有元素×2

# 外积
x = np.array([1, 2, 3])
y = np.array([4, 5])
np.add.outer(x, y)  # shape (3,2): [[5,6],[6,7],[7,8]]
```

## 聚合与统计

```python
a = np.random.randn(1000, 100)

a.mean()          # 全局均值
a.mean(axis=0)    # 每列均值 (100,)
a.sum(axis=1)     # 每行求和
a.std(axis=0)     # 每列标准差
a.min(), a.max()  # 全局极值
a.argmax(axis=1)  # 每行最大值索引
np.median(a)      # 中位数
np.percentile(a, [25, 50, 75], axis=0)  # 四分位数
```

## 矩阵操作

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

A @ B             # 矩阵乘法 [[19,22],[43,50]]
A.T               # 转置
np.linalg.inv(A)  # 逆矩阵
np.linalg.det(A)  # 行列式
np.linalg.eig(A)  # 特征值和特征向量
np.linalg.solve(A, np.array([1, 2]))  # 解线性方程组
```

## 形状操作

```python
a = np.arange(12)
a.reshape(3, 4)       # 改变形状（返回视图）
a.reshape(-1, 3)      # -1自动推断: (4, 3)
a[:, np.newaxis]      # 增加维度: (12,)→(12,1)
a.flatten()           # 展平为1D（返回拷贝）
a.ravel()             # 展平为1D（尽可能视图）
np.vstack([a, a])     # 垂直堆叠
np.hstack([a[:6], a[6:]])  # 水平拼接
np.split(a, 3)        # 等分为3份
```
