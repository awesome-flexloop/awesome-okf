---
okf_version: "0.2"
type: concept
title: GroupBy 机制
description: 解析 pandas GroupBy 的 split-apply-combine 范式、懒执行设计、聚合/转换/过滤三大操作模式及 Cython 优化的聚合内核实现。
tags: [pandas, GroupBy, split-apply-combine, 聚合, 分组, Cython优化]
generated: { by: reference_agent/trae-glm, at: 2026-08-22T15:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T15:30:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: groupby-source
    resource: pandas/core/groupby/groupby.py
    title: GroupBy 基类实现
  - id: groupby-generic
    resource: pandas/core/groupby/generic.py
    title: DataFrameGroupBy/SeriesGroupBy
  - id: groupby-grouper
    resource: pandas/core/groupby/grouper.py
    title: Grouper 分组规范
  - id: groupby-ops
    resource: pandas/core/groupby/ops.py
    title: GroupBy 操作实现
  - id: libgroupby
    resource: pandas/_libs/groupby.pyx
    title: GroupBy Cython 内核
---

# GroupBy 机制

## Split-Apply-Combine 范式

GroupBy 是 pandas 中最强大也是最常用的数据操作机制之一，其设计遵循 Hadley Wickham 提出的 **split-apply-combine**（拆分-应用-合并）范式：

```
┌─────────────┐
│  原始数据    │  DataFrame / Series
└──────┬──────┘
       │ split（按分组键拆分）
       ▼
┌─────────────┐
│ 分组1: 子集1 │ ──┐
├─────────────┤   │
│ 分组2: 子集2 │   │ apply（对每个组应用函数）
├─────────────┤   │
│ 分组3: 子集3 │   │
└─────────────┘   │
       │          │
       │ combine（合并结果）
       ▼
┌─────────────┐
│  结果数据    │  DataFrame / Series
└─────────────┘
```

源码中 `core/groupby/groupby.py` 的模块 docstring 明确指出：

> Provide the groupby split-apply-combine paradigm. Define the GroupBy class providing the base-class of operations. The SeriesGroupBy and DataFrameGroupBy sub-class (defined in pandas.core.groupby.generic) expose these user-facing objects to provide specific functionality.

## GroupBy 对象的懒执行

`df.groupby(by)` 返回一个 `DataFrameGroupBy`（或 `SeriesGroupBy`）对象，这个对象**本身不包含计算结果**，而是存储了分组所需的所有元信息，等待后续聚合/转换/过滤操作触发实际计算。

### GroupBy 对象的核心属性

| 属性 | 说明 |
|------|------|
| `obj` | 被分组的原始 DataFrame/Series |
| `keys` | 分组键列表 |
| `axis` | 分组轴（0=行，1=列） |
| `level` | 多级索引时指定分组级别 |
| `sort` | 是否对分组键排序（默认 True） |
| `group_keys` | apply 结果是否添加分组键（默认 True） |
| `observed` | Categorical 分组键是否仅显示观测值 |
| `dropna` | 是否丢弃 NA 分组（默认 True） |
| `ngroups` | 分组数量 |
| `groups` | dict，{组名: 组标签位置} |
| `indices` | dict，{组名: 位置数组} |

### 懒执行的优势

1. **链式调用高效**：`df.groupby("a").sum().reset_index()` 中，`groupby()` 本身几乎不做计算，直到 `.sum()` 才触发
2. **可复用 GroupBy 对象**：同一个 GroupBy 对象可以多次调用不同聚合函数
3. **优化空间**：pandas 可以在实际计算前对多个操作进行优化（如 Cython 聚合函数一次遍历多列）

### groups 和 indices 的区别

- `groups` 属性返回 `{组键: Index 标签}` 字典（标签是原始 index 的值）
- `indices` 属性返回 `{组键: np.ndarray 位置数组}` 字典（位置是整数位置）
- 实际内部操作使用 `indices`（位置数组），因为位置数组直接用于 ndarray 索引，性能更高

## 分组键（Grouper）

分组键通过 `Grouper` 类（`core/groupby/grouper.py`）规范化。支持多种分组键类型：

### 1. 列名字符串/列名列表

```python
df.groupby("category")           # 单列分组
df.groupby(["cat1", "cat2"])     # 多列分组（结果为 MultiIndex）
```

### 2. 数组/Series（与原数据等长）

```python
df.groupby(df["category"])       # 直接传入列
df.groupby(bins_array)           # 外部数组分组（如分箱结果）
```

### 3. 字典/Series（映射关系）

```python
mapping = {"a": "group1", "b": "group1", "c": "group2"}
df.groupby(mapping)              # 按映射关系分组
```

### 4. 函数

```python
df.groupby(lambda x: x.dayofweek)  # 按函数返回值分组（作用于 index）
```

### 5. Grouper 对象（高级用法）

```python
# 时间重采样分组
df.groupby(pd.Grouper(key="date", freq="M")).sum()
# 等同于 df.set_index("date").resample("M").sum()

# 多级索引指定级别
df.groupby(pd.Grouper(level="region"))
```

`pd.Grouper` 在 `__init__.py` 中从 `pandas.core.groupby` 导出。

## 三大操作模式

GroupBy 对象支持三类核心操作：**聚合（Aggregation）**、**转换（Transformation）**、**过滤（Filtration）**。

### 1. 聚合（Aggregation）— 每组产生一个标量/行

聚合操作将每个组的数据压缩为单个值（或一行值），结果的行数等于分组数。

#### 内置聚合函数

pandas 为常见统计量提供了优化的聚合方法，这些方法直接调用 Cython 内核：

| 方法 | 功能 | Cython 优化 |
|------|------|:-----------:|
| `sum()` | 求和 | ✅ |
| `mean()` | 均值 | ✅ |
| `median()` | 中位数 | ✅ |
| `std()` | 标准差 | ✅ |
| `var()` | 方差 | ✅ |
| `min()` / `max()` | 最小/最大值 | ✅ |
| `count()` | 非空计数 | ✅ |
| `first()` / `last()` | 首/尾值 | ✅ |
| `nunique()` | 唯一值数量 | ✅ |
| `prod()` | 乘积 | ✅ |
| `size()` | 组大小（含 NaN） | — |
| `describe()` | 汇总统计 | — |
| `sem()` | 标准误 | ✅ |
| `skew()` | 偏度 | ✅ |
| `kurt()` | 峰度 | ✅ |

源码中这些方法通过 `_cython_agg_general` 方法调用 `_libs/groupby.pyx` 中的优化函数。

#### agg() / aggregate() — 灵活聚合

```python
# 单个函数
df.groupby("cat")["value"].agg("mean")
df.groupby("cat")["value"].agg(np.mean)
df.groupby("cat")["value"].agg(lambda x: x.max() - x.min())

# 多个函数
df.groupby("cat")["value"].agg(["mean", "std", "count"])

# 不同列不同聚合
df.groupby("cat").agg({
    "value": "sum",
    "price": ["mean", "max"],
    "name": "first"
})

# 命名聚合（NamedAgg）
df.groupby("cat").agg(
    total=pd.NamedAgg(column="value", aggfunc="sum"),
    avg_price=pd.NamedAgg(column="price", aggfunc="mean"),
)
```

`NamedAgg`（和别名 `NamedFunc`）在 `core/groupby/__init__.py` 中定义，是一个简单的 namedtuple：

```python
class NamedAgg(NamedTuple):
    column: Hashable
    aggfunc: ...
```

### 2. 转换（Transformation）— 每组输出与输入等长

转换操作对每个组应用函数，但返回与原始对象**形状相同**的结果（索引对齐）。

| 方法/操作 | 说明 |
|-----------|------|
| `transform(func)` | 对每个组应用 func，结果与原数据对齐 |
| `filter(func)` | 根据组级条件筛选整个组 |

```python
# 标准化：每个值减去组均值除以组标准差
zscore = lambda x: (x - x.mean()) / x.std()
df.groupby("cat")["value"].transform(zscore)

# 组内填充缺失值
df.groupby("cat")["value"].transform(lambda x: x.fillna(x.mean()))

# 组内排名
df.groupby("cat")["value"].rank()

# 组内平移（shift）和累计（cumsum/cumprod/cummax/cummin）
df.groupby("cat")["value"].cumsum()
```

`transform` 的关键特征：结果的 index 与原始 DataFrame 完全相同，可以直接赋值为新列。

### 3. 过滤（Filter）— 根据组级条件筛选组

`filter(func)` 接受一个返回布尔值的函数，func 的参数是每个组的子 DataFrame，返回 True 的组保留，False 的组被排除。结果是原始 DataFrame 的子集。

```python
# 保留组大小 >= 3 的组
df.groupby("cat").filter(lambda g: len(g) >= 3)

# 保留组均值 > 50 的组
df.groupby("cat").filter(lambda g: g["value"].mean() > 50)
```

注意：`filter` 与布尔索引的区别在于，`filter` 的判断基于**组级聚合条件**，而不是行级条件。

### 4. apply — 通用分组操作

`apply(func)` 是最灵活的 GroupBy 操作，func 接收每个组的子 DataFrame/Series，可以返回任意形状的结果，pandas 负责拼接。

```python
# 每组取前 N 行
df.groupby("cat").apply(lambda g: g.nlargest(3, "value"), include_groups=False)

# 每组应用复杂操作
def summarize(group):
    return pd.Series({
        "total": group["value"].sum(),
        "count": len(group),
        "top_name": group["name"].iloc[0],
    })

df.groupby("cat").apply(summarize, include_groups=False)
```

`include_groups=False`（pandas 2.2+）阻止分组键被自动传入 func。

## Cython 优化的聚合内核

GroupBy 的高性能来自 Cython 层面的优化实现，位于 `pandas/_libs/groupby.pyx`。

### libgroupby 核心功能

源码导入语句：

```python
import pandas._libs.groupby as libgroupby
from pandas._libs.algos import rank_1d
```

Cython 内核提供的关键函数包括：

- 分组求和/均值/方差/标准差/最小值/最大值等的单遍（single-pass）计算
- 使用 khash 哈希表（`_libs/khash.pxd`）实现高效的分组键查找
- 支持 float64, int64, object, datetime64 等多种数据类型
- NaN 感知：聚合时正确跳过/处理缺失值

### 聚合优化的关键技术

1. **预排序/哈希分组**：根据数据类型选择排序法或哈希法进行分组
   - 对于已排序的分组键，使用排序法（更快）
   - 对于未排序的键，使用哈希表法
2. **单遍多聚合**：一次遍历数据同时计算 sum、count、mean 等多个统计量，避免多次遍历
3. **C 级循环**：核心聚合循环在 C 层运行，避免 Python 解释器开销
4. **NaN 跳过**：在 C 层检测并跳过 NaN 值

### 聚合流程

```python
# 在 _cython_agg_general 中大致流程：
1. 通过 _grouper.get_iterator() 获取分组迭代器
2. 获取数据的底层数组（np.ndarray）
3. 根据 dtype 调用 libgroupby 对应的聚合函数
   - libgroupby.group_sum
   - libgroupby.group_mean
   - libgroupby.group_agg（通用）
4. 使用 out_shape 数组接收结果
5. 将结果包装回 Series/DataFrame
```

## GroupBy 的索引输出

分组聚合后，结果的 index 取决于：

- 单键分组：分组键成为结果 index（除非 `as_index=False`）
- 多键分组：分组键组成 MultiIndex
- `as_index=False`：分组键作为普通列保留，index 为 RangeIndex
- `reset_index()`：将 index 中的分组键转回普通列

```python
# 分组键在 index 中
df.groupby("cat")["value"].sum()  # index = ["a", "b", "c"]

# 分组键作为列
df.groupby("cat", as_index=False)["value"].sum()  # columns = ["cat", "value"]
```

## 相关概念

- [pandas 简介](00-introduction.md)
- [DataFrame 数据模型](01-dataframe-model.md)
- [Series 与 Index](02-series-index.md)
- [核心初始化源码分析](../references/core-init.md)
- [基础操作示例](../examples/basic-dataframe-ops.md)
