---
type: Concept
title: "CodeWhale 简介"
description: "CodeWhale 是一个用 Rust 编写的开源终端编码 Agent，支持多模型 Provider、MCP 协议、Fleet 多 Agent 编排与 Workflow 工作流引擎。"
tags: [codewhale, introduction, rust, coding-agent, installation]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# CodeWhale 简介

CodeWhale 是一个使用 Rust 编写的开源终端编码 Agent（coding agent），专为开源和开放权重模型设计。它起源于 `deepseek-tui` 项目，至今仍保留配置和会话兼容性，但已发展为一个支持多 Provider、多模型、MCP 协议集成、Fleet 多 Agent 编排以及声明式/命令式双轨 Workflow 引擎的完整开发平台。

## 项目定位

CodeWhale 的核心定位是**本地优先的终端编码助手**。它不是一个简单的聊天客户端，而是一个具备完整工具调用、沙箱执行、权限策略、持久化会话和多 Agent 编排能力的运行时。TUI（终端用户界面）建立在 core 运行时之上，而不是反过来——这意味着同一套核心逻辑可以被 TUI、headless CLI（`codewhale exec`）、app-server 和测试共享。

项目仓库地址为 `https://github.com/Hmbown/CodeWhale`，使用 MIT 许可证。当前 workspace 版本为 `0.9.10`，采用 Rust edition 2024，最低支持 rustc 1.88。

## 核心功能特性

### 多模型与多 Provider

CodeWhale 内置了 11 个模型家族的支持，覆盖 DeepSeek、Anthropic、OpenAI、Google、Meta、Mistral、Qwen、Grok、Cohere、GptOss 和 Inferencer。`ModelFamily` 枚举定义了这些家族：

```rust
pub enum ModelFamily {
    DeepSeek,
    Anthropic,
    OpenAI,
    Google,
    Meta,
    Mistral,
    Qwen,
    Grok,
    Cohere,
    GptOss,
    Inferencer,
}
```

ProviderKind 支持 42 个条目，包括 deepseek、openai、anthropic、google、ollama、openrouter、moonshot、zai、xai 等。默认 provider 是 DeepSeek，默认模型为 `deepseek-v4-flash`。

每个模型通过 `ModelInfo` 描述其能力：

```rust
pub struct ModelInfo {
    pub id: String,
    pub provider: ProviderKind,
    pub aliases: Vec<String>,
    pub supports_tools: bool,
    pub supports_reasoning: bool,
}
```

### 三种运行模式

TUI 提供三种模式，通过 Tab 键循环切换：

- **Plan（计划模式）**：只读，拒绝文件修改和 shell 执行
- **Work（工作模式）**：普通多步执行
- **Operate（操作模式）**：多任务调度姿态

权限姿态通过 Shift+Tab 循环：Ask → Auto-Review → Full Access。推理力度通过 Ctrl+T 循环。

### MCP 协议集成

CodeWhale 实现了完整的 MCP（Model Context Protocol）客户端和服务端。它可以连接外部 MCP 服务器获取工具，也可以自身作为 MCP stdio 服务器运行（`codewhale-tui serve --mcp` 或 `codewhale mcp-server`）。MCP 工具通过限定名 `mcp__<server>__<tool>` 寻址，并具备名称折叠安全、调用时过滤和防重放等安全特性。

### Fleet 多 Agent 编排

Fleet 是一个本地优先的持久化多 worker 控制平面。每个 fleet worker 是一个无头的 `codewhale exec` 进程，支持重试、重启存活和账本审计追踪。核心安全原则是"委派转移工作，永不转移权威"——子 agent 的权限被 clamp 到父级实时姿态。

### Workflow 工作流引擎

Workflow 系统采用双轨架构：
- **声明式 IR**（`codewhale-workflow`）：类型化的 TOML 定义，8 种节点类型，支持预算/权限/模型策略和教师评审循环
- **命令式 JS**（`codewhale-workflow-js`）：基于 QuickJS 的沙箱化 JS 运行时，支持 `task()`、`parallel()`、`pipeline()` 等全局函数

### 安全与沙箱

CodeWhale 提供多层安全机制：
- 三层优先级规则集（BuiltinDefault → Agent → User）
- macOS Seatbelt（sandbox-exec）和 Linux Bubblewrap（bwrap）OS 级沙箱
- Shell 词法展开检测，防止命令替换、子 shell、wrapper 等绕过方式
- 链式命令不会被 trusted prefix 自动批准

### 技能与插件系统

Skills 是可复用的 `SKILL.md` 指令包，采用四层架构（根目录 → 审计 → 变更控制器 → 管理器视图）。插件支持本地目录、GitHub archive 和直接 tarball URL 三种安装源，安装后需要 hash-bound trust 再 enable。

### 持久化与状态

会话状态通过 SQLite 数据库和 append-only JSONL 会话索引文件持久化。`StateStore` 管理 threads、messages（树形分支）、checkpoints、jobs 和 dynamic tools 五类数据。

## 安装方式

CodeWhale 提供多种安装渠道：

### npm 安装

```bash
npm install -g codewhale
```

npm 包名为 `codewhale`。

### crates.io 安装

```bash
cargo install codewhale-cli
```

crates.io 包名为 `codewhale-cli`。

### Docker

```bash
docker run -it ghcr.io/hmbown/codewhale
```

Docker 镜像发布在 `ghcr.io/hmbown/codewhale`，容器以非 root 用户 `codewhale`（UID/GID 1000:1000）运行。

### 从源码构建

```bash
git clone https://github.com/Hmbown/CodeWhale.git
cd CodeWhale
cargo build --release
```

项目使用 mimalloc 作为全局分配器，并在 Unix 上使用 PR_SET_PDEATHSIG、在 Windows 上使用 Job Objects 实现父进程死亡时清理子进程。

## 配置文件

配置文件存储在 `~/.codewhale/config.toml`，旧版 `~/.deepseek/config.toml` 仍受支持。运行 `codewhale doctor` 可以进行离线健康检查，添加 `--json` 标志可输出机器可读报告。

## 国际化

TUI 支持 16 种语言区域，包括简体中文（zh-Hans）、繁体中文（zh-Hant）、日语、韩语等。

## 相关概念

- [工作区架构](01-workspace-architecture.md) — 21 个 crate 的 Cargo workspace 分层设计
- [Agent 核心运行时](02-agent-core.md) — Runtime、Engine、Thread/Session 和 JobManager
- [MCP 协议集成](03-mcp-protocol.md) — MCP 服务器生命周期与工具代理
- [工具系统](04-tool-system.md) — ToolRegistry 与 ToolHandler trait
- [Fleet 多 Agent](05-fleet-subagents.md) — 持久化多 worker 控制平面
- [技能与 Hooks](06-skills-hooks.md) — Skills 四层架构与 Hook 生命周期
- [沙箱与执行策略](07-sandbox-execpolicy.md) — ExecPolicyEngine 与 OS 沙箱
