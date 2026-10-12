---
okf_version: "0.2"
type: Example
title: "REA：CLI 与 MCP 使用示例"
description: "从 npx rea-agents setup 初始化到 rea analyze <path> 单次分析，再到接入 agent 客户端的 MCP 配置要点——CLI/MCP 双入口可照做流程（证据 F-010/011/013/014/056）"
tags: [rea, example, cli, mcp, setup, analyze, agent-integration]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T10:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: local-source
    url: "https://github.com/morluto/rea @ eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
  - id: rea-tools-doc
    url: "https://rea.tools/zh-CN/"
---

# 示例：CLI 与 MCP 使用示例

> ⚠️ **可复现性说明**：本示例的**输入（命令）/步骤明确**，理论上可独立复现。命令来自源码与官方文档核对（references/facts.md），**未在本机实际运行**。执行时以官方文档、`rea setup --help`、`rea doctor` 当前输出为准。

## 目标

在一台满足 Node 版本要求的机器上完成 REA 初始化，先用 CLI 单次分析验证工具链，再接入 agent 客户端走 MCP。

## 输入

- 一台满足 Node 支持范围的机器（`^22.19.0 || ^24.11.0 || >=26.0.0`，F-007），npm 存量 `npm@11.16.0`（F-008）。
- 目标分析文件（目录 / `.asar` / native 二进制等）。
- 若做 native/Android/EVM 等域分析，需已装相应分析工具（Ghidra/IDA/Hopper/JADX 等），见 [provider-setup.md](provider-setup.md)。

## 步骤

### 1. 初始化 setup

```bash
npx rea-agents setup
```

**预期**：完成 REA 初始化；`rea` 与 `rea-agents` 两条命令可用（bin 同时注册二者，F-010）。

### 2. 冒烟：CLI 单次分析

```bash
rea analyze <path>
```

对目录 / `.asar` 文件（未给 `--provider`/`--snapshot`）自动走静态 JavaScript 应用图 + Evidence 工作流（F-056）。`analyze` 命令映射到 MCP 工具 `binary_overview`（F-016）。

**预期**：无 error 输出，返回结构化结果（一带 evidence/覆盖率/unknowns，F-043）。

### 3. 验证工具链就绪（doctor 类）

```bash
rea doctor
```

以及 `rea capabilities`、`rea providers`（F-014）可查看能力与 Provider 就绪状态。

**预期**：可确认各 Provider（Ghidra/JADX 等）是否就绪，比直接走 MCP 更好排障（对应 insights「洞察三」行动）。

### 4. 其他代表性单次命令

```bash
rea inspect <path>        # inspect → binary_overview（F-016）
rea decompile <path>      # decompile → procedure_pseudo_code（F-016）
rea function <sym>        # function → analyze_function（F-016）
rea search <query>        # search → search_strings/search_procedures（F-016）
rea trace <feature>       # trace → trace_feature（F-016）
rea xrefs <target>        # 交叉引用（F-014）
rea compare-bundles ...   # 别名 compare-bundles（F-015）
rea evidence-export ...   # 证据导出（F-014）
rea capture-process ...   # 进程行为捕获（F-014/F-050）
```

> 注意：CLI 顶层命令共 129 个（F-013），命令与 MCP 工具名并非 1:1（F-016）；存在约 50+ 个「仅有 MCP、无专用 CLI」的工具（F-017）。

### 5. 进入 MCP 服务模式

```bash
rea --mcp        # 或 rea mcp（单参进入 MCP 服务模式，加载 dist/mcp/main.js）
rea mcp doctor   # 单独走 dist/mcpDoctor.js（F-011）
```

### 6. 接入 agent 客户端（MCP 配置要点）

- MCP 服务名（mcpName）为 `io.github.morluto/rea`（F-004）——接入 agent 时以此作为服务标识。
- 各 agent 客户端通常以「运行 `rea --mcp`（stdio）」方式暴露给 agent；把该命令配置为 MCP server 即可。
- 在 agent 端应**直接使用 MCP 工具名全集**（如 `binary_overview`、`procedure_pseudo_code`、`binary_session`），而非依赖 CLI 命令名（F-016/F-017）。
- 需要完整工具清单与可用性时调用 `binary_session`（返回含当前不可用工具的 `tools/list` 全集，F-029）。

## 输出 / 验收

- [ ] `npx rea-agents setup` 完成，`rea`/`rea-agents` 可识别（F-010）
- [ ] `rea analyze <path>` 返回结构化结果（F-056）
- [ ] `rea doctor` 报告各 Provider 就绪状态（F-014）
- [ ] `rea --mcp` 进入 MCP 服务模式（F-011）
- [ ] agent 客户端以 mcpName `io.github.morluto/rea` 接入并可 `tools/list`（F-004/F-029）

## 反模式提醒

- 不要在 agent 端依赖 CLI 命令名——存在大量「仅有 MCP、无专用 CLI」工具，且命令↔工具并非 1:1（F-016/F-017）。
- 不要把 `rea analyze` 的返回当作本地事实文件的长期形态：结果以 evidence/unknowns 结构化，后期应通过 `evidence-export`/`binary_session` 交互（F-014/F-029）。

## 阅读下一步

- [分析工具安装与 Provider 接入](provider-setup.md)——先装好 Ghidra/JADX 等再跑 analyze
- [安装、setup 与 CLI/MCP 双入口](../concepts/05-cli-and-setup.md)——双入口概念说明