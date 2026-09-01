---
type: Concept
title: "Skills 系统与 Hooks 生命周期"
description: "Skills 是可复用的 SKILL.md 指令包，采用根目录/审计/变更控制器/管理器视图四层架构；Hooks 提供七个生命周期事件和四种内置 Sink，用于扩展和通知。"
tags: [codewhale, skills, hooks, plugin, lifecycle, extension, sk-md]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# Skills 系统与 Hooks 生命周期

CodeWhale 提供两套互补的扩展机制：**Skills** 是可复用的 `SKILL.md` 指令包，通过四层架构管理发现、审计和变更；**Hooks** 是生命周期事件分发系统，允许外部 sink 响应 response、tool、job 和 approval 事件。

## Skills 四层架构

Skill 系统的核心设计是严格分离"磁盘上有什么"（审计）和"模型看到什么"（运行时合并），以及"谁能写文件"（变更控制器）和"谁只能发意图"（TUI 视图）。

### 第一层：根目录（Root Catalog）

根目录是优先级和所有权的唯一来源。`crates/tui/src/skills/roots.rs` 枚举所有 skill 根，标记所有权和访问权限：

```rust
pub enum SkillRootKind {
    CodeWhaleProject,
    CodeWhaleGlobal,
    CompatibleProject(CompatibleHarness),
    CompatibleGlobal(CompatibleHarness),
    Configured,
    BuiltIn,
    ReviewedPluginSnapshot,
    RegistryCache,
}

pub enum SkillRootAccess {
    WritableOwned,
    ReadOnlyExternal,
    Immutable,
    CacheOnly,
}
```

**可写目录**（仅 CodeWhale 拥有的）：
- 项目级：`<workspace>/.codewhale/skills/`
- 全局级：`~/.codewhale/skills/`

**只读兼容目录**（CodeWhale 可发现和审计但永不写入）：
- `.agents/skills`、`.claude/skills`、`.cursor/skills`、`.opencode/skills`、`.codex/skills` 等

兼容的外部 harness 类型：

```rust
pub enum CompatibleHarness {
    Agents,
    Claude,
    Cursor,
    OpenCode,
    Codex,
    DeepSeekLegacy,
    FlatProjectSkills,
}
```

每个根描述符包含稳定 ID、路径、kind、access 和 scope（Project/Global/Logical）：

```rust
pub struct SkillRootDescriptor {
    pub id: SkillRootId,
    // ...
}
```

### 第二层：审计（Audit）

审计层是有界的只读磁盘清单，定义在 `crates/tui/src/skills/audit.rs`。它**故意不合并**同名 skill——显示每个磁盘副本以使冲突和遮蔽可见。

审计限制：

```rust
pub const AUDIT_MAX_SKILL_MD_BYTES: u64 = 512 * 1024;
pub const AUDIT_MAX_PACKAGE_BYTES: u64 = package_digest::PACKAGE_DIGEST_MAX_BYTES;
pub const AUDIT_MAX_FILES: usize = package_digest::PACKAGE_DIGEST_MAX_FILES;
pub const AUDIT_MAX_DEPTH: usize = package_digest::PACKAGE_DIGEST_MAX_DEPTH;
```

审计模式：

```rust
pub enum SkillAuditMode {
    OwnedOnly,
    Compatible,
}
```

每个磁盘上的 skill 副本有稳定标识：

```rust
pub struct AuditedSkillId {
    pub root_id: SkillRootId,
    pub relative_dir: PathBuf,
    pub canonical_name: String,
}
```

审计还跟踪包摘要状态（`DigestState::Known(String)` 或 `DigestState::Unknown(DigestUnknownReason)`）和解析器状态。关键设计：审计层永不执行 skill 内容、永不联系网络、永不写入。

### 第三层：变更控制器（Mutation Controller）

变更控制器是唯一有权写入 skill 文件的组件。TUI 视图发出变更请求，宿主运行控制器执行实际文件操作。

插件安装遵循 trust-then-enable 生命周期：
1. 安装到 `~/.codewhale/plugins/<name>/`
2. 需要 hash-bound trust receipt
3. 更新时字节相同则 no-op
4. 变化则原子交换并自动失效 trust receipt

插件支持三种安装源：
- 本地目录
- GitHub archive
- 直接 tarball URL

### 第四层：管理器视图（TUI View）

TUI 视图从不直接调用安装助手或触碰文件系统。它发出变更请求，宿主运行控制器执行。运行时发现（`SkillRegistry`）合并 skill 供模型使用，但审计显示所有副本。

### 内置 Skill 包

CodeWhale 捆绑了一批第一方 skill，在首次启动时自动安装。`crates/tui/src/skills/system.rs` 定义了打包版本和技能列表：

```rust
const BUNDLED_SKILL_VERSION: &str = "10";
```

内置 skill 涵盖：
- **系统与扩展**：skill-creator、delegate、plugin-creator、skill-installer、mcp-builder、fleet-manager、help
- **终端用户工作流**：handoff、best-of-n、interview、plan、implement、debug、test、review、verify、research、simplify
- **文档与数据**：document、dataviz、docx、pdf、pptx、xlsx
- **Power/显式调用**：batch、release、dependency-update、contributor-onboarding

## Hooks 系统

Hooks 是 TUI 运行时特性，用于在 agent 生命周期关键点发出事件。`codewhale exec`（headless）、CLI dispatcher、app-server/ACP 不触发 hooks。

### HookEvent 枚举

`HookEvent` 定义了七个变体，使用 `snake_case` 序列化和 `"type"` 判别器：

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum HookEvent {
    ResponseStart { response_id: String },
    ResponseDelta { response_id: String, delta: String },
    ResponseEnd { response_id: String },
    ToolLifecycle {
        response_id: String,
        tool_name: String,
        phase: String,
        payload: Value,
    },
    JobLifecycle {
        job_id: String,
        phase: String,
        progress: Option<u8>,
        detail: Option<String>,
    },
    ApprovalLifecycle {
        approval_id: String,
        phase: String,
        reason: Option<String>,
    },
    GenericEventFrame { frame: Box<EventFrame> },
}
```

事件覆盖的生命周期：
- **Response**：Start（流开始）、Delta（增量文本块）、End（流完成）
- **Tool**：工具执行阶段转换（start、end、error）
- **Job**：后台任务阶段转换（queued、running、done）
- **Approval**：审批请求阶段转换（requested、approved、denied）
- **Generic**：转发任意协议级 `EventFrame` 的兜底变体

`to_json()` 方法将事件序列化为 JSON，序列化失败时回退为 `{"type":"serialization_error"}` 而非 panic。

### HookSink Trait

所有事件目的地实现 `HookSink` trait：

```rust
#[async_trait]
pub trait HookSink: Send + Sync {
    async fn emit(&self, event: &HookEvent) -> Result<()>;
}
```

sink 被期望为**尽力而为**：实现应避免 panic，仅在真正意外的失败时返回错误。

### 四种内置 Sink

**1. StdoutHookSink**

将每个事件作为单行 JSON 打印到 stdout，用于本地开发和调试：

```rust
#[derive(Default)]
pub struct StdoutHookSink;

#[async_trait]
impl HookSink for StdoutHookSink {
    async fn emit(&self, event: &HookEvent) -> Result<()> {
        println!("{}", event.to_json());
        Ok(())
    }
}
```

**2. JsonlHookSink**

将每个事件作为 JSON 行追加到文件，使用内部 mutex 序列化并发写入以防止行交错：

```rust
pub struct JsonlHookSink {
    path: PathBuf,
    write_lock: tokio::sync::Mutex<()>,
}
```

每行格式为 `{"at": "<ISO 8601 时间戳>", "event": {...}}`。父目录在首次 emit 时延迟创建，写入后 flush 以保证顺序 emit 的立即可见性。

**3. WebhookHookSink**

将每个事件作为 JSON POST 到远程 HTTP endpoint。最多重试 2 次，指数退避为 200ms、400ms。请求体格式与 JsonlHookSink 相同。

**4. UnixSocketHookSink**

将事件写入 Unix socket。在非 Unix 平台上 `emit` 为 no-op（返回 `Ok(())`）。

### HookDispatcher

`HookDispatcher` 将事件广播到所有注册的 sink，单个 sink 的错误被静默丢弃：

```rust
#[derive(Default, Clone)]
pub struct HookDispatcher {
    sinks: Vec<Arc<dyn HookSink>>,
}

impl HookDispatcher {
    pub fn add_sink(&mut self, sink: Arc<dyn HookSink>) {
        self.sinks.push(sink);
    }

    pub fn sink_count(&self) -> usize {
        self.sinks.len()
    }

    pub async fn emit(&self, event: HookEvent) {
        for sink in &self.sinks {
            let _ = sink.emit(&event).await;
        }
    }
}
```

`sink_count()` 方法使传输设置可以断言确切连接了哪些 sink（例如 stdio 模式下没有 stdout sink）。

## 插件扩展

插件可以贡献 MCP 服务器和 skills，但需要 hash-bound trust receipt 才能启用。插件安装到 `~/.codewhale/plugins/<name>/`，具有以下安全特性：

- 安装后需要 trust（hash-bound）再 enable
- 更新时字节相同则 no-op，变化则原子交换
- trust receipt 在内容变化时自动失效，需要重新审查
- 插件贡献的 MCP 服务器使用更严格的审查边界（未知字段失败关闭、远程 literal headers 被拒绝）

## 相关概念

- [Fleet 多 Agent](05-fleet-subagents.md) — fleet-manager skill 和子 agent 编排
- [MCP 协议集成](03-mcp-protocol.md) — 插件贡献的 MCP 服务器
- [Agent 核心运行时](02-agent-core.md) — Runtime 中的 hooks 组件
- [工具系统](04-tool-system.md) — ToolLifecycle 事件
- [CodeWhale 简介](00-introduction.md) — 项目概述
