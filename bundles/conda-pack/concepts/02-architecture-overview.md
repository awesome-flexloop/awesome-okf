---
type: "concept"
title: "架构总览"
description: conda-pack 的整体架构、模块分层、核心数据流和打包流程总览。
tags: [conda-pack, architecture, modules, dataflow]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T05:45:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T06:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: core
    resource: /references/core-source.md
    title: core.py 核心模块源码
  - id: formats
    resource: /references/formats-source.md
    title: formats.py 归档格式模块源码
  - id: prefixes
    resource: /references/prefixes-source.md
    title: prefixes.py 前缀替换模块源码
  - id: cli
    resource: /references/cli-source.md
    title: cli.py 与辅助模块源码
---

# 架构总览

conda-pack 是一个精简的 Python 库/CLI 工具，核心代码仅约 2500 行，分为 7 个模块，没有复杂的依赖链。

## 模块结构

```
conda_pack/
├── __init__.py        # 包入口，导出公开 API（4个对象）
├── core.py            # 核心逻辑（~1337行）：数据模型+环境加载+打包流程
├── cli.py             # CLI 入口（~183行）：argparse 参数解析
├── formats.py         # 归档格式（~577行）：Tar/Zip/SquashFS/NoArchive + 并行压缩
├── prefixes.py        # 前缀替换（~196行）：文本/二进制前缀替换，借鉴自 conda
├── compat.py          # 跨平台兼容（~45行）：平台检测、PY2/PY3 兼容
├── _progress.py       # 进度条（~99行）：简单文本进度条组件
└── scripts/
    ├── posix/         # POSIX 激活脚本（activate/deactivate/parcel + fish）
    └── windows/       # Windows 激活脚本（activate.bat/deactivate.bat）
```

## 模块依赖关系

```
cli.py ──→ core.py ──→ formats.py
              │            ↑
              ├──→ prefixes.py
              ├──→ _progress.py
              └──→ compat.py
```

- `cli.py` 依赖 `core.py` 的 `pack()` 函数和 `context`/`CondaPackException`
- `core.py` 是核心模块，依赖 `formats.py`（延迟导入）、`prefixes.py`、`_progress.py`、`compat.py`
- `formats.py` 依赖 `compat.py` 和 `core.py`（仅 `CondaPackException`）
- `prefixes.py` 是自包含模块，仅依赖标准库
- `compat.py` 和 `_progress.py` 是工具模块，无内部依赖
- `__init__.py` 从 `core.py` 重新导出公开 API [F-003]

## 公开 API

`__init__.py` 通过 `__all__` 导出 4 个公开对象 [F-003]：

| 导出对象 | 类型 | 说明 |
|---------|------|------|
| `CondaEnv` | 类 | 待打包 conda 环境的表示 |
| `CondaPackException` | 异常类 | 唯一的自定义异常 |
| `File` | 类 | 单个归档文件记录 |
| `pack` | 函数 | 模块级便捷打包函数 |

## 核心数据流

打包过程的完整数据流如下：

```
用户输入（name/prefix/output/format/...）
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ 1. 环境定位（name_to_prefix）                         │
│    通过 `conda info --json` 子进程解析环境路径          │
└─────────────────────┬───────────────────────────────┘
                      │ prefix
                      ▼
┌─────────────────────────────────────────────────────┐
│ 2. 环境加载（load_environment）                       │
│    ├─ 扫描 conda-meta/*.json 获取托管包列表            │
│    ├─ 从包缓存(pkgs/)加载每个包的文件列表              │
│    │  ├─ paths.json（新版）或 files + has_prefix     │
│    │  └─ 处理 noarch:python 路径重定向                │
│    ├─ 加载非托管文件（pip安装/手动放置的文件）          │
│    ├─ 检查可编辑包（editable packages）               │
│    └─ 检查缺失文件                                    │
│    输出: List[File]                                   │
└─────────────────────┬───────────────────────────────┘
                      │ List[File]
                      ▼
┌─────────────────────────────────────────────────────┐
│ 3. 文件过滤（exclude/include）                       │
│    按 fnmatch glob 模式过滤文件列表                    │
│    输出: List[File]（过滤后）                         │
└─────────────────────┬───────────────────────────────┘
                      │ filtered files
                      ▼
┌─────────────────────────────────────────────────────┐
│ 4. 归档写入（Packer.add → archive）                   │
│    ├─ 创建临时文件                                    │
│    ├─ 创建归档对象（TarArchive/ZipArchive/...）       │
│    ├─ 对每个文件:                                     │
│    │  ├─ file_mode=None → 直接添加                    │
│    │  ├─ conda-meta/*.json → 清除绝对路径后添加       │
│    │  ├─ 目录/符号链接 → 直接添加                     │
│    │  ├─ file_mode=text/binary → 读取→替换前缀→添加  │
│    │  └─ file_mode=unknown → 检测类型→替换前缀→添加  │
│    └─ 记录需要 conda-unpack 延迟修复的前缀            │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│ 5. 收尾（Packer.finish）                             │
│    ├─ 添加内置 activate/deactivate 脚本              │
│    ├─ 生成 conda-unpack 脚本（含 prefixes.py 代码）  │
│    ├─ Windows: 添加 cli-64.exe/32.exe 启动器         │
│    ├─ Parcel模式: 生成 parcel.json + conda_env.sh    │
│    └─ SquashFS: 执行 mksquashfs 批量压缩             │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│ 6. 原子交付                                          │
│    shutil.move(temp_path, output)                    │
│    输出: 归档文件路径                                 │
└─────────────────────────────────────────────────────┘
```

## 三种使用入口

conda-pack 提供三个层次的入口，满足不同使用场景：

### 1. CLI 入口（`conda-pack` 命令）

最简单的使用方式，通过 `cli.py:main()` 进入，适合命令行操作和脚本调用 [F-041]。

### 2. 便捷函数（`pack()`）

模块级函数，适合 Python 脚本中快速打包，一行代码完成环境定位+加载+过滤+打包 [F-024]。

### 3. 面向对象 API（`CondaEnv`）

通过 `CondaEnv.from_name()`/`from_prefix()`/`from_default()` 创建环境对象，支持链式调用 `exclude()`/`include()` 进行精细过滤，最后调用 `.pack()` 完成打包 [F-011]。适合需要复杂文件过滤或编程控制的场景。

## 关键设计决策

### 前缀占位符固定长度

`PREFIX_PLACEHOLDER = '/opt/anaconda1anaconda2anaconda3'` 长度固定为 22 字符 [F-005]。在二进制替换中，新前缀长度不能超过占位符长度，不足部分用 null 字节填充。这保证了二进制文件中字符串偏移量不变，不会破坏二进制结构 [F-052]。

### 两阶段前缀修复

1. **打包时修复**：对于 shebang 行和已知文本文件，在打包时直接将前缀重写为 `#!/usr/bin/env python` 形式或新前缀
2. **部署时修复**：对于无法在打包时确定目标路径的情况，将占位符写入归档，由 `conda-unpack` 在部署后完成替换 [F-036][F-038]

### 临时文件原子写入

打包过程先写入临时文件（`tempfile.mkstemp()`），全部成功后通过 `shutil.move()` 原子移动到目标位置 [F-020]。这避免了打包失败时留下损坏的部分文件。

### 并行压缩

gzip/bzip2/xz/zstd 压缩支持多线程并行，采用生产者-消费者模式：主线程将数据分块放入队列，线程池中的工作线程并行压缩，消费者线程顺序写入文件 [F-050]。

## 相关概念

- [conda-pack 简介](00-introduction.md)
- [5分钟快速上手](01-getting-started.md)
- [CondaEnv 与 File 数据模型](03-conda-env-and-file.md)
- [环境加载与文件收集](04-environment-loading.md)
