---
type: reference
title: PyTables 文件初始化
description: PyTables 的文件打开与初始化机制，包括 File 类、open_file() 工厂函数、HDF5 库版本检测、Blosc2 压缩库动态加载与节点注册表
tags: [pytables, hdf5, file, initialization, blosc2, registry]
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
  - tables/registry.py
  - tables/utilsextension.pyx
---

# PyTables 文件初始化

本文档描述 PyTables 库从导入到打开 HDF5 文件的完整初始化流程。

## Blosc2 压缩库动态加载

PyTables 在包导入阶段（`__init__.py`）即通过 `_load_blosc2()` 函数动态加载 Blosc2 压缩库。加载路径依次为：

1. **delvewheel 路径**（Windows 专用）：`tables.libs/` 同级目录下的 `libblosc2.dll`
2. **包内路径**：`tables/` 包目录
3. **site-packages 路径**：`site-packages/blosc2/lib/`（venv/conda 环境）
4. **系统默认路径**：不指定路径，依赖操作系统动态链接器搜索

```python
def _load_blosc2():
    import ctypes, platform, sysconfig
    from pathlib import Path

    search_paths = (
        Path(__file__).parent.with_suffix(".libs"),  # delvewheel
        Path(__file__).parent,                        # tables package
        Path(sysconfig.get_path("platlib")) / "blosc2" / "lib",
        Path(sysconfig.get_path("purelib")) / "blosc2" / "lib",
        "",                                           # default
    )
    # ... 按平台选择扩展名 (.so/.dylib/.dll) 并尝试 ctypes.CDLL 加载
```

若所有路径均加载失败，抛出 `RuntimeError("Blosc2 library not found.")`，包导入终止。

## HDF5 库版本检测

Blosc2 加载成功后，PyTables 通过 Cython 扩展获取底层 HDF5 库版本：

```python
from .utilsextension import get_hdf5_version as _get_hdf5_version
hdf5_version = _get_hdf5_version()
```

`utilsextension` 模块还提供以下版本相关函数：

| 函数 | 用途 |
|------|------|
| `get_hdf5_version()` | 获取 HDF5 C 库版本字符串 |
| `which_lib_version(name)` | 查询指定压缩库（blosc/blosc2/zlib/lzo/bzip2）是否可用及其版本 |
| `blosc_compressor_list()` | 列出 Blosc1 可用的子压缩器（blosclz/lz4/lz4hc/zlib/zstd） |
| `blosc2_compressor_list()` | 列出 Blosc2 可用的子压缩器 |

版本检测结果决定文件打开策略（`_FILE_OPEN_POLICY`）：HDF5 < 1.8.7 使用 `"strict"` 策略（禁止同一文件多次打开），1.8.7+ 使用 `"default"` 策略（允许多次只读打开）。

## open_file() 工厂函数

`open_file()` 是创建 `File` 实例的推荐入口，定义在 file.py:216。

### 函数签名

```python
def open_file(
    filename: str,
    mode: Literal["r", "w", "a", "r+"] = "r",
    title: str = "",
    root_uep: str = "/",
    filters: Filters | None = None,
    **kwargs,
) -> File:
```

### 文件打开模式

| 模式 | 说明 |
|------|------|
| `'r'` | 只读模式，不能修改数据 |
| `'w'` | 写入模式，创建新文件（已存在则覆盖） |
| `'a'` | 追加模式，读写已有文件，不存在则创建 |
| `'r+'` | 读写模式，文件必须已存在 |

### 重复打开检测

在调用 `File` 构造函数之前，`open_file()` 会检查 `_open_files` 注册表（`_FileRegistry` 实例），根据当前 `_FILE_OPEN_POLICY` 拒绝不兼容的重复打开请求。

### root_uep 参数

`root_uep`（User Entry Point）指定 HDF5 层次结构中作为根节点起始位置的分组路径，默认为 `"/"`。设置为子分组路径可仅加载部分对象树，适用于超大文件。

## File 类

`File` 类定义在 file.py，继承自 `hdf5extension.File`（Cython 扩展层）。它是 PyTables 文件操作的核心入口。

### 构造与初始化

```python
class File:
    def __init__(
        self,
        filename: str,
        mode: Literal["r", "w", "a", "r+"] = "r",
        title: str = "",
        root_uep: str = "/",
        filters: Filters | None = None,
        **kwargs,
    ) -> None:
```

初始化过程中：

1. 验证 `mode` 参数合法性
2. 加载 `parameters.py` 中的全部大写参数（如 `EXPECTED_ROWS_TABLE`、`MAX_BLOSC_THREADS`、`IO_BUFFER_SIZE` 等），允许通过 `kwargs` 覆盖
3. 自动检测 CPU 核心数，设置 `MAX_NUMEXPR_THREADS` 和 `MAX_BLOSC_THREADS` 默认值
4. 调用 `__get_root_group()` 创建 `RootGroup` 实例（根分组 `/`）
5. 初始化 `NodeManager`（LRU 节点缓存管理器），`node_factory` 设置为 `root._g_load_child` 实现延迟加载

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `filename` | `str` | 打开的文件名 |
| `mode` | `str` | 文件打开模式 |
| `root` | `RootGroup` | 文件根分组对象 |
| `title` | `str` | 根分组标题（读写属性） |
| `filters` | `Filters` | 根分组默认过滤器（读写属性） |
| `root_uep` | `str` | 用户入口点路径 |
| `params` | `dict` | 运行参数字典 |

### 节点创建方法

File 类提供一系列 `create_*` 方法在指定分组下创建节点：

| 方法 | 创建的节点类型 | 定义位置 |
|------|---------------|----------|
| `create_group(where, name, title, filters, createparents)` | `Group` 分组 | file.py:924 |
| `create_table(where, name, description, title, filters, expectedrows, ...)` | `Table` 结构化表 | file.py:965 |
| `create_array(where, name, obj, title, byteorder, ...)` | `Array` 数组 | file.py:1108 |
| `create_carray(where, name, atom, shape, title, filters, ...)` | `CArray` 分块数组 | file.py:1225 |
| `create_earray(where, name, atom, shape, title, filters, ...)` | `EArray` 可扩展数组 | file.py:1360 |
| `create_vlarray(where, name, atom, title, filters, ...)` | `VLArray` 变长数组 | file.py:1501 |
| `create_soft_link(where, name, target)` | `SoftLink` 软链接 | file.py:1655 |
| `create_external_link(where, name, target, ...)` | `ExternalLink` 外部链接 | file.py:1689 |

所有创建方法均接受 `createparents: bool = False` 参数，设为 `True` 时自动创建路径中不存在的父分组。

### 文件生命周期方法

| 方法 | 说明 |
|------|------|
| `flush()` | 将所有缓冲数据写入磁盘 |
| `close()` | 关闭文件，释放所有节点资源 |
| `copy_file(dstfilename, ...)` | 将文件内容复制到新文件 |
| `close_all()` | 关闭所有已打开的 PyTables 文件（静态方法） |

### 节点遍历方法

| 方法 | 说明 |
|------|------|
| `iter_nodes(where, classname)` | 迭代指定路径下的节点 |
| `walk_nodes(where, classname)` | 递归遍历节点树 |

## _FileRegistry：已打开文件注册表

`_FileRegistry` 类（file.py:90）维护所有已打开的 File 实例：

- `_name_mapping`：文件名到 File 实例集合的映射（支持同一文件多次打开）
- `_handlers`：所有活跃 File 实例集合
- `close_all()`：程序退出时通过 `atexit` 自动调用，关闭所有未关闭文件并发出 `UnclosedFileWarning`

## 节点注册表（registry.py）

registry.py 提供两个全局字典用于避免循环导入：

### class_name_dict

键为类名字符串（如 `'Group'`、`'Table'`），值为对应的类对象。所有 Node 子类在通过 `MetaNode` 元类实例化时自动注册到此字典。

### class_id_dict

键为 HDF5 类标识符（如 `'GROUP'`、`'TABLE'`、`'ARRAY'`、`'CARRAY'`、`'EARRAY'`、`'VLARRAY'`），值为对应的类对象。每个 Node 子类通过定义 `_c_classid` 类属性完成注册。

### get_class_by_name()

```python
def get_class_by_name(classname: str | None) -> type:
```

根据类名字符串返回对应的类对象。接受 `None` 或空字符串时返回 `Node` 基类。若类名未注册，抛出 `TypeError`。

## 节点管理器（NodeManager）

`NodeManager`（file.py:365）负责节点的缓存与延迟加载：

- **registry**：`WeakValueDictionary`，跟踪所有已加载节点
- **cache**：LRU 缓存（由 `lrucacheextension.NodeCache` Cython 扩展实现），默认 64 槽位
- **node_factory**：回调函数，指向 `root._g_load_child`，用于按需从磁盘加载子节点

nslots 参数控制缓存行为：
- `nslots > 0`：使用 LRU 缓存
- `nslots == 0`：禁用缓存
- `nslots < 0`：使用无界字典缓存（可能导致内存问题，发出 `PerformanceWarning`）

## 相关概念

- [节点层次体系](../concepts/01-node-hierarchy.md)
- [Table 与 Atom](../concepts/02-table-atom.md)
- [压缩与索引](../concepts/03-compression-indexing.md)
- [PyTables 简介](../concepts/00-introduction.md)
