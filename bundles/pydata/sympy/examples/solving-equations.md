---
okf_version: "0.2"
type: example
title: 方程求解与矩阵实战
description: 从代数方程求解到线性代数矩阵运算的完整SymPy指南，覆盖solve/solveset/linsolve/nonlinsolve/nsolve与Matrix操作、特征值、分解、多项式
tags: [sympy, solve, equation, matrix, linear-algebra, system]
generated: { by: reference_agent/trae-glm, at: 2026-04-22T11:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T11:30:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: core-init
    resource: /references/core-init.md
  - id: series-solvers-source
    resource: /references/series-solvers-source.md
  - id: matrices-source
    resource: /references/matrices-source.md
  - id: polys-algebra-source
    resource: /references/polys-algebra-source.md
---

# 方程求解与矩阵实战

> 前置概念：[方程求解](../concepts/08-solvers.md) | [矩阵系统](../concepts/09-matrices.md) | [多项式系统](../concepts/10-polynomials.md)

本文档通过可运行代码演示 SymPy 的方程求解能力（代数方程、线性/非线性方程组、数值求解）和线性代数能力（矩阵创建、运算、特征值、分解），最后以综合实战收尾。

```python
# 统一导入
from sympy import (symbols, Symbol, solve, solveset, linsolve, nonlinsolve,
                   nsolve, Eq, Matrix, eye, zeros, ones, diag, Poly, factor,
                   gcd, groebner, roots, S, Interval, oo, pi, I, Rational,
                   sqrt, exp, sin, cos, Function, Derivative, dsolve)
from sympy.abc import x, y, z, a, b, c, d  # 常用符号
```

## 1. 代数方程求解

`solve(f, symbol)` 是最常用的方程求解函数，求解 `f(x) = 0`。支持 `dict=True` 返回字典列表、`set=True` 返回解集。`Eq(lhs, rhs)` 创建显式等式。

```python
from sympy import solve, Eq, symbols, sqrt, I, sin, exp
from sympy.abc import x, y, a, b, c

# 一元二次方程：x² - 4 = 0
solve(x**2 - 4, x)             # -> [-2, 2]

# 使用 Eq 创建显式等式
solve(Eq(x**2, 4), x)          # -> [-2, 2]

# 一元二次方程通解：ax² + bx + c = 0
solve(a*x**2 + b*x + c, x)
# -> [(-b + sqrt(-4*a*c + b**2))/(2*a), -(b + sqrt(-4*a*c + b**2))/(2*a)]

# 高次多项式：x³ - 6x² + 11x - 6 = 0
solve(x**3 - 6*x**2 + 11*x - 6, x)
# -> [1, 2, 3]

# 复数解
solve(x**2 + 1, x)             # -> [-I, I]

# 三角方程（返回主值范围内的解）
solve(sin(x) - 1, x)           # -> [pi/2]

# dict=True：返回字典列表（便于后续替换）
solve(x**2 - 4, x, dict=True)  # -> [{x: -2}, {x: 2}]

# set=True：返回变量和解集的元组
solve([x + y - 3, x - y - 1], [x, y], set=True)
# -> ([x, y], {(2, 1)})

# 多变量方程组
solve([x + y - 3, x - y - 1], [x, y])
# -> {x: 2, y: 1}

# 三个方程三个变量
solve([x + y + z - 1, x - y + z - 2, x + y - z - 3], [x, y, z])
# -> {x: 5/2, y: -1/2, z: -1}

# 含参数的方程
solve(a*x + b, x)              # -> [-b/a]

# 根式方程（自动验证排除增根）
solve(sqrt(x + 2) - x, x)      # -> [2]（增根 -1 被自动排除）
```

> 相关参考：[solve() 函数签名与用法](/references/series-solvers-source.md)

## 2. solveset 集合求解

`solveset(f, symbol, domain)` 以集合形式返回解，是 `solve()` 的现代替代品。支持指定求解域（实数域、复数域、整数域等），原生支持不等式。

```python
from sympy import solveset, S, Interval, ConditionSet, sin, pi, oo, symbols
from sympy.abc import x

# 多项式方程（复数域默认）
solveset(x**2 - 4, x)          # -> {-2, 2}（FiniteSet）

# 指定实数域
solveset(x**2 + 1, x, S.Reals) # -> EmptySet（实数域无解）
solveset(x**2 - 4, x, S.Reals) # -> {-2, 2}

# 三角方程（返回全部周期解）
solveset(sin(x), x, S.Reals)
# -> Union(ImageSet(Lambda(_n, 2*_n*pi), Integers),
#          ImageSet(Lambda(_n, 2*_n*pi + pi), Integers))
# 即 {nπ | n∈ℤ} ∪ {(2n+1)π | n∈ℤ} = {nπ | n∈ℤ}

# 不等式
solveset(x**2 - 4 < 0, x, S.Reals)
# -> Interval.open(-2, 2)
solveset(x**2 > 4, x, S.Reals)
# -> Union(Interval.open(-oo, -2), Interval.open(2, oo))

# 无解/恒成立
solveset(x - x, x)              # -> Complexes（恒成立）
solveset(x - x - 1, x)          # -> EmptySet（矛盾方程）

# 整数域求解
solveset(x**2 - 4, x, S.Integers)  # -> {-2, 2}

# 指数方程
solveset(exp(x) - 1, x, S.Complexes)
# -> ImageSet(Lambda(_n, 2*_n*I*pi), Integers)
```

> 相关参考：[solveset() 集合化求解](/references/series-solvers-source.md)

## 3. 线性方程组

`linsolve()` 专门求解线性方程组，支持三种输入形式：方程列表、增广矩阵、AX=b 矩阵形式。`Matrix.solve()` 方法直接求解 Ax=b。

```python
from sympy import linsolve, linear_eq_to_matrix, Matrix, symbols
from sympy.abc import x, y, z

# 方程列表形式
linsolve([x + y + z - 1, x + y + 2*z - 3], (x, y, z))
# -> {(-y - 1, y, 2)}（z=2, x=-y-1, y自由变量）

# 三个方程唯一解
linsolve([x + y + z - 6, 2*x + y - z - 1, x - y + 2*z - 5], (x, y, z))
# -> {(1, 2, 3)}

# 增广矩阵形式
M = Matrix([[1, 2, 3, 1],
            [4, 5, 6, 2],
            [7, 8, 10, 3]])
linsolve(M, x, y, z)
# -> {(0, -1, 1)}

# AX=b 矩阵形式
A = Matrix([[1, 1], [1, -1]])
b_vec = Matrix([3, 1])
linsolve((A, b_vec), x, y)
# -> {(2, 1)}

# 使用 Matrix.solve() 方法
A = Matrix([[1, 2], [3, 4]])
b = Matrix([5, 11])
A.solve(b)
# -> Matrix([[1], [2]])（即 x=1, y=2）

# LU 分解求解
A.LUsolve(b)                   # 等价于 A.solve(b)

# linear_eq_to_matrix：将方程列表转为矩阵
eqs = [x + y - 3, x - y - 1]
A_mat, b_mat = linear_eq_to_matrix(eqs, [x, y])
# A_mat -> Matrix([[1, 1], [1, -1]]), b_mat -> Matrix([3, 1])
```

> 相关参考：[linsolve() 线性方程组](/references/series-solvers-source.md)

## 4. 非线性方程组

`nonlinsolve()` 求解非线性方程组，使用代入消元和 Gröbner 基等方法。

```python
from sympy import nonlinsolve, symbols, sqrt, exp
from sympy.abc import x, y

# 圆与直线相交：x²+y²=1, x-y=0
nonlinsolve([x**2 + y**2 - 1, x - y], [x, y])
# -> {(-sqrt(2)/2, -sqrt(2)/2), (sqrt(2)/2, sqrt(2)/2)}

# 代数系统
nonlinsolve([x*y - 1, x - 2], [x, y])
# -> {(2, 1/2)}

# 抛物线与直线：y=x², y=x+2
nonlinsolve([y - x**2, y - x - 2], [x, y])
# -> {(-1, 1), (2, 4)}

# 含超越函数
nonlinsolve([exp(x) - y, x - 1], [x, y])
# -> {(1, E)}
```

## 5. 数值求解

`nsolve(f, x0)` 使用数值方法（牛顿法、二分法）求方程的数值根。`x0` 可以是初始猜测值或搜索区间 `(a, b)`。

```python
from sympy import nsolve, cos, sin, exp, pi, Matrix, symbols
from sympy.abc import x, y

# 单初始猜测值（牛顿法）
nsolve(cos(x) - x, x, 1)       # -> 0.739085133215161（Dottie 数）

# 区间搜索（二分法）
nsolve(sin(x), x, (3, 4))      # -> 3.14159265358979（π）

# 多项式的数值根
nsolve(x**3 - 2*x - 5, x, 2)   # -> 2.09455148154233

# 多初始值找多个根
nsolve(x**3 - 1, x, -0.5 - 0.5j)  # 复数初始猜测，找复根

# 方程组数值解
sol = nsolve((x**2 + y**2 - 1, x - y), (x, y), (1, 1))
# -> Matrix([[0.707106781186548], [0.707106781186548]])
sol[0]                         # -> 0.707106781186548
sol[1]                         # -> 0.707106781186548

# 指定精度
nsolve(cos(x) - x, x, 1, prec=30)  # 30位精度
```

## 6. 矩阵基础

`Matrix`（别名 `MutableDenseMatrix`）是 SymPy 最常用的矩阵类。支持算术运算、行列式、逆、转置、行最简形、秩、迹等操作。

```python
from sympy import Matrix, eye, zeros, ones, diag, symbols, Rational
from sympy.abc import x, y

# 创建矩阵
M = Matrix([[1, 2], [3, 4]])
M                              # -> Matrix([[1, 2], [3, 4]])

# 平面列表 + 形状
Matrix(2, 3, [1, 2, 3, 4, 5, 6])
# -> Matrix([[1, 2, 3], [4, 5, 6]])

# 符号矩阵
Matrix([[x, y], [y, x]])
# -> Matrix([[x, y], [y, x]])

# 工厂函数
eye(3)                         # 3×3 单位矩阵
zeros(2, 3)                    # 2×3 零矩阵
ones(2, 2)                     # 2×2 全一矩阵
diag(1, 2, 3)                  # 对角矩阵 diag(1,2,3)

# 基本属性
M = Matrix([[1, 2, 3], [4, 5, 6]])
M.shape                        # -> (2, 3)
M.rows                         # -> 2
M.cols                         # -> 3

# 转置
M = Matrix([[1, 2], [3, 4]])
M.T                            # -> Matrix([[1, 3], [2, 4]])

# 矩阵算术
A = Matrix([[1, 2], [3, 4]])
B = Matrix([[5, 6], [7, 8]])
A + B                          # -> Matrix([[6, 8], [10, 12]])
A * B                          # 矩阵乘法 -> Matrix([[19, 22], [43, 50]])
A * 2                          # 标量乘法 -> Matrix([[2, 4], [6, 8]])
A ** 2                         # 矩阵幂 -> Matrix([[7, 10], [15, 22]])

# 行列式
A.det()                        # -> -2

# 逆矩阵
A.inv()
# -> Matrix([[-2, 1], [3/2, -1/2]])

# 行最简形（RREF）
M = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 10]])
M.rref()
# -> (Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]]), (0, 1, 2))

# 秩
M.rank()                       # -> 3

# 迹（对角线之和）
A.trace()                      # -> 5（1 + 4）

# 共轭转置（Hermite 转置）
from sympy import I
C = Matrix([[1, 2 + I], [3, 4]])
C.H                            # 共轭转置
```

> 相关参考：[Matrix 类与基本运算](/references/matrices-source.md)

## 7. 特征值与对角化

SymPy 矩阵提供完整的特征值/特征向量计算和对角化功能。

```python
from sympy import Matrix, symbols
from sympy.abc import x

# 特征值（返回 {特征值: 代数重数} 字典）
M = Matrix([[1, 0], [0, 2]])
M.eigenvals()                  # -> {1: 1, 2: 1}

# 特征向量（返回 [(特征值, 重数, [特征向量列表])]）
M.eigenvects()
# -> [(1, 1, [Matrix([[1], [0]])]), (2, 1, [Matrix([[0], [1]])])]

# 对角化：返回 (P, D) 使得 A = P*D*P^{-1}
P, D = M.diagonalize()
P                              # -> Matrix([[1, 0], [0, 1]])
D                              # -> Matrix([[1, 0], [0, 2]])
P * D * P.inv() == M           # -> True

# 非对角矩阵的特征值
A = Matrix([[2, 1], [1, 2]])
A.eigenvals()                  # -> {3: 1, 1: 1}
P2, D2 = A.diagonalize()
D2                             # -> Matrix([[1, 0], [0, 3]])

# 特征多项式
M = Matrix([[1, 2], [3, 4]])
lamda = symbols('lamda')
char_poly = M.charpoly(lamda)
char_poly                      # -> PurePoly(lamda**2 - 5*lamda - 2, lamda, domain='ZZ')
char_poly.as_expr()            # -> lamda**2 - 5*lamda - 2

# 验证 Cayley-Hamilton 定理
M2 = Matrix([[1, 2], [3, 4]])
cp = M2.charpoly()
cp.as_expr().subs(x, M2)       # 将矩阵代入特征多项式 -> 零矩阵
```

> 相关参考：[特征值与对角化 API](/references/matrices-source.md)

## 8. 矩阵分解

SymPy 支持 LU、QR、Cholesky、LDL 等矩阵分解，以及奇异值计算。

```python
from sympy import Matrix, Rational, symbols

# LU 分解：A = L*U（带行置换）
A = Matrix([[4, 3], [6, 3]])
L, U, perm = A.LUdecomposition()
L                              # 下三角矩阵
# -> Matrix([[1, 0], [3/2, 1]])
U                              # 上三角矩阵
# -> Matrix([[4, 3], [0, -3/2]])
L * U                          # -> Matrix([[4, 3], [6, 3]])（验证）

# QR 分解：A = Q*R（Q 正交，R 上三角）
Q, R = A.QRdecomposition()
Q                              # 正交矩阵
R                              # 上三角矩阵
Q * R                          # == A

# Cholesky 分解：A = L*L.H（对称正定矩阵）
S = Matrix([[4, 2], [2, 3]])
L_chol = S.cholesky()
L_chol                         # 下三角矩阵
L_chol * L_chol.T              # == S（验证）

# LDL 分解：A = L*D*L.H
L_ldl, D_ldl = S.LDLdecomposition()
L_ldl * D_ldl * L_ldl.T        # == S

# 奇异值（SVD 组件）
M = Matrix([[1, 0], [0, 1], [1, 1]])
M.singular_values()
```

## 9. 多项式操作

`Poly` 类提供显式生成元和系数域的多项式表示，支持因式分解、GCD、Gröbner 基等高级操作。

```python
from sympy import Poly, factor, expand, gcd, groebner, roots, symbols
from sympy.abc import x, y

# 创建 Poly 对象
p = Poly(x**2 + 2*x + 1, x)
p                              # -> Poly(x**2 + 2*x + 1, x, domain='ZZ')
p.gens                         # -> (x,)
p.domain                       # -> ZZ（整数环）
p.degree()                     # -> 2
p.coeffs()                     # -> [1, 2, 1]
p.LC()                         # -> 1（首项系数）
p.as_expr()                    # -> x**2 + 2*x + 1（转回 Expr）

# 因式分解
factor(x**2 - 1)               # -> (x - 1)*(x + 1)
factor(x**3 - 6*x**2 + 11*x - 6)  # -> (x - 3)*(x - 1)*(x - 2)
factor(x**2 + 2*x + 1)         # -> (x + 1)**2

# expand 与 factor 互为逆运算
expand((x + y)**3)              # -> x**3 + 3*x**2*y + 3*x*y**2 + y**3

# GCD（最大公因式）
from sympy import lcm
f = Poly(x**2 - 1, x)
g = Poly(x**2 - 2*x + 1, x)
gcd(f, g)                      # -> Poly(x - 1, x, domain='ZZ')
gcd(x**2 - 1, x**2 - 2*x + 1)  # -> x - 1（直接对 Expr 操作）
lcm(x**2 - 1, x**2 - 2*x + 1)  # -> (x - 1)*(x + 1)**2 或等价形式

# Gröbner 基（多变量多项式理想）
G = groebner([x**2 + y - 1, x*y - x], x, y, order='lex')
G                              # -> GroebnerBasis([...], x, y, ...)

# 多项式求根（返回 {根: 重数}）
roots(x**2 - 4, x)             # -> {-2: 1, 2: 1}
roots(x**3 - 1, x)             # -> {1: 1, -1/2 - sqrt(3)*I/2: 1, -1/2 + sqrt(3)*I/2: 1}
roots((x-1)*(x-2)**2*(x-3), x) # -> {1: 1, 2: 2, 3: 1}

# 有理函数运算
from sympy import cancel, together, apart
cancel((x**2 - 1)/(x - 1))    # -> x + 1
together(1/x + 1/(x+1))       # -> (2*x + 1)/(x*(x + 1))
apart(1/(x**2 + 2*x - 3))     # -> 1/(4*(x - 1)) - 1/(4*(x + 3))
```

> 相关参考：[Poly 类与多项式运算](/references/polys-algebra-source.md)

## 10. 综合实战：弹簧-质点系统

> 概念参考：[方程求解](../concepts/08-solvers.md) | [矩阵系统](../concepts/09-matrices.md)

以经典物理问题演示方程求解与矩阵运算的综合运用：求解弹簧-质点系统的平衡位置和特征频率。

```python
from sympy import (symbols, Matrix, solve, linsolve, dsolve, Function,
                   Derivative, Eq, sqrt, Rational, pi, pprint, init_printing)
init_printing()

# === 问题1：静力平衡（线性方程组） ===
# 两个质点 m1,m2 由三根弹簧连接（两端固定），在力 F1,F2 作用下平衡
# 位移 u1,u2 满足 K*u = F，K 为刚度矩阵
k1, k2, k3, F1, F2 = symbols('k1 k2 k3 F1 F2', positive=True)
u1, u2 = symbols('u1 u2')

# 刚度矩阵（两质点弹簧链：左墙-k1-m1-k2-m2-k3-右墙）
K = Matrix([
    [k1 + k2, -k2],
    [-k2, k2 + k3]
])
F = Matrix([F1, F2])
u = Matrix([u1, u2])

# 求解 K*u = F（平衡位移）
# 数值验证：k1=k2=k3=1, F1=1, F2=0
K_num = K.subs({k1:1, k2:1, k3:1})
F_num = F.subs({F1:1, F2:0})
u_sol = K_num.LUsolve(F_num)
u_sol                          # -> Matrix([[2/3], [1/3]])
# 解释：左端施加单位力，m1 位移 2/3，m2 位移 1/3

# === 问题2：特征频率（特征值问题） ===
# 自由振动：M*ü + K*u = 0，设 u = v*e^{iωt}
# 得广义特征值问题 K*v = ω²*M*v
m1, m2 = symbols('m1 m2', positive=True)
M_mat = Matrix([[m1, 0], [0, m2]])

# 等质量等刚度简化：m1=m2=m, k1=k2=k3=k
m, k = symbols('m k', positive=True)
K_simple = Matrix([[2*k, -k], [-k, 2*k]])
M_simple = m * eye(2)

# 广义特征值问题：det(K - ω²M) = 0
omega = symbols('omega')
char_eq = (K_simple - omega**2 * M_simple).det()
char_eq                        # -> 3*k**2 - 4*k*m*omega**2 + m**2*omega**4
freqs_sq = solve(char_eq, omega**2)
freqs_sq                       # -> [k/m, 3*k/m]
# 自然频率：ω₁ = √(k/m)（同相振动），ω₂ = √(3k/m)（反相振动）

# 对应的特征向量
P, D = K_simple.diagonalize()
P                              # 特征向量矩阵
# D = diag(k/m, 3k/m)（对角化后特征值）

# === 问题3：单质点弹簧阻尼振动（微分方程） ===
t_val = symbols('t')
omega0, zeta = symbols('omega0 zeta', positive=True)
x_func = Function('x')
# 方程：x'' + 2ζω₀x' + ω₀²x = 0（阻尼自由振动）
eq_ode = Derivative(x_func(t_val), t_val, 2) + 2*zeta*omega0*Derivative(x_func(t_val), t_val) + omega0**2*x_func(t_val)
sol_ode = dsolve(eq_ode, x_func(t_val))
sol_ode  # 通解，含 C1, C2 常数（形式取决于阻尼比 ζ）

# 带初值条件：x(0)=1, x'(0)=0（初始位移1，无初速度）
sol_ic = dsolve(eq_ode, x_func(t_val),
               ics={x_func(0): 1, x_func(t_val).diff(t_val).subs(t_val, 0): 0})
# 返回在给定初值条件下的特解（欠阻尼 ζ<1 时为振荡衰减）
```

---

**小结**：本文档覆盖了 SymPy 方程求解和线性代数的核心能力。方程求解从 `solve()`（返回列表/字典）到 `solveset()`（返回集合对象），线性方程组用 `linsolve()`/`Matrix.solve()`，非线性用 `nonlinsolve()`，数值求解用 `nsolve()`。矩阵方面掌握了创建（`Matrix`/`eye`/`zeros`/`diag`）、基本运算（`+`/`*`/`**`/`.T`/`.det()`/`.inv()`/`.rref()`/`.rank()`/`.trace()`）、特征值（`.eigenvals()`/`.eigenvects()`/`.diagonalize()`）、分解（`LUdecomposition`/`QRdecomposition`/`cholesky`）和多项式（`Poly`/`factor`/`gcd`/`groebner`）。结合 [基础符号操作](./basic-symbols.md) 和 [微积分实战](./calculus-examples.md)，你已具备 SymPy 的核心使用能力。
