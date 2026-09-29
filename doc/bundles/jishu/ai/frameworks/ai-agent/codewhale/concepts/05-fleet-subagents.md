---
type: Concept
title: "Fleet 多 Agent 编排"
description: "Fleet 是本地优先的持久化多 worker 控制平面，每个 worker 是无头 codewhale exec 进程，核心原则是委派转移工作但永不转移权威，子 agent 权限被 clamp 到父级姿态。"
tags: [codewhale, fleet, multi-agent, subagent, worker, role, permission-clamp]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# Fleet 多 Agent 编排

Fleet 是 CodeWhale 的本地优先持久化多 worker 运行控制平面。与简单的 prompt fanout 不同，每个 fleet worker 是一个无头的 `codewhale exec` 进程，拥有重试、重启存活和账本审计追踪。Fleet 的核心安全原则是"委派转移工作，永不转移权威"——子 agent 的权限被 clamp 到父级实时姿态，只读性在委派链中是传递的。

## 持久化与状态

Fleet 状态存储在工作区的 `.codewhale/fleet.jsonl`，日志在 `.codewhale/fleet/`。`codewhale fleet resume <run-id>` 是幂等的重启恢复动词，重放账本并协调心跳丢失的租约。

Fleet worker 不是短暂的模拟——`worker_runtime.rs` 模块使每个 fleet worker 真正地派发一个无头子 agent：

> Architecture:
> - `FleetTaskSpec` + `FleetWorkerSpec` → `AgentWorkerSpec`
> - `SubAgentManager::register_worker()` tracks the worker
> - Sub-agent spawn happens through the existing `agent` machinery
> - Mailbox events stream into fleet ledger as `FleetWorkerEventPayload`
> - `FleetWorkerInspection` reads both ledger state and sub-agent worker records

## Worker 角色

Fleet 支持八种 worker 角色：

| 角色 | 说明 | 默认姿态 |
|------|------|----------|
| `worker` | 通用工作者 | 继承父级 |
| `scout` | 侦察/探索 | 只读检查 |
| `planner` | 规划者 | 只读分析 |
| `reviewer` | 审查者 | 只读审查 |
| `builder` | 构建者 | 读写 |
| `verifier` | 验证者 | 只读验证 |
| `consultant` | 顾问 | 咨询（兼容规范角色名） |
| `custom` | 自定义 | 需显式工具 allowlist |

角色名称在创建持久化任务前通过 `canonicalize_fleet_task_roles` 规范化：

```rust
pub(crate) fn canonicalize_fleet_task_roles(tasks: &mut [FleetTaskSpec]) {
    for task in tasks {
        let Some(role) = task.worker.as_mut().and_then(|worker| worker.role.as_mut()) else {
            continue;
        };
        *role = canonical_public_role_name(role.trim());
    }
}
```

## 子 Agent 工具继承

子 agent 默认继承父级工具注册表，包括 `agent` 工具本身（即支持递归 spawn）。默认 spawn 深度为 3。

模型面向的 subagent 工具名为 `agent`。已移除的 `agent_open`/`agent_eval`/`agent_close` 不再存在。

## 权限 Clamp 模型

这是 Fleet 安全模型的核心。角色定义的是**意图姿态**，父级的有效姿态始终是上限。`ChildAuthority` 结构体在 `crates/tui/src/fleet/exact.rs` 中定义：

```rust
pub(crate) struct ChildAuthority {
    pub(crate) ceiling: PermissionCeiling,
    pub(crate) allowed_tools: Option<Vec<String>>,
    pub(crate) disallowed_tools: Vec<String>,
    pub(crate) write_authority: &'static str,
    pub(crate) max_depth: u32,
    pub(crate) posture_role: &'static str,
}
```

### clamp 方法

`ChildAuthority::clamp` 将保存的成员上限与实时会话姿态取交集：

```rust
impl ChildAuthority {
    #[must_use]
    pub(crate) fn clamp(member: PermissionCeiling, session: PermissionCeiling) -> Self {
        let ceiling = member.clamp_to(session);

        let allowed_tools = (!ceiling.tools).then(Vec::new);

        let mut disallowed_tools = Vec::new();
        if !ceiling.network_tool {
            disallowed_tools.extend(NETWORK_TOOL_DENYLIST.iter().map(|name| (*name).to_string()));
        }
        if !(ceiling.write && ceiling.shell == ShellCeiling::Full) {
            disallowed_tools.extend(RAW_SHELL_DENYLIST.iter().map(|name| (*name).to_string()));
        }
        // ...
    }
}
```

每个字段取更严格的一侧，因此保存的 Fleet 只能收窄实时权限。关键行为：
- `tools = false` 是完全的：空 allowlist 使子级没有模型可见工具
- deny 列表是父级限制和成员限制的**并集**，后代永远不能丢弃祖先施加的限制
- 原始 shell 需要 ceiling 明确声明 `shell = "full"`；任何更窄的 shell 姿态（`none` 或 `read_only`）都会丢失原始命令面

### PermissionCeiling

权限上限定义了成员的能力边界：

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

注意 `network_tool` 字段控制的是**模型可见的网络工具**（fetch、browse、HTTP），而不是传输层。CodeWhale 代表成员进行的普通 API 调用始终通过网络进行，不受此字段控制。

### 只读角色的 shell 保留

`clamp_for_role` 方法为只读检查角色（scout、explore、reviewer、planner 等）保留一个规范的前台 shell 工具（`Bash`），但拒绝所有遗留、后台、交互式和终端别名：

```rust
pub(crate) fn clamp_for_role(
    role: &str,
    member: PermissionCeiling,
    session: PermissionCeiling,
) -> Self {
    let mut authority = Self::clamp(member, session);
    authority.posture_role = posture_role_for_member(role, authority.ceiling);
    let bounded_inspection_role = matches!(
        role.trim().to_ascii_lowercase().as_str(),
        "scout" | "explore" | "explorer" | "reviewer" | "review"
            | "planner" | "plan" | "planning" | "awaiter"
    );
    if bounded_inspection_role && authority.ceiling.shell != ShellCeiling::None {
        authority.disallowed_tools.retain(|name| !name.eq_ignore_ascii_case("Bash"));
    }
    authority
}
```

这意味着只读角色仍可执行 `git`、`rg`、`gh ... view|list` 等检查命令，但 Bash 规范和机器权限信封都会对具体输入重新分类，移除名称拒绝不会授予任意命令通道。

### 重新计算而非信任副本

Authority binding 在跨 await 点（gates、并发槽、router 调用）后会**重新计算**权限，而不是信任传递的副本：

```rust
pub(crate) struct AuthorityBinding {
    pub(crate) authority: ChildAuthority,
    pub(crate) session: PermissionCeiling,
}
```

注释说明："recomputing is what makes a stale or tampered authority detectable rather than merely improbable."

## Exact Fleet 五条不变量

`exact.rs` 模块声明了五条治理不变量：

1. **路由先冻结，并在冻结时检查** — Provider 身份、wire model、endpoint、凭证就绪和推理能力在 Workflow 启动前全部解析
2. **准入先于成本** — 任务在 roster 解析、gate 检查和并发槽分配后才调用 Router，被拒绝的任务不消耗 Router token
3. **Auto 是推理决策，由附加的 Router 做出** — `reasoning = "auto"` 始终发送到 Fleet 的 Reasoning Router，无 provider-native-adaptive 绕过
4. **上限收窄真实子级** — 保存的权限上限与实时父级姿态取交集，转化为子运行时强制执行的实际工具策略
5. **回执真实且无内容** — selector 选择的 tier、provider 实际接收的控制和 Router 成本分别记录；任务文本从不记录

## Agent Profile

Fleet profile 可以从项目级 `.codewhale/agents/` 或个人级 `$CODEWHALE_HOME/agents/` 加载：

```rust
pub const WORKSPACE_AGENT_PROFILE_DIR: &str = ".codewhale/agents";
pub const PERSONAL_AGENT_PROFILE_DIR: &str = "agents";

pub struct AgentProfile {
    pub id: String,
    pub display_name: Option<String>,
    pub description: Option<String>,
    pub profile: FleetProfile,
    pub source: PathBuf,
    pub origin: ProfileOrigin,
    pub plugin_authority: Option<PluginAuthority>,
}
```

## 路由验证

在 Fleet run 创建时（租约任何 worker 之前），`validate_fleet_task_routes` 验证每个任务固定的模型路由确实可解析。这捕获了"无 provider 的模型固定"失败模式：配置了具体模型但没有显式 provider，运行时从不会从模型拼写推断 provider。

## Workflow 集成硬上限

Fleet 形态的 Workflow 计划有硬上限：

```rust
pub const DEFAULT_FLEET_WORKFLOW_MAX_AGENTS: usize = 1000;
pub const DEFAULT_FLEET_WORKFLOW_MAX_DEPTH: usize = 5;
```

这些限制与 JS Workflow VM 的 `WORKFLOW_LIFETIME_CAP = 1000` 一致。

## 相关概念

- [Workflow 工作流引擎](06-skills-hooks.md) — 声明式 IR 与命令式 JS 双轨
- [Agent 核心运行时](02-agent-core.md) — Runtime 和 ThreadManager
- [工具系统](04-tool-system.md) — 子 agent 继承工具注册表
- [沙箱与执行策略](07-sandbox-execpolicy.md) — 权限 clamp 与执行策略
- [MCP 协议集成](03-mcp-protocol.md) — 网络工具 deny list
