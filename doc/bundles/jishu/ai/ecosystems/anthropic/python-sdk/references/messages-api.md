---
type: reference
title: "Anthropic Python SDK 消息 API 与流式处理参考"
description: "Messages 资源类、create 方法参数、Batches 子资源、废弃模型列表、流式事件类型与 MessageStream 高级流式接口的完整 API 参考。"
tags: [messages, streaming, sse, batches, api]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-016~F-037
    resource: /python-sdk/references/messages-api.md
    title: "Anthropic Python SDK 消息 API 与流式处理参考"
---

# Anthropic Python SDK 消息 API 与流式处理参考

本文档登记 Messages（消息）API 资源类、create 方法参数、Batches 子资源、废弃模型列表、流式处理（Streaming）核心类与 SSE 事件类型。

## Messages 资源类

**类路径**：`anthropic.resources.messages.Messages`

`Messages` 类继承自 `SyncAPIResource`，定义在 `anthropic/resources/messages/messages.py`，是消息 API 的同步入口。异步版本为 `AsyncMessages`，API 完全对称。

### Batches 子资源

`Messages` 类通过 `@cached_property` 定义 `batches` 属性，返回 `Batches` 实例，用于消息批量操作。

### 响应装饰属性

| 属性 | 返回类型 | 说明 |
|------|---------|------|
| `.with_raw_response` | `MessagesWithRawResponse` | 返回原始 HTTP 响应的包装 |
| `.with_streaming_response` | `MessagesWithStreamingResponse` | 返回流式响应的包装 |

### create 方法

```python
Messages.create(
    *,
    max_tokens: int,
    messages: Iterable[MessageParam],
    model: ModelParam,
    cache_control: CacheControlEphemeralParam | NotGiven | None = ...,
    container: ContainerParam | NotGiven | None = ...,
    inference_geo: InferenceGeoParam | NotGiven | None = ...,
    metadata: MetadataParam | NotGiven | None = ...,
    output_config: OutputConfigParam | NotGiven | None = ...,
    service_tier: ServiceTierParam | NotGiven | None = ...,
    stop_sequences: List[str] | NotGiven = ...,
    stream: Literal[False] | Literal[True] | NotGiven = ...,
    system: SystemParamType | NotGiven = ...,
    thinking: ThinkingConfigParam | NotGiven | None = ...,
    tool_choice: ToolChoiceParam | NotGiven | None = ...,
    tools: Iterable[ToolParam] | NotGiven = ...,
    user_profile_id: str | NotGiven | None = ...,
    # + 额外 kwargs 传递给底层 HTTP 方法
) -> Message | Stream[MessageStreamEvent]
```

**必填参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `max_tokens` | `int` | 生成的最大 token 数 |
| `messages` | `Iterable[MessageParam]` | 输入消息序列，包含对话历史 |
| `model` | `ModelParam` | 模型标识符，如 `"claude-3-5-sonnet-latest"` |

**可选参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `stream` | `bool` | 是否启用流式响应，`False` 返回 `Message`，`True` 返回 `Stream[MessageStreamEvent]` |
| `system` | `SystemParamType` | 系统提示词 |
| `thinking` | `ThinkingConfigParam` | Extended Thinking 思考模式配置 |
| `tools` | `Iterable[ToolParam]` | 工具定义列表（Function Calling） |
| `tool_choice` | `ToolChoiceParam` | 工具选择策略 |
| `stop_sequences` | `List[str]` | 停止序列列表 |
| `metadata` | `MetadataParam` | 请求元数据 |
| `cache_control` | `CacheControlEphemeralParam` | 提示词缓存控制 |
| `container` | `ContainerParam` | 容器配置 |
| `inference_geo` | `InferenceGeoParam` | 推理地理区域配置 |
| `output_config` | `OutputConfigParam` | 输出配置 |
| `service_tier` | `ServiceTierParam` | 服务层级 |
| `user_profile_id` | `str` | 用户配置文件 ID |

**返回值**：

- `stream=False`（默认）：返回 `Message` 对象，包含完整的响应内容
- `stream=True`：返回 `Stream[MessageStreamEvent]` 迭代器，逐个产生流式事件

## 模型常量

### DEPRECATED_MODELS

已废弃模型字典，定义在 `messages.py`：

| 模型 ID | 废弃日期 |
|---------|---------|
| `"claude-1.3"` | - |
| `"claude-instant-1.2"` | - |
| `"claude-3-sonnet-20240229"` | - |
| `"claude-3-opus-20240229"` | - |

### MODELS_TO_WARN_WITH_THINKING_ENABLED

启用 Extended Thinking 时需要警告的模型列表：

```python
["claude-opus-4-6", "claude-mythos-preview"]
```

### MODEL_NONSTREAMING_TOKENS

定义在 `_constants.py`，部分模型的非流式 token 限制为 8192：

| 模型 ID | 非流式 token 限制 |
|---------|------------------|
| `"claude-opus-4-20250514"` | 8192 |
| （其他模型） | 8192 |

## 流式处理核心类

### Stream（同步流）

**类路径**：`anthropic.Stream[_T]`

泛型同步流响应包装类，定义在 `_streaming.py`，提供同步 SSE 事件迭代接口。

**构造函数**：

```python
Stream(
    cast_to: type[_T],
    response: httpx.Response,
    client: Anthropic,
    options: FinalRequestOptions | None = None,
)
```

**核心协议支持**：

- **上下文管理器**：支持 `with stream:` 语法，自动管理资源
- **迭代器协议**：支持 `for event in stream:` 语法，逐个迭代解析后的事件

**SSE 事件类型处理**：

| SSE 事件类型 | 对应事件类 |
|-------------|-----------|
| `"message_start"` | `MessageStartEvent` |
| `"message_delta"` | `MessageDeltaEvent` |
| `"message_stop"` | `MessageStopEvent` |
| `"content_block_start"` | `ContentBlockStartEvent` |
| `"content_block_delta"` | `ContentBlockDeltaEvent` |
| `"content_block_stop"` | `ContentBlockStopEvent` |
| `"agent.message"` | Agent 相关消息事件 |
| `"agent.thinking"` | Agent 思考事件 |
| `"agent.tool_use"` | Agent 工具使用事件 |
| `"agent.tool_result"` | Agent 工具结果事件 |
| `"agent.mcp_tool_use"` | Agent MCP 工具使用事件 |
| `"error"` | 错误事件（自动抛出异常） |

> 当收到 `"error"` 事件时，`Stream` 会调用 `self._client._make_status_error` 抛出对应的异常。

### AsyncStream（异步流）

**类路径**：`anthropic.AsyncStream[_T]`

泛型异步流响应包装类，与 `Stream` 对称，提供异步迭代接口。使用 `async for event in stream:` 语法迭代事件。

## SSE 底层实现

### ServerSentEvent

**类路径**：`anthropic._streaming.ServerSentEvent`

SSE 事件数据模型：

| 属性 | 类型 | 说明 |
|------|------|------|
| `event` | `str` | 事件类型名称 |
| `data` | `str` | 事件数据（JSON 字符串） |
| `id` | `str \| None` | 事件 ID |
| `retry` | `int \| None` | 重试间隔（毫秒） |
| `raw` | `list[str]` | 原始 SSE 行 |

### SSEDecoder

**类路径**：`anthropic._streaming.SSEDecoder`

SSE 协议解码器，负责将字节流解析为 `ServerSentEvent` 对象：

| 方法 | 签名 | 说明 |
|------|------|------|
| `iter_bytes` | `(iterator: Iterator[bytes]) -> Iterator[ServerSentEvent]` | 同步迭代字节流，产出 SSE 事件 |
| `aiter_bytes` | `(iterator: AsyncIterator[bytes]) -> AsyncIterator[ServerSentEvent]` | 异步迭代字节流，产出 SSE 事件 |
| `decode` | `(line: str) -> ServerSentEvent \| None` | 解码单行 SSE 数据 |

## lib/streaming 高级流式模块

### MessageStream

**类路径**：`anthropic.lib.streaming.MessageStream[ResponseFormatT]`

定义在 `lib/streaming/_messages.py`，提供更高级的消息流处理接口。

| 属性/方法 | 签名 | 说明 |
|----------|------|------|
| `.text_stream` | `Iterator[str]` | 纯文本内容流迭代器 |
| `get_final_message()` | `() -> Message` | 累积所有事件后返回最终的完整 `Message` 对象 |
| `get_final_text()` | `() -> str` | 累积所有事件后返回最终的纯文本内容 |
| `until_done()` | `() -> None` | 阻塞直到流结束，处理所有事件 |

### MessageStreamManager

**类路径**：`anthropic.lib.streaming.MessageStreamManager[ResponseFormatT]`

`MessageStream` 的上下文管理器包装类，用于 `with` 语句中安全管理流资源。

```python
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    final_message = stream.get_final_message()
```

## 流式事件生命周期

标准的流式响应事件序列如下：

```
MessageStartEvent
  └─ ContentBlockStartEvent (重复，每个内容块一次)
       └─ ContentBlockDeltaEvent (重复，每个增量一次)
       └─ ContentBlockStopEvent
  └─ MessageDeltaEvent (最终 token 统计)
MessageStopEvent
```
