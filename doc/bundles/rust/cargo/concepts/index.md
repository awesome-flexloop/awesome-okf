# 概念文档

本目录包含 rust/cargo bundle 的 10 个概念文档，沿一条命令的数据流推进：00-01 进入与分发 → 02-03 数据模型与语境 → 04-05 解析与下载 → 06-07 操作与编译调度 → 08-09 横切纵队。

## 进入与分发

* [00-简介与架构总览](00-intro-architecture-overview.md) — src/ 重组基线、根 Cargo.toml 双职、版本双轨制（0.101.0/1.100.0）、lib.rs 八大模块与组件职责。
* [01-Crate 组织与 CLI 分发](01-crate-organization-cli-dispatch.md) — main() 前置流程、cli::main() 执行序、Exec 三级推断决策树、别名递归与 19+5 个子 crate 家族。

## 数据模型与语境

* [02-Workspace 与 Package 模型](02-workspace-package-model.md) — Manifest 解析数据模型、PackageId/SourceId 的静态内部指针身份机制、Edition 枚举与 channel 判定。
* [03-GlobalContext 配置系统](03-global-context-config.md) — Config→GlobalContext 更名、两层反序列化、Definition 来源优先级、20 个顶层配置键。

## 解析与下载

* [04-依赖解析 resolver](04-dependency-resolver.md) — Resolve 依赖图结构、ResolveVersion V1-V5 锁文件格式演进、ResolveBehavior 解析行为。
* [05-Sources 与 registry](05-sources-registry.md) — Source trait 异步协议、五种包源实现、crates.io 双索引通道（git/sparse）。

## 操作与编译调度

* [06-ops 命令实现](06-ops-command-implementation.md) — 39 个薄壳下的业务核心、cargo_compile 编译族单一入口、resolve_ws 编排族与 lockfile 读写。
* [07-编译调度与 unit 图](07-build-scheduling-unit-graph.md) — BuildContext/BuildRunner 双层语境、Unit 构建语义节点、Lto 与 links 验证、rustc_interface 结构类比。

## 横切纵队

* [08-认证与 credential](08-auth-credential.md) — JSON 进程协议 v1、CredentialResponse/CacheControl、provider 配置解析链与 5 个平台实现。
* [09-util 基础设施](09-util-infrastructure.md) — 42 个子模块、Graph/Queue/job 并发原语、flock 文件锁、错误体系、Rustc 探测与 build.rs 注入链。

```{toctree}
:hidden:
:maxdepth: 7

00-intro-architecture-overview
01-crate-organization-cli-dispatch
02-workspace-package-model
03-global-context-config
04-dependency-resolver
05-sources-registry
06-ops-command-implementation
07-build-scheduling-unit-graph
08-auth-credential
09-util-infrastructure
```
