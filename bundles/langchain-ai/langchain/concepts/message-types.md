---
type: concept
title: 消息类型体系
description: BaseMessage 继承体系、AIMessage 的 tool_calls 与 usage_metadata、ToolMessage 的关联机制、ContentBlock 多模态内容
tags: [langchain, messages, aimessage, toolmessage, content-block]
generated: { by: "reference_agent/trae-solo", at: 2026-08-23 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23 }
status: stable
stale_after: 2027-02-23
sources:
  - id: ref-msg
    resource: /references/messages-tools.md
    title: 消息与工具源码信源
---

# 消息类型体系

消息（Message）是聊天模型的输入输出单元。langchain-core 在 `messages/` 目录定义了以 `BaseMessage` 为根的消息类型体系，覆盖对话中的四种角色（人类、系统、AI、工具），并标准化了工具调用、token 用量和多模态内容。

## 继承体系

```
BaseMessage(Serializable)          messages/base.py:93
├── HumanMessage                   messages/human.py:9      (type="human")
│   └── HumanMessageChunk          messages/human.py:63
├── SystemMessage                  messages/system.py:9     (type="system")
│   └── SystemMessageChunk         messages/system.py:63
├── AIMessage                      messages/ai.py:160       (type="ai")
│   └── AIMessageChunk             messages/ai.py:418
└── ToolMessage(ToolOutputMixin)   messages/tool.py:26      (type="tool")
    └── ToolMessageChunk           messages/tool.py:174

BaseMessageChunk(BaseMessage)      messages/base.py:409     (流式分块基类)
```

`BaseMessageChunk` 是所有流式分块消息的基类，定义了抽象方法 `__add__`（`messages/base.py:412`）用于将多个分块合并为完整消息。每个具体消息类型都有对应的 Chunk 变体。

## BaseMessage 基础字段

`BaseMessage`（`messages/base.py:93`）定义以下字段：

| 字段 | 类型 | 行号 | 说明 |
|---|---|---|---|
| `content` | `str \| list[str \| dict]` | 103 | 消息内容，可为纯字符串或 content block 列表 |
| `additional_kwargs` | `dict[Any, Any]` | 106 | 保留给 provider 特定附加数据 |
| `response_metadata` | `dict[Any, Any]` | 114 | 响应元数据（响应头、logprobs、token 数、模型名） |
| `type` | `str` | 117 | 消息类型标识，用于反序列化 |
| `name` | `str \| None` | 125 | 可选名称 |
| `id` | `str \| None` | 135 | 可选唯一标识（数字自动转字符串） |

`model_config = ConfigDict(extra="allow")`（第142行）允许 provider 特定的额外字段。`is_lc_serializable` 返回 `True`，`get_lc_namespace` 返回 `["langchain", "schema", "messages"]`。

### text 属性与 TextAccessor

`text` 属性（第263行）返回 `TextAccessor` 实例。`TextAccessor`（第47行）继承自 `str`，同时支持两种访问方式：
- 现代方式：`message.text`（属性，直接返回字符串）
- 遗留方式：`message.text()`（方法调用，发出弃用警告，将在 2.0.0 移除）

这种设计是为了在 v1.0 从方法迁移到属性时保持向后兼容。

### content_blocks 属性

`content_blocks`（第200行）将 `content` 懒解析为 `list[ContentBlock]`。`AIMessage` 重写了此属性（`messages/ai.py:243`）：如果 `response_metadata["model_provider"]` 存在，使用 provider 特定的 block translator；否则 best-effort 解析，并自动将 `tool_calls` 补入 content blocks。

## HumanMessage / SystemMessage

- **`HumanMessage`**（`messages/human.py:9`）：表示用户输入，`type="human"`。
- **`SystemMessage`**（`messages/system.py:9`）：表示系统指令，`type="system"`。

两者字段均继承自 `BaseMessage`，构造函数支持 `content` 位置参数或 `content_blocks` 关键字参数。

## AIMessage

`AIMessage`（`messages/ai.py:160`）是模型返回的响应消息，在 `BaseMessage` 基础上增加了标准化字段：

| 字段 | 类型 | 行号 | 说明 |
|---|---|---|---|
| `tool_calls` | `list[ToolCall]` | 170 | 工具调用请求列表 |
| `invalid_tool_calls` | `list[InvalidToolCall]` | 173 | 解析失败的工具调用 |
| `usage_metadata` | `UsageMetadata \| None` | 176 | token 用量统计 |
| `type` | `Literal["ai"]` | 182 | 固定 `"ai"` |

`lc_attributes`（第231行）返回 `{"tool_calls": ..., "invalid_tool_calls": ...}`，确保这两个派生字段被纳入序列化。

### UsageMetadata

`UsageMetadata`（`messages/ai.py:104`）是 TypedDict，标准化跨模型的 token 用量：

```python
{
    "input_tokens": 350,
    "output_tokens": 240,
    "total_tokens": 590,
    "input_token_details": {"audio": 10, "cache_creation": 200, "cache_read": 100},
    "output_token_details": {"audio": 10, "reasoning": 200},
}
```

必填字段为 `input_tokens`、`output_tokens`、`total_tokens`（第138-145行），`input_token_details`/`output_token_details` 为可选细分（v0.3.9 引入）。

### AIMessageChunk

`AIMessageChunk`（`messages/ai.py:418`）是流式分块变体：
- `init_tool_calls(self) -> Self`（第509行）：补全 tool_calls 字段。
- `init_server_tool_calls(self) -> Self`（第604行）：补全 server tool calls。
- `__add__`（第633行）：合并两个分块，拼接 content 和 tool_call_chunks。

## ToolMessage 与 ToolCall

### ToolCall

`ToolCall`（`messages/tool.py:206`）是 TypedDict，表示 AI 请求调用工具：

| 字段 | 类型 | 行号 | 说明 |
|---|---|---|---|
| `name` | `str` | 225 | 要调用的工具名 |
| `args` | `dict[str, Any]` | 228 | 工具参数 |
| `id` | `str \| None` | 231 | 调用 ID，关联请求与结果 |
| `type` | `NotRequired[Literal["tool_call"]]` | 238 | 可选鉴别字段 |

工厂函数 `tool_call(*, name, args, id) -> ToolCall`（第242行）在创建时校验必填参数。`ToolCallChunk`（第261行）是流式分块版本，按 `index` 合并。

### ToolMessage

`ToolMessage`（`messages/tool.py:26`）将工具执行结果传回模型，同时继承 `ToolOutputMixin`（第16行，标记工具可直接返回的类型）：

| 字段 | 类型 | 行号 | 说明 |
|---|---|---|---|
| `tool_call_id` | `str` | 67 | 关联的工具调用 ID（必填） |
| `type` | `Literal["tool"]` | 70 | 固定 `"tool"` |
| `artifact` | `Any` | 73 | 不发给模型的执行产物 |
| `status` | `Literal["success", "error"]` | 81 | 调用状态，默认 `"success"` |

`@model_validator(mode="before")` 的 `coerce_args`（第92行）自动：
- 将 tuple 类型的 content 转为 list；
- 将非 str/list 的 content 转为 str；
- 将 list 中的非 str/dict 元素转为 str；
- 将 UUID/int/float 类型的 `tool_call_id` 转为 str。

当多个工具并行调用时，`tool_call_id` 用于将每个 `ToolMessage` 与 `AIMessage.tool_calls` 中对应的请求关联。

## ContentBlock 多模态内容

`content` 字段支持字符串或 content block 字典列表。`ContentBlock`（`messages/content.py:844`）是所有内容块类型的联合：

```python
ContentBlock = (
    TextContentBlock
    | InvalidToolCall
    | ReasoningContentBlock
    | NonStandardContentBlock
    | DataContentBlock          # Image | Video | Audio | File | PlainText
    | ToolContentBlock          # ToolCall | ToolCallChunk | ServerToolCall | ...
)
```

`DataContentBlock`（第831行）覆盖多模态数据：`ImageContentBlock`、`VideoContentBlock`、`AudioContentBlock`、`PlainTextContentBlock`、`FileContentBlock`。

`KNOWN_BLOCK_TYPES`（第855行）集合包含已知块类型字符串：`"text"`、`"reasoning"`、`"tool_call"`、`"invalid_tool_call"`、`"tool_call_chunk"`、`"image"`、`"audio"`、`"file"`、`"text-plain"`、`"video"` 等。

典型文本块形式为 `{"type": "text", "text": "..."}`，图片块为 `{"type": "image", "source": {...}}`，工具调用块为 `{"type": "tool_call", "name": "...", "args": {...}, "id": "..."}`。

## 消息相加

`BaseMessage.__add__`（`messages/base.py:294`）返回 `ChatPromptTemplate`，允许用 `+` 将消息组合成聊天提示词模板。`BaseMessageChunk.__add__`（第412行）用于流式分块合并，各子类实现具体的合并逻辑（拼接 content、合并 tool_calls、合并 usage_metadata）。

## 代码示例

```python
from langchain_core.messages import (
    HumanMessage, SystemMessage, AIMessage, ToolMessage,
)
from langchain_core.messages.tool import tool_call

# 1. 基本消息
messages = [
    SystemMessage("你是一个助手"),
    HumanMessage("北京天气怎么样？"),
]

# 2. AIMessage 带工具调用
ai_msg = AIMessage(
    content="",
    tool_calls=[
        tool_call(name="get_weather", args={"city": "北京"}, id="call_001")
    ],
    usage_metadata={"input_tokens": 50, "output_tokens": 20, "total_tokens": 70},
)

# 3. ToolMessage 关联结果
tool_msg = ToolMessage(
    content="北京今天晴，25°C",
    tool_call_id="call_001",
    status="success",
)

# 4. 读取文本（属性方式）
assert ai_msg.text == ""

# 5. 流式分块合并
from langchain_core.messages import AIMessageChunk
chunk1 = AIMessageChunk(content="Hello")
chunk2 = AIMessageChunk(content=" world")
full = chunk1 + chunk2  # AIMessageChunk(content="Hello world")
```

## 相关概念

- [总览](/langchain-ai/langchain/concepts/overview) —— 消息在数据层中的位置
- [工具抽象](/langchain-ai/langchain/concepts/tool-abstraction) —— ToolCall 与 ToolMessage 的协作
- [聊天模型](/langchain-ai/langchain/concepts/chat-model) —— AIMessage 是模型的输出类型
- [提示词系统](/langchain-ai/langchain/concepts/prompt-system) —— 消息可通过 + 组合为提示词模板
