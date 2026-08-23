---
title: 会话与上下文管理
type: concept
module: "@deepseek-ai/dsh-session"
package: packages/core/session
related:
  - cordis-plugin-architecture
  - llm-abstraction-layer
  - agent-runtime-loop
  - acp-agent-protocol
sources:
  - packages/core/session/src/index.ts
  - packages/core/session/src/types.ts
  - packages/core/session/src/surface.ts
  - packages/core/scope/src/index.ts
  - packages/core/scope/src/store.ts
  - packages/compaction/compaction/src/index.ts
  - packages/compaction/compaction/src/types.ts
  - packages/compaction/compaction-basic/src/index.ts
---

# 会话与上下文管理

## 概述

会话（Session）是 deepseek-harness 中 Agent 交互的持久化真相源（Source of Truth）。它采用**事件溯源**（Event Sourcing）模式：所有对话状态变化以追加写入（append-only）的不可变事件序列记录，而非维护可变的状态对象。会话之上构建了两层关键抽象：

1. **Surface（表面层）**：从事件日志中投影（project）出模型可见的消息序列，支持通过 `surfaceOp` 标记实现历史替换（compaction）。
2. **Scope（作用域层）**：基于 Cordis Context 的父子嵌套路由机制，实现多 Agent 组合下的事件隔离与向上传播。

此外，**Compaction（上下文压缩）** 系统通过 Surface 的 replace 机制将历史消息摘要化，解决长对话上下文窗口溢出问题。

```mermaid
graph TB
    subgraph Session[Session 事件溯源会话]
        Log[(Append-only Log<br/>SessionEvent[])]
        Header[SessionHeader<br/>元数据]
        Snapshot[events snapshot<br/>deep-frozen]
    end

    subgraph Surface[Surface 表面投影层]
        Manager[SurfaceManager<br/>有序节点视图]
        Nodes[nodes: seq[]<br/>模型可见序列]
        Replace[replace 操作<br/>阴影替换]
    end

    subgraph Scope[Scope 作用域路由]
        Key[ScopeKey<br/>不透明标识]
        Chain[scopeChain<br/>父子链]
        Carrier[Scoped carrier<br/>事件路由]
    end

    subgraph Compaction[Compaction 上下文压缩]
        Engine[CompactionEngine<br/>抽象服务]
        Basic[BasicCompactionEngine<br/>LLM摘要实现]
        Pruner[toolResultPruner<br/>工具结果修剪]
    end

    Log -->|deriveMessages| Manager
    Log -->|append| Manager
    Manager --> Nodes
    Manager --> Replace
    Replace --> Nodes

    Carrier -->|scopeTarget| Key
    Key -->|bindScopeParent| Chain
    Chain -->|事件向上传播| Carrier

    Engine -->|compactRegion| Replace
    Basic -->|extends| Engine
    Pruner -->|model-free prune| Replace
```

## 设计原理

### 1. 事件溯源：追加日志作为唯一真相源

`Session` 不是 Service，而是一个纯数据类。其核心是 `private log: SessionEvent[]`，所有操作（用户消息、助手回复、工具调用、turn 边界等）都通过 `append()` 追加到日志末尾。一旦事件进入日志，它就是深冻结（`deepFreeze`）的，任何 JavaScript 代码都无法篡改已提交的历史。

```typescript
// packages/core/session/src/index.ts
export class Session {
  private log: SessionEvent[] = []
  private eventsSnapshot: readonly SessionEvent[] | undefined

  /** 不可变快照：事件进入日志后深冻结 */
  get events(): readonly SessionEvent[] {
    this.eventsSnapshot ??= Object.freeze([...this.log])
    return this.eventsSnapshot
  }

  /** 下一个事件的序号 —— 始终等于日志长度（seq = log.length 连续性契约） */
  get seq(): number {
    return this.log.length
  }
}
```

追加操作遵循严格的不变量：
- **序号连续**：`seq = log.length`，每个事件的 seq 与其在数组中的索引严格相等
- **JSON无损**：事件 data 必须是 lossless-JSON 可序列化的（拒绝 BigInt、函数、Symbol、循环引用、Map/Set/Date 等）
- **单次递归验证**：`snapshotJsonValue` 一次遍历完成复制、验证和冻结，防止 getter 状态攻击
- **不可重入**：append 过程中禁止再次 append，防止发布边界内递归导致状态不一致

### 2. Surface：模型可见历史的有序投影

原始事件日志包含大量模型不可见的事件（turn/step 边界、raw chunks、todo/write、request/header、compaction 标记等）。**Surface** 是从日志中投影出的、仅包含模型消息的有序视图，是 `deriveMessages()` 的唯一来源。

Surface 通过每个消息产生型事件上的 `surfaceOp` 标记来维护有序节点序列：

```typescript
// packages/core/session/src/types.ts
/** 表面操作类型 */
export type SurfaceOp =
  | 'append'                                        // 追加到尾部
  | { op: 'replace'; start: number; end: number }   // 替换区间 [start, end]

/** 可进入 Surface 的事件类型（仅三种消息事件） */
export type SurfaceEventType =
  | 'user/message'
  | 'assistant/message'
  | 'tool/result'
```

`SurfaceManager` 增量维护有序节点列表：

```typescript
// packages/core/session/src/surface.ts
export class SurfaceManager implements SessionSurface {
  private _state = { nodes: [] as number[], replaceGeneration: 0 }

  /** 当前表面的事件序号序列（模型可见顺序） */
  get nodes(): readonly number[] {
    if (this._lastProcessedSeq < this.baseSeq + this.log.length - 1)
      this._processDelta()
    return this._state.nodes
  }

  /** 位置替换的单调计数，用于缓存失效 */
  get replaceGeneration(): number { /* ... */ }

  /** 验证下一个候选事件（在其进入日志前），失败则 append 抛错 */
  validateNext(event: SessionEvent): void { /* ... */ }
}
```

消息投影规则是纯函数 `deriveEventMessage`：

```typescript
// packages/core/session/src/surface.ts
export function deriveEventMessage(event: SessionEvent): Message | null {
  switch (event.type) {
    case 'user/message': return event.data           // 用户消息原样投影
    case 'assistant/message':
      if (event.data.message.content.length === 0) return null  // 空内容（仅usage）跳过
      return event.data.message
    case 'tool/result': return event.data.message    // 工具结果投影
    default: return null                             // 其他事件（边界/chunk/log-only）不产生消息
  }
}
```

### 3. 增量折叠缓存

Session 维护三类增量缓存，均采用"首次读取时折叠新事件"的策略：

| 缓存 | 来源 | 失效条件 |
|------|------|----------|
| `headerFold` | `request/header` 事件 | 新事件追加 |
| `contextFold` | `request/context` 事件 | 新事件追加 |
| `derived` (messages) | Surface 节点投影 | `replaceGeneration` 变化或新节点追加 |

```typescript
// packages/core/session/src/index.ts — 派生消息的增量缓存
deriveMessages(): Message[] {
  const surface = this.surface
  const generation = surface.replaceGeneration
  if (generation !== this.derivedGeneration) {
    this.derived = []           // replace 发生时重建缓存
    this.derivedNodes = 0
    this.derivedGeneration = generation
  }
  for (const seq of surface.nodes.slice(this.derivedNodes)) {
    const msg = this.deriveEventMessage(this.log[seq]!)
    if (msg) this.derived.push(msg)
  }
  this.derivedNodes = surface.nodes.length
  return [...this.derived]      // 每次返回新数组快照，但 Message 对象共享且冻结
}
```

### 4. 事件类型体系

`SessionEventMap` 是可通过声明合并不断扩展的事件映射表，核心事件类型：

```typescript
// packages/core/session/src/types.ts（核心事件摘录）
export interface SessionEventMap {
  // Turn/Step 生命周期边界（log-only，不进入 Surface）
  'turn/start': { turn: number }
  'turn/end': { turn: number; reason: TurnEndReason }
  'step/start': { turn: number; step: number }
  'step/end': { turn: number; step: number }

  // 消息事件（Surface-eligible，必须携带 surfaceOp）
  'user/message': UserMessage
  'assistant/chunk': { turn: number; step: number; chunk: StreamChunk }  // log-only
  'assistant/message': { turn: number; step: number; message: AssistantMessage; usage?: TokenUsage }
  'tool/call': { turn: number; step: number; callId: CallId; name: string; arguments: string }  // log-only
  'tool/result': { turn: number; step: number; message: ToolResultMessage; error?: {...}; meta?: JsonValue }

  // 请求状态（log-only）
  'request/header': { header: EpochHeader; reason: RequestHeaderReason }
  'request/context': RequestContext
  'todo/write': { todos: TodoItem[] }

  // Seed 边界标记（log-only）
  'session/end-seed': Record<string, never>

  // Compaction 标记（通过声明合并扩展，log-only）
  // 'compaction/start', 'compaction/summary', 'compaction/end', 'compaction/prune'
}
```

每个事件的可忽略性由 `ignorable` 字段控制：
- **无 ignorable**（默认）：必需事件。旧版本 runtime 遇到未知类型必须拒绝恢复，防止静默丢失关键状态
- **`ignorable: true`**：可忽略事件。纯信息性记录，丢失不影响重建正确性

### 5. SessionStore：内存存储与生命周期管理

`SessionStore` 是 Cordis Service（`ctx.sessions`），负责 Session 的创建、发布、销毁和持久化协调。它采用**三阶段生命周期**：`prepare` → `enter` → `announce`，确保创建过程的原子性和可回滚性：

```typescript
// packages/core/session/src/index.ts
export class SessionStore extends Service {
  private store = new Map<SessionId, SessionEntry>()

  /** 便捷方法：prepare + enter + announce 一步完成 */
  create(id?: SessionId, options?: CreateSessionOptions): Session {
    const session = this.prepare(id, options)
    this.ctx.effect(function* (this: SessionStore) {
      yield this.enter(session)    // 先 detach disposer
      this.announce(session)       // 再 announce（listener 抛错则自动回滚）
    }.bind(this), 'sessions.create()')
    return session
  }

  /** 阶段1：构建但不进入存储（用于复合生命周期场景，如 agent 工厂） */
  prepare(id?: SessionId, options?: PrepareSessionOptions): Session { /* ... */ }

  /** 阶段2：进入存储，安装发布钩子，返回 detach disposer */
  enter(session: Session): () => void { /* ... */ }

  /** 阶段3：发布 session/created 事件，失败自动回滚 */
  announce(session: Session): void { /* ... */ }

  /** 等待所有持久化监听器完成 */
  async flush(session: Session): Promise<boolean> { /* ... */ }

  /** 从活跃会话 fork 出子会话 */
  fork(source: SessionForkSource, boundary?: number, childSessionId?: SessionId): Session { /* ... */ }
}
```

四个关键事件驱动持久化插件：

| 事件 | 模式 | 用途 |
|------|------|------|
| `session/created` | emit（同步） | 同步抛错可否决创建，触发回滚 |
| `session/event` | emit（提交后） | 追加提交后的 fire-and-forget 通知，失败不影响已提交事件 |
| `session/flush` | parallel（等待） | 持久化检查点，等待所有监听器完成 |
| `session/disposed` | emit | 销毁通知，含创建回滚时的配对触发 |

### 6. Scope：作用域路由与事件隔离

Scope 是基于 Cordis Fiber 的轻量级上下文隔离原语。它通过一个不透明的 `ScopeKey`（普通对象，身份比较）标记 Context，并构建父子链实现：
- **注册继承向下**：子 scope 看到祖先的层（ScopedLayers）
- **事件准入向上**：祖先 scope 的监听器接收后代的事件

```typescript
// packages/core/scope/src/index.ts
/** 创建一个 scoped context */
export function createScope(ctx: Context, key: ScopeKey, options?: CreateScopeOptions): Scope {
  if (options?.parent !== undefined) bindScopeParent(key, options.parent)
  const fiber = ctx.plugin(scope)
  const scoped: Context = fiber.ctx.extend({ [kScope]: key })
  return {
    ctx: scoped,
    rawDispose: fiber.dispose,
    dispose: () => (disposing ??= quiesceFiber(fiber)),
  }
}

/** 构建 scoped 事件载体（carrier）：保留原始 filter，加上 scope 链路由 */
export function scopeTarget<T extends object>(base: T, key: ScopeKey | undefined): Scoped<T> {
  const carrier = {
    [CordisContext.filter](ctx: Context): boolean {
      if (baseFilter?.(ctx) === false) return false
      const tag = scopeOf(ctx)
      if (tag === undefined) return true  // 无 tag 的监听器全局接收
      // 沿父链向上匹配：祖先接收后代事件
      for (let cursor = key; cursor !== undefined; cursor = scopeParents.get(cursor)) {
        if (cursor === tag) return true
      }
      return false  // 子 scope 不接收祖先/兄弟事件
    },
  }
  return carrier as unknown as Scoped<T>
}
```

Session 在 enter 时绑定 scope：
```typescript
// packages/core/session/src/index.ts enter()
const carrier = scopeTarget(session, scopeOf(this.ctx))
```

`ScopedLayers` 提供分层注册表存储，支持全局层 + scope 链叠加：

```typescript
// packages/core/scope/src/store.ts
export class ScopedLayers<L extends ScopeLayer> {
  readonly global: L                           // 全局层（始终存在）
  private readonly scoped = new Map<ScopeKey, L>()  // 各 scope 的覆盖层

  /** 合并全局 + scope 链上的命名条目，最近 scope 覆盖同名项 */
  merge<V>(scope: ScopeKey | undefined, pick: (layer: L) => NamedEntries<V>): Map<string, V> {
    const merged = new Map(pick(this.global).entries())
    for (const layer of this.chainLayers(scope)) {          // 祖先先，最近后
      for (const [name, value] of pick(layer).entries())
        merged.set(name, value)                             // 后者覆盖前者
    }
    return merged
  }
}
```

### 7. SessionHeader：持久化元数据

`SessionHeader` 存储在事件日志之外（不参与对话重建），包含格式版本、创建时间、工作目录、fork 谱系、委托深度等持久化元数据：

```typescript
// packages/core/session/src/types.ts
export interface SessionHeader {
  readonly version: number            // SESSION_FORMAT_VERSION，加载时校验
  readonly id: SessionId              // 会话标识
  readonly createdAt: number          // 创建时间（epoch ms）
  readonly cwd?: string               // 绝对工作目录
  readonly parentSession?: SessionId  // fork 父会话
  readonly seedLength?: number        // seed 继承长度
  readonly origin?: 'subagent'        // 子 Agent 来源标记
  readonly delegationDepth?: number   // 委托深度（递归预算）
  readonly agentPreset?: string       // Agent 预设 ID
}
```

格式版本 `SESSION_FORMAT_VERSION = 0` 采用单调整数策略：仅当旧 runtime 无法正确读取新日志时才 bump（如 header 结构变化、Surface 机制变更、核心事件语义变化），普通事件类型增加不 bump（由 `ignorable` 字段覆盖）。

### 8. Fork：会话分叉

`SessionStore.fork()` 支持从活跃会话的稳定前缀分叉出子会话：

```typescript
fork(source: SessionForkSource, boundary?: number, childSessionId?: SessionId): Session
```

约束：
- `boundary` 为源事件的 seq（包含），省略则取最后一个事件
- 分叉点必须在 turn 边界（`turn/start` 或 `turn/end`），不能在开放 turn 内部
- 子会话的 header 自动设置 `parentSession` 和 `seedLength`
- 分叉失败返回 `SessionForkError`，错误码包括 `SESSION_NOT_FOUND`、`INVALID_BOUNDARY`、`OPEN_TURN` 等

### 9. Compaction：上下文压缩

Compaction 系统解决长对话导致的上下文窗口溢出问题。它利用 Surface 的 `replace` 操作，将一段历史表面节点替换为单个摘要节点。

抽象服务定义：

```typescript
// packages/compaction/compaction/src/index.ts
export abstract class CompactionEngine extends Service {
  /** 自动压缩：在 pressure（步间压力）或 context-overflow（模型报错）时触发 */
  abstract compactIfNeeded(
    agent: CompactionAgentContext,
    trigger: CompactionTrigger,
    signal: AbortSignal,
  ): Promise<CompactionResult | null>

  /** 手动压缩：idle 时强制执行，必须先获取维护锁 */
  abstract compactNow(
    agent: ManualCompactAgentContext,
    signal: AbortSignal,
    sourceCommandId?: CommandId,
  ): Promise<CompactionResult | null>

  /** 强制压缩指定表面区间 */
  abstract compactRegion(
    start: number, end: number,
    agent: CompactionAgentContext,
    signal?: AbortSignal,
  ): Promise<CompactionResult>
}
```

`BasicCompactionEngine` 是默认实现，采用两阶段策略：

1. **模型无关修剪（Prune）**：先调用可选的 `toolResultPruner` 修剪冗余工具结果，重新测量 token
2. **LLM 摘要（Summarize）**：选择可压缩区间，用 LLM 生成摘要，通过 replace 提交到 Surface

```typescript
// packages/compaction/compaction-basic/src/index.ts（自动压缩核心逻辑）
override async compactIfNeeded(agent, trigger, signal): Promise<CompactionResult | null> {
  const target = routedTarget(agent.session)
  const policy = resolveTargetPolicy(this.config, target)
  let measurement = meter.measure(agent.session)

  // 1. 先尝试模型无关修剪
  if (prune !== undefined) {
    prune.pruneSession(agent.session)
    measurement = meter.measure(agent.session)
  }

  // 2. 仍超阈值则进行摘要压缩，支持重试
  for (let attempt = 0; attempt <= spec.compactionRetries; attempt++) {
    const range = selectCompactableRange(agent.session, measurement, spec.retainTokens)
    if (range === null) return result  // 无可压缩区间
    result = await this.compactRegion(range.start, range.end, agent, signal)
    measurement = meter.measure(agent.session)
    if (measurement.totalTokens < spec.thresholdTokens) return result
  }
}
```

Compaction 事务通过三对 log-only 事件标记，不进入 Surface：

```typescript
// packages/compaction/compaction/src/types.ts（声明合并到 SessionEventMap）
'compaction/start': { compactionId: CompactionId; sourceCommandId?: CommandId; turn: number | null }
'compaction/summary': {
  compactionId: CompactionId; summary: ContentBlock[];
  shadowedRange: { start: number; end: number };
  shadowedSeqs: number[]; shadowedTokenCount: number;
  provider: string; model: string; usage?: TokenUsage;
  // ...
}
'compaction/end': { compactionId: CompactionId; error?: string }
'compaction/prune': { shadowedRange: {...}; shadowedSeqs: number[]; shadowedTokenCount: number }
```

压缩后的摘要通过紧跟 `compaction/summary` 的一个 `user/message` 事件（带 `surfaceOp: { op: 'replace', start, end }`）实际执行表面替换。这种"标记事件 + 替换消息"的分离设计确保：
- 压缩过程可审计（`compaction/*` 事件记录完整元数据）
- 摘要对模型可见（作为 user/message 进入 Surface）
- 原始事件仍保留在日志中（人类可读 transcript 使用 append-origin 事件，不受替换影响）

### 10. 工具配对平衡约束

Compaction 的区间选择必须满足**工具配对平衡**（Tool Pairing Balance）：`assistant/message` 中的工具调用必须与其 `tool/result` 成对出现在压缩区间内或外，不能切断配对。

```typescript
// packages/compaction/compaction/src/tool-pairing.ts
export function toolPairingBalancedBefore(
  events: readonly SessionEvent[], end: number,
): boolean { /* 检查从起点到 end 之间工具调用是否全部配对 */ }

export function toolPairingBalancedAfter(
  events: readonly SessionEvent[], start: number,
): boolean { /* 检查从 start 到终点之间工具调用是否全部配对 */ }
```

### 11. 修复与恢复

`repair.ts` 提供中断 turn 的修复能力，处理崩溃/中断后的会话恢复。`TOOL_NOT_STARTED` 和 `TOOL_OUTCOME_UNKNOWN` 是工具调用的特殊状态标记，用于在恢复时正确处理未完成的工具调用。

```typescript
// packages/core/session/src/repair.ts（导出常量）
export const TOOL_NOT_STARTED = 'tool-not-started'
export const TOOL_OUTCOME_UNKNOWN = 'tool-outcome-unknown'
export const interruptedTurnClosers: TurnEndReason[] = [
  { kind: 'interrupted' },
  { kind: 'aborted', reason: { kind: 'disposed' } },
]
```

## 类型签名速查

```typescript
// === Session ===
class Session {
  readonly header: SessionHeader
  readonly id: SessionId
  readonly firstLiveSeq: number
  readonly events: readonly SessionEvent[]
  readonly seq: number
  readonly surface: SessionSurface

  static create(id: SessionId, seed?: readonly SessionEvent[], header?: SessionHeader): Session
  static fromRestore(id: SessionId, seed: readonly SessionEvent[], header: SessionHeader): Session

  append<T extends SessionEventType>(
    type: T, data: SessionEventMap[T],
    ...opts: T extends SurfaceEventType ? [opts: SurfaceIntent] : []
  ): SessionEvent<T>

  requestHeader(): EpochHeader | undefined
  requestContext(): RequestContext | undefined
  deriveMessages(): Message[]
  deriveEventMessage(event: SessionEvent): Message | null
}

// === SessionStore ===
class SessionStore extends Service {
  create(id?: SessionId, options?: CreateSessionOptions): Session
  prepare(id?: SessionId, options?: PrepareSessionOptions): Session
  enter(session: Session): () => void
  announce(session: Session): void
  async flush(session: Session): Promise<boolean>
  get(id: SessionId): Session | undefined
  list(): Session[]
  fork(source: SessionForkSource, boundary?: number, childSessionId?: SessionId): Session
}

// === Scope ===
type ScopeKey = object
type Scoped<T extends object> = object & { readonly [ScopedBrand]: T }
interface Scope { ctx: Context; rawDispose: () => Promise<void> | void; dispose(): Promise<void> }

function createScope(ctx: Context, key: ScopeKey, options?: { parent?: ScopeKey }): Scope
function scopeOf(ctx: Context): ScopeKey | undefined
function scopeTarget<T extends object>(base: T, key: ScopeKey | undefined): Scoped<T>
function bindScopeParent(key: ScopeKey, parent: ScopeKey): ScopeParentBinding
function scopeChainOf(key: ScopeKey | undefined): ScopeKey[]

// === Compaction ===
abstract class CompactionEngine extends Service {
  abstract compactIfNeeded(agent, trigger, signal): Promise<CompactionResult | null>
  abstract compactNow(agent, signal, sourceCommandId?): Promise<CompactionResult | null>
  abstract compactRegion(start, end, agent, signal?): Promise<CompactionResult>
}

interface CompactionResult {
  compactionId: CompactionId
  startSeq: number; summarySeq: number; endSeq: number
  summary: ContentBlock[]
  shadowedRange: { start: number; end: number }
  shadowedSeqs: number[]
  shadowedTokenCount: number
}
```

## 源码链接

- Session 类与 SessionStore：[index.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/deepseek-harness/packages/core/session/src/index.ts)
- 事件类型与 SessionHeader：[types.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/deepseek-harness/packages/core/session/src/types.ts)
- Surface 投影层：[surface.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/deepseek-harness/packages/core/session/src/surface.ts)
- Scope 核心：[index.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/deepseek-harness/packages/core/scope/src/index.ts)
- ScopedLayers 存储：[store.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/deepseek-harness/packages/core/scope/src/store.ts)
- Compaction 抽象服务：[index.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/deepseek-harness/packages/compaction/compaction/src/index.ts)
- Compaction 类型与事件：[types.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/deepseek-harness/packages/compaction/compaction/src/types.ts)
- BasicCompactionEngine 实现：[index.ts](file:///d:/spaces/SpecWeave/external/libs/models/ai/deepseek-harness/packages/compaction/compaction-basic/src/index.ts)
