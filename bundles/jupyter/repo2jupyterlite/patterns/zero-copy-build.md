---
type: Pattern
title: 零拷贝构建模式
description: 构建工具直接输出到最终服务目录，避免"构建到临时目录→拷贝到最终目录"的两次I/O开销，配合哨兵文件保证原子性
tags: [zero-copy, build-optimization, direct-output, io-optimization, sentinel-coordination]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T16:30:00+08:00" }
status: stable
source: repo2jupyterlite
applicability: 本地文件系统构建输出、静态站点生成、包管理器安装、任何"构建→服务"管道
---

# 零拷贝构建模式

## 问题

典型的"构建→发布"流程使用临时目录模式：

1. 创建临时目录
2. 构建工具输出到临时目录
3. 构建完成后，将临时目录拷贝/移动到最终服务目录
4. 清理临时目录

这存在两个问题：
- **双倍I/O开销**：构建产物（JupyterLite站点可达数十MB）需要写入磁盘两次
- **原子性窗口**：拷贝过程中服务目录处于不一致状态，可能被并发请求读到半完成文件
- **额外磁盘空间**：峰值时刻需要2倍磁盘空间（临时目录+最终目录并存）

## 解决方案

让构建工具直接将文件输出到最终服务目录，使用哨兵文件保证原子性：

```python
class LocalFilesystemPublisher(Publisher):
    @contextmanager
    def get_target_dir(self, slug):
        # 直接返回最终输出目录（不是临时目录！）
        output_dir = output_dir_prefix / slug
        if output_dir.exists():
            shutil.rmtree(output_dir)  # 清理旧构建（同时删除哨兵）
        yield output_dir               # CLI直接构建到最终目录
        # yield返回后，upload()写入哨兵文件
```

对比基类（临时目录模式）：

```python
class Publisher:
    @contextmanager
    def get_target_dir(self, slug):
        tmpdirname = tempfile.mktemp()   # 临时目录
        try:
            yield tmpdirname             # 构建到临时目录
        finally:
            shutil.rmtree(tmpdirname)    # 清理
        # 子类的upload()负责将文件从tmpdirname拷贝到最终位置
```

## 原子性保障

零拷贝构建依赖哨兵文件模式保证消费者不会读到不完整内容：

```
1. shutil.rmtree(output_dir)        → 删除旧目录（哨兵消失，exists()=False）
2. yield output_dir                 → CLI构建到output_dir
   ├── 写入 lab/index.html
   ├── 写入 pyodide/pyodide.js
   ├── 写入 kernels/...
   └── ...（此时exists()=False，不会服务文件）
3. await publisher.upload(d, slug)  → 写入 .completed-sentinel（exists()=True）
```

步骤1删除哨兵后，即使构建过程中有请求到达，`exists()`返回False，会触发重新构建或等待。步骤3才使构建产物可见。

## 前提条件

零拷贝模式需要满足以下条件：

1. **本地文件系统**：构建工具可以直接写入最终目标位置（S3等云存储需要先构建到本地临时目录再上传）
2. **构建前清理**：重新构建时先删除旧目录，防止旧文件残留
3. **哨兵协调**：必须配合哨兵文件模式，否则构建过程中会读到不完整文件
4. **单实例部署**：本地文件系统零拷贝适用于单实例；多实例需要共享存储

## 云存储场景的回退

当无法直接写入目标位置（如S3），回退到基类的临时目录模式：

```python
class S3Publisher(Publisher):
    @contextmanager
    def get_target_dir(self, slug):
        tmpdirname = tempfile.mktemp()  # 必须用临时目录
        try:
            yield tmpdirname
        finally:
            shutil.rmtree(tmpdirname)
    
    async def upload(self, source_dir, slug):
        for file_path in Path(source_dir).rglob("*"):
            if file_path.is_file():
                s3.upload_file(...)  # 从临时目录上传到S3
        # 最后上传哨兵
        s3.put_object(..., Key=s3_key(slug, ".completed-sentinel"), Body=b"")
```

## 性能收益

以JupyterLite构建为例：
- 构建产物约30-50MB（Pyodide内核+WASM+notebook）
- 临时目录模式：写入30-50MB到tmp → 拷贝30-50MB到output = 60-100MB I/O
- 零拷贝模式：直接写入output = 30-50MB I/O
- **I/O减少50%**，构建完成到可用的等待时间更短

## 关键原则

1. **清理优先**：构建前先删除旧输出目录（防止旧文件残留和删除旧哨兵）
2. **哨兵后置**：构建完成后才写入哨兵（与临时目录模式的原子性保证一致）
3. **接口兼容**：通过context manager的yield抽象，调用方无需知道目标是临时目录还是最终目录
4. **异常安全**：构建失败时哨兵未写入，目录保持不完整状态但不会被服务
5. **可选优化**：零拷贝是LocalFilesystemPublisher的优化，不是所有Publisher必须实现的——云存储场景回退到临时目录模式即可

## 反模式

- ❌ 直接在最终目录构建但不使用哨兵（消费者读到不完整文件）
- ❌ 零拷贝+不清理旧目录（旧构建的残留文件污染新构建）
- ❌ 在S3等远程存储上尝试零拷贝（无法直接写入S3文件系统）
- ❌ 移动（rename）而非删除重建（原子rename在跨文件系统时失败）

## 适用场景

- 本地文件系统静态站点生成输出
- 包管理器本地安装（`npm install`、`pip install`到目标目录）
- 构建产物与服务目录在同一文件系统上的单实例部署
- CI/CD构建步骤直接输出到部署目录
- 任何"I/O开销是瓶颈"且"构建工具接受目标目录参数"的场景
