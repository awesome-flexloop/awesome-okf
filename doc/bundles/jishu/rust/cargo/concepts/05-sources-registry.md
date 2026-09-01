---
type: Concept
title: Sources 与 registry：五种包源与 crates.io 协议
description: Source trait 抽象、RegistrySource/DirectorySource/GitSource/PathSource/ReplacedSource 五种实现与 crates.io 索引协议
tags: [rust, cargo, sources, registry, crates-io]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: cargo-source
    resource: /references/cargo-source-map.md
---

# Sources 与 registry：五种包源与 crates.io 协议

`src/sources/` 回答"包从哪里来"：lib.rs 的官方自述——`sources::source` 是 "The Source trait is an abstraction over different sources of packages"（F-cargo-037）。File Overview 补充了磁盘坐标（F-cargo-038）：`$CARGO_HOME/registry/` 下有 `index/`（索引缓存）、`cache/*/*.crate`（下载的 .crate 归档）、`src/*/*`（解包源码）。

## 五种内置 Source 实现（F-cargo-068）

sources/mod.rs 的模块文档列出 5 个实现（原文）：

| 实现 | 官方描述（原文摘录） |
|------|----------------------|
| `RegistrySource` | "A source that provides an index ... crates.io falls into this category. So do local registry and sparse registry." |
| `DirectorySource` | "Files are downloaded ahead of time. Primarily designed for crates generated from cargo vendor." |
| `GitSource` | — |
| `PathSource` | — |
| `ReplacedSource` | "This manages the source replacement feature" |

另有 `SourceConfigMap`，"which is effectively the representation of the `[source.*]` value"——`[source.*]` 配置段的运行时形态。

mod.rs 的 re-exports（F-cargo-069）：`SourceConfigMap`、`DirectorySource`、`GitSource`、`{PathEntry, PathSource, RecursivePathSource}`、`{CRATES_IO_DOMAIN, CRATES_IO_INDEX, CRATES_IO_REGISTRY, IndexSummary, RegistrySource}`、`ReplacedSource`；子模块 `config/directory/git/overlay/path/registry/replaced/source`。

## Source trait：异步查询与下载协议（F-cargo-070/071）

`#[async_trait::async_trait(?Send)] pub trait Source`（src/sources/source.rs:32）的方法清单（F-cargo-070）：

```rust
#[async_trait::async_trait(?Send)]
pub trait Source {
    fn source_id(&self) -> SourceId;
    fn replaced_source_id(&self) -> SourceId;
    fn supports_checksums(&self) -> bool;
    fn requires_precise(&self) -> bool;
    async fn query(&self, dep: &Dependency, kind: QueryKind,
                   f: &mut dyn FnMut(IndexSummary)) -> CargoResult<()>;
    async fn query_vec(...);
    fn invalidate_cache(&self);
    fn set_quiet(&mut self, quiet: bool);
    async fn download(&self, package: PackageId) -> CargoResult<MaybePackage>;
    async fn finish_download(&self, pkg_id: PackageId, contents: Vec<u8>) -> CargoResult<Package>;
    fn fingerprint(...);
}
```

三个协议要点：

1. **`(?Send)` 异步**：查询与下载是异步方法，但 local future 不要求 `Send`——cargo 的并发模型在此刻意放宽
2. **查询回调流**：`query` 把候选 `IndexSummary` 推给回调 `f`，`query_vec` 是收集为 Vec 的便利形态
3. **两段式下载**：`download` 返回 `MaybePackage`（可能已就绪或需传输），`finish_download` 接收字节流（`contents: Vec<u8>`）完成解包成 `Package`

配套类型（F-cargo-071）：`pub enum QueryKind`（:132，精确/备选两种查询意图）、`pub enum MaybePackage`（:159，下载的中间态）、`pub struct SourceMap<'src>`（:236，多源注册表——解析器同时面对 path/git/registry 混合源时的容器）。

## RegistrySource 与 crates.io 常量（F-cargo-072/073）

registry/mod.rs 定义了 crates.io 世界的四个坐标常量（F-cargo-072）：

```rust
pub const CRATES_IO_INDEX: &str = "https://github.com/rust-lang/crates.io-index";
pub const CRATES_IO_HTTP_INDEX: &str = "sparse+https://index.crates.io/";
pub const CRATES_IO_REGISTRY: &str = "crates-io";
pub const CRATES_IO_DOMAIN: &str = "crates.io";
```

`CRATES_IO_INDEX` 是旧版 git 索引、`CRATES_IO_HTTP_INDEX` 是 sparse HTTP 索引（协议前缀 `sparse+`）——两条索引通道并存。

`pub struct RegistrySource<'gctx>`（registry/mod.rs:245）是 registry 源的主体（F-cargo-073）。配套：`pub enum LoadResponse`（:269，索引加载响应）、`pub enum MaybeLock`（:385，下载锁状态）、`pub use cargo_util_schemas::index::RegistryConfig`（:216，registry 配置 schema 来自 cargo-util-schemas）、`pub use index::IndexSummary`（:403）。子模块（:400-405）：`download`、`http_remote`（sparse 协议）、`git_remote`（git 索引协议）、`local`，及 `index/{mod.rs, cache.rs}`（索引与缓存）。HTTP 传输层的 feature 选择（curl/reqwest 二选一，F-cargo-005）正是在 http_remote 处生效。

## PathSource 与本地源（F-cargo-074）

path.rs 的三个类型（F-cargo-074）：

- `pub struct PathSource<'gctx>`（:34）——本地路径源（workspace 成员与 path 依赖），`pub fn new(path: &Path, source_id: SourceId, gctx: &'gctx GlobalContext) -> Self`
- `pub struct RecursivePathSource<'gctx>`（:223）——递归路径源（path 依赖的传递闭包场景）
- `pub struct PathEntry`（:457）——路径枚举的条目

## SourceConfigMap 与源替换（F-cargo-075/076）

`pub struct SourceConfigMap<'gctx>`（config.rs:26）是 `[source.*]` 配置的表示（F-cargo-075）——源替换（source replacement）与镜像（mirror）功能的配置入口，与 `ReplacedSource` 协同。

git 子模块的文件构成（F-cargo-076）：`known_hosts.rs`（SSH known_hosts 处理）、`mod.rs`、`oxide.rs`（gitoxide 后端——对应 features.rs 的 `GitoxideFeatures`，F-cargo-088）、`source.rs`、`utils.rs`。双后端并存：`git2`（F-cargo-007 的 workspace 依赖）与 `gix`，经 `-Z gitoxide` 家族特性切换。

## 源体系的位置感

```
[SourceConfigMap] 读取 [source.*] 配置
    │
    ▼
SourceMap<'src>（多源容器）
    ├── PathSource        （path 依赖 / workspace 成员）
    ├── GitSource         （git 依赖；git2 或 gix 后端）
    ├── RegistrySource    （registry 依赖；git 索引或 sparse HTTP 索引）
    ├── DirectorySource   （cargo vendor 产物）
    └── ReplacedSource    （[source.*] 替换/镜像的包装层）
    │ query / download / finish_download
    ▼
Package（送入 resolver 激活，见依赖解析篇）
```

registry 认证（谁有权从 registry 下载/发布）由 credential 子系统承担，见[认证与 credential](/concepts/08-auth-credential.md)。

## 相关概念

- [Workspace 与 Package 模型](/concepts/02-workspace-package-model.md) — SourceId 身份与 Package 的定义地
- [依赖解析 resolver](/concepts/04-dependency-resolver.md) — 源查询的消费者
- [认证与 credential](/concepts/08-auth-credential.md) — registry 访问的凭据侧
- [util 基础设施](/concepts/09-util-infrastructure.md) — CanonicalUrl 与网络工具的支撑
