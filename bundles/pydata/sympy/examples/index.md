---
okf_version: "0.2"
type: index
title: SymPy 示例文档索引
---

# SymPy 实战示例（examples/）

本目录包含 SymPy 的实战示例文档，所有代码均可直接运行。

## 示例列表

| 文档 | 内容概要 | 前置知识 |
|------|----------|----------|
| [基础符号操作实战](basic-symbols.md) | 符号创建、表达式构建、替换(subs)、数值求值(evalf)、类型转换(sympify)、基本化简 | 建议先读 [concepts/00-03](../concepts/00-introduction.md) |
| [微积分实战](calculus-examples.md) | 导数、不定/定积分、极限、泰勒级数、Laplace/Fourier变换、微分方程 | 建议先读 [concepts/07](../concepts/07-calculus.md) |
| [方程求解与矩阵实战](solving-equations.md) | 代数方程、线性/非线性方程组、数值求解、矩阵运算、特征值分解、弹簧-质点综合实战 | 建议先读 [concepts/08-09](../concepts/08-solvers.md) |

## 运行说明

所有示例代码均使用标准 SymPy API：

```python
from sympy import *
x, y, z = symbols('x y z')
init_printing()  # 启用漂亮打印
```

建议按顺序学习：basic-symbols → calculus-examples → solving-equations。
