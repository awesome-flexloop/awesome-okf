# 概念文档

本目录包含 rust-lang/rust 知识库的 12 个概念文档，按编译器流水线阶段递进：先立地图与构建认知，再沿数据流推进，标准库为独立纵队，最后是高级横切面。

## 地图与构建认知（00-02）

* [00-简介与仓库导航](00-intro-repo-navigation.md) — 单仓库、双 workspace、三世界（编译器 79 crate / 标准库 23 目录 / 工具 45 目录）与版本真源 src/version。
* [01-bootstrap 构建系统](01-bootstrap-build-system.md) — Python 壳、Rust 芯与三阶段自举：src/stage0 锁定的 beta 起点、Builder/Kind/Step 体系与 build/ 输出布局。
* [02-编译器流水线总览](02-compiler-pipeline-overview.md) — 从 rustc 二进制壳到 rustc_driver_impl 的入口链、passes.rs 函数骨架与 query 按需求值心智模型。

## 沿数据流推进（03-07）

* [03-解析与宏展开](03-parsing-macro-expansion.md) — rustc_lexer 的 tokenize、rustc_parse 的解析器家族、rustc_expand 的 ExtCtxt 与内建宏清单。
* [04-HIR 与 AST Lowering](04-hir-ast-lowering.md) — rustc_ast_lowering 的降级机器、rustc_hir_analysis 的收集/一致性/型变检查、rustc_hir_typeck 的表达式类型检查。
* [05-类型系统与 trait 求解](05-type-system-trait-solving.md) — TyCtxt 上下文家族、四个 TyKind 的坐标、InferCtxt 与两代 trait 求解器架构。
* [06-MIR 与借用检查](06-mir-borrow-checking.md) — 数据/构建/改写的三个 crate 分工、THIR→MIR 流程、NLL 与 Polonius 的模块版图。
* [07-MIR 优化与代码生成](07-mir-optimization-codegen.md) — 四组 pass 编排与 gvn/inline/sroa、monomorphize 单态化、CodegenBackend trait 契约与 LLVM/Cranelift/GCC 三后端。

## 标准库纵队（08）

* [08-标准库分层架构](08-std-layered-architecture.md) — core 零依赖宣言、alloc 堆层、std 门面、sys/os 两级平台分发、sysroot 聚合与 panic 运行时。

## 高级横切面（09-11）

* [09-rustc 基础设施](09-rustc-infrastructure.md) — Span 与 Symbol、rustc_queries! 唯一定义点与缓存策略、rmeta 元数据格式、名称解析。
* [10-rustdoc 与工具链](10-rustdoc-toolchain.md) — librustdoc 内部结构、Miri 的 MIR 解释执行、45/36 工具差集与 compiletest 测试体系。
* [11-诊断与错误体系](11-diagnostics-error-system.md) — DiagCtxt 家族与 CodeSuggestion、贯穿各阶段 crate 的 diagnostics 模块模式、Early/Diag 两级语境。

```{toctree}
:hidden:
:maxdepth: 7

00-intro-repo-navigation
01-bootstrap-build-system
02-compiler-pipeline-overview
03-parsing-macro-expansion
04-hir-ast-lowering
05-type-system-trait-solving
06-mir-borrow-checking
07-mir-optimization-codegen
08-std-layered-architecture
09-rustc-infrastructure
10-rustdoc-toolchain
11-diagnostics-error-system
```
