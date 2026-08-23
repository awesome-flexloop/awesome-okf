---
type: Reference
title: formats.py 归档格式模块源码
description: conda-pack 归档格式模块源码索引，包含 archive 工厂函数、TarArchive/ZipArchive/SquashFSArchive/NoArchive 类和并行压缩写入器。
tags: [conda-pack, source, formats, archive]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T05:40:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T06:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: conda-pack-formats
    resource: conda_pack/formats.py
    title: conda-pack formats.py
---

# formats.py 归档格式模块源码

`conda_pack/formats.py` 是归档格式模块（约577行），实现了多种归档格式的抽象和并行压缩支持。

## 关键定义

| 定义 | 行号 | 说明 |
|------|------|------|
| `archive(fileobj, path, arcroot, format, ...)` | L32-L104 | 归档工厂函数，根据 format 返回对应 Archive 实例 |
| `_parse_n_threads(n_threads)` | L23-L29 | 解析线程数参数（-1 表示所有 CPU 核心） |

## 归档类继承关系

```
ArchiveBase (抽象基类)
├── TarArchive          # tar 系列格式（.tar/.tar.gz/.tar.bz2/.tar.xz/.tar.zst）
├── ZipArchive          # zip 格式
├── SquashFSArchive     # squashfs 格式（调用外部 mksquashfs）
└── NoArchive           # 无归档，直接复制到目录
```

## ArchiveBase 基类

| 方法 | 行号 | 说明 |
|------|------|------|
| `add(source, target)` | L293-L295 | 添加文件到归档（拼接 arcroot） |
| `add_bytes(source, sourcebytes, target)` | L297-L299 | 添加内存字节数据到归档 |

## TarArchive 类

| 方法/属性 | 行号 | 说明 |
|------|------|------|
| `__init__(fileobj, arcroot, close_file, mode, compresslevel, mtime)` | L303-L311 | 初始化 tar 归档 |
| `__enter__()` | L313-L321 | 打开 tarfile（Windows 上 dereference=True） |
| `__exit__()` | L323-L326 | 关闭 tarfile 和底层文件 |
| `_add(source, target)` | L328-L336 | 添加文件（conda-unpack 特殊处理 mtime） |
| `_add_bytes(source, sourcebytes, target)` | L338-L341 | 添加字节数据 |

## ZipArchive 类

| 方法/属性 | 行号 | 说明 |
|------|------|------|
| `__init__(fileobj, arcroot, compresslevel, zip_symlinks, zip_64)` | L358-L363 | 初始化 zip 归档 |
| `__enter__()` | L365-L370 | 打开 zipfile（ZIP_DEFLATED 压缩） |
| `__exit__()` | L372-L377 | 处理 LargeZipFile 异常 |
| `_add(source, target)` | L379-L419 | 添加文件（处理符号链接、dangling link 错误） |
| `_add_bytes(source, sourcebytes, target)` | L421-L423 | 添加字节数据 |

## SquashFSArchive 类

| 方法/属性 | 行号 | 说明 |
|------|------|------|
| `__init__(fileobj, target_path, arcroot, n_threads, ...)` | L430-L440 | 需要外部 mksquashfs 命令 |
| `__enter__()` | L442-L447 | 创建临时 staging 目录 |
| `__exit__()` | L449-L450 | 清理临时目录 |
| `mksquashfs_from_staging()` | L452-L489 | 批量执行 mksquashfs 命令 |
| `_add(source, target)` | L498-L526 | 硬链接优先的文件添加 |
| `_add_bytes(source, sourcebytes, target)` | L528-L533 | 添加字节数据到 staging |

## NoArchive 类

| 方法/属性 | 行号 | 说明 |
|------|------|------|
| `__init__(output, arcroot)` | L538-L541 | 直接复制到输出目录 |
| `_add(source, target)` | L556-L570 | 硬链接/复制文件或创建目录 |
| `_add_bytes(source, sourcebytes, target)` | L572-L577 | 写入字节数据 |

## 并行压缩写入器

| 类 | 行号 | 说明 |
|------|------|------|
| `ParallelFileWriter` | L126-L204 | 并行压缩基类（生产者-消费者模式） |
| `ParallelGzipFileWriter` | L207-L244 | 多线程 gzip 压缩（block_size=256KiB） |
| `ParallelBZ2FileWriter` | L247-L266 | 多线程 bzip2 压缩 |
| `ParallelXZFileWriter` | L269-L289 | 多线程 xz/lzma 压缩 |
| `ParallelZstdFileWriter` | L107-L123 | zstandard 压缩（使用 zstandard 库的 stream_writer） |

### 并行压缩架构

```
主线程（生产者）          Queue            线程池（消费者）
┌─────────┐         ┌──────────┐      ┌─────────────────┐
│ write() │────────→│ buffers  │─────→│ ThreadPool      │
│ 缓冲数据 │         │ (max=n)  │      │ _compress()     │
│ 满块入队 │         └──────────┘      │ 压缩后写入fileobj│
└─────────┘                           └─────────────────┘
```
