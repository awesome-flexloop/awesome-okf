---
type: concept
title: "线性代数与随机数"
description: "NumPy的dot/matmul/einsum张量运算、linalg子包（分解/求逆/特征值）、random模块（Generator/BitGenerator/SeedSequence）"
tags: [numpy, linear-algebra, linalg, dot, matmul, einsum, random, generator, fft]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: core-init
    resource: /references/core-init.md
    title: "NumPy核心初始化源码"
  - id: ufunc-source
    resource: /references/ufunc-source.md
    title: "NumPy ufunc通用函数系统源码"
  - id: ndarray-source
    resource: /references/ndarray-source.md
    title: "NumPy ndarray与数组创建API源码"
---

# 线性代数与随机数

NumPy 提供了完整的数值计算能力，包括矩阵/张量运算、线性代数、快速傅里叶变换和随机数生成。这些功能构成了科学计算的核心工具集。

## 一、矩阵与张量乘法

### np.dot()

`np.dot(a, b)` 计算两个数组的点积：

```python
import numpy as np

# 一维：向量内积
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
np.dot(a, b)  # 32 (= 1*4 + 2*5 + 3*6)

# 二维：矩阵乘法
a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])
np.dot(a, b)
# [[19, 22],
#  [43, 50]]

# 二维×一维：矩阵-向量乘法
np.dot(a, np.array([1, 2]))  # [5, 11]
```

### np.matmul() 与 @ 运算符

`np.matmul(a, b)` 或 `a @ b` 执行矩阵乘法 [F-024]，与 `dot` 的区别在于：
- 不支持标量乘法（用 `*` 做标量乘法）
- 多维时将最后两维视为矩阵，前面的维度作为批量维度广播

```python
a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])
a @ b          # 等价于 np.matmul(a, b)
np.matmul(a, b)
# [[19, 22],
#  [43, 50]]

# 批量矩阵乘法
batch_a = np.random.randn(10, 3, 4)  # 10个3×4矩阵
batch_b = np.random.randn(10, 4, 5)  # 10个4×5矩阵
result = batch_a @ batch_b  # shape (10, 3, 5) — 批量乘法

# 矩阵×向量
a @ np.array([1, 2])  # [5, 11]
```

### np.vdot()

`np.vdot(a, b)` 计算向量点积，会先将输入展平：

```python
a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])
np.vdot(a, b)  # 1*5 + 2*6 + 3*7 + 4*8 = 70
```

### np.inner()

`np.inner(a, b)` 计算内积（最后一维的和积）：

```python
# 向量内积同dot
np.inner([1,2,3], [4,5,6])  # 32

# 多维：最后一维做内积
a = np.arange(24).reshape(2,3,4)
b = np.arange(16).reshape(4,4)
np.inner(a, b).shape  # (2, 3, 4) — a的最后一维(4)和b的最后一维(4)做内积
```

### np.outer()

`np.outer(a, b)` 计算外积（所有元素对的乘积）：

```python
np.outer([1,2,3], [4,5,6])
# [[ 4,  5,  6],
#  [ 8, 10, 12],
#  [12, 15, 18]]
```

### np.tensordot()

`np.tensordot(a, b, axes)` 在指定轴上做张量缩并：

```python
a = np.arange(24).reshape(2, 3, 4)
b = np.arange(20).reshape(4, 5)
# 在a的轴2(4)和b的轴0(4)上缩并
np.tensordot(a, b, axes=([2], [0])).shape  # (2, 3, 5)
```

### np.vecdot() 和 np.vecmat()/np.matvec()

这些是Array API兼容的函数：
- `vecdot(a, b)`：向量点积（支持广播和共轭）
- `matvec(A, x)`：矩阵-向量乘法
- `vecmat(x, A)`：向量-矩阵乘法

## 二、np.einsum()：爱因斯坦求和约定

`np.einsum(subscripts, *operands)` 使用爱因斯坦求和约定执行任意张量运算 [F-023]，是 NumPy 中最灵活的张量运算工具。

### 基本语法

下标字符串（subscripts）用字母标记每个轴，重复的下标表示在该轴上求和：

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# 向量内积：i,i→ （重复的i求和）
np.einsum('i,i->', a, b)  # 32

# 外积：i,j->ij
np.einsum('i,j->ij', a, b)
# [[ 4,  5,  6],
#  [ 8, 10, 12],
#  [12, 15, 18]]

# 矩阵乘法：ik,kj->ij
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
np.einsum('ik,kj->ij', A, B)
# [[19, 22],
#  [43, 50]]
```

### 常见 einsum 模式

```python
A = np.random.randn(3, 4)
B = np.random.randn(4, 5)

# 矩阵的迹（对角线之和）
M = np.array([[1,2],[3,4]])
np.einsum('ii->', M)  # 5 (= 1+4)

# 转置
np.einsum('ij->ji', A).shape  # (4, 3)

# 对行求和
np.einsum('ij->j', A)  # 等价于 A.sum(axis=0)

# 对列求和
np.einsum('ij->i', A)  # 等价于 A.sum(axis=1)

# 批量矩阵乘法
batch_A = np.random.randn(10, 3, 4)
batch_B = np.random.randn(10, 4, 5)
np.einsum('nik,nkj->nij', batch_A, batch_B).shape  # (10, 3, 5)
```

### einsum_path：优化收缩路径

`np.einsum_path()` 可以计算最优的张量收缩顺序，避免中间结果过大：

```python
path_info = np.einsum_path('ij,jk,kl->il', A, B, np.random.randn(5,6), optimize='optimal')
print(path_info[1])  # 打印优化信息
```

## 三、numpy.linalg 子包

`numpy.linalg` 提供了完整的线性代数功能 [F-005]，底层依赖 BLAS 和 LAPACK。

### 矩阵和向量乘积

```python
from numpy import linalg as LA

A = np.array([[1, 2], [3, 4]])
b = np.array([5, 6])

LA.norm(A)        # 矩阵/向量范数
LA.cond(A)        # 条件数
LA.matrix_rank(A) # 矩阵秩
LA.det(A)         # 行列式
```

### 矩阵分解

```python
# Cholesky分解（正定矩阵）
L = LA.cholesky(np.array([[4, 2], [2, 3]]))
# [[2. 0.], [1. 1.414...]]

# QR分解
Q, R = LA.qr(A)

# SVD（奇异值分解）
U, S, Vh = LA.svd(A)

# 特征值分解
eigenvalues, eigenvectors = LA.eig(A)
eigenvalues = LA.eigvals(A)  # 仅特征值

# 对称/Hermite矩阵特征值
eigenvalues, eigenvectors = LA.eigh(A)  # 更稳定，适用于对称矩阵

# 广义特征值问题
LA.eig(A, B)  # Ax = λBx
```

### 求解线性方程组

```python
# 求解 Ax = b
x = LA.solve(A, b)
print(A @ x)  # [5., 6.] ≈ b

# 最小二乘解
x, residuals, rank, s = LA.lstsq(A, b, rcond=None)

# 矩阵求逆
A_inv = LA.inv(A)
print(A @ A_inv)  # ≈ 单位矩阵

# 伪逆
LA.pinv(A)

# 张量求解
LA.tensorsolve(A, b)
LA.tensorinv(A)
```

### 常用函数

```python
LA.norm([3, 4])           # 5.0 — L2范数
LA.norm([3, 4], ord=1)    # 7.0 — L1范数
LA.norm(A, ord='fro')     # Frobenius范数
LA.multi_dot([A, B, C])   # 高效链式矩阵乘法（自动优化括号）
LA.matrix_power(A, 3)     # 矩阵幂（A^3）
```

## 四、numpy.fft 子包

`numpy.fft` 提供快速傅里叶变换（FFT）功能：

```python
from numpy import fft

# 标准FFT
x = np.array([1, 2, 3, 4])
fft.fft(x)        # 离散傅里叶变换
fft.ifft(x)       # 逆变换

# 实数FFT（更高效，利用对称性）
fft.rfft(x)       # 实数输入的FFT
fft.irfft(x)      # 逆实数FFT

# 多维FFT
img = np.random.randn(64, 64)
fft.fft2(img)     # 二维FFT
fft.fftn(img)     # N维FFT

# 频率轴
fft.fftfreq(100, d=0.01)  # 频率采样点
fft.rfftfreq(100, d=0.01)

# 频谱移位
fft.fftshift(x)   # 将零频率移到中心
fft.ifftshift(x)  # 逆移位
```

## 五、numpy.random：随机数生成

NumPy 1.17+ 引入了新的随机数API，核心组件包括：

- **Generator**：用户接口，提供各种分布的采样方法
- **BitGenerator**：底层随机比特流生成器
- **SeedSequence**：种子初始化，用于创建独立的随机流

### 创建Generator

```python
from numpy.random import default_rng, Generator, MT19937, PCG64, PCG64DXSM, Philox, SFC64, SeedSequence

# 默认推荐方式
rng = default_rng(42)  # 使用PCG64DXSM，种子42

# 也可指定BitGenerator
rng = Generator(PCG64(42))
rng = Generator(MT19937(42))  # 经典Mersenne Twister
rng = Generator(Philox(42))   # 计数器模式（可并行）
rng = Generator(SFC64(42))    # 快速小型生成器
```

### 可用的BitGenerators [F-025]

| BitGenerator | 说明 | 特点 |
|-------------|------|------|
| `MT19937` | Mersenne Twister | 经典、周期极长（2^19937-1），但启动慢、内存大 |
| `PCG64` / `PCG64DXSM` | 排列同余生成器 | 默认、快速、统计质量好、DXSM支持更大并行流 |
| `Philox` | 计数器基生成器 | 确定性、可通过不同counter生成独立流、适合并行 |
| `SFC64` | Small Fast Chaotic | 最快、最小内存、良好统计质量 |

### SeedSequence：高质量种子初始化

```python
# 使用SeedSequence创建多个独立流
ss = SeedSequence(42)
child_seeds = ss.spawn(4)  # 创建4个独立子种子
streams = [default_rng(s) for s in child_seeds]
# 这4个rng产生独立的随机数序列，不会重叠
```

### 常用分布采样

```python
rng = default_rng(42)

# 均匀分布
rng.random((3, 4))              # [0, 1)均匀分布，shape (3,4)
rng.uniform(0, 10, (3, 4))     # [0, 10)均匀分布
rng.integers(0, 100, (5,))     # 整数[0, 100)

# 正态分布
rng.standard_normal((3, 4))    # 标准正态 N(0,1)
rng.normal(0, 1, (3, 4))      # N(loc, scale)
rng.lognormal(0, 1, (3,))     # 对数正态

# 其他连续分布
rng.exponential(1.0, (3,))    # 指数分布
rng.gamma(2, 1.0, (3,))       # Gamma分布
rng.beta(0.5, 0.5, (3,))      # Beta分布
rng.chisquare(2, (3,))        # 卡方分布
rng.uniform(0, 1, (3,))       # 均匀分布

# 离散分布
rng.binomial(10, 0.5, (3,))   # 二项分布
rng.poisson(5, (3,))          # 泊松分布
rng.geometric(0.5, (3,))      # 几何分布
rng.choice([1,2,3], 5, p=[0.2, 0.3, 0.5])  # 指定概率的选择

# 排列和洗牌
rng.permutation(10)             # 0-9的随机排列
rng.permutation([1, 2, 3, 4])   # 序列的随机排列
arr = np.array([1, 2, 3, 4])
rng.shuffle(arr)                # 原地洗牌
arr2 = rng.permutation(arr)     # 返回新排列数组（不修改原数组）
```

### 多维分布

```python
# 多元正态分布
mean = [0, 0]
cov = [[1, 0.5], [0.5, 1]]
rng.multivariate_normal(mean, cov, 100)  # 100个二维样本

# 多元正态（更高效）
from numpy.random import MultivariateNormal
```

### 旧API（RandomState，兼容性保留）

```python
# 旧API（不推荐新代码使用，但保留向后兼容）
np.random.seed(42)           # 全局种子
np.random.rand(3, 4)         # [0,1)均匀
np.random.randn(3, 4)        # 标准正态
np.random.randint(0, 10, 5)  # 整数
np.random.permutation(10)    # 排列
# 旧API使用全局状态，不可重入，不推荐
```

## 六、其他核心数值功能

### np.cross()：叉积

```python
np.cross([1, 0, 0], [0, 1, 0])  # [0, 0, 1] — 三维叉积
```

### np.kron()：Kronecker积

```python
np.kron([1, 2], [3, 4])  # [3, 4, 6, 8]
```

### 规约运算（基于ufunc.reduce）

```python
a = np.array([[1, 2, 3], [4, 5, 6]])
np.sum(a)           # 21 — 所有元素求和
np.sum(a, axis=0)   # [5, 7, 9] — 沿轴0（列方向）
np.sum(a, axis=1)   # [6, 15] — 沿轴1（行方向）
np.prod(a)          # 720 — 乘积
np.mean(a)          # 3.5 — 均值
np.std(a)           # 标准差
np.var(a)           # 方差
np.min(a)           # 1
np.max(a)           # 6
np.argmin(a)        # 0（展平后的索引）
np.argmax(a)        # 5
np.cumsum(a)        # [1, 3, 6, 10, 15, 21] — 累积和
np.cumprod(a)       # 累积乘积
np.trace(a)         # 迹（对角线之和）
```

## 相关概念

- [ufunc通用函数](03-ufunc.md) — matmul/vecdot等是特殊ufunc
- [广播规则](04-broadcasting.md) — matmul和线性代数中的广播行为
- [索引与切片](05-indexing.md) — 矩阵操作中的索引技巧
- [NumPy ufunc通用函数系统源码](/references/ufunc-source.md) — 源码信源
