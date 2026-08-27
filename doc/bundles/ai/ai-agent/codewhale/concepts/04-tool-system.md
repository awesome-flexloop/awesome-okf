---
type: Concept
title: "工具系统"
description: "tools crate 实现工具调用生命周期、schema 校验和调度并行，核心包括 ToolRegistry、ToolHandler trait、ToolCallRuntime 读写锁和六种 FunctionCallError。"
tags: [codewhale, tools, tool-registry, tool-handler, parallel-execution, schema]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# 工具系统

`codewhale-tools` crate 描述为 "Tool invocation lifecycle, schema validation, and scheduler parallelism"，负责管理工具的注册、校验、调度和执行。它依赖 protocol、async-trait、tokio 和 uuid，是 core 运行时的核心组件之一。

## ToolCapability

工具能力枚举定义了六种能力标签：

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum ToolCapability {
    ReadOnly,
    WritesFiles,
    ExecutesCode,
    Network,
    Sandboxable,
    RequiresApproval,
}
```

这些能力标签用于分类工具的行为特征，驱动审批策略和沙箱决策。

## ApprovalRequirement

审批需求有三个级别：

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum ApprovalRequirement {
    #[default]
    Auto,
    Suggest,
    Required,
}
```

- **Auto**（默认）：不需要审批，安全的只读操作
- **Suggest**：建议审批但允许用户跳过
- **Required**：始终需要显式用户审批

## ToolHandler Trait

每个注册的工具都由一个实现了 `ToolHandler` trait 的处理器支持：

```rust
#[async_trait]
pub trait ToolHandler: Send + Sync {
    fn kind(&self) -> ToolKind;

    fn matches_kind(&self, kind: ToolKind) -> bool {
        self.kind() == kind
    }

    fn is_mutating(&self) -> bool {
        false
    }

    async fn handle(
        &self,
        invocation: ToolInvocation,
    ) -> std::result::Result<ToolOutput, FunctionCallError>;
}
```

trait 要求实现三个方法：
- `kind()`：返回处理器期望的 `ToolKind`（如 `Function` 或 `Mcp`）
- `is_mutating()`：工具是否执行需要用户审批的副作用，默认为 `false`（只读/安全）
- `handle()`：执行工具，接受 `ToolInvocation` 并返回 `ToolOutput` 或 `FunctionCallError`

## ToolDescriptor

工具描述符包含工具的名称、JSON schema 和执行约束：

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolDescriptor {
    pub name: String,
    pub input_schema: Value,
    pub output_schema: Value,
    pub supports_parallel_tool_calls: bool,
    pub timeout_ms: Option<u64>,
}
```

- `supports_parallel_tool_calls`：是否允许并发调用，决定调度时获取读锁还是写锁
- `timeout_ms`：每次调用的超时时间（毫秒），`None` 表示无超时

配置后的描述符包装器：

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConfiguredToolDescriptor {
    pub spec: ToolDescriptor,
    pub supports_parallel_tool_calls: bool,
}
```

## ToolCall 与 ToolInvocation

工具调用请求在验证前为 `ToolCall`，验证后为 `ToolInvocation`：

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolCall {
    pub name: String,
    pub payload: ToolPayload,
    pub source: ToolCallSource,
    pub raw_tool_call_id: Option<String>,
}
```

`ToolCallSource` 标识调用来源：

```rust
#[serde(rename_all = "snake_case")]
pub enum ToolCallSource {
    Direct,
    JsRepl,
}
```

验证后的调用上下文：

```rust
#[derive(Debug, Clone)]
pub struct ToolInvocation {
    pub call_id: String,
    pub tool_name: String,
    pub payload: ToolPayload,
    pub source: ToolCallSource,
}
```

`ToolCall` 提供 `execution_subject` 方法，从 shell payload 中提取命令和工作目录：

```rust
impl ToolCall {
    pub fn execution_subject(&self, fallback_cwd: &str) -> (String, String, &'static str) {
        match &self.payload {
            ToolPayload::LocalShell { params } => (
                params.command.clone(),
                params.cwd.clone().unwrap_or_else(|| fallback_cwd.to_string()),
                "shell",
            ),
            _ => (self.name.clone(), fallback_cwd.to_string(), "tool"),
        }
    }
}
```

## FunctionCallError

调度层错误有六种变体：

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum FunctionCallError {
    ToolNotFound { name: String },
    KindMismatch { expected: ToolKind, got: ToolKind },
    MutatingToolRejected { name: String },
    TimedOut { name: String, timeout_ms: u64 },
    Cancelled { name: String },
    ExecutionFailed { name: String, error: String },
}
```

这些错误覆盖了从工具未找到、payload 类型不匹配、变异工具被拒绝、超时、取消到处理器返回错误的全部情况。

工具内部的输入验证错误使用独立的 `ToolError` 枚举：

```rust
pub enum ToolError {
    InvalidInput { message: String },
    MissingField { field: String },
    PathEscape { path: PathBuf },
    ExecutionFailed { message: String },
    Timeout { seconds: u64 },
    Cancelled { message: String },
    NotAvailable { message: String },
    PermissionDenied { message: String },
}
```

## ToolCallRuntime：并行/串行调度

`ToolCallRuntime` 使用 `RwLock` 管理并行和串行工具执行：

```rust
#[derive(Debug)]
pub struct ToolCallRuntime {
    execution_lock: Arc<RwLock<()>>,
}

enum ToolExecutionGuard {
    Parallel(OwnedRwLockReadGuard<()>),
    Serial(OwnedRwLockWriteGuard<()>),
    Reentrant,
}

impl ToolCallRuntime {
    async fn acquire(&self, supports_parallel: bool) -> ToolExecutionGuard {
        if TOOL_EXECUTION_LOCK_HELD.try_with(|_| ()).is_ok() {
            return ToolExecutionGuard::Reentrant;
        }
        if supports_parallel {
            ToolExecutionGuard::Parallel(self.execution_lock.clone().read_owned().await)
        } else {
            ToolExecutionGuard::Serial(self.execution_lock.clone().write_owned().await)
        }
    }
}
```

调度策略：
- **并行工具**（`supports_parallel_tool_calls = true`）：获取读锁，允许多个并行工具重叠执行
- **串行工具**：获取写锁，独占访问
- **可重入调用**：通过 task-local `TOOL_EXECUTION_LOCK_HELD` 检测，跳过锁以避免死锁（工具调用其他工具时）

## ToolRegistry

`ToolRegistry` 是中央注册表，映射工具名称到其规格和处理器：

```rust
#[derive(Default)]
pub struct ToolRegistry {
    handlers: HashMap<String, Arc<dyn ToolHandler>>,
    specs: HashMap<String, ConfiguredToolDescriptor>,
    runtime: ToolCallRuntime,
}
```

### 注册工具

```rust
impl ToolRegistry {
    pub fn register(
        &mut self,
        spec: ToolDescriptor,
        handler: Arc<dyn ToolHandler>,
    ) -> Result<()> {
        let name = spec.name.clone();
        self.specs.insert(
            name.clone(),
            ConfiguredToolDescriptor {
                supports_parallel_tool_calls: spec.supports_parallel_tool_calls,
                spec,
            },
        );
        self.handlers.insert(name, handler);
        Ok(())
    }
}
```

### 调度执行

`dispatch` 方法执行完整的验证和执行流程：

```rust
pub async fn dispatch(
    &self,
    call: ToolCall,
    allow_mutating: bool,
) -> std::result::Result<ToolOutput, FunctionCallError> {
    let handler = self.handlers.get(&call.name).cloned().ok_or_else(|| {
        FunctionCallError::ToolNotFound { name: call.name.clone() }
    })?;
    let configured = self.specs.get(&call.name).cloned().ok_or_else(|| {
        FunctionCallError::ToolNotFound { name: call.name.clone() }
    })?;

    let payload_kind = tool_payload_kind(&call.payload);
    let expected = handler.kind();
    if !handler.matches_kind(payload_kind) {
        return Err(FunctionCallError::KindMismatch { expected, got: payload_kind });
    }
    if handler.is_mutating() && !allow_mutating {
        return Err(FunctionCallError::MutatingToolRejected { name: call.name });
    }

    let invocation = ToolInvocation {
        call_id: call.raw_tool_call_id.clone()
            .unwrap_or_else(|| format!("tool-call-{}", uuid::Uuid::new_v4())),
        tool_name: call.name.clone(),
        payload: call.payload,
        source: call.source,
    };

    let _guard = self.runtime
        .acquire(configured.supports_parallel_tool_calls)
        .await;

    TOOL_EXECUTION_LOCK_HELD.scope(
        (),
        self.execute_with_timeout(handler, configured.spec.timeout_ms, invocation),
    ).await
}
```

调度流程：
1. 按名称查找处理器和规格
2. 验证 payload kind 匹配处理器期望的 kind
3. 如果工具是 mutating 且 `allow_mutating = false`，拒绝执行
4. 构造 `ToolInvocation`（生成 call_id 如果未提供）
5. 获取适当的执行锁（并行/串行/可重入）
6. 在 task-local 作用域内执行（带超时）
7. 返回 `ToolOutput` 或 `FunctionCallError`

## 参数提取的严格策略

工具参数提取器对类型不匹配采取严格策略：
- `null` 表示缺省，取默认值
- 字符串 `"true"` **不会**被强制转为布尔值
- 类型不匹配返回明确的错误信息，而非隐式转换

这种严格策略防止了模型输出的类型混淆导致意外行为。

## 相关概念

- [Agent 核心运行时](02-agent-core.md) — Runtime 中的 tool_registry 组件
- [MCP 协议集成](03-mcp-protocol.md) — MCP 工具作为 ToolHandler 注册
- [沙箱与执行策略](07-sandbox-execpolicy.md) — 工具执行的权限和审批
- [Fleet 多 Agent](05-fleet-subagents.md) — 子 agent 继承工具注册表
- [工作区架构](01-workspace-architecture.md) — tools crate 在分层中的位置
