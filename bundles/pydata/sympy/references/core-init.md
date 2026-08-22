---
okf_version: "0.2"
type: reference
title: SymPy 包初始化与顶层API
description: SymPy顶层__init__.py导出清单、S单例对象、symbols/sympify等核心入口函数
sources:
  - id: sympy-init
    resource: external/libs/python/sympy/sympy/sympy/__init__.py
    title: SymPy 包入口
  - id: sympy-core-init
    resource: external/libs/python/sympy/sympy/sympy/core/__init__.py
    title: SymPy core 初始化
---

# SymPy 包初始化与顶层 API

SymPy 是一个纯 Python 实现的计算机代数系统（CAS），顶层包 `sympy/__init__.py` 承担环境检查、依赖验证和子模块符号聚合导出三项职责。[^F-069]

## 环境与依赖检查

```python
# sympy/__init__.py 关键检查项
import sys
if sys.version_info < (3, 9):
    raise ImportError("Python version 3.9 or above is required for SymPy.")

try:
    import mpmath
except ImportError:
    raise ImportError("SymPy now depends on mpmath as an external library. ...")
```

- **Python 版本要求**：≥ 3.9[^F-069]
- **强制依赖**：mpmath（任意精度浮点运算库）[^F-069]
- **版本属性**：`__version__` 从 `sympy.release` 模块导入[^F-069]
- **调试开关**：环境变量 `SYMPY_DEBUG` 控制开发版警告输出，通过 `__sympy_debug()` 函数读取[^F-069]
- **延迟加载**：`test` 和 `doctest` 函数通过 `lazy_function` 延迟导入，避免启动时加载测试框架[^F-071]
- **初始化钩子**：导入末尾调用 `evalf._create_evalf_table()` 注册数值求值处理表[^F-071]

## S 单例注册表

`S` 是 `SingletonRegistry` 类的全局唯一实例，定义于 `core/singleton.py`，承担双重角色：[^F-065]

### 角色一：单例对象注册表

`S` 通过属性访问提供所有 SymPy 单例常量的统一入口。单例类使用 `metaclass=Singleton` 元类实现，实例化被拦截为返回唯一实例，首次访问时通过 `__getattr__` 延迟创建并缓存。[^F-065]

| 属性 | 类型 | 含义 |
|---|---|---|
| `S.Zero` | `Integer(0)` | 整数零 |
| `S.One` | `Integer(1)` | 整数一 |
| `S.NegativeOne` | `Integer(-1)` | 整数负一 |
| `S.Half` | `Rational(1, 2)` | 有理数 1/2 |
| `S.Infinity` | `oo` | 正无穷 ∞ |
| `S.NegativeInfinity` | `-oo` | 负无穷 -∞ |
| `S.ComplexInfinity` | `zoo` | 复无穷（无方向） |
| `S.NaN` | `nan` | 非数 Not a Number |
| `S.ImaginaryUnit` | `I` | 虚数单位 i = √(-1) |
| `S.Exp1` | `E` | 自然对数底 e ≈ 2.71828... |
| `S.Pi` | `pi` | 圆周率 π ≈ 3.14159... |
| `S.GoldenRatio` | — | 黄金分割比 φ = (1+√5)/2 |
| `S.EulerGamma` | — | 欧拉常数 γ ≈ 0.57721... |
| `S.Catalan` | — | Catalan 常数 G ≈ 0.91596... |
| `S.TribonacciConstant` | — | Tribonacci 常数 |
| `S.true` | `BooleanTrue` | 布尔真 |
| `S.false` | `BooleanFalse` | 布尔假 |

单例化带来两个优势：节省内存（多次引用指向同一实例）、快速比较（可用 `is` 而非 `==` 进行身份比较）。[^F-065]

```python
>>> from sympy import S, Integer
>>> Integer(0) is S.Zero
True
>>> 0 == S.Zero      # Python int 0 和 S.Zero 不共享身份
True
>>> 0 is S.Zero      # 注意：非 SymPy 对象不能用 is 比较
False
```

### 角色二：sympify 快捷方式

`S.__call__` 直接委托给 `sympify()` 函数，使得 `S(1)` 等价于 `sympify(1)`，常用于快速构造精确有理数：[^F-065]

```python
>>> from sympy import S, symbols
>>> x = symbols('x')
>>> x + S(1)/2      # S(1) 返回 Integer(1)，除法产生 Rational(1,2)
x + 1/2
>>> x + 1/2         # Python 1/2 直接求值为 float 0.5
x + 0.5
```

## 核心入口函数

以下函数从 `sympy.core` 子模块直接导出到顶层命名空间：[^F-066][^F-070]

### 符号与表达式创建

| 函数 | 签名概要 | 功能 |
|---|---|---|
| `symbols(names, *, cls=Symbol, **args)` | 字符串→符号 | 批量创建符号，逗号/空格分隔，`seq=True` 返回元组 |
| `Symbol(name, **assumptions)` | 构造函数 | 创建单个命名符号 |
| `Dummy(name=None, **assumptions)` | 构造函数 | 创建唯一匿名符号（同名不相等） |
| `Wild(name, exclude=(), properties=())` | 构造函数 | 创建模式匹配通配符 |
| `var(names, **args)` | 字符串→None | 将符号注入调用者命名空间 |
| `sympify(a, locals=None, ...)` | 任意对象→Basic | 将 Python 对象转换为 SymPy 类型 |

```python
>>> from sympy import symbols, sympify, S, Integer, Rational
>>> x, y, z = symbols('x y z')
>>> sympify(3.14)
3.14000000000000
>>> sympify(42)         # Python int → Integer
42
>>> sympify("x**2 + 1") # 字符串解析
x**2 + 1
>>> S(1)/3              # 精确有理数
1/3
>>> type(S(1)/3)
<class 'sympy.core.numbers.Rational'>
```

**sympify 转换规则**：[^F-045]

| Python 输入类型 | 转换目标 |
|---|---|
| `int` | `Integer` |
| `float` | `Float` |
| `str` | 解析为 SymPy 表达式 |
| SymPy 对象 | 原样返回 |
| 其他类型 | 查询 `converter` 字典中注册的转换函数，失败抛出 `SympifyError` |

`converter` 全局字典（core/sympify.py 第41行）注册自定义类型到 SymPy 类型的转换函数，类型 `dict[type[Any], Callable[[Any], Basic]]`，支持扩展以适配第三方库类型。[^F-046]

### 微积分与代数运算

| 函数 | 功能 |
|---|---|
| `simplify(expr, **kwargs)` | 表达式化简（委托给 simplify 子模块） |
| `integrate(f, *args, **kwargs)` | 定积分/不定积分 |
| `diff(f, *symbols, **kwargs)` | 求导 |
| `limit(e, x, xlim, dir='+')` | 极限计算 |
| `series(e, x=None, x0=0, n=6, ...)` | 级数展开 |
| `solve(f, *symbols, **flags)` | 代数方程求解 |
| `dsolve(eq, func=None, ...)` | 常微分方程求解 |
| `expand(e, **hints)` | 表达式展开 |
| `factor(f, *gens, **args)` | 因式分解 |
| `collect(e, syms, ...)` | 按符号合并同类项 |
| `N(x, n=15, **options)` | 数值求值（等价于 `sympify(x).evalf(n)`） |

```python
>>> from sympy import integrate, diff, limit, sin, symbols, solve, dsolve, Function, Eq
>>> x = symbols('x')
>>> integrate(sin(x), x)
-cos(x)
>>> diff(x**3, x)
3*x**2
>>> limit(sin(x)/x, x, 0)
1
>>> solve(x**2 - 4, x)
[-2, 2]
>>> # ODE 求解
>>> f = Function('f')
>>> dsolve(Eq(f(x).diff(x), f(x)), f(x))
Eq(f(x), C1*exp(x))
```

### 方程求解器体系

顶层 `sympy` 从 `.solvers` 子模块导出完整的方程求解器栈：[^F-070]

| 求解器 | 功能 |
|---|---|
| `solve(f, *symbols)` | 通用代数方程求解 |
| `solveset(f, symbol, domain)` | 集合形式的方程求解（新版API） |
| `linsolve(system, *symbols)` | 线性方程组求解 |
| `nonlinsolve(system, *symbols)` | 非线性方程组求解 |
| `nsolve(f, x0)` | 数值求根 |
| `dsolve(eq, func)` | 常微分方程（ODE）求解 |
| `pdsolve(eq, func)` | 偏微分方程（PDE）求解 |
| `rsolve(f, y)` | 递推方程求解 |
| `diophantine(eq)` | 丢番图方程（整数解） |
| `classify_ode(eq)` | 分类ODE类型 |
| `checkodesol(eq, sol)` | 验证ODE解 |
| `classify_pde(eq)` | 分类PDE类型 |
| `checkpdesol(eq, sol)` | 验证PDE解 |
| `reduce_inequalities(ineqs)` | 不等式化简 |

### 数值求值

- `evalf(x, prec, options)`：底层数值求值引擎，接受二进制精度 `prec`[^F-060]
- `EvalfMixin` 类提供 `.evalf(n=15, ...)` 方法和 `.n` 属性别名[^F-058]
- `N()` 函数是顶层便捷入口，等价于 `sympify(x).evalf(n)`[^F-059]

```python
>>> from sympy import pi, N
>>> N(pi, 30)
3.14159265358979323846264338328
>>> pi.evalf(5)
3.1416
```

## 核心类型

| 类型 | 所属模块 | 说明 |
|---|---|---|
| `Basic` | core/basic.py | 所有 SymPy 对象的基类 |
| `Atom` | core/basic.py | 叶子节点基类 |
| `Expr` | core/expr.py | 代数表达式基类 |
| `AtomicExpr` | core/expr.py | 原子表达式（Atom + Expr） |
| `UnevaluatedExpr` | core/expr.py | 保持不求值的表达式包装 |
| `Number` / `Integer` / `Rational` / `Float` | core/numbers.py | 数字类型层次 |
| `NumberSymbol` | core/numbers.py | 数学常量符号基类（Exp1/Pi 等） |
| `AlgebraicNumber` | core/numbers.py | 代数数 |
| `Add` / `Mul` / `Pow` | core/add.py, mul.py, power.py | 加法/乘法/幂运算节点 |
| `Mod` | core/mod.py | 取模运算 |
| `Symbol` / `Dummy` / `Wild` | core/symbol.py | 符号类层次 |
| `Function` / `AppliedUndef` | core/function.py | 函数类与未定义函数应用 |
| `Lambda` | core/function.py | Lambda 匿名函数 |
| `Derivative` | core/function.py | 未求值导数 |
| `Subs` | core/function.py | 未求值替换 |
| `Tuple` / `Dict` | core/containers.py | 容器类型 |
| `Matrix` | matrices | 矩阵类型 |
| `Poly` | polys | 多项式类型 |

关系运算类从 `core.relational` 导出：`Eq`（相等）、`Ne`（不等）、`Gt`（严格大于）、`Ge`（大于等于）、`Lt`（严格小于）、`Le`（小于等于），以及全称类名 `Equality`、`Unequality`、`StrictGreaterThan`、`GreaterThan`、`StrictLessThan`、`LessThan`。[^F-062]

## 子模块结构

顶层 `__init__.py` 从以下子模块聚合导出符号：[^F-070]

| 子模块 | 核心导出 | 功能领域 |
|---|---|---|
| `.core` | Basic, Expr, Symbol, sympify, S 等 | 核心表达式体系 |
| `.logic` | And, Or, Not, Xor, Implies, to_cnf, satisfiable | 布尔逻辑 |
| `.assumptions` | Q, ask, refine, assuming | 假设系统 |
| `.polys` | Poly, factor, gcd, groebner, roots, GF/ZZ/QQ | 多项式系统 |
| `.series` | limit, series, Limit, Order/O, residue, fps | 级数展开 |
| `.functions` | sin/cos/exp/log/gamma/bessel/erf/Piecewise 等 | 数学函数库 |
| `.ntheory` | isprime, factorint, primepi, primitive_root | 数论 |
| `.concrete` | Sum/summation, Product/product | 求和与乘积 |
| `.discrete` | fft, ntt, convolution | 离散变换 |
| `.simplify` | simplify, trigsimp, powsimp, ratsimp, cse | 化简 |
| `.sets` | Set, Interval, Union, FiniteSet, Reals, Integers | 集合论 |
| `.solvers` | solve, dsolve, pdsolve, solveset, linsolve | 方程求解 |
| `.matrices` | Matrix, eye, zeros, det, trace, MatrixSymbol | 矩阵运算 |
| `.geometry` | Point, Line, Circle, Ellipse, Polygon | 几何 |
| `.utilities` | lambdify, flatten, numbered_symbols, sift | 工具函数 |
| `.integrals` | integrate, Integral, laplace_transform, mellin_transform | 积分与变换 |
| `.tensor` | Indexed, Idx, Array, tensorproduct, NDimArray | 张量运算 |
| `.parsing` | parse_expr | 表达式解析 |
| `.calculus` | singularities, stationary_points, euler_equations | 微积分工具 |
| `.algebras` | Quaternion | 代数结构 |
| `.printing` | pretty, latex, pprint, srepr, ccode, mathematica_code | 打印与代码生成 |
| `.plotting` | plot, textplot, plot_implicit, plot_parametric | 绘图 |
| `.interactive` | init_session, init_printing, interactive_traversal | 交互环境 |

### 未自动导入的子模块

以下子模块在顶层 `__init__.py` 中有注释说明但未自动导入：[^F-071]

- **`sympy.stats`**：概率统计模块（注释标记为导致与其他模块冲突），提供随机变量、概率分布（`Normal`、`Uniform`、`Exponential` 等）、密度函数、期望、方差等功能
- **`sympy.combinatorics`**：组合数学模块（注释标记增加约 0.04-0.05 秒导入时间），提供排列（`Permutation`）、置换群、子集、分区等组合对象
- **`sympy.physics`**：物理学模块（注释标记为导入缓慢），包含经典力学、量子力学、光学、单位系统（`sympy.physics.units`）、氢原子波函数等子包

这些模块需显式导入才能使用：

```python
from sympy.stats import Normal, density, E as E_stat, variance
from sympy.combinatorics import Permutation, PermutationGroup
from sympy.physics import units
from sympy.physics.units import meter, second
```

### 离散数学与数论

`sympy.ntheory` 子模块提供数论函数，`sympy.discrete` 提供离散变换：[^F-070]

- **数论函数**：`isprime`（素性检测）、`nextprime`/`prevprime`（相邻素数）、`factorint`（整数分解）、`primepi`（素数计数）、`primorial`（素数阶乘）、`totient`（欧拉函数）、`mobius`（莫比乌斯函数）、`primitive_root`（原根）、`sqrt_mod`（模平方根）、`discrete_log`（离散对数）
- **连分数**：`continued_fraction`、`continued_fraction_periodic`、`continued_fraction_convergents`
- **离散变换**：`fft`/`ifft`（快速傅里叶变换）、`ntt`/`intt`（数论变换）、`fwht`/`ifwht`（Walsh-Hadamard变换）、`convolution`（卷积）

### 多项式系统

`sympy.polys` 子模块是 SymPy 最庞大的子模块之一，导出超过100个符号：[^F-070]

- **多项式构造**：`Poly`、`PurePoly`、`poly`、`symmetric_poly`、`chebyshevt_poly`、`legendre_poly`
- **多项式运算**：`factor`、`gcd`、`lcm`、`resultant`、`discriminant`、`groebner`、`cancel`、`apart`、`together`
- **多项式根**：`roots`、`nroots`、`real_roots`、`rootof`/`RootOf`/`CRootOf`、`all_roots`、`count_roots`
- **域表示**：`ZZ`（整数环）、`QQ`（有理数域）、`RR`（实数域）、`CC`（复数域）、`GF`/`FF`（有限域）、`PolynomialRing`、`FractionField`

```python
>>> from sympy import Poly, symbols, factor, roots
>>> x = symbols('x')
>>> p = Poly(x**3 - 6*x**2 + 11*x - 6, x)
>>> factor(p)
(x - 3)*(x - 1)*(x - 2)
>>> roots(x**2 - 2, x)
{-sqrt(2): 1, sqrt(2): 1}
```

## `__all__` 导出清单结构

顶层 `__all__` 列表按子模块分组注释，包含约 400+ 个公开符号名，覆盖从 core 到 interactive 的所有导出。[^F-070] 文件末尾额外扩展了子模块名本身（如 `algebras`、`calculus`、`polys` 等），兼容 SymPy 1.6 之前 `from sympy import *` 隐式导入子模块的行为。[^F-071]

## core 子模块的导出结构

`core/__init__.py` 是顶层包的核心依赖，它的导出构成了顶层命名空间的基础层：[^F-066]

| 来源文件 | 导出符号类别 |
|---|---|
| `core/sympify.py` | `sympify`, `SympifyError` |
| `core/cache.py` | `cacheit` 装饰器 |
| `core/assumptions.py` | `assumptions`, `check_assumptions`, `failing_assumptions` 等 |
| `core/basic.py` | `Basic`, `Atom` |
| `core/singleton.py` | `S` |
| `core/expr.py` | `Expr`, `AtomicExpr`, `UnevaluatedExpr` |
| `core/symbol.py` | `Symbol`, `Wild`, `Dummy`, `symbols`, `var` |
| `core/numbers.py` | `Number`, `Float`, `Rational`, `Integer`, `NumberSymbol`, `RealNumber`, `igcd`, `ilcm`, `seterr`, `E`, `I`, `nan`, `oo`, `pi`, `zoo`, `AlgebraicNumber`, `comp`, `mod_inverse` |
| `core/power.py` | `Pow` |
| `core/intfunc.py` | `integer_nthroot`, `integer_log`, `num_digits`, `trailing` |
| `core/mul.py` | `Mul`, `prod` |
| `core/add.py` | `Add` |
| `core/mod.py` | `Mod` |
| `core/relational.py` | `Rel`, `Eq`, `Ne`, `Lt`, `Le`, `Gt`, `Ge` 等关系类 |
| `core/function.py` | `Lambda`, `WildFunction`, `Derivative`, `diff`, `FunctionClass`, `Function`, `Subs`, `expand` 及各 expand 变体 |
| `core/evalf.py` | `PrecisionExhausted`, `N` |
| `core/containers.py` | `Tuple`, `Dict` |
| `core/exprtools.py` | `gcd_terms`, `factor_terms`, `factor_nc` |
| `core/parameters.py` | `evaluate` 上下文管理器 |
| `core/kind.py` | `UndefinedKind`, `NumberKind`, `BooleanKind` |
| `core/traversal.py` | `preorder_traversal`, `bottom_up`, `use`, `postorder_traversal` |
| `core/sorting.py` | `default_sort_key`, `ordered` |

`Catalan`、`EulerGamma`、`GoldenRatio`、`TribonacciConstant` 四个常量在 `core/__init__.py` 中通过 `S.Catalan = ...` 方式显式暴露（第39-42行），而非直接从 numbers.py 导入。[^F-066]

## 打印与代码生成

`sympy.printing` 子模块导出多种格式的输出能力：[^F-070]

| 输出格式 | 函数/类 | 目标语言/格式 |
|---|---|---|
| ASCII 艺术 | `pretty`, `pprint` | 终端文本排版 |
| LaTeX | `latex`, `print_latex`, `multiline_latex` | LaTeX 数学公式 |
| MathML | `mathml`, `print_mathml` | MathML 标记 |
| Python | `python`, `print_python`, `pycode`, `srepr` | Python 代码/表示 |
| C 代码 | `ccode`, `print_ccode` | C 语言代码 |
| Fortran | `fcode`, `print_fcode` | Fortran 代码 |
| Julia | `julia_code` | Julia 语言代码 |
| JavaScript | `jscode`, `print_jscode` | JavaScript 代码 |
| Rust | `rust_code` | Rust 语言代码 |
| MATLAB/Octave | `octave_code` | MATLAB/Octave 代码 |
| Mathematica | `mathematica_code` | Mathematica 代码 |
| Maple | `maple_code`, `print_maple_code` | Maple 代码 |
| R | `rcode`, `print_rcode` | R 语言代码 |
| GLSL | `glsl_code`, `print_glsl` | GLSL 着色器代码 |
| SMT-LIB | `smtlib_code` | SMT 求解器格式 |
| 树结构 | `print_tree`, `dotprint` | 表达式树可视化 |

```python
>>> from sympy import latex, pretty, symbols, sin, exp
>>> x = symbols('x')
>>> latex(sin(x)**2)
'\\sin^{2}{\\left(x \\right)}'
>>> print(pretty(exp(x)))
 x
ℯ
```

## lambdify 与数值计算桥接

`lambdify` 函数从 `sympy.utilities` 导出（顶层可通过 `sympy.lambdify` 访问），将 SymPy 表达式编译为可调用的数值函数，支持 NumPy、SciPy、mpmath 等后端：[^F-070]

```python
>>> from sympy import lambdify, symbols, sin
>>> import numpy as np
>>> x = symbols('x')
>>> f = lambdify(x, sin(x), 'numpy')
>>> f(np.array([0, np.pi/2, np.pi]))
array([0.00000000e+00, 1.00000000e+00, 1.22464680e-16])
```

[^F-069]: facts.md F-069 — 顶层 __init__.py 环境检查与依赖要求
[^F-070]: facts.md F-070 — 顶层 __init__.py 子模块导入清单
[^F-071]: facts.md F-071 — 顶层 __init__.py 延迟加载与 evalf 表初始化
[^F-065]: facts.md F-065 — SingletonRegistry 与 S 单例对象
[^F-066]: facts.md F-066 — core/__init__.py 导出清单
[^F-062]: facts.md F-062 — Relational 类层次
[^F-058]: facts.md F-058 — EvalfMixin 数值求值
[^F-059]: facts.md F-059 — N() 函数
[^F-060]: facts.md F-060 — evalf 底层引擎
