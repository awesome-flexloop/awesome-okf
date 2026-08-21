---
type: "concept"
title: "Repodata 网关"
sources:
  - id: rattler-repodata-gateway
    resource: /references/rattler-source.md
    title: "Rattler Crates 结构 - rattler_repodata_gateway"
---

# Repodata 网关

`rattler_repodata_gateway` 是获取 conda repodata 的高级抽象层。它封装了网络请求、缓存管理、并发控制、分片加载和增量更新等复杂性，为上层（求解器、CLI、Python 绑定）提供简洁的 `Gateway` API。

## 为什么需要 Repodata 网关

直接下载 repodata.json 面临几个挑战：
1. **大文件**：conda-forge 的 repodata.json 超过 100MB，下载和解析慢
2. **多 channel**：用户可能配置了多个 channel，需要按优先级合并
3. **缓存**：需要避免每次都重新下载，同时保证数据新鲜度
4. **并发**：多个 repodata 请求需要并发进行
5. **分片**：sharded repodata v3 格式需要按需加载分片
6. **增量更新**：支持 zstd 补丁增量更新，减少传输量

Gateway 解决了以上所有问题。

## 两种 API 层级

### 基础 API：fetch_repo_data

`fetch::fetch_repo_data()` 是底层函数，直接从 URL 获取单个 repodata：

```rust
use rattler_repodata_gateway::fetch;
use rattler_conda_types::{Channel, ChannelConfig, Platform};
use reqwest_middleware::ClientWithMiddleware;

let client = ClientWithMiddleware::default();
let result = fetch::fetch_repo_data(
    fetch::FetchRepoDataOptions {
        cache_dir: Some(cache_dir.clone()),
        ..Default::default()
    },
    client,
    &channel.clone(),
    Platform::Linux64,
    None,   // 取消令牌
).await?;

// result.repo_data: RepoData
// result.cache_state: 缓存状态（是否命中缓存）
```

### 高级 API：Gateway

`Gateway` 是推荐的使用方式，提供自动缓存、分片、多 channel 管理：

```rust
use rattler_repodata_gateway::Gateway;
use rattler_conda_types::{Channel, ChannelConfig, Platform, MatchSpec};

let channel_config = ChannelConfig::default_with_root_dir(std::env::current_dir()?);
let channels = vec![Channel::from_str("conda-forge", &channel_config)?];

let gateway = Gateway::builder()
    .with_cache_dir(cache_dir.clone())
    .with_channels(channels)
    .finish()
    .await?;
```

## Gateway 核心方法

### query：按名称查询包

```rust
// 查询指定包的可用版本（自动处理分片和缓存）
let result = gateway.query(
    [Platform::current()],     // 平台列表
    ["numpy", "pandas"],       // 包名列表
    None,                      // 取消令牌
).await?;

// result: HashMap<(Channel, Platform), Vec<RepoDataRecord>>
for ((channel, platform), records) in &result {
    println!("{} {}: {} 个包", channel, platform, records.len());
}
```

`query` 方法智能地处理：
- 检查本地缓存是否有效（基于 cache-control 头和 zstd 补丁）
- 如果是 sharded repodata，只请求涉及的分片
- 并发获取多个 channel/platform
- 自动应用增量补丁

### load_repodata：加载完整 repodata

```rust
// 加载指定 channel/platform 的完整 repodata
let repodata = gateway
    .load_repodata(channel, Platform::Linux64, None)
    .await?;

// repodata: (RepoData, ChannelUrl, CacheAction)
```

### clear：清除缓存

```rust
use rattler_repodata_gateway::CacheClearMode;

gateway.clear(CacheClearMode::All).await?;         // 清除所有缓存
gateway.clear(CacheClearMode::Repodata).await?;    // 只清除 repodata 缓存
gateway.clear(CacheClearMode::Packages).await?;    // 只清除包缓存
```

## 缓存机制

Gateway 使用多级缓存策略：

### 1. HTTP 缓存
- 遵循 HTTP `Cache-Control`、`ETag`、`Last-Modified` 头
- 发送 `If-None-Match` / `If-Modified-Since` 条件请求
- 服务端返回 304 时直接使用本地缓存

### 2. 磁盘缓存
- repodata.json 缓存到 `cache_dir/repodata/` 目录
- 原始 JSON 和 bincode 序列化格式都缓存
- bincode 格式加载速度比 JSON 快 10x+

### 3. Zstd 增量补丁
- 服务端提供 `.patch` 文件（基于 zstd 的二进制差分）
- 客户端用旧版本 + patch = 新版本，不必下载完整 repodata
- 典型 patch 只有几 MB（相比 100MB+ 完整文件）

### 4. 内存缓存
- Gateway 实例内部维护 LRU 内存缓存
- 同一进程内多次查询相同 channel/platform 直接返回内存数据

## 分片 Repodata（Sharded Repodata）

传统 repodata.json 是一个巨大的 JSON 文件。Sharded repodata v3 将其拆分为：
- `repodata.json`：轻量索引（约几 MB），包含分片映射表
- `shards/<xx>/<hash>.json`：按包名 hash 分片的小包数据文件（每个约 100KB）

```
<subdir>/
├── repodata.json        # 索引文件（分片映射+元数据）
└── shards/
    ├── 0a/
    │   ├── 0a1b2c...json # 包含以 hash 前缀 "0a" 开头的包
    │   └── ...
    ├── 0b/
    │   └── ...
    └── ff/
```

Gateway 自动检测并支持分片格式。当查询特定包名时，只下载包含该包名的分片，初始加载速度大幅提升。

## 进度报告

Gateway 支持 `Reporter` trait 来报告下载进度：

```rust
pub trait Reporter: Send + Sync {
    /// 下载开始
    fn on_download_start(&self, url: &Url, total: Option<u64>);
    /// 下载进度更新
    fn on_download_progress(&self, url: &Url, bytes: u64, total: Option<u64>);
    /// 下载完成
    fn on_download_complete(&self, url: &Url, bytes: u64);
    /// repodata 处理（解析/补丁）进度
    fn on_repodata_processed(&self, channel: &Channel, platform: Platform);
}
```

`IndicatifReporter` 是默认的 CLI 进度条实现：

```rust
use rattler_repodata_gateway::fetch::{IndicatifReporter, Placement};

let gateway = Gateway::builder()
    .with_cache_dir(cache_dir)
    .with_reporter(IndicatifReporter::builder().finish())
    .with_channels(channels)
    .finish()
    .await?;
```

## Channel 关系与 run_exports

Gateway 还处理 channel 间的关系和 run_exports 提取：

- **channel priority**：按用户指定顺序排列 channel，求解器据此决定优先级
- **subdir selection**：通过 `SubdirSelection` 控制哪些平台子目录被加载
- **run_exports 预加载**：在加载 repodata 时提取包的 run_exports 信息，供求解器使用

## 与 rattler_networking 集成

Gateway 底层使用 `rattler_networking` 提供的 HTTP 客户端，自动继承：
- OAuth 认证（私有 channel 如 prefix.dev、Anaconda.org）
- S3/GCS/OCI 中间件（直接从云存储下载）
- 重试策略（指数退避）
- 代理配置（从 `rattler_config` 读取）
- 镜像支持

## Python 绑定

```python
from rattler import Gateway, Channel, Platform

gateway = Gateway()
repodata = await gateway.load_repodata(
    channels=[Channel("conda-forge")],
    platforms=[Platform.current()],
    specs=["python", "numpy"],
)
```

Python 绑定的 `Gateway` 直接映射到 Rust Gateway，默认使用 IndicatifReporter 显示进度条。

## 相关概念

- [包记录与 RepoData](05-package-records-and-repodata.md)
- [依赖求解](06-solving-dependencies.md)
- [包流式处理](08-package-streaming.md)
- [网络/缓存/配置](12-networking-cache-config.md)
