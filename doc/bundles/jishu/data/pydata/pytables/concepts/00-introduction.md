---
type: concept
title: PyTables 简介
description: PyTables 是基于 HDF5 的 Python 分层数据集管理库，支持 TB 级超大数据高效存储与查询，内置 Blosc2 压缩，与 NumPy/pandas 深度集成
tags: [pytables, hdf5, introduction, big-data, blosc2, numpy, pandas]
generated:
  by: reference_agent/trae-glm
  at: 2026-08-22T15:00:00Z
verified:
  by: "process:seven-concepts-v"
  at: 2026-08-22T15:30:00Z
status: stable
stale_after: 2027-12-31
sources:
  - tables/__init__.py
  - tables/_version.py
---

# PyTables 简介

## 什么是 PyTables

PyTables 是一个用于管理**分层数据集（hierarchical datasets）**的 Python 包，构建在 HDF5（Hierarchical Data Format version 5）C 库之上，专为高效处理**超大规模数据**（TB 级别）而设计。

- **官方 URL**：http://www.pytables.org/
- **许可证**：BSD 风格开源许可证
- **当前版本**：3.12.0.dev0
- **底层格式**：HDF5（文件扩展名为 `.h5`、`.hdf`、`.hdf5`）

## 核心特性

### 1. 分层数据模型

PyTables 将数据组织为类似 Unix 文件系统的树状结构：
- **Group（分组）** 类似目录，可以嵌套包含其他 Group 和 Leaf
- **Leaf（叶子节点）** 类似文件，存储实际数据，包括数组和表
- **路径系统** 使用 `/` 分隔的绝对路径访问节点（如 `/detector0/events`）

### 2. Cython + C 扩展高性能内核

PyTables 的核心 I/O 操作通过 Cython 编写的扩展模块直接调用 HDF5 C 库，避免 Python 解释器开销：

| Cython 扩展模块 | 职责 |
|----------------|------|
| `hdf5extension.pyx` | HDF5 底层文件/分组/数组操作 |
| `tableextension.pyx` | 表行迭代、行写入等高性能表操作 |
| `indexesextension.pyx` | 索引搜索、B 树操作 |
| `utilsextension.pyx` | Blosc 压缩、类型转换、工具函数 |
| `lrucacheextension.pyx` | LRU 节点缓存、NumPy 数组缓存 |
| `linkextension.pyx` | 软链接/外部链接解析 |

### 3. Blosc2 压缩集成

PyTables 3.x 版本深度集成 **Blosc2** 高性能压缩库，支持多种压缩算法：

- **Blosc/Blosc2**：元压缩器，内部支持 blosclz、lz4、lz4hc、zlib、zstd 等子压缩器
- **Zlib（DEFLATE）**：通用压缩，兼容性最好
- **BZIP2**：高压缩比，速度较慢
- **LZO**：快速压缩
- **Shuffle/BitShuffle 过滤器**：重排字节顺序以提升压缩率
- **Fletcher32**：数据校验和

压缩在 HDF5 chunk（块）级别进行，数据以压缩形式存储在磁盘上，读取时实时解压。

### 4. 高效处理 TB 级数据

PyTables 针对超大数据集设计了多项优化：

- **分块存储（Chunking）**：数据按固定大小的 chunk 组织，只加载需要的 chunk 到内存
- **LRU 节点缓存**：`NodeManager` 管理最近使用的节点，减少磁盘 I/O
- **内存映射 I/O**：通过 Numexpr 实现内核外（out-of-core）计算，可处理大于内存的数据集
- **自动 chunk 大小计算**：`calc_chunksize()` 根据预期数据量自动计算最优 chunk 大小

### 5. 与 NumPy/pandas 深度集成

- 数据在内存中以 **NumPy ndarray** 形式呈现
- Array 类节点支持直接读写 NumPy 数组和 Python 原生序列
- Table 类节点支持 NumPy 结构化数组（recarray）
- `pandas.read_hdf()` / `DataFrame.to_hdf()` 底层使用 PyTables（HDFStore）
- 列数据类型直接映射到 NumPy dtype

### 6. 表查询与索引

Table 类提供了强大的查询能力：

- **`where(condition)`**：条件迭代，支持字符串表达式查询，自动利用索引加速
- **`get_where_list(condition)`**：返回满足条件的行索引数组
- **`read_where(condition)`**：直接读取满足条件的行数据
- **`read_sorted(sortby, ...)`**：按列排序读取
- **完全/部分索引**：支持 `full`、`medium`、`light`、`ultralight` 四种索引粒度
- **CSI（Chunked Sorted Index）**：分块排序索引，平衡索引大小与查询性能
- **Numexpr 加速**：条件表达式通过 Numexpr 编译求值，充分利用 CPU 向量化

## 数据节点类型概览

PyTables 的数据存储节点分为数组和表两大类：

### 数组类型（同质数据）

| 类名 | 分块 | 可扩展 | 压缩 | 说明 |
|------|------|--------|------|------|
| `Array` | 否 | 否 | 否 | 基本数组，一次性写入不可变 |
| `CArray` | 是 | 否 | 是 | 分块数组，支持压缩 |
| `EArray` | 是 | 是（一维） | 是 | 可扩展数组，支持沿单一维度追加 |
| `VLArray` | 是 | 是（行） | 是* | 变长数组，每行可包含不同数量的元素 |

*VLArray 的原始数据不经过压缩过滤器，仅内部引用结构被压缩。

### 表类型（异质结构化数据）

| 类名 | 说明 |
|------|------|
| `Table` | 结构化表，类似关系数据库表或 pandas DataFrame，每行包含多个命名字段（列），支持追加、条件查询、索引 |

## 其他核心组件

| 模块 | 功能 |
|------|------|
| `Filters` | 压缩过滤器配置管道 |
| `Atom` | 数据类型描述符系统 |
| `Col`/`Cols`/`Column` | 列定义与列访问 |
| `Expr` | 基于 Numexpr 的数组表达式求值，支持内核外计算 |
| `Link`/`SoftLink`/`ExternalLink` | 软链接与跨文件外部链接 |
| `Undo/Redo` | 事务支持，可标记回滚点 |

## 适用场景

- 科学计算中大规模实验数据的持久化存储
- 时间序列数据的归档与查询
- 多维度数组数据的分层组织
- 需要压缩的大型数值数据集
- pandas DataFrame 的长期存储格式
- 跨平台数据交换（HDF5 为标准格式）

## 相关概念

- [节点层次体系](01-node-hierarchy.md)
- [Table 与 Atom](02-table-atom.md)
- [压缩与索引](03-compression-indexing.md)
- [文件初始化参考](../references/file-init.md)
- [基础操作示例](../examples/hdf5-basics.md)
