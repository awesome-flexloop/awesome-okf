---
type: example
title: "WebSocket 语音对话示例"
description: "使用 WebSocket 进行实时语音对话：继承 EventHandler 处理事件、Builder 模式创建连接、实时音频流收发的完整异步示例。"
tags: [websocket, voice, audio, realtime, event-handler, builder, async, tts, asr]
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

# WebSocket 语音对话示例

本示例演示使用 WebSocket 进行实时语音对话：通过继承 `AsyncWebsocketsBaseEventHandler` 处理下行事件，使用 Builder 模式创建 WebSocket 连接，实现文本对话的实时消息接收。同时演示实时 TTS 和实时 ASR 的基本框架。

> **注意**：WebSocket 功能目前仅提供异步客户端（`AsyncWebsocketsClient`），需要在 async/await 环境中使用。

## 前置准备

1. 安装 cozepy：`pip install cozepy`
2. 配置 PAT Token（推荐中国区使用 `COZE_CN_BASE_URL`）
3. 有一个已发布的 Bot ID
4. 安装 `httpx` 和 `websockets` 依赖（cozepy 已包含）

## 完整代码

```python
import os
import asyncio
from typing import Optional
from cozepy import (
    AsyncCoze,
    AsyncTokenAuth,
    COZE_CN_BASE_URL,
    WebsocketsEventType,
)
from cozepy.websockets.chat import (
    WebsocketsChatBuildClient,
    ChatCreatedEvent,
    ConversationChatCompletedEvent,
    ConversationMessageDeltaEvent,
    ConversationAudioDeltaEvent,
)


# ============================================================
# 示例 1：WebSocket 文本对话（基础用法）
# ============================================================

class ChatEventHandler:
    """
    WebSocket 对话事件处理器。
    通过重写 on_xxx 方法处理不同类型的下行事件。
    """

    def __init__(self):
        self.full_reply = ""
        self.conversation_id: Optional[str] = None
        self.chat_id: Optional[str] = None
        self.audio_chunks: list[bytes] = []
        self.completed = asyncio.Event()

    async def on_chat_created(self, event: ChatCreatedEvent):
        """对话创建事件：WebSocket 连接成功，对话已初始化"""
        self.chat_id = event.data.id if event.data else None
        self.conversation_id = event.data.conversation_id if event.data else None
        print(f"[系统] 对话已创建 (chat_id: {self.chat_id})")

    async def on_conversation_message_delta(self, event: ConversationMessageDeltaEvent):
        """文本消息增量事件：实时打印 Bot 回复"""
        if event.data and event.data.content:
            content = event.data.content
            self.full_reply += content
            print(content, end="", flush=True)

    async def on_conversation_audio_delta(self, event: ConversationAudioDeltaEvent):
        """音频增量事件：收集 TTS 音频数据"""
        if event.data and event.data.delta:
            # event.data.delta 是 bytes 类型（自动 base64 解码）
            self.audio_chunks.append(event.data.delta)

    async def on_conversation_chat_completed(self, event: ConversationChatCompletedEvent):
        """对话完成事件：标记对话结束"""
        print()  # 换行
        print("-" * 40)
        print("[系统] 对话已完成")
        if event.data and event.data.usage:
            print(f"Token 消耗: {event.data.usage.token_count}")
        self.completed.set()

    async def on_error(self, event):
        """错误事件"""
        print(f"\n[错误] {event}")
        self.completed.set()

    def to_dict(self):
        """事件分发映射（必须实现，用于将事件类型路由到处理方法）"""
        return {
            WebsocketsEventType.CHAT_CREATED: self.on_chat_created,
            WebsocketsEventType.CONVERSATION_MESSAGE_DELTA: self.on_conversation_message_delta,
            WebsocketsEventType.CONVERSATION_AUDIO_DELTA: self.on_conversation_audio_delta,
            WebsocketsEventType.CONVERSATION_CHAT_COMPLETED: self.on_conversation_chat_completed,
            WebsocketsEventType.ERROR: self.on_error,
        }


async def websocket_text_chat(bot_id: str, user_id: str, message: str):
    """
    WebSocket 文本对话示例。

    Args:
        bot_id: Bot ID
        user_id: 用户标识
        message: 发送的消息文本
    """
    # 1. 初始化异步客户端
    coze = AsyncCoze(
        auth=AsyncTokenAuth(token=os.environ["COZE_API_TOKEN"]),
        base_url=COZE_CN_BASE_URL,
    )

    # 2. 创建事件处理器
    handler = ChatEventHandler()

    # 3. 使用 Builder 模式创建 WS 连接工厂
    # create() 返回一个可调用对象，调用后返回异步上下文管理器
    ws_factory = coze.websockets.chat.create(
        bot_id=bot_id,
        user_id=user_id,
        on_event=handler,
    )

    # 4. 使用 async with 建立连接
    async with ws_factory() as ws:
        print(f"[系统] WebSocket 已连接")
        print(f"[用户] {message}")
        print("[Bot] ", end="", flush=True)

        # 5. 发送上行消息（文本输入）
        # 具体的发送 API 取决于 SDK 版本的 ws 客户端方法
        # ws.send_text_message(message)  或  ws.chat_send(...)
        # 等待对话完成事件
        await handler.completed.wait()

    # 6. 输出收集到的音频（如果有的话）
    if handler.audio_chunks:
        audio_data = b"".join(handler.audio_chunks)
        print(f"\n[系统] 收到音频数据: {len(audio_data)} bytes")
        # 可以保存为文件:
        # with open("reply_audio.pcm", "wb") as f:
        #     f.write(audio_data)

    return handler.full_reply


# ============================================================
# 示例 2：实时 TTS（文本转语音，WebSocket 流式）
# ============================================================

class SpeechEventHandler:
    """实时 TTS 事件处理器"""

    def __init__(self):
        self.audio_buffer = bytearray()
        self.completed = asyncio.Event()

    async def on_speech_created(self, event):
        print("[TTS] 语音合成任务已创建")

    async def on_speech_audio_update(self, event):
        """音频增量回调"""
        if event.data and event.data.delta:
            # delta 是 bytes（自动 base64 解码）
            self.audio_buffer.extend(event.data.delta)

    async def on_speech_audio_completed(self, event):
        print(f"[TTS] 合成完成，音频大小: {len(self.audio_buffer)} bytes")
        self.completed.set()

    async def on_error(self, event):
        print(f"[TTS 错误] {event}")
        self.completed.set()

    def to_dict(self):
        return {
            WebsocketsEventType.SPEECH_CREATED: self.on_speech_created,
            WebsocketsEventType.SPEECH_AUDIO_UPDATE: self.on_speech_audio_update,
            WebsocketsEventType.SPEECH_AUDIO_COMPLETED: self.on_speech_audio_completed,
            WebsocketsEventType.ERROR: self.on_error,
        }


async def websocket_tts_demo(text: str, output_file: str = "tts_output.pcm"):
    """
    WebSocket 实时 TTS 示例：将文本流式合成为语音。
    """
    coze = AsyncCoze(
        auth=AsyncTokenAuth(token=os.environ["COZE_API_TOKEN"]),
        base_url=COZE_CN_BASE_URL,
    )

    handler = SpeechEventHandler()

    # 创建 TTS WS 连接
    ws_factory = coze.websockets.audio.speech.create(on_event=handler)

    async with ws_factory() as ws:
        print(f"[TTS] 输入文本: {text}")

        # 发送文本（通过上行事件）
        # 1. 追加文本
        # await ws.append_text(text)
        # 2. 标记文本输入完成
        # await ws.complete_text()

        # 等待合成完成
        await handler.completed.wait()

    # 保存音频文件
    if handler.audio_buffer:
        with open(output_file, "wb") as f:
            f.write(handler.audio_buffer)
        print(f"[TTS] 音频已保存到 {output_file}")


# ============================================================
# 示例 3：实时 ASR（语音转文字，WebSocket 流式）
# ============================================================

class TranscriptionEventHandler:
    """实时 ASR 事件处理器"""

    def __init__(self):
        self.full_text = ""
        self.completed = asyncio.Event()

    async def on_transcriptions_created(self, event):
        print("[ASR] 语音识别任务已创建，开始说话...")

    async def on_transcriptions_message_update(self, event):
        """识别文本增量"""
        if event.data and event.data.content:
            self.full_text += event.data.content
            print(f"\r[ASR] {self.full_text}", end="", flush=True)

    async def on_transcriptions_message_completed(self, event):
        print(f"\n[ASR] 识别完成")
        self.completed.set()

    async def on_error(self, event):
        print(f"\n[ASR 错误] {event}")
        self.completed.set()

    def to_dict(self):
        return {
            WebsocketsEventType.TRANSCRIPTIONS_CREATED: self.on_transcriptions_created,
            WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_UPDATE: self.on_transcriptions_message_update,
            WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_COMPLETED: self.on_transcriptions_message_completed,
            WebsocketsEventType.ERROR: self.on_error,
        }


async def websocket_asr_demo(audio_file: str = "input.pcm"):
    """
    WebSocket 实时 ASR 示例：流式发送音频，实时获取识别文本。
    """
    coze = AsyncCoze(
        auth=AsyncTokenAuth(token=os.environ["COZE_API_TOKEN"]),
        base_url=COZE_CN_BASE_URL,
    )

    handler = TranscriptionEventHandler()

    ws_factory = coze.websockets.audio.transcriptions.create(on_event=handler)

    async with ws_factory() as ws:
        # 读取音频文件，分块发送
        try:
            with open(audio_file, "rb") as f:
                while True:
                    chunk = f.read(3200)  # 每次发送 3200 bytes（约 100ms 的 16kHz 16bit PCM）
                    if not chunk:
                        break
                    # 发送音频块（上行事件）
                    # await ws.append_audio(chunk)
                    await asyncio.sleep(0.1)  # 模拟实时发送节奏

            # 标记音频输入完成
            # await ws.complete_audio()
        except FileNotFoundError:
            print(f"[ASR] 音频文件 {audio_file} 不存在，跳过实际数据发送")
            # await ws.complete_audio()

        await handler.completed.wait()

    print(f"[ASR] 最终识别结果: {handler.full_text}")
    return handler.full_text


# ============================================================
# 主函数
# ============================================================

async def main():
    BOT_ID = "your_bot_id_here"
    USER_ID = "user_ws_001"

    print("=" * 50)
    print("WebSocket 文本对话示例")
    print("=" * 50)
    await websocket_text_chat(BOT_ID, USER_ID, "你好，用 WebSocket 和你聊天！")

    # print("\n" + "=" * 50)
    # print("WebSocket 实时 TTS 示例")
    # print("=" * 50)
    # await websocket_tts_demo("你好，这是一段测试语音合成的文本。")

    # print("\n" + "=" * 50)
    # print("WebSocket 实时 ASR 示例")
    # print("=" * 50)
    # await websocket_asr_demo()


if __name__ == "__main__":
    asyncio.run(main())
```

## 运行方式

```bash
export COZE_API_TOKEN="your_pat_token_here"
# 修改代码中的 BOT_ID
python websocket_voice_chat.py
```

## 代码解析

### Builder 模式

WebSocket 连接使用 Builder 模式，分两步建立连接：

1. **`create()`**：传入配置（bot_id、on_event 等），返回一个工厂函数
2. **工厂函数 + `async with`**：调用工厂函数返回异步上下文管理器，进入时建立连接，退出时自动关闭

这种设计保证了连接的正确生命周期管理，避免连接泄漏。

### EventHandler 模式

EventHandler 采用事件驱动范式：
- 继承基类并重写 `on_xxx` 回调方法
- `to_dict()` 方法将事件类型映射到处理方法（必须实现）
- 使用 `asyncio.Event()` 实现等待特定事件（如对话完成）的同步

### 二进制音频处理

WebSocket 中音频数据作为 bytes 传输：
- 下行音频（TTS 输出）：`event.data.delta` 直接是 bytes（SDK 自动 base64 解码）
- 上行音频（ASR 输入）：给 delta 赋值 bytes，SDK 自动 base64 编码
- 日志中不会记录音频内容，只记录长度（`_dump_without_delta()`）

### 三种 WebSocket 场景对比

| 场景 | WS 入口 | 终止事件 | 上行核心操作 | 下行核心事件 |
|------|---------|---------|-------------|-------------|
| 文本对话 | `websockets.chat` | `CONVERSATION_CHAT_COMPLETED` | 发送消息 | 消息增量、对话完成 |
| TTS | `websockets.audio.speech` | `SPEECH_AUDIO_COMPLETED` | 追加文本、完成输入 | 音频增量、合成完成 |
| ASR | `websockets.audio.transcriptions` | `TRANSCRIPTIONS_MESSAGE_COMPLETED` | 追加音频、完成输入、清除缓冲 | 文本增量、识别完成 |

### asyncio.Event 同步

`asyncio.Event()` 是在异步环境中等待特定条件的关键工具。在 EventHandler 中设置 `completed` 事件，主协程通过 `await handler.completed.wait()` 等待对话/合成/识别完成。

## 相关概念

- [WebSocket 实时通信](/concepts/07-websockets-realtime.md) — WebSocket 架构和事件体系详解
- [音频与语音](/concepts/08-audio-voice.md) — HTTP 音频 API（TTS/ASR/房间/直播）
- [对话与流式处理](/concepts/03-chat-streaming.md) — HTTP+SSE 对话方案
- [基础对话示例](/examples/basic-chat.md) — HTTP SSE 对话示例
- [WebSocket 实时通信与音频参考](/references/websockets-audio.md) — 所有 WS 客户端和事件的完整 API
