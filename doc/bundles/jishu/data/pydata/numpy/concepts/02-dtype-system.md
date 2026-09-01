---
okf_version: "0.2"
type: concept
title: dtype 类型系统
description: NumPy dtype描述数组元素类型（数值/布尔/字符串/复合/日期时间），支持类型提升规则、自定义类型、结构化数组和类型转换
tags: [numpy, dtype, type-system, structured-arrays, type-promotion]
generated: { by: reference_agent/trae-glm, at: 2026-08-22T14:25:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T14:30:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: numpy-dtype
    resource: external/libs/python/NumPy/numpy/numpy/_core/_dtype.py
    title: NumPy dtype Python层
  - id: numpy-numerictypes
    resource: external/libs/python/NumPy/numpy/numpy/_core/numerictypes.py
    title: NumPy 数值类型定义
---

# dtype 类型系统

`dtype`（data type）描述 ndarray 中每个元素的数据类型，决定了元素的字节大小、解释方式、内存对齐。NumPy 提供了丰富的数值类型系统，从1字节布尔到8字节复数全覆盖。

## 数值类型体系

NumPy 的数值类型按**位宽**和**种类**分类：

| 类型 | 位宽 | 说明 | Python等价 |
|------|------|------|-----------|
| `bool_` | 8 | 布尔值（True/False） | `bool` |
| `int8`/`int16`/`int32`/`int64` | 8/16/32/64 | 有符号整数 | `int` |
| `uint8`/`uint16`/`uint32`/`uint64` | 8/16/32/64 | 无符号整数 | - |
| `float16`/`float32`/`float64` | 16/32/64 | 浮点数 | `float` |
| `complex64`/`complex128` | 64/128 | 复数（两个float） | `complex` |
| `datetime64`/`timedelta64` | 64 | 日期时间/时间差 | - |
| `string_`/`bytes_` | 可变 | 字节字符串 | `bytes` |
| `str_`/`unicode_` | 可变 | Unicode字符串 | `str` |
| `object_` | 指针大小 | Python对象指针 | `object` |

默认类型：`int_`（平台相关，通常int64）、`float_`（float64）、`complex_`（complex128）。

## dtype 对象属性

每个 `np.dtype` 对象包含：

```python
dt = np.dtype('float64')
dt.kind        # 'f' — 类型种类（f=float, i=signed int, u=unsigned, b=bool, c=complex...）
dt.type        # <class 'numpy.float64'> — 对应标量类型
dt.itemsize    # 8 — 元素字节大小
dt.name        # 'float64' — 类型名称
dt.str         # '<f8' — 数组协议类型字符串
dt.byteorder   # '=' — 字节序（=本机 | <小端 | >大端）
dt.alignment   # 8 — 对齐要求
dt.fields      # None — 复合类型字段（结构化数组）
dt.subdtype    # None — 子类型（子数组dtype）
```

## 类型提升（Type Promotion）

当不同类型的数组进行运算时，NumPy 按**类型提升规则**确定结果类型：

1. **安全提升**：检查类型是否可以安全转换（`np.can_cast(from, to, casting='safe')`）
2. **提升规则**：遵循 NEP 50（Python 3.14+）或旧规则
3. **通用函数提升**：ufunc 使用 `np.result_type()` 确定输出类型

```python
np.result_type(np.int32, np.float64)  # float64
np.result_type(np.int32, np.int64)    # int64
np.promote_types('int32', 'float32')  # float64

# 类型转换安全级别
np.can_cast(np.int32, np.float64, casting='safe')    # True
np.can_cast(np.float64, np.int32, casting='safe')    # False
```

四种转换模式：`no`（仅相同类型）、`equiv`（仅字节序变化）、`safe`（完全保留精度）、`same_kind`（同种类安全）、`unsafe`（任意转换）。

## 结构化数组（Structured Arrays）

NumPy 支持复合 dtype，类似 C 结构体：

```python
# 定义复合类型
dt = np.dtype([('name', 'U10'), ('age', 'i4'), ('score', 'f8')])
arr = np.array([('Alice', 25, 92.5), ('Bob', 30, 87.0)], dtype=dt)

arr['name']    # 访问name字段 → array(['Alice', 'Bob'], dtype='<U10')
arr[0]         # 第一条记录 → ('Alice', 25, 92.5)
arr[0]['age']  # 25
```

结构化 dtype 的 `fields` 属性返回字典：`{'name': (dtype, offset), 'age': (dtype, offset), ...}`。

## 自定义dtype与扩展

NumPy 支持通过 C API 注册自定义 dtype（如 pandas 的 DatetimeTZDtype）。现代扩展机制使用 `__array_ufunc__` 和 `__array_function__` 协议拦截 NumPy 操作。

## 相关概念

- [NumPy 简介](00-introduction.md)
- ndarray 数据模型
- ufunc 通用函数
