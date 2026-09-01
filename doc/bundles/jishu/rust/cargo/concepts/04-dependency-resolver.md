---
type: Concept
title: 依赖解析 resolver：Resolve 图与版本演进
description: resolver 模块的核心算法、Resolve 依赖图结构、ResolveVersion V1-V5 演进链与 ResolveBehavior 解析行为
tags: [rust, cargo, resolver, dependency, graph]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: cargo-source
    resource: /references/cargo-source-map.md
---

# 依赖解析 resolver：Resolve 图与版本演进

`src/resolver/` 是 cargo 的依赖解析核心。lib.rs 的官方自述极为简洁：`resolver` 是 "The core algorithm"（F-cargo-037），`ops::resolve` 是 "Top-level API for dependency and feature resolver (e.g. ops::resolve_ws)"——resolver 模块提供算法本体，ops 侧的 resolve 家族（见[ops 命令实现](/concepts/06-ops-command-implementation.md)）提供编排入口。

解析的产出是一个 `Resolve` 图：Cargo.lock 的内存形态（F-cargo-038："Cargo.lock ... loaded with ops::resolve_ws or a variant of it into a resolver::Resolve"）。workspace 依赖中的 `varisat = "0.2.2"`（F-cargo-007）暗示解析器内置 SAT 求解器用于处理复杂的版本约束。

## 模块地图（F-cargo-062/063）

resolver/mod.rs 的 re-exports 层（F-cargo-062）：

- `{ActivateError, ActivateResult, ResolveError}` — 激活与错误类型
- `{CliFeatures, ForceAllTargets, HasDevUnits}` — 特征请求控制
- `{Resolve, ResolveVersion}` — 解析结果与其版本
- `{ResolveBehavior, ResolveOpts}` — 解析行为与选项
- `{PublishAgePolicy, PublishAgeViolation, VersionOrdering, VersionPreferences}` — 版本偏好（version_prefs）

`pub fn resolve(...)` 定义于 mod.rs:125——算法主入口。

子模块清单（F-cargo-063）：`conflict_cache`、`context`、`dep_cache`、`encode`、`errors`、`features`（pub）、`resolve`、`types`、`version_prefs`。命名已勾勒出算法骨架：激活依赖时查 `dep_cache`，冲突记入 `conflict_cache`，特征统一在 `features`，最终图固化在 `resolve`。

## Resolve：解析结果的图结构（F-cargo-064/066）

`pub struct Resolve`（src/resolver/resolve.rs:19）的字段群（F-cargo-064）：

```rust
pub struct Resolve {
    graph: Graph<PackageId, HashSet<Dependency>>,
    replacements: HashMap<PackageId, PackageId>,
    reverse_replacements: ...,
    features: HashMap<PackageId, Vec<InternedString>>,
    checksums: HashMap<PackageId, Option<String>>,
    metadata: TomlLockfileMetadata,
    unused_patches: Vec<PackageId>,
    public_dependencies: HashMap<PackageId, HashSet<PackageId>>,
    version: ResolveVersion,
    summaries: HashMap<PackageId, Summary>,
}
```

这是一张以 `PackageId` 为节点、`HashSet<Dependency>` 为边标签的图（`Graph` 来自 `src/util/graph.rs`，见[util 基础设施](/concepts/09-util-infrastructure.md)）。字段按职责分组：

- **图本体**：`graph` + `replacements`/`reverse_replacements`（`[patch]`/`[replace]` 引入的节点替换映射）
- **锁文件数据**：`features`（每包启用的特征）、`checksums`（每包校验和，`Option` 表示 registry 包必填、本地/ git 包可无）、`metadata`（`TomlLockfileMetadata`）、`unused_patches`（未生效的 patch）
- **图属性**：`public_dependencies`（公有依赖边集合）、`version`（本图的锁文件格式版本）、`summaries`（每包的 Summary 缓存）

`Resolve::new(graph, replacements, features, checksums, metadata, unused_patches, version, summaries)` 构造；遍历接口（F-cargo-066）：`pub fn iter(&self) -> impl Iterator<Item = PackageId>`（全节点）、`pub fn deps(&self, pkg: PackageId) -> impl Iterator<Item = (PackageId, &HashSet<Dependency>)>`（后继边）、`pub fn deps_not_replaced(...)`（不含替换重映射的原始后继）。Cargo.lock 的写盘与读盘经由 `ops::lockfile` 的 `resolve_to_string`/`load_pkg_lockfile`（F-cargo-056）。

## ResolveVersion：锁文件格式的五代演进（F-cargo-065）

`pub enum ResolveVersion { V1, V2, V3, V4, V5 }`（F-cargo-065）。默认与稳定边界：

```rust
fn default() -> ResolveVersion { ResolveVersion::V4 }
pub fn max_stable() -> ResolveVersion { ResolveVersion::V4 }
```

`with_rust_version` 的版本分支：`>= 1.83 → V4`、`>= 1.53 → V3`、`>= 1.41 → V2`、否则 V1——旧工具链写旧格式锁文件，保证互操作。V5 注释原文："Unstable. Will collect a certain amount of changes and then go."（不稳定，将积累一定量的变更后再定）。

V1→V4 的演进对应 Cargo.lock 格式的历史变更（如 V2 引入依赖合并写法、V3/V4 引入更多元数据与校验和语义）；阅读旧 Cargo.lock 文件时先看文件头部的 `version` 字段再对照此枚举。

## types.rs：解析行为与选项（F-cargo-067）

`pub enum ResolveBehavior { V1, V2, V3 }`（F-cargo-067）——这是 workspace 的 `resolver` 字段（feature 统一行为），与 `ResolveVersion`（锁文件格式）是**两个不同的版本轴**，二者不可混淆。`ResolveBehavior::from_manifest` 接受字符串 "1"/"2"/"3"，否则报错：

> "`resolver` setting `{}` is not valid"

`pub struct ResolveOpts { pub dev_deps: bool, pub features: RequestedFeatures }`——单次解析的选项：是否含 dev 依赖、请求的特征集。

其余类型（F-cargo-067）：`ResolverProgress`（进度上报）、`ActivationsKey`（激活缓存键）、`SemverCompatibility`（语义版本兼容判定）、`DepsFrame`/`RemainingDeps`（剩余依赖栈帧——解析的待办列表）、`ConflictReason`（冲突原因）、`RcVecIter`；`pub type FeaturesSet = Rc<BTreeSet<InternedString>>`。

## 解析算法的位置感

结合 facts 中的坐标，resolver 在数据流中的位置：

```
Workspace + PackageSet（候选包）
    │ ops::resolve 家族编排（F-cargo-053~055）
    ▼
resolver::resolve(...)（mod.rs:125）
    │ 激活/冲突/回溯（dep_cache / conflict_cache / types::RemainingDeps）
    ▼
Resolve 图（V1~V5 格式）
    │ ops::lockfile（F-cargo-056）
    ▼
Cargo.lock 文件
```

`WorkspaceResolve`（F-cargo-053）作为 ops 侧的包装结构，把 `Resolve` 与 `PackageSet`、`specs_and_features` 打包传递给编译端——见[编译调度与 unit 图](/concepts/07-build-scheduling-unit-graph.md)。

## 相关概念

- [Workspace 与 Package 模型](/concepts/02-workspace-package-model.md) — PackageId/SourceId 身份体系与 Summary 的定义地
- [ops 命令实现](/concepts/06-ops-command-implementation.md) — resolve_ws 家族的编排层
- [编译调度与 unit 图](/concepts/07-build-scheduling-unit-graph.md) — Resolve 图的下游消费者
- [util 基础设施](/concepts/09-util-infrastructure.md) — Graph 泛型数据结构的定义
