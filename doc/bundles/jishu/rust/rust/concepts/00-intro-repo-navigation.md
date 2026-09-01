---
type: Concept
title: 简介与仓库导航：单仓库、双 workspace、三世界
description: rust-lang/rust 仓库的整体解剖：一个仓库内两个独立 Cargo workspace、编译器/标准库/工具三个构建世界，以及版本真源 src/version
tags: [rust, rustc, repository, navigation]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rustc-source
    resource: /references/rustc-source-map.md
---

# 简介与仓库导航：单仓库、双 workspace、三世界

## 本知识包是什么

本知识包是 [rust-lang/rust](https://github.com/rust-lang/rust)（Rust 语言的主源码仓库）的系统化中文教程，基于 main 分支 commit `e457a7b0`（版本 1.100.0）源码深度阅读生成。README 第一句即定位了仓库的内容边界："This is the main source code repository for Rust. It contains the compiler, standard library, and documentation."——编译器、标准库与文档同住一个仓库。

阅读 rust-lang/rust 源码的第一个心智门槛不是任何具体算法，而是**仓库解剖**：它看起来是"一个仓库"，实际是"两个 workspace、三个世界"。不先建立这张地图，任何源码导航都会迷路。

## 三个世界：编译器、标准库、工具

| 世界 | 位置 | 规模 | 构建域 |
|------|------|------|--------|
| 编译器 | `compiler/` | 79 个子目录（rustc 壳 + 78 个 rustc_* crate） | 根 Cargo workspace |
| 标准库 | `library/` | 23 个顶层目录 | **独立** Cargo workspace |
| 工具 | `src/tools/` | 45 个磁盘目录（其中 36 个是根 workspace 成员） | 大部分属根 workspace，少数外部维护 |

三个通行认知在这里被打破：

**认知一：「一个仓库 = 一个 workspace」**。实际是双 workspace 并存：根 Cargo.toml 声明 `[workspace] resolver = "2"`，编组 `compiler/rustc` 与 78 个 rustc_* crate、`src/build_helper`、三个 `src/rustc-std-workspace/*`、`src/rustdoc-json-types`、`src/shim_utils` 及 38 个 `src/tools/*` 成员条目；而 `library/` 是第二个 workspace（`resolver = "1"`，成员仅 std、sysroot、coretests、alloctests）。此外根 workspace 还显式 exclude 了 6 个路径：`build`、`compiler/rustc_codegen_cranelift`、`compiler/rustc_codegen_gcc`、`src/bootstrap`、`tests/rustdoc-gui`、`obj`——两个备选代码生成后端与构建系统本身都不在主 workspace 内。

**认知二：「版本号写在 Cargo.toml」**。实际版本真源是 `src/version` 单行文件，内容就是 `1.100.0`。构建系统读取它作为整个发行链的版本号；查版本一律看这里。

**认知三：「tools 目录都参与主构建」**。磁盘上 45 个工具目录只有 36 个是 workspace 成员；差集中的 cargo、enzyme、rust-analyzer、rustc-perf、rustbook、error_index_generator 等不在根 workspace members 中。其中 rust-analyzer 尤其特殊：它自带独立的 Cargo.toml、Cargo.lock、rust-version、josh-sync.toml、AGENTS.md、AI_POLICY.md 等文件，是 subtree/submodule 型的外部维护工具。

## 仓库顶层布局

```
rust-lang/rust/
├── x.py / x            # 构建入口（x.py 自述只是 bootstrap.py 的 "symlink"）
├── Cargo.toml          # 根 workspace（resolver = "2"）
├── src/
│   ├── version         # 版本真源：单行 "1.100.0"
│   ├── stage0          # bootstrap 起点锁定文件（哈希清单）
│   ├── bootstrap/      # 构建系统本体（Rust crate，被根 workspace exclude）
│   ├── librustdoc/    # rustdoc 本体
│   ├── tools/          # 45 个工具目录
│   └── …               # build_helper、ci、doc、etc、gcc、llvm-project、
│                       # rustc-std-workspace、rustdoc-json-types、shim_utils
├── compiler/           # 79 个编译器 crate
├── library/            # 标准库独立 workspace（23 个目录）
└── tests/              # 22 个测试套件
```

`src/` 顶层子目录包括：bootstrap、build_helper、ci、doc、etc、gcc、librustdoc、llvm-project、rustc-std-workspace、rustdoc-json-types、shim_utils、tools。

## 版本、许可与治理事实

- **版本**：`src/version` 单行 `1.100.0`（本知识包基线）。
- **许可证**：README 声明 Rust "primarily distributed under the terms of both the MIT license and the Apache License (Version 2.0), with portions covered by various BSD-like licenses."
- **商标**："The Rust Foundation owns and protects the Rust and Cargo trademarks and logos."
- **仓库治理**：仓库根存在 `AGENTS.md`，内容为 LLM 使用政策与编辑门槛规则（外部仓库路由、禁止文本、reviewer 门槛、soundness 分类等），并声明 `x.py` 是本仓库的构建工具（调用方式 `./x`）。
- **构建入口**：`x.py` 第 5 行注释自述 "This file is only a 'symlink' to bootstrap.py, all logic should go there."——它把 `src/bootstrap` 插入 `sys.path` 后 `import bootstrap` 并调用 `bootstrap.main()`。

## 值得注意的构建细节

根 Cargo.toml 里藏着两处"反直觉"的 profile 调优，都能帮助读者体会这个仓库的工程精细度：

- `lld-wrapper` 与 `wasm-component-ld-wrapper` 两个包在 release profile 下设 `debug = 0`、`strip = true`，注释称它们是 "very thin wrappers around executing lld"——极薄的包装器不值得携带调试信息。
- 测试专用 crate `test-float-parse` 在 dev 与 release 两个 profile 下均设 `opt-level = 3`，注释直言 "Bigint libraries are slow without optimization"——即使是测试，浮点解析的 bigint 依赖慢到必须开优化。

## 测试世界一览

`tests/` 顶层有 22 个套件目录：assembly-llvm、auxiliary、build-std、codegen-llvm、codegen-units、coverage、coverage-run-rustdoc、crashes、debuginfo、incremental、mir-opt、pretty、run-make、run-make-cargo、rustdoc-gui、rustdoc-html、rustdoc-js、rustdoc-js-std、rustdoc-json、rustdoc-ui、ui、ui-fulldeps。其中 `ui` 是编译器行为测试的主力，`mir-opt` 守护 MIR 优化效果，六套 `rustdoc-*` 覆盖文档工具的输出。完整索引见 [rustc 编译器信源登记](/references/rustc-source-map.md)。

## 学习路径建议

本知识包按编译器流水线阶段递进组织：先立地图（本篇）与构建认知（[bootstrap 构建系统](/concepts/01-bootstrap-build-system.md)），再沿数据流推进（[流水线总览](/concepts/02-compiler-pipeline-overview.md) → [解析与宏展开](/concepts/03-parsing-macro-expansion.md) → [HIR](/concepts/04-hir-ast-lowering.md) → [类型系统](/concepts/05-type-system-trait-solving.md) → [MIR 与借用检查](/concepts/06-mir-borrow-checking.md) → [优化与代码生成](/concepts/07-mir-optimization-codegen.md)），标准库作为独立纵队（[标准库分层架构](/concepts/08-std-layered-architecture.md)），最后是横切面专题（基础设施、rustdoc 与工具链、诊断体系）。

读任何源码前，先判定目标属于哪个构建域；查版本，一律看 `src/version`。

## 相关概念

- [bootstrap 构建系统](/concepts/01-bootstrap-build-system.md) — 双 workspace 之一的构建机制：Python 壳、Rust 芯与三阶段自举
- [编译器流水线总览](/concepts/02-compiler-pipeline-overview.md) — 79 个 crate 如何串成一条编译数据流
- [标准库分层架构](/concepts/08-std-layered-architecture.md) — 另一个 workspace（library/）的洋葱分层
- [rustc 编译器信源登记](/references/rustc-source-map.md) — 79 crate 清单与关键文件坐标
