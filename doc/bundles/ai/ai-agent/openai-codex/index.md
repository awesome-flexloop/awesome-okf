---
type: bundle
okf_version: "0.2"
scope: openai-codex
name: openai-codex
version: "0.1.0"
source: local
description: >
  OpenAI Codex CLI 的 OKF v0.2 知识包。Codex CLI 是 OpenAI 推出的本地编码智能体，
  采用 Node.js + Rust + Python 三语言架构：Rust 工作区（130+ crate）承载全部核心
  agent 逻辑与事件驱动 TUI，Node.js 作为 npm 分发启动器，Python SDK 通过子进程
  JSON-RPC 提供程序化调用。涵盖工作区架构、Rust 核心与 TUI、沙箱执行模型、
  Skills/AGENTS.md 约定、MCP 支持等架构级主题。
---

# OpenAI Codex CLI — OKF Wiki Bundle

OpenAI Codex CLI 是一个在本地运行的编码智能体（coding agent），能够理解代码库、在沙箱中执行命令、生成和修改代码。本知识包基于源码阅读生成，聚焦架构级覆盖。

## 功能特性

- **三语言架构**：Node.js 启动器（npm 分发）+ Rust 核心（130+ crate）+ Python SDK（程序化调用）
- **事件驱动 TUI**：基于 ratatui/crossterm 的全屏终端界面，100+ 子模块，AppEvent 消息总线
- **非交互模式**：`codex exec` 支持脚本和 CI 场景
- **多层沙箱安全**：平台原生沙箱（Seatbelt/Landlock/bwrap/Windows Sandbox）+ execpolicy 规则引擎 + 用户审批
- **AGENTS.md 约定**：沿目录树自动发现项目指令文件并拼接注入上下文
- **Skills 系统**：SKILL.md 定义可复用技能，支持 `@mention` 显式调用和命令模式隐式触发
- **MCP 支持**：连接外部 Model Context Protocol 服务器扩展工具能力
- **多会话管理**：resume、fork、archive、queue 会话，支持远程 app-server 连接
- **跨平台**：macOS、Linux、Windows（含 WSL2），六平台二进制分发

## 导航

### 概念（Concepts）

| 编号 | 文档 | 说明 |
|------|------|------|
| 00 | [简介](./concepts/00-introduction.md) | 定位、三语言架构、功能特性、安装 |
| 01 | [工作区架构](./concepts/01-workspace-architecture.md) | pnpm + Cargo + Python monorepo，Bazel 构建 |
| 02 | [Rust 核心与 TUI](./concepts/02-rust-core-tui.md) | codex-core、事件驱动 TUI、线程管理、终端渲染 |
| 03 | [Node.js CLI 入口](./concepts/03-nodejs-cli.md) | bin/codex.js 启动器、平台检测、信号转发 |
| 04 | [沙箱执行模型](./concepts/04-sandbox-execution.md) | 平台沙箱、execpolicy、SafetyCheck 三层防御 |
| 05 | [Skills 与 AGENTS.md](./concepts/05-skills-agents-md.md) | 文件即上下文的约定优于配置 |
| 06 | [Python SDK](./concepts/06-python-sdk.md) | 同步/异步客户端、JSON-RPC、认证、沙箱 |

### 示例（Examples）

| 编号 | 文档 | 说明 |
|------|------|------|
| 01 | [CLI 基本使用](./examples/01-basic-usage.md) | 安装、TUI、exec、会话管理、配置、MCP |
| 02 | [Python SDK 使用](./examples/02-python-sdk.md) | pip 安装、线程管理、流式进度、错误处理 |

### 参考（References）

| 文档 | 说明 |
|------|------|
| [source.md](./references/source.md) | 源码文件索引，按组件分类，标注事实 ID |

### 规格（Spec）

| 文档 | 说明 |
|------|------|
| [facts.md](./spec/facts.md) | 82 条编号事实，每条引用文件路径和行号 |
| [insights.md](./spec/insights.md) | 5 个架构级核心洞察（陈述/证据/反常识/行动） |

## 学习路径

### 路径一：快速了解（30 分钟）

1. 阅读 [00 简介](./concepts/00-introduction.md)
2. 浏览 [CLI 基本使用](./examples/01-basic-usage.md)
3. 查看 [facts.md](./spec/facts.md) 中的事实概览

### 路径二：架构深入（2 小时）

1. [01 工作区架构](./concepts/01-workspace-architecture.md) — 理解三语言分层
2. [02 Rust 核心与 TUI](./concepts/02-rust-core-tui.md) — 深入核心实现
3. [04 沙箱执行模型](./concepts/04-sandbox-execution.md) — 理解安全模型
4. 阅读 [insights.md](./spec/insights.md) — 5 个架构洞察
5. 查阅 [source.md](./references/source.md) — 定位源码文件

### 路径三：集成开发（1 小时）

1. [03 Node.js CLI 入口](./concepts/03-nodejs-cli.md) — 理解分发机制
2. [06 Python SDK](./concepts/06-python-sdk.md) — 程序化集成
3. [Python SDK 示例](./examples/02-python-sdk.md) — 实际代码
4. [05 Skills 与 AGENTS.md](./concepts/05-skills-agents-md.md) — 扩展 agent 能力

## 目录结构

```
openai-codex/
├── index.md                    # 本文件（bundle 清单）
├── log.md                      # 变更日志
├── concepts/
│   ├── index.md
│   ├── 00-introduction.md
│   ├── 01-workspace-architecture.md
│   ├── 02-rust-core-tui.md
│   ├── 03-nodejs-cli.md
│   ├── 04-sandbox-execution.md
│   ├── 05-skills-agents-md.md
│   └── 06-python-sdk.md
├── examples/
│   ├── index.md
│   ├── 01-basic-usage.md
│   └── 02-python-sdk.md
├── references/
│   ├── index.md
│   └── source.md
└── spec/
    ├── facts.md
    └── insights.md
```

## 技术栈摘要

| 层 | 技术 |
|----|------|
| CLI 分发 | Node.js (ESM), pnpm, npm optionalDependencies |
| 核心实现 | Rust edition 2024, Cargo workspace (130+ crates) |
| TUI | ratatui 0.30, crossterm 0.29 |
| CLI 解析 | clap 4 |
| 构建系统 | Cargo (主要), Bazel (辅助/RBE), uv (Python) |
| 协议 | JSON-RPC 2.0 over stdio/WebSocket/Unix socket |
| MCP | rmcp 3.1.3 |
| Python SDK | Python 3.10+, pydantic 2.12+, uv_build |
| 沙箱 | Seatbelt (macOS), Landlock/bwrap (Linux), Windows Sandbox |
| 测试 | cargo-nextest, insta (快照), pytest, wiremock |
| 可观测性 | tracing, OpenTelemetry, RUST_LOG |

## 许可证

Apache-2.0

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
