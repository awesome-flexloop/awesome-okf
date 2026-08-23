---
type: "concept"
title: "包流式处理"
sources:
  - id: rattler-package-streaming
    resource: /references/rattler-source.md
    title: "Rattler Crates 结构 - rattler_package_streaming"
---

# 包流式处理

`rattler_package_streaming` 负责 conda 包归档的下载、解压、读取和写入。conda 包有两种格式：传统的 `.tar.bz2` 和新的 `.conda`（基于 Zstandard 的双归档格式）。该 crate 提供了统一的抽象来处理这两种格式，支持同步和异步（tokio）操作。

## Conda 包格式

### .tar.bz2（旧格式）

传统的 conda 包是一个 tar.bz2 压缩归档，包含：
- `info/` 目录：元数据（`index.json`、`about.json`、`paths.json`、`files`、`recipe/` 等）
- `pkg/` 目录：实际安装的文件

整个 tarball 使用 bzip2 压缩，文件需要按顺序读取（tar 格式特性）。

### .conda（新格式）

新的 `.conda` 格式是一个 Zstandard 压缩的 zip 文件，内部包含两个 tar.zst 归档：
- `metadata.tar.zst`：仅包含 `info/` 元数据（小文件，快速读取）
- `pkg.tar.zst`：包含实际的 `pkg/` 文件（大文件，延迟解压）

相比 `.tar.bz2`，`.conda` 格式的优势：
- **更快解压**：Zstandard 比 bzip2 快 3-5 倍
- **元数据优先**：可以先读取 metadata.tar.zst 获取包信息，不必下载完整包
- **随机访问**：zip 格式允许只解压特定文件
- **多线程压缩**：zstd 支持多线程，构建更快

## 核心模块

rattler_package_streaming 的模块按功能和运行时划分：

```
rattler_package_streaming/
├── read.rs       # 同步读取包内容（从 Read 类型）
├── seek.rs       # 同步从 Seek 类型读取（支持随机访问）
├── fs.rs         # 同步文件系统操作（解压到目录）
├── write.rs      # 创建/写入包归档
├── reqwest/      # 异步 HTTP 下载（基于 reqwest）
├── tokio/
│   ├── fs.rs     # 异步文件系统操作（tokio）
│   └── ...       # 其他异步模块
├── extract.rs    # 包提取逻辑
└── lib.rs        # 公开 API 导出
```

## 读取包元数据

### 同步读取（从文件）

```rust
use rattler_package_streaming::read;
use std::fs::File;
use std::path::Path;

// 读取包的 index.json（元数据）
let file = File::open("numpy-1.26.0-py312habcd_0.conda")?;
let index_json: rattler_conda_types::package::IndexJson =
    read::read_index_json(file)?;

println!("包名: {}", index_json.name);
println!("版本: {}", index_json.version);
println!("依赖: {:?}", index_json.depends);
```

### 从 HTTP 异步下载并读取元数据

```rust
use rattler_package_streaming::reqwest::tokio::read_repo_data_package;
use reqwest_middleware::ClientWithMiddleware;

let client = ClientWithMiddleware::default();
let url = "https://conda.anaconda.org/conda-forge/linux-64/numpy-1.26.0-py312habcd_0.conda";

// 流式下载，只读取 metadata 部分（对于 .conda 格式不需要下载整个包）
let (index_json, package_bytes) = read_repo_data_package(
    &client,
    url.parse()?,
    None,  // 取消令牌
).await?;

println!("包名: {}", index_json.name);
```

**关键优化**：对于 `.conda` 格式，`read_repo_data_package` 利用 HTTP Range 请求只下载 metadata.tar.zst 部分（通常只有几 KB），不必下载整个包（可能几十 MB）。

## 解压包到目录

```rust
use rattler_package_streaming::fs::extract;
use std::path::Path;

// 解压 .conda 或 .tar.bz2 包到指定目录
// 自动检测格式
extract(
    "numpy-1.26.0-py312habcd_0.conda".as_ref(),  // 包文件路径
    Path::new("/tmp/numpy_extracted"),            // 目标目录
)?;
```

解压后目标目录结构：
```
/tmp/numpy_extracted/
├── info/
│   ├── index.json
│   ├── about.json
│   ├── paths.json
│   ├── files
│   └── ...
└── site-packages/
    └── numpy/
        └── ...
```

## 创建 conda 包

```rust
use rattler_package_streaming::write::{write_conda_package, write_tar_bz2_package};
use std::path::Path;

// 创建 .conda 格式包
write_conda_package(
    Path::new("/path/to/extracted/package_dir"),  // 已解压的包目录
    Path::new("output.conda"),                     // 输出文件
    None,                                          // 压缩级别（默认）
)?;

// 创建 .tar.bz2 格式包
write_tar_bz2_package(
    Path::new("/path/to/extracted/package_dir"),
    Path::new("output.tar.bz2"),
    9,  // bzip2 压缩级别
)?;
```

## 异步下载与解压

```rust
use rattler_package_streaming::reqwest::tokio::download_and_extract;
use rattler_package_streaming::DownloadReporter;

// 异步下载并解压到目录
download_and_extract(
    &client,                      // HTTP 客户端
    url,                          // 包 URL
    &target_directory,            // 解压目标
    None,                         // SHA256 校验
    Some(Box::new(MyReporter)),   // 进度报告器
    None,                         // 取消令牌
).await?;
```

### DownloadReporter 进度报告

```rust
pub trait DownloadReporter: Send + Sync {
    fn on_download_start(&self, url: &Url, total_size: Option<u64>);
    fn on_download_progress(&self, url: &Url, bytes_downloaded: u64, total_size: Option<u64>);
    fn on_download_complete(&self, url: &Url, bytes_downloaded: u64);
}
```

## 哈希校验

包下载后必须进行哈希校验以确保完整性：

```rust
use rattler_digest::{Md5, Sha256};
use rattler_package_streaming::fs::extract_with_sha256;

// 下载后验证 SHA256
extract_with_sha256(
    &client,
    url,
    target_dir,
    &expected_sha256_hash,
    Some(Box::new(reporter)),
    cancellation_token,
).await?;
```

当校验失败时，返回 `ExtractError::HashMismatch` 错误，包含期望哈希和实际哈希。

## 包链接方式

解压包到包缓存目录后，安装时通过以下方式链接到环境前缀：

| 链接方式 | 说明 | 跨文件系统 | 速度 | 磁盘空间 |
|---------|------|-----------|------|---------|
| **Hardlink** | 硬链接，多个环境共享同一 inode | ❌ 需同一文件系统 | ⚡ 极快 | 极小（无复制） |
| **Symlink** | 符号链接 | ✅ | ⚡ 快 | 极小（路径引用） |
| **Copy** | 复制文件 | ✅ | 🐢 慢 | 大（完整复制） |
| **Directory** | 创建目录 | ✅ | ⚡ 快 | 无 |

`rattler` crate 的 `install/link.rs` 模块处理具体的链接逻辑，`rattler_package_streaming` 只负责包归档的下载和解压。

## 相关概念

- [Repodata 网关](07-repodata-gateway.md)
- [安装事务](09-install-and-transaction.md)
- [网络/缓存/配置](12-networking-cache-config.md)
