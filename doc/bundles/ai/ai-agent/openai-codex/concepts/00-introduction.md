---
type: Concept
title: OpenAI Codex CLI 简介
description: >
  OpenAI Codex CLI 是一个在本地运行的编码智能体，采用 Node.js + Rust + Python
  三语言架构。本文介绍其定位、核心功能、安装方式与基本使用。
tags: [openai-codex, introduction, cli, coding-agent]
generated:
  by: "reference_agent/trae-cn"
  at: 2026-08-23T10:00:00+08:00
verified:
  by: "process:grep-verification"
  at: 2026-08-23T10:00:00+08:00
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# OpenAI Codex CLI 简介

OpenAI Codex CLI 是 OpenAI 推出的本地编码智能体（coding agent），在用户的计算机上运行，能够理解代码库、执行命令、生成和修改代码。它是一个终端工具，同时提供交互式 TUI（文本用户界面）和非交互式执行模式。

## 定位

Codex CLI 在本地运行，与云端的 Codex Web（chatgpt.com/codex）和 IDE 扩展（VS Code、Cursor、Windsurf）并列，是 OpenAI Codex 生态的命令行入口。它支持：

- 使用 ChatGPT 账户（Plus/Pro/Business/Edu/Enterprise）登录
- 使用 OpenAI API Key
- 本地沙箱执行命令
- 读取和修改项目文件
- MCP（Model Context Protocol）工具集成

## 三语言架构

Codex CLI 的代码库由三部分组成，形成"壳—核—接口"的分层：

| 部分 | 语言 | 职责 |
|------|------|------|
| `codex-cli/` | Node.js (ESM) | npm 分发启动器，平台检测与信号转发 |
| `codex-rs/` | Rust (edition 2024) | 全部核心逻辑：TUI、agent、沙箱、MCP、配置 |
| `sdk/python/` | Python (>=3.10) | 程序化调用 SDK，通过子进程 JSON-RPC 驱动 Rust 二进制 |

Node.js 和 Python 层都是薄适配层，不含 agent 业务逻辑。Rust 二进制是唯一的功能实现。

## 核心功能

- **交互式 TUI**：默认启动 `codex` 进入全屏终端界面，支持对话、命令审批、diff 查看
- **非交互执行**：`codex exec "prompt"` 在脚本和 CI 中运行
- **沙箱安全**：平台原生沙箱（macOS Seatbelt、Linux Landlock/bwrap、Windows Sandbox）
- **执行策略**：execpolicy 声明式规则引擎控制命令白名单/黑名单
- **AGENTS.md**：沿目录树自动发现项目指令文件
- **Skills 系统**：通过 `SKILL.md` 文件扩展能力，支持显式 `@mention` 和隐式触发
- **MCP 集成**：连接外部 MCP 服务器扩展工具
- **多会话管理**：resume、fork、archive、queue 会话
- **远程模式**：TUI 可连接远程 app-server（`--remote ws://host:port`）

## 安装

### macOS / Linux

```shell
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

### Windows

```shell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

### npm

```shell
npm install -g @openai/codex
```

### Homebrew

```shell
brew install --cask codex
```

安装后运行 `codex` 即可启动。首次使用需登录 ChatGPT 账户或配置 API Key。

## 从源码构建

```bash
git clone https://github.com/openai/codex.git
cd codex/codex-rs
cargo build
cargo run --bin codex -- "explain this codebase to me"
```

构建需要 Rust 工具链、`just`、`cargo-nextest` 等工具。项目同时支持 Bazel 构建系统。

## 相关概念

- [工作区架构](01-workspace-architecture.md)
- [Rust 核心与 TUI](02-rust-core-tui.md)
- [Node.js CLI 入口](03-nodejs-cli.md)
- [沙箱执行模型](04-sandbox-execution.md)
- [Skills 与 AGENTS.md](05-skills-agents-md.md)
- [Python SDK](06-python-sdk.md)
