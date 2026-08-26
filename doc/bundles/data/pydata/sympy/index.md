---
okf_version: "0.2"
---

# SymPy 符号计算库知识库

本知识包是 [SymPy](https://www.sympy.org)（Python 符号计算库，纯 Python 实现的 CAS）的系统化中文教程，基于 SymPy 1.x 源码（`sympy/sympy/` 目录）深度阅读生成，覆盖从表达式树模型到微积分、求解器、矩阵、多项式的完整符号计算知识体系。所有内容均溯源至 SymPy 源码，遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 入门基础（concepts/）

* [SymPy 符号计算简介](concepts/00-introduction.md) — 符号计算vs数值计算、BSD许可证、核心模块概览、安装与快速开始。
* [表达式树模型](concepts/01-expression-tree.md) — 不可变树结构、Basic/Expr/Atom层次、args/func恒等式、Add/Mul/Pow节点、subs/xreplace/doit/rewrite操作、遍历机制。
* [符号与数值系统](concepts/02-symbols-numbers.md) — Symbol/Dummy/Wild符号、Number/Integer/Rational/Float层次、S单例常量、symbols()批量创建、abc预定义符号。
* [sympify与类型转换](concepts/03-sympify-basics.md) — sympify()转换、parse_expr()字符串解析、Function/Lambda/Derivative、evalf()/N()数值计算、Relational关系运算。
* [函数体系](concepts/04-function-basics.md) — 初等函数（三角/指数/对数/双曲/复数/分段/Piecewise）、特殊函数（Gamma/Bessel/误差/超几何/正交多项式）、rewrite/expand机制。

## 核心机制（concepts/）

* [假设推理系统](concepts/05-assumptions.md) — is_*属性、ask()/Q谓词、三值逻辑(True/False/None)、CNF合取范式、SAT求解、refine()假设化简。
* [表达式化简](concepts/06-simplification.md) — simplify()启发式化简、expand/factor/cancel/together/apart、trigsimp/fu三角化简、powsimp/radsimp/ratsimp、cse公共子表达式消除。
* [微积分](concepts/07-calculus.md) — diff()微分、integrate()积分(不定/定积分/算法链)、limit()极限(Gruntz算法)、series()泰勒级数、Laplace/Fourier/Mellin积分变换。
* [方程求解](concepts/08-solvers.md) — solve()代数求解、solveset()集合求解、linsolve()/nonlinsolve()方程组、dsolve()常微分方程、roots()多项式求根、nsolve()数值求解。
* [矩阵运算](concepts/09-matrices.md) — Matrix创建与运算、行列式/逆/秩/迹、特征值/对角化/Jordan形、LU/QR/Cholesky/SVD分解、SparseMatrix稀疏矩阵、MatrixSymbol符号矩阵。

## 进阶主题（concepts/）

* [多项式代数](concepts/10-polynomials.md) — Poly类与显式生成元、域系统(ZZ/QQ/GF)、gcd/factor/结式/判别式、Groebner基、特殊/正交多项式、RootOf。
* [离散数学](concepts/11-discrete-math.md) — 布尔逻辑(And/Or/Not/Xor/Implies)、集合运算(Interval/FiniteSet/Union)、数论(isprime/factorint/totient)、求和与乘积(Sum/Product)。
* [进阶主题](concepts/12-advanced-topics.md) — 张量(Indexed/NDimArray)、统计分布(P/E/density)、打印系统(latex/pretty)、代码生成(lambdify/codegen/autowrap)、向量微积分(CoordSys3D/Del)。

## 实战示例（examples/）

* [基础符号操作实战](examples/basic-symbols.md) — 符号创建、表达式构建、subs替换、evalf数值求值、sympify转换、化简操作，全部代码可直接运行。
* [微积分实战](examples/calculus-examples.md) — 导数计算、不定/定积分、极限、泰勒级数、Laplace/Fourier变换、微分方程dsolve。
* [方程求解与矩阵实战](examples/solving-equations.md) — 代数方程/方程组求解、矩阵运算与特征值分解、弹簧-质点系统综合实战。

## 信源登记簿（references/）

* [包初始化与顶层API](references/core-init.md) — `sympy/__init__.py` 顶层导出、S单例对象(SingletonRegistry)、子模块结构。
* [Basic/Expr核心类体系源码](references/basic-source.md) — `core/basic.py` Basic基类、`core/expr.py` Expr类、Atom/AssocOp、表达式遍历。
* [数字类型与符号系统源码](references/numbers-symbols-source.md) — `core/symbol.py` Symbol/Dummy/Wild、`core/numbers.py` 数字层次与单例常量、`abc.py` 预定义符号。
* [sympify转换与Function函数体系源码](references/sympify-function-source.md) — `core/sympify.py`、`core/function.py` Function/Lambda/Derivative、`core/evalf.py` 数值计算、`core/relational.py` 关系运算。
* [假设推理系统源码](references/assumptions-source.md) — `assumptions/ask.py` ask()/Q、`assumptions/cnf.py` CNF编码、SAT求解器、refine()。
* [微积分与积分系统源码](references/calculus-integrals-source.md) — `calculus/` 工具、`integrals/` 积分算法链(heurisch/Risch/MeijerG/manualintegrate)、积分变换。
* [函数库（初等与特殊）源码](references/functions-source.md) — `functions/elementary/`、`functions/special/`、`functions/combinatorial/` 全部函数类清单。
* [化简策略体系源码](references/simplify-source.md) — `simplify/` 各化简函数、FU三角算法、cse公共子表达式消除。
* [级数/极限与求解器源码](references/series-solvers-source.md) — `series/` 级数展开、`solvers/` 代数/微分/数值求解器。
* [矩阵系统源码](references/matrices-source.md) — `matrices/dense.py` Matrix、`matrices/matrixbase.py` MatrixBase、稀疏矩阵、符号矩阵表达式。
* [多项式代数系统源码](references/polys-algebra-source.md) — `polys/polytools.py` Poly类、域系统、Groebner基、正交多项式。
* [逻辑、集合、数论与离散数学源码](references/logic-sets-source.md) — `logic/boolalg.py` 布尔逻辑、`sets/` 集合运算、`ntheory/` 数论、`concrete/` 求和乘积。
* [张量/统计/打印/代码生成/向量系统源码](references/tensor-stats-source.md) — `tensor/`、`stats/`、`printing/`、`codegen/`、`vector/`、`utilities/lambdify.py`。

## 学习路径建议

1. **新手入门**：00-introduction → 01-expression-tree → 02-symbols-numbers → 03-sympify-basics → 运行 examples/basic-symbols.md
2. **数学运算核心**：04-function-basics → 05-assumptions → 06-simplification → 07-calculus → 08-solvers → 运行 examples/calculus-examples.md
3. **线性代数与进阶**：09-matrices → 运行 examples/solving-equations.md → 10-polynomials → 11-discrete-math → 12-advanced-topics
4. **源码溯源**：阅读 references/ 中的信源文档，理解API的底层实现机制

## 信任与生命周期说明

* **status 判定依据**：全部 32 个内容文档（13 个概念 + 3 个示例 + 13 个信源登记 + 3 个子目录 index）+ 根 index.md + log.md，非 index/log 文件均 `status: stable`。内容基于对 SymPy 1.x 源码（`external/libs/python/sympy/sympy/sympy/` 目录）41个子模块的逐模块阅读与事实提取（148个编号源码事实 F-001 ~ F-148）。
* **stale_after 解释**：统一设置为 `2027-12-31`。SymPy 核心 API（Basic/Expr/Symbol/Number/Add/Mul/Pow、sympify、simplify、integrate、solve、Matrix）自 SymPy 1.0 以来保持高度稳定，该日期作为对未来大版本变化的保守重新评估节点。
* **核验链路**：`generated.at` 记录原始生成时刻（2026-04-22）；`verified.at` 记录过程核验事件（2026-04-22），所有类名、函数名、参数名均通过源码Read/Grep验证，示例代码通过Python执行验证。
* **覆盖范围**：覆盖 core/、assumptions/、calculus/、functions/、integrals/、simplify/、series/、solvers/、matrices/、polys/、logic/、ntheory/、sets/、stats/、concrete/、tensor/、printing/、parsing/、codegen/、utilities/、vector/ 共22个核心模块；排除 physics/、geometry/、plotting/、crypto/、holonomic/、liealgebras/、categories/、combinatorics/、diffgeom/、discrete/ 等领域专用模块。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
