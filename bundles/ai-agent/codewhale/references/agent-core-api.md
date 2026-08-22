---
type: reference
title: Agent 与 Core API 参考
description: CodeWhale 模型注册表、核心引擎、会话/线程、协议通道的关键类型与签名
tags: [codewhale, rust, agent, core, protocol]
sources:
  - resource: "/references/crates-overview.md"
    title: "Crates 全景概览"
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# Agent 与 Core API 参考

本页登记 `agent`、`core`、`protocol` 三个 crate 的关键类型签名，均与其源码逐字一致。

## 模型注册表（crates/agent）

```rust
pub enum ModelFamily { DeepSeek, Anthropic, OpenAI, Google, Meta, Mistral, Qwen, Grok, Cohere, GptOss, Inferencer }

pub struct ModelInfo {
    pub id: String,
    pub provider: ProviderKind,
    pub aliases: Vec<String>,
    pub supports_tools: bool,
    pub supports_reasoning: bool,
}

pub struct ModelResolution {
    pub requested: Option<String>,
    pub resolved: ModelInfo,
    pub used_fallback: bool,
    pub fallback_chain: Vec<String>,
}

pub struct ModelRegistry {
    models: Vec<ModelInfo>,
    alias_map: HashMap<String, usize>,
}
```

`ModelRegistry::default()` 预置模型条目含 `"deepseek-v4-pro"`、`"deepseek-v4-flash"`（aliases 含 `deepseek-chat`/`deepseek-reasoner`/`deepseek-r1`）、`"gpt-5.3-codex"` 等（见 [F-006]）。

## 核心引擎（crates/core）

```rust
// crates/core/src/engine/mod.rs
pub enum CancelReason { User, External, Preempted, Internal }

pub struct EngineHandle {
    pub tx_op: mpsc::Sender<OpEnvelope>,
    pub rx_event: Arc<tokio::sync::RwLock<mpsc::Receiver<EventMsg>>>,
    cancel_token: Arc<StdMutex<tokio_util::sync::CancellationToken>>,
}

impl EngineHandle {
    pub async fn send(&self, op: OpEnvelope) -> anyhow::Result<()>;
    pub fn cancel(&self);
    pub fn cancel_with_reason(&self, reason: CancelReason);
    pub async fn steer(&self, thread_id: ThreadId, content: impl Into<String>) -> anyhow::Result<()>;
}

pub struct EngineConfig {
    pub workspace: PathBuf,
    pub model: String,
    pub model_provider: String,
    pub thread_id: ThreadId,
    pub session_id: SessionId,
    pub max_steps: u32,
}

pub fn spawn_engine(config: EngineConfig, state: StateStore) -> EngineHandle;
pub fn spawn_headless_thread(
    workspace: PathBuf,
    model: impl Into<String>,
    state: StateStore,
) -> (EngineHandle, ThreadId, SessionId);
```

## 线程与会话（crates/core）

```rust
// crates/core/src/session.rs
pub struct Thread {
    pub thread_id: ThreadId,
    pub leaf_id: Option<String>,
    pub journal: Journal,
    pub model: String,
    pub reasoning_effort: Option<String>,
    pub workspace: PathBuf,
    pub ephemeral: bool,
}

pub struct Session {
    pub session_id: SessionId,
    pub thread_id: ThreadId,
    pub model: String,
    pub workspace: PathBuf,
    pub messages_revision: u64,
}

pub fn session_for_thread(thread: &Thread, workspace: PathBuf) -> Session;
```

`Thread` 是持久化实体（一条 `state.threads` 行 + 一个磁盘目录），拥有 append-only `Journal` 与 `leaf_id` 游标；`Session` 是一次 engine 生命周期内的临时姿态。

## 协议通道（crates/protocol）

```rust
// crates/protocol/src/op.rs
pub struct OpEnvelope {
    pub op_id: String,
    pub thread_id: ThreadId,
    pub session_id: SessionId,
    pub op: Op,
}

pub enum Op {  // #[serde(tag = "kind", rename_all = "snake_case")]
    SendMessage { content, mode, model, model_provider, allowed_tools, dynamic_tools, provenance },
    Steer { content },
    ContinueGoal,
    RunShellCommand { command },
    SetGoalStatus { status, clear },
    Cancel,
    Shutdown,
    PreviewOutboundRequest { json, base_prompt_only },
}
```

```rust
// crates/protocol/src/event_msg.rs
pub enum EventMsg {  // #[serde(tag = "event")]
    TurnStarted { thread_id, session_id, turn_id },
    ResponseDelta { thread_id, session_id, delta, channel },
    ToolCallStarted { thread_id, session_id, tool_call_id, tool_name, input },
    ToolCallComplete { thread_id, session_id, tool_call_id, tool_name, result },
    TurnComplete { thread_id, session_id, turn_id, status, error },
    TurnUsage { thread_id, session_id, input_tokens, output_tokens },
    CompactionStarted { thread_id, session_id, message },
    CompactionCompleted { thread_id, session_id, message },
    Error { thread_id, session_id, message },
}
```

ID 类型（`crates/protocol/src/ids.rs`）为透明 newtype：

```rust
pub struct ThreadId(pub String);   // new -> "thread-{uuid}"
pub struct SessionId(pub String);
```

## 相关文档

- [Crates 全景概览](/references/crates-overview.md)
- [Agent 主循环](/concepts/01-agent-loop.md)