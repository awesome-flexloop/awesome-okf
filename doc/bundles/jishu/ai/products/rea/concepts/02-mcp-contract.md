---
okf_version: "0.2"
type: Concept
title: "MCP 契约层：单一事实源与工具全集"
description: "REA 的能力边界集中在 src/contracts/ —— TOOL_CONTRACTS 以只读 as const 数组聚合 24 组工具契约、统一 ToolContract 类型、15 种 kind、38 个官方代理工具，CLI 命令与 MCP 运行时都由此派生（证据：F-019~F-029, F-004）"
tags: [rea, mcp, tool-contracts, single-source-of-truth, reverse-engineering, contracts]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T10:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: local-source
    url: "https://github.com/morluto/rea @ eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
  - id: rea-tools-doc
    url: "https://rea.tools/zh-CN/"
---

# MCP 契约层：单一事实源与工具全集

> ARTICLE-DEPENDENT 前置：建议先读 [01 REA 是什么](01-rea-overview.md) 建立全局视图。本文与洞察二对应（见 [references/insights.md](../references/insights.md)「洞察二」）。

## 核心论断：契约是主体，CLI 是投影

REA 的能力边界**不是散落的命令**，而是集中在契约层 `src/contracts/`。多数 CLI 工具是「命令为主体、内部调用共享函数」；REA 反其道而行——**契约（MCP 工具定义）是主体，CLI 只是契约的一个前端投影**。证据：存在大量「只有 MCP 工具、没有 CLI 命令」的能力，且 CLI 命令名与 MCP 工具名并不一一对应、需要别名映射。

## TOOL_CONTRACTS：单一聚合清单

- MCP 工具契约的单一聚合清单为 `TOOL_CONTRACTS`，以只读 `as const` 数组聚合导出（F-019）。
- 它由 **24** 个工具契约数组 spread 汇总而成（F-020），聚合自 24 个导入变量——`OFFICIAL_TOOL_CONTRACTS`、`ENHANCED_TOOL_CONTRACTS`、`NATIVE_TOOL_CONTRACTS`、`EVM_TOOL_CONTRACTS`、`WASM_TOOL_CONTRACTS`、`ADB_TOOL_CONTRACTS`、`FIRMWARE_TOOL_CONTRACTS` 等（F-021）。

## 统一契约类型 ToolContract

- 通用契约类型 `ToolContract<Name, InputSchema, OutputSchema>`，字段含 `name/title/description/kind/inputSchema/outputSchema/effects/annotations/examples`（F-022）。
- `TOOL_KINDS` 定义 **15** 种 kind：`official-proxy`、`enhanced`、`native-provider`、`artifact-provider`、`managed-provider`、`android-provider`、`apktool-provider`、`jeb-provider`、`adb-provider`、`firmware-provider`、`browser-provider`、`electron-provider`、`runtime-provider`、`application`、`session`（F-023）。

## 官方桥接工具（kind=official-proxy）

- `OFFICIAL_TOOL_CONTRACTS` 在 `officialToolContracts.ts` 以 `official("name", ...)` 声明 **38** 个（F-024）。
- 官方工具名含 `annotate_native_function`、`inspect_native_load_image`、`inspect_native_data_type`、`resolve_native_call_targets`、`address_name`、`comment`、`current_address`、`list_bookmarks`、`list_procedures`、`list_strings`、`procedure_pseudo_code`、`read_function_instructions`、`search_procedures`、`search_strings`、`xrefs` 等（F-025）。
- 官方工具另含来自 Hopper 内存契约扩展（`...HOPPER_MEMORY_TOOL_DEFINITIONS.map(...official)`），定义于 `src/contracts/hopperMemoryContracts.ts`（F-026）。

## 契约按目标域分散组织

各域工具契约按子域分散在多个文件（F-027）：`wasm/wasmToolContracts.ts`、`evm/evmToolContracts.ts`、`firmware/firmwareToolContracts.ts`、`android/androidToolContracts.ts`、`apktool/apktoolToolContracts.ts`、`jeb/jebToolContracts.ts`、`adb/adbToolContracts.ts`、`managed/managedToolContracts.ts`、`javascript/electronToolContracts.ts`、`javascript/javascriptRecoveryToolContracts.ts`、`native/nativeToolContracts.ts`、`native/binaryDiagnosticsToolContracts.ts` 等。

- 21 个 `*ToolContracts.ts` 文件中，以 `name: "..."` 属性形式直接声明工具名合计 **100** 处（不含 `official("...")` 函数形式的 `officialToolContracts.ts`）（F-028）。

## 契约 ↔ CLI 的映射

- 命令到 MCP 工具的映射在 `CLI_COMMAND_TOOL_ALIASES` 声明，如 `analyze → binary_overview`、`inspect → binary_overview`、`decompile → procedure_pseudo_code`、`function → analyze_function`、`search → search_strings/search_procedures`、`trace → trace_feature`（F-016）。
- 存在 `MCP_TOOLS_WITHOUT_DEDICATED_CLI`（无专用 CLI、仅 MCP 暴露的工具），含 `analyze_function`、`compare_functions`、`compare_artifacts`、`export_evidence_bundle`、`import_evidence_bundle`、`correlate_static_and_runtime`、`get_call_graph`、`open_binary`、`close_binary`、`binary_session` 等约 50+ 项（F-017）——说明**契约全集 ⊇ CLI 子集**。

## 会话健康与工具可用性

- 会话健康/目录身份工具 `binary_session` 是运行中服务目录身份与工具可用性的权威来源：`tools/list` 返回完整工具清单、含当前不可用工具（F-029）。

## 对外单入口

最终所有能力聚合后对外呈现为一个 MCP 服务（mcpName `io.github.morluto/rea`，F-004）——即「一套契约、一个入口、多种目标」。

## 阅读下一步

- [04 · 支持的分析目标域与工具矩阵](04-analysis-domains.md)——这些契约工具落到哪些目标域
- [03 · Provider 适配器：如何接入分析工具](03-provider-adapters.md)——契约背后的 Provider 适配器如何接入外部工具