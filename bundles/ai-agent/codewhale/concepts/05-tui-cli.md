---
type: concept
title: TUI 与 CLI（TUI & CLI）
description: CodeWhale 的交互式终端 UI、三类模式与权限姿态、Hooks 触发边界，以及单二进制 CLI 的 provider 派发
tags: [codewhale, tui, cli, modes, hooks]
sources:
  - resource: "/references/crates-overview.md"
    title: "Crates 全景概览"
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# TUI 与 CLI

CodeWhale 的界面层横跨 `crates/tui`（真正的 turn loop 所在地）与 `crates/cli`（clap 子命令派发）。两者又共享同一套 `EngineHandle` 通道。

## TUI 模式与按键

`docs/MODES.md` 定义了三种可见交互模式（见 [F-087]）：

- `Tab`：循环切换 `Plan → Work → Operate`；
- `Shift+Tab`：循环切换权限姿态 `Ask → Auto-Review → Full Access`；
- `Ctrl+T`：循环推理强度；
- `/mode plan|work|operate`：直接切换（`Act` 是 `Work` 的兼容别名，存值归一化为 `agent`）。

三种模式的工具可用性（见 [F-088]）：`read` 与策略允许的延迟研究工具在三种模式下都可用；`write`/`edit`/`bash` 在 `Plan` 下「名称可见、执行拒绝」，在 `Work`/`Operate` 下受审批、沙箱、仓库法（repository law）与托管策略共同裁决。

## 提示词与本地化

`BASE_PROMPT` 是唯一的 base prompt，定义于 `crates/tui/src/prompts/text.rs`（见 [F-085]）。TUI 通过 `rust_i18n::i18n!("locales", fallback = ["en"])` 做本地化，`locales/` 下含 zh-Hans、ja、de 等十余种语言（见 [F-084]）。

## Hooks 的触发边界

Hooks 是 **TUI 运行时特性**（见 [F-095]）：它会在生命周期点运行一条 shell 命令，通过环境变量/JSON on stdin 传上下文。但 `codewhale exec`（无头）、CLI 派发器、app-server/ACP 都**不**触发 hooks。`crates/hooks` 这个 crate 是无关的内部事件 sink，与这里描述的 TUI hooks 无共享配置。

## CLI 与单二进制

`cli/src/main.rs` 用 `mimalloc::MiMalloc` 做全局分配器，入口是 `codewhale_cli::run_cli()`（见 [F-079]）。`ProviderArg` 枚举（`clap::ValueEnum`）列出数十个 provider：`Deepseek`、`NvidiaNim`、`Openai`、`Anthropic`、`Google`、`Xai`、`Mistral`、`Ollama` 等（见 [F-080]）。

## 本地 Web 前端

`codewhale web` 启动内嵌的浏览器客户端，默认 `http://127.0.0.1:7878`，服务器始终绑定 `127.0.0.1` 且不可禁用认证（见 [F-096]）。它是同一本地 Runtime 的另一个视图，不创建云端账号、不把凭证复制进浏览器存储。

## 相关概念

- [总览](/concepts/00-overview.md)
- [Agent 主循环](/concepts/01-agent-loop.md)
- [Workflow 与 Fleet](/concepts/04-workflow-fleet.md)
- [Crates 全景概览](/references/crates-overview.md)