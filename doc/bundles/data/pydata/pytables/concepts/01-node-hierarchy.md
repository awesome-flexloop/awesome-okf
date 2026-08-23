---
type: concept
title: 节点层次体系
description: PyTables 的节点继承体系与层次结构，包括 Node 基类、Group 分组、Leaf 叶子节点、四种数组类型、Table 表、路径系统与链接机制
tags: [pytables, node, hierarchy, group, leaf, array, table, link, path]
generated:
  by: reference_agent/trae-glm
  at: 2026-08-22T15:00:00Z
verified:
  by: "process:seven-concepts-v"
  at: 2026-08-22T15:30:00Z
status: stable
stale_after: 2027-12-31
sources:
  - tables/node.py
  - tables/group.py
  - tables/leaf.py
  - tables/array.py
  - tables/carray.py
  - tables/earray.py
  - tables/vlarray.py
  - tables/table.py
  - tables/path.py
  - tables/link.py
---

# 节点层次体系

PyTables 使用树状层次结构组织数据，所有存储对象均为 **Node（节点）**。节点分为两大类：**Group（分组）** 类似目录容器，**Leaf（叶子）** 类似文件存储实际数据。

## 继承体系

```
Node (metaclass=MetaNode)
├── Group (hdf5extension.Group)
│   ├── RootGroup          — 根分组 "/"
│   ├── TransactionG       — 事务分组
│   ├── IndexesTableG      — 索引表容器分组
│   ├── IndexesDescG       — 索引描述分组
│   └── MarkG              — Undo 标记分组
├── Link
│   ├── SoftLink           — 软链接（文件内）
│   └── ExternalLink       — 外部链接（跨文件）
├── Leaf
│   ├── Array (hdf5extension.Array)
│   │   └── CArray
│   │       └── EArray
│   ├── VLArray (hdf5extension.VLArray)
│   └── Table (tableextension.Table)
├── UnImplemented          — 未实现的节点类型占位
└── Unknown                — 未知节点类型占位
```

## MetaNode 元类与自动注册

所有 Node 子类通过 `MetaNode` 元类（[node.py:56](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/node.py#L56)）自动完成注册：

1. **class_name_dict 注册**：将类名（如 `'Group'`、`'Table'`）映射到类对象
2. **class_id_dict 注册**：将 `_c_classid` 属性（如 `'GROUP'`、`'TABLE'`、`'ARRAY'`）映射到类对象
3. **字符串表示增强**：自动包装 `__str__` 和 `__repr__` 方法，节点关闭时显示 `<closed tables.group.Group at 0x...>`

各节点的类标识符：

| 类 | _c_classid |
|----|-----------|
| `Group` | `'GROUP'` |
| `Array` | `'ARRAY'` |
| `CArray` | `'CARRAY'` |
| `EArray` | `'EARRAY'` |
| `VLArray` | `'VLARRAY'` |
| `Table` | `'TABLE'` |

## Node 基类

`Node`（[node.py:99](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/node.py#L99)）是所有节点的抽象基类，不能直接实例化。

### 位置相关属性（_v_ 前缀）

所有实例变量以 `_v_` 开头，避免与子节点自然命名冲突：

| 属性 | 说明 |
|------|------|
| `_v_name` | 节点在父分组中的名称（字符串） |
| `_v_pathname` | 节点在文件中的完整路径（如 `/group1/table1`） |
| `_v_depth` | 节点在树中的深度（整数，根为 0） |
| `_v_file` | 所属 File 实例 |
| `_v_parent` | 父分组引用 |
| `_v_attrs` | 节点的属性集合（AttributeSet） |
| `_v_isopen` | 节点是否处于打开状态 |
| `_v_title` | 节点标题（TITLE 属性） |
| `_v_objectid` | HDF5 对象标识符 |

### 公共方法前缀约定

| 前缀 | 含义 | 示例 |
|------|------|------|
| `_f_` | 公共方法 | `_f_rename()`, `_f_close()`, `_f_copy()` |
| `_g_` | 私有方法 | `_g_pre_kill_hook()`, `_g_load_child()` |
| `_v_` | 实例变量 | `_v_name`, `_v_pathname` |
| `_c_` | 类变量/常量 | `_c_classid` |

## Group（分组）

`Group`（[group.py:39](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/group.py#L39)）是容器节点，类似 Unix 文件系统目录，可以包含其他 Group、Leaf 和 Link。

### 核心属性

| 属性 | 说明 |
|------|------|
| `_v_children` | 包含所有子节点的字典 |
| `_v_groups` | 仅包含子分组的字典 |
| `_v_leaves` | 仅包含叶子节点的字典 |
| `_v_links` | 仅包含链接节点的字典 |
| `_v_hidden` | 包含隐藏节点（以 `_i_` 或 `_p_` 开头）的字典 |
| `_v_unknown` | 包含未知/未实现节点的字典 |
| `_v_nchildren` | 直接子节点数量 |
| `_v_filters` | 继承给子节点的默认过滤器 |

### 自然命名访问

Group 支持通过属性访问语法直接获取子节点（自然命名）：

```python
# 假设有 /detector/events 表
table = h5file.root.detector.events    # 自然命名
table = h5file.get_node("/detector/events")  # 编程方式
```

自然命名限制：
- 子节点名必须是有效的 Python 标识符（不能以数字开头，不能包含特殊字符）
- 不能是 Python 关键字（如 `class`、`for`）
- 不能与 Group 的保留前缀（`_f_`、`_g_`、`_v_`、`_c_`）开头
- 不符合条件的名称会发出 `NaturalNameWarning`，需用 `_f_get_child(name)` 访问

### RootGroup

根分组 `RootGroup` 是树的顶层节点，路径固定为 `/`。通过 `file.root` 属性访问。它设置 `root_uep`（User Entry Point），支持加载部分子树。

## Leaf（叶子节点）

`Leaf`（[leaf.py](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/leaf.py)）是所有存储实际数据的节点的基类。Leaf 不能包含子节点。

### 核心属性

| 属性 | 说明 |
|------|------|
| `shape` | 数据形状（元组） |
| `nrows` | 行数（第一维大小） |
| `dtype` | NumPy 数据类型 |
| `nrowsinbuf` | I/O 缓冲区行数 |
| `extdim` | 可扩展维度索引（EArray 为 0，不可扩展为 -1） |
| `chunkshape` | HDF5 分块形状 |
| `filters` | 该叶子的过滤器配置 |
| `flavor` | 数据风味（'numpy' 等） |
| `byteorder` | 字节序（'little'/'big'） |
| `size_in_memory` | 全部加载到内存时的字节数 |
| `size_on_disk` | 磁盘占用字节数 |

### ChunkInfo

`ChunkInfo`（[leaf.py:119](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/leaf.py#L119)）是 NamedTuple，描述单个数据块的存储信息：

| 字段 | 说明 |
|------|------|
| `start` | 块起始坐标（元组） |
| `filter_mask` | 过滤器禁用位掩码 |
| `offset` | 块在文件中的字节偏移 |
| `size` | 块在磁盘上的字节大小 |

## 四种数组类型

### Array — 基本数组

`Array`（[array.py:41](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/array.py#L41)）是最简单的数组类型：
- **不分块**（non-chunked），不支持压缩
- 创建时一次性写入完整数据，之后不可修改大小
- 无内部 I/O 缓冲区，写入操作立即落盘
- 支持 NumPy 数组、Python 序列、标量值
- 记忆输入数据的"风味"（flavor），读取时自动转换回原类型

### CArray — 分块数组

`CArray`（[carray.py:25](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/carray.py#L25)）继承自 Array：
- **分块布局**，支持压缩过滤器
- 大小固定不可扩展
- 支持通过索引读写数据
- 需要指定 `atom`（数据类型描述符）和 `shape`

### EArray — 可扩展数组

`EArray`（[earray.py:27](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/earray.py#L27)）继承自 CArray：
- 支持沿**单一维度**（可扩展维度，`extdim=0`）追加数据
- 创建时该维度 shape 必须设为 `0`
- 通过 `append(sequence)` 方法在末尾添加数据
- 典型用途：逐步写入模拟数据、日志数据

### VLArray — 变长数组

`VLArray`（[vlarray.py:41](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/vlarray.py#L41)）存储可变长度行：
- 每行可以包含**不同数量**的同类型原子元素
- 读取行范围时始终返回 Python 列表
- 支持 ObjectAtom、VLStringAtom、VLUnicodeAtom 等特殊类型
- 注意：原始数据不经过压缩过滤器

## Table — 结构化表

`Table`（[table.py:383](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/table.py#L383)）继承自 `tableextension.Table` 和 `Leaf`，存储异构结构化数据：
- 一维行序列，每行包含多个命名字段（列）
- 字段支持嵌套（任意深度）
- 支持行追加、条件查询、索引、排序
- 详细说明见 [Table 与 Atom](02-table-atom.md)

## 路径系统（path.py）

[path.py](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/path.py) 提供节点路径操作工具函数。

### 路径规则

- 使用 `/` 作为分隔符，类似 Unix 路径
- 绝对路径以 `/` 开头（如 `/group1/table1`）
- 根路径为 `/`
- 名称不能包含 `/` 或 `.`
- 以 `_i_` 开头的名称为索引隐藏节点
- 以 `_p_` 开头的名称为事务隐藏节点

### 核心函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `join_path(parentpath, name)` | 拼接路径 | `join_path('/foo', 'bar') → '/foo/bar'` |
| `split_path(path)` | 拆分路径为（父路径, 名称） | `split_path('/foo/bar') → ('/foo', 'bar')` |
| `check_name_validity(name)` | 验证节点名合法性 | 拒绝 `/`、`.`、空字符串 |
| `check_attribute_name(name)` | 验证属性名合法性 | 拒绝保留前缀、`__members__` |
| `isvisiblename(name)` | 判断名称是否可见（非隐藏） | |
| `isvisiblepath(path)` | 判断路径是否可见 | |

### 命名保留前缀

正则 `^_[cfgv]_` 匹配保留前缀：

| 前缀 | 用途 |
|------|------|
| `_c_` | 类变量 |
| `_f_` | 公共方法 |
| `_g_` | 私有方法 |
| `_v_` | 实例变量 |

## 链接（link.py）

[link.py](file:///d:/spaces/SpecWeave/external/libs/python/PyTables/tables/link.py) 实现了两种链接节点。链接不支持 HDF5 属性。

### SoftLink（软链接）

- 指向**同一文件内**的另一个节点路径
- 类似 Unix 符号链接
- 通过 `target` 属性获取/设置目标路径
- 解引用：访问链接节点时通过 `__call__()` 方法获取目标节点

### ExternalLink（外部链接）

- 指向**外部 HDF5 文件**中的节点
- 目标路径格式为 `filename:pathname`
- 支持跨文件引用
- 解引用时会打开外部文件（如果尚未打开）

### 硬链接

HDF5 硬链接不需要特殊容器类，表现为同一节点拥有多个路径名，通过 Group 的 `_f_link()` 等方法创建。

## 节点遍历

### File/Group 级别遍历

| 方法 | 说明 |
|------|------|
| `iter_nodes(where, classname)` | 迭代直接子节点，可按类名过滤 |
| `walk_nodes(where, classname)` | 递归遍历所有后代节点 |
| `_f_list_nodes(classname)` | 列出子节点列表 |

### 自然命名与遍历

```python
# 遍历根分组下所有叶子
for leaf in h5file.walk_nodes("/", classname="Leaf"):
    print(leaf._v_pathname)
```

## 相关概念

- [PyTables 简介](00-introduction.md)
- [Table 与 Atom](02-table-atom.md)
- [压缩与索引](03-compression-indexing.md)
- [文件初始化参考](../references/file-init.md)
