---
type: Concept
title: 沙箱执行模型
description: >
  Codex CLI 采用多层防御的命令执行安全模型：平台原生沙箱（macOS Seatbelt、
  Linux Landlock/bwrap、Windows Sandbox）、execpolicy 声明式规则引擎、
  用户审批策略（SafetyCheck），以及 Shell 抽象和执行超时/输出限制。
tags: [openai-codex, sandbox, security, execpolicy, seatbelt, landlock, bwrap, execution]
generated:
  by: "reference_agent/trae-cn"
  at: 2026-08-23T10:00:00+08:00
verified:
  by: "process:grep-verification"
  at: 2026-08-23T10:00:00+08:00
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# 沙箱执行模型

Codex CLI 需要在用户机器上执行 shell 命令，因此安全是核心设计考量。它采用三层防御模型，每层独立运作又协同决策，确保命令执行可控、可审计、可回滚。

## 三层防御架构

```
┌─────────────────────────────────────────────┐
│  第 3 层：用户审批策略 (AskForApproval)       │
│  SafetyCheck: AutoApprove / AskUser / Reject │
├─────────────────────────────────────────────┤
│  第 2 层：execpolicy 规则引擎                │
│  PrefixRule / NetworkRuleProtocol / 策略文件  │
├─────────────────────────────────────────────┤
│  第 1 层：平台原生沙箱                       │
│  macOS Seatbelt │ Linux Landlock/bwrap │ Win │
└─────────────────────────────────────────────┘
```

## 第 1 层：平台原生沙箱

沙箱由独立的 `codex-sandboxing` crate 提供，按目标操作系统条件编译：

### Linux

Linux 支持两种后端：

- **Landlock**：Linux 内核原生的非特权沙箱，限制文件系统访问
- **bubblewrap (bwrap)**：用户态命名空间沙箱，提供更强隔离

```rust
// codex-rs/sandboxing/src/lib.rs
#[cfg(target_os = "linux")]
mod bwrap;
pub mod landlock;
```

bwrap 是可选的，系统会检测是否安装了 bubblewrap。WSL1 不支持 bwrap。

### macOS

macOS 使用 **Seatbelt**（`sandbox-exec`），通过沙箱配置文件限制文件系统和网络访问。Seatbelt 是 macOS 自带的沙箱机制。

### Windows

Windows 使用专门的 `codex-windows-sandbox-rs` crate，支持：

- Restricted token 沙箱（非提权）
- Elevated backend 沙箱（提权）
- WFP（Windows Filtering Platform）网络过滤
- 工作区 ACL 控制
- 私有桌面隔离

### 沙箱 API

公共 API 包括：

```rust
pub enum SandboxType { /* ... */ }
pub struct SandboxManager { /* ... */ }
pub fn get_platform_sandbox(...) -> Option<...>;
pub struct SandboxTransformRequest { /* ... */ }
```

沙箱通过"转换请求"模式工作：接收一个执行请求，返回经过沙箱包装的命令（如 `sandbox-exec -p <profile> <command>` 或 `bwrap <args> <command>`）。

### 沙箱环境变量

子进程通过两个环境变量感知沙箱状态：

```rust
pub const CODEX_SANDBOX_NETWORK_DISABLED_ENV_VAR: &str = "CODEX_SANDBOX_NETWORK_DISABLED";
pub const CODEX_SANDBOX_ENV_VAR: &str = "CODEX_SANDBOX";
```

- `CODEX_SANDBOX_NETWORK_DISABLED=1`：网络被限制
- `CODEX_SANDBOX=seatbelt`：在 Seatbelt 沙箱下运行（值因平台而异）

AGENTS.md 严禁修改与这些变量相关的代码，因为测试依赖它们判断是否应提前退出。

## 第 2 层：execpolicy 规则引擎

`codex-execpolicy` crate 提供声明式命令策略：

```rust
pub struct PrefixRule { /* 命令前缀匹配 */ }
pub enum NetworkRuleProtocol { /* 网络协议规则 */ }
pub struct Policy { /* 完整策略 */ }
pub struct ExecPolicyCheckCommand { /* CLI 检查命令 */ }
```

策略文件定义允许/拒绝的命令前缀和网络访问规则。可通过 CLI 独立检查：

```bash
codex execpolicy check -- <command>
```

规则类型包括：
- **PrefixRule**：基于命令前缀的允许/拒绝（如允许 `git status`，拒绝 `rm -rf /`）
- **PatternToken**：命令参数的模式匹配
- **网络规则**：按协议和域名控制网络访问

execpolicy 与平台沙箱互补：沙箱在操作系统层面强制执行，execpolicy 在 agent 层面提供更细粒度的命令白名单。

## 第 3 层：用户审批策略

### AskForApproval

`AskForApproval` 枚举定义审批模式：

- `Never`：从不询问（配合沙箱自动批准安全操作）
- `OnRequest`：按需询问
- `UnlessTrusted`：不信任时询问
- `Granular`：细粒度控制（含 `sandbox_approval` 等子开关）

### SafetyCheck

`safety.rs` 在执行补丁操作前评估安全性：

```rust
pub enum SafetyCheck {
    AutoApprove,
    AskUser,
    Reject { reason: String },
}
```

评估逻辑：
1. 空补丁直接拒绝
2. 如果补丁写入路径被约束在可写根目录内，且平台沙箱可用，则自动批准
3. 如果沙箱不可用，回退到询问用户
4. 写入项目外或只读沙箱下拒绝
5. 硬链接可能指向可写路径外的文件，因此即使路径看似安全也在沙箱中执行

### Python SDK 沙箱预设

Python SDK 将复杂配置简化为三档：

```python
class Sandbox(str, Enum):
    read_only = "read-only"
    workspace_write = "workspace-write"
    full_access = "full-access"
```

映射到 wire 类型：
- `read_only` → `ReadOnlySandboxPolicy(type="readOnly")`
- `workspace_write` → `WorkspaceWriteSandboxPolicy(type="workspaceWrite")`
- `full_access` → `DangerFullAccessSandboxPolicy(type="dangerFullAccess")`

## Shell 抽象

`shell.rs` 显式建模五种 shell 类型，因为不同 shell 的参数传递直接影响安全：

```rust
pub fn derive_exec_args(&self, command: &str, use_login_shell: bool) -> Vec<String> {
    match self.shell_type {
        ShellType::Zsh | ShellType::Bash | ShellType::Sh => {
            let arg = if use_login_shell { "-lc" } else { "-c" };
            vec![self.shell_path, arg, command]
        }
        ShellType::PowerShell => {
            vec![self.shell_path, "-NoProfile", "-Command", command]
        }
        ShellType::Cmd => {
            vec![self.shell_path, "/c", command]
        }
    }
}
```

Shell 类型从环境检测或 exec-server 的 `ShellInfo` 获取。

## 执行限制

`exec.rs` 设置了多层硬限制防止资源耗尽：

```rust
pub const DEFAULT_EXEC_COMMAND_TIMEOUT_MS: u64 = 10_000;  // 10 秒超时
const EXEC_OUTPUT_MAX_BYTES: usize = DEFAULT_OUTPUT_BYTES_CAP;  // 输出字节上限
pub const MAX_EXEC_OUTPUT_DELTAS_PER_CALL: usize = 10_000;  // delta 事件上限
pub const IO_DRAIN_TIMEOUT_MS: u64 = 2_000;  // I/O 排空超时
```

- **超时**：默认 10 秒，超时后发送 SIGKILL（信号码 9）
- **输出上限**：防止失控命令 OOM
- **Delta 上限**：限制实时事件流数量，但仍收集完整输出
- **I/O 排空**：子进程终止后 2 秒内关闭管道，防止继承 fd 的孙进程挂起

## CLI 沙箱命令

`codex sandbox` 子命令允许直接在 Codex 提供的沙箱中运行命令，类型按平台分派：

```rust
#[cfg(target_os = "macos")]
type HostSandboxArgs = codex_cli::SeatbeltCommand;
#[cfg(target_os = "linux")]
type HostSandboxArgs = codex_cli::LandlockCommand;
#[cfg(target_os = "windows")]
type HostSandboxArgs = codex_cli::WindowsCommand;
```

支持 `--permission-profile` 指定命名权限配置，`-C/--cd` 设置工作目录，`--allow-unix-socket` 允许 Unix socket 访问（macOS）。

## 相关概念

- [Rust 核心与 TUI](02-rust-core-tui.md)
- [Skills 与 AGENTS.md](05-skills-agents-md.md)
- [Python SDK](06-python-sdk.md)
- [简介](00-introduction.md)
