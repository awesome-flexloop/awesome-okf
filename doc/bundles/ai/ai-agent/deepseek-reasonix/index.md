---
type: bundle
okf_version: "0.2"
scope: deepseek-reasonix
name: deepseek-reasonix
version: "0.1.0"
title: DeepSeek-Reasonix Wiki
description: DeepSeek 开源 Go 语言 AI 编码 Agent 的 OKF v0.2 Wiki  bundle——覆盖 Agent 运行循环、ACP 协议、Bot 网关、CLI/TUI、Checkpoint 恢复、Fleet/Subagent 架构
tags: [deepseek-reasonix, ai-agent, go, acp, bot-gateway, checkpoint, fleet]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-23T00:00:00Z
status: stable
stale_after: 2027-08-23
sources:
  - id: SRC-001
    resource: /references/source.md
    title: DeepSeek-Reasonix 源码信源索引
---

# DeepSeek-Reasonix Wiki

DeepSeek-Reasonix 是 DeepSeek 开源的 Go 语言 AI 编码 Agent，支持 ACP 协议、Wails 桌面应用、多平台 Bot 网关，以单个静态二进制分发。本 Wiki bundle 基于源码分析生成，所有事实可溯源到具体文件和行号。

## 快速导航

### 概念文档

| # | 文档 | 说明 |
|---|------|------|
| 00 | [Reasonix 简介](/concepts/00-introduction.md) | 项目概述、四种接入方式、技术栈 |
| 01 | [项目架构](/concepts/01-project-architecture.md) | 包分层、cmd 入口、boot 启动组装 |
| 02 | [Agent 运行循环](/concepts/02-agent-run-loop.md) | 核心循环、采样恢复、arbiter、governor、compaction |
| 03 | [ACP 协议](/concepts/03-acp-protocol.md) | NDJSON JSON-RPC、能力协商、Factory、inbox |
| 04 | [Bot 网关](/concepts/04-bot-gateway.md) | QQ/飞书适配器、会话隔离、消息渲染 |
| 05 | [CLI 与 TUI](/concepts/05-cli-tui.md) | 命令系统、Bubble Tea TUI、MCP/插件 |
| 06 | [Checkpoint 与恢复](/concepts/06-checkpoint-recovery.md) | blob 存储、事务回滚、fork/branch |
| 07 | [Fleet 与 Subagent](/concepts/07-fleet-subagents.md) | 并行调度、写路径声明、DAG 依赖 |

### 示例

- [基础使用](/examples/01-basic-usage.md)——安装、配置、CLI/TUI 基本对话
- [Bot 网关配置](/examples/02-bot-gateway.md)——QQ/飞书接入、会话隔离、审批

### 信源与规格

- [源码信源索引](/references/source.md)——按包索引的关键文件，关联事实编号
- [事实清单](/spec/facts.md)——107 条编号事实（F-001 至 F-107）
- [架构洞察](/spec/insights.md)——5 个核心洞察（陈述/证据/反常识/行动）

## 核心架构速览

```
                    ┌──────────────────────────┐
                    │       前端层              │
                    │  CLI/TUI │ Desktop │ ACP │ Bot │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │    boot.BuildRuntime     │
                    │  (配置→Controller 组装)   │
                    └────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
     ┌────────▼────────┐ ┌──────▼──────┐ ┌────────▼────────┐
     │  Agent          │ │  Tool       │ │  Provider       │
     │  ┌────────────┐ │ │  Registry   │ │  (DeepSeek/     │
     │  │ run loop   │ │ │  (builtin + │ │   OpenAI/       │
     │  │ arbiter    │ │ │   MCP)      │ │   Anthropic)    │
     │  │ governor   │ │ └─────────────┘ └─────────────────┘
     │  │ scheduler  │ │
     │  │ checkpoint │ │
     │  └────────────┘ │
     └─────────────────┘
```

## 变更日志

见 [log.md](/log.md)。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/index
log
```
