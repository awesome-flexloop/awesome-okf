---
type: concept
title: "音频与语音"
description: "掌握 HTTP 音频 API 的 TTS 语音合成、ASR 语音识别、声音管理、实时音视频房间、直播和声纹组功能。"
tags: [audio, tts, asr, speech, voice, room, live, voiceprint, transcription]
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

# 音频与语音

cozepy 提供了丰富的音频能力，涵盖文本转语音（TTS）、语音转文本（ASR）、声音克隆与管理、实时音视频房间、直播以及声纹识别。这些功能通过 `coze.audio` 入口下的多个子客户端提供 HTTP API 接口。实时音频场景（边说边转、低延迟语音对话）则通过 WebSocket 通道提供，见[WebSocket 实时通信](07-websockets-realtime.md)。

## AudioClient 总览

`AudioClient`（异步版本 `AsyncAudioClient`）通过 `coze.audio` 访问，包含以下子客户端：

```
AudioClient (coze.audio)
├── .speech             → SpeechClient         TTS 语音合成
├── .transcriptions     → TranscriptionsClient ASR 语音识别
├── .voices             → VoicesClient         声音管理
├── .rooms              → RoomsClient          实时音视频房间
├── .live               → LiveClient           直播
├── .voiceprint_groups  → VoiceprintGroupsClient 声纹组
└── .translations       → Translations 子模块   音频翻译
```

## TTS：语音合成（Speech）

`SpeechClient` 提供 HTTP 接口的文本转语音功能，将文本合成为音频文件。适用于不需要实时流式输出的场景——如生成播客音频、有声书、语音通知等。

```python
from cozepy import Coze, TokenAuth, COZE_CN_BASE_URL

coze = Coze(auth=TokenAuth(token="your_token"), base_url=COZE_CN_BASE_URL)

# 创建 TTS 任务
resp = coze.audio.speech.create(
    text="你好，欢迎使用 Coze 语音合成",
    voice_id="voice_id",  # 声音 ID
    # format=AudioFormat.MP3,  # 音频格式
    # language_code=LanguageCode.ZH,  # 语言
)

# resp 包含合成的音频数据
```

### AudioFormat（枚举）

音频格式枚举，支持 MP3、WAV、OGG 等常见格式。

### LanguageCode（枚举）

语言代码枚举，如中文（ZH）、英文（EN）、日文（JA）等。

> 实时 TTS（边生成边播放）请使用 [WebSocket Speech](07-websockets-realtime.md#实时-ttsspeech-ws)。

## ASR：语音识别（Transcriptions）

`TranscriptionsClient` 提供 HTTP 接口的语音转文字功能。通过 multipart 表单上传音频文件，返回识别文本。

```python
# 上传音频文件进行识别
with open("audio.wav", "rb") as f:
    resp = coze.audio.transcriptions.create(file=f)
    print(f"识别结果: {resp.text}")
```

- **HTTP 端点**：`POST /v1/audio/transcriptions`
- **支持格式**：ogg、mp3、wav
- **限制**：文件大小 10MB，时长 30 分钟
- **返回**：`CreateTranscriptionsResp`，包含 `text` 字段（识别结果文本）

> 实时 ASR（边说边转写）请使用 [WebSocket Transcriptions](07-websockets-realtime.md#实时-asrtranscriptions-ws)。

## 声音管理（Voices）

`VoicesClient` 用于管理 TTS 使用的声音资源，包括预置声音和自定义克隆声音。

### Voice 模型

| 字段 | 类型 | 说明 |
|------|------|------|
| `voice_id` | `str` | 声音唯一 ID |
| `name` | `str` | 声音名称 |
| `emotion_info` | `VoiceEmotionInfo` | 情感表达能力信息 |

### 声音相关枚举

| 枚举 | 说明 |
|------|------|
| `VoiceState` | 声音状态（可用/训练中/失败等） |
| `VoiceModelType` | 声音模型类型 |

### VoiceEmotionInfo

声音情感信息模型，描述该声音支持的情感风格（如开心、悲伤、严肃等）。

## 实时音视频房间（Rooms）

`RoomsClient` 用于创建和管理实时音视频房间，支持多种房间模式——包括语音对话、S2S（Speech-to-Speech）、播客和翻译模式。

### 创建房间

```python
from cozepy import Coze, TokenAuth, COZE_CN_BASE_URL, RoomMode

coze = Coze(auth=TokenAuth(token="your_token"), base_url=COZE_CN_BASE_URL)

room = coze.audio.rooms.create(
    # room_config=RoomConfig(
    #     room_mode=RoomMode.S2S,
    #     audio_config={...},
    #     prologue_content="你好，我是你的语音助手",
    # ),
)

print(f"房间 ID: {room.room_id}")
print(f"加入 Token: {room.token}")
print(f"用户 ID: {room.uid}")
print(f"App ID: {room.app_id}")
```

### CreateRoomResp

创建房间返回：

| 字段 | 类型 | 说明 |
|------|------|------|
| `token` | `str` | 加入房间的认证 Token |
| `uid` | `str` | 分配的用户 ID |
| `room_id` | `str` | 房间 ID |
| `app_id` | `str` | 应用 ID |

### RoomConfig 模型

| 字段 | 类型 | 说明 |
|------|------|------|
| `audio_config` | dict | 音频配置参数 |
| `video_config` | dict | 视频配置参数 |
| `prologue_content` | str | 开场白（用户加入时自动播放） |
| `room_mode` | `RoomMode` | 房间模式 |
| `translate_config` | dict | 翻译配置（翻译模式下使用） |

### RoomMode（枚举）

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| `DEFAULT` | 默认模式 | 普通语音对话 |
| `S2S` | Speech-to-Speech | 端到端语音对话 |
| `PODCAST` | 播客模式 | 多人语音播客 |
| `TRANSLATE` | 翻译模式 | 实时语音翻译 |

## 直播（Live）

`LiveClient` 用于查询直播相关信息。

### 查询直播信息

```python
live_info = coze.audio.live.retrieve(live_id="live_id")
# HTTP: GET /v1/audio/live/{id}
```

### LiveType（枚举）

| 值 | 说明 |
|----|------|
| `ORIGIN` | 原始流 |
| `TRANSLATION` | 翻译流 |

### LiveInfo 模型

直播信息模型，包含直播状态、流地址等信息。

## 声纹组（Voiceprint Groups）

`VoiceprintGroupsClient` 提供声纹（Voiceprint）管理能力。声纹是语音中的个体特征，可用于说话人识别、身份验证等场景。包含 `features` 子客户端用于管理声纹特征。

## 音频翻译（Translations）

Translations 子模块提供音频翻译能力，在 TRANSLATE 房间模式或单独的翻译场景中使用。

## HTTP 音频 vs WebSocket 音频

音频功能在 HTTP 和 WebSocket 两个通道都有提供，选择依据如下：

| 功能 | HTTP API | WebSocket | 选择建议 |
|------|---------|-----------|---------|
| TTS | `audio.speech.create()` | `websockets.audio.speech` | 文件下载用 HTTP，实时播放用 WS |
| ASR | `audio.transcriptions.create(file=)` | `websockets.audio.transcriptions` | 文件上传用 HTTP，实时转录用 WS |
| 房间 | `audio.rooms.create()` | — | 仅 HTTP 创建 |
| 声音管理 | `audio.voices` | — | 仅 HTTP |
| 直播 | `audio.live.retrieve()` | — | 仅 HTTP |
| 声纹 | `audio.voiceprint_groups` | — | 仅 HTTP |

简单判断标准：如果处理的是**已有的音频文件**，用 HTTP；如果需要**实时流式处理**（边说边转、边生成边播放），用 WebSocket。

## 相关概念

- [WebSocket 实时通信](07-websockets-realtime.md) — 实时 TTS/ASR 的 WebSocket 方案
- [客户端初始化](02-client-init.md) — AudioClient 的初始化方式
- [WebSocket 语音对话示例](../examples/websocket-voice-chat.md) — 实时语音对话示例
- [WebSocket 实时通信与音频参考](../references/websockets-audio.md) — 音频 HTTP API 和 WS API 的完整参考
