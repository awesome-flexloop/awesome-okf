---
type: reference
title: "WebSocket 实时通信与音频参考"
description: "WebSocket 架构、Chat/Audio WS 客户端、Builder 模式、EventHandler 事件处理、音频 HTTP 客户端（TTS/ASR/房间/直播/声纹）的完整 API 参考。"
tags: [websocket, realtime, audio, tts, asr, speech, voice, event-handler]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cp-004
    resource: /references/websockets-audio.md
    title: "WebSocket 实时通信与音频参考"
---

# WebSocket 实时通信与音频参考

本文档登记 WebSocket 实时通信架构和音频（TTS/ASR/房间/直播/声纹）HTTP 接口的客户端类、数据模型、事件类型和使用模式。

## WebSocket 架构总览

```
WebsocketsClient (顶层入口，通过 coze.websockets 访问)
├── .chat   → WebsocketsChatClient / AsyncWebsocketsChatClient (v1/chat)
└── .audio  → WebsocketsAudioClient / AsyncWebsocketsAudioClient
    ├── .speech         → WebsocketsSpeechClient (v1/audio/speech)
    └── .transcriptions → WebsocketsTranscriptionsClient (v1/audio/transcriptions)
```

## WebSocket 基础设施

### WebsocketsBaseClient / AsyncWebsocketsBaseClient

**文件**：ws.py

WebSocket 客户端基类，封装连接管理、事件循环和消息收发。

```python
WebsocketsBaseClient(
    base_url: str,
    requester: Requester,
    path: str,
    event_factory: WebsocketsEventFactory,
    on_event: WebsocketsBaseEventHandler,
    wait_events: List[WebsocketsEventType],
)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `base_url` | `str` | WebSocket 基础 URL（使用 `http_base_url_to_ws()` 转换） |
| `requester` | `Requester` | 请求器（用于鉴权） |
| `path` | `str` | WS 端点路径 |
| `event_factory` | `WebsocketsEventFactory` | 事件工厂 |
| `on_event` | `WebsocketsBaseEventHandler` | 事件处理器 |
| `wait_events` | `List[WebsocketsEventType]` | 等待完成的事件类型列表 |

内部使用 `_input_queue` 队列管理上行消息。

### WebsocketsEvent

所有 WebSocket 事件的基类。

### WebsocketsEventType（枚举）

WebSocket 事件类型枚举，包含上行（客户端→服务端）和下行（服务端→客户端）事件类型。

### WebsocketsEventFactory

事件工厂类，将 `event_type` 字符串映射到对应的事件类，负责反序列化 WebSocket 消息。

### EventHandler（事件处理器）

#### WebsocketsBaseEventHandler / AsyncWebsocketsBaseEventHandler

事件处理器基类，定义了 `on_xxx` 回调方法族。子类可以重写特定事件的处理方法。

核心方法：

| 方法 | 说明 |
|------|------|
| `on_open()` | 连接建立时回调 |
| `on_event(event)` | 收到任意事件时回调（分发入口） |
| `on_close()` | 连接关闭时回调 |
| `on_error(error)` | 发生错误时回调 |
| `to_dict()` | 转换为分发表单（dict），用于事件路由 |

## Builder 模式

所有 WebSocket 子客户端使用 Builder 模式创建连接。每个客户端有对应的 `XxxBuildClient`：

- `WebsocketsChatBuildClient`
- `WebsocketsSpeechBuildClient`（音频语音合成）
- `WebsocketsTranscriptionsBuildClient`（音频语音识别）

### 使用方式

```python
# 1. 创建 Builder（传入 on_event 处理器）
factory = client.chat.create(on_event=my_event_handler)

# 2. 使用 async with 建立连接
async with factory() as ws:
    # ws 是已连接的 WebSocket 客户端实例
    await ws.send(...)  # 发送上行事件
    ...
```

`create()` 方法返回一个可调用工厂，调用工厂返回异步上下文管理器，`async with` 进入时自动建立连接，退出时自动关闭。

## Chat WebSocket

### WebsocketsChatClient / AsyncWebsocketsChatClient

**端点**：`v1/chat`

实时对话 WebSocket 客户端。等待 `CONVERSATION_CHAT_COMPLETED` 事件表示对话完成。

#### Chat WS 事件类型（20+种）

| 事件类 | 方向 | 说明 |
|--------|------|------|
| `ChatCreatedEvent` | 下行 | 对话已创建 |
| `ConversationChatCompletedEvent` | 下行 | 对话完成（等待的终止事件） |
| `ConversationMessageDeltaEvent` | 下行 | 消息内容增量 |
| `ConversationAudioDeltaEvent` | 下行 | 音频数据增量（语音合成输出） |
| 其他消息/对话事件 | 下行 | 消息完成、错误等 |

上行事件包括：发送消息、配置更新、打断等。

## Audio WebSocket

### WebsocketsAudioClient / AsyncWebsocketsAudioClient

音频 WebSocket 顶层客户端，通过 `websockets.audio` 访问。包含 speech 和 transcriptions 两个子客户端。

### Speech WebSocket（语音合成/TTS）

**端点**：`v1/audio/speech`

实时语音合成，将文本转换为语音流。

#### 上行事件（客户端→服务端）

| 事件类 | 说明 |
|--------|------|
| `InputTextBufferAppendEvent` | 追加输入文本 |
| `InputTextBufferCompleteEvent` | 输入文本完成（触发合成） |

#### 下行事件（服务端→客户端）

| 事件类 | 说明 |
|--------|------|
| `SpeechCreatedEvent` | 语音合成任务已创建 |
| `SpeechUpdateEvent` | 合成状态更新 |
| `SpeechAudioUpdateEvent` | 音频数据增量（`Data.delta` 为 bytes） |
| `SpeechAudioCompletedEvent` | 音频输出完成（等待的终止事件） |

等待事件：`SPEECH_AUDIO_COMPLETED`。

### Transcriptions WebSocket（语音识别/ASR）

**端点**：`v1/audio/transcriptions`

实时语音识别，将音频流转写为文本。

#### 上行事件

| 事件类 | 说明 |
|--------|------|
| `TranscriptionsUpdateEvent` | 识别配置更新 |
| `InputAudioBufferAppendEvent` | 追加音频数据（`Data.delta` 为 bytes） |
| `InputAudioBufferCompleteEvent` | 音频输入完成 |
| `InputAudioBufferClearEvent` | 清除音频缓冲区 |

#### 下行事件

| 事件类 | 说明 |
|--------|------|
| `TranscriptionsCreatedEvent` | 识别任务已创建 |
| `TranscriptionsMessageUpdateEvent` | 识别文本增量 |
| `TranscriptionsMessageCompletedEvent` | 识别完成（等待的终止事件） |

等待事件：`TRANSCRIPTIONS_MESSAGE_COMPLETED`。

## 二进制音频数据处理

WebSocket 传输中，二进制音频数据通过 Pydantic validator/serializer 自动进行 base64 编解码：

- **上行**：`InputAudioBufferAppendEvent.Data.delta` 赋值为 bytes，发送时自动 base64 编码
- **下行**：`SpeechAudioUpdateEvent.Data.delta` 接收时自动 base64 解码为 bytes
- **日志安全**：`_dump_without_delta()` 方法记录日志时只输出数据长度，不记录内容（避免敏感音频数据泄露）

## 音频配置模型

### InputAudio

输入音频配置：

| 字段 | 类型 | 说明 |
|------|------|------|
| `format` | 音频格式 | Opus 或 PCM |
| `codec` | 编解码器 | 具体编码参数 |
| `sample_rate` | int | 采样率 |

### OutputAudio

输出音频配置，字段同 InputAudio。

### OpusConfig

Opus 编解码配置。

### PCMConfig

PCM 原始音频配置：

| 字段 | 类型 | 说明 |
|------|------|------|
| `sample_rate` | `int` | 采样率 |
| `bit_depth` | `int` | 位深度 |

### LimitConfig

音频时长/大小限制配置。

---

## 音频 HTTP API

### AudioClient / AsyncAudioClient

音频 HTTP 客户端顶层入口，通过 `coze.audio` 访问。包含以下子客户端：

| 属性 | 类型 | 说明 |
|------|------|------|
| `.speech` | `SpeechClient` | TTS 语音合成 |
| `.transcriptions` | `TranscriptionsClient` | ASR 语音识别 |
| `.voices` | `VoicesClient` | 声音管理 |
| `.rooms` | `RoomsClient` | 实时音视频房间 |
| `.live` | `LiveClient` | 直播 |
| `.voiceprint_groups` | `VoiceprintGroupsClient` | 声纹组 |
| `.translations` | Translations 子模块 | 翻译 |

### SpeechClient / AsyncSpeechClient（HTTP TTS）

#### audio.speech.create()

创建 TTS 合成任务。

相关枚举：
- **AudioFormat**：音频格式枚举
- **LanguageCode**：语言代码枚举

### TranscriptionsClient / AsyncTranscriptionsClient（HTTP ASR）

#### create()

```python
audio.transcriptions.create(file: ...) -> CreateTranscriptionsResp
```

HTTP 端点：`POST /v1/audio/transcriptions`（multipart 文件上传）

| 参数 | 类型 | 说明 |
|------|------|------|
| `file` | 文件对象 | 音频文件 |

返回 `CreateTranscriptionsResp`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `text` | `str` | 识别结果文本 |

支持格式：ogg、mp3、wav。限制：10MB / 30分钟。

### VoicesClient / AsyncVoicesClient

声音管理客户端。

#### Voice 模型

| 字段 | 类型 | 说明 |
|------|------|------|
| `voice_id` | `str` | 声音 ID |
| `name` | `str` | 声音名称 |
| `emotion_info` | `VoiceEmotionInfo` | 情感信息 |

相关枚举：
- **VoiceState**：声音状态枚举
- **VoiceModelType**：声音模型类型枚举
- **VoiceEmotionInfo**：声音情感信息模型

### RoomsClient / AsyncRoomsClient

实时音视频房间客户端。

#### create()

```python
audio.rooms.create(...) -> CreateRoomResp
```

HTTP 端点：`POST /v1/audio/rooms`

返回 `CreateRoomResp`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `token` | `str` | 加入房间的 Token |
| `uid` | `str` | 用户 ID |
| `room_id` | `str` | 房间 ID |
| `app_id` | `str` | 应用 ID |

#### RoomConfig 模型

| 字段 | 类型 | 说明 |
|------|------|------|
| `audio_config` | dict | 音频配置 |
| `video_config` | dict | 视频配置 |
| `prologue_content` | str | 开场白内容 |
| `room_mode` | `RoomMode` | 房间模式 |
| `translate_config` | dict | 翻译配置 |

#### RoomMode（枚举）

| 值 | 说明 |
|----|------|
| `DEFAULT` | 默认模式 |
| `S2S` | 语音到语音（Speech-to-Speech） |
| `PODCAST` | 播客模式 |
| `TRANSLATE` | 翻译模式 |

### LiveClient / AsyncLiveClient

直播客户端。

#### retrieve()

```python
audio.live.retrieve(live_id: str) -> LiveInfo
```

HTTP 端点：`GET /v1/audio/live/{id}`

#### LiveType（枚举）

| 值 | 说明 |
|----|------|
| `ORIGIN` | 原始流 |
| `TRANSLATION` | 翻译流 |

### VoiceprintGroupsClient

声纹组客户端，包含 `features` 子客户端（声纹特征管理）。
