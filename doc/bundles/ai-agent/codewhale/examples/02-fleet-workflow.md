---
type: Example
title: "Fleet 工作流示例"
description: "演示 Fleet profile TOML 配置、声明式 WorkflowSpec 定义和基于 QuickJS 的命令式 JS workflow 脚本编写，包含角色、权限和并发控制。"
tags: [codewhale, example, fleet, workflow, subagent, js, toml, multi-agent]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# Fleet 工作流示例

本示例演示如何配置 Fleet profile、编写声明式 Workflow TOML 和命令式 JS Workflow 脚本，实现多 Agent 协同工作。

## 1. Fleet Profile 配置

Fleet profile 定义了 Agent 角色的权限和模型路由。Profile 文件放在项目级 `.codewhale/agents/` 或个人级 `$CODEWHALE_HOME/agents/` 目录。

### 基本 Profile TOML

```toml
id = "code-reviewer"
name = "代码审查员"
description = "只读代码审查专家，使用强推理模型"

[permissions]
write = false
network_tool = false
shell = "read_only"
tools = true
delegation_depth = 1

[model]
provider = "deepseek"
model = "deepseek-v4-pro"
reasoning = "high"
```

`PermissionCeiling` 结构体定义了权限上限的字段：

```rust
pub struct PermissionCeiling {
    pub write: bool,
    #[serde(alias = "network")]
    pub network_tool: bool,
    pub shell: ShellCeiling,
    pub delegation_depth: u32,
    pub tools: bool,
}
```

### Builder Profile（读写权限）

```toml
id = "builder"
name = "构建者"
description = "可以写入文件和执行命令的实现 Agent"

[permissions]
write = true
network_tool = false
shell = "full"
tools = true
delegation_depth = 2

[model]
provider = "deepseek"
model = "deepseek-v4-flash"
reasoning = "medium"
```

### Custom Profile（需显式工具 allowlist）

```toml
id = "docs-writer"
name = "文档编写者"
description = "只能编辑文档文件的自定义角色"

[permissions]
write = true
network_tool = false
shell = "none"
tools = true
delegation_depth = 0

[tools]
allow = ["read_file", "write_file", "edit_file", "list_dir"]
```

## 2. 声明式 Workflow TOML

`WorkflowSpec` 是类型化的声明式 IR，支持预算、权限、模型策略、门控和 8 种节点类型。

### 完整 Workflow 示例

```toml
goal = "审查并修复 src/auth 模块的安全问题"
description = "多 Agent 协作：侦察、规划、实现、验证"

[budget]
max_tokens = 500000
max_cost_usd = 5.0

[permissions]
allow_write = true
network = false

[model_policy]
default_model = "deepseek-v4-flash"
review_model = "deepseek-v4-pro"

[[nodes]]
kind = "leaf"
id = "scout"
role = "explore"
description = "扫描 src/auth 目录，识别所有潜在安全问题"
mode = "read_only"

[[nodes]]
kind = "sequence"
id = "fix-sequence"

[[nodes.children]]
kind = "leaf"
id = "fix-1"
role = "implementer"
description = "修复第一个发现的安全漏洞"
mode = "read_write"
isolation = "worktree"

[[nodes.children]]
kind = "leaf"
id = "fix-2"
role = "implementer"
description = "修复第二个发现的安全漏洞"
mode = "read_write"
isolation = "worktree"

[[nodes]]
kind = "teacher_review"
id = "review"
description = "教师评审：验证修复是否正确，测试是否通过"
baseline = "scout"
candidate = "fix-sequence"
```

### WorkflowSpec 结构

```rust
pub struct WorkflowSpec {
    pub id: Option<String>,
    pub goal: String,
    pub description: Option<String>,
    pub budget: BudgetSpec,
    pub permissions: PermissionSpec,
    pub model_policy: ModelPolicy,
    pub promotion_policy: PromotionPolicy,
    pub gates: Vec<GateSpec>,
    pub nodes: Vec<WorkflowNode>,
}
```

### 八种节点类型

```rust
#[serde(tag = "kind", content = "spec", rename_all = "snake_case")]
pub enum WorkflowNode {
    BranchSet(BranchSpec),
    Leaf(LeafSpec),
    Sequence(SequenceSpec),
    Reduce(ReduceSpec),
    TeacherReview(TeacherReviewSpec),
    LoopUntil(LoopUntilSpec),
    Cond(CondSpec),
    Expand(ExpandSpec),
}
```

- **BranchSet**：并行或串行分支集合
- **Leaf**：实际 Agent 任务节点
- **Sequence**：顺序执行的子节点
- **Reduce**：归约多个分支结果
- **TeacherReview**：教师评审循环（自动对比 baseline/candidate、检查测试通过和策略违规）
- **LoopUntil**：循环直到条件满足
- **Cond**：条件分支
- **Expand**：运行时动态生成子节点

### Agent 角色

```rust
#[serde(rename_all = "snake_case")]
pub enum AgentType {
    General,
    Explore,
    Plan,
    Review,
    Implementer,
    Verifier,
}
```

### 隔离模式

```rust
#[serde(rename_all = "snake_case")]
pub enum IsolationMode {
    Auto,
    Shared,
    Worktree,
}
```

`Auto` 模式在并行写时自动解析为 `Worktree`，避免并发写冲突：

```rust
impl IsolationMode {
    pub fn resolve(self, parallel_write: bool) -> Self {
        match self {
            Self::Auto if parallel_write => Self::Worktree,
            Self::Auto => Self::Shared,
            other => other,
        }
    }
}
```

### 硬上限

```rust
pub const DEFAULT_FLEET_WORKFLOW_MAX_AGENTS: usize = 1000;
pub const DEFAULT_FLEET_WORKFLOW_MAX_DEPTH: usize = 5;
```

## 3. 命令式 JS Workflow

`codewhale-workflow-js` 提供基于 QuickJS（rquickjs）的沙箱化 JS 运行时。VM 保持单线程，通过 channel 与多线程引擎桥接。

### 基本 JS Workflow

```javascript
// 简单的并行任务工作流
const results = await parallel([
  () => task({
    description: "审查 src/auth/login.rs 的安全问题",
    role: "scout",
    model_strength: "same"
  }),
  () => task({
    description: "审查 src/auth/token.rs 的安全问题",
    role: "scout",
    model_strength: "same"
  }),
  () => task({
    description: "审查 src/auth/session.rs 的安全问题",
    role: "scout",
    model_strength: "same"
  })
]);

log(`侦察完成，发现 ${results.filter(r => r).length} 份报告`);

const summary = await task({
  description: `汇总以下审查结果，列出所有安全问题：\n${results.join("\n---\n")}`,
  role: "planner"
});

phase("实现修复");

const fixes = await parallel([
  () => task({
    description: `根据汇总修复高优先级问题：\n${summary}`,
    role: "implementer",
    worktree: true,
    write_roots: ["src/auth"]
  }),
  () => task({
    description: "为修复编写安全测试",
    role: "verifier",
    worktree: true,
    write_roots: ["tests"]
  })
]);

return { summary, fixes };
```

### Pipeline 示例

```javascript
// 流水线：每个项目依次经过多个阶段
const items = ["auth", "api", "db"];

const results = await pipeline(
  items,
  // 阶段 1：侦察
  (item) => task({
    description: `分析 ${item} 模块的代码质量`,
    role: "scout"
  }),
  // 阶段 2：规划
  (analysis, item) => task({
    description: `基于分析为 ${item} 制定改进计划：\n${analysis}`,
    role: "planner"
  }),
  // 阶段 3：实现
  (plan, item) => task({
    description: `实施 ${item} 的改进计划：\n${plan}`,
    role: "implementer",
    worktree: true,
    write_roots: [`src/${item}`]
  })
);

log(`流水线完成，处理了 ${results.filter(r => r).length} 个模块`);
```

### 带 Schema 验证的任务

```javascript
const issues = await task({
  description: "列出所有需要修复的 bug，返回结构化数据",
  role: "scout",
  responseSchema: {
    type: "object",
    properties: {
      bugs: {
        type: "array",
        items: {
          type: "object",
          properties: {
            file: { type: "string" },
            severity: { type: "string", enum: ["low", "medium", "high", "critical"] },
            description: { type: "string" }
          },
          required: ["file", "severity", "description"]
        }
      }
    },
    required: ["bugs"]
  }
});

// issues 是已解析并验证的对象
for (const bug of issues.bugs) {
  if (bug.severity === "critical" || bug.severity === "high") {
    await task({
      description: `修复 ${bug.file} 中的问题：${bug.description}`,
      role: "implementer",
      worktree: true
    });
  }
}
```

## 4. JS 全局函数与限制

### 可用全局函数

| 函数 | 说明 |
|------|------|
| `await task(opts)` | 派发一个子 agent，返回完整结果文本或 schema 验证对象 |
| `parallel(thunks)` | 全完成扇出，普通失败槽返回 `null`，最多 1000 项 |
| `pipeline(items, ...stages)` | 逐项阶段链，阶段间无屏障，同 1000 项上限 |
| `log(msg)` | 记录进度日志 |
| `phase(title)` | 设置当前阶段标题 |
| `budget.total` | 总预算（无上限时为 `null`） |
| `budget.spent()` | 已花费预算快照 |
| `budget.remaining()` | 剩余预算（无上限时为 `Infinity`） |

### TaskRequest 字段

`task()` 调用映射到 `TaskRequest` 结构体：

```rust
pub struct TaskRequest {
    pub description: String,
    pub subagent_type: Option<String>,
    pub role: Option<String>,
    pub profile: Option<String>,
    pub model: Option<String>,
    pub model_strength: Option<String>,
    pub thinking: Option<String>,
    pub cwd: Option<String>,
    pub worktree: bool,
    pub write_authority: Option<String>,
    pub write_roots: Vec<String>,
    pub exact_files: Vec<String>,
    pub allowed_tools: Option<Vec<String>>,
    pub disallowed_tools: Vec<String>,
    pub max_depth: Option<u32>,
    pub token_budget: Option<u64>,
    pub max_steps: Option<u32>,
    pub wall_time_secs: Option<u64>,
    pub response_schema: Option<serde_json::Value>,
}
```

### 确定性约束

为保证可回放，以下 JS 函数被**禁用**并抛出异常：

- `Date.now()`、`new Date()`、`Date.parse()`、`Date.UTC()`
- `Math.random()`

运行必须是确定性的，以便记录的 trace 可以被回放。

### 并发上限

```rust
pub const WORKFLOW_LIFETIME_CAP: u64 = 1000;
pub const WORKFLOW_MAX_CONCURRENT: usize = 16;
pub const PARALLEL_MAX_ITEMS: usize = 1000;
```

- 每次运行最多 1000 个 agent
- 最多 16 个并发执行 agent
- 单次 `parallel()`/`pipeline()` 最多 1000 项

## 5. 运行 Fleet Workflow

### CLI 命令

```bash
# 使用声明式 TOML 运行
codewhale fleet run --workflow review-fix.toml

# 使用 JS 脚本运行
codewhale fleet run --workflow security-review.js

# 查看 Fleet 状态
codewhale fleet status

# 恢复中断的运行
codewhale fleet resume <run-id>

# 查看当前会话子 agent
/fleet workers
```

### 权限 Clamp 提醒

设计 Fleet 时需记住：角色的默认权限是**意图而非保证**。实际权限由父级姿态 clamp。一个只读的 scout 即使委派给 builder，builder 也不能写——因为 scout 本身是只读的。`ChildAuthority::clamp` 对每个字段取交集，deny-list 取并集：

```rust
pub(crate) fn clamp(member: PermissionCeiling, session: PermissionCeiling) -> Self {
    let ceiling = member.clamp_to(session);
    let allowed_tools = (!ceiling.tools).then(Vec::new);
    // deny list 是父级和成员限制的并集
    // ...
}
```

## 相关概念

- [Fleet 多 Agent](/concepts/05-fleet-subagents.md) — Fleet 控制平面和权限 clamp 模型
- [Agent 核心运行时](/concepts/02-agent-core.md) — Runtime 和 Engine 架构
- [工具系统](/concepts/04-tool-system.md) — 子 agent 工具注册表继承
- [沙箱与执行策略](/concepts/07-sandbox-execpolicy.md) — Worktree 隔离和权限控制
- [基本使用示例](/examples/01-basic-usage.md) — 安装和基础配置
