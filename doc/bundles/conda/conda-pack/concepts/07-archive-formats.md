---
type: "concept"
title: "归档格式体系"
description: formats.py 中的归档抽象层——ArchiveBase 基类、TarArchive/ZipArchive/SquashFSArchive/NoArchive 四种归档实现，以及多线程并行压缩机制。
tags: [conda-pack, archive, tar, zip, squashfs, parallel-compression]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T05:45:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T06:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: formats
    resource: /references/formats-source.md
    title: formats.py 归档格式模块源码
---

# 归档格式体系

conda-pack 支持 9 种归档格式，通过 `ArchiveBase` 抽象基类统一接口，使用工厂函数 `archive()` 根据格式创建对应的归档实例。

## archive() 工厂函数

```python
def archive(fileobj, path, arcroot, format, compress_level=4,
            zip_symlinks=False, zip_64=True, n_threads=1,
            verbose=False, output=None, mtime=None):
```

根据 `format` 参数返回对应的归档上下文管理器 [F-044]：

| format | 返回类型 | 说明 |
|--------|---------|------|
| `'zip'` | `ZipArchive` | ZIP 格式 |
| `'tar.gz'`/`'tgz'`/`'parcel'` | `TarArchive` + gzip | gzip 压缩 tar |
| `'tar.bz2'`/`'tbz2'` | `TarArchive` + bzip2 | bzip2 压缩 tar |
| `'tar.xz'`/`'txz'` | `TarArchive` + xz | xz/lzma 压缩 tar |
| `'tar.zst'`/`'tzst'` | `TarArchive` + zstd | zstandard 压缩 tar |
| `'tar'` | `TarArchive` | 无压缩 tar |
| `'squashfs'` | `SquashFSArchive` | SquashFS 只读文件系统 |
| `'no-archive'` | `NoArchive` | 直接复制到目录（无归档） |

线程数解析：`n_threads=-1` 表示使用所有 CPU 核心 [F-044]。

## ArchiveBase 基类

所有归档类继承自 `ArchiveBase`，提供统一的添加接口 [F-045]：

```python
class ArchiveBase:
    def add(self, source, target):
        """添加文件到归档"""
        target = os.path.join(self.arcroot, target)
        self._add(source, target)

    def add_bytes(self, source, sourcebytes, target):
        """添加内存字节数据到归档"""
        target = os.path.join(self.arcroot, target)
        self._add_bytes(source, sourcebytes, target)
```

- `arcroot` 是归档内环境的根路径前缀
- `add()` 添加磁盘上的文件
- `add_bytes()` 添加内存中的字节内容（用于动态生成的文件如 conda-unpack）
- 子类实现 `_add()` 和 `_add_bytes()` 抽象方法

## TarArchive

基于 Python 标准库 `tarfile` 模块 [F-046]：

```python
class TarArchive(ArchiveBase):
    def __enter__(self):
        self.archive = tarfile.open(fileobj=self.fileobj,
                                    dereference=on_win,  # Windows 上解引用符号链接
                                    mode=self.mode)
```

### 关键特性

- **Windows 特殊处理**：`dereference=on_win`，因为硬链接在 Windows 上会破坏 tar 格式
- **conda-unpack mtime**：`bin/conda-unpack` 文件的 mtime 被设置为 `conda-meta/history` 的 mtime，确保构建可重现
- **并行压缩**：单线程使用标准库压缩器，多线程使用自定义的 ParallelFileWriter
- **add_bytes**：通过 `tarfile.gettarinfo()` 创建 TarInfo，设置 size 后用 `addfile()` 写入

### tar 压缩模式

| 模式 | 单线程 | 多线程 |
|------|--------|--------|
| tar.gz / tgz / parcel | `gzip.GzipFile` | `ParallelGzipFileWriter` |
| tar.bz2 / tbz2 | `tarfile mode='w:bz2'` | `ParallelBZ2FileWriter` |
| tar.xz / txz | `tarfile mode='w:xz'` | `ParallelXZFileWriter` |
| tar.zst / tzst | `ParallelZstdFileWriter`（无单线程回退） | 同左 |
| tar | `tarfile mode='w'`（无压缩） | 同左 |

## ZipArchive

基于 Python 标准库 `zipfile` 模块 [F-047]：

```python
class ZipArchive(ArchiveBase):
    def __enter__(self):
        self.archive = zipfile.ZipFile(self.fileobj, "w",
                                       allowZip64=self.zip_64,
                                       compresslevel=self.compresslevel,
                                       compression=zipfile.ZIP_DEFLATED)
```

### 关键特性

- **ZIP64 扩展**：默认启用（`zip_64=True`），支持 >4GB 大文件；可通过 `--no-zip-64` 禁用
- **压缩级别**：使用 ZIP_DEFLATED 压缩，但注意 `compresslevel` 参数对 zip 的效果（0-9）
- **符号链接处理**：
  - `zip_symlinks=False`（默认）：复制链接指向的实际文件，更兼容但占更多空间
  - `zip_symlinks=True`：存储符号链接本身（存储链接目标路径），省空间但部分 unzip 实现不支持
- **Dangling link 检测**：如果符号链接指向的目标不存在，抛出明确错误
- **空目录处理**：递归遍历时保留空目录
- **LargeZipFile 处理**：`__exit__` 中捕获 `LargeZipFile` 异常并给出友好提示

### ZIP 符号链接存储

启用 `zip_symlinks` 时，符号链接以特殊方式存储：
- `create_system = 3`（Unix 系统）
- `external_attr` 设置文件模式位（含 symlink 标志）
- 内容存储为链接目标路径字符串

## SquashFSArchive

通过调用外部 `mksquashfs` 命令创建 SquashFS 镜像 [F-048]：

### 为什么需要外部命令？

SquashFS 是 Linux 内核支持的只读压缩文件系统格式，Python 标准库没有原生支持。conda-pack 通过 staging 目录模式工作：

1. 创建临时 staging 目录
2. 将所有文件添加到 staging 目录（使用硬链接优化）
3. Packer.finish() 时一次性调用 `mksquashfs` 压缩整个目录
4. 清理临时目录

### 关键特性

- **硬链接优先**：同源设备且同用户时使用 `os.link()` 硬链接（零拷贝），否则使用 `shutil.copy2()`
- **压缩算法选择**：
  - `compress_level=0`：无压缩（`-noI -noD -noF -noX`）
  - `compress_level=9`：xz 压缩
  - 其他：zstd 压缩（级别映射：`level/8*20`），256KB block size
- **mksquashfs 选项**：`-noappend`（不追加）、`-processors N`（线程数）、`-quiet`/`-no-progress`
- **依赖检查**：初始化时检查 `mksquashfs` 是否在 PATH 中

```bash
mksquashfs <staging_dir> <output> -noappend -processors N \
    -comp zstd -Xcompression-level <level> -b 262144
```

## NoArchive

不创建归档文件，直接将文件复制到输出目录 [F-049]：

- 用于本地部署场景，省去打包/解压步骤
- 同样使用硬链接优化
- 文件直接复制，目录用 `os.mkdir()` 创建
- 字节内容通过 `_add_bytes()` 写入文件

## 并行压缩架构

对于 gzip/bzip2/xz 三种格式，conda-pack 实现了多线程并行压缩，采用**生产者-消费者模式** [F-050]：

```
主线程（生产者）              压缩队列               消费者线程
┌─────────────┐         ┌──────────────┐      ┌──────────────────┐
│ write(data) │────────→│ Queue(max=N) │─────→│ _consumer()      │
│ 累积缓冲区   │         │              │      │ ThreadPool.imap  │
│ 满块入队     │         └──────────────┘      │ _compress() 压缩 │
└─────────────┘                               │ 写入 fileobj     │
                                              └──────────────────┘
```

### ParallelFileWriter 基类

```python
class ParallelFileWriter:
    def __init__(self, fileobj, compresslevel, n_threads, mtime):
        self.pool = ThreadPool(n_threads)
        self.compress_queue = Queue(maxsize=n_threads)
        self._consumer_thread = threading.Thread(target=self._consumer)
        self._consumer_thread.daemon = True
        self._consumer_thread.start()
```

- 主线程调用 `write(data)` 累积数据到缓冲区
- 缓冲区超过 `_block_size` 时将数据块列表放入队列
- 消费者线程从队列取出数据，通过 `ThreadPool.imap()` 并行压缩
- 压缩结果按顺序写入输出文件
- `close()` 时刷新剩余数据，发送 None 哨兵，等待消费者线程结束

### 各压缩器参数

| 压缩器 | _block_size | 压缩库 | 特殊处理 |
|--------|-------------|--------|---------|
| ParallelGzipFileWriter | 256 KiB | zlib | 计算 CRC32、写 gzip header/footer |
| ParallelBZ2FileWriter | level×100 KiB | bz2 | 无 header/footer |
| ParallelXZFileWriter | 4×max(1,2^(level-4)) MiB | lzma | 无 header/footer |
| ParallelZstdFileWriter | N/A（流式） | zstandard | 使用 `stream_writer`，支持 threads 参数 |

### 为什么块大小大于字典大小？

并行压缩的块之间无法共享字典（串行操作），因此块大小需要大于压缩器的最大字典大小，否则压缩率会显著下降：
- gzip 最大字典 32 KiB，块大小 256 KiB（8倍）[F-050]
- xz 字典大小根据 level 变化（64 KiB - 32 MiB），块大小设为 4 倍
- Pigz（并行 gzip 参考实现）使用 128 KiB 块，但额外维护运行字典

### Gzip 格式细节

ParallelGzipFileWriter 手动写入 gzip 格式的 header 和 footer：
- Header: `\x1f\x8b\x08\x00<mtime>\x02\xff`（固定头+修改时间+最大压缩标志）
- 每块使用 Z_FULL_FLUSH 刷新，确保块可独立解压
- Footer: CRC32（4字节小端序）+ 原始大小（4字节小端序）

## arcroot 参数

`arcroot` 指定环境在归档内的相对根路径：
- 默认为 `""`（空字符串），环境文件直接在归档根目录
- 可设置为子目录，如 `"my_env"`，则所有文件在归档的 `my_env/` 目录下
- Parcel 模式自动设置 arcroot 为 `parcel_name-parcel_version`

```python
# 环境在归档根目录
pack(arcroot="")  # tar xzf 后直接得到 bin/, lib/, etc.

# 环境在子目录
pack(arcroot="my_env")  # tar xzf 后得到 my_env/bin/, my_env/lib/, etc.
```

## 相关概念

- [打包流程与 Packer](05-packing-process.md)
- [5分钟快速上手](01-getting-started.md)
