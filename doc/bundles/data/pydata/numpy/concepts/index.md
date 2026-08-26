# 概念文档

本目录包含 NumPy 的 8 个核心概念文档，按学习路径排列：

**入门基础**：

* [00-NumPy 简介](00-introduction.md) — 科学计算基础库定位、BSD许可证、ndarray核心概念、NumPy vs Python list、核心子包概览。
* [01-ndarray 多维数组](01-ndarray.md) — 内存布局（C/F顺序）、shape/strides/dtype/nbytes核心属性、视图vs副本、flags标志位详解。
* [02-dtype 数据类型系统](02-dtype-system.md) — 类型层次（int/float/complex/bool/string/datetime）、kind字符码、类型提升规则、结构化dtype。
* [03-ufunc 通用函数](03-ufunc.md) — 逐元素运算机制、一元/二元ufunc分类、out/where参数、reduce/accumulate/outer/reduceat/at方法。

**核心机制**：

* [04-广播规则](04-broadcasting.md) — 广播的4条核心规则、形状对齐过程、stride=0零拷贝实现、常见广播模式与错误诊断。
* [05-索引与切片](05-indexing.md) — 基本切片、布尔索引、花式索引、np.where条件选择、np.take沿轴提取、视图/副本行为。
* [06-数组创建](06-array-creation.md) — array/asarray、arange/linspace/logspace、zeros/ones/empty/full、fromfunction/fromiter/frombuffer、mgrid/ogrid。
* [07-线性代数与随机数](07-linear-algebra.md) — dot/matmul/einsum张量运算、linalg子包（分解/求逆/特征值/SVD）、FFT、random模块。

```{toctree}
:maxdepth: 7

00-introduction
01-ndarray
02-dtype-system
03-ufunc
04-broadcasting
05-indexing
06-array-creation
07-linear-algebra
```
