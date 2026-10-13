---
type: Concept
title: "安装、setup 与 CLI/MCP 双入口"
description: "REA 的安装与双入口 —— npm 包 rea-agents 的 bin 双命令、scripts/rea.mjs 双层路由、129 顶层命令、命令↔工具别名映射、官方 npx rea-agents setup、CLI/MCP 双端同源（证据：F-010~F-018, F-056）"
tags: [rea, cli, mcp, setup, installation, npm, double-entry, reverse-engineering]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T10:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: local-source
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
  - id: rea-tools-doc
    resource: "https://rea.tools/zh-CN/"
---

# 安装、setup 与 CLI/MCP 双入口

> ARTICLE-DEPENDENT 前置：先读 [01 REA 是什么](01-rea-overview.md) 与 [02 MCP 契约层](02-mcp-contract.md)。本文与洞察三对应（见 [references/insights.md](../references/insights.md)「洞察三」）。

## 核心论断：安装一次，两端同源

REA 不区分「CLI 用户」与「MCP 用户」——安装一个 npm 包 `rea-agents` 即同时获得两条入口，命令与工具语义保持一致，学习一次两处可用。官方安装指引为 `npx rea-agents setup`，随后可配置接入多个 agent 客户端。

## 单包双命令

- bin 同时注册 `rea` 与 `rea-agents` 两个命令，均指向 `scripts/rea.mjs`（F-010）。

## 双层路由

`scripts/rea.mjs` 用一个布尔判定决定入口（F-011）：

- 单参 `--mcp` / `mcp` → MCP 服务模式（加载 `dist/mcp/main.js`）；
- 否则 → one-shot CLI 模式（加载 `dist/cli.js`）；
- `mcp doctor` → 加载 `dist/mcpDoctor.js`。

## CLI 命令体系

- CLI 顶层命令由 `CLI_COMMANDS` 对象以 kebab-case 字符串集中声明（F-012），总数 **129** 个（F-013）。
- 一级代表性命令名含 `analyze`、`inspect`、`decompile`、`setup`、`doctor`、`uninstall`、`update`、`xrefs`、`trace`、`search`、`function`、`providers`、`capabilities`、`instructions`、`compare`、`capture-process`、`evidence-import`、`evidence-export` 等（F-014）。
- 命令别名机制：`CLI_COMMAND_ALIASES` 声明一个别名 `compare-bundles`（F-015）。
- CLI 由 `createCli()` 构建，各命令族以 `registerXxxCommands()` 注册（如 `registerWasmCommands`、`registerEvmCommands`、`registerSetupCommands`、`registerAdbCommands`、`registerBrowserCommands` 等），CLI 框架依赖 `incur@0.6.1`（F-018）。

## 命令 ↔ MCP 工具映射（非 1:1）

- `CLI_COMMAND_TOOL_ALIASES` 声明命令到 MCP 工具映射，如 `analyze → binary_overview`、`inspect → binary_overview`、`decompile → procedure_pseudo_code`、`function → analyze_function`、`search → search_strings/search_procedures`、`trace → trace_feature`（F-016）。
- 存在约 50+ 个「仅有 MCP、无专用 CLI」的工具（`MCP_TOOLS_WITHOUT_DEDICATED_CLI`）（F-017）。因此在 agent 端应直接使用工具名全集，而非依赖 CLI 命令名。

## 默认分析行为

`rea analyze PATH` 对目录 / `.asar` 文件（未给 `--provider`/`--snapshot` 时）自动选择静态 JavaScript 应用图 + Evidence 工作流（F-056）。

## 上手顺序建议

1. `npx rea-agents setup` 初始化；
2. 先 CLI 单次 `rea analyze <path>` 验证工具链（含 Ghidra 等）装好——doctor 类命令能暴露 Provider 是否就绪；
3. 再接入 agent 客户端走 MCP 批量分析。

> 若只用自动化/agent 场景，仍建议先跑一次 CLI 冒烟——它能暴露 Provider 就绪状态，比直接走 MCP 更好排障。

## 阅读下一步

- [CLI 与 MCP 使用示例](../examples/cli-and-mcp-usage.md)——`npx rea-agents setup`、`rea analyze <path>` 等可照做流程
- [分析工具安装与 Provider 接入](../examples/provider-setup.md)——Ghidra/IDA/… 本地准备与 doctor 校验
