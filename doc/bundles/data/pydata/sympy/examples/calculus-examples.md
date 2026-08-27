---
okf_version: "0.2"
type: example
title: 微积分实战
description: 从导数、积分、极限到泰勒级数、积分变换、微分方程的完整SymPy微积分操作指南，所有代码均可直接运行
tags: [sympy, calculus, derivative, integral, limit, series, diff, integrate]
generated: { by: reference_agent/trae-glm, at: 2026-04-22T11:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T11:30:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: core-init
    resource: /references/core-init.md
  - id: calculus-integrals-source
    resource: /references/calculus-integrals-source.md
  - id: series-solvers-source
    resource: /references/series-solvers-source.md
---

# 微积分实战

> 前置概念：[函数体系](../concepts/04-function-basics.md) | [微积分核心](../concepts/07-calculus.md) | [方程求解](../concepts/08-solvers.md)

本文档通过可运行代码演示 SymPy 的全部微积分能力：导数、积分、极限、级数展开、积分变换、函数分析和微分方程。每个代码块均可直接复制到 Python 环境运行。

```python
# 统一导入
from sympy import (symbols, Symbol, Function, Derivative, Integral, Limit,
                   diff, integrate, limit, series, N, oo, pi, E, I,
                   sin, cos, tan, exp, log, sqrt, Rational, S, Eq)
from sympy.abc import x, y, z, a, b, c, t, s  # 常用预定义符号
```

## 1. 导数计算

`diff()` 函数和 `.diff()` 方法是求导的主要入口。支持一阶导数、高阶导数、混合偏导数。`Derivative` 类表示未求值的导数，通过 `.doit()` 触发计算。

```python
from sympy import diff, Derivative, sin, cos, exp, log, symbols
from sympy.abc import x, y

# 一阶导数
diff(sin(x), x)                # -> cos(x)
diff(x**3, x)                  # -> 3*x**2
diff(exp(x)*sin(x), x)         # -> exp(x)*sin(x) + exp(x)*cos(x)
diff(log(x), x)                # -> 1/x
diff(sqrt(x), x)               # -> 1/(2*sqrt(x))

# 使用 .diff() 方法
sin(x).diff(x)                 # -> cos(x)
(x**3 + 2*x + 1).diff(x)       # -> 3*x**2 + 2

# 高阶导数：diff(f, x, n)
diff(x**4, x, 3)               # -> 24*x（三阶导数）
diff(sin(x), x, 4)             # -> sin(x)（四阶导回到自身）
diff(exp(x), x, 5)             # -> exp(x)（指数函数任意阶导数不变）

# 混合偏导数：diff(f, x1, n1, x2, n2, ...)
diff(x**2*y**3, x, 2, y, 1)   # -> 6*y**2（∂³/(∂x²∂y)）
diff(sin(x)*cos(y), x, y)      # -> -sin(y)*cos(x)（∂²/(∂x∂y)）
diff(exp(x*y), x, y)           # -> x*y*exp(x*y) + exp(x*y)

# 未求值导数（Derivative 类）
d = Derivative(sin(x), x)
d                              # -> Derivative(sin(x), x)
d.doit()                       # -> cos(x)

# evaluate=False 阻止自动求值
diff(sin(x), x, evaluate=False)  # -> Derivative(sin(x), x)
```

> 相关参考：[Derivative 与 diff()](../references/calculus-integrals-source.md)

## 2. 高阶导数与偏导数

对多元函数，SymPy 可以计算任意阶偏导数和方向导数。对未定义函数，自动应用链式法则。

```python
from sympy import diff, Derivative, Function, symbols
from sympy.abc import x, y, z

# 定义未定义函数
f = Function('f')
g = Function('g')

# 链式法则：对复合函数求导
f(g(x)).diff(x)
# -> Derivative(f(g(x)), g(x))*Derivative(g(x), x)

# 多变量函数的偏导
expr = x**2*y + y**2*z + z**2*x
diff(expr, x)                  # -> 2*x*y + z**2
diff(expr, y)                  # -> x**2 + 2*y*z
diff(expr, x, y)               # -> 2*x（混合偏导）
diff(expr, x, 2)               # -> 2*y（对 x 的二阶偏导）

# 拉普拉斯算子：∂²f/∂x² + ∂²f/∂y² + ∂²f/∂z²
fxyz = f(x, y, z)
laplacian = diff(fxyz, x, 2) + diff(fxyz, y, 2) + diff(fxyz, z, 2)
laplacian
# -> Derivative(f(x,y,z), (x,2)) + Derivative(f(x,y,z), (y,2)) + Derivative(f(x,y,z), (z,2))

# 对未定义函数求导（变分法场景）
Derivative(f(x)**2, f(x), evaluate=True)  # -> 2*f(x)

# 抽象函数的 n 阶导数
Derivative(f(x), (x, 3))       # -> Derivative(f(x), (x, 3))

# 多参数链式法则
f(x, y).diff(x)                # -> Derivative(f(x, y), x)
```

## 3. 不定积分

`integrate(f, x)` 计算不定积分 ∫f(x)dx。SymPy 内部按策略链依次尝试 manualintegrate（类人步骤）、meijerint（G函数）、heurisch（启发式Risch）、risch（Risch判定过程）、ratint（有理函数）等算法。

```python
from sympy import integrate, Integral, sin, cos, exp, log, sqrt, Rational
from sympy.abc import x, a, b, n

# 基本幂函数
integrate(x**2, x)             # -> x**3/3
integrate(x**n, x)             # -> Piecewise((x**(n+1)/(n+1), n≠-1), (log(x), True))
integrate(1/x, x)              # -> log(x)
integrate(x**Rational(3,2), x) # -> 2*x**(5/2)/5

# 三角函数
integrate(sin(x), x)           # -> -cos(x)
integrate(cos(x), x)           # -> sin(x)
integrate(sin(2*x), x)         # -> -cos(2*x)/2
integrate(sin(x)**2, x)        # -> x/2 - sin(x)*cos(x)/2

# 指数与对数
integrate(exp(x), x)           # -> exp(x)
integrate(exp(-x), x)          # -> -exp(-x)
integrate(log(x), x)           # -> x*log(x) - x
integrate(x*exp(x), x)         # -> (x - 1)*exp(x)

# 经典积分：分部积分
integrate(x*sin(x), x)         # -> -x*cos(x) + sin(x)
integrate(sin(x)*exp(x), x)    # -> exp(x)*sin(x)/2 - exp(x)*cos(x)/2

# 有理函数
integrate(1/(x**2 + 1), x)     # -> atan(x)
integrate(1/(x**2 - 1), x)     # -> log(x - 1)/2 - log(x + 1)/2

# 含参数积分
integrate(a*x + b, x)          # -> a*x**2/2 + b*x

# 未求值积分（Integral 类）
i = Integral(x**2, x)
i                              # -> Integral(x**2, x)
i.doit()                       # -> x**3/3

# 不可积情况：返回未求值 Integral
integrate(x**x, x)             # -> Integral(x**x, x)（无初等原函数）
```

> 相关参考：[积分算法策略链](../references/calculus-integrals-source.md)

## 4. 定积分

`integrate(f, (x, a, b))` 计算定积分 ∫[a,b] f(x)dx。支持反常积分（无穷限、含奇点）。

```python
from sympy import integrate, sin, cos, exp, log, sqrt, pi, oo, Rational, E
from sympy.abc import x, a, b

# 有限区间定积分
integrate(x**2, (x, 0, 1))     # -> 1/3
integrate(sin(x), (x, 0, pi))  # -> 2
integrate(x*exp(x), (x, 0, 1)) # -> 1
integrate(sqrt(1 - x**2), (x, -1, 1))  # -> pi/2（半圆面积）

# 反常积分：无穷限
integrate(exp(-x), (x, 0, oo))           # -> 1
integrate(1/(x**2 + 1), (x, -oo, oo))    # -> pi
integrate(exp(-x**2), (x, -oo, oo))      # -> sqrt(pi)（Gauss积分）
integrate(x*exp(-x), (x, 0, oo))         # -> 1

# 含三角函数的反常积分
integrate(sin(x)/x, (x, 0, oo))          # -> pi/2（Dirichlet积分）

# 带符号参数的定积分
integrate(exp(-a*x), (x, 0, oo))         # -> 1/a（当 Re(a) > 0）

# 经典定积分
integrate(log(x)/x, (x, 0, 1))           # -> -oo（发散）

# 分段结果（带收敛条件）
from sympy import Symbol
n = Symbol('n', positive=True)
integrate(x**n, (x, 0, 1))               # -> 1/(n+1)（Piecewise 结果）
```

## 5. 多元积分

`integrate(f, (x, xmin, xmax), (y, ymin, ymax))` 计算多重积分，变量顺序从外到内。

```python
from sympy import integrate, exp, pi, oo, Rational
from sympy.abc import x, y, a

# 二重积分：矩形区域
integrate(x*y, (x, 0, 1), (y, 0, 1))    # -> 1/4
integrate(x + y, (x, 0, 1), (y, 0, 1))  # -> 1

# 二重积分：三角形区域（先 y 后 x）
# ∫[0,1] ∫[0,x] (x+y) dy dx
integrate(x + y, (y, 0, x), (x, 0, 1))  # -> 1/2

# 三重积分：体积
integrate(1, (z, 0, 1-x-y), (y, 0, 1-x), (x, 0, 1))
# -> 1/6（四面体体积）

# 极坐标下的积分（圆面积）
from sympy.abc import r, theta
integrate(r, (r, 0, 1), (theta, 0, 2*pi))  # -> pi

# 含参数的二重积分
integrate(exp(-a*(x**2 + y**2)), (x, -oo, oo), (y, -oo, oo))
# -> pi/a（当 a > 0）
```

## 6. 极限计算

`limit(f, x, x0)` 计算函数极限，`dir` 参数控制方向（`+` 右极限、`-` 左极限、`+-` 双向）。底层使用 Gruntz 算法处理趋向无穷的极限。

```python
from sympy import limit, Limit, sin, cos, exp, log, oo, E, Symbol
from sympy.abc import x

# 经典极限
limit(sin(x)/x, x, 0)          # -> 1
limit((1 + 1/x)**x, x, oo)     # -> E（自然对数底）
limit((cos(x) - 1)/x**2, x, 0) # -> -1/2

# 多项式比的极限
limit((x**2 - 1)/(x - 1), x, 1)  # -> 2
limit((3*x**2 + 2*x + 1)/(x**2 + 1), x, oo)  # -> 3

# 对数/指数极限
limit(exp(-x), x, oo)          # -> 0
limit(log(x)/x, x, oo)         # -> 0
limit(x*log(x), x, 0, dir='+') # -> 0

# 单侧极限
limit(1/x, x, 0, dir='+')      # -> oo（右极限）
limit(1/x, x, 0, dir='-')      # -> -oo（左极限）
limit(1/x, x, 0, dir='+-')     # -> zoo（复无穷，双向极限不存在）

# 振荡极限
from sympy import AccumBounds
limit(sin(x), x, oo)           # -> AccumBounds(-1, 1)（振荡有界）

# 未求值极限
L = Limit(sin(x)/x, x, 0)
L                              # -> Limit(sin(x)/x, x, 0)
L.doit()                       # -> 1

# Expr.limit() 方法
sin(x).limit(x, 0)             # -> 0
```

> 相关参考：[limit() 与 Gruntz 算法](../references/calculus-integrals-source.md)

## 7. 泰勒级数展开

`series(f, x, x0, n)` 计算函数在点 `x0` 处的 n 阶泰勒展开。结果包含 `O(x**n)` 截断项，可用 `.removeO()` 移除。

```python
from sympy import series, sin, cos, exp, log, sqrt, O, Symbol
from sympy.abc import x

# 麦克劳林展开（在 x=0 处，默认 n=6）
series(sin(x), x, 0, 10)
# -> x - x**3/6 + x**5/120 - x**7/5040 + x**9/362880 + O(x**10)

series(cos(x), x, 0, 8)
# -> 1 - x**2/2 + x**4/24 - x**6/720 + O(x**8)

series(exp(x), x, 0, 6)
# -> 1 + x + x**2/2 + x**3/6 + x**4/24 + x**5/120 + O(x**6)

series(log(1 + x), x, 0, 5)
# -> x - x**2/2 + x**3/3 - x**4/4 + O(x**5)

series(1/(1 - x), x, 0, 6)
# -> 1 + x + x**2 + x**3 + x**4 + x**5 + O(x**6)（几何级数）

# 在非零点展开
series(1/(1 + x), x, 1, 4)
# -> 1/2 - (x - 1)/4 + (x - 1)**2/8 - (x - 1)**3/16 + O((x-1)**4, (x, 1))

# 移除 O 项，获得截断多项式
series(sin(x), x, 0, 6).removeO()
# -> x**5/120 - x**3/6 + x

# 洛朗级数（含负幂次）
series(1/sin(x), x, 0, 5)
# -> 1/x + x/6 + 7*x**3/360 + O(x**4)

# 使用 .series() 方法
sin(x).series(x, 0, 8)         # 等价于 series(sin(x), x, 0, 8)
```

> 相关参考：[series() 泰勒/洛朗级数](../references/series-solvers-source.md)

## 8. 积分变换

SymPy 提供 Laplace、Fourier、Mellin、Hankel、Sine、Cosine 等多种积分变换。变换函数默认返回三元组 `(结果, 收敛条件, 收敛横坐标)`，传 `noconds=True` 只返回结果。

```python
from sympy import (laplace_transform, inverse_laplace_transform,
                   fourier_transform, mellin_transform,
                   sine_transform, cosine_transform,
                   exp, sin, cos, DiracDelta, Heaviside, symbols)
from sympy.abc import t, s, x, k, a

# Laplace 变换：L{f(t)} = F(s) = ∫₀^∞ f(t)e^{-st}dt
laplace_transform(exp(-a*t), t, s, noconds=True)
# -> 1/(a + s)
laplace_transform(t**2, t, s, noconds=True)
# -> 2/s**3
laplace_transform(Heaviside(t), t, s, noconds=True)
# -> 1/s
laplace_transform(DiracDelta(t), t, s, noconds=True)
# -> 1
laplace_transform(sin(a*t), t, s, noconds=True)
# -> a/(a**2 + s**2)

# 逆 Laplace 变换
inverse_laplace_transform(1/(s + a), s, t)
# -> exp(-a*t)*Heaviside(t)
inverse_laplace_transform(1/s**2, s, t)
# -> t*Heaviside(t)

# Fourier 变换：F{f(x)} = F(k) = ∫ f(x)e^{-2πikx}dx
fourier_transform(exp(-x**2), x, k)
# -> sqrt(pi)*exp(-pi**2*k**2)

# Mellin 变换：M{f(x)} = F(s) = ∫₀^∞ f(x)x^{s-1}dx
mellin_transform(exp(-x), x, s)
# -> (gamma(s), (0, oo), True)

# Sine / Cosine 变换
sine_transform(x*exp(-a*x), x, k, noconds=True)
cosine_transform(exp(-a*x), x, k, noconds=True)
```

> 相关参考：[积分变换模块](../references/calculus-integrals-source.md)

## 9. 微积分工具

`sympy.calculus` 模块提供奇点分析、单调性判定、凸性判定、驻点与极值、周期性等函数分析工具。

```python
from sympy.calculus import (singularities, is_increasing, is_decreasing,
                             periodicity, stationary_points,
                             minimum, maximum, is_convex)
from sympy.calculus.util import continuous_domain
from sympy import sin, cos, exp, log, pi, oo, S, Interval, Symbol
from sympy.abc import x

# 奇点分析
singularities(1/(x**2 - 1), x)   # -> {-1, 1}
singularities(1/x + 1/(x-1), x)  # -> {0, 1}
singularities(tan(x), x)         # -> {pi/2 + n*pi | n ∈ ℤ}（周期奇点集）

# 单调性判定（默认在全体实数域 S.Reals 上）
is_increasing(x**3)             # -> True（全局递增）
is_increasing(exp(x))           # -> True
is_decreasing(-x)               # -> True（全局递减）

# 周期性
periodicity(sin(x), x)            # -> 2*pi
periodicity(exp(x), x)            # -> None（非周期）
periodicity(tan(x), x)            # -> pi

# 驻点（临界点）
stationary_points(x**3 - 3*x, x, S.Reals)  # -> {-1, 1}
stationary_points(x**2, x, S.Reals)        # -> {0}

# 极值
minimum(x**2, x, S.Reals)                 # -> 0
maximum(-x**2 + 4, x, S.Reals)            # -> 4

# 凸性判定
is_convex(x**2, x)                # -> True
is_convex(-x**2, x)               # -> False

# 连续域
continuous_domain(1/x, x, S.Reals)
# -> Union(Interval.open(-oo, 0), Interval.open(0, oo))
```

> 相关参考：[calculus 模块工具集](../references/calculus-integrals-source.md)

## 10. 微分方程

`dsolve()` 求解常微分方程（ODE），支持多种解法分类。`classify_ode()` 列出可用解法，`ics` 参数指定初值条件。

```python
from sympy import (dsolve, classify_ode, checkodesol, Function,
                   Derivative, Eq, sin, cos, exp, symbols, pprint)
x = Symbol('x')
f = Function('f')
y = f(x)

# 一阶 ODE：y' = y（指数增长/衰减）
eq1 = Derivative(y, x) - y
dsolve(eq1, y)
# -> Eq(f(x), C1*exp(x))

# 一阶 ODE 带初值条件：y' = y, y(0) = 1
sol1 = dsolve(eq1, y, ics={f(0): 1})
sol1                            # -> Eq(f(x), exp(x))

# 二阶常系数齐次 ODE：y'' + y = 0（简谐振动）
eq2 = Derivative(y, x, 2) + y
dsolve(eq2, y)
# -> Eq(f(x), C1*sin(x) + C2*cos(x))

# 二阶 ODE 带初值条件：y'' + y = 0, y(0)=1, y'(0)=0
sol2 = dsolve(eq2, y, ics={f(0): 1, f(x).diff(x).subs(x, 0): 0})
sol2                            # -> Eq(f(x), cos(x))

# 一阶线性 ODE：y' + y = x
eq3 = Derivative(y, x) + y - x
dsolve(eq3, y)
# -> Eq(f(x), C1*exp(-x) + x - 1)

# 可分离变量 ODE：y' = -x/y
eq4 = Derivative(y, x) + x/y
dsolve(eq4, y)
# -> [Eq(f(x), -sqrt(C1 - x**2)), Eq(f(x), sqrt(C1 - x**2))]

# 分类 ODE 可用解法
classify_ode(eq1, y)
# -> ('separable', '1st_exact', '1st_linear', 'Bernoulli', ...)

# 验证解是否正确
sol = dsolve(eq1, y)
checkodesol(eq1, sol)           # -> (True, 0)（验证通过，残差为0）

# 一阶 ODE：y' = 2*x*y（可分离）
eq5 = Derivative(y, x) - 2*x*y
dsolve(eq5, y)
# -> Eq(f(x), C1*exp(x**2))
```

> 相关参考：[dsolve 与 ODE 分类](../references/series-solvers-source.md)

---

**小结**：SymPy 的微积分覆盖了从求导（`diff`/`Derivative`）、积分（`integrate`/`Integral`）、极限（`limit`/`Limit`）、级数（`series`）到积分变换（`laplace_transform`/`fourier_transform`）、函数分析（`singularities`/`stationary_points`）和微分方程（`dsolve`）的完整工具链。关键模式是：未求值类（`Derivative`/`Integral`/`Limit`）+ `.doit()` 触发计算，顶层函数（`diff`/`integrate`/`limit`）直接求值。继续学习 [方程求解与矩阵实战](solving-equations.md) 掌握更多代数工具。
