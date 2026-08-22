---
title: Agent运行时主循环
type: concept
module: "@deepseek-ai/dsh-agent-loop"
package: packages/core/agent-loop
related:
  - cordis-plugin-architecture
  - llm-abstraction-layer
  - session-and-context
  - tool-and-subagent
sources:
  - packages/core/agent-loop/src/agent.ts
  - packages/core/agent-loop/src/runtime-context.ts
  - packages/core/agent-loop/src/tool-calls.ts
  - packages/core/agent-loop/src/constants.ts
  - packages/core/agent/src/inbox.ts
  - packages/core/agent/src/types.ts
  - packages/core/agent/src/index.ts
---

# Agent运行时主循环

## 概述

Agent 运行时主循环是 deepseek-harness 的核心驱动引擎，实现了经典的 **ReAct（Reasoning + Acting）循环模式**，并在此基础上增加了多步连续推理（multi-step continuation）、工具并行调度、运行时上下文投影、维护任务锁、取消/恢复语义等增强能力。

默认实现 `ReactLoopAgent` 驱动一个 Session 通过 turn（轮次）和 step（步骤）边界：每个 turn 由一个或多个 step 组成，每个 step 对应一次 LLM 调用加上该调用请求的工具执行；当模型不再请求工具调用时 turn 结束；Inbox 中有排队消息时自动开启下一个 turn。

```mermaid
graph TB
    subgraph Driver[ReactLoopAgent Driver]
        Phase[Phase状态机<br/>idle/maintenance/running]
        Inbox[Inbox 双队列<br/>next-turn / next-step]
        Scope[Agent Scope<br/>作用域隔离]
        RTCtx[RuntimeContextProjection<br/>运行时上下文投影]
    end

    subgraph Loop[ReAct 循环]
        Turn[turn 边界<br/>turn/start → turn/end]
        PreStep[preStep<br/>声明消息+系统提示+waterfall]
        Step[step 执行<br/>LLM流式调用+BlockAssembler]
        ToolCalls[工具调度<br/>排他屏障+并行池]
    end

    subgraph Events[Waterfall 事件链]
        PreStepEvt[agent/pre-step]
        RequestEvt[agent/request]
        ReqErrEvt[agent/request-error]
        TurnStopEvt[agent/turn-stopping]
        StatusEvt[agent/status]
        ErrorEvt[agent/error]
    end

    subgraph Session[Session 事件日志]
        Events2[SessionEvent<br/>append-only log]
        Surface2[Surface<br/>消息投影]
        Msgs[deriveMessages()<br/>模型历史]
    end

    Inbox -->|claim| PreStep
    PreStep -->|waterfall| PreStepEvt
    PreStep -->|组装请求| RequestEvt
    RequestEvt -->|llm.stream| Step
    Step -->|BlockAssembler| Events2
    Step -->|tool-call blocks| ToolCalls
    ToolCalls -->|tool/result append| Events2
    Events2 -->|deriveMessages| Msgs
    Msgs -->|下一次LLM调用| Step

    Step -->|max-tokens| Turn
    Step -->|completed (无tool calls)| Turn
    Step -->|有next-step消息| Step

    Phase -->|状态转换| StatusEvt
    ToolCalls -->|scheduler error| ErrorEvt
    Step -->|请求错误| ReqErrEvt
    ReqErrEvt -->|retry决策| Step
    Turn -->|hasPending| Turn
```

## 设计原理

### 1. Phase 状态机

`ReactLoopAgent` 通过三态 Phase 管理驱动生命周期：

```typescript
// packages/core/agent-loop/src/agent.ts
type Phase =
  | { kind: 'idle'; lastTurn: number }                          // 空闲，等待唤醒
  | { kind: 'maintenance'; abort: AbortController;              // 执行维护任务（如手动压缩）
      lastTurn: number; wakeRequested: boolean }
  | { kind: 'running'; abort: AbortController;                  // 活跃运行中
      turn: number; step: number; wakeRequested: boolean }
```

状态转换规则：
- **idle → running**：`wakeDriver()` 被调用（收到唤醒消息或维护完成后有排队工作）
- **running → idle**：turn 循环自然结束（无排队消息）或驱动异常
- **idle → maintenance**：`runMaintenance()` 被调用（如手动 compaction）
- **maintenance → idle**：维护任务完成；若 `wakeRequested` 且 inbox 有待处理消息，立即唤醒新 turn
- **running → running**：turn 内 step 推进、AbortController 重置（取消后同 turn 内新step）

```typescript
setPhase(next: Phase): void {
  const previousStatus = this.status
  this.phase = next
  const status = this.status  // idle/maintenance → 'idle', running → 'running'
  if (status !== previousStatus) {
    this.dispatch.emit('agent/status', { status })  // 状态变化时发布事件
  }
}
```

`wakeDriver()` 处理非 idle 状态下的唤醒请求：维护中或已中止的驱动不能直接交付唤醒，而是通过 `wakeRequested` 锁存，待收敛时重放。

### 2. Inbox：双队列消息调度

`Inbox` 维护两个有序的待处理消息队列，其状态通过 `agent/inbox/spliced` 事件持久化到 Session 日志中：

```typescript
// packages/core/agent/src/types.ts & inbox.ts
type InboxTarget = 'next-turn' | 'next-step'

class Inbox {
  private readonly state: Record<InboxTarget, UserMessage[]> = {
    'next-turn': [],   // 等待独立 turn 的消息（用户followup）
    'next-step': [],   // 等待当前/下一个step边界注入的消息（steer、inject、工具结果上下文）
  }
}
```

三种消息投递方式：

| 方法 | 队列 | 唤醒 | 用途 |
|------|------|------|------|
| `followup(input)` | next-turn | 是 | 用户后续提问，开启新 turn |
| `steer(input)` | next-step | 是 | 干预当前/下一个 step（如重定向） |
| `inject(input)` | next-step | 否 | 注入上下文（文件变更通知、AGENTS.md等），不主动唤醒 |

Inbox 的变更通过 `splice()` 原子操作完成：
1. 验证 splice 参数合法性（位置、删除计数、消息ID不重复）
2. 追加 `agent/inbox/spliced` 事件到 Session（**在**投影变更**之前**，所以同步观察者能看到变更前列表）
3. 更新内存投影
4. 发布 `inserted`/`discarded`/`claimed` 通知

```typescript
// packages/core/agent/src/inbox.ts
private mutate(target, start, deleteCount, inserted, discardRemoved): UserMessage[] {
  // 1. 规范化参数
  // 2. 验证（ID不重复、边界合法）
  this.validate(splice)
  // 3. 先追加持久化事件
  const event = this.session.append('agent/inbox/spliced', splice)
  // 4. 再更新内存投影
  const removed = inbox.splice(actualStart, actualDeleteCount, ...event.data.inserted)
  // 5. 发布通知
  if (discardRemoved) for (const msg of removed) this.notifications.discarded(msg)
  for (const msg of event.data.inserted) this.notifications.inserted(msg)
  return removed
}
```

`claim(target, turn)` 在每个 step 边界原子地取出待处理消息：先取全部 next-step，再根据 target 决定是否取一条 next-turn。取走的消息发布 `claimed` 通知。

### 3. Turn/Step 双层循环

主循环采用嵌套结构：外层 `turn()` 管理 turn 边界，内层 `step()` 执行单次 LLM 调用+工具调度。

```typescript
// packages/core/agent-loop/src/agent.ts
private async kick(): Promise<void> {
  try {
    while (await this.turn()) {}  // 持续turn直到无待处理消息
  } catch (_error) {
    // 失败和取消在驱动边界内包含
  } finally {
    if (this.phase.kind === 'running') {
      const { turn, wakeRequested } = this.phase
      this.setPhase({ kind: 'idle', lastTurn: turn })
      if (wakeRequested && this.inbox.hasPending) this.wakeDriver()
    }
  }
}
```

#### Turn 生命周期

```typescript
private async turn(): Promise<boolean> {
  const turn = phase.turn + 1
  this.session.append('turn/start', { turn })     // 打开turn边界
  let turnEnds: TurnEndReason | null = null
  let target: InboxTarget = 'next-turn'
  try {
    while (true) {
      const step = phase.step + 1
      const decision = await this.preStep(target, { turn, step })
      if (decision.kind === 'reject') { turnEnds = { kind: 'blocked' }; return false }
      if (turnEnds && decision.messages.length === 0) break  // 无新消息，结束turn
      if (phase.step === 0 && decision.messages.length === 0) {
        turnEnds = { kind: 'completed' }; return false       // 空turn直接完成
      }
      this.session.append('step/start', { turn, step })
      try {
        for (const message of decision.messages) {
          this.session.append('user/message', message, { surfaceOp: 'append' })
        }
        const stepEnd = await this.step(decision.assembly)
        if (turnEnds === null || turnEnds.kind !== 'max-tokens') turnEnds = stepEnd
      } finally {
        this.session.append('step/end', { turn, step })
      }
      // 检查是否有next-step消息或turn结束
      if (turnEnds && this.inbox.nextStep.length === 0) {
        await this.dispatch.serial('agent/turn-stopping', { turn, signal })
      }
      if (turnEnds && this.inbox.nextStep.length === 0) break
      target = 'next-step'
    }
  } catch (error) {
    if (signal.aborted) {
      turnEnds = { kind: 'aborted', reason: signal.reason as AgentCancelCause }
      throw error  // 取消重新抛出，由kick()的finally处理
    }
    turnEnds = {
      kind: 'error',
      error: error instanceof LlmError ? error.failure : { message: errorChain(error), code: 'UNKNOWN' },
    }
    this.throwError(error)
  } finally {
    this.session.append('turn/end', { turn, reason: turnEnds! })  // 总是关闭turn
  }
  if (!this.inbox.hasPending) return false  // 无待处理消息，退出驱动
  phase.abort = new AbortController()       // 重置取消控制器
  phase.wakeRequested = false
  phase.step = 0
  return true  // 继续下一个turn
}
```

Turn 结束原因（`TurnEndReason`）：
- `completed`：模型完成回答（无更多工具调用）
- `max-tokens`：达到输出 token 上限（sticky：后续 completed step 不能降级此结果）
- `aborted`：被取消（用户/父agent/hook/disposed）
- `blocked`：pre-step 拒绝
- `error`：LLM 或工具执行错误
- `interrupted`：崩溃遗留的 turn 被恢复时关闭

#### Step 执行

```typescript
private async step(assembly: PromptAssembly): Promise<StepEndReason | null> {
  while (true) {
    // 1. 构建请求
    const { request, preparedCall } = await this.buildRequest(
      turn, step, assembly.tools, system, this.session.deriveMessages(), signal,
    )
    // 2. 流式调用LLM，逐chunk记录
    const assembler = new BlockAssembler()
    const chunkSeqs: number[] = []
    const stream = preparedCall?.stream(request) ?? this.loopCtx.llm.stream(request)
    for await (const chunk of stream) {
      chunkSeqs.push(this.session.append('assistant/chunk', { turn, step, chunk }).seq)
      assembler.push(chunk)
    }
    const finish = assembler.finish
    // 3. 错误处理与重试
    if (finish.kind === 'error' || finish.kind === 'aborted') {
      const action = await this.dispatch.waterfall('agent/request-error', { ... },
        () => Promise.resolve<RequestErrorAction>(undefined))
      if (action?.kind !== 'retry') throw new LlmError(...)
      continue  // retry：重新构建请求并重试
    }
    // 4. 提交assistant消息
    const message = createAssistantMessage({
      content: assembler.blocks(),
      source: { provider: request.provider, model: request.model, ... },
    })
    this.session.append('assistant/message',
      { turn, step, message, ...assembler.usage ? { usage: assembler.usage } : {} },
      { surfaceOp: 'append', sourceEventSeqs: chunkSeqs })
    if (finish.kind === 'max-tokens') return { kind: 'max-tokens' }
    // 5. 检查工具调用并调度
    const toolCalls = message.content.filter(block => block.type === 'tool-call')
    if (toolCalls.length === 0) return { kind: 'completed' }
    const { concluded } = await executeToolCalls(
      this.loopCtx, turn, step, toolCalls, signal,
      context => this.inbox.splice('next-step', this.inbox.nextStep.length, 0, [context]),
    )
    return concluded ? { kind: 'completed' } : null  // null表示继续下一个step
  }
}
```

关键设计点：
- **流式 chunk 实时记录**：每个 `StreamChunk` 立即 append 为 `assistant/chunk` 事件，支持token级重放
- **BlockAssembler 增量组装**：将流式 chunk 组装为完整的 content blocks
- **sourceEventSeqs 溯源**：`assistant/message` 引用其所有 chunk 的 seq
- **错误重试waterfall**：`agent/request-error` 允许插件（如compaction overflow recovery）决定重试
- **max-tokens 粘性**：一旦某 step 命中输出上限，后续 step 完成也不能将 turn 结果降级为 completed
- **工具后续上下文注入**：工具执行产生的 additionalContexts 注入到 next-step inbox

### 4. 请求构建与头部折叠

`buildRequest()` 是每个 step 的请求组装核心：

```typescript
private async buildRequest(turn, step, tools, system, boundaryMessages, signal) {
  const persistedHeader = session.requestHeader()
  // 1. 从持久化header或初始选项构建种子配置
  const seedConfig = deepFreeze(structuredClone(
    this.requestHeaderLogged
      ? requestProposal(persistedHeader!)  // 移除adapterDefaults，让插件重新提议
      : { provider: this.options.provider, model: this.options.model, ... }
  ))
  // 2. agent/request waterfall 允许插件修改配置
  const proposedConfig = await this.dispatch.waterfall(
    'agent/request', { turn, step, signal }, () => Promise.resolve(seedConfig))
  // 3. prepareCall 解析适配器默认值
  let preparedCall = await this.loopCtx.llm.prepareCall(proposedConfig, signal)
  let config = preparedCall.config
  // 4. 规范化header并决定是否需要追加request/header事件
  const header = canonicalHeader({ config, adapterDefaults, system, tools })
  const baseline = this.session.requestHeader()
  if (!this.requestHeaderLogged) {
    this.session.append('request/header', { header, reason: baseline === undefined ? 'initial' : 'resume' })
    this.requestHeaderLogged = true
  } else if (!headerEquals(baseline, header)) {
    this.session.append('request/header', { header, reason: 'change' })
  }
  // 5. 追加request/context（路由元数据变更时）
  // 6. 构建最终frozen请求
  const request = markAgentLoopRequest(deepFreeze({
    ...header.config, messages: boundaryMessages,
    ...header.system ? { system: header.system } : {},
    ...header.tools ? { tools: header.tools } : {},
    sessionId: this.session.id, signal,
  }))
  return { request, preparedCall }
}
```

请求头部采用增量折叠：
- `request/header` 事件记录完整快照（而非delta），最新快照重建请求状态
- `adapterDefaults` 标记哪些配置字段是适配器默认值（如 reasoningEffort、maxTokens），在下一次请求提议前被移除，允许插件重新决策
- `request/context` 事件记录路由元数据（contextWindow等），仅在变更时追加

### 5. 工具调用调度：排他屏障+并行池

`executeToolCalls` 实现了智能的工具并发调度：

```typescript
// packages/core/agent-loop/src/tool-calls.ts
export async function executeToolCalls(ctx, turn, step, toolCalls, signal, acceptContext) {
  const planned = toolCalls.map(block => ({
    block,
    exec: { callId: block.id, name: block.name, arguments: parseArguments(block.arguments), agent, signal },
  }))
  let next = 0
  let concluded = false
  while (next < planned.length) {
    const first = planned[next]!
    const mode = ctx.tools.executionMode(first.exec).kind  // 'exclusive' | 'parallel'
    const group = mode === 'parallel' ? planned.slice(next) : [first]
    const outcome = await runGroup(ctx, turn, step, group, mode, signal, acceptContext)
    next += outcome.consumed
    concluded ||= outcome.concluded
    if (outcome.aborted) {
      // 为未启动的调用记录合成错误结果
      for (const call of planned.slice(next)) appendSkippedToolCall(session, turn, step, call.block)
      return { concluded }
    }
  }
  return { concluded }
}
```

调度策略：
- **排他工具（exclusive）**：形成屏障——该工具必须单独执行，完成后才能调度后续调用
- **并行工具（parallel）**：尽可能与后续并行工具一起放入有界池（`maxParallelToolCalls`），直到遇到排他工具
- **运行时重分类**：每次启动前重新读取 executionMode，允许排他工具"打断"并行组（等待当前池排空后形成屏障）

```typescript
async function runGroup(ctx, turn, step, group, mode, signal, acceptContext) {
  const slots: (Slot | undefined)[] = group.map(() => undefined)
  let nextToStart = 0, committed = 0, started = 0, aborted = false, concluded = false

  // 按模型顺序提交结果：committed只在连续就绪slot上推进
  const commitReady = async () => {
    while (committed < group.length) {
      const slot = slots[committed]
      if (slot === undefined) break
      const result = slot.needsPost ? await finalize(slot.exec, slot.result) : finish(slot.exec, slot.result)
      appendToolResult(session, turn, step, call, result, callSeqs[committed]!)
      for (const context of result.additionalContexts ?? []) acceptContext(context)
      concluded ||= result.concludesTurn === true
      committed++
    }
  }

  // 填充并行池 + 等待完成
  await fillPool()  // 启动并行调用直到池满或遇到排他工具
  while (inFlight.size > 0) {
    const settledIndex = await Promise.race(inFlight.values())
    inFlight.delete(settledIndex)
    await commitReady()
    if (signal.aborted) aborted = true
    await fillPool()  // 补充新的并行调用
  }

  if (aborted) {
    for (const call of group.slice(started)) appendSkippedToolCall(session, turn, step, call.block)
    return { consumed: group.length, aborted: true, concluded }
  }
  return { consumed: started, aborted: false, concluded }
}
```

关键点：
- **结果按模型顺序提交**：即使并行执行，`tool/result` 事件按调用顺序追加，保证确定性
- **pre-execute/dispatch/post-execute 四阶段**：prepare→dispatch→post-result/final-result
- **中止时排干已启动调用**：AbortSignal 触发后，已启动的工具正常完成并记录结果，未启动的调用获得合成的 "aborted before dispatch" 结果
- **调度器故障处理**：内部错误停止新调度，排干已启动调用后抛出，不伪造结果
- **`concludesTurn`**：工具可标记结果导致 turn 立即结束（如用户主动结束）
- **`additionalContexts`**：工具可注入额外 UserMessage 到 next-step inbox（如文件变更通知）

### 6. 运行时上下文投影

`RuntimeContextProjection` 跟踪动态运行时上下文快照（如系统提示中的动态section），避免在每次step中无变化时重复追加上下文消息：

```typescript
// packages/core/agent-loop/src/runtime-context.ts
export class RuntimeContextProjection {
  private retained: { seq: number; text: string | undefined } | null | undefined

  constructor(ctx: Context, session: Session) {
    // 从session恢复：反向扫描找到最后一个仍在surface上的snapshot消息
    const surface = new Set(session.surface.nodes)
    for (let index = session.events.length - 1; index >= 0; index -= 1) {
      const event = session.events[index]
      if (event?.type !== 'user/message' || !isOwned(event.data)) continue
      this.retained ??= null
      if (surface.has(event.seq)) { this.retained = { seq: event.seq, text: textOf(event.data) }; break }
    }
    // 订阅session/event跟踪后续变更
    ctx.on('session/event', (subject, event) => {
      if (event.type === 'user/message' && isOwned(event.data)) {
        this.retained = { seq: event.seq, text: textOf(event.data) }  // 新snapshot
      } else if (this.retained && isReplacementSurfaceEvent(event)
        && event.sourceEventSeqs?.includes(this.retained.seq)) {
        this.retained = null  // compaction替换了snapshot，清除保留
      }
    })
  }

  project(current: string, sections: readonly ContextSnapshotSection[]): UserMessage | undefined {
    const snapshot = current.length === 0 ? CLEARED : current
    if (this.retained?.text === snapshot) return  // 无变化，不追加
    return createUserMessage({
      content: [{ type: 'text', text: snapshot }],
      source: { kind: 'plugin', plugin: SOURCE, form: 'snapshot', sections },
    })
  }
}
```

设计要点：
- **去重**：仅当渲染的上下文字符串与上次保留的不同时才生成新消息
- **清空标记**：空上下文使用特殊 CLEARED 文本，显式声明"之前的运行时上下文不再适用"
- **Compaction 感知**：当 compaction replace 阴影了保留的 snapshot，自动清除保留状态
- **可恢复**：构造时从 session 历史恢复投影状态，支持进程重启

### 7. Agent 作用域隔离

每个 `ReactLoopAgent` 在构造时创建自己的 Cordis Scope：

```typescript
this.scope = createScope(loopCtx, this)
this.ctx = this.scope.ctx.extend({ agent: this })
```

这实现了：
- **事件隔离**：通过 `scopeTarget`，agent-scoped 监听器只接收该 agent 进入的 session 的事件
- **注册隔离**：通过 `ScopedLayers`，agent 内注册的工具/服务在 agent dispose 时自动清理
- **发起者传播**：`ctx.agents.withInitiator(this, () => this.kick())` 设置当前发起 agent，工具执行可通过 `ctx.agents.requireInitiator()` 访问

### 8. Waterfall 事件扩展点

Agent 循环通过多个 waterfall/serial/emit 事件暴露扩展点：

| 事件 | 模式 | 用途 |
|------|------|------|
| `agent/pre-step` | waterfall | 拦截/修改step输入，决定enter/reject/skip |
| `agent/request` | waterfall | 修改LLM请求配置（provider/model/参数） |
| `agent/request-error` | waterfall | 请求错误处理，决定retry或抛出 |
| `agent/turn-stopping` | serial | turn即将结束时的串行处理（如checkpoint flush） |
| `agent/status` | emit | 状态变化通知（idle/running） |
| `agent/error` | emit | 错误报告 |
| `agent/inbox/inserted` | emit | 消息插入inbox通知 |
| `agent/inbox/discarded` | emit | 消息被取消通知 |
| `agent/inbox/claimed` | emit | 消息被step认领通知 |

### 9. 取消语义

`cancel(cause, options?)` 提供灵活的取消控制：

```typescript
cancel(cause: AgentCancelCause, options: CancelOptions = {}): void {
  if (!options.keepInbox) {
    this.inbox.clear()                              // 清空待处理消息
    if (this.phase.kind !== 'idle') this.phase.wakeRequested = false  // 清除锁存的唤醒
  }
  if (this.phase.kind !== 'idle') this.phase.abort.abort(cause)  // 中止当前活动
}
```

取消原因（`AgentCancelCause`）：
- `{ kind: 'user' }`：用户主动取消
- `{ kind: 'parent' }`：父 agent 取消
- `{ kind: 'hook'; reason: string }`：hook 拦截取消
- `{ kind: 'disposed' }`：作用域被 dispose

取消后的保证：
- 正在执行的 LLM 流式调用被中断
- 已启动的工具调用排干（完成并记录结果）
- 未启动的工具调用获得合成的 abort 结果
- turn 以 `{ kind: 'aborted', reason }` 关闭
- `keepInbox: true` 时保留待处理消息（用于非破坏性中断）

### 10. 维护任务锁

`runMaintenance(job)` 允许在 idle 状态下执行独占维护任务（如手动 compaction），防止驱动和维护操作并发：

```typescript
runMaintenance<T>(job: (signal: AbortSignal) => Promise<T>): Promise<T> {
  if (this.phase.kind !== 'idle') throw new Error('agent already has active work')
  const maintenance: Phase = {
    kind: 'maintenance', abort: new AbortController(),
    lastTurn: this.phase.lastTurn, wakeRequested: false,
  }
  this.setPhase(maintenance)
  return (async () => {
    try { return await job(maintenance.abort.signal) }
    finally {
      this.setPhase({ kind: 'idle', lastTurn: maintenance.lastTurn })
      if (maintenance.wakeRequested && this.inbox.hasPending) this.wakeDriver()
    }
  })()
}
```

维护期间到达的唤醒消息通过 `wakeRequested` 锁存，维护完成后自动唤醒新 turn。

## 类型签名速查

```typescript
// === ReactLoopAgent ===
class ReactLoopAgent implements Agent {
  readonly id: SessionId
  readonly options: AgentOptions
  readonly session: Session
  readonly inbox: Inbox
  readonly scope: Scope
  readonly ctx: Context
  readonly status: AgentStatus  // 'idle' | 'running'

  send(message: UserMessage, target: InboxTarget, wakeup: boolean): void
  followup(input: UserMessage): void     // → next-turn, wake
  steer(input: UserMessage): void        // → next-step, wake
  inject(input: UserMessage): void       // → next-step, no wake
  cancel(cause: AgentCancelCause, options?: CancelOptions): void
  runMaintenance<T>(job: (signal: AbortSignal) => Promise<T>): Promise<T>
  whenIdle(): Promise<void>
}

// === Inbox ===
class Inbox {
  readonly nextTurn: readonly UserMessage[]
  readonly nextStep: readonly UserMessage[]
  readonly hasPending: boolean
  claim(target: InboxTarget, turn: number): UserMessage[]
  splice(target, start, deleteCount, inserted): UserMessage[]
  append(target: InboxTarget, message: UserMessage): void
  prepend(target: InboxTarget, message: UserMessage): void
  replace(messageId: MessageId, newMessage: UserMessage): boolean
  remove(messageId: MessageId): boolean
  clear(): void
}

// === 关键事件类型 ===
type AgentStatus = 'idle' | 'running'
type InboxTarget = 'next-turn' | 'next-step'
type PreStepDecision =
  | { kind: 'enter'; messages: UserMessage[] }
  | { kind: 'reject' }
  | { kind: 'skip' }
type RequestErrorAction = { kind: 'retry' } | undefined
type TurnEndReason =
  | { kind: 'completed' }
  | { kind: 'max-tokens' }
  | { kind: 'aborted'; reason: TurnEndCancelCause }
  | { kind: 'blocked' }
  | { kind: 'error'; error: LlmFailure }
  | { kind: 'interrupted' }
```

## 源码链接

- ReactLoopAgent 主循环实现：[agent.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/deepseek-harness/packages/core/agent-loop/src/agent.ts)
- 运行时上下文投影：[runtime-context.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/deepseek-harness/packages/core/agent-loop/src/runtime-context.ts)
- 工具调用调度器：[tool-calls.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/deepseek-harness/packages/core/agent-loop/src/tool-calls.ts)
- Inbox 双队列实现：[inbox.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/deepseek-harness/packages/core/agent/src/inbox.ts)
- Agent 类型定义：[types.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/deepseek-harness/packages/core/agent/src/types.ts)
- Agent 注册与事件声明：[index.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/deepseek-harness/packages/core/agent/src/index.ts)
