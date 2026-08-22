---
okf_version: "0.2"
type: concept
title: pandas 简介
description: pandas 是 Python 生态中最核心的数据分析库，提供 DataFrame/Series 两大带标签数据结构，基于 NumPy 构建并以 Cython 加速核心运算。
tags: [pandas, 入门, 数据结构, BSD, NumPy, Cython]
generated: { by: reference_agent/trae-glm, at: 2026-08-22T15:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T15:30:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: pandas-init
    resource: pandas/__init__.py
    title: pandas 包初始化文件
  - id: pandas-readme
    resource: README.md
    title: pandas README
  - id: pandas-license
    resource: LICENSE
    title: pandas 许可证
---

# pandas 简介

## 什么是 pandas

**pandas** 是一个开源的、BSD 许可的 Python 数据分析与处理库。它的名称来源于"panel data"（面板数据），这是计量经济学中描述多维结构化数据集的术语。

pandas 的官方定位在 `__init__.py` 的模块文档字符串中表述为：

> **pandas** is a Python package providing fast, flexible, and expressive data structures designed to make working with "relational" or "labeled" data both easy and intuitive. It aims to be the fundamental high-level building block for doing practical, **real world** data analysis in Python.

核心设计目标：让处理"关系型"或"带标签"数据变得快速、灵活且直观。

## 两大核心数据结构

pandas 的核心围绕两个数据结构构建：

### DataFrame（二维表格）

- 定义位置：`pandas/core/frame.py`，类声明为 `class DataFrame(NDFrame, OpsMixin)`
- 二维、大小可变、**类型可异质**（heterogeneous）的表格型数据结构
- 同时拥有行标签（index）和列标签（columns）
- 可视为"Series 对象的字典式容器"
- 算术运算在行标签和列标签上自动对齐
- `__pandas_priority__ = 4000`，优先级高于 Series 和 Index

### Series（一维数组）

- 定义位置：`pandas/core/series.py`，类声明为 `class Series(base.IndexOpsMixin, NDFrame)`
- 一维带标签数组，标签不需要唯一但必须可哈希
- 支持整数位置索引和标签索引
- 统计方法自动排除缺失数据（NaN）
- Series 之间的运算按索引对齐，结果索引为两索引的有序并集

### Index（索引）

- 定义位置：`pandas/core/indexes/base.py`
- 不可变的有序序列，用于轴标签和对齐
- 拥有丰富的子类体系（详见 [02-series-index.md](02-series-index.md)）

## 技术基础

### 基于 NumPy 构建

pandas 的数值运算底层依赖 NumPy：

- DataFrame/Series 的 `values` 属性返回 NumPy `ndarray`
- `numpy` 是 pandas 的两个硬依赖之一（另一个是 `dateutil`）
- 导入时首先检查 numpy 是否可用，缺失则直接抛出 `ImportError`
- 数据块（Block）中 NumpyBlock 直接持有 NumPy 数组

### Cython 加速核心

pandas 的性能关键路径使用 Cython（`.pyx` 文件）编写，编译为 C 扩展：

| Cython 模块 | 职责 |
|-------------|------|
| `_libs/algos.pyx` | 排序、分组、唯一值、isin 等核心算法 |
| `_libs/hashtable.pyx` | 哈希表实现，支撑 Index 的 O(1) 查找 |
| `_libs/groupby.pyx` | GroupBy 聚合的 Cython 优化 |
| `_libs/lib.pyx` | 类型推断、缺失值检查等底层工具 |
| `_libs/join.pyx` | 连接/合并算法 |
| `_libs/index.pyx` | Index 的底层操作 |
| `_libs/internals.pyx` | BlockManager 内部操作 |
| `_libs/tslibs/` | 时间序列处理（日历、解析、时区等） |
| `_libs/window/` | 滚动窗口计算 |

如果 C 扩展未正确编译，pandas 在导入时会检测到并给出明确的错误提示和编译命令。

### 可选依赖

pandas 的硬依赖仅为 `numpy` 和 `dateutil`（`python-dateutil`）。其他功能按需加载可选依赖：

- `numexpr` — 加速 `pd.eval()` 表达式求值
- `bottleneck` — 加速 NaN 友好的统计函数
- `pyarrow` — Arrow 后端支持和 Parquet/Feather/ORC 读写
- `openpyxl`/`xlrd` — Excel 文件读写
- `SQLAlchemy` — 数据库连接
- `matplotlib` — 绘图功能
- `numba` — JIT 编译的 apply 函数
- `pytz`/`zoneinfo` — 时区支持

## 许可证

pandas 使用 **BSD 3-Clause License**（BSD 许可证），这是一种宽松的开源许可证：

- ✅ 允许商业使用
- ✅ 允许修改分发
- ✅ 允许私有使用
- ⚠️ 必须保留版权声明和许可文本
- ⚠️ 不得使用项目作者名字做背书

许可证文件位于源码根目录 `LICENSE`，第三方依赖的许可证在 `LICENSES/` 目录下逐一列出（包括 NUMPY_LICENSE、DATEUTIL_LICENSE 等）。

## pandas 在数据科学生态中的位置

```
┌─────────────────────────────────────────────────────────┐
│                    应用与可视化层                         │
│   Jupyter · Matplotlib · Seaborn · Plotly · Streamlit   │
├─────────────────────────────────────────────────────────┤
│                    数据分析与建模层                       │
│   pandas ── statsmodels · scikit-learn · SciPy          │
├─────────────────────────────────────────────────────────┤
│                    数值计算基础层                         │
│   NumPy · Numba · Cython                                │
├─────────────────────────────────────────────────────────┤
│                    数据存储与 IO                          │
│   CSV/Excel/Parquet · SQL · HDF5 · Arrow · S3           │
└─────────────────────────────────────────────────────────┘
```

pandas 在 Python 数据科学生态中处于**核心枢纽**位置：

1. **向下**依托 NumPy 提供高效的数值数组运算
2. **向上**为 scikit-learn（机器学习）、statsmodels（统计建模）、Matplotlib/Seaborn（可视化）等库提供标准数据输入格式
3. **向外**通过丰富的 IO 模块连接各种数据源
4. **自身**提供数据清洗、转换、聚合、透视、时间序列处理等一站式功能

典型工作流：**数据加载 → 清洗/转换（pandas）→ 建模（sklearn/statsmodels）→ 可视化（matplotlib/seaborn）**

## pandas 的核心特性

根据 `__init__.py` 文档字符串，pandas 的主要特性包括：

- **缺失数据处理**：浮点和非浮点类型都能便捷处理缺失值
- **大小可变性**：DataFrame 支持列的插入和删除
- **自动/显式数据对齐**：运算时按标签自动对齐，也可显式对齐到标签集
- **强大的 GroupBy**：split-apply-combine 范式，支持聚合和变换
- **智能标签切片**：灵活的花式索引、子集选择
- **直观的合并连接**：类 SQL 的 merge/join 操作
- **灵活的变形透视**：reshape 和 pivot 功能
- **层次化标签**：MultiIndex 支持多级索引
- **健壮的 IO 工具**：CSV、Excel、数据库、HDF5 等格式
- **时间序列功能**：日期范围生成、频率转换、移动窗口统计、日期偏移

## 相关概念

- [DataFrame 数据模型](01-dataframe-model.md)
- [Series 与 Index](02-series-index.md)
- [GroupBy 机制](03-groupby-aggregation.md)
- [核心初始化源码分析](../references/core-init.md)
- [基础操作示例](../examples/basic-dataframe-ops.md)
