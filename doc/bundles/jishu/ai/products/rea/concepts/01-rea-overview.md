---
okf_version: "0.2"
type: Concept
title: "REA 是什么：产品身份与定位"
description: "REA（Reverse Engineer Anything）的产品身份 —— npm 包 rea-agents v6.4.0（MIT）、MCP 服务名、官方定位语、Node 支持、目标域概览与『编排器而非反编译器』的定位（事实层）"
tags: [rea, product-profile, mit, mcp, reverse-engineering, local-first, project-profile]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T10:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: local-source
    url: "https://github.com/morluto/rea @ eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
  - id: rea-tools-doc
    url: "https://rea.tools/zh-CN/"
---

# REA 是什么：产品身份与定位

> 事实层（What / Who / License / 定位）。本文只陈述可核验的产品身份事实，架构机制请见 [MCP 契约层](02-mcp-contract.md) 与 [Provider 适配器](03-provider-adapters.md)。

## 一句话定位

REA（Reverse Engineer Anything）官方定位语为：

> "Reverse engineer anything from your terminal or agent with one CLI and MCP server."（F-006）

它是一层把 AI agent 连接到各种逆向工具的统一契约层——**不是又一个反编译器**，而是通过 Provider 适配器把用户自备的分析工具接入一个 MCP 服务 + CLI，让一个 agent 用一套契约覆盖多个目标域。核心洞察见 [references/insights.md](../references/insights.md)「洞察一」。

## 身份卡片

| 项目 | 值 | 出处 |
|------|-----|------|
| npm 包名 | `rea-agents` | F-001 |
| 版本 | **6.4.0** | F-002 |
| 许可 | **MIT**（根 LICENSE 首行 "MIT License"，Copyright (c) 2026 morluto） | F-003 |
| MCP 服务名 | `io.github.morluto/rea` | F-004 |
| 主仓库 | https://github.com/morluto/rea | F-005 |
| Node 支持 | `^22.19.0 \|\| ^24.11.0 \|\| >=26.0.0`（Node 23/25 及 prerelease 不支持） | F-007 |
| 存量包管理器 | `npm@11.16.0` | F-008 |
| 模块类型 | ESM（`"type": "module"`） | F-009 |

## 目标域概览

官网把支持的逆向目标概括为（F-055）：

> "native binaries, JavaScript and Electron apps, .NET assemblies, Android packages, firmware, and websites."

加上进程行为捕获，实际覆盖八大目标域，逐域的边界与工具要求见 [04 分析目标域](04-analysis-domains.md)。

## 入口形态：一个包，两条入口

安装一个 npm 包 `rea-agents`，bin 同时注册 `rea` 与 `rea-agents` 两个命令，均指向 `scripts/rea.mjs`（F-010）；该脚本双层路由——单参 `--mcp`/`mcp` 进入 MCP 服务模式，否则进入 one-shot CLI 模式（F-011）。CLI 顶层命令共 **129** 个（F-013），官方安装指引为 `npx rea-agents setup`，随后可接入多个 agent 客户端。详见 [05 安装、setup 与双入口](05-cli-and-setup.md)。

## 断言口径

- facts.md 中关于「X 个」的数量断言（如 129 命令、100 处工具名等）均标注计数方法与独立 Grep 输出，可复跑核验。
- 本包不把动态数字（Star 等）作为规范事实；版本与功能以本地源码 `main@eaf88aca`（v6.4.0）为准（见 [references/source-manifest.md](../references/source-manifest.md)）。

## 阅读下一篇

- [02 · MCP 契约层：单一事实源与工具全集](02-mcp-contract.md)——工具全集从哪来、为什么契约是主体
- [03 · Provider 适配器：如何接入分析工具](03-provider-adapters.md)——为什么 REA 不自己反编译
- [04 · 支持的分析目标域与工具矩阵](04-analysis-domains.md)——能分析什么、各域边界