---
okf_version: "0.2"
type: concept
title: Series 与 Index
description: Series 是一维带标签数组，Index 是不可变标签序列；详解 Index 类型层次（RangeIndex/MultiIndex/DatetimeIndex 等）与索引对齐机制。
tags: [pandas, Series, Index, 索引对齐, RangeIndex, MultiIndex, DatetimeIndex]
generated: { by: reference_agent/trae-glm, at: 2026-08-22T15:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T15:30:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: series-source
    resource: pandas/core/series.py
    title: Series 实现
  - id: index-base-source
    resource: pandas/core/indexes/base.py
    title: Index 基类实现
  - id: index-range-source
    resource: pandas/core/indexes/range.py
    title: RangeIndex 实现
  - id: index-multi-source
    resource: pandas/core/indexes/multi.py
    title: MultiIndex 实现
  - id: index-datetimes-source
    resource: pandas/core/indexes/datetimes.py
    title: DatetimeIndex 实现
  - id: indexes-api
    resource: pandas/core/indexes/api.py
    title: Indexes API 导出
---

# Series 与 Index

## Series：一维带标签数组

Series 定义于 `pandas/core/series.py`：

```python
class Series(base.IndexOpsMixin, NDFrame):
    _typ = "series"
    _HANDLED_TYPES = (Index, ExtensionArray, np.ndarray)
    _name: Hashable
    _metadata: list[str] = ["_name"]
```

### Series 的构造

```python
pd.Series(data=None, index=None, dtype=None, name=None, copy=None)
```

参数说明：

| 参数 | 说明 |
|------|------|
| `data` | array-like、Iterable、dict 或标量值 |
| `index` | 轴标签，默认为 `RangeIndex(0, 1, ..., n)`；若 data 是 dict 且 index 为 None，使用字典键 |
| `dtype` | 数据类型，None 则自动推断 |
| `name` | Series 名称，用于 DataFrame 列标识和结果对齐 |
| `copy` | 是否拷贝数据，对 ndarray 输入默认 copy=True |

### Series 的核心特性

1. **标签索引优先**：`ser["a"]` 按标签查找，`ser.iloc[0]` 按位置查找
2. **自动对齐**：两个 Series 运算时，按 index 标签对齐，不匹配的标签结果为 NaN
3. **缺失值自动排除**：统计方法（`mean()`, `sum()`, `std()` 等）默认跳过 NaN
4. **名称属性**：`.name` 属性用于标识 Series，在 DataFrame 操作中保留列名
5. **字典式行为**：支持 `in` 操作符检查标签是否存在，支持 `.get()` 方法
6. **NumPy 互操作**：通过 `.values` 或 `.to_numpy()` 转为 ndarray，也可直接传入接受 ndarray 的 NumPy 函数

### Series 与 DataFrame 的关系

- DataFrame 的每一列是一个 Series，它们共享同一个 index
- `df["col"]` 返回 Series
- `df["new_col"] = series` 赋值时按 index 对齐
- `ser.to_frame(name="col")` 将 Series 转为单列 DataFrame
- DataFrame 在二元运算中优先级高于 Series（`__pandas_priority__`：DataFrame=4000，Series=3000）

## Index：不可变标签序列

Index 定义于 `pandas/core/indexes/base.py`，是所有索引类型的基类：

```python
class Index(metaclass=…):
    _typ = "index"
```

### Index 的核心属性

| 属性 | 说明 |
|------|------|
| `values` | 返回底层数组 |
| `dtype` | 数据类型 |
| `name` | 索引名称（DataFrame 中 index.name 和 columns.name） |
| `shape` | 形状 |
| `is_monotonic_increasing` | 是否单调递增 |
| `is_monotonic_decreasing` | 是否单调递减 |
| `is_unique` | 标签是否唯一 |
| `has_duplicates` | 是否有重复标签 |
| `nlevels` | 层级数（普通 Index 为 1，MultiIndex 为多级） |

### Index 的不可变性

Index 对象创建后不可修改，这是 pandas 数据安全的重要保障：

- 不能通过 `idx[0] = new_val` 修改标签
- 任何"修改"操作（如 `set_names`, `sort_values`）都返回新的 Index 对象
- 不可变性使得 Index 可以安全地在多个 DataFrame/Series 间共享

### Index 的核心方法

| 方法 | 功能 |
|------|------|
| `get_loc(key)` | 返回标签对应的位置（整数或切片/布尔数组） |
| `get_indexer(target)` | 返回 target 在当前 index 中的位置数组，未找到为 -1 |
| `union(other)` | 并集 |
| `intersection(other)` | 交集 |
| `difference(other)` | 差集 |
| `symmetric_difference(other)` | 对称差集 |
| `isin(values)` | 检查标签是否在 values 中 |
| `sort_values()` | 排序返回新 Index |
| `map(mapper)` | 应用映射函数 |
| `rename(name)` | 重命名，返回新 Index |
| `astype(dtype)` | 类型转换 |
| `drop(labels)` | 删除指定标签 |
| `insert(loc, item)` | 在指定位置插入标签 |
| `append(other)` | 拼接另一个 Index |

底层查找使用 `_libs/hashtable.pyx` 实现的哈希表，`get_loc` 对唯一索引提供 O(1) 查找。

## Index 类型层次

pandas 提供丰富的 Index 子类以适应不同数据类型和使用场景：

```
Index
├── NumericIndex / Index (dtype=int64/float64/object)  — 通用索引
├── RangeIndex                                          — 整数范围
├── CategoricalIndex                                    — 分类标签
├── IntervalIndex                                       — 区间标签
├── MultiIndex                                          — 多级层次标签
├── DatetimeIndex                                       — 时间戳
│   └── DatetimeIndex (tz-aware / tz-naive)
├── TimedeltaIndex                                      — 时间差
└── PeriodIndex                                         — 时间段
```

### RangeIndex

定义于 `pandas/core/indexes/range.py`。

- **用途**：默认行索引，表示整数范围 `[start, stop)`，步长为 step
- **内存高效**：不存储实际数组，仅保存 `_start`, `_stop`, `_step` 三个整数
- **自动降级**：当进行可能产生非连续整数的操作时，自动转换为 Int64Index/Index
- **构造**：`pd.RangeIndex(start=0, stop=10, step=1)` 或直接 `range(10)`

```python
# 默认 DataFrame 的 index 就是 RangeIndex
df = pd.DataFrame({"a": [1,2,3]})
type(df.index)  # <class 'pandas.core.indexes.range.RangeIndex'>
```

### MultiIndex

定义于 `pandas/core/indexes/multi.py`。

- **用途**：层次化/多级索引，在单个轴上存储多层标签
- **典型场景**：多维数据透视表、分组聚合结果、面板数据
- **核心属性**：
  - `levels`：各级别的唯一值标签元组
  - `codes`：各级别的整数编码（指向 levels 的位置）
  - `names`：各级别的名称
- **构造方法**：
  - `pd.MultiIndex.from_tuples(tuples)`
  - `pd.MultiIndex.from_arrays(arrays)`
  - `pd.MultiIndex.from_product(iterables)`
  - `pd.MultiIndex.from_frame(df)`
- **索引方式**：
  - `df.loc[("level0_val", "level1_val")]` 元组选择
  - `df.loc[pd.IndexSlice[:, "level1_val"], :]` 使用 `IndexSlice`
  - `df.xs("val", level="level_name")` 横切选择

### DatetimeIndex

定义于 `pandas/core/indexes/datetimes.py`。

- **用途**：时间戳索引，pandas 时间序列功能的核心
- **底层**：基于 `DatetimeArray`（int64 存储纳秒时间戳）
- **时区支持**：`tz` 属性指定时区（None 为 naive，否则为 tz-aware），使用 `DatetimeTZDtype`
- **核心构造函数**：
  - `pd.date_range(start, end, periods, freq)` — 生成固定频率日期范围
  - `pd.bdate_range(...)` — 工作日日期范围
- **频率字符串**：`"D"`(日), `"B"`(工作日), `"H"`(小时), `"T"/"min"`(分钟), `"S"`(秒), `"W"`(周), `"M"`(月末), `"Q"`(季末), `"A"/"Y"`(年末) 等
- **时间属性访问**：通过 `.dt` accessor（对 DatetimeIndex 直接用 `.year`, `.month`, `.day` 等）
- **重采样**：`.resample(freq)` 配合 GroupBy 做时间重采样

### TimedeltaIndex

定义于 `pandas/core/indexes/timedeltas.py`。

- **用途**：时间差/持续时间索引
- **构造**：`pd.timedelta_range(start, end, periods, freq)`
- **底层**：`TimedeltaArray`（int64 存储纳秒）

### PeriodIndex

定义于 `pandas/core/indexes/period.py`。

- **用途**：时间段索引（如"2024年1月"、"2024Q1"）
- **构造**：`pd.period_range(start, end, periods, freq)`
- **底层**：`PeriodArray`（int64 编码 + 频率）

### IntervalIndex

定义于 `pandas/core/indexes/interval.py`。

- **用途**：区间标签（如分箱后的 bins）
- **构造**：`pd.interval_range(start, end, periods, freq)`
- **应用**：`pd.cut()` 和 `pd.qcut()` 返回的分类索引
- **属性**：`.left`, `.right`, `.closed`, `.mid`, `.length`

### CategoricalIndex

定义于 `pandas/core/indexes/category.py`。

- **用途**：基于分类类型的索引，适用于有限且固定的标签集合
- **优势**：内存高效（内部使用整数编码），保持分类顺序
- **底层**：`Categorical`

### IndexSlice

```python
from pandas import IndexSlice as idx
```

`IndexSlice` 是 `pandas/core/indexing.py` 中提供的便捷工具，本质上就是 `slice(None)` 的包装，用于在 MultiIndex 切片中创建更清晰的语法：

```python
# 等价于 df.loc[(slice(None), "val"), :]
df.loc[idx[:, "val"], :]
```

## 索引对齐机制

索引对齐是 pandas 最核心的设计理念之一，也是 pandas 区别于 NumPy 的关键特性。

### 对齐的基本规则

当两个 pandas 对象进行运算时：

1. **Series + Series**：结果 index 为两个 index 的**有序并集**，匹配标签的值参与运算，不匹配的标签结果为 NaN
2. **DataFrame + DataFrame**：同时在 index（行）和 columns（列）上对齐
3. **DataFrame + Series**：Series 的 index 与 DataFrame 的 columns 对齐（按列广播）
4. **DataFrame/Series + 标量**：标量广播到所有元素

### 对齐的实现

对齐操作在 `core/ops/` 和 `core/computation/align.py` 中实现，核心步骤：

1. 通过 `get_objs_combined_axis` （`core/indexes/api.py`）计算结果轴（并集或交集）
2. 使用 `reindex` 将各对象对齐到结果轴
3. 填充缺失值为 NaN
4. 执行实际运算
5. 结果以对齐后的轴构造新对象

### 对齐示例

```python
s1 = pd.Series([1, 2, 3], index=["a", "b", "c"])
s2 = pd.Series([10, 20, 30], index=["b", "c", "d"])

s1 + s2
# a     NaN   (s1 有 a，s2 没有 → 缺失)
# b    12.0   (2 + 10)
# c    23.0   (3 + 20)
# d     NaN   (s2 有 d，s1 没有 → 缺失)
# dtype: float64
```

结果的 index 是 `["a", "b", "c", "d"]`（有序并集），不匹配的标签产生 NaN，且整数类型自动提升为 float64 以容纳 NaN。

### 交集对齐 vs 并集对齐

- **默认**：并集对齐（`join="outer"`），不匹配的标签填充 NaN
- **交集对齐**：`df.add(df2, join="inner")`，仅保留两者共有的标签
- **对齐到指定对象**：`df.add(df2, axis="columns", fill_value=0)`，fill_value 在对齐前填充缺失值

## 相关概念

- [pandas 简介](00-introduction.md)
- [DataFrame 数据模型](01-dataframe-model.md)
- [GroupBy 机制](03-groupby-aggregation.md)
- [核心初始化源码分析](../references/core-init.md)
- [基础操作示例](../examples/basic-dataframe-ops.md)
