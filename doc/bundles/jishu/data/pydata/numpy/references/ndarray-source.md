---
type: reference
title: "NumPy ndarray与数组创建API源码"
description: "_core/multiarray.py与_core/numeric.py中的ndarray类定义及array/arange/zeros/ones/empty/full等数组创建函数"
tags: [numpy, source, ndarray, array-creation, multiarray]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: multiarray
    resource: "file:///d:/spaces/SpecWeave/external/libs/python/NumPy/numpy/numpy/_core/multiarray.py"
    title: "numpy/_core/multiarray.py"
  - id: numeric
    resource: "file:///d:/spaces/SpecWeave/external/libs/python/NumPy/numpy/numpy/_core/numeric.py"
    title: "numpy/_core/numeric.py"
  - id: fromnumeric
    resource: "file:///d:/spaces/SpecWeave/external/libs/python/NumPy/numpy/numpy/_core/fromnumeric.py"
    title: "numpy/_core/fromnumeric.py"
---

# NumPy ndarray 与数组创建 API 源码信源

## 源码路径

- C扩展包装：`numpy/_core/multiarray.py`（Python层包装，实际实现在 `_multiarray_umath` C扩展中）
- Python层数值函数：`numpy/_core/numeric.py`
- 数组方法转发：`numpy/_core/fromnumeric.py`

## 关键事实提取

### F-011：ndarray在C扩展中定义

ndarray类本身不在Python文件中定义，而是在C扩展模块 `_multiarray_umath` 中实现。`multiarray.py` 第12行 `from ._multiarray_umath import *` 将其导入。`numeric.py` 第49行 `from .multiarray import (... ndarray ...)` 二次导入。

### F-012：multiarray.py的__all__导出列表

`multiarray.py` 第30-50行定义了该模块的 `__all__`，核心符号包括：
- 常量：`ALLOW_THREADS`, `BUFSIZE`, `CLIP`, `MAXDIMS`, `RAISE`, `WRAP`
- 数组标志：`MAY_SHARE_BOUNDS`, `MAY_SHARE_EXACT`
- 核心类：`ndarray`, `flatiter`, `nditer`, `nested_iters`, `dtype`, `broadcast`, `flagsobj`
- 数组创建：`arange`, `array`, `empty`, `zeros`, `frombuffer`, `fromfile`, `fromiter`, `fromstring`, `from_dlpack`, `empty_like`
- 数组操作：`concatenate`, `copyto`, `where`, `dot`, `inner`, `vdot`, `matmul`, `vecdot`, `correlate`, `correlate2`
- 类型系统：`can_cast`, `min_scalar_type`, `promote_types`, `result_type`, `typeinfo`, `sctypeDict`
- 排序搜索：`lexsort`, `searchsorted`, `bincount`, `packbits`, `unpackbits`
- 日期：`busday_count`, `busday_offset`, `busdaycalendar`, `is_busday`, `datetime_as_string`, `datetime_data`
- 内存：`may_share_memory`, `shares_memory`
- 其他：`count_nonzero`, `putmask`, `c_einsum`, `ravel_multi_index`, `unravel_index`, `frompyfunc`

### F-013：empty_like是Python层包装

`multiarray.py` 第115-194行定义了 `empty_like` 函数，使用 `@array_function_from_c_func_and_dispatcher` 装饰器，签名为：
```python
def empty_like(prototype, dtype=None, order="K", subok=True, shape=None, *, device=None):
```
参数说明：
- `order`: {'C', 'F', 'A', 'K'}，默认'K'（匹配原型布局）
- `subok`: bool，默认True（保留子类类型）
- `device`: str，可选，Array API互操作性，仅允许"cpu"
- `shape`: int或int序列，可选，覆盖结果形状

### F-014：concatenate参数签名

`multiarray.py` 第197-198行：
```python
def concatenate(arrays, axis=0, out=None, *, dtype=None, casting="same_kind"):
```
- `casting`: {'no', 'equiv', 'safe', 'same_kind', 'unsafe'}，默认'same_kind'
- `dtype` 和 `casting` 在NumPy 1.20.0新增

### F-015：numeric.py中定义的数组创建函数

`numeric.py` 中通过 `@array_function_dispatch` 装饰器定义的核心创建函数：

**zeros_like**（第97-100行）：
```python
def zeros_like(a, dtype=None, order='K', subok=True, shape=None, *, device=None):
```

**ones**（第172行）：
```python
def ones(shape, dtype=None, order='C', *, device=None, like=None):
```

**full**（第325行）：
```python
def full(shape, fill_value, dtype=None, order='C', *, device=None, like=None):
```

**indices**（第1731行）：
```python
def indices(dimensions, dtype=int, sparse=False):
```

**fromfunction**（第1834行）：
```python
def fromfunction(function, shape, *, dtype=float, like=None, **kwargs):
```

**identity**（第2184行）：
```python
def identity(n, dtype=None, *, like=None):
```

### F-016：newaxis是None的别名

`numeric.py` 第67行：`newaxis = None`，用于在索引中插入新维度。

### F-017：ufunc类型通过sin获取

`numeric.py` 第66行：`ufunc = type(sin)`，ufunc类本身不直接暴露，而是通过现有ufunc实例的type获取。

### F-018：fromnumeric.py中的数组方法转发机制

`fromnumeric.py` 中的函数大多通过两种方式实现：
1. 对于ndarray子类或非ndarray对象，调用对象的对应方法（如 `obj.sum(axis=...)`）
2. 对于纯ndarray，直接调用ufunc的reduce方法

第44-67行的 `_wrapreduction` 函数是核心的规约包装器：
```python
def _wrapreduction(obj, ufunc, method, axis, dtype, out,
                   keepdims=_NoValue, initial=_NoValue, where=_NoValue, /):
    if type(obj) is not mu.ndarray:
        try:
            reduction = getattr(obj, method)
        except AttributeError:
            pass
        else:
            return reduction(axis=axis, dtype=dtype, out=out, **passkwargs)
    return ufunc.reduce(obj, axis, dtype, out, **passkwargs)
```

### F-019：fromnumeric.py的__all__列表

`fromnumeric.py` 第18-28行导出的方法包括：
- 规约：`all`, `any`, `sum`, `prod`, `mean`, `std`, `var`, `max`(amax), `min`(amin), `ptp`
- 最值索引：`argmax`, `argmin`
- 排序分区：`sort`, `argsort`, `partition`, `argpartition`, `searchsorted`
- 形状操作：`reshape`, `ravel`, `squeeze`, `transpose`, `swapaxes`, `resize`, `ndim`, `shape`, `size`
- 选择索引：`take`, `choose`, `compress`, `diagonal`, `nonzero`, `put`
- 累积：`cumsum`, `cumprod`, `cumulative_sum`, `cumulative_prod`
- 其他：`clip`, `round`(around), `trace`, `repeat`, `matrix_transpose`, `top_k`

### F-020：take函数签名

`fromnumeric.py` 第95行：
```python
def take(a, indices, axis=None, out=None, mode='raise'):
```
`mode` 参数取值：{'raise', 'wrap', 'clip'}，默认'raise'。

### F-021：array_function_dispatch装饰器

`fromnumeric.py` 第35-36行：
```python
array_function_dispatch = functools.partial(
    overrides.array_function_dispatch, module='numpy')
```
所有公共API函数都通过此装饰器支持 `__array_function__` 协议（NEP-18）。

### F-022：MAXDIMS常量

`multiarray.py` 的 `__all__` 中导出了 `MAXDIMS`，表示数组最大维度数（NumPy中默认值为32）。

## 相关概念

- [ndarray多维数组](../concepts/01-ndarray.md)
- [数组创建](../concepts/06-array-creation.md)
- [索引与切片](../concepts/05-indexing.md)
