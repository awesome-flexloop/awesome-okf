---
type: concept
title: "对话与流式处理"
description: "理解 ChatClient 的 SSE 流式对话机制、ChatEvent 事件类型、Message 模型构建、工具调用处理和 Token 用量统计。"
tags: [chat, streaming, sse, message, event, tool-call, usage]
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
---

# 对话与流式处理

对话（Chat）是 cozepy 最核心的功能，用于与 Coze Bot 进行交互。SDK 通过 SSE（Server-Sent Events）实现流式响应，让你能够实时看到模型生成的内容，而不是等待完整响应后一次性返回。这种流式体验对于聊天应用至关重要——用户可以逐字看到回复，而不是面对空白屏幕等待。

## ChatClient 入口

`ChatClient`（异步版本 `AsyncChatClient`）通过 `coze.chat` 访问。核心方法是 `stream()`，它发起一次对话并返回一个 `Stream[ChatEvent]` 对象：

```python
from cozepy import Coze, TokenAuth, Message, ChatEventType, COZE_CN_BASE_URL

coze = Coze(auth=TokenAuth(token="your_token"), base_url=COZE_CN_BASE_URL)

# 发起流式对话
for event in coze.chat.stream(
    bot_id="your_bot_id",
    user_id="user_123",
    additional_messages=[
        Message.build_user_question_text("你好，请介绍一下你自己"),
    ],
):
    # 处理每个 SSE 事件
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        print(event.message.content, end="", flush=True)
    elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
        print("\n\n对话完成！")
        print(f"Token 用量: {event.chat.usage.token_count}")
```

### stream() 参数详解

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `bot_id` | `str` | ✅ | 要对话的 Bot ID |
| `user_id` | `str` | ✅ | 标识当前用户的 ID，用于区分不同用户的对话 |
| `additional_messages` | `List[Message]` | ✅ | 本次发送的消息列表 |
| `conversation_id` | `str \| None` | ❌ | 会话 ID，传入则在已有会话中继续，不传则创建新会话 |

## Message 模型

消息是对话的基本单元。每个 `Message` 包含角色、内容、类型等信息：

| 字段 | 类型 | 说明 |
|------|------|------|
| `role` | `MessageRole` | 消息角色：`MessageRole.USER`（用户）或 `MessageRole.ASSISTANT`（助手） |
| `type` | `str` | 消息类型 |
| `content` | `str` | 消息文本内容 |
| `content_type` | `str` | 内容 MIME 类型 |
| `meta_data` | `dict` | 附加元数据 |

SDK 提供两个便捷的静态方法来构建消息：

```python
# 构建用户文本问题
user_msg = Message.build_user_question_text("今天天气怎么样？")
# role = MessageRole.USER, content = "今天天气怎么样？"

# 构建助手回答（通常由模型返回，手动构建场景较少）
assistant_msg = Message.build_assistant_answer("今天天气晴朗。")
```

### 多轮对话

要在同一会话中继续对话，有两种方式：

**方式一**：不传 `conversation_id`，SDK 自动创建会话，从返回的事件中获取 `conversation_id`：

```python
conversation_id = None
for event in coze.chat.stream(
    bot_id="bot_id",
    user_id="user_123",
    additional_messages=[Message.build_user_question_text("你好")],
    conversation_id=conversation_id,  # 第一轮为 None
):
    if event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
        conversation_id = event.chat.conversation_id
        print(f"会话 ID: {conversation_id}")

# 第二轮对话，传入 conversation_id 保持上下文
for event in coze.chat.stream(
    bot_id="bot_id",
    user_id="user_123",
    additional_messages=[Message.build_user_question_text("我刚才说了什么？")],
    conversation_id=conversation_id,  # 传入上一轮的 conversation_id
):
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        print(event.message.content, end="", flush=True)
```

**方式二**：通过 `conversations` 服务显式创建和管理会话（见[会话管理](06-conversations.md)）。

## ChatEvent 事件体系

`stream()` 返回的每个事件是一个 `ChatEvent` 对象，通过 `event.event`（`ChatEventType` 枚举）判断事件类型。核心事件类型包括：

| 事件类型 | 含义 | 常见用途 |
|----------|------|---------|
| `CONVERSATION_MESSAGE_DELTA` | 消息内容增量 | **逐字打印回复内容**，最常用 |
| `CONVERSATION_MESSAGE_COMPLETED` | 单条消息完成 | 获取完整消息对象 |
| `CONVERSATION_CHAT_COMPLETED` | 整个对话完成 | 获取最终 Chat 对象（含 usage、status） |
| 错误事件 | 对话出错 | 处理错误情况 |

### 事件处理模式

典型的事件处理循环模式：

```python
full_reply = ""

for event in coze.chat.stream(
    bot_id="bot_id",
    user_id="user_123",
    additional_messages=[Message.build_user_question_text("讲个笑话")],
):
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        # 增量输出
        content = event.message.content
        full_reply += content
        print(content, end="", flush=True)

    elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
        chat = event.chat
        if chat.last_error:
            print(f"\n错误: {chat.last_error.msg}")
        else:
            print(f"\n\nToken 消耗: {chat.usage.token_count}")
```

## Chat 模型

对话完成后，`CONVERSATION_CHAT_COMPLETED` 事件携带完整的 `Chat` 对象：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `str` | 对话 ID |
| `conversation_id` | `str` | 会话 ID |
| `bot_id` | `str` | Bot ID |
| `status` | `ChatStatus` | 对话状态 |
| `created_at` | `int` | 创建时间戳 |
| `completed_at` | `int` | 完成时间戳 |
| `failed_at` | `int` | 失败时间戳 |
| `usage` | `ChatUsage` | Token 用量（`token_count` 字段） |
| `last_error` | `ChatError \| None` | 错误信息（code + msg） |
| `required_action` | `ChatRequiredAction \| None` | 需要执行的动作（工具调用） |
| `meta_data` | `dict` | 元数据 |

## 工具调用（Function Calling）

当 Bot 配置了插件/工具时，模型可能在对话中请求执行工具调用。此时 `Chat.required_action` 包含工具调用信息：

### 工具调用模型

- **ChatRequiredAction**：包含需要提交的工具输出信息
- **ChatSubmitToolOutputs**：工具调用列表容器
- **ChatToolCall**：单次工具调用，包含 ID、类型和函数信息
- **ChatToolCallFunction**：函数名和参数（`name` + `arguments` JSON 字符串）
- **ChatToolCallType**：工具调用类型枚举
- **ToolOutput**：工具执行结果（`tool_call_id` + `output`）

### 工具调用流程

```
用户提问 → 模型判断需要调用工具 → 返回 required_action →
开发者执行工具 → 提交工具结果 → 模型继续生成最终回答
```

工具调用在流式对话中的处理需要监听相关事件类型，当检测到 `required_action` 时，执行对应函数并通过 `ChatSubmitToolOutputs` 提交结果。

## ChatMessagesClient

通过 `coze.chat.message` 访问的 `ChatMessagesClient` 提供对话中消息的管理能力，可以查询、检索已发送的消息。

## SSE 流处理器

内部的 `_chat_stream_handler` 是 SSE 事件解析的核心。它负责：
1. 逐行读取 HTTP 响应体中的 SSE 数据
2. 解析 `event:` 和 `data:` 字段
3. 将 JSON 数据反序列化为对应的 `ChatEvent` 子类
4. 被 Chat 和 Workflows Chat 两个模块复用，保证事件格式的一致性

## 异常处理

对话过程中可能遇到的错误：

```python
from cozepy import CozeAPIError, CozeInvalidEventError

try:
    for event in coze.chat.stream(...):
        ...
except CozeAPIError as e:
    print(f"API 错误: code={e.code}, msg={e.msg}, logid={e.logid}")
    # debug_url 可用于在 Coze 平台查看详细日志
    print(f"调试链接: {e.debug_url}")
except CozeInvalidEventError as e:
    print(f"事件解析错误: {e}")
```

`CozeAPIError` 的 `logid` 字段在排查问题时非常重要，提供给 Coze 技术支持可以快速定位请求。

## 相关概念

- [客户端初始化与配置](02-client-init.md) — 创建客户端后才能发起对话
- [Bot 管理](04-bot-management.md) — 创建和管理 Bot
- [工作流](05-workflows.md) — 工作流式对话（ChatEvent 复用）
- [会话管理](06-conversations.md) — 显式管理会话生命周期
- [基础对话示例](../examples/basic-chat.md) — 完整的流式对话代码示例
- [对话与工作流参考](../references/chat-workflow.md) — ChatClient 和 Message 模型的完整 API
