---
okf_version: "0.2"
type: bundle
title: PyTables 知识包
description: PyTables（tables）HDF5 分层数据管理库的 OKF Wiki 教程，涵盖核心概念、API 参考与实战示例
tags: [pytables, hdf5, python, data-storage, big-data, blosc2, numpy, scientific-computing]
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
  - tables/file.py
  - tables/node.py
  - tables/group.py
  - tables/leaf.py
  - tables/array.py
  - tables/carray.py
  - tables/earray.py
  - tables/vlarray.py
  - tables/table.py
  - tables/atom.py
  - tables/description.py
  - tables/filters.py
  - tables/index.py
  - tables/indexes.py
  - tables/link.py
  - tables/path.py
  - tables/registry.py
  - tables/exceptions.py
  - tables/expression.py
  - tables/_version.py
---

# PyTables 知识包

[PyTables](http://www.pytables.org/) 是基于 HDF5 的 Python 分层数据集管理库，BSD 许可证开源。它使用 Cython + C 扩展实现高性能 I/O，支持 TB 级超大数据集的高效存储、Blosc2 实时压缩、条件查询和列式索引，与 NumPy/pandas 深度集成。

本知识包基于 PyTables 3.12.0.dev0 源码静态分析生成，所有类名、方法名、参数名均直接来自源码验证。

## 快速开始

```python
import tables as tb
import numpy as np

# 创建文件并写入表
with tb.open_file('data.h5', mode='w', title='My data') as f:
    class Particle(tb.IsDescription):
        energy = tb.Float64Col()
        position = tb.Float32Col(shape=(3,))
    table = f.create_table('/', 'particles', Particle, expectedrows=10000)
    row = table.row
    for i in range(1000):
        row['energy'] = np.random.exponential(100)
        row['position'] = np.random.randn(3)
        row.append()
    table.flush()
    # 条件查询
    high_e = [r['energy'] for r in table.where('energy > 200')]
    print(f"高能量事件: {len(high_e)} 个")
```

## 目录

### 概念文档（concepts/）

按学习顺序排列，建议依次阅读。

| 编号 | 文档 | 主题 |
|------|------|------|
| 00 | [concepts/00-introduction.md](concepts/00-introduction.md) | PyTables 简介：定位、特性、架构、适用场景 |
| 01 | [concepts/01-node-hierarchy.md](concepts/01-node-hierarchy.md) | 节点层次体系：Node→Group/Leaf/Link 继承树、路径系统、四种数组类型、Table、链接 |
| 02 | [concepts/02-table-atom.md](concepts/02-table-atom.md) | Table 与 Atom：结构化表、Cols/Column 列访问、Atom 类型系统、行操作、where 条件查询 |
| 03 | [concepts/03-compression-indexing.md](concepts/03-compression-indexing.md) | 压缩与索引：Filters 管道、Blosc2、Shuffle/BitShuffle、CSI 索引、查询优化 |

[→ 概念索引](concepts/index.md)

### API 参考（references/）

基于源码的精确 API 参考文档。

| 文档 | 覆盖模块 |
|------|---------|
| [references/file-init.md](references/file-init.md) | 文件初始化：`open_file()` 工厂函数、`File` 类、Blosc2 动态加载、HDF5 版本检测、节点注册表、NodeManager |

[→ 信源登记簿](references/index.md)

### 示例代码（examples/）

完整可运行的 Python 代码示例。

| 文档 | 难度 | 覆盖内容 |
|------|------|---------|
| [examples/hdf5-basics.md](examples/hdf5-basics.md) | 入门 | 文件创建、全部节点类型、读写追加、条件查询、索引、压缩、pandas 转换 |

[→ 示例索引](examples/index.md)

## 源码模块对照

| 模块文件 | 职责 | 知识包覆盖位置 |
|----------|------|---------------|
| `__init__.py` | Blosc2 加载、版本检测、公共 API 导出 | [file-init](references/file-init.md) |
| `file.py` | File 类、open_file()、节点管理、节点创建 | [file-init](references/file-init.md) |
| `node.py` | Node 基类、MetaNode 元类、属性约定 | [01-node-hierarchy](concepts/01-node-hierarchy.md) |
| `group.py` | Group 类、RootGroup、自然命名 | [01-node-hierarchy](concepts/01-node-hierarchy.md) |
| `leaf.py` | Leaf 基类、ChunkInfo、chunk 计算 | [01-node-hierarchy](concepts/01-node-hierarchy.md) |
| `array.py` | Array（基本数组） | [01-node-hierarchy](concepts/01-node-hierarchy.md), [hdf5-basics](examples/hdf5-basics.md) |
| `carray.py` | CArray（分块压缩数组） | [01-node-hierarchy](concepts/01-node-hierarchy.md) |
| `earray.py` | EArray（可扩展数组） | [01-node-hierarchy](concepts/01-node-hierarchy.md) |
| `vlarray.py` | VLArray（变长数组） | [01-node-hierarchy](concepts/01-node-hierarchy.md) |
| `table.py` | Table、Cols、Column、Row、where 查询 | [02-table-atom](concepts/02-table-atom.md) |
| `atom.py` | Atom 类型描述符系统 | [02-table-atom](concepts/02-table-atom.md) |
| `description.py` | Description、IsDescription、Col 类型 | [02-table-atom](concepts/02-table-atom.md) |
| `filters.py` | Filters 压缩过滤器管道 | [03-compression-indexing](concepts/03-compression-indexing.md) |
| `index.py` | Index 类、索引创建与优化 | [03-compression-indexing](concepts/03-compression-indexing.md) |
| `indexes.py` | CacheArray、IndexArray、LastRowArray | [03-compression-indexing](concepts/03-compression-indexing.md) |
| `link.py` | SoftLink、ExternalLink | [01-node-hierarchy](concepts/01-node-hierarchy.md) |
| `path.py` | 路径操作工具函数 | [01-node-hierarchy](concepts/01-node-hierarchy.md) |
| `registry.py` | class_name_dict、class_id_dict | [file-init](references/file-init.md) |
| `expression.py` | Expr（数组表达式求值） | [00-introduction](concepts/00-introduction.md) |
| `exceptions.py` | 异常与警告类 | [file-init](references/file-init.md) |

## Cython 扩展层

| 扩展模块 | 职责 |
|----------|------|
| `hdf5extension.pyx` | HDF5 底层文件/分组/数组操作的 C 绑定 |
| `tableextension.pyx` | 表 Row 迭代、高性能行 I/O |
| `indexesextension.pyx` | 索引二分搜索、B 树操作 |
| `utilsextension.pyx` | Blosc 压缩、版本查询、类型转换、bisect 工具 |
| `lrucacheextension.pyx` | LRU 节点缓存、NumPy 数组缓存 |
| `linkextension.pyx` | 链接类型检测与解析 |

## 版本信息

- PyTables 版本：3.12.0.dev0
- 生成日期：2026-08-22
- OKF 格式版本：0.2
- 分析源码路径：`tables/`

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
