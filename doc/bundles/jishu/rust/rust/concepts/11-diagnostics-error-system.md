---
type: Concept
title: 诊断与错误体系：DiagCtxt 与贯穿各阶段的 diagnostics 模式
description: rustc_errors 的 DiagCtxt 家族与建议/替换数据结构，以及"每个阶段 crate 自带 diagnostics 模块"的贯穿性组织模式
tags: [rust, rustc, diagnostics, errors]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rustc-source
    resource: /references/rustc-source-map.md
---

# 诊断与错误体系：DiagCtxt 与贯穿各阶段的 diagnostics 模式

## 主锚：rustc_errors 的 DiagCtxt 家族

诊断体系的中枢 crate 是 rustc_errors。其 src/lib.rs 的 pub 模块：annotate_snippet_emitter_writer、codes、emitter、formatting、json、markdown、timings；核心结构体：

| 结构 | 行号 | 角色 |
|------|------|------|
| `CodeSuggestion` | L157 | 一条修复建议（含替换区段） |
| `Substitution` | L193 | 具体替换文本 |
| `ExplicitBug` | L263 | 显式 bug（ICE 的显式形态） |
| `DelayedBugPanic` | L267 | 延迟 bug panic |
| `DiagCtxt` | L272 | 诊断上下文本体 |
| `DiagCtxtHandle<'a>` | L277 | 诊断上下文句柄 |
| `DiagCtxtFlags` | L415 | 诊断行为开关 |

模块表同样信息量大：`emitter` 是输出后端（终端/JSON），`annotate_snippet_emitter_writer` 接入外部 annotate-snippets 渲染库，`json` 支撑 `-Zunpretty` 与 IDE 的 JSON 诊断流，`codes` 对接错误码注册表，`timings` 是性能计时输出。

**DiagCtxt 是诊断的唯一入口约定**：各阶段代码不直接打印，而是把带 span 与结构化载荷的 Diag 提交给 DiagCtxt，由 emitter 统一渲染。`CodeSuggestion`/`Substitution` 两个结构是"帮助信息"（help）的数据形态——IDE 一键修复吃的就是它们。`ExplicitBug` 与 `DelayedBugPanic` 则是内部错误的分类：前者立即崩溃，后者延迟到安全点（避免在不一致状态下的二次崩溃）。

## 贯穿模式：每个阶段 crate 的 diagnostics 模块

rustc 的诊断不是集中式"错误报告模块"，而是**分布式 + 中央协议**的组织：每个阶段 crate 自带一个 diagnostics 模块存放本阶段的错误类型（通常是 derive(Diagnostic) 的结构体），再由 rustc_errors 统一渲染。事实清单中可数的同类模式至少有：

| crate | diagnostics 载体 |
|-------|------------------|
| rustc_interface | 模块 `diagnostics`（与 interface、passes 等并列） |
| rustc_session | `Session` 持有 EarlyDiagCtxt（build_session_options 的首参即 `early_dcx: &mut EarlyDiagCtxt`） |
| rustc_expand | 模块 `diagnostics`（私有模块之一） |
| rustc_hir_analysis | `diagnostics`(pub) 模块 |
| rustc_hir_typeck | `diagnostics` 子模块 |
| rustc_infer | `diagnostics`（私有模块之一） |
| rustc_trait_selection | `diagnostics` pub 模块（trait 错误信息的主产地） |
| rustc_borrowck | `borrowck_errors`、`diagnostics`、`session_diagnostics` 三个模块 |
| rustc_codegen_ssa | `diagnostics` pub 模块 |
| rustc_metadata | `diagnostics` pub 模块 |
| rustc_resolve | `diagnostics`（私有模块之一） |

这张表揭示了 rustc 源码的又一个"形态识别符"：**看到一个 crate 里有 diagnostics 模块，就知道它负责产出结构化错误**；`session_diagnostics` 的命名变体（如 rustc_borrowck）则表示用宏派生的会话诊断类型。

## 配套 crate：错误码与本地化

诊断的"编号世界"由两个 crate 承载（70-crate 清单中的成员）：**rustc_error_codes**（错误码注册表，即 E0xxx 的真源）与 **rustc_error_messages**（错误消息的翻译/本地化层）。三者分工：rustc_errors 定义机制，error_codes 定义编号，error_messages 定义文案——拆开机制、编号、文案是诊断体系能做本地化与 IDE 集成的基础。

## 诊断贯穿编译器的四个证据点

1. **驱动层**：rustc_driver_impl 的 run_compiler 接收的回调里可注册 lints（rustc_interface 的 Config 字段 `register_lints`）；early lint 检查是 queries.rs 里名字直白的 query（"perform lints prior to AST lowering"）。
2. **会话层**：`Session`（rustc_session）持有 EarlyDiagCtxt，build_session_options 从命令行解析阶段就带诊断上下文——**诊断上下文的诞生早于编译本身**。
3. **流水线各层**：上表所列每个阶段的 diagnostics 模块。
4. **rustdoc 层**：librustdoc 的 main_args 也以 `early_dcx: &mut EarlyDiagCtxt` 开场——连文档工具都复用同一套会话级早期诊断协议。

## 会话内外的两级诊断

一个值得建立的心智区分：**EarlyDiagCtxt**（早期诊断，命令行解析等"Session 尚未建成"阶段）与 **DiagCtxt**（会话诊断，编译主体阶段）。`build_session_options(early_dcx: &mut EarlyDiagCtxt, matches: &getopts::Matches)` 的签名与 librustdoc 的 `main_args(early_dcx: &mut EarlyDiagCtxt, ...)` 签名共同说明：编译器把"启动期报错"与"编译期报错"设计为两级不同语境——启动期的错误（如非法命令行参数）没有 span 可言，只能用早期上下文裸报。

## 相关概念

- [rustc 基础设施](/concepts/09-rustc-infrastructure.md) — 诊断所依附的 Span 与 query 系统
- [编译器流水线总览](/concepts/02-compiler-pipeline-overview.md) — Session 与 EarlyDiagCtxt 在入口链中的诞生点
- [MIR 与借用检查](/concepts/06-mir-borrow-checking.md) — borrowck_errors：错误信息最密集的阶段之一
- [rustc 编译器信源登记](/references/rustc-source-map.md) — rustc_errors 家族的精确行号坐标
