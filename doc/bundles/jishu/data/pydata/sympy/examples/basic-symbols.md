---
okf_version: "0.2"
type: example
title: 基础符号操作实战
description: 从安装导入开始，练习符号创建、表达式构建、替换、求值、化简等核心操作，所有代码均可直接运行
tags: [sympy, symbol, expression, subs, evalf, simplify, basic]
generated: { by: reference_agent/trae-glm, at: 2026-04-22T11:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T11:30:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: core-init
    resource: /references/core-init.md
  - id: basic-source
    resource: /references/basic-source.md
  - id: numbers-symbols-source
    resource: /references/numbers-symbols-source.md
---

# 基础符号操作实战

> 前置概念：[符号系统与数字类型](../concepts/02-symbols-numbers.md) | [表达式树模型](../concepts/01-expression-tree.md) | [类型转换机制](../concepts/03-sympify-basics.md)

本文档带你从零开始掌握 SymPy 的核心操作：符号创建、表达式构建、结构查看、替换、数值求值、类型转换与基本化简。每个代码块均可直接复制运行。

## 1. 安装与导入

SymPy 是纯 Python 包，通过 pip 安装后即可使用。`from sympy import *` 是交互式环境中最常见的导入方式，它将常用符号和函数注入当前命名空间。

```python
# 安装 SymPy（首次使用时执行）
# pip install sympy

# 基本导入方式
import sympy                    # 推荐用于脚本：sympy.sin(x)
from sympy import symbols, sin, cos, exp, pi, E, I, oo, S  # 显式导入
from sympy import *             # 交互式环境常用：一次性导入所有公开符号

# 验证版本
import sympy
print(sympy.__version__)       # -> 1.x.x（取决于安装版本）

# 初始化美观打印（Jupyter/IPython 中自动启用 LaTeX 渲染）
from sympy import init_printing
init_printing()                # 终端中使用 Unicode 字符打印
```

## 2. 定义符号

`symbols()` 是创建符号变量的核心函数，支持逗号、空格分隔，支持下标序列生成，还可附加数学假设（positive、real、integer 等）。

```python
from sympy import symbols, Symbol, var

# 单个符号
x = symbols('x')
x                              # -> x
type(x)                        # -> <class 'sympy.core.symbol.Symbol'>

# 批量创建（空格或逗号分隔均可）
x, y, z = symbols('x y z')
a, b, c = symbols('a, b, c')

# 带下标的序列符号：symbols('x0:n') 生成 x0, x1, ..., x(n-1)
x0, x1, x2, x3, x4 = symbols('x0:5')
x0, x1, x2                     # -> (x0, x1, x2)

# 带下划线的序列
a0_to_a2 = symbols('a:3')      # -> (a0, a1, a2)

# var() 函数：直接将符号注入当前命名空间（交互式便利）
from sympy import var
var('p q r')                   # -> (p, q, r)，且 p/q/r 自动可用
p + q + r                      # -> p + q + r

# 带数学假设的符号（影响化简行为）
t = symbols('t', positive=True)
n = symbols('n', integer=True)
u = symbols('u', real=True)
v = symbols('v', even=True)

t.is_positive                  # -> True
n.is_integer                   # -> True
u.is_real                      # -> True

# 同名但假设不同的符号互不相等
x_real = Symbol('x', real=True)
x_pos = Symbol('x', positive=True)
x_real == x_pos                # -> False
```

> 相关参考：[symbols() 与 var() 函数](../references/numbers-symbols-source.md) | [假设系统](../concepts/05-assumptions.md)

## 3. 预定义符号与常量

SymPy 提供了两组预定义符号来源：`sympy.abc` 模块预定义了所有拉丁/希腊字母；`S` 单例注册表和顶层常量提供数学常数。

```python
from sympy import S, pi, E, I, oo, nan, zoo
from sympy.abc import a, b, c, d, x, y, z  # 拉丁字母
from sympy.abc import alpha, beta, gamma, delta, theta, phi, omega  # 希腊字母

# S 单例：精确数值构造器与常量注册表
S.Zero                         # -> 0（Integer 单例）
S.One                          # -> 1
S.Half                         # -> 1/2
S.Pi is pi                     # -> True（pi 就是 S.Pi 的快捷名）
S.Exp1 is E                    # -> True
S.ImaginaryUnit is I           # -> True
S.Infinity is oo               # -> True

# 使用 S() 快捷构造精确有理数
S(1)/3                         # -> 1/3（精确 Rational，非 float 0.333...）
1/3                            # -> 0.3333333333333333（Python float，有精度损失）

# 数学常数
pi.evalf(10)                   # -> 3.141592654
E.evalf(10)                    # -> 2.718281828
I**2                           # -> -1（虚数单位）
oo + 1                         # -> oo（正无穷）
-oo                            # -> -oo
zoo                            # -> zoo（复无穷）

# 注意 abc 中的符号无假设属性
from sympy.abc import x as abc_x
abc_x.is_real is None          # -> True（无假设，不确定是否为实数）
```

> 相关参考：[S 单例注册表](../references/core-init.md) | [abc 预定义符号](../references/numbers-symbols-source.md)

## 4. 构建表达式

有了符号后，使用 Python 运算符即可构建 SymPy 表达式。SymPy 重载了算术运算符，返回不可变的表达式树节点。

```python
from sympy import symbols, sin, cos, exp, log, sqrt, tan
x, y = symbols('x y')

# 多项式
poly = x**2 + 2*x + 1
poly                           # -> x**2 + 2*x + 1

# 三角函数
trig_expr = sin(x)/cos(x)      # -> sin(x)/cos(x)
trig_expr                      # SymPy 不会自动化简为 tan(x)

# 指数与对数
exp_expr = exp(x)*sin(x)
exp_expr                       # -> exp(x)*sin(x)

log_expr = log(x**2)           # -> log(x**2)

# 根式
sqrt_expr = sqrt(x**2 + 1)     # -> sqrt(x**2 + 1)

# 复合表达式
compound = exp(-x**2) * cos(2*x) + log(x+1)/(x+1)
compound                       # -> exp(-x**2)*cos(2*x) + log(x + 1)/(x + 1)

# 多变量表达式
mv = x**2 + x*y + y**2
mv                             # -> x**2 + x*y + y**2

# 使用 S() 避免 float 精度问题
exact = x + S(1)/2             # -> x + 1/2（精确）
inexact = x + 1/2              # -> x + 0.5（引入 float）
```

## 5. 查看表达式结构

SymPy 表达式是不可变树结构，通过 `.args` 可访问子节点，`.func` 可访问构造类，`.free_symbols` 可获取自由符号集合。`srepr()` 输出精确的字符串表示，便于调试。

```python
from sympy import symbols, sin, srepr
x, y = symbols('x y')
expr = sin(x) + 1

# func 与 args：重构恒等式 expr == expr.func(*expr.args)
expr.func                      # -> <class 'sympy.core.add.Add'>
expr.args                      # -> (1, sin(x))
expr.func(*expr.args) == expr  # -> True

# 子表达式的结构
sin(x).func                    # -> sin
sin(x).args                    # -> (x,)

# 自由符号
expr = x**2 + y + 1
expr.free_symbols              # -> {x, y}

# 查看所有原子节点（叶子节点）
expr = x + sin(y)
expr.atoms()                   # -> {1, x, y}（数字和符号）
expr.atoms(sin)                # -> {sin(y)}（指定类型的原子）

# srepr：精确字符串表示（适合调试）
srepr(x + 1)                   # -> "Add(Symbol('x'), Integer(1))"
srepr(sin(x))                  # -> "sin(Symbol('x'))"

# 前序遍历表达式树
from sympy.core.traversal import preorder_traversal
expr = x + sin(y)
[node for node in preorder_traversal(expr)]
# -> [x + sin(y), x, sin(y), y]
```

> 相关参考：[Basic/Expr 核心类体系](../references/basic-source.md)

## 6. 替换操作

`.subs()` 方法将表达式中的符号替换为值或其他表达式；`.xreplace()` 执行精确节点匹配替换，不做模式匹配。

```python
from sympy import symbols, sin, cos, exp, pi
x, y, z = symbols('x y z')
expr = x**2 + 2*x + 1

# 单替换：subs(old, new)
expr.subs(x, 2)                # -> 9（2^2 + 4 + 1）
sin(x).subs(x, pi)             # -> 0

# 字典批量替换
expr = x + y
expr.subs({x: pi, y: 2})       # -> 2 + pi

# 列表按序替换（注意顺序替换的陷阱）
expr = x + y
expr.subs([(x, y), (y, x)])    # -> 2*x（先 x→y，再 y→x，顺序依赖）
expr.subs({x: y, y: x}, simultaneous=True)  # -> x + y（同时替换）

# 替换为表达式
expr = sin(x) + x
expr.subs(x, y**2)             # -> y**2 + sin(y**2)

# xreplace：精确节点匹配，不做数学推理
(1 + x*y).xreplace({x: y})     # -> y**2 + 1（x 精确匹配，替换为 y）
(1 + x*y).xreplace({x*y: 1})   # -> 2（x*y 精确匹配为子表达式节点）

# 链式替换：逐步代入
expr = x**2 + y
expr.subs(x, y).subs(y, 1)     # -> 2
```

> 相关参考：[subs 方法三种调用形式](../references/basic-source.md)

## 7. 数值求值

`.evalf()` 方法（别名 `.n()`）将符号表达式转为数值近似；顶层函数 `N()` 等价于 `sympify(x).evalf(n)`。支持任意精度。

```python
from sympy import pi, sqrt, exp, sin, N, S, Rational, I, symbols
x, y, z = symbols('x y z')

# 默认 15 位十进制精度
pi.evalf()                     # -> 3.14159265358979
pi.n()                         # -> 3.14159265358979（.n() 是别名）

# 指定精度位数
pi.evalf(50)                   # -> 3.1415926535897932384626433832795028841971693993751
sqrt(2).evalf(30)              # -> 1.41421356237309504880168872421

# N() 函数：先 sympify 再 evalf
N(pi, 4)                       # -> 3.142
N(sqrt(2), 20)                 # -> 1.4142135623730950488

# 先替换再求值（推荐方式）
expr = x**2 + sin(x)
expr.subs(x, 1).evalf()        # -> 1.84147098480790

# 使用 evalf 的 subs 参数（更精确，避免浮点误差）
(x + y - z).evalf(subs={x: 1e16, y: 1, z: 1e16})  # -> 1.00000000000000
# 对比：直接 subs 会产生浮点精度损失
(x + y - z).subs({x: 1e16, y: 1, z: 1e16})         # -> 0

# chop 参数：截断接近零的微小虚部（数值计算残留）
(I*1e-30).n(chop=True)         # -> 0（去除微小虚部）
(I*1e-30).n()                  # -> 1.0e-30*I（保留虚部）

# Rational 的精确性对比
S(1)/3 + S(1)/3 + S(1)/3       # -> 1（精确）
Rational(1,10) + Rational(2,10) # -> 3/10（精确）
0.1 + 0.2                      # -> 0.30000000000000004（浮点误差）
```

> 相关参考：[EvalfMixin 数值求值](../references/core-init.md) | [evalf 体系](../references/sympify-function-source.md)

## 8. 类型转换

`sympify()`（也叫 `S()`）是 SymPy 的类型入口，将 Python 对象转换为 SymPy 类型。`rational=True` 参数可在解析字符串时将小数转为精确分数；Python float 转精确分数使用 `nsimplify()` 或 `Rational()`。

```python
from sympy import sympify, S, Rational, Float, Symbol, nsimplify

# 基本类型转换
sympify(1)                     # -> 1（Integer）
sympify(3.14)                  # -> 3.14000000000000（Float）
sympify("x**2 + 1")            # -> x**2 + 1（字符串解析）
type(sympify(42))              # -> <class 'sympy.core.numbers.Integer'>

# S() 是 sympify() 的快捷方式
S(3.14)                        # -> 3.14000000000000
S("x + y")                     # -> x + y

# rational=True：字符串中的浮点数转精确分数
sympify("0.1", rational=True)  # -> 1/10（字符串解析时生效）
sympify("0.5", rational=True)  # -> 1/2
sympify(0.1) + sympify(0.2)   # -> 0.300000000000000（Float 相加）
# 使用 nsimplify 将 Python float 转为最简分数
nsimplify(0.1)                 # -> 1/10
nsimplify(0.1) + nsimplify(0.2)  # -> 3/10（精确）

# Rational 直接构造
Rational(1, 10)                # -> 1/10
Rational(3, 6)                 # -> 1/2（自动约分）
Rational(1.5)                  # -> 3/2
Rational("1/3")                # -> 1/3

# Float 构造（指定精度）
Float(0.1, 30)                 # -> 0.100000000000000000000000000000

# 字符串转表达式
sympify("2*x + 3*y")           # -> 2*x + 3*y
sympify("sin(x)^2 + cos(x)^2") # -> sin(x)**2 + cos(x)**2

# 已是 SymPy 对象则原样返回
x = Symbol('x')
sympify(x) is x                # -> True

# strict 模式：仅接受已 sympify 的对象
from sympy import SympifyError
try:
    sympify(1, strict=True)
except SympifyError:
    print("strict 模式拒绝 Python int")  # -> 会打印
```

> 相关参考：[sympify() 转换规则](../references/sympify-function-source.md)

## 9. 基本化简

SymPy 提供从通用 `simplify()` 到专用化简函数的完整体系。专用函数（`expand`、`factor`、`collect`、`together`、`apart`、`cancel`）在特定场景下更可预测。

```python
from sympy import (simplify, expand, factor, collect, together, apart,
                   cancel, trigsimp, powsimp, sin, cos, tan, symbols)
x, y = symbols('x y')

# simplify()：通用启发式化简
expr = (x + x**2)/(x*sin(y)**2 + x*cos(y)**2)
simplify(expr)                 # -> x + 1（利用 sin²+cos²=1）

# expand()：展开多项式
expand((x + y)**2)             # -> x**2 + 2*x*y + y**2
expand((x + 1)*(x - 2))        # -> x**2 - x - 2
expand(sin(x + y))             # -> sin(x)*cos(y) + sin(y)*cos(x)

# factor()：因式分解
factor(x**2 - 1)               # -> (x - 1)*(x + 1)
factor(x**3 - 6*x**2 + 11*x - 6)  # -> (x - 3)*(x - 1)*(x - 2)
factor(x**2 + 2*x + 1)         # -> (x + 1)**2

# collect()：按变量合并同类项
expr = x*y + x - 3 + 2*x**2 - z*x**2 + x**3
collect(expr, x)               # -> x**3 + x**2*(2 - z) + x*(y + 1) - 3

# together()：通分
together(1/x + 1/(x + 1))     # -> (2*x + 1)/(x*(x + 1))

# apart()：部分分式分解
apart(1/(x**2 + 2*x - 3))     # -> 1/(4*(x - 1)) - 1/(4*(x + 3))

# cancel()：约分
cancel((x**2 - 1)/(x - 1))    # -> x + 1
cancel((x**2 + 2*x + 1)/(x + 1))  # -> x + 1

# trigsimp()：三角恒等式化简
trigsimp(sin(x)**2 + cos(x)**2)  # -> 1
trigsimp(sin(x)/cos(x))          # -> tan(x)

# powsimp()：幂运算化简（需要 positive 假设才会同底合并）
a_p, b_p = symbols('a b', positive=True)
powsimp(a_p**x * a_p**y)      # -> a**(x + y)（同底合并）
```

> 相关参考：[化简策略体系](../references/simplify-source.md) | [化简概念](../concepts/06-simplification.md)

## 10. 关系运算

SymPy 使用 `Eq` 创建符号等式，`!=`、`>`、`<`、`>=`、`<=` 创建不等关系。注意 Python 的 `==` 在 SymPy 中创建 `Eq` 对象（符号等式），而非布尔比较。

```python
from sympy import Eq, Ne, Gt, Lt, Ge, Le, And, symbols, solve, pi
x, y = symbols('x y')

# Eq：创建符号等式
eq = Eq(x, y)
eq                             # -> Eq(x, y)
eq.lhs                         # -> x（左边）
eq.rhs                         # -> y（右边）

# 直接使用运算符（更简洁）
x == y                         # -> Eq(x, y)
x != y                         # -> Ne(x, y)
x > y                          # -> x > y（Gt(x, y)）
x < y                          # -> x < y（Lt(x, y)）
x >= 0                         # -> x >= 0（Ge(x, 0)）
x <= 1                         # -> x <= 1（Le(x, 1)）

# 关系运算可用于 solve
solve(Eq(x**2, 4), x)          # -> [-2, 2]
solve(x**2 - 4, x)             # -> [-2, 2]（等价于 solve(Eq(x**2-4, 0), x)）

# canonical：规范化形式（小的在右边）
(x < y).canonical              # -> y > x
(x >= y).reversed              # -> y <= x

# 关系运算可数值求值
(pi > 3)                        # -> True
(pi < 4)                        # -> True
(pi**2 < 10)                    # -> True
expr = Eq(x, 3)
expr.subs(x, 3)                 # -> True
expr.subs(x, 4)                 # -> False

# 关系链（注意：Python 不支持链式比较自动转换）
And(x > 0, x < 1)              # -> (x > 0) & (x < 1)
```

> 相关参考：[Relational 类层次](../references/sympify-function-source.md)

---

**小结**：掌握符号创建（`symbols`/`var`/`abc`）、表达式构建（Python 运算符）、结构查看（`args`/`func`/`srepr`/`free_symbols`）、替换（`subs`/`xreplace`）、数值求值（`evalf`/`n`/`N`）、类型转换（`sympify`/`S`/`Rational`）、化简（`simplify`/`expand`/`factor`/`cancel`）和关系运算（`Eq`/`Gt`/`Lt`），你已经具备了 SymPy 的核心操作能力。下一步可学习 [微积分实战](calculus-examples.md) 和 [方程求解与矩阵实战](solving-equations.md)。
