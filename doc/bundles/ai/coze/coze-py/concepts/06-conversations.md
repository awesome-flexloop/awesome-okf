---
type: concept
title: "会话管理"
description: "掌握 Conversation 的完整生命周期——创建、查询、更新、删除，以及消息管理和消息反馈机制。"
tags: [conversation, message, feedback, lifecycle, section]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cp-005
    resource: /references/data-pagination.md
    title: "数据模型、分页与资源管理参考"
  - id: F-cp-003
    resource: /references/chat-workflow.md
    title: "对话与工作流参考"
---

# 会话管理

会话（Conversation）是对话上下文的容器。一次对话（Chat）发生在一个会话中，同一会话内的多轮对话共享上下文历史。`ConversationsClient` 提供了会话的显式生命周期管理——创建、查询、更新、删除，以及会话内消息的管理和反馈功能。

## ConversationsClient 入口

`ConversationsClient`（异步版本 `AsyncConversationsClient`）通过 `coze.conversations` 访问。它包含两个子客户端：

```
ConversationsClient
├── .message             → MessagesClient        消息管理
│   └── .feedback        → ConversationsMessagesFeedbackClient  消息反馈
└── (会话级操作: create/list/retrieve/update/delete)
```

## 会话生命周期

### 创建会话

使用 `conversations.create()` 显式创建会话：

```python
from cozepy import Coze, TokenAuth, COZE_CN_BASE_URL

coze = Coze(auth=TokenAuth(token="your_token"), base_url=COZE_CN_BASE_URL)

# 创建新会话
conversation = coze.conversations.create(
    bot_id="your_bot_id",  # 可选：关联 Bot
    # meta_data={},        # 可选：元数据
)
print(f"会话 ID: {conversation.id}")
```

创建会话后获得 `conversation.id`，可以在后续的 `chat.stream()` 中传入 `conversation_id` 来在同一会话中进行多轮对话。

### 查询会话

```python
# 获取单个会话详情
conv = coze.conversations.retrieve(conversation_id="conv_id")
print(f"会话 ID: {conv.id}, 创建时间: {conv.created_at}")
```

### 列出会话

使用 `conversations.list()` 列出会话，支持分页：

```python
# 遍历所有会话
for conv in coze.conversations.list(bot_id="bot_id", user_id="user_123"):
    print(f"会话: {conv.id}")
```

### 更新会话

```python
updated = coze.conversations.update(
    conversation_id="conv_id",
    # meta_data={"key": "value"},  # 更新元数据
)
```

### 删除会话

```python
resp = coze.conversations.delete(conversation_id="conv_id")
# resp 是 DeleteConversationResp 类型
```

删除会话后，该会话的所有消息和上下文将被清除，无法恢复。

## Conversation 模型

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `str` | 会话唯一 ID |
| `created_at` | `int` | 创建时间（Unix 时间戳） |
| `meta_data` | `dict` | 自定义元数据 |
| 其他字段 | - | Bot 关联、最后活跃时间等 |

### Section 模型

`Section`（分段）是会话内的消息分组机制，用于组织长对话中的不同阶段或主题。

### DeleteConversationResp

删除会话的响应模型，确认删除操作的结果。

## 消息管理（MessagesClient）

通过 `conversations.message` 访问消息管理客户端。消息是会话内的对话内容单元。

### MessagesClient 能力

`MessagesClient`/`AsyncMessagesClient` 提供对会话内消息的 CRUD 操作：

- **创建消息**：向会话插入消息（历史消息或系统消息）
- **列出消息**：查询会话内的消息列表（分页）
- **检索消息**：获取单条消息详情
- **更新消息**：修改消息元数据
- **删除消息**：删除特定消息

```python
# 列出会话中的消息
for msg in coze.conversations.message.list(conversation_id="conv_id"):
    print(f"[{msg.role}] {msg.content[:50]}...")
```

## 消息反馈（Feedback）

通过 `conversations.message.feedback` 访问消息反馈客户端。反馈机制让用户可以对 Bot 的回复进行评价（如点赞/点踩），用于改进模型质量。

### FeedbackType（枚举）

消息反馈类型枚举，定义了支持的反馈类型（如点赞、点踩等）。

```python
from cozepy import FeedbackType

# 对消息提交反馈
coze.conversations.message.feedback.create(
    conversation_id="conv_id",
    message_id="msg_id",
    feedback_type=FeedbackType.LIKE,  # 点赞
    # comment="写得很好",  # 可选：反馈评论
)
```

## 会话 vs 对话：概念区分

理解**会话（Conversation）**和**对话（Chat）**的区别很重要：

| 维度 | 会话（Conversation） | 对话（Chat） |
|------|---------------------|-------------|
| 含义 | 上下文容器，持久存储 | 一次交互，有始有终 |
| 生命周期 | 可创建/删除/长期存在 | 创建→完成/失败，瞬时 |
| 关系 | 一个会话包含多次对话 | 每次对话属于一个会话 |
| 类比 | 聊天室/房间 | 房间里的一次发言回合 |
| 管理方式 | conversations.create/delete | chat.stream() 隐式创建 |

简单来说：你创建一个"会话"（房间），然后在其中进行多次"对话"（发言回合），每次对话都可以引用之前的上下文。

## 隐式会话 vs 显式会话

使用 `chat.stream()` 时有两种会话管理方式：

### 隐式会话（不传 conversation_id）

```python
# 不传 conversation_id，SDK 自动创建新会话
for event in coze.chat.stream(
    bot_id="bot_id",
    user_id="user_123",
    additional_messages=[Message.build_user_question_text("你好")],
):
    if event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
        conv_id = event.chat.conversation_id  # 从完成事件中获取会话 ID
```

适合简单场景，不需要提前管理会话。

### 显式会话（先创建再传入）

```python
# 1. 先创建会话
conv = coze.conversations.create(bot_id="bot_id")

# 2. 在会话中进行多轮对话
for event in coze.chat.stream(
    bot_id="bot_id",
    user_id="user_123",
    additional_messages=[Message.build_user_question_text("第一轮")],
    conversation_id=conv.id,  # 显式传入
):
    ...

# 3. 后续对话继续使用同一个 conv_id
for event in coze.chat.stream(
    bot_id="bot_id",
    user_id="user_123",
    additional_messages=[Message.build_user_question_text("第二轮")],
    conversation_id=conv.id,  # 同一会话
):
    ...
```

适合需要预配置会话（如设置元数据）、提前准备、或在多个对话之间共享和管理会话的场景。

## 会话管理最佳实践

1. **显式创建会话**用于需要长期保存的对话记录，便于后续检索和管理
2. **使用 meta_data**存储业务关联信息（如订单号、用户标签等），方便查询
3. **及时删除不需要的会话**，避免数据堆积
4. **使用消息反馈**收集用户满意度数据，持续优化 Bot 表现
5. **多轮对话务必传入 conversation_id**，否则每轮都是新会话，无法保持上下文

## 相关概念

- [对话与流式处理](/concepts/03-chat-streaming.md) — chat.stream() 中 conversation_id 的使用
- [Bot 管理](/concepts/04-bot-management.md) — 会话关联的 Bot
- [分页模式与资源管理](/concepts/09-pagination-resources.md) — 会话列表的分页遍历
- [基础对话示例](/examples/basic-chat.md) — 多轮对话示例
- [数据模型、分页与资源管理参考](/references/data-pagination.md) — Conversation/Section 模型的完整 API
