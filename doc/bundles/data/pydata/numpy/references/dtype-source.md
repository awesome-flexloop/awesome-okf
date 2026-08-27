---
type: reference
title: "NumPy dtype与数值类型系统源码"
description: "_core/_dtype.py和_core/numerictypes.py中dtype系统的类型层次、kind字符码、类型提升规则与结构化dtype"
tags: [numpy, source, dtype, numerictypes, type-system]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: dtype
    resource: "file:///d:/spaces/SpecWeave/external/libs/python/NumPy/numpy/numpy/_core/_dtype.py"
    title: "numpy/_core/_dtype.py"
  - id: numerictypes
    resource: "file:///d:/spaces/SpecWeave/external/libs/python/NumPy/numpy/numpy/_core/numerictypes.py"
    title: "numpy/_core/numerictypes.py"
  - id: ndarraytypes-h
    resource: "file:///d:/spaces/SpecWeave/external/libs/python/NumPy/numpy/numpy/_core/include/numpy/ndarraytypes.h"
    title: "numpy/_core/include/numpy/ndarraytypes.h"
---

# NumPy dtype 与数值类型系统源码信源

## 源码路径

- dtype辅助实现：`numpy/_core/_dtype.py`（字符串表示、构造repr等Python层辅助）
- 数值类型定义：`numpy/_core/numerictypes.py`（类型层次、sctypeDict、sctypes）
- C类型定义：`numpy/_core/include/numpy/ndarraytypes.h`、`arrayscalars.h`

## 关键事实提取

### F-032：dtype的kind字符映射

`_dtype.py` 第8-20行定义了kind字符到类型名的映射：
```python
_kind_to_stem = {
    'u': 'uint',       # 无符号整数
    'i': 'int',        # 有符号整数
    'c': 'complex',    # 复数
    'f': 'float',      # 浮点数
    'b': 'bool',       # 布尔值
    'V': 'void',       # void/结构化类型
    'O': 'object',     # Python对象
    'M': 'datetime',   # 日期时间
    'm': 'timedelta',  # 时间差
    'S': 'bytes',      # 字节串
    'U': 'str',        # Unicode字符串
}
```

### F-033：numerictypes.py中的类型层次树

`numerictypes.py` 第40-76行的docstring清晰描述了完整的类型继承层次：

```
generic
  +-> bool                                   (kind=b)
  +-> number
  |   +-> integer
  |   |   +-> signedinteger     (intxx)      (kind=i)
  |   |   |     byte (int8)
  |   |   |     short (int16)
  |   |   |     intc
  |   |   |     intp
  |   |   |     int_ (default int, int32/int64)
  |   |   |     longlong (int64)
  |   |   \-> unsignedinteger  (uintxx)     (kind=u)
  |   |         ubyte (uint8)
  |   |         ushort (uint16)
  |   |         uintc
  |   |         uintp
  |   |         uint (default uint)
  |   |         ulonglong (uint64)
  |   +-> inexact
  |       +-> floating          (floatxx)    (kind=f)
  |       |     half (float16)
  |       |     single (float32)
  |       |     double (float64)
  |       |     longdouble
  |       \-> complexfloating  (complexxx)  (kind=c)
  |             csingle (complex64)
  |             cdouble (complex128)
  |             clongdouble
  +-> flexible
  |   +-> character
  |   |     bytes_                           (kind=S)
  |   |     str_                             (kind=U)
  |   \-> void                              (kind=V)
  \-> object_                                (kind=O)
```

### F-034：固定宽度类型名称

`numerictypes.py` 第15-19行docstring列出的固定宽度类型：
- 整数：`int8`, `int16`, `int32`, `int64`, `uint8`, `uint16`, `uint32`, `uint64`
- 浮点：`float16`, `float32`, `float64`, `float96`, `float128`（后两者平台相关）
- 复数：`complex64`, `complex128`, `complex192`, `complex256`（后两者平台相关）
- 日期：`datetime64`, `timedelta64`

### F-035：C风格类型别名

`numerictypes.py` 第21-38行docstring列出的C风格别名：
- 整数：`byte`, `ubyte`, `short`, `ushort`, `intc`, `uintc`, `intp`, `uintp`, `int_`, `uint`, `longlong`, `ulonglong`, `long`, `ulong`
- 浮点：`half`, `single`, `double`, `longdouble`
- 复数：`csingle`, `cdouble`, `clongdouble`

### F-036：sctypeDict和sctypes

`numerictypes.py` 第116行：`from ._type_aliases import allTypes, sctypeDict, sctypes`
- `sctypeDict`：包含所有已注册数值类型（含别名）的字典
- `sctypes`：按类别组织的类型集合
- `allTypes`：以'generic'为根的所有类型字典

### F-037：genericTypeRank类型提升顺序

`numerictypes.py` 第121-125行定义了类型排名（用于类型提升）：
```python
genericTypeRank = ['bool', 'int8', 'uint8', 'int16', 'uint16',
                   'int32', 'uint32', 'int64', 'uint64',
                   'float16', 'float32', 'float64', 'float96', 'float128',
                   'complex64', 'complex128', 'complex192', 'complex256',
                   'object']
```

### F-038：dtype的字符串表示规则

`_dtype.py` 第32-40行 `__str__` 函数：
- 有fields（结构化dtype）→ 调用 `_struct_str`
- 有subdtype（子数组dtype）→ 调用 `_subarray_str`
- flexible类型或非本机字节序 → 使用 `dtype.str`（如'<f8'）
- 其他 → 使用 `dtype.name`（如'float64'）

### F-039：dtype的repr格式

`_dtype.py` 第43-47行：
```python
def __repr__(dtype):
    arg_str = _construction_repr(dtype, include_align=False)
    if dtype.isalignedstruct:
        arg_str = arg_str + ", align=True"
    return f"dtype({arg_str})"
```

### F-040：dtype构造repr中的类型字符串

`_dtype.py` 第101-155行 `_scalar_str` 函数定义了各类型的构造字符串：
- bool → `'bool'`（短格式`'?'`）
- object → `'O'`
- bytes → `'S{n}'`（n为itemsize），unsized为`'S'`
- str → `'{byteorder}U{n}'`（n为itemsize//4），unsized为`'{byteorder}U'`
- datetime64 → `'{byteorder}M8{unit}'`
- timedelta64 → `'{byteorder}m8{unit}'`
- void → `'V{n}'`，unsized为`'V'`
- 数值内建类型 → 类型名（如`'float64'`、`'int32'`）

### F-041：ndarray标志位常量

`ndarraytypes.h` 第917-1014行定义了数组标志位：
- `NPY_ARRAY_C_CONTIGUOUS` = 0x0001：C顺序（行优先）连续
- `NPY_ARRAY_F_CONTIGUOUS` = 0x0002：Fortran顺序（列优先）连续
- `NPY_ARRAY_OWNDATA` = 0x0004：数组拥有自己的数据内存
- `NPY_ARRAY_ALIGNED` = 0x0100：数据适当对齐
- `NPY_ARRAY_WRITEABLE` = 0x0400：数组可写
- `NPY_ARRAY_WRITEBACKIFCOPY` = 0x2000：写回副本

第930-932行注释说明：0维数组同时是C_CONTIGUOUS和F_CONTIGUOUS；1维数组如果是C_CONTIGUOUS则也是F_CONTIGUOUS；多维数组可以同时是C_CONTIGUOUS和F_CONTIGUOUS（当所有维度的stride一致时）。

### F-042：复合标志位宏

`ndarraytypes.h` 第1028-1055行：
- `NPY_ARRAY_BEHAVED` = ALIGNED | WRITEABLE
- `NPY_ARRAY_CARRAY` = C_CONTIGUOUS | BEHAVED
- `NPY_ARRAY_FARRAY` = F_CONTIGUOUS | BEHAVED
- `NPY_ARRAY_UPDATE_ALL` = C_CONTIGUOUS | F_CONTIGUOUS | ALIGNED

### F-043：StringDType导入

`numerictypes.py` 第84行：`from ._multiarray_umath import StringDType`，这是NumPy 2.0引入的可变长度字符串dtype。

## 相关概念

- [dtype数据类型系统](../concepts/02-dtype-system.md)
- [ndarray多维数组](../concepts/01-ndarray.md)
- [NumPy简介](../concepts/00-introduction.md)
