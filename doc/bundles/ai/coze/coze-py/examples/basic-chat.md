---
type: example
title: "基础对话示例"
description: "使用 TokenAuth 初始化客户端，通过 SSE 流式接口与 Bot 对话，处理消息增量事件和对话完成事件，获取 Token 用量。"
tags: [chat, stream, sse, token-auth, message, event]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cp-003
    resource: /references/chat-workflow.md
    title: "对话与工作流参考"
  - id: F-cp-001
    resource: /references/coze-client.md
    title: "Coze 客户端入口与基础设施参考"
  - id: F-cp-002
    resource: /references/auth-model.md
    title: "认证体系参考"
---

# 基础对话示例

本示例演示使用 cozepy 进行最基础的 Bot 对话：使用个人访问令牌（PAT）初始化客户端，通过 SSE 流式接口发送消息，逐字打印回复内容，并在对话完成后获取 Token 用量统计。

## 前置准备

1. 在 [Coze 平台](https://www.coze.cn)（中国区）或 [Coze 国际版](https://www.coze.com)注册账号
2. 在个人设置中生成个人访问令牌（PAT）
3. 创建一个 Bot 并发布，获取 Bot ID
4. 安装 cozepy：`pip install cozepy`

## 完整代码

```python
import os
from cozepy import (
    Coze,
    TokenAuth,
    Message,
    ChatEventType,
    COZE_CN_BASE_URL,
    CozeAPIError,
)

def chat_with_bot(bot_id: str, user_id: str, question: str) -> str:
    """
    与 Bot 进行一轮流式对话，返回完整回复文本。

    Args:
        bot_id: Bot ID
        user_id: 用户标识（用于区分不同用户的对话上下文）
        question: 用户提问文本

    Returns:
        Bot 的完整回复文本
    """
    # 1. 初始化客户端（从环境变量读取 Token，避免硬编码）
    coze = Coze(
        auth=TokenAuth(token=os.environ["COZE_API_TOKEN"]),
        base_url=COZE_CN_BASE_URL,  # 中国区使用此 URL
    )

    full_reply = ""

    try:
        # 2. 发起流式对话
        for event in coze.chat.stream(
            bot_id=bot_id,
            user_id=user_id,
            additional_messages=[
                Message.build_user_question_text(question),
            ],
            # conversation_id=None,  # 不传则创建新会话
        ):
            # 3. 处理不同类型的 SSE 事件
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                # 消息增量：逐字打印回复
                content = event.message.content
                full_reply += content
                print(content, end="", flush=True)

            elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                # 对话完成：输出统计信息
                chat = event.chat
                print()  # 换行
                print("---")
                if chat.last_error:
                    print(f"对话出错: [{chat.last_error.code}] {chat.last_error.msg}")
                else:
                    print(f"对话 ID: {chat.id}")
                    print(f"会话 ID: {chat.conversation_id}")
                    print(f"Token 消耗: {chat.usage.token_count}")
                    print(f"创建时间: {chat.created_at}")
                    print(f"完成时间: {chat.completed_at}")

    except CozeAPIError as e:
        print(f"\nAPI 错误: code={e.code}, msg={e.msg}")
        print(f"日志 ID: {e.logid}")
        print(f"调试链接: {e.debug_url}")
        raise

    return full_reply


def multi_turn_chat(bot_id: str, user_id: str, questions: list[str]) -> None:
    """
    多轮对话示例：在同一会话中连续提问，保持上下文。

    Args:
        bot_id: Bot ID
        user_id: 用户标识
        questions: 多轮问题列表
    """
    coze = Coze(
        auth=TokenAuth(token=os.environ["COZE_API_TOKEN"]),
        base_url=COZE_CN_BASE_URL,
    )

    conversation_id = None  # 第一轮不传，由服务端创建

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*50}")
        print(f"第 {i} 轮 | 用户: {question}")
        print(f"{'='*50}")
        print("Bot: ", end="", flush=True)

        for event in coze.chat.stream(
            bot_id=bot_id,
            user_id=user_id,
            additional_messages=[
                Message.build_user_question_text(question),
            ],
            conversation_id=conversation_id,  # 传入会话 ID 保持上下文
        ):
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                print(event.message.content, end="", flush=True)

            elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                # 第一轮从完成事件中获取 conversation_id
                if conversation_id is None:
                    conversation_id = event.chat.conversation_id
                    print(f"\n(会话 ID: {conversation_id})")
                if event.chat.usage:
                    print(f"\n(Token 消耗: {event.chat.usage.token_count})")


if __name__ == "__main__":
    # 配置你的 Bot ID
    BOT_ID = "your_bot_id_here"
    USER_ID = "user_001"

    # 单轮对话
    print("=== 单轮对话 ===")
    reply = chat_with_bot(BOT_ID, USER_ID, "你好，请简单介绍一下你自己")

    # 多轮对话
    print("\n\n=== 多轮对话 ===")
    multi_turn_chat(BOT_ID, USER_ID, [
        "我叫小明，喜欢编程",
        "你还记得我的名字吗？我喜欢什么？",
        "推荐一本适合我的编程入门书",
    ])
```

## 运行方式

```bash
# 设置环境变量
export COZE_API_TOKEN="your_pat_token_here"

# 运行（修改代码中的 BOT_ID 为你自己的 Bot ID）
python basic_chat.py
```

## 代码解析

### 初始化客户端

```python
coze = Coze(auth=TokenAuth(token=...), base_url=COZE_CN_BASE_URL)
```

- `TokenAuth` 是最简单的认证方式，直接使用 PAT
- `COZE_CN_BASE_URL` 指向中国区 API，国际版使用默认值 `COZE_COM_BASE_URL`
- Token 从环境变量读取，避免硬编码泄露

### 发起流式对话

```python
coze.chat.stream(bot_id=..., user_id=..., additional_messages=[...])
```

- `bot_id`：要对话的 Bot
- `user_id`：用户标识，用于区分不同用户
- `additional_messages`：本次发送的消息列表，使用 `Message.build_user_question_text()` 构建

### 事件处理

核心是遍历 `Stream[ChatEvent]`，根据 `event.event` 判断事件类型：

- `CONVERSATION_MESSAGE_DELTA`：每次收到一小段文本，拼接并打印，实现打字机效果
- `CONVERSATION_CHAT_COMPLETED`：对话结束，可以获取 Token 用量、会话 ID、错误信息

### 多轮对话

多轮对话的关键是在后续调用中传入上一轮获得的 `conversation_id`，这样 Bot 能"记住"之前的对话内容。第一轮不传 `conversation_id` 时，SDK 会自动创建新会话。

### 错误处理

捕获 `CozeAPIError` 获取错误码、错误消息和 `logid`。`logid` 在排查问题时非常重要，可以提供给 Coze 技术支持快速定位。

## 扩展：异步版本

使用 `AsyncCoze` + `AsyncTokenAuth`，事件循环中使用 `async for`：

```python
import asyncio
from cozepy import AsyncCoze, AsyncTokenAuth, Message, ChatEventType, COZE_CN_BASE_URL

async def async_chat(bot_id: str, user_id: str, question: str):
    coze = AsyncCoze(
        auth=AsyncTokenAuth(token=os.environ["COZE_API_TOKEN"]),
        base_url=COZE_CN_BASE_URL,
    )
    full_reply = ""
    async for event in coze.chat.stream(
        bot_id=bot_id,
        user_id=user_id,
        additional_messages=[Message.build_user_question_text(question)],
    ):
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            full_reply += event.message.content
            print(event.message.content, end="", flush=True)
    return full_reply

# asyncio.run(async_chat("bot_id", "user_id", "你好"))
```

## 相关概念

- [对话与流式处理](../concepts/03-chat-streaming.md) — SSE 流式对话的机制详解
- [认证体系](../concepts/01-auth-system.md) — TokenAuth 和其他认证方式
- [客户端初始化](../concepts/02-client-init.md) — 客户端配置选项
- [会话管理](../concepts/06-conversations.md) — 多轮对话的会话管理
- [工作流执行示例](workflow-execution.md) — 工作流流式调用
