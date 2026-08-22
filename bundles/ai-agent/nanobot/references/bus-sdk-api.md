---
type: reference
title: MessageBus 与 SDK 类型 API
description: MessageBus 双向队列、Inbound/Outbound 消息与 OutboundEvent 事件家族、SDK 值对象签名及源码位置
tags: [nanobot, bus, events, sdk, types, reference]
sources:
  - resource: "/references/agent-api.md"
    title: "Nanobot SDK 门面 API"
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# MessageBus 与 SDK 类型 API

本页登记消息总线与 SDK 值对象的公共类型/函数签名与源码位置，作为 concepts/ 与 examples/ 的信源。来源为 `nanobot/bus/*.py` 与 `nanobot/sdk/*.py`。

## MessageBus

源码：`nanobot/bus/queue.py`

| 成员 | 签名 | 说明 |
|---|---|---|
| 类 | `class MessageBus`（L8） | 解耦 channel 与 agent core 的异步消息总线 |
| 字段 | `self.inbound: asyncio.Queue[InboundMessage]`（L17） | 入站消息队列 |
| 字段 | `self.outbound: asyncio.Queue[OutboundMessage]`（L18） | 出站消息队列 |
| 方法 | `async publish_inbound(msg)`（L20-22） | channel → agent 入站 |
| 方法 | `async consume_inbound() -> InboundMessage`（L24-26） | 阻塞消费下一条入站消息 |
| 方法 | `async publish_outbound(msg)`（L28-30） | agent → channel 出站 |
| 方法 | `async consume_outbound() -> OutboundMessage`（L32-34） | 阻塞消费下一条出站消息 |
| property | `inbound_size` / `outbound_size`（L36-43） | 队列中待处理消息数 |

## InboundMessage / OutboundMessage

源码：`nanobot/bus/events.py`

| 类型 | 字段 | 说明 |
|---|---|---|
| `@dataclass InboundMessage`（L24-49） | `channel, sender_id, chat_id, content, timestamp, media, metadata, session_key_override, require_existing_session, input_role` | 频道收到的消息 |
| property | `session_key`（L39-42） | 返回 `session_key_override` 或 `f"{channel}:{chat_id}"` |
| property | `is_user_input`（L44-49） | 是否作为用户输入进入对话 |
| `@dataclass OutboundMessage`（L52-68） | `channel, chat_id, content, reply_to, media, metadata, buttons, event` | 发回频道的消息；`event` 承载运行时/UI 语义 |

内部元数据键（L13-21）：`OUTBOUND_META_AGENT_UI = "_agent_ui"`、`INBOUND_META_RUNTIME_CONTROL = "_runtime_control"`、`INBOUND_META_USER_SHELL = "_user_shell"` 等。

## OutboundEvent 事件家族

源码：`nanobot/bus/outbound_events.py`

| 类型 | 关键字段 | 说明 |
|---|---|---|
| `class OutboundEvent`（L17-18） | — | 内部出站事件的标记基类 |
| `ProgressEvent`（L21-30） | `content, tool_hint, reasoning, tool_events, file_edit_events` | 进度/推理/工具事件 |
| `RetryWaitEvent`（L33-35） | `content` | 重试等待提示 |
| `StreamDeltaEvent`（L38-41） | `content, stream_id` | 流式增量 |
| `StreamEndEvent`（L44-49） | `content, stream_id, resuming, merge_next` | 流式结束 |
| `StreamedResponseEvent`（L52-53） | — | 流式完整响应标记 |
| `TurnEndEvent`（L57-62） | `latency_ms, goal_state, usage, context_window_tokens` | 轮次结束 |
| `GoalStatusEvent` / `GoalStateSyncEvent` | `status` / `goal_state` | 目标状态同步 |
| `SessionUpdatedEvent` | `scope` | 会话更新通知 |
| `RuntimeModelUpdatedEvent` / `TurnModelUpdatedEvent` | `model, model_preset` | 模型切换通知 |

工具函数（L106-130）：`outbound_message_for_event(...)`、`outbound_event_from_message(msg)`、`replace_outbound_event(...)`。

## SDK 值对象

源码：`nanobot/sdk/types.py`

| 类型 | 说明 |
|---|---|
| `StreamEventType`（L11-22） | `Literal` 联合 10 个事件字符串 |
| `STREAM_EVENT_*` 常量（L24-33） | 10 个事件类型常量（`run.started` 等） |
| `STREAM_EVENT_TYPES`（L35-46） | 按序包含全部 10 个值的元组 |
| `@dataclass(slots=True) RunResult`（L49-59） | `content, tools_used, messages, usage, stop_reason, error, metadata` |
| `@dataclass(slots=True) StreamEvent`（L62-77） | `type, delta, content, result, name, tool_call_id, arguments, iteration, resuming, usage, error, metadata` |
| `SessionSnapshot`（L80-98） | `key, messages, metadata, created_at, updated_at` + `to_dict` |
| `SessionInfo`（L101-121） | `key, created_at, updated_at, title, preview, path` + `to_dict` |
| 函数 | `snapshot_from_session`（L124-138）、`snapshot_from_payload`（L141-160）、`result_from_response`（L163-174） |

## SDK 流式与运行时工具

源码：`nanobot/sdk/streaming.py`、`nanobot/sdk/runtime.py`

| 类型/函数 | 说明 |
|---|---|
| `RunStream`（L26-40） | `stream_events()`（单消费者）、`wait()`、`text()`、`cancel()`、`aclose()`、`done` property |
| `SDKStreamEmitter`（L120-169） | `emit` / `text_delta` / `text_completed` / `close` |
| `SDKStreamingHook(AgentHook)`（L172-224） | `before_execute_tools` / `emit_reasoning` / `emit_reasoning_end` / `after_iteration` |
| `ensure_single_model_selector`（runtime.py L9-15） | 校验 model 与 model_preset 互斥 |
| `build_process_direct_kwargs`（runtime.py L18-48） | 组装 `process_direct` 的关键字参数 |

## 相关概念

- [消息总线系统](/concepts/02-bus-system.md)
- [CLI 与 SDK](/concepts/03-cli-sdk.md)
- [Nanobot SDK 门面 API](/references/agent-api.md)