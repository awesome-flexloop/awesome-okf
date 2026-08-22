# CodeWhale 事实清单

> 本清单由源码逐字采集，每一条均指向 `external/libs/ai/agents/CodeWhale` 下的具体文件与行号。仅记录「代码里有什么」，不含任何因果、意图或设计推断。

## 项目结构与 Cargo 工作区

F-001: 文件 `Cargo.toml` 第2-23行，`[workspace] members` 列表包含 21 个 crate 成员：`crates/agent`、`crates/app-server`、`crates/build-support`、`crates/cli`、`crates/command-contract`、`crates/config`、`crates/core`、`crates/execpolicy`、`crates/hooks`、`crates/lane`、`crates/mcp`、`crates/paths`、`crates/protocol`、`crates/release`、`crates/secrets`、`crates/state`、`crates/telemetry`、`crates/tools`、`crates/tui`、`crates/workflow`、`crates/workflow-js`。

## crates/agent（模型注册表）

F-002: 文件 `crates/agent/src/lib.rs` 第7-20行，枚举 `pub enum ModelFamily`，变体为 `DeepSeek`、`Anthropic`、`OpenAI`、`Google`、`Meta`、`Mistral`、`Qwen`、`Grok`、`Cohere`、`GptOss`、`Inferencer`。

F-003: 文件 `crates/agent/src/lib.rs` 第27-39行，结构体 `pub struct ModelInfo`，字段为 `id: String`、`provider: ProviderKind`、`aliases: Vec<String>`、`supports_tools: bool`、`supports_reasoning: bool`。

F-004: 文件 `crates/agent/src/lib.rs` 第45-55行，结构体 `pub struct ModelResolution`，字段为 `requested: Option<String>`、`resolved: ModelInfo`、`used_fallback: bool`、`fallback_chain: Vec<String>`。

F-005: 文件 `crates/agent/src/lib.rs` 第62-66行，结构体 `pub struct ModelRegistry`，字段为 `models: Vec<ModelInfo>`、`alias_map: HashMap<String, usize>`。

F-006: 文件 `crates/agent/src/lib.rs` 第69-150行，`impl Default for ModelRegistry` 预置的 `ModelInfo` 条目含 `id: "deepseek-v4-pro"`（provider `ProviderKind::Deepseek`）、`id: "deepseek-v4-flash"`（aliases 含 `"deepseek-chat"`、`"deepseek-reasoner"`、`"deepseek-r1"`、`"deepseek-v3"`）、`id: "gpt-5.3-codex"`、`id: "gpt-5.5"`、`id: "gpt-5.5-pro"`。

## crates/core（边界类型）

F-007: 文件 `crates/core/src/lib.rs` 第1-7行，模块声明为 `pub mod engine; pub mod fragments; pub mod ids; pub mod journal; pub mod request; pub mod session; pub mod tool_parser;`。

F-008: 文件 `crates/core/src/lib.rs` 第54-66行，枚举 `pub enum InitialHistory`，变体为 `New`、`Forked(Vec<Value>)`、`Resumed { conversation_id: String, history: Vec<Value>, rollout_path: PathBuf }`。

F-009: 文件 `crates/core/src/lib.rs` 第69-83行，结构体 `pub struct NewThread`，字段为 `thread: Thread`、`model: String`、`model_provider: String`、`cwd: PathBuf`、`approval_policy: Option<String>`、`sandbox: Option<String>`。

F-010: 文件 `crates/core/src/lib.rs` 第86-100行，枚举 `pub enum JobStatus`，变体为 `Queued`、`Running`、`Paused`、`Completed`、`Failed`、`Cancelled`；第102-112行为 `impl Status for JobStatus`。

F-011: 文件 `crates/core/src/lib.rs` 第114-117行，常量 `JOB_DETAIL_SCHEMA_VERSION: u8 = 1`、`DEFAULT_JOB_MAX_ATTEMPTS: u32 = 3`、`DEFAULT_JOB_BACKOFF_BASE_MS: u64 = 500`、`MAX_JOB_HISTORY_ENTRIES: usize = 64`。

F-012: 文件 `crates/core/src/lib.rs` 第120-132行，结构体 `pub struct JobRetryMetadata`，字段为 `attempt: u32`、`max_attempts: u32`、`backoff_base_ms: u64`、`next_backoff_ms: u64`、`next_retry_at: Option<i64>`。

## crates/core/engine（核心引擎句柄与无头(spawn)入口）

F-013: 文件 `crates/core/src/engine/mod.rs` 第49-55行，枚举 `pub enum CancelReason`，变体为 `User`、`External`、`Preempted`、`Internal`。

F-014: 文件 `crates/core/src/engine/mod.rs` 第62-67行，结构体 `pub struct EngineHandle`，字段为 `tx_op: mpsc::Sender<OpEnvelope>`、`rx_event: Arc<RwLock<mpsc::Receiver<EventMsg>>>`、`cancel_token`。

F-015: 文件 `crates/core/src/engine/mod.rs` 第88-106行，方法 `pub async fn steer(&self, thread_id: ThreadId, content: impl Into<String>) -> anyhow::Result<()>`，构造 `OpEnvelope`（`op: Op::Steer`）并发送。

F-016: 文件 `crates/core/src/engine/mod.rs` 第116-124行，结构体 `pub struct EngineConfig`，字段为 `workspace: PathBuf`、`model: String`、`model_provider: String`、`thread_id: ThreadId`、`session_id: SessionId`、`max_steps: u32`。

F-017: 文件 `crates/core/src/engine/mod.rs` 第151-152行，常量 `ENGINE_OP_CHANNEL_CAPACITY: usize = 32`、`ENGINE_EVENT_CHANNEL_CAPACITY: usize = 128`。

F-018: 文件 `crates/core/src/engine/mod.rs` 第189-226行，方法 `pub async fn run(mut self)`，循环接收 `OpEnvelope`，对 `Op::SendMessage` 执行 `self.journal.append("user", …)` 并发送 `EventMsg::TurnComplete`，对 `Op::Shutdown | Op::Cancel` 执行 `break`。

F-019: 文件 `crates/core/src/engine/mod.rs` 第233-240行，函数 `pub fn spawn_engine(config: EngineConfig, state: StateStore) -> EngineHandle`，通过 `tokio::spawn` 后台运行 `engine.run()`。

F-020: 文件 `crates/core/src/engine/mod.rs` 第257-274行，函数 `pub fn spawn_headless_thread(workspace: PathBuf, model: impl Into<String>, state: StateStore) -> (EngineHandle, ThreadId, SessionId)`。

## crates/core（session / journal / request / tool_parser）

F-021: 文件 `crates/core/src/session.rs` 第29-45行，结构体 `pub struct Thread`，字段为 `thread_id: ThreadId`、`leaf_id: Option<String>`、`journal: Journal`、`model: String`、`reasoning_effort: Option<String>`、`workspace: PathBuf`、`ephemeral: bool`。

F-022: 文件 `crates/core/src/session.rs` 第75-85行，结构体 `pub struct Session`，字段为 `session_id: SessionId`、`thread_id: ThreadId`、`model: String`、`workspace: PathBuf`、`messages_revision: u64`。

F-023: 文件 `crates/core/src/session.rs` 第108-110行，函数 `pub fn session_for_thread(thread: &Thread, workspace: PathBuf) -> Session`。

F-024: 文件 `crates/core/src/journal.rs` 第24-28行，结构体 `pub struct ThreadLeafState`，字段为 `thread_id: String`、`leaf_id: Option<String>`。

F-025: 文件 `crates/core/src/journal.rs` 第31-39行，枚举 `pub enum JournalKind`，变体为 `Header`、`User`、`Assistant`、`ToolResult`、`Compaction`、`BranchSummary`。

F-026: 文件 `crates/core/src/request.rs` 第12-37行，结构体 `pub struct MessageRequest`，字段含 `model: String`、`messages: Vec<Message>`、`max_tokens: u32`、`system: Option<SystemPrompt>`、`tools: Option<Vec<Tool>>`、`tool_choice: Option<Value>`、`reasoning_effort: Option<String>`、`stream: Option<bool>`、`temperature: Option<f32>`、`top_p: Option<f32>`。

F-027: 文件 `crates/core/src/request.rs` 第62-77行，函数 `pub fn prepare_primary_turn_request(input: PrimaryTurnRequest) -> MessageRequest`，返回体固定 `stream: Some(true)`、`metadata: None`、`thinking: None`、`temperature: None`、`top_p: None`。

F-028: 文件 `crates/core/src/request.rs` 第80-85行，枚举 `pub enum SystemPrompt`（`#[serde(untagged)]`），变体为 `Text(String)`、`Blocks(Vec<SystemBlock>)`。

F-029: 文件 `crates/core/src/request.rs` 第104-108行，结构体 `pub struct Message`，字段为 `role: String`、`content: Vec<ContentBlock>`。

F-030: 文件 `crates/core/src/tool_parser.rs` 第29-37行，结构体 `pub struct ParsedToolCall`，字段为 `name: String`、`args: Value`、`id: String`；第40-46行，结构体 `pub struct ParseResult`，字段为 `clean_text: String`、`tool_calls: Vec<ParsedToolCall>`。

F-031: 文件 `crates/core/src/tool_parser.rs` 第54-75行，常量 `FAKE_TOOL_CALL_MARKERS: &[&str]`，含 `<function_calls>`、`<｜DSML｜tool_calls>`、`<｜DSML｜invoke `、`<|DSML|tool_calls>`、`<|DSML|invoke `、`<|dsml|tool_calls>`、`<|dsml|invoke `、`<|tool_calls>`、`<｜tool▁calls▁begin｜>`、`<｜tool▁call▁begin｜>`、`<|tool▁calls▁begin|>`、`<|tool▁call▁begin|>`、`<｜tool_calls_begin｜>`、`<｜tool_call_begin｜>`、`<|tool_calls_begin|>`、`<|tool_call_begin|>` 共 16 项。

## crates/protocol（协议 DTO）

F-032: 文件 `crates/protocol/src/lib.rs` 第6-14行，模块声明为 `agent_mail`、`agent_run`、`event_msg`、`fleet`、`ids`、`journal`、`op`、`runtime`、`workroom`。

F-033: 文件 `crates/protocol/src/lib.rs` 第21-33行，trait `pub trait Status`，方法为 `fn is_terminal(&self) -> bool`、`fn is_active(&self) -> bool`、`fn is_paused(&self) -> bool`。

F-034: 文件 `crates/protocol/src/lib.rs` 第43-52行，枚举 `pub enum ThreadStatus`（`rename_all = "snake_case"`），变体为 `Running`、`Idle`、`Completed`、`Failed`、`Paused`、`Archived`。

F-035: 文件 `crates/protocol/src/lib.rs` 第76-92行，结构体 `pub struct Thread`，字段为 `id: String`、`preview: String`、`ephemeral: bool`、`model_provider: String`、`created_at: i64`、`updated_at: i64`、`status: ThreadStatus`、`path: Option<PathBuf>`、`cwd: PathBuf`、`cli_version: String`、`source: SessionSource`、`name: Option<String>`。

F-036: 文件 `crates/protocol/src/lib.rs` 第246-273行，枚举 `pub enum ThreadRequest`（`tag = "kind"`），变体为 `Create`、`Start(ThreadStartParams)`、`Resume(ThreadResumeParams)`、`Fork(ThreadForkParams)`、`List(ThreadListParams)`、`Read(ThreadReadParams)`、`SetName(ThreadSetNameParams)`、`GoalSet(ThreadGoalSetParams)`、`GoalGet(ThreadGoalGetParams)`、`GoalClear(ThreadGoalClearParams)`、`GoalRecordProgress(ThreadGoalProgressParams)`、`Archive`、`Unarchive`、`Message`。

F-037: 文件 `crates/protocol/src/lib.rs` 第315-353行，枚举 `pub enum AppRequest`（`tag = "kind"`），变体为 `Capabilities`、`ConfigGet`、`ConfigSet`、`ConfigUnset`、`ConfigList`、`ConfigReload`、`Models`、`ThreadLoadedList`、`SubmitUserInput`。

F-038: 文件 `crates/protocol/src/lib.rs` 第393-410行，枚举 `pub enum AskForApproval`（`rename_all = "snake_case"`），变体为 `UnlessTrusted`、`OnFailure`、`OnRequest`、`Reject { sandbox_approval: bool, rules: bool, mcp_elicitations: bool }`、`Never`。

F-039: 文件 `crates/protocol/src/lib.rs` 第413-420行，枚举 `pub enum ToolKind`，变体为 `Function`、`Mcp`。

F-040: 文件 `crates/protocol/src/lib.rs` 第436-453行，枚举 `pub enum ToolPayload`（`tag = "type"`），变体为 `Function { arguments: String }`、`Custom { input: String }`、`LocalShell { params: LocalShellParams }`、`Mcp { server: String, tool: String, raw_arguments: Value, raw_tool_call_id: Option<String> }`。

F-041: 文件 `crates/protocol/src/lib.rs` 第456-472行，枚举 `pub enum ToolOutput`（`tag = "type"`），变体为 `Function { body: Option<Value>, success: bool }`、`Mcp { result: Value }`。

F-042: 文件 `crates/protocol/src/lib.rs` 第509-527行，枚举 `pub enum ReviewDecision`（`tag = "type"`），变体为 `Approved`、`ApprovedExecpolicyAmendment`、`ApprovedForSession`、`NetworkPolicyAmendment { host, action }`、`Denied`、`Abort`。

F-043: 文件 `crates/protocol/src/lib.rs` 第710-791行，枚举 `pub enum EventFrame`（`tag = "event"`），变体含 `ResponseStart`、`ResponseDelta`、`ResponseEnd`、`ToolCallStart`、`ToolCallResult`、`McpStartupUpdate`、`McpStartupComplete`、`McpToolCallBegin`、`McpToolCallEnd`、`ExecApprovalRequest`、`ApplyPatchApprovalRequest`、`UserInputRequest`、`ElicitationRequest`、`ExecCommandBegin`、`ExecCommandOutputDelta`、`ExecCommandEnd`、`PatchApplyBegin`、`PatchApplyEnd`、`TurnStarted`、`TurnComplete`、`TurnAborted`、`ThreadGoalUpdated`、`Error`。

## crates/protocol（op / event_msg / ids）

F-044: 文件 `crates/protocol/src/op.rs` 第18-25行，结构体 `pub struct OpEnvelope`，字段为 `op_id: String`、`thread_id: ThreadId`、`session_id: SessionId`、`op: Op`。

F-045: 文件 `crates/protocol/src/op.rs` 第32-97行，枚举 `pub enum Op`（`tag = "kind"`），变体为 `SendMessage { content, mode, model, model_provider, allowed_tools, dynamic_tools, provenance }`、`Steer { content }`、`ContinueGoal`、`RunShellCommand { command }`、`SetGoalStatus { status, clear }`、`Cancel`、`Shutdown`、`PreviewOutboundRequest { json, base_prompt_only }`。

F-046: 文件 `crates/protocol/src/event_msg.rs` 第19-77行，枚举 `pub enum EventMsg`（`tag = "event"`），变体为 `TurnStarted`、`ResponseDelta`、`ToolCallStarted`、`ToolCallComplete`、`TurnComplete`、`TurnUsage`、`CompactionStarted`、`CompactionCompleted`、`Error`。

F-047: 文件 `crates/protocol/src/ids.rs` 第21-23行，结构体 `pub struct ThreadId(pub String)`（`#[serde(transparent)]`）；第27-29行 `pub fn new()` 返回 `Self(format!("thread-{}", Uuid::new_v4()))`。

F-048: 文件 `crates/protocol/src/ids.rs` 第84行，结构体 `pub struct SessionId(pub String)`。

## crates/tools

F-049: 文件 `crates/tools/src/lib.rs` 第26-40行，枚举 `pub enum ToolCapability`，变体为 `ReadOnly`、`WritesFiles`、`ExecutesCode`、`Network`、`Sandboxable`、`RequiresApproval`。

F-050: 文件 `crates/tools/src/lib.rs` 第43-52行，枚举 `pub enum ApprovalRequirement`（`#[default]` 为 `Auto`），变体为 `Auto`、`Suggest`、`Required`。

F-051: 文件 `crates/tools/src/lib.rs` 第55-73行，枚举 `pub enum ToolError`（`thiserror::Error`），变体为 `InvalidInput`、`MissingField`、`PathEscape`、`ExecutionFailed`、`Timeout`、`Cancelled`、`NotAvailable`、`PermissionDenied`。

F-052: 文件 `crates/tools/src/lib.rs` 第125-134行，结构体 `pub struct ToolResult`，字段为 `content: String`、`success: bool`、`metadata: Option<Value>`。

F-053: 文件 `crates/tools/src/lib.rs` 第232-256行，函数 `pub fn required_str<'a>(input: &'a Value, field: &str) -> Result<&'a str, ToolError>`。

F-054: 文件 `crates/tools/src/lib.rs` 第348-364行，结构体 `pub struct ToolDescriptor`，字段为 `name: String`、`input_schema: Value`、`output_schema: Value`、`supports_parallel_tool_calls: bool`、`timeout_ms: Option<u64>`。

F-055: 文件 `crates/tools/src/lib.rs` 第379-386行，枚举 `pub enum ToolCallSource`（`rename_all = "snake_case"`），变体为 `Direct`、`JsRepl`。

F-056: 文件 `crates/tools/src/lib.rs` 第392-402行，结构体 `pub struct ToolCall`，字段为 `name: String`、`payload: ToolPayload`、`source: ToolCallSource`、`raw_tool_call_id: Option<String>`。

F-057: 文件 `crates/tools/src/lib.rs` 第469-493行，trait `pub trait ToolHandler: Send + Sync`（`#[async_trait]`），方法为 `fn kind(&self) -> ToolKind`、`fn matches_kind`、`fn is_mutating(&self) -> bool`、`async fn handle(&self, invocation: ToolInvocation) -> Result<ToolOutput, FunctionCallError>`。

F-058: 文件 `crates/tools/src/lib.rs` 第539-544行，结构体 `pub struct ToolRegistry`（`#[derive(Default)]`），字段为 `handlers: HashMap<String, Arc<dyn ToolHandler>>`、`specs: HashMap<String, ConfiguredToolDescriptor>`、`runtime: ToolCallRuntime`。

F-059: 文件 `crates/tools/src/lib.rs` 第577-628行，方法 `pub async fn dispatch(&self, call: ToolCall, allow_mutating: bool) -> Result<ToolOutput, FunctionCallError>`，依次查找 handler、校验 kind、`MutatingToolRejected` 守卫、`runtime.acquire(configured.supports_parallel_tool_calls)` 后执行。

F-060: 文件 `crates/tools/src/lib.rs` 第653-660行，函数 `fn tool_payload_kind(payload: &ToolPayload) -> ToolKind`，`Mcp` 分支返回 `ToolKind::Mcp`，其余分支返回 `ToolKind::Function`。

F-061: 文件 `crates/tools/src/prepared.rs` 第7-17行，结构体 `pub struct PreparedToolCall`，字段为 `name: String`、`input: Value`、`description: String`、`read_only: bool`、`supports_parallel: bool`、`starts_detached: bool`、`approval: ApprovalRequirement`、`resources: Vec<ResourceClaim>`。

F-062: 文件 `crates/tools/src/resources.rs` 第10-18行，枚举 `pub enum ResourceClaim`（`rename_all = "snake_case"`），变体为 `ReadPath(PathBuf)`、`WritePath(PathBuf)`、`ReadTree(PathBuf)`、`WriteTree(PathBuf)`、`Terminal(String)`、`GlobalExclusive`。

F-063: 文件 `crates/tools/src/resources.rs` 第60-89行，函数 `pub fn schedule_non_conflicting<T>(items: Vec<(T, Vec<ResourceClaim>)>) -> Vec<Vec<T>>`，按 `ResourceClaim::conflicts_with` 将无冲突项放入同一批。

F-064: 文件 `crates/tools/src/outcome.rs` 第10-18行，枚举 `pub enum ToolTerminalStatus`（`rename_all = "snake_case"`），变体为 `Succeeded`、`Failed`、`Denied`、`InvalidArguments`、`Cancelled`、`TimedOut`。

F-065: 文件 `crates/tools/src/outcome.rs` 第39-44行，结构体 `pub struct ToolExecutionOutcome`，字段为 `status: ToolTerminalStatus`、`result: Option<ToolResult>`、`error: Option<ToolError>`。

## crates/mcp

F-066: 文件 `crates/mcp/src/lib.rs` 第17行，`pub use stdio_client::ChildProcessMcpClient;`。

F-067: 文件 `crates/mcp/src/lib.rs` 第20-35行，结构体 `pub struct McpServerConfig`，字段为 `name: String`、`command: String`、`args: Vec<String>`、`env: HashMap<String, String>`、`enabled: bool`。

F-068: 文件 `crates/mcp/src/lib.rs` 第41-49行，结构体 `pub struct ToolFilter`（`#[derive(Default)]`），字段为 `allow: Vec<String>`、`deny: Vec<String>`。

F-069: 文件 `crates/mcp/src/lib.rs` 第52-59行，结构体 `pub struct McpServerDefinition`，字段为 `config: McpServerConfig`、`filter: ToolFilter`。

F-070: 文件 `crates/mcp/src/lib.rs` 第130-140行，trait `pub trait McpManagedClient: Send + Sync`，方法为 `fn list_tools(&self) -> Result<Vec<McpToolDescriptor>>`、`fn call_tool(&self, tool_name: &str, arguments: Value) -> Result<Value>`、`fn list_resources(&self) -> Result<Vec<McpResourceDescriptor>>`、`fn read_resource(&self, uri: &str) -> Result<Value>`。

F-071: 文件 `crates/mcp/src/lib.rs` 第211-214行，结构体 `pub struct McpManager`，字段为 `configs: HashMap<String, (McpServerConfig, ToolFilter)>`、`clients: HashMap<String, Box<dyn McpManagedClient>>`。

F-072: 文件 `crates/mcp/src/lib.rs` 第690-692行，函数 `pub fn run_stdio_server(initial_definitions: Vec<McpServerDefinition>) -> Result<Vec<McpServerDefinition>>`。

## crates/workflow 与 crates/workflow-js

F-073: 文件 `crates/workflow/src/lib.rs` 第7-28行，模块声明为 `elevation`、`experimental_search`、`fleet_composition`、`fleet_exact`、`fleet_preflight`、`fleet_reasoning`、`fleet_snapshot`、`gates`、`js_authoring`、`model_policy`、`named_fleet`、`reasoning_router`、`redaction`、`replay`、`review_repair`、`role_resolve`。

F-074: 文件 `crates/workflow/src/lib.rs` 第63-66行，`pub use gates::{GateError, GateKind, GateOn, GateOnFail, GateOutcome, GateSpec, GateState, GateStatusLine, HandoffArtifact, LaneGateBoard, stopship_gate_pipeline};`。

F-075: 文件 `crates/workflow/src/lib.rs` 第98行，`pub const DEFAULT_FLEET_WORKFLOW_MAX_AGENTS: usize = 1000;`；第99行，`pub const DEFAULT_FLEET_WORKFLOW_MAX_DEPTH: usize = 5;`。

F-076: 文件 `crates/workflow/src/lib.rs` 第101-110行，结构体 `pub struct WorkflowConfig`，字段为 `goal: String`、`max_concurrent: u8`、`description: Option<String>`、`phases: Vec<Phase>`。

F-077: 文件 `crates/workflow-js/src/lib.rs` 第45-49行，模块声明为 `driver`、`error`、`schema`、`testing`、`vm`。

F-078: 文件 `crates/workflow-js/src/lib.rs` 第63行，`pub const WORKFLOW_LIFETIME_CAP: u64 = 1000;`；第70行，`pub const WORKFLOW_MAX_CONCURRENT: usize = 16;`。

## crates/cli 与 crates/config

F-079: 文件 `crates/cli/src/main.rs` 第1-2行，`#[global_allocator] static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;`；第34行调用 `codewhale_cli::run_cli()`。

F-080: 文件 `crates/cli/src/lib.rs` 第35-120行，枚举 `enum ProviderArg`（`#[derive(ValueEnum)]`），变体含 `Deepseek`、`NvidiaNim`、`Openai`、`Anthropic`、`Google`、`Antigravity`、`Xai`、`Mistral`、`Ollama` 等数十个 provider。

F-081: 文件 `crates/config/src/lib.rs` 第1737行，`pub const DEFAULT_SPAWN_DEPTH: u32 = 3;`。

## crates/execpolicy

F-082: 文件 `crates/execpolicy/src/lib.rs` 第201行，枚举 `pub enum AskForApproval`；第276行，结构体 `pub struct ExecPolicyDecision`。

F-083: 文件 `crates/execpolicy/src/lib.rs` 第315行，结构体 `pub struct ExecPolicyEngine`；第446行，方法 `pub fn check(&self, ctx: ExecPolicyContext<'_>) -> Result<ExecPolicyDecision>`。

## crates/tui

F-084: 文件 `crates/tui/src/lib.rs` 第20-21行，`rust_i18n::i18n!("locales", fallback = ["en"]);`，第23-60行列出的模块声明含 `acp_server`、`core`、`fleet`、`hooks`、`mcp_server`、`skills`、`work_graph` 等。

F-085: 文件 `crates/tui/src/prompts/text.rs` 第44行，`pub const BASE_PROMPT: &str`。

F-086: 文件 `crates/tui/src/core/engine.rs` 第239行，结构体 `pub struct EngineConfig`，字段含 `model: String`、`workspace: PathBuf`、`allow_shell: bool`、`trust_mode: bool`、`mcp_config_path: PathBuf`、`skills_dir: PathBuf`；第561行，结构体 `pub struct EngineHandle`；第6361行，函数 `pub fn spawn_engine(config: EngineConfig, api_config: &Config) -> EngineHandle`。

## docs（权威文档关键约束）

F-087: 文件 `docs/MODES.md` 第21-34行，TUI 模式通过 `Tab` 依次循环 `Plan → Work → Operate → Plan`，`Shift+Tab` 循环权限姿态 `Ask → Auto-Review → Full Access`，`/mode plan|work|operate` 直接切换；`Act` 是 `Work` 的兼容别名，存储值归一化为 `agent`。

F-088: 文件 `docs/MODES.md` 第38-48行，工具可用性：`read` 与策略允许的延迟研究工具在 Plan/Work/Operate 均可用；`write`/`edit`/`bash` 在 Plan 模式下「名称可见、执行拒绝」。

F-089: 文件 `docs/MCP.md` 第1-3行，MCP 服务器可为 TUI 启动的本地 stdio 进程，或「Streamable HTTP + legacy SSE fallback」的远程 URL 服务器。

F-090: 文件 `docs/MCP.md` 第73-90行，管理命令含 `codewhale-tui mcp init`、`mcp list`、`mcp tools [server]`、`mcp add <name> --command/--url`、`mcp login/logout/enable/disable <name>`。

F-091: 文件 `docs/FLEET.md` 第18-29行，fleet CLI 动词为 `init`、`run tasks.json --max-workers 4`、`status`、`inspect <worker-id>`、`logs <worker-id>`、`artifacts <worker-id>`、`interrupt <worker-id>`、`restart <worker-id>`、`resume <run-id>`、`stop --all`。

F-092: 文件 `docs/FLEET.md` 第38-40行，fleet 状态存储于 workspace 下 `.codewhale/fleet.jsonl`，worker 日志位于 `.codewhale/fleet/` 与 `.codewhale/fleet-host/`。

F-093: 文件 `docs/SUBAGENTS.md` 第65-70行，角色 `worker`（可写/可网络/可 shell）、`scout`（只读）、`planner`（只产出策略）、`reviewer`（只读并评分）。

F-094: 文件 `docs/SKILLS.md` 第26-32行，可写（CodeWhale-owned）roots 为 `<workspace>/.codewhale/skills/` 与 `~/.codewhale/skills/`；`.claude/skills`、`.opencode/skills` 等为只读兼容目录。

F-095: 文件 `docs/HOOKS.md` 第1-6行，Hooks 是 TUI 运行时特性；`codewhale exec`（无头一次性）、CLI 派发器与子命令、app-server/ACP 均不触发 hooks。

F-096: 文件 `docs/WEB.md` 第10-16行，`codewhale web` 启动内嵌浏览器客户端，默认地址 `http://127.0.0.1:7878`，`--port` 可改端口，服务器始终绑定 `127.0.0.1`。