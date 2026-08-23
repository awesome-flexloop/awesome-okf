---
type: concept
title: "WebSocket 实时通信"
description: "深入理解 WebSocket 实时架构、Builder 模式创建连接、EventHandler 事件驱动、实时对话和实时语音（TTS/ASR）的实现方式。"
tags: [websocket, realtime, event-handler, builder, chat-ws, audio-ws, binary]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cp-004
    resource: /references/websockets-audio.md
    title: "WebSocket 实时通信与音频参考"
  - id: F-cp-001
    resource: /references/coze-client.md
    title: "Coze 客户端入口与基础设施参考"
---

# WebSocket 实时通信

HTTP+SSE 方案适用于大多数场景，但在需要双向实时通信的场景下——如实时语音对话、边说边转写、打断当前发言等——WebSocket 是更合适的选择。cozepy 的 WebSocket 模块提供了统一的基础设施、事件驱动模型和 Builder 连接模式，支持实时对话、实时 TTS（语音合成）和实时 ASR（语音识别）三大场景。

## WebSocket 架构总览

所有 WebSocket 功能通过 `coze.websockets` 入口访问，分为 Chat（实时对话）和 Audio（实时音频）两个域：

```
WebsocketsClient (coze.websockets)
├── .chat    → WebsocketsChatClient        实时对话 (端点: v1/chat)
└── .audio   → WebsocketsAudioClient
    ├── .speech         → 实时 TTS (端点: v1/audio/speech)
    └── .transcriptions → 实时 ASR (端点: v1/audio/transcriptions)
```

异步版本对应 `AsyncWebsocketsClient`、`AsyncWebsocketsChatClient` 等。

## 基础设施层

### WebsocketsBaseClient

所有 WS 客户端共享 `WebsocketsBaseClient`（ws.py）基类，它封装了：
- WebSocket 连接建立与关闭
- 上行消息队列（`_input_queue`）
- 事件接收循环
- 事件分发到 EventHandler
- 等待特定完成事件的机制（`wait_events`）

构造参数：

| 参数 | 作用 |
|------|------|
| `base_url` | WebSocket 基础 URL（自动从 HTTP URL 转换） |
| `requester` | 用于鉴权的请求器 |
| `path` | WS 端点路径 |
| `event_factory` | 事件工厂，负责反序列化消息 |
| `on_event` | 事件处理器实例 |
| `wait_events` | 标记"完成"的事件类型列表 |

### WebsocketsEventFactory

事件工厂根据消息中的 `event_type` 字段，将原始 JSON 映射到对应的事件类。这是一个典型的工厂模式，确保每个事件类型都被正确反序列化为对应的 Pydantic 模型。

### WebsocketsEventType

统一的事件类型枚举，定义了所有上行（客户端→服务端）和下行（服务端→客户端）事件的类型字符串。

## EventHandler 事件驱动模型

WebSocket 使用事件驱动（Event-Driven）范式。你需要继承 `WebsocketsBaseEventHandler`（或异步版本 `AsyncWebsocketsBaseEventHandler`）并重写感兴趣的事件回调方法：

```python
from cozepy import AsyncWebsocketsBaseEventHandler, WebsocketsEventType
from cozepy.websockets.chat import (
    ConversationChatCompletedEvent,
    ConversationMessageDeltaEvent,
)

class MyChatEventHandler(AsyncWebsocketsBaseEventHandler):
    async def on_conversation_chat_completed(self, event: ConversationChatCompletedEvent):
        """对话完成时回调"""
        print("对话完成！")

    async def on_conversation_message_delta(self, event: ConversationMessageDeltaEvent):
        """消息增量回调"""
        print(event.data.content, end="", flush=True)

    async def on_error(self, event):
        """错误回调"""
        print(f"错误: {event}")
```

EventHandler 的 `on_xxx` 方法命名遵循 `on_{event_type_snake_case}` 约定。`to_dict()` 方法内部构建了事件类型到处理方法的分发表。

## Builder 模式创建连接

WebSocket 连接使用 Builder 模式创建，这是 SDK 中一个重要的设计模式。每个 WS 客户端都有对应的 `XxxBuildClient`：

```
WebsocketsChatClient        ← WebsocketsChatBuildClient.create()
WebsocketsSpeechClient      ← WebsocketsSpeechBuildClient.create()  (audio.speech)
WebsocketsTranscriptionsClient ← WebsocketsTranscriptionsBuildClient.create()  (audio.transcriptions)
```

### 连接流程

```python
# 异步场景下的标准模式
from cozepy import AsyncCoze, AsyncTokenAuth, COZE_CN_BASE_URL

coze = AsyncCoze(auth=AsyncTokenAuth(token="your_token"), base_url=COZE_CN_BASE_URL)

# Step 1: 创建 Builder（传入事件处理器）
ws_factory = coze.websockets.chat.create(
    on_event=MyChatEventHandler(),
    # 其他配置参数...
)

# Step 2: 使用 async with 建立和管理连接
async with ws_factory() as ws:
    # ws 是已连接的 WebsocketsChatClient
    # 在上下文中发送上行事件
    await ws.send(...)
    # ... 等待事件通过 handler 回调处理
# 退出 async with 时自动关闭连接
```

这种模式的优点：
- **资源安全**：`async with` 保证连接正确建立和关闭
- **配置分离**：`create()` 设置配置，`ws_factory()` 建立连接
- **可复用**：同一个 factory 可以创建多个连接

## 实时对话（Chat WS）

**端点**：`v1/chat`

Chat WS 支持 20+ 种事件类型，覆盖完整的对话生命周期：

| 下行事件 | 说明 |
|----------|------|
| `ChatCreatedEvent` | 对话已创建 |
| `ConversationMessageDeltaEvent` | 文本消息增量（逐字输出） |
| `ConversationAudioDeltaEvent` | 音频增量（语音输出） |
| `ConversationChatCompletedEvent` | 对话完成（**等待的终止事件**） |
| 其他事件 | 消息完成、错误等 |

Chat WS 等待 `CONVERSATION_CHAT_COMPLETED` 事件表示对话完成，此时事件循环自动退出。

与 HTTP+SSE 的 `chat.stream()` 相比，Chat WS 支持：
- **双向通信**：可以在对话过程中发送新消息、打断
- **实时音频**：直接收发音频流，实现语音对话
- **更低延迟**：WebSocket 连接复用，避免反复建连

## 实时 TTS（Speech WS）

**端点**：`v1/audio/speech`

实时语音合成，将文本流转换为语音流输出。

### 上行事件（你发送的）

| 事件 | 说明 |
|------|------|
| `InputTextBufferAppendEvent` | 追加要合成的文本 |
| `InputTextBufferCompleteEvent` | 文本输入完毕，触发合成 |

### 下行事件（你接收的）

| 事件 | 说明 |
|------|------|
| `SpeechCreatedEvent` | 合成任务已创建 |
| `SpeechUpdateEvent` | 合成状态更新 |
| `SpeechAudioUpdateEvent` | 音频数据增量（`Data.delta` 是 bytes） |
| `SpeechAudioCompletedEvent` | 合成完成（**终止事件**） |

等待事件：`SPEECH_AUDIO_COMPLETED`。

## 实时 ASR（Transcriptions WS）

**端点**：`v1/audio/transcriptions`

实时语音识别，边说边转写。

### 上行事件

| 事件 | 说明 |
|------|------|
| `TranscriptionsUpdateEvent` | 更新识别配置 |
| `InputAudioBufferAppendEvent` | 追加音频数据（`Data.delta` 是 bytes） |
| `InputAudioBufferCompleteEvent` | 音频输入完毕 |
| `InputAudioBufferClearEvent` | 清除音频缓冲（如用户打断说话） |

### 下行事件

| 事件 | 说明 |
|------|------|
| `TranscriptionsCreatedEvent` | 识别任务已创建 |
| `TranscriptionsMessageUpdateEvent` | 识别文本增量 |
| `TranscriptionsMessageCompletedEvent` | 识别完成（**终止事件**） |

等待事件：`TRANSCRIPTIONS_MESSAGE_COMPLETED`。

## 二进制音频数据处理

WebSocket 中传输的音频数据是二进制格式（bytes）。SDK 通过 Pydantic 的 validator 和 serializer 自动处理 base64 编解码：

```
上行：Python bytes → Pydantic serializer → base64 编码 → JSON 发送
下行：JSON 中的 base64 字符串 → Pydantic validator → 解码为 Python bytes
```

- 发送时：直接给 `Data.delta` 赋值 bytes，SDK 自动编码
- 接收时：`event.data.delta` 直接是 bytes，可直接写入文件或送入音频播放器

### 日志安全

`_dump_without_delta()` 方法在日志输出时只记录音频数据的长度，不记录内容本身。这是一个重要的安全设计——避免敏感语音数据被写入日志文件。

## 音频配置模型

建立音频 WS 连接时需要配置音频参数：

| 模型 | 说明 |
|------|------|
| `InputAudio` | 输入音频配置（格式、编解码器、采样率） |
| `OutputAudio` | 输出音频配置 |
| `OpusConfig` | Opus 编解码配置（适合实时传输，压缩率高） |
| `PCMConfig` | PCM 原始音频配置（无损，数据量大） |
| `LimitConfig` | 音频时长/大小限制 |

Opus 适合网络传输，PCM 适合直接播放或本地处理。

## HTTP vs WebSocket 选择指南

| 场景 | 推荐通道 | 理由 |
|------|---------|------|
| 普通文本对话 | HTTP SSE (`chat.stream()`) | 简单、稳定、重连容易 |
| 需要打断对话 | WebSocket Chat | 双向通信，支持打断 |
| 语音合成后播放 | HTTP TTS | 一次性合成，下载音频文件 |
| 实时语音对话 | WebSocket Speech + Chat | 低延迟双向音频流 |
| 录音文件转写 | HTTP ASR | 文件上传，简单 |
| 边说边转写 | WebSocket Transcriptions | 流式识别，实时出字 |

## 相关概念

- [对话与流式处理](/concepts/03-chat-streaming.md) — HTTP+SSE 对话方案
- [音频与语音](/concepts/08-audio-voice.md) — HTTP 音频 API（TTS/ASR/房间/直播）
- [WebSocket 语音对话示例](/examples/websocket-voice-chat.md) — 完整的实时语音对话代码
- [WebSocket 实时通信与音频参考](/references/websockets-audio.md) — 所有 WS 客户端和事件的完整 API
