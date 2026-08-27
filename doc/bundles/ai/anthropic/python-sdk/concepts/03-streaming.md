---
type: concept
title: "流式响应处理"
description: "掌握 Claude 流式输出的两种使用方式：基础 Stream 事件迭代和高级 MessageStream 便捷接口，理解 SSE 事件类型层次，实现实时打字效果、工具调用流处理与同步/异步双轨流式编程。"
tags: [streaming, sse, real-time, text-stream, async-stream, context-manager]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-026~F-037
    resource: /python-sdk/references/messages-api.md
    title: "Anthropic Python SDK 消息 API 与流式处理参考"
  - id: F-001~F-015
    resource: /python-sdk/references/sdk-client.md
    title: "Anthropic Python SDK 客户端入口与基础设施参考"
---

# 流式响应处理

流式响应（Streaming Response）是大语言模型 API 的重要特性，它通过 SSE（Server-Sent Events，服务器发送事件）协议在模型生成 token 的同时逐个返回增量内容，而不是等待完整响应生成完毕后一次性返回。对于聊天界面、实时交互、长文本生成等场景，流式处理能显著降低用户感知等待时间，提供流畅的"打字机"体验。

本文档将讲解流式处理的核心概念、两种使用方式、事件类型层次结构，以及如何处理文本流和工具调用流。

## 为什么需要流式

在非流式模式下，你必须等待 Claude 生成完整回复后才能收到结果。对于一个生成 1000 个 token 的回复，假设模型每秒生成 50 个 token，用户需要等待约 20 秒才能看到第一个字。而在流式模式下，第一个 token 通常在几百毫秒内就能返回，之后每几十毫秒返回一个增量，用户可以边看 Claude 生成边阅读，感知等待时间大幅缩短。

**流式 vs 非流式对比**：

| 维度 | 非流式（默认） | 流式（stream=True） |
|------|---------------|---------------------|
| 首字延迟 | 等待完整生成（数秒到数十秒） | 数百毫秒 |
| 用户体验 | 长时间空白等待 | 实时打字效果 |
| 编程复杂度 | 简单，直接拿到 Message 对象 | 需要处理事件流、累积内容 |
| 适用场景 | 脚本、批处理、后端 API | 聊天 UI、CLI 工具、实时演示 |
| 错误处理 | 响应返回时抛出异常 | 流中途可能收到 error 事件 |

## stream=True 参数

启用流式非常简单，只需要在 `client.messages.create()` 调用时传入 `stream=True` 参数：

```python
from anthropic import Anthropic

client = Anthropic()

# 启用流式响应
stream = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[{"role": "user", "content": "写一首关于 Python 的短诗"}],
    stream=True,  # 关键参数：启用流式
)
```

返回值不再是 `Message` 对象，而是一个 `Stream[MessageStreamEvent]` 实例——这是一个可迭代的流对象，你可以通过 `for` 循环逐个迭代流式事件。

## Stream 与 AsyncStream 类

SDK 提供对称的同步和异步流类：

- **`Stream[_T]`**：同步流，定义在 `anthropic._streaming` 模块，支持 `for event in stream:` 迭代
- **`AsyncStream[_T]`**：异步流，与同步版本对称，支持 `async for event in stream:` 异步迭代

两个类都支持上下文管理器协议（`with`/`async with`），推荐使用上下文管理器确保资源正确释放。

## 流式事件类型层次

流式响应是一系列按特定顺序到达的 SSE 事件。理解事件类型层次是处理流式响应的关键。标准的消息生成事件序列遵循严格的生命周期：

```
MessageStartEvent
  └─ ContentBlockStartEvent (每个内容块开始时触发一次)
       └─ ContentBlockDeltaEvent (每个增量 token 触发，可能多次)
       └─ ContentBlockStopEvent (该内容块结束时触发)
  └─ MessageDeltaEvent (可选，包含最终的 usage 和 stop_reason 增量更新)
MessageStopEvent
```

### 核心事件类型详解

| 事件类 | SSE 事件名 | 触发时机 | 包含内容 |
|--------|-----------|---------|---------|
| `MessageStartEvent` | `"message_start"` | 流开始时，第一个事件 | 消息元数据（id、model、role、初始 usage） |
| `ContentBlockStartEvent` | `"content_block_start"` | 每个内容块开始时 | 内容块索引、内容块类型（text/tool_use/thinking） |
| `ContentBlockDeltaEvent` | `"content_block_delta"` | 生成每个增量 token 时 | 内容块索引、增量数据（text_delta/input_json_delta/thinking_delta） |
| `ContentBlockStopEvent` | `"content_block_stop"` | 一个内容块生成完毕时 | 内容块索引 |
| `MessageDeltaEvent` | `"message_delta"` | 所有内容块生成后 | stop_reason、最终 usage 增量更新 |
| `MessageStopEvent` | `"message_stop"` | 流结束时，最后一个事件 | 无额外数据，标记流结束 |

> ⚠️ **error 事件**：如果流中途发生错误，会收到 `"error"` 类型的事件，此时 Stream 会自动调用 `_make_status_error` 抛出对应异常。

除了上述核心消息事件，流中还可能包含 Agent 相关事件：`"agent.message"`、`"agent.thinking"`、`"agent.tool_use"`、`"agent.tool_result"`、`"agent.mcp_tool_use"`，这些在 Beta Agents 功能中使用。

## 迭代 Stream：基本模式

最基础的流式用法是直接迭代 `Stream` 对象，根据事件类型分别处理：

```python
from anthropic import Anthropic
from anthropic.types import (
    MessageStartEvent,
    ContentBlockStartEvent,
    ContentBlockDeltaEvent,
    ContentBlockStopEvent,
    MessageDeltaEvent,
    MessageStopEvent,
)

client = Anthropic()

stream = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[{"role": "user", "content": "解释什么是递归，用简单的例子"}],
    stream=True,
)

for event in stream:
    if isinstance(event, MessageStartEvent):
        print(f"[开始] 消息 ID: {event.message.id}")
    
    elif isinstance(event, ContentBlockStartEvent):
        print(f"\n[内容块开始] 类型: {event.content_block.type}, 索引: {event.index}")
    
    elif isinstance(event, ContentBlockDeltaEvent):
        if event.delta.type == "text_delta":
            # 文本增量：直接打印
            print(event.delta.text, end="", flush=True)
    
    elif isinstance(event, ContentBlockStopEvent):
        print(f"\n[内容块结束] 索引: {event.index}")
    
    elif isinstance(event, MessageDeltaEvent):
        if event.usage:
            print(f"\n[Token 使用] 输出: {event.usage.output_tokens}")
    
    elif isinstance(event, MessageStopEvent):
        print("\n[结束] 流完成")
```

这种方式虽然灵活，但需要手动处理事件类型判断和内容累积。对于大多数简单场景，SDK 提供了更便捷的高级接口。

## 文本流拼接：使用 MessageStream

直接处理事件比较繁琐，SDK 在 `lib/streaming` 模块提供了更高级的 `MessageStream` 类，封装了常见的流式操作。使用 `client.messages.stream()` 方法（而不是 `create(stream=True)`）可以直接获得 `MessageStreamManager` 上下文管理器：

```python
from anthropic import Anthropic

client = Anthropic()

# 使用 stream() 方法获得 MessageStreamManager
with client.messages.stream(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[{"role": "user", "content": "讲一个关于程序员的笑话"}],
) as stream:
    # text_stream 是一个纯文本增量迭代器，直接产出字符串
    for text in stream.text_stream:
        print(text, end="", flush=True)
    
    # 流结束后，可以获取最终的完整 Message 对象
    final_message = stream.get_final_message()
    print(f"\n\n[完成] 共 {final_message.usage.output_tokens} 个输出 token")
    print(f"[停止原因] {final_message.stop_reason}")
```

`MessageStream` 提供了几个非常实用的方法和属性：

| 方法/属性 | 说明 |
|----------|------|
| `.text_stream` | 迭代器，直接产出文本增量字符串，无需手动处理事件类型 |
| `.get_final_message()` | 累积所有事件，返回完整的 `Message` 对象（与非流式返回值相同） |
| `.get_final_text()` | 返回最终的完整文本字符串 |
| `.until_done()` | 阻塞直到流结束，处理所有事件（不返回内容） |

### 实时 CLI 聊天示例

使用 `MessageStream` 可以非常简洁地实现一个带打字效果的 CLI 聊天工具：

```python
from anthropic import Anthropic

def streaming_chat():
    client = Anthropic()
    messages = []
    system = "你是一位友好的 AI 助手，用简洁的中文回答。"
    
    print("=== Claude 流式聊天（输入 'quit' 退出）===\n")
    
    while True:
        user_input = input("你：")
        if user_input.lower() == "quit":
            break
        
        messages.append({"role": "user", "content": user_input})
        
        print("Claude：", end="", flush=True)
        
        try:
            with client.messages.stream(
                model="claude-3-5-sonnet-latest",
                max_tokens=1024,
                system=system,
                messages=messages,
            ) as stream:
                full_response = ""
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                    full_response += text
                
                final_message = stream.get_final_message()
            
            print()  # 换行
            messages.append({"role": "assistant", "content": full_response})
            
            print(f"[token: {final_message.usage.input_tokens}+{final_message.usage.output_tokens}]\n")
        
        except Exception as e:
            print(f"\n错误：{e}\n")

if __name__ == "__main__":
    streaming_chat()
```

## 工具调用流的处理

当使用工具调用（Function Calling）时，流式响应中会出现 `tool_use` 类型的内容块，其增量类型为 `input_json_delta`——工具的输入参数 JSON 是分块传输的，需要手动累积拼接成完整的 JSON 字符串再解析。

### 手动累积 JSON 示例

```python
import json
from anthropic import Anthropic

client = Anthropic()

tools = [
    {
        "name": "get_weather",
        "description": "获取指定城市的天气",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名称"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["city"]
        }
    }
]

with client.messages.stream(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[{"role": "user", "content": "北京现在天气怎么样？"}],
    tools=tools,
) as stream:
    # 用于累积工具调用输入的字典：{index: json_string}
    tool_json_accumulator = {}
    
    for event in stream:
        if event.type == "content_block_start":
            if event.content_block.type == "tool_use":
                # 新工具调用开始，初始化累积器
                tool_json_accumulator[event.index] = ""
                print(f"\n[工具调用] {event.content_block.name}")
        
        elif event.type == "content_block_delta":
            if event.delta.type == "input_json_delta":
                # 累积 JSON 片段
                tool_json_accumulator[event.index] += event.delta.partial_json
                print(event.delta.partial_json, end="", flush=True)
        
        elif event.type == "content_block_stop":
            if event.index in tool_json_accumulator:
                # 工具调用结束，解析完整 JSON
                full_json = tool_json_accumulator[event.index]
                tool_input = json.loads(full_json) if full_json else {}
                print(f"\n[解析完成] 参数: {tool_input}")
    
    final_message = stream.get_final_message()
    print(f"\n[停止原因] {final_message.stop_reason}")
```

关键点是：`input_json_delta` 的 `partial_json` 字段是不完整的 JSON 片段，可能在任意位置断开（比如对象中间、字符串中间），必须等收到 `content_block_stop` 后才能用 `json.loads()` 解析，不能在中途尝试解析。

## AsyncStream：异步流式用法

异步流式与同步完全对称，只需要使用 `AsyncAnthropic` 客户端和 `async for`、`async with` 语法：

```python
import asyncio
from anthropic import AsyncAnthropic

async def async_streaming_example():
    client = AsyncAnthropic()
    
    async with client.messages.stream(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=[{"role": "user", "content": "用异步方式写一首诗"}],
    ) as stream:
        # 异步迭代文本流
        async for text in stream.text_stream:
            print(text, end="", flush=True)
        
        # 异步获取最终消息
        final_message = await stream.get_final_message()
        print(f"\n\n[异步完成] {final_message.usage.output_tokens} tokens")

if __name__ == "__main__":
    asyncio.run(async_streaming_example())
```

异步版本的方法名都有对应的 `await` 形式：`get_final_message()` → `await get_final_message()`，`until_done()` → `await until_done()`。

## Context Manager 的重要性

强烈建议始终使用 `with client.messages.stream(...) as stream:` 上下文管理器形式，而不是手动调用 `stream = client.messages.create(stream=True)` 然后迭代。原因：

1. **自动资源释放**：上下文管理器保证 HTTP 连接在流结束后正确关闭，即使发生异常
2. **异常安全**：流中途出错时，上下文管理器能正确清理资源
3. **更简洁的 API**：直接获得 `MessageStream` 高级接口，而不是原始 `Stream`

如果确实需要手动管理（例如在某些框架集成中），记得在结束后调用 `stream.close()`：

```python
stream = client.messages.create(..., stream=True)
try:
    for event in stream:
        handle_event(event)
finally:
    stream.close()
```

## 常见问题与注意事项

### 1. 空内容块
Claude 的响应可能包含多个内容块（比如先思考，再输出文本，再调用工具），因此 `content` 是一个列表而不是单个块。迭代时要注意按 `index` 区分不同内容块。

### 2. 文本可能在 delta 之间分割
不要假设每个 `text_delta` 包含完整的词或句子——token 可能在任意字符边界断开。增量拼接是唯一正确的方式。

### 3. usage 信息的位置
- 初始的输入 token 数在 `MessageStartEvent` 中
- 输出 token 数在 `MessageDeltaEvent` 中增量更新
- 最终完整 usage 在 `get_final_message().usage` 中

### 4. stop_reason 不在 StopEvent 中
`MessageStopEvent` 只是标记流结束，不包含 `stop_reason`。`stop_reason` 在 `MessageDeltaEvent` 中，或者通过 `get_final_message().stop_reason` 获取。

## 相关概念

- [Messages API 基础](/python-sdk/concepts/02-messages-basics.md) — 非流式消息 API 的基础用法，理解 Message 对象结构
- [工具调用（Function Calling）](/python-sdk/concepts/04-tool-use.md) — 学习如何定义工具和处理工具调用循环
- [流式对话示例](/python-sdk/examples/02-streaming-chat.md) — 完整可运行的流式 CLI 聊天机器人代码
- [Anthropic Python SDK 消息 API 与流式处理参考](/python-sdk/references/messages-api.md) — 流式类、事件类型、MessageStream API 的完整参考手册
