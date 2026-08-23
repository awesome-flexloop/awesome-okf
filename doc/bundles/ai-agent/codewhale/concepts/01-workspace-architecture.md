---
type: Concept
title: "工作区架构"
description: "CodeWhale 是包含 21 个 crate 的 Rust Cargo workspace，采用从协议层到 UI 层的严格依赖方向，core crate 是运行时边界的汇聚点。"
tags: [codewhale, workspace, cargo, crate, architecture, layering]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# 工作区架构

CodeWhale 是一个 Rust Cargo workspace，将一个约 68 万行的编码 Agent 拆分为 21 个职责单一的 crate，形成从协议层到 UI 层的严格依赖方向。`core` crate 是运行时边界的汇聚点，但它本身不依赖 `tui`——终端 UI 建立在 core 之上，而非反之。

## Workspace 定义

workspace 定义在根目录 `Cargo.toml` 中，包含 21 个 crate 成员：

```toml
[workspace]
members = [
    "crates/agent",
    "crates/app-server",
    "crates/build-support",
    "crates/cli",
    "crates/command-contract",
    "crates/config",
    "crates/core",
    "crates/execpolicy",
    "crates/hooks",
    "crates/lane",
    "crates/mcp",
    "crates/paths",
    "crates/protocol",
    "crates/release",
    "crates/secrets",
    "crates/state",
    "crates/telemetry",
    "crates/tools",
    "crates/tui",
    "crates/workflow",
    "crates/workflow-js",
]
default-members = ["crates/cli"]
resolver = "2"
```

workspace 版本为 `0.9.10`，使用 Rust edition 2024，最低 rustc 版本为 1.88。默认构建成员为 `crates/cli`，resolver 设置为 `"2"`。

## 编译 Profile

workspace 使用三种编译 profile：

```toml
[profile.dev]
debug = "line-tables-only"

[profile.release]
lto = "thin"
strip = true
codegen-units = 16

[profile.dist]
inherits = "release"
lto = true
strip = true
codegen-units = 1
```

- **dev**：仅保留行号表，不生成完整 DWARF 调试信息，大幅减少增量构建的 IO 开销
- **release**：thin LTO、strip、16 个 codegen units，优化但构建快速
- **dist**：fat LTO、1 个 codegen unit，用于发布二进制

值得注意的是，`dist` profile 不设置 `panic = "abort"`，因为 TUI 的 panic supervision（`catch_unwind`/`spawn_supervised`）需要 unwinding，这样一个 panic 的工具调用或任务可以优雅失败而不是中止整个会话。

## Crate 分层架构

21 个 crate 可以按依赖方向分为以下几层：

### 第一层：基础协议与工具

这些 crate 不依赖任何内部 crate，是整个工作区的地基：

| Crate | 描述 | 关键依赖 |
|-------|------|----------|
| `codewhale-protocol` | App-server 协议帧，跨进程通信的唯一类型来源 | chrono, serde, serde_json, uuid |
| `codewhale-paths` | 用户范围的运行时路径权威 | dirs |
| `codewhale-agent` | 模型/provider 注册表和 fallback 策略 | config, serde |

`protocol` crate 包含九个模块：`agent_mail`、`agent_run`、`event_msg`、`fleet`、`ids`、`journal`、`op`、`runtime`、`workroom`。它定义了通用的 `Status` trait：

```rust
pub trait Status {
    fn is_terminal(&self) -> bool;
    fn is_active(&self) -> bool;
    fn is_paused(&self) -> bool;
}
```

这个 trait 被 thread、goal、fleet、job 等状态枚举实现，使得通用代码可以询问三个统一问题而无需匹配每个变体。

### 第二层：核心能力

| Crate | 描述 |
|-------|------|
| `codewhale-config` | 配置 schema 和优先级模型，依赖 execpolicy、paths、secrets |
| `codewhale-state` | 会话/线程持久化和恢复，使用 SQLite (rusqlite) 和 fd-lock |
| `codewhale-execpolicy` | 执行策略和审批模型，依赖 protocol 和 serde |
| `codewhale-tools` | 工具调用生命周期、schema 校验和调度并行 |
| `codewhale-mcp` | MCP 服务器生命周期和工具代理兼容性 |
| `codewhale-hooks` | Hook 分发和通知支持 |
| `codewhale-secrets` | 密钥存储后端（OS keyring + 文件回退） |
| `codewhale-workflow` | 类型化 Workflow IR 和校验 |
| `codewhale-workflow-js` | 动态 Workflow 运行时（沙箱化 QuickJS） |
| `codewhale-lane` | Lane 注册表和 Runtime 后端 |
| `codewhale-telemetry` | 匿名、用户可禁用的产品使用计数 |

### 第三层：核心运行时

`codewhale-core` 是运行时边界的汇聚点，描述为 "Core runtime boundaries for Codewhale"。它组合了八个组件：

```rust
pub struct Runtime {
    pub config: ConfigToml,
    pub model_registry: ModelRegistry,
    pub thread_manager: ThreadManager,
    pub tool_registry: Arc<ToolRegistry>,
    pub mcp_manager: Arc<McpManager>,
    pub exec_policy: ExecPolicyEngine,
    pub hooks: HookDispatcher,
    pub jobs: JobManager,
}
```

core 依赖 agent、config、execpolicy、hooks、mcp、protocol、state、tools，但**不依赖 tui**。

### 第四层：接口与传输

| Crate | 描述 |
|-------|------|
| `codewhale-app-server` | 基于 axum 和 tower-http 的应用服务器传输层 |
| `codewhale-cli` | 命令行入口，二进制名称为 `codewhale` |
| `codewhale-tui` | 终端 UI，使用 ratatui 0.30.2、crossterm 0.29、rmcp 2.2.0 |
| `codewhale-command-contract` | 原型命令能力和调度形状，依赖 core |
| `codewhale-release` | 版本发现、比较和安装逻辑 |
| `codewhale-build-support` | 共享构建脚本助手 |

## 依赖方向的关键原则

Engine 模块的注释明确写道：

> The TUI crate depends on `core`, not the reverse.

这意味着：

1. **core 不导入任何终端相关库**（ratatui、crossterm、prompt_zones 渲染），因此引擎可以在无 TUI 的情况下启动会话
2. TUI、CLI exec、app-server 和测试共享同一个 `EngineHandle`（Op-in / EventMsg-out channel API）
3. 新增核心功能应优先放入 core 或更低层 crate，避免在 tui 中添加不依赖终端的逻辑

## 进行中的架构迁移

值得注意的是，CodeWhale 正在进行一个**进行中的架构迁移**（issue #5261），将 turn loop、session、thread manager 从 tui 迁移到 core。engine/mod.rs 的注释直言：

> Only request-building and fragments have moved so far. The turn loop still lives in `crates/tui/src/core/engine/turn_loop.rs`.

这意味着 core 目前同时包含已迁移的 `Runtime`（900+ 行）和新建的 `Engine`（channel 边界证明），两者并存。`crates/core/src/engine/mod.rs` 中的 `Engine` 是未来 turn loop 迁移的目标边界，而 `crates/core/src/lib.rs` 中的 `Runtime` 是当前无头运行时的实际入口。

## 补丁与特殊配置

workspace 对 `unicode-width` 打了补丁以支持 CJK 宽度表。原版 unicode-width 0.2.2 的 `width()` 方法始终使用非 CJK 表，导致 Ratatui 在 CJK 终端中将模糊宽度字符测量为 1 列而非 2 列，造成单元格偏移渲染故障。

CLI crate 使用 mimalloc 作为全局分配器，并在 Unix 上使用 `PR_SET_PDEATHSIG`、在 Windows 上使用 Job Objects 实现父进程死亡时清理子进程。

## 相关概念

- [CodeWhale 简介](/concepts/00-introduction.md) — 项目概述与安装
- [Agent 核心运行时](/concepts/02-agent-core.md) — Runtime、Engine、Thread/Session 详解
- [MCP 协议集成](/concepts/03-mcp-protocol.md) — MCP crate 架构
- [工具系统](/concepts/04-tool-system.md) — tools crate 与 ToolRegistry
- [Fleet 多 Agent](/concepts/05-fleet-subagents.md) — Fleet 控制平面与 workflow 集成
- [技能与 Hooks](/concepts/06-skills-hooks.md) — hooks crate 与技能系统
- [沙箱与执行策略](/concepts/07-sandbox-execpolicy.md) — execpolicy crate 与安全层
