---
type: Reference
title: core.py 核心模块源码
description: conda-pack 核心模块源码索引，包含 CondaEnv、File、Packer、pack() 等核心类和函数的定义位置与签名。
tags: [conda-pack, source, core]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T05:40:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T06:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: conda-pack-core
    resource: conda_pack/core.py
    title: conda-pack core.py
---

# core.py 核心模块源码

`conda_pack/core.py` 是 conda-pack 的核心模块（约1337行），包含所有主要的数据模型、文件收集逻辑、打包流程和前缀处理。

## 关键定义

| 定义 | 行号 | 说明 |
|------|------|------|
| `CondaPackException` | L24-L26 | 唯一的自定义异常类，继承自 `Exception` |
| `PREFIX_PLACEHOLDER` | L30-L31 | 默认前缀占位符 `/opt/anaconda1anaconda2anaconda3`，字符串拆分避免意外出现 |
| `BIN_DIR` | L33 | 二进制目录：Windows 为 `Scripts`，POSIX 为 `bin` |
| `_Context` | L50-L67 | CLI 上下文管理类，控制 warn 行为（stderr vs warnings.warn） |
| `context` | L70 | `_Context` 单例实例 |
| `CondaEnv` | L73-L454 | 待打包 conda 环境的表示类 |
| `File` | L457-L485 | 单个归档文件记录，使用 `__slots__` 优化 |
| `pack()` | L488-L631 | 模块级便捷打包函数 |
| `Packer` | L1153-L1337 | 文件打包器，逐个添加文件到归档并处理前缀替换 |

## 核心函数

| 函数 | 行号 | 说明 |
|------|------|------|
| `find_site_packages(prefix)` | L634-L658 | 查找环境中的 Python site-packages 路径 |
| `check_no_editable_packages(prefix, site_packages)` | L661-L688 | 检查是否有可编辑安装的包（editable packages） |
| `name_to_prefix(name=None)` | L691-L715 | 通过 `conda info --json` 将环境名解析为路径 |
| `read_noarch_type(pkg)` | L718-L728 | 读取包的 noarch 类型（python/generic/None） |
| `read_has_prefix(path)` | L731-L742 | 解析 has_prefix 文件，返回路径→(placeholder, mode)映射 |
| `load_files(prefix)` | L745-L785 | 遍历环境目录收集所有文件，忽略特殊目录 |
| `managed_file(...)` | L788-L804 | 创建一个 conda 托管的 File 对象 |
| `load_managed_package(...)` | L807-L854 | 从包缓存加载一个托管包的所有文件 |
| `load_environment(prefix, ...)` | L886-L1003 | 加载环境中的所有文件（托管+非托管），核心文件收集逻辑 |
| `rewrite_shebang(data, target, prefix)` | L1006-L1035 | 将 shebang 重写为 `#!/usr/bin/env program` 形式 |
| `rewrite_conda_meta(source)` | L1038-L1054 | 清除 conda-meta JSON 中的绝对路径字段 |
| `is_binary_file(data)` | L1145-L1150 | 通过尝试 UTF-8 解码判断是否为二进制文件 |

## CondaEnv 类关键方法

| 方法 | 行号 | 说明 |
|------|------|------|
| `from_name(name, **kwargs)` | L134-L147 | 从环境名创建 CondaEnv（类方法） |
| `from_prefix(prefix, **kwargs)` | L149-L164 | 从路径创建 CondaEnv（类方法） |
| `from_default(**kwargs)` | L166-L174 | 从当前激活环境创建 CondaEnv（类方法） |
| `exclude(pattern)` | L176-L201 | 排除匹配 glob 模式的文件 |
| `include(pattern)` | L203-L226 | 重新包含之前排除的文件 |
| `pack(...)` | L309-L454 | 执行打包，返回输出文件路径 |

## Packer 类关键方法

| 方法 | 行号 | 说明 |
|------|------|------|
| `__init__(prefix, archive, dest_prefix, parcel)` | L1154-L1161 | 初始化打包器 |
| `add(file)` | L1163-L1249 | 添加单个文件到归档，处理前缀替换 |
| `finish()` | L1263-L1337 | 完成打包：添加激活脚本、生成 conda-unpack、处理 parcel |

## 模板字符串

| 模板 | 行号 | 说明 |
|------|------|------|
| `_parcel_json_template` | L1057-L1086 | Cloudera Parcel JSON 元数据模板 |
| `_parcel_package_template` | L1088-L1092 | Parcel 中单个包的记录模板 |
| `_conda_unpack_template` | L1094-L1140 | 自动生成的 conda-unpack 脚本模板 |
