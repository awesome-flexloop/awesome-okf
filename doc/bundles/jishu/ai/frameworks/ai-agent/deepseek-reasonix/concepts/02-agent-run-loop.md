---
type: Concept
title: Agent 运行循环
description: Agent 核心——agent.go 结构体、run_loop.go 工具循环、session/task/scheduler、arbiter 仲裁、governor 调控、turn_phase 阶段
tags: [deepseek-reasonix, agent, run-loop, arbiter, governor, session, compaction]
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

## Agent 结构体

`Agent` 是驱动单个任务的核心结构体，将 Provider、工具 Registry 和 Session 连接到主循环中：

```go
type Agent struct {
    agentConfig
    svc      agentServices
    sess     sessionRuntime
    task     taskRuntime
    turn     turnRuntime
    planMode atomic.Bool
    steerMu  sync.Mutex
    steerQueue []steerEntry
    // ...
}
```

（F-014）

通过 `New` 构造：

```go
func New(prov provider.Provider, tools *tool.Registry, session *Session,
    opts Options, sink event.Sink) *Agent
```

（F-015）

`agentServices` 将协作者（prov、tools、sink、gate、extensions、hooks、asker）与 Agent 记忆的状态分离，Controller 可在 turn 之间通过 Set* 方法重新绑定。（F-105）

## Run 入口

`Run` 方法是 agent 主循环入口：

```go
func (a *Agent) Run(ctx context.Context, input string) (runErr error)
```

它追加用户输入，驱动工具循环直到 model 返回最终答案、context 被取消或 provider 出错。（F-016）

## 运行循环结构

主循环 `runToolLoop` 的每一步：

1. **消费 Steer**——检查队列中的 mid-turn 引导
2. **捕获前缀形状**——记录 tool schemas 用于缓存诊断
3. **采样恢复**——调用 `streamWithSamplingRecovery` 获取 model 响应
4. **提交响应**——将 assistant 消息写入 Session
5. **分流**：
   - 无 tool calls → `handleFinalResponse`
   - 有 tool calls → `handleToolRound`

```go
for step := 0; state.runMaxSteps <= 0 || step < state.runMaxSteps || ...; step++ {
    if text, itemID, ok := a.consumeSteer(); ok { ... }
    streamed := a.streamWithSamplingRecovery(ctx, step+1)
    a.sess.conversation.Add(provider.Message{
        Role: provider.RoleAssistant,
        Content: text, ToolCalls: calls, ...
    })
    if len(calls) == 0 {
        cont, ferr := a.handleFinalResponse(ctx, state, text, reasoning, usage)
    } else {
        cont, terr := a.handleToolRound(ctx, state, step, text, reasoning, calls, usage)
    }
}
```

（F-028）

## 采样恢复

`streamWithSamplingRecovery` 实现 Codex 风格的请求冻结重放：

- `prepareSamplingRequest` 准备一次，freeze provider 请求
- 最多 `maxSamplingAttempts = 6` 次 body 尝试（1 初始 + 5 重试）
- 失败尝试**不写 Session 状态、不执行工具**
- 退避策略：0.5s → 1s → 2s → 4s → 8s 带 jitter
- context limit 错误触发 `recoverContextLimit`，重置 attempt 计数器

（F-029, F-034）

`deferredStreamSink` 在 reasoning 到达前缓冲 tool 事件。健康的 DeepSeek 响应先发出 reasoning，解锁实时 tool-card 事件；malformed turn 的推测性 tool cards 保持私有，重试不闪卡。（F-030）

## Turn 初始化

`beginRunTurn` 处理每个 turn 的初始化：

- evidence scope 和 delivery 分类
- background-job evidence re-lease
- runtime constraints 解析（Plan mode、inherited constraints）
- 初始 user-turn 持久化
- `emitTurnPhase(event.TurnPhaseWorking)` 发布阶段事件

（F-031）

## 最终响应处理

`handleFinalResponse` 处理无 tool call 的 assistant turn，包含多个恢复/重试路径：

| 路径 | 触发条件 |
|------|---------|
| Recovery pause | `state.recoveryGraceRound` |
| Readiness retry | final readiness 检查发现缺失签名/证据 |
| Empty final retry | 无可见最终答案（最多 `maxEmptyFinalBlocks=3` 次） |
| Executor handoff nudge | executor 未使用工具（最多 1 次 nudge） |
| Steer drain | `closeSteerIntakeIfIdle` 检查队列 |
| 正常结束 | model 给出最终答案 |

（F-032）

## 工具轮处理

`handleToolRound` 执行工具批次：

1. 检查 context-unavailable 工具重复调用
2. 边界最终化器检查
3. `executeBatch` 并发执行工具
4. 将 tool result 消息持久化到 Session
5. 处理 cancellation（保留已完成的 tool 对）
6. todo 进度追踪
7. 预算检查（task budget、max steps grace round）
8. recovery grace round 处理

（F-033）

## Arbiter 仲裁

Arbiter 定义四级 verdict 升级阶梯：

```go
const (
    verdictContinue verdict = iota
    verdictAdvise
    verdictRedirect
    verdictLand
)
```

每轮信号降级为最强 verdict。`intervention` 包含 verdict、guidance 和 notice：

```go
type intervention struct {
    verdict  verdict
    guidance string
    notice   *event.Event
}
```

`applyInterventions` 将多个信号折叠：最强 verdict 胜出，所有 guidance 追加到 round tail（**不是**合成 user turn），所有 notice 发送给前端。（F-036, F-037）

> 设计要点：Host 不是 user，合成假 user turn 会在 compaction 时与真实 user 文本竞争保留优先级。

## Governor 调控

Reasoning governor 是环境变量门控的 A/B 实验（`REASONIX_EXPERIMENT_GOVERNOR=1`）：

```go
func governorTrigger(sample evidence.OutcomeSample, lastReasoning int) bool {
    return sample.DebtAge == 0 && !sample.LocalExecSeen &&
        lastReasoning >= govReasoningThreshold  // 1500
}

func governorExit(sample evidence.OutcomeSample) bool {
    return sample.DebtAge > 0 || sample.LocalExecSeen ||
        sample.Discriminating > 0
}
```

- **触发**：无验证债务、无本地执行、上一轮 reasoning ≥ 1500 字节
- **退出**：出现突变债务、本地执行或判别性观察
- **效果**：将 provider effort 降为 `"low"`
- 启用时发送一次性 notice

（F-038, F-039, F-040, F-041）

## Turn Phase

`emitTurnPhase` 发布无内容的 host phase 事件，前端据此显示阶段状态：

```go
func (a *Agent) emitTurnPhase(phase event.TurnPhaseName) {
    a.svc.sink.Emit(event.Event{
        Kind: event.TurnPhase,
        PhaseName: phase,
        Text: string(phase),
    })
}
```

（F-035）

## Session 消息管理

`Session` 持有对话历史，`sync.RWMutex` 保护并发访问：

```go
type Session struct {
    mu             sync.RWMutex
    Messages       []provider.Message
    version        uint64
    rewriteVersion int
    // ...
}
```

关键方法：
- `Add(m)`——追加消息，run loop 是唯一写入者
- `Rewrite(msgs, reason)`——原子替换消息日志（compaction/prune/rewind），记录 provider-visible 变更原因
- `Snapshot()`——返回消息副本供跨 goroutine 读取
- `ReplaceLocalMetadata(msgs)`——仅替换本地显示元数据，不报告 cache-prefix 变更

（F-025, F-026, F-027）

## 上下文压缩

自动压缩在 `compactRatio`（默认 0.80）触发：

- 保留最近 16% 的 verbatim 尾部（`recentTailBudgetRatio = 0.16`）
- 摘要最大 8192 tokens
- 摘要使用 `<compaction-summary>` 标签包裹
- 包含 7 个固定章节：Standing facts、Goal、Decisions、Files、Commands、Errors、Pending
- 压缩指令作为唯一新消息追加，保持前缀 KV cache 温暖

（F-050, F-051, F-052）

## Mid-turn Steer

`Steer(text)` 方法在 turn 执行中注入引导消息：

```go
func (a *Agent) Steer(text string) bool {
    return a.SteerItem("", func() (string, error) { return text, nil })
}
```

- 返回 `true` 表示活跃 turn 接受了文本
- 返回 `false` 时调用方需作为新 turn 投递
- steer 消息带 `[Mid-turn steer queued by the user...]` 前缀
- turn 结束时未消费的 steer 标记为 LocalOnly 并记录 warning

（F-024）

## 权限门

`Gate` 接口是 per-call 权限检查点：

```go
type Gate interface {
    Check(ctx context.Context, toolName string,
        args json.RawMessage, readOnly bool) (allow bool, reason string, err error)
}
```

nil gate 表示无门控——每个调用都运行。`SetGate` 支持运行时切换审批模式。（F-020）

## 相关概念

- [项目架构](01-project-architecture.md)——boot 如何组装 Agent
- [ACP 协议](03-acp-protocol.md)——ACP 如何驱动 Agent.Run
- [Checkpoint 与恢复](06-checkpoint-recovery.md)——Session 持久化和回滚
- [Fleet 与 Subagent](07-fleet-subagents.md)——scheduler 和并行 agent
