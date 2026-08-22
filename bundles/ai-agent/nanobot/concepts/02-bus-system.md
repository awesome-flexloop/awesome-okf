---
type: concept
title: 消息总线系统
description: MessageBus 双向异步队列、InboundMessage/OutboundMessage 数据结构与 OutboundEvent 事件家族的语义分工
tags: [nanobot, bus, events, async]
sources:
  - resource: "/references/bus-sdk-api.md"
    title: "MessageBus 与 SDK 类型 API"
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# 消息总线系统

消息总线（`MessageBus`）是 nanobot 解耦聊天频道与 agent 核心的机制（F-017）。频道把消息推入入站队列，agent 处理后再把响应推入出站队列。整个总线只有一对 `asyncio.Queue` 和四个方法，设计意图非常克制。

## MessageBus 结构

`MessageBus` 内部仅持有两个有界无界默认队列（F-018）：

```python
class MessageBus:
    def __init__(self):
        self.inbound: asyncio.Queue[InboundMessage] = asyncio.Queue()
        self.outbound: asyncio.Queue[OutboundMessage] = asyncio.Queue()
```

四个方法（F-019）两两对称：

```python
async def publish_inbound(self, msg: InboundMessage) -> None   # channel → agent
async def consume_inbound(self) -> InboundMessage              # 阻塞取一条
async def publish_outbound(self, msg: OutboundMessage) -> None # agent → channel
async def consume_outbound(self) -> OutboundMessage            # 阻塞取一条
```

另有 `inbound_size` / `outbound_size` 两个 property 返回 `qsize()`（F-019）。`MessageBus`/`InboundMessage`/`OutboundMessage` 统一从 `nanobot.bus` 导出（F-020）。

## 入站与出站消息

`InboundMessage` 是频道收到的消息，字段含链路标识 `channel/sender_id/chat_id`、正文 `content`、可选 `media` 列表、`metadata`，以及会话控制字段 `session_key_override`、`require_existing_session`、`input_role`（F-021）。

两个派生属性（F-021）：

- `session_key`：返回 `session_key_override`，否则 `f"{channel}:{chat_id}"`——这是默认的会话身份来源，让不同频道/会话自动隔离历史。
- `is_user_input`：有 `input_role` 时按它判断，否则 `channel != "system"`。

`OutboundMessage` 是发回频道的消息，含 `channel/chat_id/content` 与 `reply_to/media/metadata/buttons`，以及一个 `event` 字段承载内部运行时/UI 语义（F-022）。

## 事件语义外置为类型

出站消息的"运行时/UI 语义"并不塞进 `metadata` 的保留标志，而是挂在 `OutboundMessage.event` 字段上，其类型是一族 `@dataclass(frozen=True)`、继承自 `OutboundEvent` 标记基类的事件（F-024）：

| 事件 | 作用 |
|---|---|
| `ProgressEvent` | 进度提示、推理增量、工具事件聚合 |
| `StreamDeltaEvent` / `StreamEndEvent` / `StreamedResponseEvent` | 流式增/终/完整响应 |
| `TurnEndEvent` | 轮次结束（延迟、目标状态、用量、上下文窗口 token） |
| `GoalStatusEvent` / `GoalStateSyncEvent` | 持续目标状态同步 |
| `SessionUpdatedEvent` | 会话更新通知 |
| `RuntimeModelUpdatedEvent` / `TurnModelUpdatedEvent` | 模型切换通知 |

配套函数 `outbound_message_for_event` 用于按类型事件构造消息、`outbound_event_from_message` 反向解析类型事件（F-025）。

### 遗留元数据桥接

`_legacy_event_from_metadata` 会把 `_stream_delta`/`_stream_end`/`_progress`/`_turn_end` 等旧 metadata 标志翻译成对应的类型化事件（F-025）。它存在的意义是兼容还在用旧保留标志迁移中的内部扩展与频道插件——新代码应直接设置 `OutboundMessage.event` 字段，而不是继续堆叠 metadata 标志。

## 谁走总线、谁不走

并非所有入口都经过 `MessageBus`。`nanobot agent -m "..."` 的一次性消息直接调用 `agent_loop.process_direct`，绕过总线；只有交互 CLI 与频道才 `publish_inbound` 到总线再消费 `outbound`（F-046）。SDK 的 `run/stream` 同样直连 `process_direct`。理解这一差异是读懂 nanobot 数据流的关键。

## 相关概念

- [Agent 核心：Nanobot 门面](/concepts/01-agent-core.md)
- [CLI 与 SDK](/concepts/03-cli-sdk.md)
- [MessageBus 与 SDK 类型 API](/references/bus-sdk-api.md)