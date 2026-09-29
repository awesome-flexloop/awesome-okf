---
type: Example
title: 构建 Agent 主循环
description: 学习 DeepSeek Harness 的 ReactLoopAgent 状态机、Inbox 消息队列、Turn-Step 执行循环、以及如何通过编程方式创建 Agent、发送消息、监控状态和处理事件。
tags:
  - agent-loop
  - react-loop
  - inbox
  - turn-step
  - phase
  - state-machine
  - lifecycle
related:
  - create-cordis-plugin
  - define-custom-tool
  - connect-mcp-server
sources:
  - packages/core/agent-loop/src/agent.ts
  - packages/core/agent/src/index.ts
  - packages/core/agent/src/runtime-types.ts
  - packages/core/agent/src/inbox.ts
  - packages/boot/app-boot/src/index.ts
---

# 构建 Agent 主循环

## 场景说明

DeepSeek Harness 的核心是 **ReactLoopAgent**——一个基于「感知-思考-行动-观察」（Think-Act-Observe）循环的 Agent 驱动引擎。每个 Agent 拥有独立的会话（Session）、消息收件箱（Inbox）、作用域上下文（Scope）和状态机（Phase）。Agent 循环管理 LLM 调用、工具执行、消息分发和生命周期事件。本示例深入讲解：

- Agent 的三态状态机（idle → running → maintenance → idle）
- Inbox 消息队列与消息目标（next-turn / next-step）
- Turn-Step 循环结构（一轮对话包含多个执行步骤）
- 四种消息投递方式：`send` / `followup` / `steer` / `inject`
- 通过 `ctx.agents.create()` 编程式创建 Agent
- 事件监听与状态监控
- 取消执行与维护任务

## 完整代码示例

### 示例 1：编程式创建 Agent 并发送消息

```typescript
/**
 * 演示如何在已启动的 Cordis 上下文中创建 Agent、发送消息并观察生命周期。
 * 前提：已通过 boot() 加载了必要的插件（llm-deepseek、tools、agent-loop 等）。
 */

import type { Context } from '@deepseek-ai/cordis'
import type { Agent, AgentStatus, UserMessage } from '@deepseek-ai/dsh-agent'
import { randomUUID } from 'node:crypto'

/**
 * 创建一个新 Agent 并发送第一条消息。
 * @param ctx - 已启动的 Cordis 根上下文（来自 boot() 的返回值）
 * @param userMessage - 用户第一条消息文本
 * @param cwd - Agent 的工作目录
 * @returns Agent 句柄（包含 agent 实例和 dispose 方法）
 */
async function createAgentAndChat(
  ctx: Context,
  userMessage: string,
  cwd: string = process.cwd(),
): Promise<{ agent: Agent; dispose: () => Promise<void> }> {
  const sessionId = `session-${randomUUID()}`

  // ---- 1. 通过 AgentRegistry 创建 Agent ----
  // ctx.agents.create() 会：
  //   a. 创建 Session（持久化会话日志）
  //   b. 在 Agent 作用域内执行 setup 回调（注册作用域工具/监听器等）
  //   c. 注册 Agent 到注册表
  //   d. 启动驱动循环（但等待消息才开始执行）
  const handle = await ctx.agents.create({
    sessionId,
    meta: {
      cwd,                      // Agent 的工作目录（绝对路径）
      origin: undefined,         // 非子 Agent，顶层 Agent
      delegationDepth: 0,        // 委托深度
    },
    agentOptions: {
      provider: 'deepseek-official',  // LLM 提供商标识
      model: 'deepseek-v4-flash',     // 模型 ID
      maxTokens: 8192,                // 每步最大输出 token
    },
    // setup 回调在 Agent 发布前执行，此时 agentCtx 是未发布的作用域上下文
    // 可以注册作用域工具、监听器、prompt section 等
    setup(agentCtx) {
      // 注册一个仅对该 Agent 可见的工具示例
      // agentCtx.tools.register(...)

      // 监听该 Agent 的状态变化
      agentCtx.on('agent/status', ({ status }) => {
        console.log(`[Agent ${sessionId.slice(0, 8)}] status → ${status}`)
      })

      // 监听错误
      agentCtx.on('agent/error', ({ turn, step, error }) => {
        console.error(`[Agent ${sessionId.slice(0, 8)}] error at turn ${turn}, step ${step}:`, error)
      })

      // 监听收件箱消息
      agentCtx.on('agent/inbox/inserted', ({ message }) => {
        const preview = typeof message.content === 'string'
          ? message.content.slice(0, 80)
          : JSON.stringify(message.content).slice(0, 80)
        console.log(`[Agent ${sessionId.slice(0, 8)}] inbox +: ${preview}...`)
      })
    },
  })

  const agent = handle.agent

  // ---- 2. 构造用户消息 ----
  // UserMessage 是 Agent 接收的外部消息类型
  const message: UserMessage = {
    role: 'user',
    content: userMessage,
    // 可选字段：
    // source: { type: 'cli' | 'api' | 'webhook' | ... }  -- 消息来源
    // attachments: [...]                                   -- 附件列表
  }

  // ---- 3. 发送消息并唤醒驱动循环 ----
  // followup() 是最常用的发送方式：将消息排队为下一轮（next-turn），
  // 并唤醒驱动循环开始处理。
  agent.followup(message)

  console.log(`[Agent ${sessionId.slice(0, 8)}] created, message sent`)
  console.log(`[Agent ${sessionId.slice(0, 8)}] initial status: ${agent.status}`)

  return { agent, dispose: handle.dispose }
}

/**
 * 完整使用示例：启动应用、创建 Agent、等待完成、清理。
 */
async function main() {
  const { boot } = await import('@deepseek-ai/dsh-app-boot')
  const path = await import('node:path')

  // 启动 Cordis 应用（加载 cordis.yml 中的所有插件）
  const configPath = path.resolve(process.cwd(), 'cordis.yml')
  const ctx = await boot('my-app', configPath)

  try {
    const { agent, dispose } = await createAgentAndChat(
      ctx,
      'List the files in the current directory and tell me what this project is about.',
    )

    // ---- 4. 等待 Agent 处理完成 ----
    // whenIdle() 在 Agent 回到 idle 状态时 resolve
    // （所有排队消息处理完毕、无活动驱动）
    await agent.whenIdle()
    console.log(`[Agent] finished, status: ${agent.status}`)

    // ---- 5. 继续对话：发送第二条消息 ----
    agent.followup({
      role: 'user',
      content: 'Now run the tests and show me the results.',
    })

    await agent.whenIdle()
    console.log('[Agent] second turn completed')

    // ---- 6. 中途干预：发送转向指令（steer）----
    // steer() 将消息插入当前步骤的边界（next-step），
    // 如果 Agent 正在运行，会在当前步骤结束后立即处理；
    // 如果空闲，则启动新轮次。
    // 适合纠正、补充指令。
    agent.steer({
      role: 'user',
      content: 'Wait, also check for TypeScript compilation errors before running tests.',
    })

    await agent.whenIdle()

    // ---- 7. 注入上下文（不唤醒）----
    // inject() 将消息插入 next-step 队列但不唤醒驱动，
    // 适合预加载上下文信息，等待下一条用户消息触发处理。
    agent.inject({
      role: 'user',
      content: '[System] Current time: ' + new Date().toISOString(),
    })

    // ---- 8. 清理：销毁 Agent ----
    await dispose()
    console.log('[Agent] disposed')
  } finally {
    // 关闭整个 Cordis 应用
    await ctx.fiber.dispose()
  }
}
```

### 示例 2：Agent 状态机与取消控制

```typescript
/**
 * 演示 Agent 状态转换、取消执行和维护任务。
 */

import type { Agent, AgentStatus } from '@deepseek-ai/dsh-agent'

// ---- Agent 三态状态机 ----
//
//  Phase 状态：
//  ┌──────────────────────────────────────────────┐
//  │ idle ──wakeup──→ running ──drain──→ idle     │
//  │  ↑                  │  ↑                     │
//  │  └── maintenance ←──┘  └── wakeRequested     │
//  │     (runMaintenance)                         │
//  └──────────────────────────────────────────────┘
//
// - idle：无活动驱动，可以接收消息
// - running：驱动循环正在执行 Turn-Step
// - maintenance：执行维护任务（如压缩、持久化），消息排队等待
//
// 对外 status 只有两种：'idle' | 'running'
// （maintenance 对外表现为 idle）

/**
 * 监控 Agent 状态变化并记录转换。
 */
function monitorAgentStatus(agent: Agent): () => void {
  const transitions: Array<{ from: AgentStatus; to: AgentStatus; at: Date }> = []
  let currentStatus: AgentStatus = agent.status

  const off = agent.ctx.on('agent/status', ({ status }) => {
    if (status !== currentStatus) {
      transitions.push({ from: currentStatus, to: status, at: new Date() })
      currentStatus = status
      console.log(`[Agent ${agent.id.slice(0, 8)}] ${transitions[transitions.length - 1].from} → ${status}`)
    }
  })

  // 返回停止监控的函数
  return () => {
    off()
    console.log('[Monitor] stopped. Transitions:', transitions)
  }
}

/**
 * 演示取消正在运行的 Agent 执行。
 */
async function cancelAgentExample(agent: Agent) {
  // 发送一条需要长时间执行的消息
  agent.followup({
    role: 'user',
    content: 'Analyze every file in the repository in detail. This will take many steps.',
  })

  // 等待一小段时间让 Agent 开始运行
  await new Promise(resolve => setTimeout(resolve, 2000))

  if (agent.status === 'running') {
    console.log('[Cancel] Agent is running, sending cancel...')

    // cancel() 取消当前活动：
    // - 中止当前 Turn（通过 AbortController）
    // - 默认清空 Inbox 中未处理的消息
    // - 记录取消原因
    agent.cancel({
      kind: 'user-cancel',
      reason: 'User requested cancellation',
    })

    // 可选：保留 Inbox 中的排队消息
    // agent.cancel({ kind: 'user-cancel', reason: 'Pausing...' }, { keepInbox: true })

    await agent.whenIdle()
    console.log('[Cancel] Agent cancelled and returned to idle')
  }
}

/**
 * 演示维护任务（maintenance）：在 idle 状态下执行非轮次工作。
 */
async function maintenanceTaskExample(agent: Agent) {
  console.log('[Maintenance] Running session compaction...')

  try {
    // runMaintenance() 在 idle 状态下执行维护任务，
    // 期间 Agent 对外 status 仍为 'idle'，但新消息会排队等待。
    // 任务接收 AbortSignal，cancel() 会中止它。
    const result = await agent.runMaintenance(async (signal) => {
      // 模拟压缩操作
      console.log('[Maintenance] Compacting session history...')

      for (let i = 0; i < 5; i++) {
        // 模拟异步工作
        await new Promise<void>((resolve, reject) => {
          const timer = setTimeout(resolve, 500)
          signal.addEventListener('abort', () => {
            clearTimeout(timer)
            reject(signal.reason)
          })
        })

        if (signal.aborted) {
          throw signal.reason
        }

        console.log(`[Maintenance] Progress: ${(i + 1) * 20}%`)
      }

      return { compactedTurns: 10, savedTokens: 4096 }
    })

    console.log('[Maintenance] Completed:', result)
  } catch (error) {
    if ((error as Error)?.name === 'AbortError') {
      console.log('[Maintenance] Aborted by cancel')
    } else {
      throw error
    }
  }
}
```

### 示例 3：Turn-Step 循环与事件扩展点

```typescript
/**
 * 演示 Agent 循环的 Turn-Step 结构和事件扩展点（waterfall/serial/emit）。
 */

import type { Context } from '@deepseek-ai/cordis'
import type { PreStepDecision } from '@deepseek-ai/dsh-agent'

/**
 * 通过事件监听扩展 Agent 行为。
 * 事件类型：
 * - emit：通知型，监听器失败被包含
 * - waterfall：决策型，每个监听器可调用 next() 继续链或返回替换值
 * - serial：串行执行，所有监听器按顺序 await
 */
function installAgentExtensions(ctx: Context): void {
  // ---- agent/pre-step（waterfall）----
  // 在每个步骤开始前触发，可拒绝步骤或替换消息。
  ctx.on('agent/pre-step', async ({ agent, messages, turn, step, signal }, next) => {
    console.log(`[pre-step] Turn ${turn}, Step ${step}, ${messages.length} messages`)

    // 示例：阻止特定消息进入步骤
    // if (messages.some(m => isDangerous(m))) {
    //   return { kind: 'reject' }
    // }

    // 调用 next() 继续默认行为
    return next()
  })

  // ---- agent/request（waterfall）----
  // 在 LLM 请求构建时触发，可修改请求配置（切换模型/调整参数等）。
  ctx.on('agent/request', async ({ agent, turn, step }, next) => {
    const baseConfig = await next()
    console.log(`[request] Turn ${turn}, Step ${step}, model=${baseConfig.model}`)

    // 示例：特定条件下切换到更快的模型
    // if (turn > 10) {
    //   return { ...baseConfig, model: 'deepseek-v4-flash' }
    // }

    return baseConfig
  })

  // ---- agent/request-error（waterfall）----
  // LLM 请求失败时触发，可决定重试或让错误终止步骤。
  ctx.on('agent/request-error', async ({ failure, retryPolicy }, next) => {
    console.warn(`[request-error] ${failure.code}: ${failure.message}`)

    // 示例：速率限制时自动重试
    // if (failure.code === 'RATE_LIMITED' && retryPolicy) {
    //   return { kind: 'retry' }
    // }

    return next()
  })

  // ---- agent/turn-stopping（serial）----
  // 轮次即将结束时触发（无待处理工具调用和转向消息）。
  // 可在此注入 steer() 来添加额外工作。
  ctx.on('agent/turn-stopping', async ({ agent, turn }) => {
    console.log(`[turn-stopping] Turn ${turn} is about to close`)

    // 示例：自动运行 lint 检查
    // agent.steer({ role: 'user', content: 'Now run npm run lint to check for issues.' })
  })

  // ---- agent/error（emit）----
  // 错误通知（不影响流程）。
  ctx.on('agent/error', ({ agent, turn, step, error }) => {
    console.error(`[agent-error] Turn ${turn}, Step ${step}:`, error instanceof Error ? error.message : error)
  })

  // ---- tools/pre-execute（waterfall）----
  // 工具执行前审批（allow/deny/ask）。
  ctx.on('tools/pre-execute', async (exec, next) => {
    console.log(`[tool-pre-execute] ${exec.name}`, exec.arguments)
    return next()
  })

  // ---- tools/post-execute（waterfall）----
  // 工具执行后可接受、替换结果或阻塞。
  ctx.on('tools/post-execute', async (exec, result, next) => {
    if (!result.isError) {
      console.log(`[tool-post-execute] ${exec.name} completed successfully`)
    }
    return next()
  })
}

/**
 * Turn-Step 循环结构示意（ReactLoopAgent 内部逻辑）：
 *
 * turn():  // 一轮对话
 *   session.append('turn/start', { turn })
 *   while (inbox has messages or tool results):
 *     step():  // 一个执行步骤（一次 LLM 调用 + 可能的工具调用）
 *       messages = inbox.claim('next-step')
 *       decision = waterfall('agent/pre-step', messages)
 *       if decision.kind === 'reject': break
 *
 *       session.append('step/start', { turn, step })
 *       for msg in decision.messages:
 *         session.append('user/message', msg)
 *
 *       request = buildRequest(turn, step, system, messages, tools)
 *       stream = llm.stream(request)
 *       for chunk in stream:
 *         session.append('assistant/chunk', chunk)
 *
 *       message = assemble(stream chunks)
 *       session.append('assistant/message', message)
 *
 *       if message has no tool_calls:
 *         return { kind: 'completed' }  // 轮次结束
 *
 *       // 执行工具调用
 *       results = executeToolCalls(toolCalls)
 *       for result in results:
 *         session.append('tool/result', result)
 *         if result.concludesTurn: return { kind: 'completed' }
 *
 *       session.append('step/end', { turn, step })
 *
 *     serial('agent/turn-stopping', { turn })
 *     if inbox.nextStep is empty: break
 *
 *   session.append('turn/end', { turn, reason })
 */
```

### 示例 4：最小 cordis.yml 配置（编程式创建 Agent）

```yaml
# cordis.yml — 最小 Agent 运行配置

# LLM 适配器
- id: llm-deepseek
  name: '@deepseek-ai/dsh-llm-deepseek'
  config:
    thinking: enabled
    reasoningEffort: medium
    models:
      - id: deepseek-v4-flash

# Agent 循环驱动（注册 AgentFactory）
- id: agent-loop
  name: '@deepseek-ai/dsh-agent-loop'

# 会话管理
- id: session
  name: '@deepseek-ai/dsh-session-jsonl'
  config:
    persistenceRoot: './.sessions'

# 系统提示词组装
- id: system-prompt
  name: '@deepseek-ai/dsh-system-prompt'

# 工具注册表
- id: tools
  name: '@deepseek-ai/dsh-tools'
  config:
    mode: native

# 可选：文件系统工具
- id: fs-local
  name: '@deepseek-ai/dsh-fs-local'
- id: tool-fs
  name: '@deepseek-ai/dsh-tool-fs'

# 可选：Bash 工具
- id: subprocess
  name: '@deepseek-ai/dsh-subprocess-local'
- id: bash
  name: '@deepseek-ai/dsh-bash-local'
  config:
    timeoutMs: 60000
```

## 逐步解释

### 1. ReactLoopAgent 的 Phase 状态机

Agent 内部维护一个三态 Phase：

| Phase | 说明 | 对外 status |
|-------|------|-------------|
| `idle` | 无活动驱动，可以接收新消息 | `'idle'` |
| `running` | Turn-Step 循环正在执行 | `'running'` |
| `maintenance` | 执行维护任务（压缩、持久化等），新消息排队等待 | `'idle'` |

状态转换规则：
- **wakeup**（收到 followup/steer 且 idle）→ `running`，开始 kick() → turn() 循环
- **drain**（所有消息处理完毕，Inbox 为空）→ `idle`
- **runMaintenance()**（idle 时调用）→ `maintenance`，任务完成 → `idle`
- **cancel()** → 中止当前 AbortController，运行中的 Promise reject，Phase 回到 `idle`
- 如果 maintenance 期间有消息到达，`wakeRequested` 标记为 true，任务完成后自动唤醒

### 2. Inbox 消息队列与投递目标

每个 Agent 有一个 Inbox（收件箱），管理待处理的消息。消息有两个目标位置：

| 目标 | 说明 | 触发方法 |
|------|------|----------|
| `next-turn` | 下一轮对话的起始消息，等待当前轮次完全结束 | `followup()` |
| `next-step` | 当前轮次内的下一个步骤，当前步骤完成后立即处理 | `steer()`, `inject()`, 工具结果 |

四种投递方法：

| 方法 | 目标 | 唤醒 | 典型用途 |
|------|------|------|----------|
| `followup(msg)` | next-turn | ✅ | 用户新消息 |
| `steer(msg)` | next-step | ✅ | 纠正/补充当前轮次指令 |
| `inject(msg)` | next-step | ❌ | 预加载上下文（不主动唤醒） |
| `send(msg, target, wakeup)` | 自定义 | 自定义 | 底层控制 |

关键点：
- `steer()` 在 Agent 运行时会在当前步骤结束后立即注入消息；在 idle 时则启动新轮次
- `inject()` 不唤醒驱动，适合系统预加载（如时间戳、环境信息），等下一条用户消息时一起处理
- 工具执行产生的上下文（`exec.deferContext()`）通过 `next-step` 注入
- 标记了 `concludeTurn` 的工具结果会立即结束轮次

### 3. Turn-Step 循环结构

一个 **Turn**（轮次）对应一次用户交互的完整处理：
1. 打开轮次边界（`turn/start` 事件）
2. 循环执行 Step 直到无更多工作
3. 关闭轮次边界（`turn/end` 事件，携带结束原因）

一个 **Step**（步骤）对应一次 LLM 调用：
1. 声明步骤开始（`step/start`）
2. 从 Inbox 领取消息，组装 prompt（system + history + 工具 schemas）
3. 触发 `agent/pre-step` waterfall（可拒绝或修改消息）
4. 触发 `agent/request` waterfall（可修改请求配置）
5. 调用 LLM（流式处理 chunk）
6. 组装 Assistant 消息（包含文本和/或 tool_calls）
7. 如果有 tool_calls → 执行工具，结果注入 next-step，继续循环
8. 如果无 tool_calls → 步骤结束，检查 Inbox 是否有待处理消息
9. 如果 Inbox 为空 → 触发 `agent/turn-stopping` serial → 轮次结束

Turn 结束原因（`TurnEndReason`）：
- `completed`：模型返回无工具调用的最终回复
- `max-tokens`：模型输出达到 token 上限（自动继续下一步）
- `aborted`：被 cancel() 中止
- `error`：发生错误
- `blocked`：pre-step 拒绝进入步骤

### 4. 创建 Agent 的完整流程

`ctx.agents.create(options)` 的执行序列：

1. **创建 Session**：根据 sessionId 和 meta 创建持久化会话
2. **创建作用域**（Scope）：Agent 拥有独立的 Context 派生（`agent.ctx`），作用域内注册的工具/监听器仅对该 Agent 可见
3. **实例化 ReactLoopAgent**：创建 Inbox、Phase、Scope、事件分发器
4. **执行 setup 回调**：在 Agent 发布前，setup 可通过 `agentCtx` 注册作用域工具、监听器等。setup 可返回 `commit()` 函数，在发布前做最终校验
5. **事务性发布**：
   - 将 Agent 注册到 AgentRegistry
   - 触发 `session/created` → `agent/created` → `agent/session-start` 事件
   - 启动驱动循环（立即 kick() 如果有初始消息）
6. **返回 AgentHandle**：包含 `agent` 实例和 `dispose()` 方法

`dispose()` 会：停止驱动循环 → 等待退出 → 从注册表移除 → 触发 `agent/disposed` → 移除 Session → 解消作用域。

### 5. 事件系统扩展点

Agent 生命周期通过 Cordis 事件系统暴露丰富的扩展点：

**通知事件（emit）**：仅通知，监听器异常被包含（不中断流程）
- `agent/created` / `agent/disposed`
- `agent/status`（idle ⇄ running）
- `agent/inbox/inserted` / `claimed` / `discarded`
- `agent/error`
- `tools/result`、`tools/change`

**决策事件（waterfall）**：每个监听器可通过 `next()` 继续链，或返回替换值
- `agent/pre-step`：拒绝步骤或替换消息
- `agent/request`：修改 LLM 请求配置
- `agent/request-error`：决定重试或终止
- `tools/pre-execute`：allow/deny/ask 审批
- `tools/execute`：around-dispatch 包装（超时、重试、指标）
- `tools/post-execute`：接受/替换/阻塞结果

**串行事件（serial）**：按顺序 await 所有监听器
- `agent/turn-stopping`：轮次即将关闭

## 输出结果

运行上述示例代码时的典型输出：

```
[Agent a1b2c3d4] created, message sent
[Agent a1b2c3d4] initial status: idle
[Agent a1b2c3d4] status → running
[Agent a1b2c3d4] inbox +: List the files in the current directory and tell me what this project is about....
[pre-step] Turn 1, Step 1, 1 messages
[request] Turn 1, Step 1, model=deepseek-v4-flash
[tool-pre-execute] mcp__filesystem__list_directory { path: "." }
[tool-post-execute] mcp__filesystem__list_directory completed successfully
[pre-step] Turn 1, Step 2, 1 messages
[request] Turn 1, Step 2, model=deepseek-v4-flash
[Agent a1b2c3d4] status → idle
[Agent] finished, status: idle
[Agent a1b2c3d4] inbox +: Now run the tests and show me the results....
[Agent a1b2c3d4] status → running
[pre-step] Turn 2, Step 1, 1 messages
[request] Turn 2, Step 1, model=deepseek-v4-flash
[tool-pre-execute] bash { command: "npm test" }
...
[Agent a1b2c3d4] status → idle
[Agent] second turn completed
[Agent] disposed
```

## 注意事项

1. **不要手动 new ReactLoopAgent()**：始终通过 `ctx.agents.create()` 创建 Agent。直接构造会绕过事务性发布、setup 回调、工厂注册等关键流程。

2. **作用域隔离**：通过 `agent.ctx` 注册的工具、监听器、prompt section 仅对该 Agent 可见，Agent 销毁时自动清理。通过根 `ctx` 注册的是全局的。

3. **cancel() 不等同 dispose()**：`cancel()` 中止当前执行但 Agent 仍然存活，可以接收新消息；`dispose()` 完全销毁 Agent（停止循环、移除会话、解消作用域）。

4. **whenIdle() 可能永远不 resolve**：如果 Agent 收到持续的 steer 消息（如工具结果不断注入 next-step），Agent 可能一直在 running 状态。需要设置超时或使用 cancel()。

5. **maintenance 期间消息排队**：`runMaintenance()` 执行期间新到达的消息不会立即处理，而是在维护任务完成后才被驱动消费。维护任务应尽快完成。

6. **事件监听器作用域**：在根 `ctx` 上注册的监听器监听所有 Agent 的事件；在 `agent.ctx` 上注册的仅监听该 Agent。使用 `agent.ctx.on()` 可避免全局泄漏。

7. **setup 回调的事务性**：setup 中抛出异常会导致 Agent 创建回滚——不会注册到注册表、不会触发 created 事件。setup 返回的 `commit()` 函数在所有异步 setup 完成后、发布前同步执行，commit() 抛异常也会回滚。

8. **waterfall 事件必须调用 next()**：waterfall 类型的事件监听器如果不调用 `next()` 也不返回替换值，会导致流程挂起。不修改决策时应 `return next()`。

9. **AbortSignal 传播**：长时间运行的操作（工具执行、维护任务、LLM 流式调用）必须检查或转发 AbortSignal，否则 cancel() 无法真正中止工作。

10. **Session 持久化**：Agent 创建时需要 session 持久化服务（如 `dsh-session-jsonl`），否则 create() 会失败。确保 cordis.yml 中加载了 session 插件。
