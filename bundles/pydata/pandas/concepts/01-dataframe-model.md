---
okf_version: "0.2"
type: concept
title: DataFrame 数据模型
description: 深入解析 DataFrame 的二维表格结构、columns/index/values 三要素、BlockManager 列式存储引擎、数据类型系统与 Index 体系。
tags: [pandas, DataFrame, BlockManager, 数据模型, 列式存储, 内部表示]
generated: { by: reference_agent/trae-glm, at: 2026-08-22T15:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T15:30:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: dataframe-source
    resource: pandas/core/frame.py
    title: DataFrame 实现
  - id: blockmanager-source
    resource: pandas/core/internals/managers.py
    title: BlockManager 实现
  - id: blocks-source
    resource: pandas/core/internals/blocks.py
    title: 数据块 Block 实现
  - id: generic-source
    resource: pandas/core/generic.py
    title: NDFrame 抽象基类
---

# DataFrame 数据模型

## 类继承关系

DataFrame 在源码中定义于 `pandas/core/frame.py`，类声明为：

```python
class DataFrame(NDFrame, OpsMixin):
    _typ = "dataframe"
    _mgr: BlockManager
    __pandas_priority__ = 4000
```

继承链：

```
OpsMixin          PandasObject
    │                  │
    └──── NDFrame ─────┘
              │
         DataFrame
```

- `NDFrame`（`core/generic.py`）：N 维帧的抽象基类，提供 DataFrame 和 Series 共享的大量功能（索引、运算、统计、IO 等）
- `OpsMixin`（`core/arraylike.py`）：运算符重载 mixin，实现 `+`, `-`, `*`, `/`, `==` 等算术和比较运算
- `_mgr: BlockManager`：类型注解明确指出内部存储管理器为 BlockManager

## 二维表格的三要素

DataFrame 是一个二维带标签数据结构，包含三个核心组件：

### 1. index（行标签）

- 类型：`Index` 及其子类（RangeIndex 为默认）
- 默认值：`RangeIndex(0, 1, 2, ..., n)`，由 `core/indexes/api.py` 中的 `default_index(n)` 函数生成
- 通过 `.index` 属性访问
- 行标签用于数据对齐、查找和选择

### 2. columns（列标签）

- 类型：`Index`（通常是普通 Index 或 RangeIndex）
- 通过 `.columns` 属性访问
- 列标签是"字典键"，选择单个列返回 Series
- `_internal_names_set = {"columns", "index"}` 将这两个属性标记为内部名称

### 3. values（数据值）

- 不在用户面前直接暴露为简单 ndarray，而是由 `_mgr`（BlockManager）管理
- `.values` 属性返回 NumPy ndarray（可能涉及数据拷贝和类型转换）
- `.to_numpy()` 方法提供更可控的 ndarray 转换

## BlockManager：列式内部存储

DataFrame 并非简单地以二维 NumPy 数组存储数据，而是使用 **BlockManager**（块管理器）进行列式存储。

### 为什么用 BlockManager？

DataFrame 的核心设计约束是：**不同列可以有不同的数据类型**（heterogeneous）。一个二维 NumPy 数组要求所有元素类型相同，无法满足这一需求。BlockManager 通过将同类型的列组织为连续内存块来解决这个问题。

### BlockManager 架构

定义于 `pandas/core/internals/managers.py`：

```python
class BlockManager(libinternals.BlockManager, BaseBlockManager):
```

BlockManager 继承自：
- `libinternals.BlockManager`：Cython 层的 BlockManager（`_libs/internals.pyx`），提供核心存储和操作
- `BaseBlockManager`：Python 层的基类，提供高级 API

核心组成：

| 属性 | 类型 | 说明 |
|------|------|------|
| `blocks` | `tuple[Block, ...]` | 数据块元组，每个块是同类型的连续数据 |
| `axes` | `list[Index, Index]` | 两个轴：[index, columns] |
| `shape` | `tuple[int, int]` | 形状 (n_rows, n_cols) |

### Block（数据块）

定义于 `pandas/core/internals/blocks.py`：

```python
class Block:
    values: np.ndarray | ExtensionArray
    mgr_locs: BlockPlacement  # 列位置
```

关键 Block 类型：

| Block 类型 | 存储内容 | 底层数组类型 |
|------------|----------|-------------|
| `NumpyBlock` | 通用 NumPy 数据（float64, int64 等） | `np.ndarray` |
| `DatetimeLikeBlock` | datetime64/timedelta64 数据 | `DatetimeArray`/`TimedeltaArray` |
| `CategoricalBlock` | 分类数据 | `Categorical` |
| `ObjectBlock` | Python 对象类型 | `np.ndarray` (dtype=object) |
| `ExtensionBlock` | 扩展类型（StringDtype, BooleanDtype 等） | `ExtensionArray` 子类 |

### 存储示例

假设一个 DataFrame：

```python
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],     # object/string
    "age": [25, 30, 35],                     # int64
    "score": [92.5, 87.0, 95.3],             # float64
    "grade": ["A", "B", "A"],                # object/string
})
```

内部 Block 布局大致为：

```
Block 0 (ObjectBlock/NumpyBlock): columns [0, 3]  → values 是 2×3 的 object 数组
Block 1 (NumpyBlock):           columns [1]     → values 是 1×3 的 int64 数组
Block 2 (NumpyBlock):           columns [2]     → values 是 1×3 的 float64 数组
```

同类型的连续列（或被操作后合并的同类型列）会被组织在同一个 Block 中。这也是为什么添加列时可能触发 Block 合并或分裂。

### BlockManager  vs  二维数组

| 特性 | BlockManager | 二维 ndarray |
|------|-------------|-------------|
| 类型异构 | ✅ 支持 | ❌ 必须同类型 |
| 列式操作 | ✅ 高效（整列访问） | 行优先/列优先取决于 order |
| 类型提升 | ✅ 按块提升 | 全局提升 |
| 内存布局 | 同类型列连续存储 | 所有数据连续 |
| 向量化运算 | ✅ 按块执行 | ✅ 全局执行 |

## 数据类型系统

pandas 拥有丰富的 dtype 体系，远超 NumPy 的类型集合。

### NumPy 原生类型

- 整数：`int8`, `int16`, `int32`, `int64`, `uint8`...`uint64`
- 浮点：`float32`, `float64`
- 布尔：`bool`
- 对象：`object`
- 时间：`datetime64[ns]`, `timedelta64[ns]`

### pandas 扩展类型（ExtensionDtype）

定义于 `pandas/core/dtypes/dtypes.py` 和 `pandas/core/arrays/`：

| Dtype 类 | 类型名 | 用途 | 底层 Array |
|----------|--------|------|-----------|
| `Int8Dtype`~`Int64Dtype` | `Int8`~`Int64` | 可空整数 | `IntegerArray` (masked) |
| `UInt8Dtype`~`UInt64Dtype` | `UInt8`~`UInt64` | 可空无符号整数 | `IntegerArray` |
| `Float32Dtype`, `Float64Dtype` | `Float32`, `Float64` | 可空浮点 | `FloatingArray` (masked) |
| `BooleanDtype` | `boolean` | 可空布尔 | `BooleanArray` (masked) |
| `StringDtype` | `string` | 字符串类型 | `StringArray` / `ArrowStringArray` |
| `CategoricalDtype` | `category` | 分类/枚举类型 | `Categorical` |
| `DatetimeTZDtype` | `datetime64[ns, tz]` | 带时区时间戳 | `DatetimeArray` |
| `PeriodDtype` | `period[freq]` | 时间段 | `PeriodArray` |
| `IntervalDtype` | `interval` | 区间 | `IntervalArray` |
| `SparseDtype` | `Sparse` | 稀疏数据 | `SparseArray` |
| `ArrowDtype` | `arrow[type]` | Apache Arrow 后端 | `ArrowExtensionArray` |

这些扩展类型都继承自 `ExtensionDtype`，对应的数组继承自 `ExtensionArray`，通过 `ExtensionBlock` 存储在 BlockManager 中。

### 缺失值表示

| 数据类型 | 缺失值标记 |
|----------|-----------|
| float64 | `np.nan` |
| datetime64[ns] | `NaT` (Not-a-Time) |
| timedelta64[ns] | `NaT` |
| object | `np.nan` 或 `None` |
| 可空整数/布尔/浮点 | `pd.NA` |
| string | `pd.NA` |
| Categorical | `np.nan` 或 `pd.NA` |
| Interval | `pd.NA` |

`NA` 是一个 `NAType` 单例，定义于 `pandas/_libs/missing.pyx`，在所有扩展类型中统一表示缺失值。

## Index 对象体系

Index 是 pandas 标签系统的核心，在 DataFrame 中同时作为行标签（index）和列标签（columns）。

```
Index (base.py)
├── RangeIndex (range.py)      — 整数范围索引，默认索引
├── CategoricalIndex (category.py) — 分类索引
├── IntervalIndex (interval.py)   — 区间索引
├── MultiIndex (multi.py)         — 多级/层次索引
├── DatetimeIndex (datetimes.py)  — 时间戳索引
├── TimedeltaIndex (timedeltas.py)— 时间差索引
└── PeriodIndex (period.py)       — 时间段索引
```

Index 的核心特性：
- **不可变性**：Index 对象创建后不可修改，保证数据安全
- **有序**：维持标签的插入/排序顺序
- **类集合操作**：支持 `union`, `intersection`, `difference`, `symmetric_difference`
- **哈希查找**：底层使用 `_libs/hashtable.pyx` 实现 O(1) 标签查找

详见 [02-series-index.md](02-series-index.md)。

## DataFrame 构造与内部流程

DataFrame 构造函数接受多种输入类型（在源码 `_HANDLED_TYPES = (Series, Index, ExtensionArray, np.ndarray)` 中声明）：

1. **dict 输入**：key 为列名，value 为数组/Series/常量/列表
   - 列顺序遵循字典插入顺序
   - 若 value 是 Series，按其 index 对齐
2. **ndarray 输入**：二维 NumPy 数组，需指定 columns
3. **Series 输入**：单个 Series，构造为单列 DataFrame
4. **dataclass 输入**：Python dataclass 实例列表
5. **另一个 DataFrame**：拷贝或引用

构造过程内部会：
1. 对输入数据进行 `sanitize_array` 处理
2. 通过 `init_dict`/`init_ndarray` 等内部方法创建数据块
3. 使用 `BlockManager` 组织 Block 和 axes
4. 设置 `_mgr` 属性

## 相关概念

- [pandas 简介](00-introduction.md)
- [Series 与 Index](02-series-index.md)
- [GroupBy 机制](03-groupby-aggregation.md)
- [核心初始化源码分析](../references/core-init.md)
- [基础操作示例](../examples/basic-dataframe-ops.md)
