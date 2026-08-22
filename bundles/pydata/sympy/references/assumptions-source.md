---
okf_version: "0.2"
type: reference
title: 假设推理系统源码
description: ask()查询、Q谓词对象、CNF合取范式、SAT求解、refine()细化、新旧假设系统
sources:
  - id: ask-source
    resource: external/libs/python/sympy/sympy/sympy/assumptions/ask.py
    title: ask 查询引擎
  - id: cnf-source
    resource: external/libs/python/sympy/sympy/sympy/assumptions/cnf.py
    title: CNF 合取范式
  - id: refine-source
    resource: external/libs/python/sympy/sympy/sympy/assumptions/refine.py
    title: refine 表达式细化
  - id: satask-source
    resource: external/libs/python/sympy/sympy/sympy/assumptions/satask.py
    title: SAT求解器
---

# 假设推理系统源码信源

SymPy 拥有两套并行的假设系统：核心层 `is_*` 属性系统（构造时确定，快速但有限）和 `sympy.assumptions` 新假设系统（基于 SAT 求解，灵活但较慢）。`ask()` 函数在给定假设下查询命题真值，`Q` 对象提供谓词构造器，`refine()` 利用假设化简表达式，CNF/SAT 模块提供底层逻辑推理能力。[^F-076][^F-077][^F-078]

## 新旧假设系统双轨设计

SymPy 的假设推理采用"双轨制"设计，两套系统各司其职：[^F-012][^F-077]

| 特性 | 旧系统（核心 is_* 属性） | 新系统（sympy.assumptions） |
|------|--------------------------|----------------------------|
| 存储位置 | `Basic._assumptions`（`StdFactKB` 类型） | 独立模块 `sympy.assumptions` |
| 确定时机 | 对象构造时通过 `__init_subclass__` 设置[^F-003] | 运行时通过 `ask()` 动态查询 |
| 查询方式 | `expr.is_positive`、`expr.is_real` 等属性 | `ask(Q.positive(x), assumptions)` |
| 返回值 | `True`/`False`/`None`（三值逻辑） | `True`/`False`/`None`（三值逻辑） |
| 推理能力 | 基于蕴含规则的直接推导（有限） | 基于 SAT 求解器的通用逻辑推理（强大） |
| 性能 | 快速（属性访问，O(1) 查表） | 较慢（SAT 求解开销） |
| 扩展性 | 需在类上定义 `_eval_is_*` 方法 | 通过注册 handler 扩展谓词 |
| 适用场景 | 简单判断、代码内部快速检查 | 复杂假设组合、条件化简 |

### 核心 is_* 属性系统

`Basic` 类在 [core/basic.py:229-258](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L229-L258) 声明了一组 `is_*` 类属性，初始值为 `False` 或 `None`，子类在构造时通过 `_prepare_class_assumptions(cls)` 初始化默认假设。[^F-012]

```python
from sympy import Symbol, Integer, pi

# 构造时设置假设
x = Symbol('x', positive=True)
x.is_positive       # True
x.is_real           # True（positive 蕴含 real）
x.is_complex        # True（real 蕴含 complex）
x.is_negative       # False

# 常量的 is_* 属性
Integer(5).is_integer   # True
Integer(5).is_positive  # True
Integer(-3).is_negative # True
pi.is_positive          # True
pi.is_transcendental    # True

# 无法确定时返回 None
y = Symbol('y')
y.is_positive       # None（无假设信息）
```

核心 is_* 属性通过三值逻辑（fuzzy logic）进行推导：`True`（确定为真）、`False`（确定为假）、`None`（无法确定）。推导由 `sympy.core.logic` 中的 `fuzzy_and`、`fuzzy_or`、`fuzzy_not` 等函数支持。

## ask() 查询函数

`ask()` 定义于 [assumptions/ask.py:406](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/ask.py#L406)，是新假设系统的核心查询入口。[^F-077]

### 函数签名

```python
def ask(proposition, assumptions=True, context=global_assumptions):
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `proposition` | Boolean | — | 待查询的命题（`Q.xxx(expr)` 形式） |
| `assumptions` | Boolean | `True` | 已知假设条件（`Q.xxx(expr)` 或 `And(...)` 组合） |
| `context` | AssumptionsContext | `global_assumptions` | 全局假设上下文 |

返回值：`True`（命题成立）、`False`（命题不成立）、`None`（无法确定）。

```python
from sympy import ask, Q, Symbol, And, Or, Not
from sympy.abc import x, y

# 基本查询
ask(Q.real(x), Q.positive(x))       # True（positive → real）
ask(Q.positive(x), Q.real(x))       # None（real 不蕴含 positive）
ask(Q.complex(x), Q.real(x))        # True（real → complex）
ask(Q.nonzero(x), Q.positive(x))    # True（positive → nonzero）

# 直接查询（无额外假设）
ask(Q.positive(1))                  # True
ask(Q.negative(0))                  # False
ask(Q.prime(7))                     # True
ask(Q.even(3))                      # False

# 组合假设
ask(Q.positive(x), And(Q.real(x), Q.nonzero(x), ~Q.negative(x)))  # True

# 否定与复合
ask(Q.positive(x), Q.negative(x))   # False
ask(Q.real(x + 1), Q.real(x))       # True
```

### ask() 的推理机制

`ask()` 内部采用多层推理策略：

1. **已知事实查询**：首先检查表达式的 `is_*` 属性（新旧系统桥接）
2. **Handler 直接推理**：调用谓词注册的 handler 函数
3. **SAT 求解**：当直接推理无法确定时，调用 `satask()` 使用 SAT 求解器
4. **结果缓存**：查询结果被缓存以提高性能

## Q 谓词对象

`Q` 是 `AssumptionKeys` 类（[assumptions/ask.py:20](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/ask.py#L20)）的单例实例，通过 `@memoize_property` 装饰器提供谓词键。每个属性访问返回对应的 `Predicate` 实例，用于构造 `AppliedPredicate` 命题。[^F-078]

### 集合论谓词

| 谓词 | 含义 | 蕴含关系 |
|------|------|----------|
| `Q.hermitian` | 厄米特（实对称） | — |
| `Q.antihermitian` | 反厄米特 | — |
| `Q.real` | 实数 | → `Q.complex`、`Q.hermitian` |
| `Q.extended_real` | 扩充实数（含 ±∞） | — |
| `Q.imaginary` | 纯虚数 | → `Q.complex`、`Q.antihermitian` |
| `Q.complex` | 复数 | → `Q.commutative` |
| `Q.algebraic` | 代数数 | → `Q.complex` |
| `Q.transcendental` | 超越数 | → `Q.complex` |
| `Q.rational` | 有理数 | → `Q.real`、`Q.algebraic` |
| `Q.irrational` | 无理数 | → `Q.real` |
| `Q.integer` | 整数 | → `Q.rational` |
| `Q.noninteger` | 非整数 | — |

### 序关系谓词

| 谓词 | 含义 | 蕴含关系 |
|------|------|----------|
| `Q.positive` | 正数（>0） | → `Q.nonzero`、`Q.real`、`Q.extended_positive` |
| `Q.negative` | 负数（<0） | → `Q.nonzero`、`Q.real`、`Q.extended_negative` |
| `Q.zero` | 零 | → `Q.real`、`Q.even`、`Q.nonnegative`、`Q.nonpositive` |
| `Q.nonzero` | 非零 | — |
| `Q.nonpositive` | 非正数（≤0） | → `Q.real` |
| `Q.nonnegative` | 非负数（≥0） | → `Q.real` |
| `Q.extended_positive` | 扩充正数（含 +∞） | — |
| `Q.extended_negative` | 扩充负数（含 -∞） | — |
| `Q.positive_infinite` | 正无穷 | → `Q.infinite`、`Q.extended_positive` |
| `Q.negative_infinite` | 负无穷 | → `Q.infinite`、`Q.extended_negative` |

### 数论谓词

| 谓词 | 含义 |
|------|------|
| `Q.even` | 偶数 | → `Q.integer` |
| `Q.odd` | 奇数 | → `Q.integer` |
| `Q.prime` | 素数 | → `Q.integer`、`Q.positive` |
| `Q.composite` | 合数 | → `Q.integer`、`Q.positive` |

### 微积分类谓词

| 谓词 | 含义 |
|------|------|
| `Q.finite` | 有限 |
| `Q.infinite` | 无穷 |

### 矩阵谓词

| 谓词 | 含义 |
|------|------|
| `Q.symmetric` | 对称矩阵 |
| `Q.invertible` | 可逆矩阵 |
| `Q.orthogonal` | 正交矩阵 |
| `Q.unitary` | 酉矩阵 |
| `Q.positive_definite` | 正定矩阵 |
| `Q.upper_triangular` | 上三角矩阵 |
| `Q.lower_triangular` | 下三角矩阵 |
| `Q.diagonal` | 对角矩阵 |
| `Q.fullrank` | 满秩矩阵 |
| `Q.square` | 方阵 |
| `Q.singular` | 奇异矩阵 |
| `Q.normal` | 正规矩阵 |

### 通用谓词

| 谓词 | 含义 |
|------|------|
| `Q.commutative` | 交换律成立 |
| `Q.is_true` | 布尔真 |
| `Q.eq(x, y)` | 相等（x == y） |
| `Q.ne(x, y)` | 不等（x != y） |
| `Q.gt(x, y)` | 严格大于（x > y） |
| `Q.ge(x, y)` | 大于等于（x ≥ y） |

```python
from sympy import ask, Q, symbols, pi, I, Rational, sqrt, Integer, S

# 集合论谓词
x = symbols('x', real=True)
ask(Q.real(x))              # True
ask(Q.complex(x))           # True
ask(Q.integer(Rational(5))) # False（Integer(5) 是，但 Rational(5) 是 5/1...）
ask(Q.integer(Integer(5)))  # True
ask(Q.rational(S.Half))     # True
ask(Q.transcendental(pi))   # True
ask(Q.algebraic(sqrt(2)))   # True（sqrt(2)是代数数）
ask(Q.imaginary(I))         # True

# 数论谓词
ask(Q.prime(7))             # True
ask(Q.prime(4))             # False
ask(Q.composite(4))         # True
ask(Q.even(2))              # True
ask(Q.odd(3))               # True

# 序关系谓词
ask(Q.positive(pi))         # True
ask(Q.negative(-1))         # True
ask(Q.zero(0))              # True
ask(Q.nonzero(1))           # True
```

### 常用蕴含推理链

SymPy 假设系统内置了谓词间的蕴含关系（存储在 `sympy.assumptions.facts` 中），构成有向无环图：

```
integer → rational → real → complex → commutative
integer → rational → algebraic → complex
positive → nonzero ∧ real → complex
negative → nonzero ∧ real → complex
zero → real ∧ even ∧ nonnegative ∧ nonpositive
even → integer
odd → integer
prime → integer ∧ positive
composite → integer ∧ positive
positive → extended_positive
negative → extended_negative
```

## CNF 合取范式

CNF（Conjunctive Normal Form，合取范式）是 SAT 求解的基础表示形式。SymPy 在 [assumptions/cnf.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/cnf.py) 中实现了完整的 CNF 编码系统。[^F-080][^F-081]

### Literal 类

`Literal` 定义于 [cnf.py:16](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/cnf.py#L16)，是 CNF 的最小元素，表示一个可能被否定的布尔原子。[^F-081]

```python
class Literal:
    def __new__(cls, lit, is_Not=False):
```

| 属性/方法 | 说明 |
|-----------|------|
| `lit` | 布尔表达式（`AppliedPredicate` 等） |
| `is_Not` | 是否为否定形式 |
| `arg` 属性 | 返回 `self.lit` |
| `rcall(expr)` | 将谓词应用到表达式，返回新的 Literal |
| `~` 运算符 | 返回否定 Literal |

```python
from sympy import Q
from sympy.assumptions.cnf import Literal
from sympy.abc import x

lit = Literal(Q.even(x))         # Literal(Q.even(x), False)
neg_lit = ~lit                   # Literal(Q.even(x), True)
lit.arg                          # Q.even(x)
lit.is_Not                       # False
neg_lit.is_Not                   # True
```

### CNF 类

`CNF` 定义于 [cnf.py:271](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/cnf.py#L271)，表示布尔表达式的合取范式，由子句（clause）集合组成，每个子句是 `Literal` 对象的 `frozenset`（文字的析取）。[^F-080]

CNF 的核心方法：

| 方法 | 说明 |
|------|------|
| `to_CNF(expr)` （类方法） | 将布尔表达式转换为 CNF |
| `add_clause(clause)` | 添加子句 |
| `_convert_prop(prop)` | 递归转换属性表达式 |
| `from_prop(prop)` | 从布尔属性构造 CNF |

```python
from sympy import Q, And, Or, Not
from sympy.assumptions.cnf import CNF
from sympy.abc import x

# CNF 构造与转换
expr = And(Q.real(x), Or(Q.positive(x), Q.negative(x)))
cnf = CNF.to_CNF(expr)
# CNF 内部表示为子句的 frozenset 集合
# 每个子句是 Literal 的 frozenset（析取）
```

### EncodedCNF 类

`EncodedCNF` 定义于 [cnf.py:383](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/cnf.py#L383)，是 CNF 的编码表示，将每个布尔变量映射为整数，用于 SAT 求解器高效处理。[^F-080]

```python
class EncodedCNF:
    def __init__(self, data=None, encoding=None):
```

| 属性 | 说明 |
|------|------|
| `data` | 编码后的子句列表（`list[list[int]]`），每个整数代表一个变量（正数=正文字，负数=否定文字） |
| `encoding` | 符号到整数的映射字典 |

EncodedCNF 是连接 SymPy 逻辑系统与底层 SAT 求解器的桥梁：SymPy 的布尔表达式 → CNF → EncodedCNF → SAT 求解器（整数列表输入）。

## satisfiable() SAT 求解函数

`satisfiable()` 从 `sympy.logic.inference` 导入（在 [ask.py:10](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/ask.py#L10)），是 SymPy 的布尔可满足性求解器。它接受一个 CNF 编码的布尔公式，返回满足赋值（字典）或 `False`（不可满足）。

`ask.py` 模块开头导入：
```python
from sympy.logic.inference import satisfiable
from sympy.logic.boolalg import And
```

### satask() SAT 推理函数

`satask()` 定义于 [assumptions/satask.py:18](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/satask.py#L18)，使用 SAT 算法评估命题在假设下的布尔值。[^F-082]

```python
def satask(proposition, assumptions=True, use_known_facts=True, iterations=oo):
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `proposition` | — | 待查询命题 |
| `assumptions` | `True` | 已知假设 |
| `use_known_facts` | `True` | 是否使用内置事实规则 |
| `iterations` | `oo` | 迭代次数限制 |

工作原理：
1. 将命题和假设的否定编码为 CNF
2. 与已知事实（`get_known_facts_dict()`）合并
3. 调用 `satisfiable()` 检测是否存在反例
4. 若不可满足则命题为 `True`；若假设下命题否定可满足则命题为 `False`；否则为 `None`

## refine() 表达式细化

`refine()` 定义于 [assumptions/refine.py:21](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/refine.py#L21)，利用假设条件化简表达式。与 `simplify()` 不同，`refine()` 只在给定假设下进行等价变换，不做结构上的"盲目化简"。[^F-079]

### 函数签名

```python
def refine(expr, assumptions=True):
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `expr` | Expr/Basic | — | 待化简表达式 |
| `assumptions` | Boolean/bool | `True` | 假设条件 |

### 典型化简规则

| 表达式 | 假设 | 结果 |
|--------|------|------|
| `sqrt(x**2)` / `Abs(x)` | `Q.real(x)` | `Abs(x)` |
| `sqrt(x**2)` / `Abs(x)` | `Q.positive(x)` | `x` |
| `Abs(x)` | `Q.negative(x)` | `-x` |
| `sign(x)` | `Q.positive(x)` | `1` |
| `sign(x)` | `Q.negative(x)` | `-1` |
| `Q.real(x)` | `Q.positive(x)` | `True` |

```python
from sympy import refine, sqrt, Abs, sign, Q, symbols, exp, log
from sympy.abc import x, y

# Abs 化简
refine(Abs(x), Q.positive(x))       # x
refine(Abs(x), Q.negative(x))       # -x
refine(sqrt(x**2), Q.positive(x))   # x
refine(sqrt(x**2), Q.real(x))       # Abs(x)

# sign 化简
refine(sign(x), Q.positive(x))      # 1
refine(sign(x), Q.negative(x))      # -1

# 布尔表达式化简
refine(Q.real(x), Q.positive(x))    # True
refine(Q.positive(x), Q.real(x))    # Q.positive(x)（无法确定）

# 复合假设
refine(Abs(x - y), Q.positive(x - y))  # x - y
```

### refine 的实现机制

`refine()` 内部通过 `Basic.refine(assumption)` 方法（[core/basic.py:2036](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L2036)）递归调用各类型的 `_eval_refine(assumptions)` 钩子方法。`Abs`、`sign`、`sqrt`、`re`、`im`、`conjugate` 等类都定义了各自的细化规则。[^F-011]

## 假设上下文管理

### assuming() 上下文管理器

`assuming()` 从 `sympy.assumptions.assume` 导出，允许在代码块内临时添加全局假设：

```python
from sympy import assuming, Q, ask, symbols
x = symbols('x')

with assuming(Q.positive(x)):
    print(ask(Q.positive(x)))   # True（上下文内有效）
    print(ask(Q.real(x)))       # True

print(ask(Q.positive(x)))       # None（退出上下文后失效）
```

### global_assumptions

`global_assumptions` 是 `AssumptionsContext` 的全局实例，存储全局有效的假设条件。`ask()` 默认将其纳入推理上下文。

## 模块导出

[assumptions/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/__init__.py) 导出的公开 API：[^F-076]

| 导出符号 | 来源 | 说明 |
|----------|------|------|
| `AppliedPredicate` | `.assume` | 应用后的谓词实例（如 `Q.positive(x)`） |
| `Predicate` | `.assume` | 谓词基类 |
| `AssumptionsContext` | `.assume` | 假设上下文类 |
| `assuming` | `.assume` | 假设上下文管理器 |
| `global_assumptions` | `.assume` | 全局假设上下文实例 |
| `Q` | `.ask` | 谓词键单例 |
| `ask` | `.ask` | 假设查询函数 |
| `refine` | `.refine` | 表达式细化函数 |
| `BinaryRelation` | `.relation` | 二元关系基类 |
| `AppliedBinaryRelation` | `.relation` | 应用后的二元关系 |

## 完整使用示例

### 示例 1：综合使用 ask/Q/refine

```python
from sympy import (ask, Q, refine, Abs, sqrt, sign, symbols,
                   pi, E, I, oo, And, Or, Not, simplify)
from sympy.abc import x, y, z

# === ask() 查询示例 ===
# 数域判断
ask(Q.integer(5))                 # True
from sympy import Rational
ask(Q.rational(Rational(3, 4)))   # True
ask(Q.transcendental(pi))         # True
ask(Q.algebraic(sqrt(2)))         # True
ask(Q.imaginary(I))               # True
ask(Q.complex(I))                 # True

# 序关系
n = symbols('n', positive=True)
ask(Q.positive(n + 1))            # True
ask(Q.positive(-n))               # False
ask(Q.zero(0))                    # True

# 组合推理
ask(Q.real(x), And(Q.rational(x), Q.positive(x)))  # True
ask(Q.positive(x), Q.prime(x))    # True（素数必为正整数）

# === refine() 化简示例 ===
# Abs 化简
expr = Abs(x**2 - 1)
refine(expr, Q.positive(x - 1))   # x**2 - 1（x > 1 时）
refine(expr, Q.negative(x + 1))   # -(x**2 - 1) = 1 - x**2（x < -1 时）

# 分段函数结合假设
from sympy import Piecewise
p = Piecewise((x, Q.positive(x)), (-x, True))
refine(p, Q.positive(x))          # x
refine(p, Q.negative(x))          # -x
```

### 示例 2：新旧系统协同

```python
from sympy import Symbol, ask, Q

# 构造 Symbol 时指定的假设进入旧系统
x = Symbol('x', positive=True, integer=True)
x.is_positive       # True（旧系统直接属性访问）
x.is_integer        # True
x.is_real           # True

# 新系统也能看到这些假设
ask(Q.positive(x))  # True
ask(Q.real(x))      # True

# 新系统支持更灵活的临时假设
y = Symbol('y')
ask(Q.real(y))                      # None（无假设）
ask(Q.real(y), Q.positive(y))       # True（临时假设下推导）

# 注意：ask() 的临时假设不会修改对象本身
y.is_positive       # None（未改变）
```

### 示例 3：SAT 推理演示

```python
from sympy import ask, Q, And, Or, Not, symbols, satisfiable
from sympy.abc import x

# SAT 可以进行复杂的组合推理
# 已知：x 是实数且非零，且 x 不是负数 → x 必为正
ask(Q.positive(x),
    And(Q.real(x), Q.nonzero(x), Not(Q.negative(x))))
# True

# 已知：x 是整数且是素数且是偶数 → x = 2（虽然 SymPy 不会直接返回2）
ask(Q.positive(x),
    And(Q.integer(x), Q.prime(x), Q.even(x)))
# True（唯一的偶素数是2，必为正）

# satisfiable() 底层演示
from sympy.logic.inference import satisfiable
from sympy.logic.boolalg import And, Or, Not
from sympy import symbols as sym_symbols
A, B, C = sym_symbols('A B C')
satisfiable(And(A, Or(B, C), Not(And(A, B))))
# {A: True, B: False, C: True}（一个满足赋值）
satisfiable(And(A, Not(A)))
# False（不可满足）
```
