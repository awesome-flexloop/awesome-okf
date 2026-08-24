---
type: bundle
okf_version: "0.2"
scope: codewhale
name: codewhale
version: "0.1.0"
source: local
description: "CodeWhale 开源 Rust 编码 Agent 的完整 OKF wiki 包，覆盖工作区架构、Agent 核心、MCP 协议、工具系统、Fleet 多 Agent、Workflow 引擎、Skills/Hooks、沙箱与执行策略。"
---

# CodeWhale Wiki

CodeWhale 是一个用 Rust 构建的开源终端编码 Agent，支持多模型 Provider、MCP 工具集成、Fleet 多 Agent 编排、Workflow 工作流引擎和操作系统级沙箱。本 wiki 包基于 CodeWhale v0.9.10 源码生成。

## 概述

CodeWhale 将一个约 68 万行的 Rust 编码 Agent 拆分为 21 个职责单一的 crate，从协议层到 UI 层形成严格的依赖方向。它起源于 `deepseek-tui`，现在是 provider 中立的独立维护项目。

**核心能力**：

- 多模型支持（42 种 ProviderKind，包括 DeepSeek、OpenAI、Anthropic、Google、Ollama 等）
- MCP 外部工具服务器集成（stdio + HTTP/SSE）
- Fleet 持久化多 worker 控制平面
- 双轨 Workflow 引擎（声明式 TOML IR + 命令式 QuickJS）
- 三层执行策略引擎（Builtin/Agent/User）
- macOS Seatbelt / Linux Bubblewrap 沙箱
- Skills 指令包 + Hooks 生命周期 + Plugin 插件系统
- 终端 TUI（ratatui）+ 本地 Web 客户端 + headless exec

## 功能特性

| 领域 | 描述 |
|------|------|
| **模型 Provider** | DeepSeek、OpenAI、Anthropic、Google、Meta、Mistral、Qwen、Grok、本地 Ollama/vLLM/SGLang 等 42 种 |
| **TUI 模式** | Plan（只读规划）、Work（多步执行）、Operate（多任务调度） |
| **权限姿态** | Ask、Auto-Review、Full Access |
| **MCP** | stdio 子进程 + HTTP/SSE 远程服务器，工具限定名 `mcp__server__tool` |
| **Fleet** | 8 种角色（worker/scout/planner/reviewer/builder/verifier/consultant/custom），持久化账本 |
| **Workflow** | 8 种节点类型、1000 agent/run 上限、JS 沙箱、确定性回放 |
| **安全** | 三层规则、链式命令检测、shell 展开绕过防护、Seatbelt/bwrap 沙箱 |
| **扩展** | Skills（SKILL.md）、Hooks（11 事件）、Plugins（hash-bound trust） |
| **持久化** | SQLite + JSONL，线程/消息树/检查点/任务 |
| **缓存** | KV-cache 前缀稳定性，冻结 system prompt + tool catalog |
| **记忆** | 原生 Markdown + SQLite FTS5，opt-in，按 git origin hash 限定范围 |
| **国际化** | 16 种语言（zh-Hans、zh-Hant、ja、ko、en 等） |

## 导航

### 概念文档

| 文档 | 说明 |
|------|------|
| [CodeWhale 简介](/concepts/00-introduction.md) | 项目定位、功能特性、安装方式 |
| [工作区架构](/concepts/01-workspace-architecture.md) | 21 个 crate 的 Cargo workspace、依赖关系图、核心分层 |
| [Agent 核心](/concepts/02-agent-core.md) | Runtime、Thread/Session 分离、Engine、JobManager |
| [MCP 协议](/concepts/03-mcp-protocol.md) | MCP 服务器生命周期、工具代理、JSON-RPC stdio |
| [工具系统](/concepts/04-tool-system.md) | ToolRegistry、ToolHandler、并行调度、参数验证 |
| [Fleet 多 Agent](/concepts/05-fleet-subagents.md) | Fleet 控制平面、角色分类、权限 clamp |
| [技能与 Hooks](/concepts/06-skills-hooks.md) | Skills 四层架构、Hooks 事件、插件系统 |
| [沙箱与执行策略](/concepts/07-sandbox-execpolicy.md) | 执行策略引擎、Shell 安全防护、OS 沙箱 |

### 示例

| 示例 | 说明 |
|------|------|
| [基本使用](/examples/01-basic-usage.md) | 安装、配置、基本对话、模式切换 |
| [Fleet 与 Workflow](/examples/02-fleet-workflow.md) | Fleet profile、CLI、TOML/JS Workflow、agent 委派 |

### 参考

| 参考 | 说明 |
|------|------|
| [源文件索引](/references/source.md) | 按 crate 组织的关键源文件清单 |

### 规格

| 文件 | 说明 |
|------|------|
| [事实清单 (F-001~F-110)](/spec/facts.md) | 110 条带源文件引用的编号事实 |
| [核心洞察](/spec/insights.md) | 5 条核心架构洞察（陈述/证据/反常识/行动） |

## 学习路径

### 路径一：新用户入门

1. [CodeWhale 简介](/concepts/00-introduction.md) — 了解项目是什么
2. [基本使用示例](/examples/01-basic-usage.md) — 安装并开始对话
3. [沙箱与执行策略](/concepts/07-sandbox-execpolicy.md) — 理解安全模型

### 路径二：架构理解

1. [工作区架构](/concepts/01-workspace-architecture.md) — 21 个 crate 如何组织
2. [Agent 核心](/concepts/02-agent-core.md) — Runtime、Engine、Session
3. [工具系统](/concepts/04-tool-system.md) — 工具注册、分发和并发
4. [MCP 协议](/concepts/03-mcp-protocol.md) — 外部工具集成

### 路径三：多 Agent 与工作流

1. [Fleet 多 Agent](/concepts/05-fleet-subagents.md) — 角色、权限 clamp
2. [Fleet 与 Workflow 示例](/examples/02-fleet-workflow.md) — 实际配置和脚本
3. [技能与 Hooks](/concepts/06-skills-hooks.md) — 扩展和自动化

## 目录结构

```
codewhale/
├── index.md                    # 本文件（bundle 根索引）
├── log.md                      # 变更日志
├── spec/
│   ├── facts.md                # R Phase: 110 条编号事实
│   └── insights.md             # I Phase: 5 条核心洞察
├── references/
│   ├── index.md
│   └── source.md               # 源文件索引（按 crate）
├── concepts/
│   ├── index.md
│   ├── 00-introduction.md
│   ├── 01-workspace-architecture.md
│   ├── 02-agent-core.md
│   ├── 03-mcp-protocol.md
│   ├── 04-tool-system.md
│   ├── 05-fleet-subagents.md
│   ├── 06-skills-hooks.md
│   └── 07-sandbox-execpolicy.md
└── examples/
    ├── index.md
    ├── 01-basic-usage.md
    └── 02-fleet-workflow.md
```

## 技术栈

- **语言**：Rust 2024 edition（rustc 1.88+）
- **异步运行时**：tokio 1.50（多线程）
- **终端 UI**：ratatui 0.30.2 + crossterm 0.29
- **持久化**：rusqlite 0.40（SQLite，bundled）+ JSONL
- **HTTP 服务器**：axum 0.8 + tower-http
- **JS 引擎**：rquickjs 0.12（QuickJS，单线程）
- **HTTP 客户端**：reqwest 0.13（rustls）
- **序列化**：serde + serde_json + toml
- **全局分配器**：mimalloc
- **MCP 协议**：rmcp 2.2.0

## 源码来源

本 wiki 包基于以下源码生成：

- **仓库**：`https://github.com/Hmbown/CodeWhale`
- **版本**：0.9.10
- **本地路径**：`d:\spaces\SpecWeave\external\libs\ai\agents\CodeWhale\`
- **关键文件**：Cargo.toml、21 个 crate 的 Cargo.toml 和 src/、docs/ 目录下的官方文档

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
