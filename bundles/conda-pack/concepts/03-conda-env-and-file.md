---
type: "concept"
title: "CondaEnv 与 File 数据模型"
description: CondaEnv 类（环境表示）和 File 类（文件记录）的设计、创建方式、链式过滤 API，以及 _Context 上下文管理。
tags: [conda-pack, data-model, CondaEnv, File, API]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T05:45:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T06:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: core
    resource: /references/core-source.md
    title: core.py 核心模块源码
---

# CondaEnv 与 File 数据模型

conda-pack 的核心数据模型围绕两个类构建：`CondaEnv`（表示一个待打包的 conda 环境）和 `File`（表示环境中的单个文件记录）。

## CondaEnv 类

`CondaEnv` 是 conda-pack 的核心类，表示一个待打包的 conda 环境，包含环境路径和文件列表 [F-010]。

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `prefix` | `str` | 环境的绝对路径 |
| `files` | `list[File]` | 环境中的所有文件列表，按 `target` 排序 |
| `name` | `str` | 环境名称（prefix 的 basename） |

`CondaEnv` 支持 `len()` 返回文件数、`iter()` 迭代文件列表、`repr()` 显示为 `CondaEnv<'/path/to/env', N files>` 形式 [F-020]。

### 创建方式

**不直接使用构造函数**，而是通过三个类方法创建 [F-011]：

```python
from conda_pack import CondaEnv

# 1. 从环境名创建（通过 conda info --json 解析路径）
env = CondaEnv.from_name("my_env")

# 2. 从路径创建
env = CondaEnv.from_prefix("/home/user/miniconda3/envs/my_env")

# 3. 从当前激活环境创建
env = CondaEnv.from_default()
```

三个类方法最终都调用 `from_prefix()`，其流程为 [F-012][F-013][F-014]：

1. 将路径转为绝对路径（`os.path.abspath`）
2. 调用 `load_environment(prefix, **kwargs)` 收集文件列表
3. 构造并返回 `CondaEnv(prefix, files)`

### 链式文件过滤

`CondaEnv` 提供 `exclude()` 和 `include()` 方法进行文件过滤，支持链式调用 [F-015][F-016]：

```python
env = (CondaEnv.from_default()
       .exclude("*.pyc")           # 排除所有 .pyc 文件
       .exclude("tests/*")         # 排除 tests 目录
       .include("tests/test_app.py")  # 但包含特定测试文件
       )
```

**`exclude(pattern)`** 方法：
- 使用 `fnmatch.fnmatch(file.target, pattern)` 匹配文件路径
- 匹配到的文件移入 `_excluded_files` 列表
- 返回新的 `CondaEnv` 对象（不可变模式，不修改原对象）

**`include(pattern)`** 方法：
- 在 `_excluded_files` 列表中查找匹配的文件
- 匹配到的文件重新加入 `files` 列表
- 返回新的 `CondaEnv` 对象

> **注意**：过滤基于文件的 `target`（环境内相对路径），不是 `source`（绝对路径）。模式匹配使用 `fnmatch` 模块的 shell-style wildcards（`*`、`?`、`[seq]`）。

### pack() 方法

`pack()` 是 `CondaEnv` 的核心方法，执行实际打包 [F-019]：

```python
env.pack(
    output=None,              # 输出文件路径
    format="infer",           # 归档格式
    arcroot="",               # 归档内根路径
    dest_prefix=None,         # 目标前缀（预指定路径）
    parcel_root=None,         # Parcel 根目录
    parcel_name=None,         # Parcel 名称
    parcel_version=None,      # Parcel 版本
    parcel_distro=None,       # Parcel 发行版
    verbose=False,            # 显示进度
    force=False,              # 强制覆盖
    compress_level=4,         # 压缩级别
    n_threads=1,              # 压缩线程数
    zip_symlinks=False,       # zip 中存储符号链接
    zip_64=True,              # 启用 ZIP64
)
```

返回值是输出文件的绝对路径 [F-020]。

#### 格式推断

`_output_and_format()` 方法根据 `output` 文件扩展名自动推断格式 [F-017]：

| 扩展名 | 格式 |
|--------|------|
| `.zip` | zip |
| `.tar.gz`/`.tgz` | tar.gz |
| `.tar.bz2`/`.tbz2` | tar.bz2 |
| `.tar.xz`/`.txz` | tar.xz |
| `.tar.zst`/`.tzst` | tar.zst |
| `.tar` | tar |
| `.parcel` | parcel |
| `.squashfs` | squashfs |
| `.no-archive` | no-archive |

无 output 且 format="infer" 时，默认使用 `tar.gz` [F-017]。

## File 类

`File` 类表示环境中的单个文件记录，使用 `__slots__` 优化内存占用（因为环境可能包含数千个文件）[F-022]。

### 属性（__slots__）

| 属性 | 类型 | 说明 |
|------|------|------|
| `source` | `str` | 源文件的绝对路径 |
| `target` | `str` | 文件在归档/目标环境中的相对路径 |
| `is_conda` | `bool` | 是否为 conda 托管文件（vs pip/手动放置） |
| `file_mode` | `None`/`'text'`/`'binary'`/`'unknown'` | 文件处理模式 |
| `prefix_placeholder` | `None`/`str` | 文件中的前缀占位符 |

### file_mode 详解

`file_mode` 决定了 Packer 如何处理该文件 [F-023]：

| mode | 含义 | Packer 处理方式 |
|------|------|----------------|
| `None` | 无需前缀处理 | 直接添加到归档（如 conda-meta/*.json 先重写再添加） |
| `'text'` | 文本文件 | 读取内容，替换前缀后添加 |
| `'binary'` | 二进制文件 | 读取内容，二进制前缀替换（null填充）后添加 |
| `'unknown'` | 类型未知 | 读取内容，尝试 UTF-8 解码判断 text/binary 后处理 |

对于 `bin/` 目录下的文本文件（脚本），Packer 会额外尝试 shebang 重写 [F-036]。

### repr 格式

```python
File<'bin/python', is_conda=True>
File<'lib/python3.10/site-packages/numpy/__init__.py', is_conda=True>
File<'my_custom_script.sh', is_conda=False>
```

## _Context 上下文管理器

`_Context` 是一个简单的上下文管理类，控制 CLI 模式下的警告行为 [F-008]：

| 属性/方法 | 说明 |
|-----------|------|
| `is_cli` | 布尔标志，是否运行在 CLI 模式 |
| `warn(msg)` | CLI 模式下打印到 stderr，否则调用 `warnings.warn()` |
| `set_cli()` | 上下文管理器，临时设置 `is_cli=True` |

```python
context = _Context()  # 单例 [F-009]

# CLI 中使用
with context.set_cli():
    pack(...)  # 警告信息输出到 stderr
```

## pack() 便捷函数

模块级 `pack()` 函数是 `CondaEnv` 的便捷封装 [F-024]：

1. 根据 `name`/`prefix` 参数选择环境定位方式
2. 调用 `CondaEnv.from_name()`/`from_prefix()`/`from_default()` 创建环境对象
3. 按顺序应用 `filters` 列表中的 `(kind, pattern)` 过滤
4. 调用 `env.pack()` 执行打包

```python
def pack(
    name=None, prefix=None, output=None, format="infer",
    arcroot="", dest_prefix=None,
    parcel_root=None, parcel_name=None, parcel_version=None, parcel_distro=None,
    verbose=False, force=False, compress_level=4, n_threads=1,
    zip_symlinks=False, zip_64=True,
    filters=None,                    # 额外参数：过滤器列表
    ignore_editable_packages=False,  # 额外参数：跳过editable检查
    ignore_missing_files=False,      # 额外参数：跳过缺失文件检查
):
```

## 相关概念

- [架构总览](02-architecture-overview.md)
- [环境加载与文件收集](04-environment-loading.md)
- [打包流程与 Packer](05-packing-process.md)
