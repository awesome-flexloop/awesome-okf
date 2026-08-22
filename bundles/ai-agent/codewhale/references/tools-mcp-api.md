---
type: reference
title: Tools 与 MCP API 参考
description: CodeWhale 工具注册表、资源调度、终态建模与 MCP 管理器/客户端的关键签名
tags: [codewhale, rust, tools, mcp]
sources:
  - resource: "/references/crates-overview.md"
    title: "Crates 全景概览"
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# Tools 与 MCP API 参考

本页登记 `tools`、`mcp` 两个 crate 的关键类型签名。

## 工具系统（crates/tools）

```rust
pub enum ToolCapability { ReadOnly, WritesFiles, ExecutesCode, Network, Sandboxable, RequiresApproval }

pub enum ApprovalRequirement { Auto, Suggest, Required }   // default = Auto

pub enum ToolError {
    InvalidInput { message }, MissingField { field }, PathEscape { path },
    ExecutionFailed { message }, Timeout { seconds }, Cancelled { message },
    NotAvailable { message }, PermissionDenied { message },
}

pub struct ToolResult {
    pub content: String,
    pub success: bool,
    pub metadata: Option<Value>,
}

pub struct ToolDescriptor {
    pub name: String,
    pub input_schema: Value,
    pub output_schema: Value,
    pub supports_parallel_tool_calls: bool,
    pub timeout_ms: Option<u64>,
}

pub enum ToolCallSource { Direct, JsRepl }

pub struct ToolCall {
    pub name: String,
    pub payload: ToolPayload,
    pub source: ToolCallSource,
    pub raw_tool_call_id: Option<String>,
}

#[async_trait]
pub trait ToolHandler: Send + Sync {
    fn kind(&self) -> ToolKind;
    fn matches_kind(&self, kind: ToolKind) -> bool;
    fn is_mutating(&self) -> bool;                       // default false
    async fn handle(&self, invocation: ToolInvocation) -> Result<ToolOutput, FunctionCallError>;
}

pub struct ToolRegistry {
    handlers: HashMap<String, Arc<dyn ToolHandler>>,
    specs: HashMap<String, ConfiguredToolDescriptor>,
    runtime: ToolCallRuntime,
}

impl ToolRegistry {
    pub fn register(&mut self, spec: ToolDescriptor, handler: Arc<dyn ToolHandler>) -> Result<()>;
    pub fn list_specs(&self) -> Vec<ConfiguredToolDescriptor>;
    pub async fn dispatch(&self, call: ToolCall, allow_mutating: bool)
        -> Result<ToolOutput, FunctionCallError>;
}
```

### 资源调度与终态

```rust
// crates/tools/src/resources.rs
pub enum ResourceClaim {
    ReadPath(PathBuf), WritePath(PathBuf), ReadTree(PathBuf), WriteTree(PathBuf),
    Terminal(String), GlobalExclusive,
}
pub fn schedule_non_conflicting<T>(items: Vec<(T, Vec<ResourceClaim>)>) -> Vec<Vec<T>>;

// crates/tools/src/outcome.rs
pub enum ToolTerminalStatus { Succeeded, Failed, Denied, InvalidArguments, Cancelled, TimedOut }
pub struct ToolExecutionOutcome {
    pub status: ToolTerminalStatus,
    result: Option<ToolResult>,
    error: Option<ToolError>,
}
```

`ResourceClaim::conflicts_with` 实现以下冲突规则：`GlobalExclusive` 与任何其他 claim 冲突；同名 `Terminal` 冲突；`WritePath`/`WriteTree` 与路径重叠的读写冲突；纯读之间不冲突（见 [F-062]）。

## MCP 系统（crates/mcp）

```rust
pub struct McpServerConfig {
    pub name: String,
    pub command: String,
    pub args: Vec<String>,
    pub env: HashMap<String, String>,
    pub enabled: bool,
}

pub struct ToolFilter { pub allow: Vec<String>, pub deny: Vec<String> }   // deny 优先，allow 空 = 全放行

pub struct McpServerDefinition { pub config: McpServerConfig, pub filter: ToolFilter }

pub trait McpManagedClient: Send + Sync {
    fn list_tools(&self) -> Result<Vec<McpToolDescriptor>>;
    fn call_tool(&self, tool_name: &str, arguments: Value) -> Result<Value>;
    fn list_resources(&self) -> Result<Vec<McpResourceDescriptor>>;
    fn read_resource(&self, uri: &str) -> Result<Value>;
}

pub struct McpManager {
    configs: HashMap<String, (McpServerConfig, ToolFilter)>,
    clients: HashMap<String, Box<dyn McpManagedClient>>,
}

impl McpManager {
    pub fn register_server(&mut self, config: McpServerConfig, filter: ToolFilter,
        client: Box<dyn McpManagedClient>) -> Result<()>;
}

pub use stdio_client::ChildProcessMcpClient;
pub fn run_stdio_server(initial_definitions: Vec<McpServerDefinition>) -> Result<Vec<McpServerDefinition>>;
```

`register_server` 会用 `sanitize_component` 折叠后检查名称冲突：`my-server`、`my_server`、`My.Server` 都产生 `mcp__my_server__*` 限定名，重复注册会 `bail!`（见 [F-071] 上下文）。

## 相关文档

- [Crates 全景概览](/references/crates-overview.md)
- [工具系统](/concepts/02-tools-system.md)
- [MCP 集成](/concepts/03-mcp-integration.md)