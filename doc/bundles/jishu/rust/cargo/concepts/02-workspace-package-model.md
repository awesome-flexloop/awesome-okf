---
type: Concept
title: Workspace 与 Package 模型：从 Cargo.toml 到包身份
description: workspace 模块的 Manifest/Package/Workspace 数据模型、PackageId 与 SourceId 的静态内部指针身份机制、Edition 与 channel
tags: [rust, cargo, workspace, package, manifest]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: cargo-source
    resource: /references/cargo-source-map.md
---

# Workspace 与 Package 模型：从 Cargo.toml 到包身份

`src/workspace/` 模块是 cargo 的数据模型层：`Cargo.toml` 在这里被解析为 `Manifest`、被组装成 `Package`、被编组进 `Workspace`；"包身份"（`PackageId`）与"源身份"（`SourceId`）两个核心标识类型也定义于此。lib.rs 的官方自述：`workspace::parser` 是 "the code for parsing Cargo.toml files"（F-cargo-037）。

注意本基线的坐标变更：`PackageId` 与 `SourceId` 位于 `src/workspace/` 模块（`package_id.rs`/`source_id.rs`），而非旧文档所说的独立 id 模块（F-cargo-083/085）。

## 模块地图（F-cargo-077/078）

workspace/ 的子模块清单（F-cargo-078）：

```
workspace/
├── dependency.rs        # Dependency、Patch、PatchLocation、SerializedDependency
├── editor.rs
├── features.rs          # CliUnstable、Edition、Feature、Features
├── gc.rs
├── global_cache_tracker.rs
├── manifest.rs          # EitherManifest、VirtualManifest、Manifest、Target、TargetKind
├── package.rs           # Package、PackageSet
├── package_id.rs        # PackageId
├── package_id_spec.rs
├── parser.rs            # Cargo.toml 解析
├── profiles.rs
├── registry.rs          # Registry trait
├── source_id.rs         # SourceId
├── summary.rs           # FeatureMap、FeatureValue、Summary
└── workspace.rs         # Workspace
```

mod.rs 的 re-exports 层（F-cargo-077）：`{Dependency, Patch, PatchLocation, SerializedDependency}`、`{CliUnstable, Edition, Feature, Features}`、`{EitherManifest, VirtualManifest}`、`{Manifest, Target, TargetKind}`、`{Package, PackageSet}`、`PackageId`、`PackageIdSpecQuery`、`Registry`、`SourceId`、`{FeatureMap, FeatureValue, Summary}`、workspace 模块项；另有 `pub use cargo_util_schemas::core::{GitReference, PackageIdSpec, SourceKind};`——清单 schema 的部分定义已下沉到 cargo-util-schemas 子 crate。

## Workspace：成员编组与解析行为（F-cargo-079/080）

`pub struct Workspace<'gctx>`（src/workspace/workspace.rs:50）的字段群（F-cargo-079）：

```rust
pub struct Workspace<'gctx> {
    gctx: &'gctx GlobalContext,
    current_manifest: PathBuf,
    packages: Packages<'gctx>,
    root_manifest: Option<PathBuf>,
    target_dir: Option<Filesystem>,
    build_dir: Option<Filesystem>,
    members: IndexSet<PathBuf>,
    member_ids: HashSet<PackageId>,
    default_members: Vec<PathBuf>,
    is_ephemeral: bool,
    require_optional_deps: bool,
    loaded_packages: RefCell<HashMap<PathBuf, Package>>,
    ignore_lock: bool,
    requested_lockfile_path: Option<PathBuf>,
    resolve_behavior: ResolveBehavior,
    resolve_honors_rust_version: bool,
    resolve_feature_unification: FeatureUnification,
    resolve_honors_publish_age: bool,
    resolve_publish_time: Option<jiff::Timestamp>,
    custom_metadata: Option<toml::Value>,
    local_overlays: HashMap<SourceId, PathBuf>,
}
```

三个观察点：

1. **生命周期绑定语境**：`gctx: &'gctx GlobalContext`——Workspace 的构造需要 `&GlobalContext`，这决定了[GlobalContext 配置系统](/concepts/03-global-context-config.md)必须先于本篇阅读。
2. **成员是路径而非包**：`members: IndexSet<PathBuf>`、`default_members: Vec<PathBuf>`——Workspace 编组的是清单路径，`loaded_packages: RefCell<HashMap<PathBuf, Package>>` 按需缓存加载的 Package。
3. **解析行为就地存储**：`resolve_behavior`、`resolve_honors_rust_version`、`resolve_feature_unification`、`resolve_honors_publish_age` 等字段把 workspace 级的 resolver 配置固化在模型上，供后续 `ops::resolve` 家族读取。

核心方法（F-cargo-080）：`pub fn new(manifest_path: &Path, gctx: &'gctx GlobalContext) -> CargoResult<Workspace<'gctx>>`（:224）——从任一成员清单出发定位并构造整个 workspace；`pub fn ephemeral(...)`（:286）——构造临时 workspace（`cargo install` 等场景）；`pub fn default_members<'a>(&'a self) -> impl Iterator<Item = &'a Package>`（:662）。

## 虚拟根与成员身份（F-cargo-081）

workspace 根清单的两种形态由 `MaybePackage` 区分（F-cargo-081）：

```rust
pub enum MaybePackage {
    Package(Package),
    Virtual(VirtualManifest),
}
```

根有 `[package]` 时是实根（`Package`），只有 `[workspace]` 时是虚拟根（`VirtualManifest`）。成员判定依赖 `WorkspaceConfig`（:156）：`Root(WorkspaceRootConfig)` 表示"我是根"，`Member { root: Option<String> }` 表示"我是成员，我的根在哪"。`WorkspaceRootConfig`（:208）的字段：`root_dir: PathBuf`、`members: Option<Vec<String>>`、`default_members: Option<Vec<String>>`、`exclude: Vec<String>`、`inheritable_fields: InheritableFields`、`custom_metadata: Option<toml::Value>`——`inheritable_fields` 正是 `[workspace.package]` 继承机制（version/edition 等从根继承）的数据载体。

workspace.rs 的自由函数（F-cargo-082）：`pub fn resolve_relative_path(...)`（:2126）、`pub fn find_workspace_root(...)`（:2154）、`pub fn find_workspace_root_with_membership_check(...)`（:2173）——从成员清单向上找根是库用户（如 rust-analyzer）也依赖的公共能力。

## PackageId：静态内部指针 + 全局缓存的身份（F-cargo-083）

包身份的设计是本模块最反直觉的部分：

```rust
pub struct PackageId {
    inner: &'static PackageIdInner,
}
struct PackageIdInner {
    name: InternedString,
    version: semver::Version,
    source_id: SourceId,
}
static PACKAGE_ID_CACHE: OnceLock<Mutex<HashSet<&'static PackageIdInner>>>>;
```

要点（F-cargo-083）：

- **`&'static` 内部指针**：`PackageId` 本体只有一个指向 `PackageIdInner` 的静态引用，克隆即指针拷贝，因此 `PackageId: Copy` 级别廉价。
- **全局缓存**：`PACKAGE_ID_CACHE` 保证同名+同版本+同源的身份在进程内唯一，"缓存即规范化"（interning）。
- **自定义相等**：`PartialEq`/`Hash` 使用 `source_id.full_eq`/`full_hash`——相等语义委托给 `SourceId` 的完整比较，而非默认 derive。
- **序列化格式**：`Serialize` 输出 `"{} {} ({})"`（name version url）。

## Package 与 PackageSet（F-cargo-084）

`pub struct Package`（package.rs:43）经 `pub fn new(manifest: Manifest, manifest_path: &Path) -> Package`（:103）构造，方法族覆盖了构建所需的全部包语义：`dependencies`/`manifest`/`manifest_path`/`name`/`package_id`/`root`/`summary`/`targets`/`library`/`version`/`authors`/`publish`/`proc_macro`/`rust_version`/`hints`/`has_custom_build`/`map_source`（F-cargo-084）。`map_source` 支持源替换（`[patch]`/`[replace]`）下的身份重映射。

`pub struct PackageSet<'gctx>`（:288）是**已解析包集合**（resolver 的输出端）：`package_ids()` 返回全部 id，`packages()` 按 id 取回 Package。

## SourceId：源身份与精确性（F-cargo-085）

```rust
pub struct SourceId {
    inner: &'static SourceIdInner,
}
struct SourceIdInner {
    url: Url,
    canonical_url: CanonicalUrl,
    kind: SourceKind,
    precise: Option<Precise>,
    registry_key: Option<KeyOf>,
}
enum Precise {
    Locked,
    Updated { name: InternedString, from: semver::Version, to: semver::Version },
    GitUrlFragment(String),
}
```

与 `PackageId` 同构的"静态内部指针 + 缓存"模式（F-cargo-085）。`Precise` 枚举承载三种精确性状态：`Locked`（锁定于 Cargo.lock）、`Updated`（记录从哪个版本更新到哪个版本，用于诊断输出）、`GitUrlFragment`（git 源的精确 commit 定位）。`pub fn as_url(&self) -> SourceIdAsUrl<'_>` 提供序列化视图。`full_eq`/`full_hash`（被 `PackageId` 的自定义相等使用）定义于此。

## features.rs：Edition 枚举与发布通道（F-cargo-086/087/088）

features.rs 虽名为 features，实际承载三块独立职责：

### Edition 枚举（F-cargo-086）

```rust
pub enum Edition {
    Edition2015, Edition2018, Edition2021, Edition2024, EditionFuture,
}
pub const LATEST_STABLE: Edition = Edition::Edition2024;
pub const CLI_VALUES: [&'static str; 4] = ["2015", "2018", "2021", "2024"];
```

`EditionFuture` 是尚未稳定的 edition 占位；`CLI_VALUES` 只接受四个稳定值。这与 RFC 2052-epochs（Edition 机制）直接呼应。

### Feature 与 nightly 门（F-cargo-086）

`pub struct Feature { name: &'static str, stability: Status, version: &'static str, docs: &'static str, get: fn(&Features) -> bool }`——每个不稳定特性一条静态登记（名称、稳定状态、引入版本、文档链接、读取函数）。`Features::new(features: &[String], gctx, warnings, is_local)` 解析 `-Z` 标志集。三个宏支撑这一体系（F-cargo-088）：`macro_rules! features!`（:422）、`macro_rules! stab!`（:490）、`macro_rules! unstable_cli_options!`（:805）；`CliUnstable` 结构的 impl 位于 :1257。`GitFeatures`（:1045）与 `GitoxideFeatures`（:1141）分别登记 git/gitoxide 相关特性族。

### channel()：通道判定链（F-cargo-087）

`pub fn channel() -> String`（features.rs:1588）的读取顺序：

1. `__CARGO_TEST_CHANNEL_OVERRIDE_DO_NOT_USE_THIS`（测试覆写）
2. `RUSTC_BOOTSTRAP == "1"` 时返回 `"dev"`
3. `crate::version().release_channel.unwrap_or("dev")`

文档注释："Returns the current release channel (\"stable\", \"beta\", \"nightly\", \"dev\")." ——CLI 入口的 nightly 补全判断（F-cargo-014）正是调用此函数。另有常量 `pub const SEE_CHANNELS: &str = "See https://doc.rust-lang.org/book/appendix-07-nightly-rust.html ..."`（F-cargo-088），用于不稳定特性报错时引导读者。

## 数据流小结

```
Cargo.toml 文件
    │ workspace::parser::read_manifest
    ▼
EitherManifest（Manifest | VirtualManifest）  ── workspace::manifest
    │ Package::new(manifest, manifest_path)
    ▼
Package ──(Workspace::new 编组)──► Workspace<'gctx>
    │ resolver（见依赖解析篇）
    ▼
PackageSet + Resolve  ──(PackageId/SourceId 身份体系贯穿全程)
```

`Cargo.lock` 的加载与保存则由 `ops::lockfile` 承担（F-cargo-037），见[ops 命令实现](/concepts/06-ops-command-implementation.md)。

## 相关概念

- [简介与架构总览](/concepts/00-intro-architecture-overview.md) — File Overview 中 Cargo.toml 的坐标定义
- [GlobalContext 配置系统](/concepts/03-global-context-config.md) — Workspace 构造所依赖的 gctx 参数
- [依赖解析 resolver](/concepts/04-dependency-resolver.md) — Package/PackageId 流向的下一站
- [Cargo.toml 解析流程](/examples/cargo-toml-parsing-flow.md) — 本篇模型的源端实走示例
