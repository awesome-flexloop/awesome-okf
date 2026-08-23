---
type: concept
title: "ufunc通用函数"
description: "NumPy ufunc系统的逐元素运算机制、广播、out参数、reduce/accumulate/outer/reduceat/at方法详解"
tags: [numpy, ufunc, vectorization, element-wise, reduction, broadcasting]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: ufunc-source
    resource: /references/ufunc-source.md
    title: "NumPy ufunc通用函数系统源码"
---

# ufunc 通用函数

ufunc（universal function，通用函数）是 NumPy 实现**逐元素（element-wise）运算**的核心机制。ufunc 对 ndarray 中的每个元素执行相同的操作，利用 C 级循环避免 Python 解释器开销，实现高速向量化运算。

## 什么是 ufunc

ufunc 是 C 扩展中定义的函数对象（`PyUFunc_Type` 类型）[F-025]，它具有以下特征：

- **逐元素运算**：对输入数组的每个元素独立执行运算
- **自动广播**：支持不同形状数组之间的运算（遵循广播规则）
- **类型提升**：自动将输入提升为公共类型
- **多输出支持**：可以有多个输出（如 `divmod` 同时返回商和余数）
- **C级循环**：核心运算在C中执行，速度远快于Python循环

ufunc 类本身不直接从Python层导入，而是通过现有ufunc实例获取：`ufunc = type(np.sin)` [F-017]。

## 常用一元 ufunc

一元ufunc接受一个输入，产生一个输出 [F-024]：

```python
import numpy as np

x = np.array([0, np.pi/6, np.pi/4, np.pi/3, np.pi/2])

# 三角函数
np.sin(x)      # 正弦
np.cos(x)      # 余弦
np.tan(x)      # 正切
np.arcsin(x)   # 反正弦
np.arccos(x)   # 反余弦
np.arctan(x)   # 反正切

# 双曲函数
np.sinh(x)     # 双曲正弦
np.cosh(x)     # 双曲余弦
np.tanh(x)     # 双曲正切

# 指数与对数
np.exp(x)      # e^x
np.exp2(x)     # 2^x
np.expm1(x)    # e^x - 1（x接近0时更精确）
np.log(x)      # ln(x)
np.log2(x)     # log2(x)
np.log10(x)    # log10(x)
np.log1p(x)    # ln(1+x)（x接近0时更精确）

# 数值操作
np.sqrt(x)     # 平方根
np.square(x)   # 平方
np.absolute(x) # 绝对值（别名abs）
np.negative(x) # 取负
np.sign(x)     # 符号函数（-1/0/1）
np.ceil(x)     # 向上取整
np.floor(x)    # 向下取整
np.rint(x)     # 四舍五入到最近整数
np.trunc(x)    # 截断小数部分
np.reciprocal(x) # 倒数
np.conjugate(x)  # 复共轭（别名conj）

# 浮点判断
np.isfinite(x) # 是否有限
np.isinf(x)    # 是否无穷
np.isnan(x)    # 是否NaN
np.isnat(x)    # 是否NaT（Not a Time）
```

## 常用二元 ufunc

二元ufunc接受两个输入，产生一个输出 [F-024]：

```python
a = np.array([1, 2, 3, 4])
b = np.array([5, 6, 7, 8])

# 算术运算
np.add(a, b)         # 加法（等价于 a + b）
np.subtract(a, b)    # 减法（a - b）
np.multiply(a, b)    # 乘法（a * b）
np.divide(a, b)      # 真除法（a / b）
np.floor_divide(a, b) # 地板除法（a // b）
np.power(a, b)       # 幂运算（a ** b）
np.remainder(a, b)   # 取余（a % b，别名mod）
np.divmod(a, b)      # 返回商和余数两个输出
np.modf(a)           # 返回小数部分和整数部分

# 比较运算（返回布尔数组）
np.equal(a, b)           # a == b
np.not_equal(a, b)       # a != b
np.less(a, b)            # a < b
np.less_equal(a, b)      # a <= b
np.greater(a, b)         # a > b
np.greater_equal(a, b)   # a >= b
np.maximum(a, b)         # 逐元素取最大值
np.minimum(a, b)         # 逐元素取最小值
np.fmax(a, b)            # 逐元素取最大值（忽略NaN）
np.fmin(a, b)            # 逐元素取最小值（忽略NaN）

# 位运算
np.bitwise_and(a, b)     # 按位与（a & b）
np.bitwise_or(a, b)      # 按位或（a | b）
np.bitwise_xor(a, b)     # 按位异或（a ^ b）
np.left_shift(a, b)      # 左移（a << b）
np.right_shift(a, b)     # 右移（a >> b）
np.invert(a)             # 按位取反（~a）

# 逻辑运算
np.logical_and(a > 0, b > 0)  # 逻辑与
np.logical_or(a > 0, b > 0)   # 逻辑或
np.logical_xor(a > 0, b > 0)  # 逻辑异或
np.logical_not(a > 0)         # 逻辑非
```

## ufunc 的关键属性

每个ufunc对象都有以下属性 [F-029]：

```python
sin = np.sin
sin.nin          # 1 — 输入参数个数
sin.nout         # 1 — 输出参数个数
sin.nargs        # 2 — 总参数个数（nin + nout）
sin.ntypes       # 20+ — 支持的类型循环数量
sin.types        # ['e->e', 'f->f', 'd->d', 'g->g', 'F->F', 'D->D', 'G->G', ...]
sin.identity     # None — 单位元（add为0，multiply为1）
sin.signature    # None — 广义ufunc的签名（普通ufunc为None）
```

对于二元ufunc：
```python
np.add.nin        # 2
np.add.nout       # 1
np.add.identity   # 0 — 加法的单位元
np.multiply.identity  # 1 — 乘法的单位元
np.divide.identity    # None — 除法没有单位元
```

## ufunc 调用的关键字参数

调用ufunc时可以传递以下关键字参数来控制行为：

### out 参数：指定输出数组

`out` 参数允许将结果写入预先分配的数组，避免创建临时数组：

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
result = np.empty(3)
np.add(a, b, out=result)  # 结果写入result
print(result)  # [5. 7. 9.]

# out也可以是元组（多输出ufunc）
quotient, remainder = np.empty(3, dtype=int), np.empty(3, dtype=int)
np.divmod(a, b, out=(quotient, remainder))
```

### where 参数：条件执行

`where` 参数是一个布尔数组，为True的位置才执行运算，False的位置保留输出数组的原值：

```python
a = np.array([1, 2, 3, 4, 5])
result = np.zeros(5)
np.sqrt(a, out=result, where=a > 0)
# 当a>0时计算sqrt，否则保持0（result的初始值）
```

### dtype 和 casting 参数

- `dtype`：指定输出数组的数据类型
- `casting`：控制类型转换严格度（'no'/'equiv'/'safe'/'same_kind'/'unsafe'）

```python
a = np.array([1, 2, 3])
np.add(a, a, dtype=np.float64)  # 输出为float64
```

### order 参数

`order` 指定输出数组的内存顺序：'C'、'F'、'A'（保持输入顺序）、'K'（尽可能保持输入布局）。

## ufunc 的方法

ufunc不仅仅是函数，它还提供了一组强大的方法：

### reduce：规约运算

`reduce` 沿着指定轴重复应用ufunc，将数组规约为更小的维度 [F-028]：

```python
a = np.array([1, 2, 3, 4, 5])
np.add.reduce(a)        # 15 (= 1+2+3+4+5)，等价于np.sum(a)
np.multiply.reduce(a)   # 120 (= 1*2*3*4*5)，等价于np.prod(a)
np.maximum.reduce(a)    # 5，等价于np.max(a)

# 沿指定轴规约
b = np.array([[1, 2, 3], [4, 5, 6]])
np.add.reduce(b, axis=0)  # [5, 7, 9] — 沿行规约（列方向求和）
np.add.reduce(b, axis=1)  # [6, 15] — 沿列规约（行方向求和）

# keepdims：保持维度
np.add.reduce(b, axis=0, keepdims=True)  # shape (1, 3)

# initial：初始值
np.add.reduce(a, initial=10)  # 25 (= 10 + 1+2+3+4+5)
```

`np.sum`、`np.prod`、`np.any`、`np.all`、`np.min`、`np.max` 等函数底层都使用 `reduce` 实现 [F-018]。

### accumulate：累积运算

`accumulate` 沿着轴累积应用ufunc，保留中间结果：

```python
a = np.array([1, 2, 3, 4, 5])
np.add.accumulate(a)      # [1, 3, 6, 10, 15]，等价于np.cumsum(a)
np.multiply.accumulate(a) # [1, 2, 6, 24, 120]，等价于np.cumprod(a)
np.maximum.accumulate(a)  # [1, 2, 3, 4, 5]，累计最大值
```

### reduceat：分段规约

`reduceat` 在指定的位置执行分段规约：

```python
a = np.array([1, 2, 3, 4, 5, 6])
indices = [0, 2, 5]
np.add.reduceat(a, indices)
# [1+2=3, 3+4+5=12, 6=6] → [3, 12, 6]
```

### outer：外积

`outer` 计算两个一维数组的外积（所有元素对的运算结果）：

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
np.multiply.outer(a, b)
# [[ 4,  5,  6],
#  [ 8, 10, 12],
#  [12, 15, 18]]
# 等价于 np.outer(a, b) 对于乘法
np.add.outer(a, b)
# [[5, 6, 7],
#  [6, 7, 8],
#  [7, 8, 9]]
```

> **注意**：`outer` 方法适用于任何二元ufunc，而 `np.outer` 函数只做乘法外积。

### at：无缓冲就地运算

`at` 对数组中指定索引的位置执行**无缓冲**（unbuffered）就地运算。这与普通索引运算不同，普通索引运算可能使用缓冲区导致同位置多次操作被跳过：

```python
a = np.array([1, 2, 3, 4])
# 普通索引加法：相同索引只加一次（缓冲）
b = a.copy()
b[[0, 0, 1]] += 1
print(b)  # [2, 3, 3, 4] — 位置0只加了一次！

# at方法：每个索引独立操作（无缓冲）
c = a.copy()
np.add.at(c, [0, 0, 1], 1)
print(c)  # [3, 3, 3, 4] — 位置0加了两次！
```

## 运算符重载

NumPy 通过ufunc重载了Python的算术运算符，使得 `+`、`-`、`*`、`/` 等运算符自动执行逐元素运算：

| Python运算符 | 对应的ufunc |
|-------------|------------|
| `a + b` | `np.add(a, b)` |
| `a - b` | `np.subtract(a, b)` |
| `a * b` | `np.multiply(a, b)` |
| `a / b` | `np.true_divide(a, b)` |
| `a // b` | `np.floor_divide(a, b)` |
| `a % b` | `np.remainder(a, b)` |
| `a ** b` | `np.power(a, b)` |
| `-a` | `np.negative(a)` |
| `a & b` | `np.bitwise_and(a, b)` |
| `a | b` | `np.bitwise_or(a, b)` |
| `a ^ b` | `np.bitwise_xor(a, b)` |
| `~a` | `np.invert(a)` |
| `a == b` | `np.equal(a, b)` |
| `a < b` | `np.less(a, b)` |

## frompyfunc：从Python函数创建ufunc

`np.frompyfunc` 可以将任意Python函数转换为ufunc，但性能不如内置ufunc（因为每个元素仍需调用Python函数）：

```python
def my_func(x, y):
    return x * y + x + y  # 任意Python逻辑

# 创建ufunc：1个输入？不，frompyfunc(func, nin, nout)
my_ufunc = np.frompyfunc(my_func, 2, 1)
result = my_ufunc(np.array([1, 2, 3]), np.array([4, 5, 6]))
# 注意：frompyfunc返回object类型数组，可能需要astype转换
```

## 广播与ufunc

ufunc运算自动支持广播（broadcasting）——即不同形状的数组可以在运算时自动对齐。广播的详细规则见 [广播规则](04-broadcasting.md)。

```python
a = np.array([[1, 2, 3], [4, 5, 6]])  # shape (2, 3)
b = np.array([10, 20, 30])             # shape (3,)
a + b  # b自动广播为(2, 3)
# [[11, 22, 33],
#  [14, 25, 36]]
```

## 浮点错误控制：errstate

`np.errstate` 上下文管理器可以临时控制浮点错误的处理方式 [F-031]：

```python
with np.errstate(divide='ignore', invalid='ignore'):
    result = np.divide(1, 0)  # 不产生除零警告
    # result 为 inf
```

错误处理模式：
- `'ignore'`：忽略
- `'warn'`：打印警告
- `'raise'`：抛出FloatingPointError
- `'call'`：调用指定的回调函数
- `'print'`：打印警告
- `'log'`：记录到日志

## 相关概念

- [广播规则](04-broadcasting.md) — ufunc运算中的形状对齐机制
- [ndarray多维数组](01-ndarray.md) — ufunc操作的对象
- [dtype数据类型系统](02-dtype-system.md) — ufunc的类型循环选择
- [NumPy ufunc通用函数系统源码](/references/ufunc-source.md) — 源码信源
