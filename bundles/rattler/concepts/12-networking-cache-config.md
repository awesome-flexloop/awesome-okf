---
type: "concept"
title: "网络/缓存/配置"
sources:
  - id: rattler-networking-config
    resource: /references/rattler-source.md
    title: "Rattler Crates 结构 - rattler_networking/rattler_config/rattler_cache"
---

# 网络/缓存/配置

Rattler 的网络请求、缓存管理和配置系统分布在三个 crate 中：`rattler_networking`（HTTP 客户端栈）、`rattler_cache`（包缓存管理）和 `rattler_config`（配置文件解析）。本文档概述这三个支撑模块。

## rattler_networking：HTTP 客户端栈

`rattler_networking` 基于 [`reqwest-middleware`](https://github.com/TrueLayer/reqwest-middleware) 构建，提供生产级别的 HTTP 客户端能力。

### 核心组件

```mermaid
graph LR
    A["Gateway/Installer"] --> B["ClientWithMiddleware"]
    B --> C["OAuth Middleware"]
    B --> D["Retry Middleware"]
    B --> E["S3/GCS/OCI Middleware"]
    B --> F["Mirror Middleware"]
    C --> G["reqwest Client"]
    D --> G
    E --> G
    F --> G
```

### LazyClient：懒加载客户端

`rattler_networking` 提供 `LazyClient`，按需初始化 HTTP 客户端（首次使用时创建），避免在不需要网络的场景中浪费初始化开销：

```rust
use rattler_networking::LazyClient;

let client = LazyClient::new();
// 首次使用时自动初始化
// client.client() 返回 &ClientWithMiddleware
```

### 认证中间件

**OAuth2 认证**：`authentication.rs` 和 `oauth_refresh.rs` 处理 OAuth2 Bearer Token 的自动刷新。支持：
- 静态 token 配置
- 客户端凭证模式（client_credentials）
- Token 自动过期刷新
- 多个 channel 的独立认证

```rust
// 认证存储
use rattler_networking::authentication_storage;
// 从配置文件或 keychain 加载认证信息
let auth_storage = authentication_storage::AuthenticationStorage::from_env()?;
```

认证信息来源：
1. 环境变量（`CONDA_TOKEN`、`CONDA_USERNAME`/`CONDA_PASSWORD`）
2. `.rattler/credentials.json` 配置文件
3. 系统密钥链（macOS Keychain、Windows Credential Manager、Linux Secret Service）
4. netrc 文件

### 重试策略

`retry_policies.rs` 实现了指数退避重试策略：
- 默认重试 3 次
- 对 5xx 错误、连接超时、DNS 错误重试
- 对 4xx 错误（除了 408/429）不重试
- 支持 `Retry-After` 头（如 429 限流时）

### S3/GCS/OCI 中间件

- **S3 中间件**：自动对 S3 URL 签名请求（AWS Signature V4），支持访问 S3 托管的 conda channel
- **GCS 中间件**：对 Google Cloud Storage 请求附加认证头
- **OCI 中间件**：对 OCI registry 请求进行认证（用于 `oci://` 协议的 channel）

### 镜像支持

镜像中间件将请求重定向到配置的镜像站点，用于加速下载（如配置国内镜像源）。

### 代理配置

从环境变量 `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY` 自动读取代理配置，与 reqwest 默认行为一致。也支持通过 `rattler_config` 显式配置。

## rattler_config：配置系统

`rattler_config` 实现了与 `.condarc` 兼容的配置解析，同时支持 Rattler 自己的配置扩展。

### 配置文件位置

配置文件按优先级加载（后者覆盖前者）：

1. 系统级：`/etc/conda/.condarc`（Linux/macOS）、`C:\ProgramData\conda\.condarc`（Windows）
2. 用户级：`~/.condarc`、`~/.config/conda/.condarc`
3. 环境级：`$CONDA_PREFIX/.condarc`
4. 目录级：当前目录的 `.condarc`
5. 环境变量：`CONDA_*` 前缀的环境变量

### 核心配置项

```toml
# 概念性示意（实际为 YAML 格式）
channels = ["conda-forge", "defaults"]  # 默认 channel 列表
channel_alias = "https://conda.anaconda.org"  # channel URL 别名
default_channels = ["https://repo.anaconda.com/pkgs/main", "..."]

[proxy_servers]
http = "http://proxy:8080"
https = "https://proxy:8080"

[s3]
endpoint_url = "https://s3.example.com"
region = "us-east-1"

[network]
connect_timeout_secs = 10
read_timeout_secs = 30
max_retries = 3

[concurrency]
max_concurrent_downloads = 50
max_concurrent_requests = 20

[ssl_verify]
enabled = true
ca_bundle = "/path/to/ca-bundle.crt"
```

### Config 结构体

```rust
use rattler_config::Config;

// 加载配置
let config = Config::load_with_cli_args(&cli_args)?;

// 访问配置项
let channels = config.channels();
let proxy = config.proxy_servers();
let ssl_verify = config.ssl_verify();
```

## rattler_cache：缓存管理

Rattler 使用本地文件系统缓存来存储下载的包和 repodata，避免重复下载。

### 缓存目录结构

默认缓存目录（`default_cache_dir()`）：

| 平台 | 默认路径 |
|------|---------|
| Linux | `~/.cache/rattler/` |
| macOS | `~/Library/Caches/rattler/` |
| Windows | `%LOCALAPPDATA%\rattler\` |

缓存目录结构：

```
rattler/
├── repodata/                    # Repodata 缓存
│   ├── https_conda_anaconda_org_conda_forge_linux-64.json
│   ├── https_conda_anaconda_org_conda_forge_linux-64.json.bincode
│   ├── https_conda_anaconda_org_conda_forge_linux-64.json.state
│   └── patches/                 # zstd 增量补丁
│       └── ...
├── pkgs/                        # 包缓存
│   ├── <sha256-hash>/           # 每个包一个目录（按 SHA256 命名）
│   │   ├── info/
│   │   │   ├── index.json
│   │   │   └── paths.json
│   │   ├── bin/
│   │   ├── lib/
│   │   └── ...
│   └── cache.json               # 包缓存索引
└── virtual-packages/            # 虚拟包检测缓存
    └── cuda.json
```

### 包缓存键

包缓存使用 SHA256 哈希作为键，确保内容寻址（content-addressed）：
- 相同内容的包共享缓存（即使来自不同 channel）
- 哈希验证确保缓存完整性
- 格式：`pkgs/<sha256>/`

```rust
use rattler_cache::package_cache::{PackageCache, PackageCacheRaw};

let cache = PackageCache::new(cache_dir.join("pkgs"));

// 获取包（如果缓存命中直接返回，否则下载解压）
let cached = cache.get_or_put_from_url(
    &sha256_hash,
    url,
    &client,
    reporter,
    cancellation_token,
).await?;
```

### 缓存验证

`validation.rs` 提供缓存完整性校验：
- 检查 SHA256/MD5 哈希是否匹配
- 检查文件是否存在
- 检查 paths.json 中的文件是否都已正确解压
- 验证失败的包会被删除并重新下载

### 缓存清理

```rust
use rattler_cache::package_cache::CacheClearMode;

// 清理过期包（超过指定天数未使用的）
cache.cleanup(Duration::days(30)).await?;

// 完全清空缓存
cache.clear(CacheClearMode::All)?;
```

## rattler_digest：哈希工具

`rattler_digest` 封装了 MD5 和 SHA256 哈希计算，提供同步和异步（tokio）接口：

```rust
use rattler_digest::{compute_file_digest, Sha256, Md5};

// 同步计算文件哈希
let sha256 = compute_file_digest::<Sha256>(&path)?;
let md5 = compute_file_digest::<Md5>(&path)?;

// 异步（tokio）计算文件哈希
let sha256 = rattler_digest::tokio::compute_file_digest::<Sha256>(&path).await?;
```

`SerializableHash<T>` 包装类型提供 serde 序列化支持，将哈希表示为十六进制字符串。

## rattler_redaction：敏感信息脱敏

在日志输出时，`rattler_redaction` 确保 URL 中的 token、密码等敏感信息被掩码：

```rust
use rattler_redaction::{Redacted, Redactable};

let url = url::Url::parse("https://token:abc123@conda.example.com/path")?;
let redacted: Redacted<url::Url> = url.redact();
println!("{}", redacted);  // https://token:****@conda.example.com/path
```

这确保在输出日志或错误信息时不会泄露认证凭证。

## rattler_macros：过程宏

`rattler_macros` 提供编译时辅助宏：

```rust
use rattler_macros::sorted_enum;

#[sorted_enum]
enum MyEnum {
    Alpha,
    Beta,
    Gamma,
}
// 编译时检查变体是否按字母顺序排列，避免序列化不一致
```

## 工具 Crates

### coalesced_map

提供 `CoalescedMap` 数据结构，将多个值合并到同一键下，用于处理重复键场景（如多个 channel 提供同名包）。

### simple_spawn_blocking

对 `tokio::task::spawn_blocking` 的封装，提供取消支持和更好的错误处理：

```rust
use simple_spawn_blocking::spawn_blocking;

let result = spawn_blocking(|| {
    // CPU 密集或阻塞操作
    heavy_computation()
}, cancellation_token).await?;
```

### file_url

处理 `file://` URL 与本地路径的转换。

### path_resolver

根据环境变量和已知位置解析文件路径（如 conda 安装路径、缓存路径等）。

## 相关概念

- [Repodata 网关](07-repodata-gateway.md)
- [包流式处理](08-package-streaming.md)
- [安装事务](09-install-and-transaction.md)
