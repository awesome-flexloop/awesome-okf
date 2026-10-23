---
type: concept
title: "Agent 循环——轮次、步骤与事件序列"
description: "dsh 默认 agent loop（ReactLoopAgent）的 turn/step 状态机、pre-step 准入、瀑布事件顺序、取消语义与失败步骤的工具结果补记机制。"
tags: [deepseek-harness, agent-loop, turn, step, waterfall, cancellation]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-upstream
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: DeepSeek Harness 官方仓库 packages/core/agent-loop 与 docs/agent-lifecycle
---

# Agent 循环：轮次、步骤与事件序列

## 1. turn 与 step

- **step** = 一次模型请求 + 它调用的工具
- **turn** = 零个或多个 step；在领取首条输入之前打开，在不再欠下任何工作时关闭

驱动器实现类 `ReactLoopAgent implements Agent`（`packages/core/agent-loop/src/agent.ts`），核心方法 `turn()` / `step()` / `preStep()` / `kick()`（`kick` 是 `while (await this.turn()) {}` 的驱动泵）。

## 2. 一次 turn 的实际顺序

```text
turn/start
  claim next-step 输入 + 一条排队消息
  assemble prompt 段 + 工具 schema
  → agent/pre-step（水瀑布）
      reject → turn 以 blocked 结束，无 step
      首次领取被拒绝或为空 → turn 以 completed 结束，无 step
      enter(messages, startsRequestSeries?)
  → step/start
  → agent/request（水瀑布）→ prepareCall
      提交系统提示词与已接纳用户消息（append user/message）
      记录 request/header、request/context
      冻结模型历史
  → llm/stream（水瀑布）→ agent/assistant-stream(start / chunk* / end)
  → tool/call* → tools/pre-execute → tools/execute → tools/post-execute → tool/result*
  → step/end
  → agent/turn-stopping（serial）
turn/end
```

三种"不开步骤"的分支值得注意：**被拒绝的输入不会产生一个空 step**，而是让轮次直接以 `blocked` 或 `completed` 收尾。

## 3. pre-step：准入与改写

`agent/pre-step` 是第一个瀑布事件，它决定**接纳哪些输入**：

- 监听器可以**改写**或**拒绝**已领取的消息
- 返回 `enter` 决策时可设置 `startsRequestSeries`——循环据此记录新的 `request/header`（原因 `series`），或在封装同时变化时记录携带 `startsSeries: true` 的 `change`
- 包装型监听器通过 `{ ...decision, messages }` 保留该声明

注入的上下文等待一条唤醒消息；输入通过同一个 inbox 到达驱动器。

## 4. agent/request：只换配置，不改消息

`agent/request` 是第二个瀑布事件。它**不能修改消息**，只能替换 `LlmCallConfig`（换模型路由、换参数、换工具）。

紧随其后的 `prepareCall()` 先解析实际路由，再提交系统提示词与已接纳用户消息；在任一异步阶段取消都**不会提交这两者**。提示词准入依据**已准备调用的能力**，而不是先前的 `request/context`。

## 5. 提示词只走历史，不走请求字段

`request/header` 里 `system?: never` 被永久保留（`@persistenceReserved`）。系统提示词只通过 `system/message` surface 节点进入派生历史：

| 路由能力 | 准入规则 |
|---|---|
| 无系统节点 | 即使提示词为空也**预留**第 0 号节点（不产生协议消息） |
| 不具备能力的路由 / 新请求序列 | 非空渲染文本**归并到首个系统节点**；每个非空后续系统节点先收到有日志记录的空内容替换 |
| 具备能力的路由（`in-history`） | 延续序列中在缓存历史之后追加非空更新 |
| 空渲染文本 | 逐节点空内容替换，清除所有生效系统节点 |

开启新请求序列的条件：`startsRequestSeries`，或 `session.surface.contentGeneration` 自附接/上次请求以来变化，或（已准备路由未声明 `toolUpdate` 且）可见工具 schema 变化。

## 6. 取消语义

`AgentCancelCause = { kind: 'user' | 'parent' | 'hook' | 'disposed' }`。

- 取消被识别后，`turn/end` 记录 `{ kind: 'aborted', reason }`
- 循环发送不可变请求，同时保持取消有效，仅对完全冻结的对象复用冻结证据
- **失败步骤补记缺失的工具结果**（否则模型历史里会留下悬空调用）：
  - 已记录 `tool/call` 但无结果 → 记 `TOOL_OUTCOME_UNKNOWN`，结果文本 `Its outcome is unknown.`
  - 无调用记录 → 记 `TOOL_NOT_STARTED`，文本说明调用在 Harness 记录其开始前就被中断
  - 取消后未分发的调用 → 合成 `tool/call` + `ABORTED_BEFORE_DISPATCH`

## 7. 错误恢复

`agent/request-error` 是瀑布事件：监听器返回 `{ kind: 'retry' }` 且不调用 `next()` 即接管恢复；默认 `undefined` 让失败成为终态。

`LlmError` 保留 `failure` 结构；其他错误扁平为 `{ message: errorChain(error), code: 'UNKNOWN' }`。

## 8. 实时流与持久流的分家

`agent/assistant-stream` 发布**进程本地**的 start / 瞬态 chunk / end frame；循环会在 committed end frame 前把完整紧凑 stream 提交为一条 `assistant/message`（进入模型历史）或仅日志的 `assistant/attempt`（失败/重试/取消，不进模型历史）。Web 的 Session-follow adapter 是这个 live event **唯一的远程消费方**。

> 若进程在 settlement 前硬中断，则不会留下持久 attempt stream。

## 下一步

- [会话与持久化](05-session-and-persistence.md)——上面这些事件如何落盘
- [工具系统](06-tool-system.md)——`tools/*` 三段瀑布的细节
