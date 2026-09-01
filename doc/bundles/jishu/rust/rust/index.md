---
okf_version: "0.2"
---

# Rust 编译器核心架构知识库

本知识包是 [rust-lang/rust](https://github.com/rust-lang/rust)（Rust 语言主源码仓库：编译器、标准库与文档）的系统化中文教程，基于 main @ e457a7b0（版本 `1.100.0`，记录于 `src/version` 单行文件）源码深度阅读生成，覆盖从仓库导航、bootstrap 构建系统、编译器流水线到标准库分层架构的完整知识体系。所有内容均溯源至 rust-lang/rust 源码（`external/libs/rust-lang/rust/` 下的 `compiler/`、`library/`、`src/`、`tests/` 等核心目录），遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 地图与构建认知（concepts/）

* [简介与仓库导航](concepts/00-intro-repo-navigation.md) — 单仓库、双 workspace、三世界：编译器 79 个 crate、标准库 23 个目录、工具 45 个目录分属不同构建域。
* [bootstrap 构建系统](concepts/01-bootstrap-build-system.md) — Python 壳、Rust 芯与三阶段自举：起点是 `src/stage0` 锁定的固定哈希 beta 编译器。
* [编译器流水线总览](concepts/02-compiler-pipeline-overview.md) — 入口链与 query 心智模型：passes.rs 的函数序列只是骨架，按需求值才是执行模型。

## 沿数据流推进（concepts/）

* [解析与宏展开](concepts/03-parsing-macro-expansion.md) — 从字节流到 AST：rustc_lexer/rustc_parse/rustc_expand/rustc_builtin_macros。
* [HIR 与 AST Lowering](concepts/04-hir-ast-lowering.md) — 面向编译器的第二个 AST：rustc_ast_lowering、rustc_hir_analysis、rustc_hir_typeck。
* [类型系统与 trait 求解](concepts/05-type-system-trait-solving.md) — TyCtxt、InferCtxt 与下一代求解器：四个 TyKind 与中央数据仓库 rustc_middle。
* [MIR 与借用检查](concepts/06-mir-borrow-checking.md) — THIR→MIR 构建与 NLL：数据在 rustc_middle、构建在 mir_build、检查在 borrowck。
* [MIR 优化与代码生成](concepts/07-mir-optimization-codegen.md) — pass 流与三大后端：四组 pass 编排、monomorphize 与 LLVM/Cranelift/GCC。

## 标准库纵队（concepts/）

* [标准库分层架构](concepts/08-std-layered-architecture.md) — core→alloc→std 洋葱与平台分发：零依赖宣言、sys/os 两级分发、sysroot 聚合与 panic 运行时。

## 高级横切面（concepts/）

* [rustc 基础设施](concepts/09-rustc-infrastructure.md) — span、query 系统、元数据与名称解析：rustc_queries! 全仓库唯一一处。
* [rustdoc 与工具链](concepts/10-rustdoc-toolchain.md) — 45 个工具目录与测试套件：librustdoc 内部结构、Miri、compiletest。
* [诊断与错误体系](concepts/11-diagnostics-error-system.md) — DiagCtxt 与贯穿各阶段的 diagnostics 模式。

## 实战示例（examples/）

* [x.py 构建流程剖析](examples/x-py-build-walkthrough.md) — 沿一次 ./x 调用逐层走读构建系统的完整调用链。
* [std 模块结构剖析](examples/std-module-anatomy.md) — 以 library/std 为标本的逐层模块走读与 API 表面剖析。

## 信源登记簿（references/）

* [rustc 编译器信源登记](references/rustc-source-map.md) — 基线 commit、79 crate 清单、流水线各 crate 关键文件/行号坐标、tests/ 22 套件索引。
* [标准库信源登记](references/std-source-map.md) — library/ 23 目录清单、core/alloc/std 关键坐标、sysroot/rtstartup/panic 运行时坐标、构建特殊配置。

## 信任与生命周期说明

* **status 判定依据**：全部 16 个内容文档（12 个概念 + 2 个示例 + 2 个信源登记）均 `status: stable`。内容基于对 rust-lang/rust 源码（`external/libs/rust-lang/rust/` 目录，main @ e457a7b0，版本 1.100.0）核心子系统的逐模块阅读与事实提取（133 条源码事实，编号 F-rust-001~133），经 source-code-to-okf-wiki 五阶段流程（R→I→E→V→C）生成。
* **stale_after 解释**：统一设置为 `2027-08-28`。rustc 的核心架构（query 驱动执行模型、AST→HIR→THIR/MIR 数据流、core→alloc→std 洋葱分层）长期保持稳定；该日期作为对未来演进（如 next-trait-solver 全面接管、MIR pass 调整、新平台目录增删）的保守重新评估节点。文档中引用的行号均为采集时快照，主分支后续提交可能导致行号漂移，结构判断（模块清单、类型定义归属、crate 边界）的衰减则慢得多。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-28）；`verified.at` 记录 V 阶段对抗审查核验事件（2026-08-28），两者分离、可追溯。每条论断均可按信源登记页给出的路径 + 符号名回到源码复核。

本知识包共收录 16 个内容文档（12 个概念 + 2 个示例 + 2 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
