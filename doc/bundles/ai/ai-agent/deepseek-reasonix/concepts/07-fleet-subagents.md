---
type: Concept
title: Fleet 与 Subagent
description: 多 Agent 并行架构——fleet 工具、subagent profiles、task contract、SubagentScheduler 并发控制、写路径声明、DAG 依赖
tags: [deepseek-reasonix, fleet, subagent, scheduler, parallel, delegation, dag]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-23T00:00:00Z
verified:
  by: process:seven-concepts-v
  at: 2026-08-23T00:00:00Z
status: stable
stale_after: 2027-08-23
sources:
  - id: SRC-001
    resource: /references/source.md
    title: DeepSeek-Reasonix 源码信源索引
---

## Fleet 与 Subagent 概述

Reasonix 支持通过 `task` 工具委派单个子代理，通过 `fleet` 工具并行调度 2-64 个子代理任务。并发安全由 `SubagentScheduler` 通过槽位限制和写路径声明确保。（F-042, F-044）

## SubagentScheduler

`SubagentScheduler` 是 session 级并发控制器，被 task、fleet、parallel_tasks、profile skills 和嵌套 subagent 共享：

```go
type SubagentScheduler struct {
    mu            sync.Mutex
    maxTotal      int
    maxWriters    int
    activeTotal   int
    activeWriters int
    activeLive    []liveClaim
    parentClaims  []WritePathSet
    waiters       []*schedulerWaiter
}
```

（F-042）

### 槽位获取

```go
type AcquireRequest struct {
    Writer     bool
    WritePaths WritePathSet
    Nested     bool
    Label      string
}

func (s *SubagentScheduler) Acquire(ctx context.Context,
    req AcquireRequest) (release func(), err error)
```

- **Writer=true**：写能力运行，需要写路径声明
- **WritePaths**：槽位活跃期间持有的写声明，空表示只读
- **Nested=true**：容量不足时**立即失败**而非排队——嵌套 subagent 不能阻塞等待父持有的槽位
- **parentClaims**：父 agent 在写工具 Execute 期间持有的写路径，阻塞重叠的 subagent 声明但不消耗并发槽位

（F-043）

### 写路径安全

并发 writer 必须声明**不重叠**的 `write_paths`。省略 write_paths 等于声明整个工作区。两个并发的整工作区声明（或任何重叠）在 preflight 阶段失败，**任何任务都不会启动**。

有序任务（通过 `depends_on`）可以共享路径，因为它们不会并发执行。

## FleetTool

`FleetTool` 调度 2-64 个 profile-aware 子代理任务作为小型依赖图：

```go
type FleetTool struct {
    taskTool *TaskTool
}

func (*FleetTool) Name() string { return "fleet" }
```

（F-044）

### 任务 schema

每个 fleet 任务项支持：

| 字段 | 说明 |
|------|------|
| `prompt` | 子代理任务提示（必填） |
| `id` | 可选稳定 ID，被 depends_on 引用，默认 1-based 位置 |
| `depends_on` | 必须在此任务开始前完成的任务 ID |
| `profile` | runAs=subagent profile 名称 |
| `write_paths` | 写目标声明 |
| `read_only` | 强制只读注册表 |
| `tools` | 可选工具白名单（与 profile 允许工具交集） |
| `max_steps` | 可选最大工具调用轮数 |
| `model` | 可选模型覆盖 |
| `effort` | 可选推理 effort 覆盖 |

（F-044）

### 依赖图

- 未知 ID、自引用、循环在 preflight 失败
- 依赖失败或被跳过的任务也被跳过
- 无依赖的任务并行运行
- `fail_fast`：首次失败后停止启动新任务，已运行的任务继续完成（不放弃部分写入）
- `run_in_background`：异步返回 job ID，可用 `wait` 收集

### 任务状态

```go
const (
    fleetItemPending   fleetItemStatus = "pending"
    fleetItemCompleted fleetItemStatus = "completed"
    fleetItemFailed    fleetItemStatus = "failed"
    fleetItemCancelled fleetItemStatus = "cancelled"
    fleetItemSkipped   fleetItemStatus = "skipped"
)
```

（F-045）

## Task 工具与 Subagent Prompt

### 读写分离的 System Prompt

可写 subagent 使用 `DefaultTaskSystemPrompt`：

```
You are a sub-agent invoked by a parent coding agent to carry out one focused task.
Use the provided tools to investigate or act. For MCP, use the stable use_capability
proxy (list → inspect → call); do not expect direct mcp__* tool schemas. Return a
single final answer that is concise and self-contained — the parent will see only
that answer, not your tool calls or reasoning.
```

只读 subagent 使用 `DefaultReadOnlyTaskSystemPrompt`，明确禁止：
- 写文件
- 安装 capability
- 变更 memory
- 控制长生命周期进程
- 委派给 writer-capable agent

（F-046, F-047）

### 递归深度

```go
const DefaultMaxSubagentDepth = 2
```

根 agent depth=0，子代理 depth=1。达到最大深度时，递归 agent/skill 工具被排除。`NormalizeMaxSubagentDepth` 将小于 1 的值规范化为 1（保留旧的单委派边界）。（F-019）

### 工具可见性

```go
var subagentRecursiveTools = []string{
    "task", "read_only_task", "run_skill", "read_only_skill",
    "explore", "research", "review", "security_review",
}

var subagentAlwaysHiddenTools = []string{
    "parallel_tasks", "fleet", "read_subagent_result",
    "set_session_title", "install_skill", "install_source",
}
```

- `read_skill` 故意不在隐藏列表中——它渲染 playbook 文本，不能递归
- 嵌套 depth 达到上限时递归工具被排除
- job 工具（`wait`、`bash_output`、`kill_shell`）在后台模式可用

（F-048, F-049）

## Subagent Profile 管理

CLI 提供 `reasonix subagent` 命令管理 profile：

```sh
reasonix subagent list
reasonix subagent create <name> --description "..." --prompt "..." [--model REF] [--tools a,b]
reasonix subagent edit <name>
reasonix subagent delete <name> --yes
reasonix subagent try <name> <task>    # 试运行
reasonix subagent run <name> <task>    # 正式运行
```

Profile 支持 `--scope project|global`，可指定 model、effort、工具白名单、颜色标记。（F-100）

## 父 Agent 写保留

父 agent 在执行写工具期间通过 `reserveParentWrite` 保留写声明：

```go
func (a *Agent) reserveParentWrite(runTool tool.Tool,
    args json.RawMessage, readOnly bool) (release func(), err error) {
    // subagent (depth > 0)、只读、无 scheduler 时 no-op
    // 否则 parentWriteReservation + scheduler.ReserveParentWrite
}
```

这确保后台 writer 不能在父写操作期间 TOCTOU 竞争同一文件。（F-042 隐含）

## 典型工作流

### Research → Implement → Review

```json
{
  "tasks": [
    {"id": "research", "prompt": "分析 auth 模块", "read_only": true},
    {"id": "implement", "prompt": "实现 OAuth2", "depends_on": ["research"],
     "write_paths": ["internal/auth/"]},
    {"id": "review", "prompt": "安全审查", "depends_on": ["implement"],
     "profile": "security_review", "read_only": true}
  ]
}
```

research 和 review 只读，implement 写 `internal/auth/`。三者有序执行。

### 并行独立修改

```json
{
  "tasks": [
    {"prompt": "重构 user service", "write_paths": ["internal/user/"]},
    {"prompt": "重构 payment service", "write_paths": ["internal/payment/"]}
  ]
}
```

两个任务无依赖、写路径不重叠，并行执行。

## 相关概念

- [Agent 运行循环](02-agent-run-loop.md)——subagent 如何嵌套在 Run 中
- [CLI 与 TUI](05-cli-tui.md)——subagent profile 管理命令
- [Checkpoint 与恢复](06-checkpoint-recovery.md)——后台 writer 的 checkpoint 影响
- [项目架构](01-project-architecture.md)——scheduler 在 boot 中的组装
