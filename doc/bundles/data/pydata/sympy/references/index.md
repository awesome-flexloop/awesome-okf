---
okf_version: "0.2"
type: index
title: SymPy 信源登记簿
---

# SymPy 信源登记簿（references/）

本目录包含 SymPy 各模块的源码溯源文档，记录类、方法、函数的精确定义位置和签名，作为概念文档的信源基础。

## 核心层信源

| 文档 | 覆盖源文件 | 内容概要 |
|------|-----------|----------|
| [包初始化与顶层API](core-init.md) | `sympy/__init__.py`, `sympy/core/__init__.py`, `sympy/core/singleton.py` | S单例对象、顶层导出清单、子模块结构 |
| [Basic/Expr核心类体系](basic-source.md) | `core/basic.py`, `core/expr.py`, `core/operations.py`, `core/traversal.py` | Basic基类、Expr表达式类、Atom、AssocOp、遍历工具 |
| [数字类型与符号系统](numbers-symbols-source.md) | `core/symbol.py`, `core/numbers.py`, `abc.py` | Symbol/Dummy/Wild、Number层次、单例常量、预定义符号 |
| [sympify与Function体系](sympify-function-source.md) | `core/sympify.py`, `core/function.py`, `core/evalf.py`, `core/relational.py` | sympify/parse_expr、Function/Lambda/Derivative、evalf/N、关系运算 |

## 数学能力层信源

| 文档 | 覆盖源文件 | 内容概要 |
|------|-----------|----------|
| [假设推理系统](assumptions-source.md) | `assumptions/ask.py`, `assumptions/cnf.py`, `assumptions/refine.py`, `assumptions/satask.py` | ask()/Q谓词、CNF/SAT求解、refine() |
| [微积分与积分系统](calculus-integrals-source.md) | `calculus/`, `integrals/` (integrals.py, heurisch.py, risch.py, meijerint.py, transforms.py) | diff/integrate/limit/series、积分算法链、积分变换 |
| [函数库（初等与特殊）](functions-source.md) | `functions/` (elementary/, special/, combinatorial/) | 三角函数/指数对数/双曲/分段、Gamma/Bessel/Zeta/超几何/正交多项式 |
| [化简策略体系](simplify-source.md) | `simplify/` (simplify.py, trigsimp.py, fu.py, cse_main.py, radsimp.py, powsimp.py) | simplify/trigsimp/powsimp/radsimp/fu/cse/nsimplify |
| [级数/极限与求解器](series-solvers-source.md) | `series/`, `solvers/` | series/Order/limit、solve/solveset/dsolve/linsolve/nonlinsolve/nsolve |

## 扩展模块信源

| 文档 | 覆盖源文件 | 内容概要 |
|------|-----------|----------|
| [矩阵系统](matrices-source.md) | `matrices/` (dense.py, matrixbase.py, sparse.py, expressions/) | Matrix/SparseMatrix、特征值/分解/求解、符号矩阵 |
| [多项式代数系统](polys-algebra-source.md) | `polys/` (polytools.py, constructor.py, factortools.py, groebnertools.py) | Poly类、域系统、factor/gcd/Groebner基 |
| [逻辑、集合、数论与离散数学](logic-sets-source.md) | `logic/`, `sets/`, `ntheory/`, `concrete/` | 布尔逻辑、集合运算、数论函数、求和乘积 |
| [张量/统计/打印/代码生成/向量](tensor-stats-source.md) | `tensor/`, `stats/`, `printing/`, `codegen/`, `vector/`, `utilities/lambdify.py` | 索引张量、概率统计、多格式输出、代码生成、向量微积分 |

```{toctree}
:hidden:
:maxdepth: 7

assumptions-source
basic-source
calculus-integrals-source
core-init
functions-source
logic-sets-source
matrices-source
numbers-symbols-source
polys-algebra-source
series-solvers-source
simplify-source
sympify-function-source
tensor-stats-source
```
