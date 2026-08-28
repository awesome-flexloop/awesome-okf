---
type: Concept
title: rustdoc 与工具链：45 个工具目录与测试套件
description: librustdoc 的内部结构与二进制壳、Miri 的 MIR 解释执行世界、src/tools 下 45 个工具目录与 36 个 workspace 成员的差集、测试执行器 compiletest
tags: [rust, rustdoc, tools, testing]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rustc-source
    resource: /references/rustc-source-map.md
---

# rustdoc 与工具链：45 个工具目录与测试套件

## rustdoc：住在 src/ 而非 compiler/ 的文档工具

rustdoc 本体是 `src/librustdoc`：Cargo.toml 声明 `name = "rustdoc"`、`version = "0.0.0"`、`edition = "2024"`。它的目录结构：

- **clean/**（含 cfg、types、utils）——把 rustc 的内部表示"清洗"为文档模型；
- **doctest/**——文档测试的执行支持；
- **formats/**——输出格式层；
- **html/**（含 escape、highlight、layout、length_limit、markdown、render、static、templates、toc、url_parts_builder）——HTML 渲染全家桶；
- **json/**、**theme/**、**passes/**（含 lint）。

lib.rs 的模块清单（L99-120）：calculate_doc_coverage、clean、config、core、display、docfs、doctest、error、externalfiles、fold、formats、html(pub)、json、markdown、passes、scrape_examples、theme、visit、visit_ast、visit_lib。

入口双函数：`pub fn main() -> ExitCode`(L122) 与 `fn main_args(early_dcx: &mut EarlyDiagCtxt, at_args: &[String])`(L805)。

二进制壳在 `src/tools/rustdoc/main.rs`，全文仅 13 行：`#![feature(rustc_private)]`、`extern crate rustc_driver;`、调用 `rustc_driver::override_c_allocator_in_binary!()`，然后 `fn main() -> ExitCode { rustdoc::main() }`。这印证了 rustdoc 与 rustc 共享内部 API（`rustc_private` feature）的架构事实——rustdoc 是"编译器内部 API 的另一个消费者"。

## Miri：直接解释执行 MIR

Miri（`src/tools/miri`）是 Rust MIR 的实验性解释器，Cargo.toml description 原文："An experimental interpreter for Rust MIR (core driver)."，`name = "miri"`、`version = "0.1.0"`。

其目录结构揭示了它的疆域：src/（alloc、bin、concurrency、intrinsics、shims/unix、shims/windows、machine.rs、eval.rs、operator.rs、provenance_gc.rs、sym.rs 等）、cargo-miri/、miri-script/、priroda/、genmc-sys/、test-cargo-miri/、tests/（fail、panic、pass、utils、ui.rs）。lib.rs 定义 `pub mod sym`(L99) 与 `pub mod native_lib`(L113)。`shims/`（垫片）目录名精确描述了 Miri 的工作方式：对系统调用与外部函数提供解释级模拟；concurrency 模块支撑数据竞争检测。

## 工具全景：45 个目录的清单

`src/tools/` 磁盘上共 45 个顶层目录：build-manifest、bump-stage0、cargo、cargotest、clippy、collect-license-metadata、compiletest、coverage-dump、enzyme、error_index_generator、features-status-dump、generate-copyright、generate-windows-sys、html-checker、jsondocck、jsondoclint、libcxx-version、linkchecker、lint-docs、lld-wrapper、llvm-bitcode-linker、miri、miropt-test-tools、nix-dev-shell、opt-dist、remote-test-client、remote-test-server、replace-version-placeholder、run-make-support、rust-analyzer、rust-installer、rustbook、rustc-perf、rustdoc、rustdoc-gui-test、rustdoc-js、rustdoc-themes、rustfmt、test-float-parse、tidy、tier-check、unicode-table-generator、unstable-book-gen、wasm-component-ld、x。

粗分类（按功能）：**构建与发布**（build-manifest、bump-stage0、opt-dist、rust-installer、x）；**测试**（compiletest、cargotest、remote-test-client/server、jsondocck、jsondoclint、html-checker、linkchecker、test-float-parse、miropt-test-tools、coverage-dump、run-make-support）；**文档**（rustdoc、rustbook、unstable-book-gen、error_index_generator、lint-docs、rustdoc-gui-test、rustdoc-js、rustdoc-themes）；**lint 与格式**（clippy、rustfmt、tidy、tier-check、lint-docs）；**许可与合规**（collect-license-metadata、generate-copyright）；**代码生成辅助**（enzyme、lld-wrapper、llvm-bitcode-linker、wasm-component-ld、generate-windows-sys、unicode-table-generator、libcxx-version、features-status-dump）；**其他**（cargo、cargotest、miri、rustc-perf、rust-analyzer、nix-dev-shell、replace-version-placeholder）。

## 45 与 36 的差集

[仓库导航](/concepts/00-intro-repo-navigation.md) 已指出：磁盘 45 个工具目录只有 36 个是根 workspace members（含 clippy/clippy_dev、miri/cargo-miri 双成员）。差集（不在根 workspace 的）包括 cargo、enzyme、rust-analyzer、rustc-perf、rustbook、error_index_generator 等——它们要么是外部维护（如 cargo 在独立仓库开发），要么有独立构建流程。

rust-analyzer 是最典型的"飞地中的飞地"：含独立 Cargo.toml、Cargo.lock、rust-version、josh-sync.toml、AGENTS.md、AI_POLICY.md 等文件，是 subtree/submodule 型外部维护工具。

## 测试世界：compiletest 与 22 套件

测试执行器是 `src/tools/compiletest`（含 src/runtest/、directives.rs、executor.rs 等），它是根 workspace members 之一。[仓库导航](/concepts/00-intro-repo-navigation.md) 提到的 22 个 tests/ 套件由它统一驱动：ui/rustdoc-*（界面行为）、run-make/run-make-cargo（端到端构建）、mir-opt（MIR 优化）、incremental（增量编译）、debuginfo、assembly-llvm/codegen-llvm/codegen-units、coverage、crashes、pretty 等。

bootstrap 对测试的编排则由 build_steps/test 模块承接（见[bootstrap 构建系统](/concepts/01-bootstrap-build-system.md)），`x test` 命令（Kind::Test）把两者接在一起。工具自身的健康由 toolstate 机制追踪（build_steps 模块之一）。

## 相关概念

- [简介与仓库导航](/concepts/00-intro-repo-navigation.md) — 45/36 差集与三个世界
- [bootstrap 构建系统](/concepts/01-bootstrap-build-system.md) — Kind::Test 与 build_steps 编排
- [MIR 优化与代码生成](/concepts/07-mir-optimization-codegen.md) — Miri 解释的 MIR 数据结构来源
- [rustc 编译器信源登记](/references/rustc-source-map.md) — tests/ 22 套件完整索引
