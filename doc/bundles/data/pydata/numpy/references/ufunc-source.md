---
type: reference
title: "NumPy ufunc通用函数系统源码"
description: "_core/umath.py中ufunc系统的定义、逐元素运算、广播机制与reduce/accumulate/outer方法"
tags: [numpy, source, ufunc, umath, broadcasting, vectorization]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: umath
    resource: "file:///d:/spaces/SpecWeave/external/libs/python/NumPy/numpy/numpy/_core/umath.py"
    title: "numpy/_core/umath.py"
  - id: ufunc-h
    resource: "file:///d:/spaces/SpecWeave/external/libs/python/NumPy/numpy/numpy/_core/include/numpy/ufuncobject.h"
    title: "numpy/_core/include/numpy/ufuncobject.h"
---

# NumPy ufunc 通用函数系统源码信源

## 源码路径

- Python层包装：`numpy/_core/umath.py`
- C头文件：`numpy/_core/include/numpy/ufuncobject.h`
- C实现：`numpy/_core/src/umath/ufunc_object.c`、`loops.c.src`

## 关键事实提取

### F-023：umath.py是C扩展的Python包装

`umath.py` 第1-6行docstring说明：In v1.16 the multiarray and umath c-extension modules were merged into a single `_multiarray_umath` extension module. So we replicate the old namespace by importing from the extension module.

第11-12行：
```python
from . import _multiarray_umath
from ._multiarray_umath import *
```

### F-024：umath.py导出的ufunc列表

`umath.py` 第45-60行 `__all__` 列出了所有ufunc，按类别整理如下：

**数学常量**：`pi`, `e`, `euler_gamma`

**一元数学函数**：
- 三角函数：`sin`, `cos`, `tan`, `arcsin`(asin), `arccos`(acos), `arctan`(atan), `arctan2`(atan2)
- 双曲函数：`sinh`, `cosh`, `tanh`, `arcsinh`(asinh), `arccosh`(acosh), `arctanh`(atanh)
- 指数/对数：`exp`, `exp2`, `expm1`, `log`, `log2`, `log10`, `log1p`, `logaddexp`, `logaddexp2`
- 取整：`ceil`, `floor`, `trunc`, `rint`
- 其他：`sqrt`, `square`, `absolute`, `fabs`, `sign`, `conjugate`(conj), `negative`, `positive`, `reciprocal`, `spacing`, `signbit`, `copysign`, `nextafter`, `modf`, `frexp`, `ldexp`, `fmod`, `floor_divide`, `true_divide`, `float_power`, `cbrt`

**二元数学函数**：
- 算术：`add`, `subtract`, `multiply`, `divide`, `power`(pow), `remainder`(mod), `divmod`
- 比较：`equal`, `not_equal`, `less`, `less_equal`, `greater`, `greater_equal`
- 逻辑：`logical_and`, `logical_or`, `logical_xor`, `logical_not`
- 位运算：`bitwise_and`, `bitwise_or`, `bitwise_xor`, `invert`, `left_shift`, `right_shift`, `bitwise_count`
- 极值：`maximum`, `minimum`, `fmax`, `fmin`
- 其他：`hypot`, `arctan2`, `heaviside`, `gcd`, `lcm`

**浮点测试**：`isfinite`, `isinf`, `isnan`, `isnat`

**矩阵乘法**：`matmul`, `matvec`, `vecdot`, `vecmat`

**角度转换**：`deg2rad`(radians), `rad2deg`(degrees)

### F-025：ufunc对象在C层定义

ufunc类的类型对象为 `PyUFunc_Type`，定义在C扩展中。Python层通过 `type(sin)` 获取ufunc类型（见 `numeric.py` 第66行：`ufunc = type(sin)`）。

### F-026：frompyfunc用于创建自定义ufunc

`multiarray.py` 的 `__all__` 导出了 `frompyfunc`，这是从Python函数创建ufunc的工厂函数。`umath.py` 也在 `from ._multiarray_umath import *` 中获取了它。

### F-027：ufunc模块属性覆盖

`multiarray.py` 第81-105行的 `_override___module__()` 函数将所有ufunc的 `__module__` 设为 `"numpy"`（而非 `"numpy._core.umath"`），`__qualname__` 设为ufunc名称。

### F-028：ufunc的核心方法

每个ufunc对象在C层实现了以下方法（可从NumPy文档和头文件确认）：
- `__call__(*inputs, **kwargs)`：逐元素调用，支持 `out`, `where`, `casting`, `order`, `dtype`, `subok`, `signature` 等关键字参数
- `reduce(a, axis=0, dtype=None, out=None, keepdims=False, initial=, where=)`：规约运算
- `accumulate(a, axis=0, dtype=None, out=None)`：累积运算
- `reduceat(a, indices, axis=0, dtype=None, out=None)`：分段规约
- `outer(A, B, **kwargs)`：外积
- `at(a, indices, b=None)`：无缓冲的就地运算

### F-029：ufunc的nin/nout/nargs属性

每个ufunc在C层包含以下核心属性：
- `nin`：输入参数个数
- `nout`：输出参数个数
- `nargs`：总参数个数（nin + nout）
- `ntypes`：类型循环数量
- `types`：支持的类型签名列表
- `identity`：单位元（如add的0，multiply的1，None表示无单位元）

### F-030：matmul和vecdot是特殊ufunc

`matmul`（矩阵乘法）和 `vecdot`（向量点积）被列为ufunc但具有特殊的广播规则——它们不遵循标准的逐元素广播，而是执行矩阵运算语义。

### F-031：errstate上下文管理器

`numeric.py` 第14行从 `._ufunc_config` 导入 `errstate`，这是控制浮点错误处理（如除零、溢出、无效值）的上下文管理器。

## 相关概念

- [ufunc通用函数](/concepts/03-ufunc.md)
- [广播规则](/concepts/04-broadcasting.md)
- [线性代数与随机数](/concepts/07-linear-algebra.md)
