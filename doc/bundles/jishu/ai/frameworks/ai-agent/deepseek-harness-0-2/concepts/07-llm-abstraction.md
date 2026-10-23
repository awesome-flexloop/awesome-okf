---
type: concept
title: "LLM 抽象层——适配器、内容块与流式协议"
description: "dsh 的模型接入层：LlmAdapter 契约、ContentBlock 词汇表、StreamChunk 流式协议与 BlockAssembler 组装、模型路由与请求头、系统提示词组装与压缩、token 计费。"
tags: [deepseek-harness, llm, adapter, streaming, compaction, token-meter]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-upstream
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: DeepSeek Harness 官方仓库 packages/llm 与 docs/subsystems/llm-streaming
---

# LLM 抽象层：适配器、内容块与流式协议

## 1. 适配器契约

`abstract class LlmAdapter`——唯一必需方法是：

```ts
abstract stream(options: GenerateOptions): AsyncIterable<StreamChunk>
```

可覆写钩子：`providerInfo()`、`providerRetryPolicy()`、`imageRequestPricing()`、`imageRequestTarget()`、`listModels()`、`resolveModel()`、`prepareCall()`。

注册：`ctx.llm.registerAdapter(providers, adapter)` 返回 `AdapterRegistrationHandle`（支持原子路由替换）。未注册路由以 `NO_ADAPTER` 失败。

内置提供方：`dsh-llm-deepseek`（官方 API + 账号）、`dsh-llm-deepseek-api-key`、`dsh-llm-pi-ai`（多提供方聚合）、`dsh-llm-retry`。

## 2. 内容块词汇表

`ContentBlockMap` 定义块类型：

```text
text | reasoning | image | file | tool-call | tool-addition | tool-removal
```

- `ToolCallBlock` 含 `id: ToolCallId`、`name`、原始 JSON `arguments`
- `ToolAdditionBlock.toolName` 激活由 Session 事件请求头引用的定义；`ToolRemovalBlock.toolName` 移除当前定义

消息角色映射 `MessageRoleMap`；`AssistantProviderMetadata` 携带 provider / model / replayState。

## 3. 流式协议

`StreamChunk` 是封闭可辨识联合：

```ts
type StreamChunk =
  | { type: 'block-start'; index: number; blockType: ContentBlockType }
  | { type: 'text-delta'; index: number; text: string }
  | { type: 'reasoning-delta'; index: number; text: string }
  | { type: 'tool-call-delta'; index: number; id: ToolCallId; name?: string; argumentsDelta: string }
  | { type: 'block-end'; index: number; block: ContentBlock }
  | { type: 'usage'; usage: TokenUsage }
  | { type: 'finish'; reason: FinishReason; replayState?: ReplayEnvelope }
```

- `index` 关联交错的 delta；`block-end` 携带**已组装的完整 ContentBlock**，消费方无需自行重组
- `BlockAssembler`（`packages/llm/llm/src/assembler.ts`）负责组装，并提供 `interruptedBlocks()`

**适配器必须遵守的六条约定**：

1. `usage` 必须在 `finish` 之前，`finish` 之后不再有任何分片
2. 工具 `arguments` 全程保持原始 JSON 字符串
3. 两条错误路径共用 `LlmFailure`：从 `stream()` 抛出，或以 `finish { kind: 'error' | 'aborted', failure }` 结束
4. 一次适配器调用 = 一次提供方尝试（**适配器禁用库重试**）
5. 提供方停顿受 `streamIdleTimeoutMs` 约束（默认 5 分钟），watchdog 映射为 `TIMEOUT`
6. 上下文溢出只有一个规范 code：`CONTEXT_WINDOW_EXCEEDED`；空 completion → `EMPTY_RESPONSE`（默认可重试）

每个 HTTP 请求携带 `attributionHeaders()`。

> **安全细节**：`BlockAssembler` 在 max-tokens 结束时**丢弃每个工具调用**——被截断的调用不能安全执行；同一决定同时裁剪 replay 的逐块条目。

## 4. 模型路由

路由元数据 `RequestContext = { provider, model, contextWindow?, systemPromptUpdate? }`。其中 `systemPromptUpdate === 'in-history'` 表示该路由把**最新** system 消息视为有效系统提示词。

`request/context` 仅在 provider / model / 容量 / 更新模式与上一条不同时追加；它**不参与**请求重建与 header 相等比较（否则一次路由变化会被登记成 header 的 `change`）。

`RequestHeaderReason = 'initial' | 'resume' | 'change' | 'series'`。

## 5. 系统提示词组装

`ctx.systemPrompt` 提供 `section()` / `context()` / `variable()` / `assemble()` / `renderPrompt()`。

`PromptSection` 含 `name` / `order` / `text`（静态或函数）/ `interpolate?` / `complete?`；**同名重复注册抛错**；同名作用域段遮蔽全局段。排序：先按 `order` 升序，再按名称**码元序**。

两阶段设计：

- **求值** `assemble()`：返回已求值未插值的段 + 有序工具 schema + 变量值
- **渲染** `renderPrompt()`：插值 `{{variable}}`、删空段、空行连接

未知引用、已注册但无值、格式错误——**整组都抛错**，不静默降级。

`PromptContext` 是"缓存安全的动态上下文"，在循环中成为**带来源的 user 角色快照**，而不是 system 段。

## 6. 压缩（compaction）

压缩是**可选能力 seam**，不属于 agent loop 主干，三角色：`ctx.compaction`（Service Definition）、`compaction-basic`（Provider）、`command-compact`（Consumer）。

三个**仅日志**事件：

| 事件 | 载荷要点 |
|---|---|
| `compaction/start` | `{ turn }`（数字 = 自动轮次，`null` = 独立手动尝试），取锁 |
| `compaction/summary` | `summary`、`shadowedRange`、`shadowedSeqs`、`shadowedTokenCount`、provider/model/usage 等 |
| `compaction/end` | `{ turn, error? }`，释放锁 |

- 锁括住整个操作；中途崩溃表现为**可检测的遗留锁**（有 start 无 end），而非虚假声称完成的 end
- **摘要本身承载在一条 `user/message` 上**，其 `surfaceOp: { op: 'replace', startSeq, endSeq }`——这是摘要压缩执行的**唯一 surface 变更**
- `shadowedRange` 是 **surface 位置跨度**，不是数值区间：替换检查点落在更早位置时 `start` 可能**大于** `end`；权威集合是 `shadowedSeqs`
- 触发类型 `CompactionTrigger = 'pressure' | 'context-overflow'`；自动路径接入点在**派生请求之前**的 `agent/pre-step`

## 7. Token 计费

`ctx.tokenMeter`（`packages/llm/token-meter`）：

- `TokenMeasurement` 含 `logRevision`、`baseline`、`surfaceDeltaTokens`（有符号）、`totalTokens`、`surfaceTokens`、`nodes`
- `TokenSurfaceNode` 含 `seq` / `tokens`（路由计价）/ `heuristicTokens`（固定启发式，保证 O(1) 投影折叠自洽）
- `baseline.kind === 'usage'` 表示最近一次成功提供方调用具有相同的规范请求 envelope；`'estimated'` 表示无可复用保守锚点
- 计量成本 O(surface)：每次调用克隆位置节点

`TokenUsage` 的计数**互不重叠**：`inputTokens` 仅未缓存输入；`cacheReadTokens` / `cacheWriteTokens` 单独报告，计费输入 = 三者之和；`reasoningTokens` 已含在 `outputTokens` 内，**不得重复相加**。

图片定价：`ctx.llm.imageRequestPricing(provider, model)` 同步解析，返回与 images 对齐的价格数组。

## 下一步

- [能力 seam 与子系统地图](08-capability-seams.md)
- [源码路径与包清单](../references/source-map.md)
