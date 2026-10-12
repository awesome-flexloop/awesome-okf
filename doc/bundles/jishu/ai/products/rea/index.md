---
okf_version: "0.2"
type: bundle
title: "REA：Reverse Engineer Anything（统一 MCP 契约的本地逆向编排器）"
description: "REA（npm 包 rea-agents v6.4.0，MIT）——用一套统一 MCP 契约把 AI agent 连接到用户自备的逆向工具（Ghidra/IDA/Hopper/JEB/ADB/JADX/EVM/WASM/.NET/固件/网站/进程）的本地优先编排层，而非反编译器本体：MCP 契约层单一事实源（100+ 工具）、Provider 适配器、八大目标域、CLI/MCP 双入口（129 顶层命令）与领域类型/证据模型"
tags: [rea, mcp, reverse-engineering, ghidra, ida, hopper, jadx, evm, wasm, local-first, agent-tools]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T10:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: local-source
    url: "https://github.com/morluto/rea @ eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
  - id: rea-tools-doc
    url: "https://rea.tools/zh-CN/"
  - id: docs-full
    url: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/docs @ 49 个 .md"
---

# REA：Reverse Engineer Anything

> **类型**：可安装工具包（含可照做 examples/；命令经源码/官方文档核对，未在本机实跑）
> **信源**：本地源码 `external/dao/rea`（npm 包 `rea-agents` v6.4.0，MIT，固定 commit `eaf88aca`）+ 官方文档 `rea.tools` + `docs/` 全量 49 个 `.md`（facts.md 登记 F-001~F-131）
> **口径**：事实唯一来源为 `references/facts.md`；动态数字（Star 等）不作为规范事实，仅按快照登记（见 [references/source-manifest.md](references/source-manifest.md)）

## 本文概要

[REA](https://github.com/morluto/rea)（Reverse Engineer Anything）官方定位是 "Reverse engineer anything from your terminal or agent with one CLI and MCP server."（F-006）。它是 npm 包 **`rea-agents` v6.4.0（MIT）**（F-001/002/003），对外只暴露一个 MCP 服务名 **`io.github.morluto/rea`**（F-004）与统一 CLI。它的本体不是某个反编译器，而是一层**适配编排层**：把用户自备的逆向工具（Ghidra/IDA/Hopper、JADX/Apktool/ADB、EVM/WASM、Binwalk/Unblob、CDP 浏览器等）经 **Provider 适配器**接入统一 MCP 契约（`TOOL_CONTRACTS` 聚合 100+ 个契约化工具），让一个 agent 用一套契约就能覆盖 native/Android/.NET/EVM/WASM/固件/网站/进程等目标域。

## 阅读路径

**先建立概念（10 分钟）**

1. [REA 是什么：产品身份与定位](concepts/01-rea-overview.md)——npm 包、版本、许可、MCP 服务名、产品定位
2. [MCP 契约层：单一事实源与工具全集](concepts/02-mcp-contract.md)——为什么契约是主体、工具全集从哪来
3. [Provider 适配器：如何接入分析工具](concepts/03-provider-adapters.md)——为什么 REA 不自己反编译

**核心机制**

4. [领域类型与证据模型](concepts/06-domain-types-and-evidence.md)——分析结果如何被规整为 agent 可消费的证据

**能分析什么 / 怎么用**

5. [支持的分析目标域与工具矩阵](concepts/04-analysis-domains.md)——八大目标域边界与要求
6. [安装、setup 与 CLI/MCP 双入口](concepts/05-cli-and-setup.md)——安装一次、两端同源

**深入指定域**

7. [JavaScript / Web 浏览器域](concepts/07-js-web-domains.md)——应用图、模块追溯、浏览器 ADB/CDP 捕获
8. [Native 二进制与专项 Ghidra](concepts/08-native-ghidra-specialty.md)——Mach-O/dylib、逐格式 Ghidra 适配矩阵
9. [平台分析域深挖](concepts/09-platform-domains-deep.md)——Android/.NET/固件/Apple/Electron/HarmonyOS
10. [从逆向工具到可审计重建工程](concepts/10-engineering-workflow.md)——9 阶段工作流与义务台账

**再动手实操**

11. [CLI 与 MCP 使用示例](examples/cli-and-mcp-usage.md) / [分析工具安装与 Provider 接入](examples/provider-setup.md)——可照做流程
12. [JS 应用重建示例](examples/js-reconstruction-example.md) / [平台深挖示例](examples/platform-deep-example.md) / [重建工程工作流示例](examples/reconstruction-workflow-example.md)——对照 docs 可复现路径

## 核心事实速查

| 项 | 值 |
|----|-----|
| 包名 / 版本 / 许可 | `rea-agents` / **6.4.0** / **MIT**（F-001/002/003） |
| MCP 服务名 | `io.github.morluto/rea`（F-004） |
| 仓库 | https://github.com/morluto/rea（F-005） |
| Node 支持 | `^22.19.0 \|\| ^24.11.0 \|\| >=26.0.0`（F-007） |
| 入口 | `rea` 与 `rea-agents` 双命令，指向 `scripts/rea.mjs` 双层路由（F-010/011） |
| CLI 顶层命令 | **129** 个（F-013） |
| MCP 工具契约 | `TOOL_CONTRACTS` = 24 组 spread、100 处 `*ToolContracts.ts` 工具名、38 个官方桥接工具、15 种 kind（F-020/024/023/028） |
| 目标域 | native / JavaScript+Electron / .NET / Android(APK+设备) / EVM / WASM / 固件 / 网站 / 进程（F-055） |
| 架构 | 不沙箱、不托管运行；本地优先、显式选择、有界证据（F-050/051/053/045） |
| JS 域核心 | `JavaScriptApplicationGraph` 应用图、12 关系词汇、runtime 观测/协同（F-067/068/076） |
| 专项 Ghidra | 逐格式/逐 ABI 适配矩阵 + 版本钉扎（DOS/MIPS32r2/PSP/NativeAOT/Windows，F-088~F-096） |
| 平台域深挖 | Android jadx/ADB、.NET Managed、固件 Binwalk、Apple/Electron/HarmonyOS、EVM/WASM（F-103~F-118） |
| 工程工作流 | 9 阶段可审计重建 + 义务台账 + closure_digest（F-125~F-131） |

## ⚠️ 阅读前必知的三条口径要点

1. **REA 不自己反编译**：分析计算发生在你自备的工具（Ghidra/IDA/Hopper…）内，REA 只做编排与证据标准化（见 [03 Provider 适配器](concepts/03-provider-adapters.md)）。用它前先确认已有相应分析工具。
2. **契约是主体，CLI 是投影**：能力全集以 `TOOL_CONTRACTS`（MCP 工具名）为准；CLI 129 命令只是契约的一个别名前端，存在约 50+ 个「仅有 MCP、无专用 CLI」的工具（F-017）。
3. **动态数字口径**：Star/App 下载量等动态数字跨信源不一致，本包不把任何动态数字作为规范事实，仅在 facts/source-manifest 中按快照登记；产品功能一律以本地源码 `main@eaf88aca`（v6.4.0）为准。

## 采用提示与已知边界

- **本地优先 + 自带工具**：REA 不虚拟化/沙箱目标；目标可信度与隔离由「你选的分析工具 + 你的命令」决定（F-050 进程捕获「非沙箱」）。
- **网站/进程默认离线附着而非拉取**：网站通过 CDP 附加到用户自有浏览器（F-051），WASM 不执行（F-045），WEB 网络捕获为离线操作（F-053）。
- **上手顺序建议**：`npx rea-agents setup` → 先 CLI 单次 `rea analyze <path>` 冒烟验证工具链 → 再接入 agent 走 MCP。
- **结果可信度**：看每条结果的 `evidence` 与 `unknowns` 字段（F-043）——证据非空、unknowns 小的结果才适合直接交给 agent 推理。
- **边界**：软件生命周期、KPI 数据、商业承诺等不在本包覆盖范围；本包只覆盖源码/文档可核验的结构性事实与命令能力。

## 信源与可信度

- 事实清单（F-001~F-131）：[references/facts.md](references/facts.md)
- 架构洞察与知识地图：[references/insights.md](references/insights.md)
- 信源登记与公开性预检：[references/source-manifest.md](references/source-manifest.md)

## 主题关联

- [octop](../octop/index.md)：本仓库同类「本地优先 + MCP 工具接入 agent」的自托管 AI 平台（Agent 工具生态相邻）
- [loopx](../loopx/index.md)：长程 Agent 控制面（Agent 工具调用生态相邻）
- [todesk-ai](../todesk-ai/index.md)：Computer Use 工具化实践（Agent 工具/逆向相邻）
- [wigolo](../wigolo/index.md)：AI Agent 本地 Web 情报层（local-first Agent 基础设施）
- [mobile-use](../mobile-use/index.md)：移动设备控制 Agent（设备分析与工具化相邻）

```{toctree}
:maxdepth: 2
:hidden:

concepts/index
examples/index
references/index
log
```