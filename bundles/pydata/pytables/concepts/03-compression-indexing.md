---
type: concept
title: 压缩与索引
description: PyTables 的 Filters 压缩过滤管道（Blosc/Blosc2/Zlib/BZIP2/LZO、Shuffle/BitShuffle/Fletcher32）与索引系统（完全/部分索引、CSI 分块排序索引、查询优化）
tags: [pytables, compression, filters, blosc, blosc2, shuffle, index, csi, query-optimization]
generated:
  by: reference_agent/trae-glm
  at: 2026-08-22T15:00:00Z
verified:
  by: "process:seven-concepts-v"
  at: 2026-08-22T15:30:00Z
status: stable
stale_after: 2027-12-31
sources:
  - tables/filters.py
  - tables/index.py
  - tables/indexes.py
  - tables/idxutils.py
  - tables/utilsextension.pyx
---

# 压缩与索引

压缩和索引是 PyTables 处理大规模数据时的两大性能支柱。压缩减少磁盘占用和 I/O 量，索引加速条件查询。两者都在 chunk（数据块）级别发挥作用。

## Filters 过滤管道

`Filters` 类定义在 [filters.py:50](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/filters.py#L50)，是一个容器类，保存分块叶子节点（Table、CArray、EArray、VLArray）的 I/O 过滤器配置。过滤器以管道方式应用于每个 chunk：写入时依次编码，读取时反向解码。

### Filters 构造参数

```python
Filters(
    complevel=0,              # 压缩级别 0-9，0 表示不压缩
    complib='zlib',           # 压缩库
    shuffle=True,             # Shuffle 过滤器
    bitshuffle=False,         # BitShuffle 过滤器（Blosc/Blosc2 专属）
    fletcher32=False,         # Fletcher32 校验和
    least_significant_digit=None,  # 量化精度（有损压缩）
)
```

### 支持的压缩库

| 压缩库 | 说明 | 速度 | 压缩比 |
|--------|------|------|--------|
| `zlib` (DEFLATE) | 默认压缩库，通用性最好 | 中等 | 中等 |
| `lzo` | 极快的压缩/解压 | 极快 | 低 |
| `bzip2` | 高压缩比 | 慢 | 高 |
| `blosc` | 元压缩器，内部阻塞+多线程 | 极快 | 中等 |
| `blosc2` | Blosc 升级版，推荐使用 | 极快 | 中高 |

#### Blosc/Blosc2 子压缩器

Blosc 和 Blosc2 是"压缩器的压缩器"（meta-compressor），内部集成多种编解码器。通过 `blosc:codec` 或 `blosc2:codec` 语法指定子压缩器：

| 子压缩器 | 说明 |
|----------|------|
| `blosc:blosclz` / `blosc2:blosclz` | 默认，Blosc 自带，速度最快 |
| `blosc:lz4` / `blosc2:lz4` | LZ4，极速压缩 |
| `blosc:lz4hc` / `blosc2:lz4hc` | LZ4-HC，高压缩比 LZ4 变种 |
| `blosc:zlib` / `blosc2:zlib` | Zlib 内部使用 |
| `blosc:zstd` / `blosc2:zstd` | Zstandard，现代高效压缩 |

可用压缩器列表通过 `blosc_compressor_list()` 和 `blosc2_compressor_list()` 动态查询。若指定的压缩库不可用，发出 `FiltersWarning` 并回退到 zlib。

### Shuffle 与 BitShuffle 过滤器

**Shuffle 过滤器**（HDF5 内置）重排字节顺序：将同一位置的字节聚集在一起，显著提升数值数据的压缩率。例如 `[0x12345678, 0x9ABCDEF0]` 会被重排为 `[0x12,0x9A, 0x34,0xBC, 0x56,0xDE, 0x78,0xF0]`。

**BitShuffle 过滤器**（Blosc/Blosc2 内部）在位级别进行重排，对浮点数据和时序数据效果更好。BitShuffle 与 Shuffle 互斥（同时启用时 BitShuffle 优先，Shuffle 被禁用）。

BitShuffle 只能在 Blosc/Blosc2 内部使用，不能用于其他压缩库。

### Fletcher32 校验和

启用 Fletcher32 后，每个 chunk 存储 32 位校验和，读取时验证数据完整性。检测数据损坏的开销很小。

### least_significant_digit：量化有损压缩

若指定 `least_significant_digit=N`，浮点数将被截断保留 N 位小数精度。配合压缩实现**有损压缩**，对科学数据可大幅减小体积。例如 `least_significant_digit=1` 保留 0.1 精度。量化仅在启用压缩时生效。

### 压缩级别（complevel）

范围 0-9：
- 0 = 不压缩
- 1 = 最快，压缩比最低
- 9 = 最慢，压缩比最高
- 推荐值：Blosc/Blosc2 用 1-5，zlib 用 1-6

### Filters 继承机制

Filters 在节点树中**继承**：
- 文件根组设置默认 filters
- 创建子 Group 时可指定独立 filters，覆盖继承值
- 创建叶子节点时若不指定 filters，继承父 Group 的设置
- 不指定任何 filters 时默认不压缩、不使用过滤器

### 典型用法

```python
import tables as tb

# Blosc2 高速压缩 + Shuffle
filters = tb.Filters(complevel=5, complib='blosc2:zstd', shuffle=True)

# Blosc2 + BitShuffle + 校验和（推荐用于浮点数据）
filters = tb.Filters(complevel=5, complib='blosc2', bitshuffle=True, fletcher32=True)

# Zlib 兼容压缩
filters = tb.Filters(complevel=1, complib='zlib', shuffle=True, fletcher32=True)

# 创建文件时指定根级默认过滤器
h5file = tb.open_file('data.h5', mode='w', filters=filters)
```

### Filters 的打包表示

`Filters._pack()` 将过滤器配置打包为 64 位整数存储；`Filters._unpack(packed)` 反向解包。格式：
- Byte 0：压缩级别
- Byte 1：压缩库 ID
- Byte 2：无参过滤器标志位（shuffle/bitshuffle/fletcher32/rounding）
- Byte 3：least_significant_digit

### Chunk 大小计算

[leaf.py:95](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/leaf.py#L95) 中的 `calc_chunksize(expected_mb)` 根据预期数据量自动计算最优 chunk 大小：

```python
def calc_chunksize(expected_mb: int) -> int:
```

算法基于对数刻度：数据集越大，chunk 越大。公式：`8KB * 2^log10(expected_mb) * 8`。8 KB 为最小值，1 MB 为 10 TB 数据集的 chunk 大小。chunk 大小影响 B 树深度、内存占用和 I/O 效率。

## 索引系统

PyTables 为 Table 的列提供索引以加速条件查询。索引定义在 [index.py](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/index.py)，底层实现使用 [indexes.py](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/indexes.py) 和 `indexesextension.pyx` Cython 扩展。

### 索引类型（kind）

创建索引时通过 `kind` 参数选择索引粒度：

| kind | 说明 | 行定位精度 | 索引大小 |
|------|------|-----------|---------|
| `full` | 完全索引 | 精确行号（64位） | 最大 |
| `medium` | 中等索引 | 块级别（32位） | 中等 |
| `light` | 轻量索引 | 块级别（16位） | 较小 |
| `ultralight` | 超轻量索引 | 块级别（8位） | 最小 |

- **完全索引（full）** 存储排序后的精确值与行号映射，查询时直接定位到具体行
- **部分索引（medium/light/ultralight）** 只记录数据所在的 chunk 位置，索引体积更小，查询时需在候选 chunk 内顺序扫描

### 优化级别（optlevel）

| 级别 | 说明 |
|------|------|
| 0 | 无额外优化 |
| 1-9 | 索引压缩/排序优化程度，级别越高索引越小但创建越慢 |

### CSI：Chunked Sorted Index（分块排序索引）

PyTables 的索引实现基于 CSI（Chunked Sorted Index）：

1. **分块**：列数据按 chunk 划分
2. **排序**：每个 chunk 内的数据值和对应行号被排序
3. **索引结构**：排序后的值和行号存储为 EArray（可扩展数组），支持压缩
4. **搜索**：二分查找定位值范围，再获取候选 chunk 或行号
5. **合并**：多个索引条件的结果通过 Numexpr 组合 chunkmap（布尔掩码）

索引存储在隐藏分组 `_i_<tablename>/` 下，每个被索引的列对应一个 Index Group。

### Index 类

`Index`（[index.py:113](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/index.py#L113)）继承自 `NotLoggedMixin`、`Group` 和 `indexesextension.Index`，是列索引的容器：

| 属性/方法 | 说明 |
|-----------|------|
| `kind` | 索引类型（full/medium/light/ultralight） |
| `optlevel` | 优化级别 |
| `dirty` | 索引是否需要重建 |
| `nelements` | 已索引元素数量 |
| `search(range_)` | 在索引中搜索值范围，返回匹配数 |
| `get_lookup_range(ops, lims)` | 根据操作符和边界值计算搜索范围 |
| `get_chunkmap()` | 获取候选 chunk 布尔掩码 |
| `optimize(verbose=...)` | 优化（压缩/排序）索引 |
| `create_index(...)` | （Column 方法）为列创建索引 |
| `reindex()` | 重建已有索引 |
| `reindex_dirty()` | 仅重建脏索引 |

### 创建索引

```python
# 为单个列创建索引
table.cols.energy.create_index(
    optlevel=9,        # 最高优化级别
    kind='full',       # 完全索引
    filters=None,      # 索引压缩过滤器，默认 zlib level 1
    tmp_dir=None,      # 临时目录
    blocksizes=None,   # 块大小，自动计算
    verbose=False,
)

# 自动索引（默认开启）
table.autoindex = True   # 追加行后自动更新索引
table.flush_rows_to_index()  # 手动将缓冲区行写入索引
```

### 默认配置

```python
default_auto_index = True   # 追加后自动更新索引
default_index_filters = Filters(complevel=1, complib='zlib', shuffle=True)
```

### 索引可支持的数据类型

经过优化的搜索在 Cython/C 层实现了以下类型的快速路径（`opt_search_types`）：

- 整数：int8/16/32/64、uint8/16/32/64
- 浮点：float32/64

不支持索引的类型：
- uint64 列（[table.py:292](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/table.py#L292) 抛出 NotImplementedError）
- 复数列
- 多维列（shape 非空）

### 自动索引维护

当 `table.autoindex = True`（默认）：
1. `append()` 操作后，新行被标记但索引不立即更新（性能优化）
2. `flush()` 时调用 `flush_rows_to_index()` 将缓冲行合并到索引
3. 删除/修改行会使索引变脏（dirty），下次查询时自动重建
4. `reindex_dirty()` 手动重建所有脏索引

## 查询优化流程

Table.where() 的查询优化遵循以下流程：

1. **编译条件**：`compile_condition()` 解析表达式，识别可用索引的列
2. **索引查找**：对每个索引列：
   - 调用 `index.get_lookup_range(ops, lims)` 确定值范围
   - 调用 `index.search(range_)` 二分搜索匹配的 chunk
   - 获取 chunkmap（布尔数组，标记可能包含匹配的 chunk）
3. **组合 chunkmap**：多个索引条件通过 `numexpr.evaluate()` 用位运算合并
4. **候选扫描**：仅在 chunkmap 标记的 chunk 内顺序扫描，应用完整条件过滤
5. **缓存结果**：相同查询的行号序列缓存于 `_seqcache`，加速重复查询
6. **返回迭代器**：返回 Row 迭代器或通过 `get_where_list()` 返回行号数组

### 性能建议

- 将最具选择性（最严格）的索引条件放在条件表达式最左侧
- 为常用查询条件列创建 full 索引
- 对超大表使用 light/ultralight 索引节省磁盘空间
- 批量追加后统一 flush，避免频繁索引更新
- 使用 `get_where_list()` 获取行号后批量读取，减少迭代开销
- 设置合理的 `expectedrows` 参数帮助优化 chunk 和索引大小

## 相关概念

- [Table 与 Atom](02-table-atom.md)
- [节点层次体系](01-node-hierarchy.md)
- [PyTables 简介](00-introduction.md)
- [文件初始化参考](../references/file-init.md)
- [基础操作示例](../examples/hdf5-basics.md)
