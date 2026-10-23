---
type: concept
title: "会话与持久化——事件日志与 generation 发布"
description: "dsh 的 SessionEvent 日志模型、deriveMessages 消息投影、两套 generation 的区分、JSONL vN 排他发布与格式迁移链，以及投影 seam。"
tags: [deepseek-harness, session, persistence, event-sourcing, jsonl, generation]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-upstream
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: DeepSeek Harness 官方仓库 packages/core/session 与 docs/subsystems/persistence
---

# 会话与持久化：事件日志与 generation 发布

## 1. 核心原则

> **模型可见即已记录。** 每个模型请求都必须能从会话日志重建。新增模型可见输入需要会话事件。

会话日志是**仅追加（append-only）**的事件流，模型所见上下文由它投影而来，而不是反过来。

## 2. SessionEvent 词汇

核心 14 个变体（`packages/core/session/src/types.ts` 的 `SessionEventMap`）：

```text
turn/start  turn/end  step/start  step/end
user/message  developer/message  system/message
assistant/message  assistant/attempt
tool/call  tool/result
request/header  request/context  session/end-seed
```

事件信封：

```ts
{ type, seq: SessionSeq, time: number, data, ignorable?: true,
  surfaceOp?, sourceEventSeqs? }
```

`surfaceOp` 与 `sourceEventSeqs` 只在 surface 事件类型上携带（`system/message`、`developer/message`、`user/message`、`assistant/message`、`tool/result`）。

声明合并可扩展新事件：压缩 seam 加 `compaction/start|summary|end`，钩子桥加 `hook/invoked|hook/result`，图片省略加 `image/offload`。

## 3. deriveMessages：日志到模型历史

`Session.deriveMessages(): Message[]`（`packages/core/session/src/index.ts`）把事件投影成模型消息：

| 事件 | 投影 |
|---|---|
| `user/message` | user 消息，原样承载 content |
| `assistant/message` | assistant 消息（含 provider/model 与可选 replayState）；**内容为空则跳过**，不进 transcript |
| `tool/result` | 一等 **tool-role** 消息（不是 ContentBlock） |
| `turn/*`、`step/*`、`assistant/attempt`、`llm/retry` 等 | 不投影 |

缓存语义：`derived` / `derivedNodes` / `derivedGeneration` 三字段；`contentGeneration` 变化则整体重建，纯尾部增长只处理新增节点。返回**新数组**，内部 `Message` 对象共享且深冻结。

投影是纯函数：`deriveEventMessage(event)`、`foldSurface(events, projections)`。

## 4. 两套 generation（务必区分）

这是最容易读错的地方——同名不同义：

| | Surface generation | 物理格式 generation |
|---|---|---|
| 位置 | `SessionSurface.contentGeneration` / `replaceGeneration`（内存） | `session.vN.jsonl[.zstd]` 文件（磁盘） |
| 作用 | 让增量消费方区分"纯尾部增长"与"重写" | 标识会话日志的格式代数 |
| 递增时机 | 每次提交一次替换，两者 `+= 1`；仅追加则只 `contentGeneration += 1` | 新一版格式发布时 +1 |

## 5. JSONL 发布语义

- JSONL **v0** 使用 `session.jsonl[.zstd]`，v1 及后续使用小写 `session.vN.jsonl[.zstd]`
- **已提交 generation 路径绝不重命名、替换或删除**
- 写 open：先编码、校验，再在未改变源的**旁边排他发布**最终版本命名的后继
- 只读 open：直接使用内存结果，不发布后继
- 仅 header 的 `stat` 与 `list` 会重新扫描每个 Session 目录，选择**数值最高**的规范 generation；未来版本会导致拒绝
- 已被后续事件封住的普通中断尾部由句柄消费方修复；只有当后续 `turn/start` 已封住一种有限的已发布 restart 时，migration 才插入缺失的 interrupted `turn/end`

格式迁移链：每个相邻迁移包只负责一个 `vN → vN+1` 步骤（`packages/session/session-format-v0-to-v1` … `v3-to-v4`），由 `defineSessionFormatMigration()` / `createSessionFormatChain()` 组装。

## 6. 投影 seam

`dsh-session-projection` 提供 `ctx.sessionProjections`：已注册单元增量折叠已提交事件。

- host 消费方通过 `stateOf()` 读取单个类型化状态
- 载体通过 `snapshot()` 批量取得裁剪后的客户端视图
- host 读取方要么在激活时**要求**该服务，要么在注册表或必需 key 缺席时**明确失败**——贡献方不得为缺失的 host 值静默提供默认值
- agent loop 为读取方注册共享的 `turnBoundary` 状态

## 7. 纯消息投影：插件改内容也要留痕

修改现有消息内容的插件注册**纯消息投影**，独立读取器显式传入相同的处理器。工具变更不依赖能力，由 Session 工具历史提供方声明。

> 一句话：会话层的设计目标是"任何时候都能从日志重建出模型看到的东西"。

## 下一步

- [工具系统](06-tool-system.md)
- [源码路径与包清单](../references/source-map.md)
