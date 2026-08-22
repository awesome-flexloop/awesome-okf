---
type: Pattern
title: 哨兵文件原子发布模式
description: 写入所有数据文件后再写入一个空哨兵文件标记完成，消费者仅检查哨兵文件存在性即可判断数据完整性，无需文件锁
tags: [sentinel-file, atomic-publish, marker-file, lock-free, filesystem, atomicity]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T16:30:00+08:00" }
status: stable
source: repo2jupyterlite
applicability: 静态站点构建、文件上传、目录发布、任何需要原子性"全部完成"语义的文件系统操作
---

# 哨兵文件原子发布模式

## 问题

构建过程会产生多个输出文件（HTML、JS、CSS、WASM内核、notebook等）。在构建过程中，这些文件逐步写入输出目录。如果消费者（HTTP请求）在构建未完成时访问文件：

- 可能读到不完整的HTML
- 可能请求尚不存在的JS/CSS文件
- 可能在构建失败时访问到半完成的站点

传统方案使用文件锁（flock/fcntl），但在跨进程/跨容器/跨网络文件系统（NFS/S3）上不可靠，且增加实现复杂度。

## 解决方案

**最后写入哨兵文件**标记构建完成，消费者只检查哨兵文件：

```python
class LocalFilesystemPublisher(Publisher):
    async def upload(self, source_dir, slug):
        # 对于零拷贝构建，source_dir就是最终目录
        # 所有文件已被repo2jupyterlite写入
        # 最后只写一个空文件标记完成
        with open(output_dir_prefix / slug / ".completed-sentinel", "w") as f:
            f.write("")

    async def exists(self, slug):
        # 只检查哨兵文件是否存在
        return (output_dir_prefix / slug / ".completed-sentinel").exists()
```

## 原子性保证

```
构建开始:
  mkdir output/gh-user/repo/sha/
  写入 lab/index.html        ← 部分文件已写入
  写入 pyodide/pyodide.js    ← 更多文件
  写入 kernels/...           ← 还在写...
  → 此时 exists() 返回 False，不会服务文件 ←

构建完成:
  写入 .completed-sentinel   ← 最后一步！
  → exists() 返回 True，开始服务文件 ←

构建失败:
  异常导致进程退出
  .completed-sentinel 从未写入
  → exists() 返回 False，后续请求重新构建 ←
```

文件系统保证：`open()` + `write("")` + `close()` 对空文件是原子操作（文件要么不存在，要么存在且完整）。

## 关键原则

1. **哨兵文件最后写入**：所有数据文件写入完成后才创建哨兵文件
2. **哨兵文件为空**：不携带任何数据，仅作为存在性标记
3. **消费者只检查哨兵**：不检查目录是否存在、不检查文件数量、不校验checksum
4. **重新构建前清理**：`get_target_dir`在构建前`shutil.rmtree`删除旧目录（包含旧哨兵）
5. **命名以`.`开头**：哨兵文件是隐藏文件（`.completed-sentinel`），不会被Web服务器当作内容服务

## 云存储适配

S3/对象存储同样适用：

```python
async def upload(self, source_dir, slug):
    # 第一步：上传所有构建文件
    for file_path in Path(source_dir).rglob("*"):
        if file_path.is_file():
            s3.upload_file(str(file_path), bucket, s3_key(file_path))
    
    # 第二步：最后上传哨兵文件
    s3.put_object(Bucket=bucket, Key=s3_key(slug, ".completed-sentinel"), Body=b"")

async def exists(self, slug):
    try:
        s3.head_object(Bucket=bucket, Key=s3_key(slug, ".completed-sentinel"))
        return True
    except:
        return False
```

在S3上，`put_object`是原子的——哨兵文件要么不存在，要么存在。

## 与零拷贝构建的协同

零拷贝构建直接写入最终目录（不使用临时目录），哨兵文件更加重要：

```python
@contextmanager
def get_target_dir(self, slug):
    output_dir = output_dir_prefix / slug
    if output_dir.exists():
        shutil.rmtree(output_dir)  # 清理旧构建（删除哨兵）
    yield output_dir               # CLI直接写入此目录
    # upload()在yield返回后被调用，写入哨兵
```

构建流程：
1. `get_target_dir()` 清理旧目录（哨兵消失 → exists()=False）
2. CLI在目录中构建所有文件（此时exists()=False）
3. `upload()` 写入哨兵（exists()=True）

## 反模式

- ❌ 检查目录是否存在来判断构建完成（目录在构建开始就创建了）
- ❌ 检查特定文件是否存在（该文件可能先写完但其他文件未写完）
- ❌ 使用文件锁协调（跨平台不可靠，增加复杂度）
- ❌ 哨兵文件先于数据文件写入（破坏原子性）
- ❌ 构建失败时删除部分文件（不需要，哨兵不存在即表示失败）
- ❌ 哨兵文件包含内容（引入"哨兵文件本身写入不完整"的问题）

## 适用场景

- 静态站点构建输出（Jekyll、Hugo、JupyterLite）
- 云存储批量上传（S3/GCS多文件上传）
- CI/CD构建产物发布
- 数据管道输出目录标记
- 任何"多个文件组成一个逻辑单元"的原子发布场景
- 容器镜像分层（类似思想：最后一层标记完成）
