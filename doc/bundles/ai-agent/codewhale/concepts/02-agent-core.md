---
type: Concept
title: "Agent 核心运行时"
description: "core crate 是 CodeWhale 的运行时核心，包含 Runtime 组合体、Thread/Session 分离模型、EngineHandle 通道边界、ThreadManager 和 JobManager。"
tags: [codewhale, core, runtime, engine, thread, session, job-manager]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# Agent 核心运行时

`codewhale-core` 是 CodeWhale 的运行时边界汇聚点，描述为 "Core runtime boundaries for Codewhale"。它组合了配置、模型注册、线程管理、工具注册、MCP 管理、执行策略、Hooks 和后台任务管理八大组件，是 TUI、CLI exec、app-server 和测试共享的无头运行时入口。

## Runtime 组合体

`Runtime` 结构体是顶级运行时容器，定义在 `crates/core/src/lib.rs`：

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

`Runtime::new` 接受所有依赖并从 StateStore 加载已有任务：

```rust
impl Runtime {
    pub fn new(
        config: ConfigToml,
        model_registry: ModelRegistry,
        state: StateStore,
        tool_registry: Arc<ToolRegistry>,
        mcp_manager: Arc<McpManager>,
        exec_policy: ExecPolicyEngine,
        hooks: HookDispatcher,
    ) -> Self {
        let mut jobs = JobManager::default();
        if let Err(e) = jobs.load_from_store(&state) {
            tracing::warn!("Failed to load job store, starting with empty job list: {e}");
        }
        Self {
            config,
            model_registry,
            thread_manager: ThreadManager::new(state),
            tool_registry,
            mcp_manager,
            exec_policy,
            hooks,
            jobs,
        }
    }
}
```

### 热重载

`Runtime` 支持配置和执行策略的热重载，但有明确的边界：

```rust
pub fn reload_config_and_policy(&mut self, config: ConfigToml, exec_policy: ExecPolicyEngine) {
    self.config = config;
    self.exec_policy = exec_policy;
}
```

**不会被重载**的组件包括：
- `mcp_manager` — MCP 服务器连接在启动时从 `mcp_config_path` 加载一次，更改需要重启（TUI 有单独的 `/mcp reload`）
- `tool_registry` — 启动时构建一次
- `model_registry` — 静态目录

工具调度超时在测试中为 50ms，生产环境为 300 秒：

```rust
fn tool_dispatch_timeout() -> Duration {
    if cfg!(test) {
        Duration::from_millis(50)
    } else {
        Duration::from_secs(300)
    }
}
```

## Thread / Session 分离

CodeWhale 的核心设计之一是 `Thread` 和 `Session` 的明确分离。旧代码中 `Session` 实际上是一个 thread，新的拆分定义在 `crates/core/src/session.rs`：

### Thread（持久化会话单元）

`Thread` 是持久化的、append-only 的会话单元，对应 `state.threads` 表中的一行和磁盘上的一个目录：

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Thread {
    pub thread_id: ThreadId,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub leaf_id: Option<String>,
    #[serde(default)]
    pub journal: Journal,
    pub model: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub reasoning_effort: Option<String>,
    pub workspace: PathBuf,
    #[serde(default)]
    pub ephemeral: bool,
}
```

关键字段：
- `leaf_id`：Journal 游标，标记当前活跃分支尖端。分支只移动 leaf，不重写历史
- `journal`：append-only 日志，消息以树形结构存储，root→leaf 派生投影

### Session（临时 per-turn 单元）

`Session` 是临时的、per-turn 或 per-engine-lifetime 的，拥有内存中的 `TurnContext` 和本次会话的实时审批/沙箱姿态：

```rust
#[derive(Debug, Clone)]
pub struct Session {
    pub session_id: SessionId,
    pub thread_id: ThreadId,
    pub model: String,
    pub workspace: PathBuf,
    pub messages_revision: u64,
}
```

多个 Session 可以随时间附加到同一个 Thread，但同一时刻只有一个 Session 为给定的 ThreadId 驱动 turn。`messages_revision` 是单调递增的，用于 prefix-cache memoization。

### InitialHistory

新线程的对话历史初始化有三种方式：

```rust
pub enum InitialHistory {
    New,
    Forked(Vec<Value>),
    Resumed {
        conversation_id: String,
        history: Vec<Value>,
        rollout_path: PathBuf,
    },
}
```

## Engine 与 EngineHandle

`Engine` 是 core crate 中新建的 channel 边界，代表未来 turn loop 迁移的目标。它通过 `Op`-in / `EventMsg`-out channel 通信。

### EngineHandle

`EngineHandle` 是每个消费者（TUI、CLI exec、app-server、测试）持有的邮箱：

```rust
#[derive(Clone)]
pub struct EngineHandle {
    pub tx_op: mpsc::Sender<OpEnvelope>,
    pub rx_event: Arc<tokio::sync::RwLock<mpsc::Receiver<EventMsg>>>,
    cancel_token: Arc<StdMutex<tokio_util::sync::CancellationToken>>,
}

impl EngineHandle {
    pub async fn send(&self, op: OpEnvelope) -> anyhow::Result<()> { ... }
    pub fn cancel(&self) { ... }
    pub fn cancel_with_reason(&self, _reason: CancelReason) { ... }
    pub async fn steer(
        &self,
        thread_id: ThreadId,
        content: impl Into<String>,
    ) -> anyhow::Result<()> { ... }
}
```

`steer` 方法构造一个 `Op::Steer` 信封发送到引擎，允许在 turn 进行中注入用户内容。

### EngineConfig

引擎配置包含启动无头会话所需的最小字段：

```rust
#[derive(Debug, Clone)]
pub struct EngineConfig {
    pub workspace: PathBuf,
    pub model: String,
    pub model_provider: String,
    pub thread_id: ThreadId,
    pub session_id: SessionId,
    pub max_steps: u32,
}

impl Default for EngineConfig {
    fn default() -> Self {
        Self {
            workspace: PathBuf::from("."),
            model: "deepseek-v4-flash".to_string(),
            model_provider: "deepseek".to_string(),
            thread_id: ThreadId::new(),
            session_id: SessionId::new(),
            max_steps: 32,
        }
    }
}
```

默认模型为 `deepseek-v4-flash`，provider 为 `deepseek`，最大步数为 32。

### spawn_engine

`spawn_engine` 在后台 tokio task 中运行 Engine，返回 EngineHandle：

```rust
pub fn spawn_engine(config: EngineConfig, state: StateStore) -> EngineHandle {
    let (engine, handle) = Engine::new(config, state);
    let handle_clone = handle.clone();
    tokio::spawn(async move {
        engine.run().await;
    });
    handle_clone
}
```

Engine 的 `run` 循环从 `rx_op` 接收 `OpEnvelope`，处理 `Op::SendMessage`、`Op::Steer`、`Op::Shutdown`、`Op::Cancel` 等操作，并通过 `tx_event` 发送 `EventMsg`（如 `TurnStarted`、`TurnComplete`）。

## ThreadManager

`ThreadManager` 管理线程的完整生命周期，底层使用 `StateStore` 持久化。它支持：

- **spawn**：创建新线程，支持 `InitialHistory::New`、`Forked`、`Resumed`
- **resume**：恢复已持久化的线程
- **fork**：从现有线程分叉，复制历史但创建新的 thread_id
- **archive**：归档线程
- **goal 生命周期**：设置、获取、更新、清除线程目标

ThreadManager 构造时接受 `StateStore`：

```rust
pub struct ThreadManager {
    state: StateStore,
    // ...
}

impl ThreadManager {
    pub fn new(state: StateStore) -> Self { ... }
    pub fn state_store(&self) -> &StateStore { ... }
}
```

## JobManager

`JobManager` 管理后台任务的重试和历史记录。关键常量：

```rust
const DEFAULT_JOB_MAX_ATTEMPTS: u32 = 3;
const DEFAULT_JOB_BACKOFF_BASE_MS: u64 = 500;
const MAX_JOB_HISTORY_ENTRIES: usize = 64;
```

重试元数据：

```rust
pub struct JobRetryMetadata {
    pub attempt: u32,
    pub max_attempts: u32,
    pub backoff_base_ms: u64,
    pub next_backoff_ms: u64,
    pub next_retry_at: Option<i64>,
}
```

任务状态枚举实现了 protocol crate 的 `Status` trait：

```rust
pub enum JobStatus {
    Queued,
    Running,
    Paused,
    Completed,
    Failed,
    Cancelled,
}

impl Status for JobStatus {
    fn is_terminal(&self) -> bool {
        matches!(self, Self::Completed | Self::Failed | Self::Cancelled)
    }
    fn is_active(&self) -> bool {
        matches!(self, Self::Queued | Self::Running)
    }
    fn is_paused(&self) -> bool {
        matches!(self, Self::Paused)
    }
}
```

JobManager 支持从 StateStore 加载已有任务，记录任务历史（最多 64 条），并实现指数退避重试。

## 架构迁移说明

需要强调的是，core crate 正在进行从 tui 迁移 turn loop 的过程（issue #5261）。当前：

- `crates/core/src/lib.rs` 的 `Runtime` 是当前无头运行时的实际入口
- `crates/core/src/engine/mod.rs` 的 `Engine` 是未来 turn loop 迁移的目标边界
- 完整的 turn loop（stream、tool exec、guards、compaction）目前仍在 `crates/tui/src/core/engine/turn_loop.rs`
- Engine 模块注释明确说明这是"the boundary that move lands against, not the current owner of turn execution"

这种并存状态意味着阅读源码时需要注意区分当前运行路径和未来目标边界。

## 相关概念

- [工作区架构](/concepts/01-workspace-architecture.md) — core crate 在 21 crate 分层中的位置
- [MCP 协议集成](/concepts/03-mcp-protocol.md) — Runtime 中的 mcp_manager 组件
- [工具系统](/concepts/04-tool-system.md) — Runtime 中的 tool_registry 组件
- [沙箱与执行策略](/concepts/07-sandbox-execpolicy.md) — Runtime 中的 exec_policy 组件
- [技能与 Hooks](/concepts/06-skills-hooks.md) — Runtime 中的 hooks 组件
- [Fleet 多 Agent](/concepts/05-fleet-subagents.md) — 多 worker 编排与子 agent
