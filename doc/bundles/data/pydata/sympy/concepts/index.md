---
okf_version: "0.2"
type: index
title: SymPy 概念文档索引
---

# SymPy 概念文档（concepts/）

本目录包含 SymPy 符号计算的系统化概念文档，从入门到进阶共 13 篇。

## 入门基础

| 编号 | 文档 | 内容概要 |
|------|------|----------|
| 00 | [SymPy 符号计算简介](00-introduction.md) | 符号计算vs数值计算、核心模块概览、安装与快速开始 |
| 01 | [表达式树模型](01-expression-tree.md) | 不可变树结构、args/func、Add/Mul/Pow节点、遍历与操作 |
| 02 | [符号与数值系统](02-symbols-numbers.md) | Symbol/Dummy/Wild、Number层次、S单例常量、abc预定义符号 |
| 03 | [sympify与类型转换](03-sympify-basics.md) | sympify/parse_expr、Function类、Lambda、evalf数值计算、Relational |
| 04 | [函数体系](04-function-basics.md) | 初等函数（三角/指数/双曲/分段）、特殊函数（Gamma/Bessel/正交多项式） |

## 核心机制

| 编号 | 文档 | 内容概要 |
|------|------|----------|
| 05 | [假设推理系统](05-assumptions.md) | is_*属性、ask()/Q谓词、三值逻辑、SAT推理、refine() |
| 06 | [表达式化简](06-simplification.md) | simplify/expand/factor/cancel/trigsimp/powsimp/cse化简策略 |
| 07 | [微积分](07-calculus.md) | diff微分、integrate积分、limit极限、series级数、积分变换 |
| 08 | [方程求解](08-solvers.md) | solve/solveset/linsolve/dsolve/roots/nsolve方程求解体系 |
| 09 | [矩阵运算](09-matrices.md) | Matrix创建、行列式/逆/特征值/分解、SparseMatrix、符号矩阵 |

## 进阶主题

| 编号 | 文档 | 内容概要 |
|------|------|----------|
| 10 | [多项式代数](10-polynomials.md) | Poly类、域系统(ZZ/QQ/GF)、Groebner基、特殊多项式 |
| 11 | [离散数学](11-discrete-math.md) | 布尔逻辑、集合论、数论函数、求和与乘积 |
| 12 | [进阶主题](12-advanced-topics.md) | 张量、统计分布、打印系统、代码生成、向量微积分 |

## 学习路径

1. **新手入门**：00 → 01 → 02 → 03 → 运行 [examples/basic-symbols.md](../examples/basic-symbols.md)
2. **数学运算**：04 → 06 → 07 → 08 → 运行 [examples/calculus-examples.md](../examples/calculus-examples.md)
3. **线性代数**：09 → 运行 [examples/solving-equations.md](../examples/solving-equations.md)
4. **源码溯源**：阅读 [references/](../references/) 中的信源文档

```{toctree}
:maxdepth: 7

00-introduction
01-expression-tree
02-symbols-numbers
03-sympify-basics
04-function-basics
05-assumptions
06-simplification
07-calculus
08-solvers
09-matrices
10-polynomials
11-discrete-math
12-advanced-topics
```
