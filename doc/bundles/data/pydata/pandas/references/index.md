# pandas 信源登记簿（References Index）

本页登记本知识包中所有引用文档及其对应的源码信源。

## 信源文档列表

| 文档 | 信源 ID | 源码路径（相对 pandas/pandas/） | 信源标题 |
|------|---------|-------------------------------|----------|
| [core-init.md](core-init.md) | `pandas-init` | `__init__.py` | pandas 包初始化文件 |
| [core-init.md](core-init.md) | `pandas-core-api` | `core/api.py` | pandas 核心 API 导出 |
| [core-init.md](core-init.md) | `pandas-compat` | `compat/__init__.py` | pandas 兼容性层 |
| [core-init.md](core-init.md) | `pandas-config` | `_config/config.py` | pandas 配置系统 |
| [core-init.md](core-init.md) | `pandas-io-api` | `io/api.py` | pandas IO API 导出 |
| [core-init.md](core-init.md) | `pandas-reshape-api` | `core/reshape/api.py` | pandas 变形/合并 API |

## 核心源码模块索引

以下是 pandas 核心源码模块及其职责概览，供深入学习时参考：

| 模块路径 | 主要职责 | 关键符号 |
|----------|----------|----------|
| `__init__.py` | 包初始化，公共 API 导出 | `DataFrame`, `Series`, `read_csv`, `concat` |
| `core/frame.py` | DataFrame 二维表格实现 | `class DataFrame` |
| `core/series.py` | Series 一维带标签数组实现 | `class Series` |
| `core/generic.py` | NDFrame 抽象基类 | `class NDFrame` |
| `core/base.py` | 基础 Mixin 类 | `IndexOpsMixin`, `PandasObject` |
| `core/indexes/base.py` | Index 基类 | `class Index`, `ensure_index` |
| `core/indexes/range.py` | RangeIndex 实现 | `class RangeIndex` |
| `core/indexes/multi.py` | MultiIndex 多级索引 | `class MultiIndex` |
| `core/indexes/datetimes.py` | DatetimeIndex 时间索引 | `class DatetimeIndex`, `date_range` |
| `core/indexes/timedeltas.py` | TimedeltaIndex | `class TimedeltaIndex`, `timedelta_range` |
| `core/indexes/period.py` | PeriodIndex 周期索引 | `class PeriodIndex`, `period_range` |
| `core/indexes/category.py` | CategoricalIndex | `class CategoricalIndex` |
| `core/indexes/interval.py` | IntervalIndex 区间索引 | `class IntervalIndex`, `interval_range` |
| `core/groupby/groupby.py` | GroupBy 基类 | `class GroupBy` |
| `core/groupby/generic.py` | SeriesGroupBy/DataFrameGroupBy | `class DataFrameGroupBy`, `class SeriesGroupBy` |
| `core/groupby/grouper.py` | 分组键规范 | `class Grouper` |
| `core/internals/managers.py` | BlockManager 内部存储 | `class BlockManager` |
| `core/internals/blocks.py` | 数据块抽象 | `class Block`, `NumpyBlock` |
| `core/dtypes/common.py` | 类型判断工具 | `is_numeric_dtype`, `is_datetime64_any_dtype` |
| `core/dtypes/dtypes.py` | Dtype 类定义 | `CategoricalDtype`, `DatetimeTZDtype`, `StringDtype` |
| `core/reshape/merge.py` | 合并连接 | `merge` |
| `core/reshape/pivot.py` | 透视表 | `pivot_table` |
| `core/reshape/concat.py` | 拼接 | `concat` |
| `io/parsers/readers.py` | CSV 解析 | `read_csv` |
| `_libs/` | Cython C 扩展 | `algos`, `hashtable`, `lib`, `groupby`, `tslibs/` |

## 源码版本信息

- **仓库路径**: `external/libs/python/pandas/pandas/`
- **许可证**: BSD 3-Clause（见 `LICENSE` 文件）
- **构建系统**: Meson（`meson.build`）
- **C 扩展目录**: `pandas/_libs/`（.pyx 文件需编译为 .so/.pyd）

```{toctree}
:maxdepth: 7

core-init
```
