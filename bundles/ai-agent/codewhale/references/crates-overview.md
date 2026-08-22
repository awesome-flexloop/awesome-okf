---
type: reference
title: Crates 全景概览
description: CodeWhale Rust 工作区 21 个 crate 的职责、边界与依赖关系索引
tags: [codewhale, rust, crates, workspace]
sources:
  - resource: "/references/agent-core-api.md"
    title: "Agent 与 Core API 参考"
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# Crates 全景概览

CodeWhale 是一个大型 Rust 编码 Agent，源码以 Cargo workspace 组织，共 21 个 crate 成员（见 [F-001]）。本页按职责分组给出全景索引，供后续概念文档引用。

## 分组总览

| 分组 | Crate | 一句话职责 |
|---|---|---|
| 模型 | `agent` | 模型注册表（`ModelRegistry` / `ModelInfo`），解析用户模型名到具体条目 |
| 协议 | `protocol` | 可序列化 DTO：`Thread`、`ThreadRequest`、`AppRequest`、`ToolPayload`、`EventFrame`、`Op`/`EventMsg`、`ThreadId`/`SessionId` |
| 边界核心 | `core` | 无 TUI 会话边界：`Engine`/`EngineHandle`、`Thread`/`Session` 拆分、`Journal`、`MessageRequest` |
| 工具 | `tools` | `ToolRegistry`、`ToolHandler` trait、`ToolDescriptor`、`ResourceClaim`、`ToolExecutionOutcome` |
| 外部工具 | `mcp` | `McpManager`、`McpManagedClient` trait、`McpServerConfig`、`run_stdio_server` |
| 编排声明 | `workflow` | 静态 Workflow IR：gates、fleet、replay、review_repair、role_resolve |
| 编排执行 | `workflow-js` | 沙箱 QuickJS 运行时，`task()`/`parallel()`/`pipeline()` 派发子代理 |
| 执行策略 | `execpolicy` | `ExecPolicyEngine`、`AskForApproval`、`ExecPolicyDecision`、`ToolAskRule` |
| 配置 | `config` | `ConfigToml`、`ProviderKind`、`DEFAULT_SPAWN_DEPTH`、setup/用户宪法 |
| CLI | `cli` | clap 子命令分发、`ProviderArg`、`run_cli()` |
| TUI | `tui` | 终端 UI 与真正运行的 turn loop（`EngineConfig` 全量、`BASE_PROMPT`、`spawn_engine`） |
| 持久化 | `state` | `StateStore`（`JobStateRecord`、`ThreadMetadata`） |
| 支撑 | `app-server` / `build-support` / `command-contract` / `hooks` / `lane` / `paths` / `release` / `secrets` / `telemetry` | 服务端、构建、命令契约、钩子事件 sink、worktree 车道、路径、发布、密钥、遥测 |

## 核心依赖方向（据 doc comment）

- `crates/core/src/engine/mod.rs` 头部注释（见 [F-012] 上下文）明确声明：`core` 依赖 `config`、`execpolicy`、`protocol`、`state`、`tools`、`mcp`、`hooks`、`agent`；`ratatui`/`crossterm`/`prompt_zones` 渲染不进入 `core`，保持 engine「terminal-free」。同时明确「TUI crate 依赖 core，而非反向」。
- `core/src/ids.rs`（见 [F-047][F-048]）re-export `codewhale_protocol::ids::{SessionId, ThreadId}`，让依赖 `core` 的 crate 不必直接依赖 `protocol`。

## 边界迁移状态（重要）

`core`/`protocol` 是正在从巨型 `tui` crate 中「搬出边界」的产物：
- 已搬：`ThreadId`/`SessionId` 边界、`Op`-in / `EventMsg`-out 通道、`Journal` 叶子、`Thread` 独有的无头 `spawn`。
- 未搬：真实 turn loop 仍在 `crates/tui`；全量 `EngineConfig`（`allow_shell`、`trust_mode`、`mcp_config_path`、`skills_dir`，见 [F-086]）仍在 `tui/src/core/engine.rs`。

## 相关文档

- [Agent 与 Core API](/references/agent-core-api.md)
- [Tools 与 MCP API](/references/tools-mcp-api.md)
- [总览](/concepts/00-overview.md)