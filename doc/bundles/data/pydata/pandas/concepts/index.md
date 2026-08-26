# pandas 概念文档索引

本目录包含 pandas 核心概念的深度解析文档，建议按顺序阅读。

## 概念文档列表

| 序号 | 文档 | 一句话描述 |
|------|------|-----------|
| 00 | [00-introduction.md](00-introduction.md) | pandas 简介：DataFrame/Series 核心数据结构、BSD 许可证、基于 NumPy 构建、Cython 加速核心、在数据科学生态中的位置 |
| 01 | [01-dataframe-model.md](01-dataframe-model.md) | DataFrame 数据模型：二维表格结构（columns/index/values）、BlockManager 列式内部存储、丰富的数据类型系统、Index 对象体系 |
| 02 | [02-series-index.md](02-series-index.md) | Series 与 Index：Series 一维带标签数组、Index 类型层次（RangeIndex/MultiIndex/DatetimeIndex 等）、索引对齐机制 |
| 03 | [03-groupby-aggregation.md](03-groupby-aggregation.md) | GroupBy 机制：split-apply-combine 范式、GroupBy 对象懒执行、聚合/转换/过滤三种模式、Cython 优化的聚合内核 |

## 阅读路线

```
入门路线:  00-introduction → 01-dataframe-model → 02-series-index → 03-groupby-aggregation
              ↓                    ↓                    ↓                    ↓
         了解 pandas 全貌     理解数据存储模型     掌握标签与对齐       掌握分组聚合
```

阅读完概念文档后，建议通过 [examples/](../examples/basic-dataframe-ops.md) 中的代码示例进行实践，并参考 [references/](../references/core-init.md) 中的源码分析深入理解实现细节。

```{toctree}
:maxdepth: 7

00-introduction
01-dataframe-model
02-series-index
03-groupby-aggregation
```
