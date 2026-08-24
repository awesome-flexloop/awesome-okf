---
okf_version: "0.2"
type: concept
title: NumPy 简介
description: NumPy是Python科学计算的基础库，提供N维数组对象ndarray、广播机制、ufunc通用函数、线性代数/傅里叶/随机数等核心能力
tags: [numpy, ndarray, scientific-computing, array]
generated: { by: reference_agent/trae-glm, at: 2026-08-22T14:15:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T14:30:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: numpy-core
    resource: /references/core-init.md
    title: NumPy 核心初始化源码
  - id: numpy-init
    resource: external/libs/python/NumPy/numpy/numpy/__init__.py
    title: NumPy 包入口
---

# NumPy 简介

NumPy（Numerical Python）是 Python 科学计算生态的**基础底座库**，采用 BSD-3-Clause 许可证开源发布。它提供了高性能的 N 维数组对象 `ndarray`、广播（broadcasting）机制、通用函数（ufunc）系统，以及线性代数、傅里叶变换、随机数生成等核心数值计算能力。[^numpy-core]

## 核心定位

NumPy 的核心价值可以概括为三个关键词：

1. **N维数组（ndarray）**：NumPy 的核心数据结构，同构、固定类型、连续内存布局的多维数组，比 Python 原生 list 快数十倍到数百倍。所有 PyData 生态库（pandas、scikit-learn、matplotlib、PyTorch 等）都构建在 ndarray 之上。

2. **通用函数（ufunc）**：逐元素操作的向量化函数，支持广播、类型提升、输出参数指定、累积/归约等高级特性。ufunc 在 C 层实现循环，避免 Python 解释器开销。

3. **生态基石**：NumPy 定义了 Python 数组计算的事实标准——数组协议（`__array_interface__`/`__array_function__`/`__array_ufunc__`），使得整个 PyData 生态的库可以无缝互操作。

## 模块架构

NumPy 的包结构以 `numpy/_core/` 为核心（C 扩展层），上层是纯 Python 功能模块：

| 模块 | 职责 |
|------|------|
| `numpy._core` | 核心 C 扩展（ndarray、dtype、ufunc、multiarray、umath） |
| `numpy._core.multiarray` | ndarray 构造函数（`array`/`zeros`/`empty`/`arange` 等） |
| `numpy._core.umath` | ufunc 实现（三角函数/算术/比较/逻辑等） |
| `numpy.linalg` | 线性代数（矩阵分解、特征值、求解线性方程组） |
| `numpy.fft` | 快速傅里叶变换 |
| `numpy.random` | 随机数生成（多种分布、BitGenerator、种子管理） |
| `numpy.lib` | 实用函数库（数组操作、I/O、格式转换、索引工具） |
| `numpy.f2py` | Fortran 到 Python 的接口生成器 |
| `numpy.typing` | 类型注解支持（ArrayLike、DTypeLike 等） |

## C 扩展架构

NumPy 的核心计算由单一 C 扩展模块 `_multiarray_umath` 提供。v1.16 之前 `multiarray` 和 `umath` 是两个独立的 C 扩展，之后合并为一个模块以减少导入开销和符号冲突。[^numpy-core]

```
numpy/_core/
├── _multiarray_umath*.so/.pyd   # 合并后的C扩展（核心计算引擎）
├── multiarray.py                 # Python封装：从 _multiarray_umath 导入
├── umath.py                      # Python封装：从 _multiarray_umath 导入
├── _dtype.py                     # dtype 类型系统Python层
├── fromnumeric.py                # ndarray方法的函数版本（np.sum/np.mean等）
├── function_base.py              # 高阶函数（piecewise/diff/gradient等）
├── numerictypes.py               # 数值类型定义（int32/float64等）
└── overrides.py                  # __array_function__ 协议实现
```

## NumPy vs 原生 Python list

| 特性 | NumPy ndarray | Python list |
|------|--------------|-------------|
| **元素类型** | 同构（固定 dtype） | 异构（任意类型） |
| **内存布局** | 连续内存块 | 指针数组（分散堆对象） |
| **运算速度** | C级向量化，快10-100倍 | Python解释器循环 |
| **广播** | ✅ 原生支持 | ❌ 不支持 |
| **切片** | 视图（view），零拷贝 | 浅拷贝（引用复制） |
| **多维支持** | ✅ 原生N维 | ❌ 需嵌套list |
| **数学函数** | ✅ ufunc 全覆盖 | ❌ 需手动循环/列表推导 |
| **内存效率** | 紧凑（dtype大小×元素数） | 每个元素是Python对象（~28字节/int） |

## 生态依赖关系

NumPy 是整个 PyData 生态的底座，其上游/下游关系：

```
Python 解释器
    ↓
NumPy（ndarray + ufunc + dtype）
    ├── pandas（DataFrame/Series，基于ndarray）
    ├── matplotlib（绑图，ndarray作为数据输入）
    ├── scipy（科学计算，基于NumPy数组）
    ├── scikit-learn（机器学习，ndarray为核心数据格式）
    ├── PyTables（HDF5存储，ndarray序列化）
    └── PyTorch/TensorFlow（深度学习，与NumPy互转）
```

## 相关概念

- [ndarray 数据模型](01-ndarray-model.md)
- [dtype 类型系统](02-dtype-system.md)
- [ufunc 通用函数](03-ufunc-system.md)

[^numpy-core]: NumPy 核心初始化源码
