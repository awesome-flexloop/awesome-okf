---
okf_version: "0.2"
---

# cargo 包管理器核心架构知识库

本知识包是 [cargo](https://github.com/rust-lang/cargo)（Rust 语言的官方包管理器与构建工具）的系统化中文教程，基于 **master @ 75d17360928f57ff2a7d2f2da1c753f5fe1926d1** 基线（2026-08-26 采集）源码深度阅读生成。此基线版本采用**版本双轨制**：包版本 `0.101.0`（库 API 永久不稳定），CLI 显示版本 `1.100.0`（与 rustc 同步）。所有内容均溯源至 cargo 源码（`src/` 八大模块、`src/bin/cargo/` CLI 层、`crates/` 与 `credential/` 子 crate 家族），遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

> ⚠️ 此基线已完成结构重组：主 crate 源码位于 `src/`（非旧版 `src/cargo/`）、`Config` 已更名 `GlobalContext`、SourceId/PackageId 位于 `src/workspace/`、根 Cargo.toml 为 package+workspace 合一。本 bundle 全部路径引用使用重组后坐标，详见[信源登记](references/cargo-source-map.md)。

## 进入与分发（concepts/）

* [简介与架构总览](concepts/00-intro-architecture-overview.md) — src/ 重组基线与组件地图、根 Cargo.toml 双职、版本双轨制。
* [Crate 组织与 CLI 分发](concepts/01-crate-organization-cli-dispatch.md) — 19+5 个子 crate 家族、Exec 三级推断决策树、别名递归与外部子命令磁盘扫描。

## 数据模型与语境（concepts/）

* [Workspace 与 Package 模型](concepts/02-workspace-package-model.md) — 从 Cargo.toml 到包身份：Manifest/Package/Workspace 模型与 PackageId 静态缓存身份。
* [GlobalContext 配置系统](concepts/03-global-context-config.md) — 两层反序列化、Definition 来源优先级、20 个顶层配置键。

## 解析与下载（concepts/）

* [依赖解析 resolver](concepts/04-dependency-resolver.md) — Resolve 图与版本演进：V1-V5 锁文件格式、ResolveBehavior 双版本轴。
* [Sources 与 registry](concepts/05-sources-registry.md) — 五种包源、Source trait 异步协议与 crates.io 双索引通道。

## 操作与编译调度（concepts/）

* [ops 命令实现](concepts/06-ops-command-implementation.md) — 39 个薄壳下的业务核心：cargo_compile 单一入口与 resolve_ws 编排族。
* [编译调度与 unit 图](concepts/07-build-scheduling-unit-graph.md) — BuildRunner 的世界：Unit 构建语义节点、25 个 compiler 子模块与 rustc 结构类比。

## 横切纵队（concepts/）

* [认证与 credential](concepts/08-auth-credential.md) — JSON 进程协议 v1、CacheControl 缓存语义与 5 个平台 credential 实现。
* [util 基础设施](concepts/09-util-infrastructure.md) — 42 个子模块与构建支撑：Graph/Queue/job/flock、错误体系与 build.rs 注入链。

## 实战示例（examples/）

* [cargo new 源码路径追踪](examples/cargo-new-source-trace.md) — 从敲下 cargo new 到目录落盘的完整源码实走。
* [Cargo.toml 解析流程](examples/cargo-toml-parsing-flow.md) — 从磁盘清单到 Workspace 数据模型的逐站拆解。

## 信源登记簿（references/）

* [cargo 源码信源登记](references/cargo-source-map.md) — master @ 75d17360 基线坐标、doc/man 37 手册、doc/book 四大部分、testsuite 120+ 测试模块、benches 三类基准与旧名→新名迁移对照。

## 信任与生命周期说明

* **status 判定依据**：全部 13 个内容文档（10 个概念 + 2 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 cargo 源码（`external/libs/rust-lang/cargo/` 目录）核心子系统的逐模块阅读与事实提取（144 条编号事实 F-cargo-001~144），经 source-code-to-okf-wiki 五阶段流程（R→I→E→V→C）生成；概念文档主覆盖 135 条、信源登记主覆盖 9 条，事实覆盖率 100%。
* **stale_after 解释**：统一设置为 `2027-08-28`。cargo 核心架构（CLI 分发决策树、Resolve 图、Unit 调度、credential 协议）演进缓慢，但本基线刚经历结构重组（src/ 上提、GlobalContext 更名），上游后续重构可能再次移动坐标；该日期为保守的重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-28）；`verified.at` 记录 V 阶段对抗审查核验事件（2026-08-28），两者分离、可追溯。

本知识包共收录 13 个内容文档（10 个概念 + 2 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
