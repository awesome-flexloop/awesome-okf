---
type: reference
title: "对话与工作流参考"
description: "ChatClient/AsyncChatClient、消息模型、SSE 流式事件、WorkflowClient 及工作流运行/异步中断恢复的完整 API 参考。"
tags: [chat, message, sse, streaming, workflow, conversation]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cp-003
    resource: /references/chat-workflow.md
    title: "对话与工作流参考"
---

# 对话与工作流参考

本文档登记 Chat（对话）与 Workflow（工作流）两大核心模块的客户端类、数据模型、枚举类型和流式处理机制。

## Chat 模块

### ChatClient / AsyncChatClient

对话客户端，提供与 Bot 的对话能力。通过 `coze.chat` / `async_coze.chat` 访问。

#### 核心方法

**stream()** — 流式对话（SSE）

```python
chat.stream(
    bot_id: str,
    user_id: str,
    additional_messages: List[Message],
    conversation_id: str | None = None,
    # **kwargs 支持自定义 headers
) -> Stream[ChatEvent]
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `bot_id` | `str` | ✅ | Bot ID |
| `user_id` | `str` | ✅ | 用户标识 |
| `additional_messages` | `List[Message]` | ✅ | 本次对话追加的消息列表 |
| `conversation_id` | `str \| None` | ❌ | 会话 ID，不传则创建新会话 |

返回 `Stream[ChatEvent]`，遍历可逐个获取 SSE 事件。

### Chat 数据模型

#### Chat

对话实例模型：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `str` | 对话 ID |
| `conversation_id` | `str` | 所属会话 ID |
| `bot_id` | `str` | Bot ID |
| `status` | `ChatStatus` | 对话状态 |
| `created_at` | `int` | 创建时间（Unix 时间戳） |
| `completed_at` | `int` | 完成时间 |
| `failed_at` | `int` | 失败时间 |
| `meta_data` | `dict` | 元数据 |
| `last_error` | `ChatError \| None` | 最后的错误信息 |
| `required_action` | `ChatRequiredAction \| None` | 需要执行的动作（如工具调用） |
| `usage` | `ChatUsage` | Token 用量统计 |

#### ChatStatus（枚举）

对话状态枚举，表示对话的生命周期阶段。

#### ChatEvent

流式事件模型，封装 SSE 事件数据。

#### ChatEventType（枚举）

SSE 事件类型枚举，包含：

| 事件类型 | 说明 |
|----------|------|
| `CONVERSATION_MESSAGE_DELTA` | 消息增量（正在生成） |
| `CONVERSATION_CHAT_COMPLETED` | 对话完成 |
| `CONVERSATION_MESSAGE_COMPLETED` | 单条消息完成 |
| 其他事件类型 | 错误、中断等 |

#### ChatError

对话错误模型：

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | `int` | 错误码 |
| `msg` | `str` | 错误信息 |

#### ChatUsage

Token 用量统计：

| 字段 | 类型 | 说明 |
|------|------|------|
| `token_count` | `int` | Token 消耗总数 |

#### ChatPoll

对话轮询工具，用于非流式场景下轮询对话状态。

#### InsertedMessage

插入消息模型，表示在对话中插入的消息。

### Message 模型

#### Message

| 字段 | 类型 | 说明 |
|------|------|------|
| `role` | `MessageRole` | 消息角色（user/assistant） |
| `type` | `str` | 消息类型 |
| `content` | `str` | 消息内容 |
| `content_type` | `str` | 内容类型 |
| `meta_data` | `dict` | 元数据 |

#### MessageRole（枚举）

| 值 | 说明 |
|----|------|
| `USER` = `"user"` | 用户消息 |
| `ASSISTANT` = `"assistant"` | 助手消息 |

#### Message 静态方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `build_user_question_text` | `(content: str) -> Message` | 构建用户文本问题消息 |
| `build_assistant_answer` | `(content: str) -> Message` | 构建助手回答消息 |

### 工具调用模型

#### ChatToolCall

工具调用模型，表示模型请求执行的工具调用。

#### ChatToolCallFunction

工具调用函数信息：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 函数名 |
| `arguments` | `str` | 函数参数（JSON 字符串） |

#### ChatToolCallType（枚举）

工具调用类型枚举。

#### ChatRequiredAction

需要执行的动作模型，当 Bot 需要调用工具时返回。

#### ChatSubmitToolOutputs

提交工具执行结果模型。

#### ToolOutput

工具输出结果：

| 字段 | 类型 | 说明 |
|------|------|------|
| `tool_call_id` | `str` | 工具调用 ID |
| `output` | `str` | 工具执行结果 |

### ChatMessagesClient / AsyncChatMessagesClient

Chat 的子客户端，管理对话中的消息。通过 `chat.message` 访问。

### SSE 流式处理

#### _chat_stream_handler

内部 SSE 事件解析处理器，被 Chat 和 Workflows Chat 模块复用。负责解析 Server-Sent Events 格式数据并转换为 `ChatEvent` 对象。

---

## Workflow 模块

### WorkflowsClient / AsyncWorkflowsClient

工作流客户端，通过 `coze.workflows` / `async_coze.workflows` 访问。

### 工作流基础模型

#### WorkflowBasic

工作流基础信息：

| 字段 | 类型 | 说明 |
|------|------|------|
| `workflow_id` | `str` | 工作流 ID |
| `name` | `str` | 工作流名称 |
| `description` | `str` | 描述 |

#### WorkflowInfo

工作流详细信息，继承 WorkflowBasic，包含更多元数据。

#### WorkflowMode（枚举）

工作流运行模式枚举。

#### WorkflowVersionInfo

工作流版本信息模型。

#### WorkflowRunResult

工作流运行结果模型。

#### WorkflowRunHistory

工作流运行历史记录模型。

### 子客户端

通过 `workflows.xxx` 访问：

| 属性 | 类型 | 说明 |
|------|------|------|
| `.chat` | `WorkflowsChatClient` | 工作流式对话 |
| `.collaborators` | WorkflowCollaboratorsClient | 协作者管理 |
| `.versions` | WorkflowVersionsClient | 版本管理 |
| `.runs` | `WorkflowsRunsClient` | 工作流运行 |
| `.run_histories` | WorkflowRunHistoriesClient | 运行历史 |

### WorkflowsChatClient / AsyncWorkflowsChatClient

工作流式对话客户端，将工作流作为对话入口。

#### stream()

```python
workflows.chat.stream(
    workflow_id: str,
    additional_messages: List[Message],
    parameters: dict | None = None,
    app_id: str | None = None,
    bot_id: str | None = None,
    conversation_id: str | None = None,
    ext: dict | None = None,
) -> Stream[ChatEvent]
```

HTTP 端点：`POST /v1/workflows/chat`

| 参数 | 类型 | 说明 |
|------|------|------|
| `workflow_id` | `str` | 工作流 ID |
| `additional_messages` | `List[Message]` | 追加消息 |
| `parameters` | `dict \| None` | 工作流输入参数 |
| `app_id` | `str \| None` | 应用 ID |
| `bot_id` | `str \| None` | Bot ID |
| `conversation_id` | `str \| None` | 会话 ID |
| `ext` | `dict \| None` | 扩展字段 |

### WorkflowsRunsClient / AsyncWorkflowsRunsClient

工作流运行客户端。

#### stream()

```python
workflows.runs.stream(...) -> Stream[WorkflowEvent]
```

返回 `Stream[WorkflowEvent]`，支持工作流异步运行模式。

#### 中断与恢复

工作流运行支持中断（interrupt）和恢复（resume）机制。当工作流执行到需要人工介入的节点时，会产生 `WorkflowEventInterrupt` 事件。

### WorkflowEvent 模型

#### WorkflowEvent 类型

| 事件类型 | 对应类 | 说明 |
|----------|--------|------|
| `MESSAGE` | `WorkflowEventMessage` | 工作流消息事件 |
| `ERROR` | `WorkflowEventError` | 工作流错误事件 |
| `INTERRUPT` | `WorkflowEventInterrupt` | 工作流中断事件 |

#### WorkflowEventMessage

工作流消息事件，携带输出数据。

#### WorkflowEventError

工作流错误事件：

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | `int` | 错误码 |
| `message` | `str` | 错误信息 |

#### WorkflowEventInterrupt

工作流中断事件：

| 字段 | 类型 | 说明 |
|------|------|------|
| `data` | `WorkflowEventInterruptData` | 中断数据 |

#### WorkflowEventInterruptData

中断数据模型，包含中断节点信息和需要用户提供的数据。
