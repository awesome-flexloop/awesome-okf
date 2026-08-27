---
type: example
title: "流式对话"
description: "实现实时打字效果的流式响应，包括基本流式迭代、text_stream简化接口、最终消息获取和异步版本。"
tags: [streaming, sse, real-time, text-stream, async, context-manager]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-026~F-037
    resource: /python-sdk/references/messages-api.md
    title: "Anthropic Python SDK 消息 API 与流式处理参考"
  - id: concept-02
    resource: /python-sdk/concepts/02-messages-basics.md
    title: "Messages API 基础"
  - id: concept-03
    resource: /python-sdk/concepts/03-streaming.md
    title: "流式响应处理"
---

# 流式对话

本示例演示如何使用 Anthropic Python SDK 的流式响应功能，实现实时打字效果。流式模式通过 SSE（Server-Sent Events）逐个返回 token，用户无需等待完整响应生成即可看到内容，显著提升交互体验。我们将展示：基本流式事件迭代、`text_stream` 简化接口、获取最终完整消息，以及异步版本的实现。

## 前置准备

与基础对话相同，确保已安装 SDK 并设置 `ANTHROPIC_API_KEY` 环境变量：

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

## 完整代码

```python
import os
import asyncio
from anthropic import Anthropic, AsyncAnthropic


def streaming_basic(client: Anthropic, question: str) -> None:
    """
    基本流式示例：手动迭代 SSE 事件，逐块打印文本。
    这是最灵活的方式，可以处理所有类型的内容块事件。

    Args:
        client: Anthropic 客户端实例
        question: 用户问题
    """
    print("--- 基本流式（手动事件迭代）---")
    print(f"你：{question}")
    print("Claude：", end="", flush=True)

    # 使用 stream=True 启用流式响应，返回 Stream[MessageStreamEvent]
    # 必须使用上下文管理器（with 语句）确保连接正确关闭
    with client.messages.stream(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=[{"role": "user", "content": question}],
    ) as stream:
        # 遍历所有流式事件
        for event in stream:
            # event.type 指示事件类型
            if event.type == "content_block_delta":
                # 内容块增量事件：包含新生成的一小段文本
                if event.delta.type == "text_delta":
                    # 打印文本增量，flush=True 确保立即输出（不缓冲）
                    print(event.delta.text, end="", flush=True)

    print()  # 流结束后换行


def streaming_text_stream(client: Anthropic, question: str) -> str:
    """
    使用 text_stream 简化接口：直接迭代纯文本，无需手动判断事件类型。
    这是最常用的流式方式，适合只需要文本输出的场景。

    Args:
        client: Anthropic 客户端实例
        question: 用户问题

    Returns:
        完整的回复文本
    """
    print("\n--- 简化流式（text_stream）---")
    print(f"你：{question}")
    print("Claude：", end="", flush=True)

    full_text = ""

    with client.messages.stream(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=[{"role": "user", "content": question}],
    ) as stream:
        # text_stream 是一个迭代器，直接产出文本增量
        for text in stream.text_stream:
            full_text += text
            print(text, end="", flush=True)

        # 流结束后，可以获取完整的 Message 对象
        final_message = stream.get_final_message()
        print(f"\n\n[流结束] 消息 ID：{final_message.id}")
        print(f"[token 使用] 输入：{final_message.usage.input_tokens}，输出：{final_message.usage.output_tokens}")
        print(f"[停止原因] {final_message.stop_reason}")

    return full_text


def streaming_get_final_message(client: Anthropic, question: str) -> None:
    """
    演示 until_done() 和 get_final_message()：
    先让流在后台处理完所有事件，然后获取最终的完整 Message 对象。
    适合需要同时获取流式体验和最终结构化数据的场景。

    Args:
        client: Anthropic 客户端实例
        question: 用户问题
    """
    print("\n--- 获取最终消息（until_done + get_final_message）---")
    print(f"你：{question}")

    collected_text = []

    with client.messages.stream(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=[{"role": "user", "content": question}],
    ) as stream:
        # 实时打印
        print("Claude（流式）：", end="", flush=True)
        for text in stream.text_stream:
            collected_text.append(text)
            print(text, end="", flush=True)

        # until_done() 阻塞直到流完全结束
        stream.until_done()

        # 现在可以安全获取最终完整消息
        final_msg = stream.get_final_message()

        # 也可以用 get_final_text() 直接获取拼接好的文本
        final_text = stream.get_final_text()

    print(f"\n\n[验证] 实时收集长度：{len(''.join(collected_text))}")
    print(f"[验证] get_final_text() 长度：{len(final_text)}")
    print(f"[验证] 两者一致：{''.join(collected_text) == final_text}")


async def async_streaming_example(question: str) -> None:
    """
    异步流式示例：使用 AsyncAnthropic 客户端，async with 和 async for 语法。
    在异步 Web 框架（FastAPI、aiohttp 等）中使用流式响应必须用异步版本。

    Args:
        question: 用户问题
    """
    print("\n--- 异步流式（AsyncAnthropic）---")
    print(f"你：{question}")
    print("Claude：", end="", flush=True)

    # 初始化异步客户端
    async with AsyncAnthropic() as client:
        # async with 管理异步流上下文
        async with client.messages.stream(
            model="claude-3-5-sonnet-latest",
            max_tokens=1024,
            messages=[{"role": "user", "content": question}],
        ) as stream:
            # async for 迭代异步文本流
            async for text in stream.text_stream:
                print(text, end="", flush=True)

            # 异步获取最终消息
            final_message = await stream.get_final_message()
            print(f"\n\n[异步完成] 输入 token：{final_message.usage.input_tokens}")

    print()


def streaming_multi_turn(client: Anthropic) -> None:
    """
    多轮对话 + 流式：在交互式聊天中结合流式输出和上下文保持。

    Args:
        client: Anthropic 客户端实例
    """
    print("\n--- 多轮交互式流式聊天 ---")
    print("输入 'quit' 退出，输入 'clear' 清空对话历史")

    system_prompt = "你是一位友好的 AI 助手，回答简洁明了。"
    messages = []

    while True:
        try:
            user_input = input("\n你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("再见！")
            break
        if user_input.lower() == "clear":
            messages = []
            print("[对话历史已清空]")
            continue

        messages.append({"role": "user", "content": user_input})
        print("Claude：", end="", flush=True)

        assistant_reply = ""
        with client.messages.stream(
            model="claude-3-5-sonnet-latest",
            max_tokens=2048,
            system=system_prompt,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                assistant_reply += text
                print(text, end="", flush=True)

            final_msg = stream.get_final_message()

        print()  # 换行
        messages.append({"role": "assistant", "content": assistant_reply})
        print(f"[token：{final_msg.usage.input_tokens} in / {final_msg.usage.output_tokens} out]")


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("错误：请先设置 ANTHROPIC_API_KEY 环境变量")
        exit(1)

    client = Anthropic()

    # 1. 基本流式（手动处理事件）
    streaming_basic(client, "用三句话解释什么是机器学习")

    # 2. 简化流式（text_stream 接口）+ 获取最终消息
    streaming_text_stream(client, "Python 有哪些主要的数据类型？")

    # 3. until_done + get_final_message 演示
    streaming_get_final_message(client, "什么是递归？举一个简单的例子")

    # 4. 异步流式（需要 asyncio 运行）
    asyncio.run(async_streaming_example("简单介绍一下异步编程的优势"))

    # 5. 多轮交互式流式聊天（取消注释可以体验）
    # streaming_multi_turn(client)
```

## 运行方式

```bash
python 02-streaming-chat.py
```

## 代码解析

### 流式 vs 非流式：核心区别

| 模式 | 触发方式 | 返回类型 | 用户体验 | 适用场景 |
|------|---------|---------|---------|---------|
| 非流式 | 默认 | `Message` 对象 | 等待完整响应后一次性显示 | 脚本、批处理、API 后端 |
| 流式 | `stream=True` | `Stream[MessageStreamEvent]` | 实时逐字显示（打字效果） | 聊天界面、长文本生成、CLI 工具 |

### 上下文管理器是必须的

```python
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

**必须使用 `with` 语句**（或手动调用 `stream.close()`），否则 HTTP 连接可能不会正确释放，导致资源泄漏。`Stream` 类实现了上下文管理器协议（`__enter__`/`__exit__`），退出 `with` 块时自动关闭连接。

### 两种流式使用方式

#### 方式1：手动迭代事件（灵活但复杂）

```python
for event in stream:
    if event.type == "content_block_delta":
        if event.delta.type == "text_delta":
            print(event.delta.text, end="", flush=True)
```

这种方式可以处理所有 SSE 事件类型：
- `message_start`：消息开始
- `content_block_start`：新内容块开始
- `content_block_delta`：内容增量（文本增量在此）
- `content_block_stop`：内容块结束
- `message_delta`：消息元数据增量（如 token 统计）
- `message_stop`：消息结束

适合需要处理工具调用、思考块等复杂内容块的场景。

#### 方式2：text_stream 简化接口（推荐）

```python
for text in stream.text_stream:
    print(text, end="", flush=True)
```

`text_stream` 是 SDK 提供的便捷迭代器，**直接产出纯文本增量**，无需手动判断事件类型。这是 90% 场景下的推荐用法。

### flush=True 的重要性

```python
print(text, end="", flush=True)
```

- `end=""`：不换行，让文本连续输出
- `flush=True`：**强制立即刷新输出缓冲区**。如果不加，Python 可能会缓冲输出直到攒够一定字符才显示，用户就看不到逐字打字效果了。

### 获取最终完整消息

流结束后，可以调用以下方法获取结构化数据：

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `stream.get_final_message()` | `Message` | 完整的 Message 对象，与非流式返回的一样 |
| `stream.get_final_text()` | `str` | 拼接好的完整文本 |
| `stream.until_done()` | `None` | 阻塞直到流完全处理完 |

```python
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    # 必须在 with 块内调用（流还未关闭）
    final_message = stream.get_final_message()
```

**注意**：这些方法必须在 `with` 块内部调用，此时流仍然活跃。退出 `with` 块后流已关闭，无法再获取。

### 异步流式（AsyncAnthropic）

在异步 Web 框架（FastAPI、aiohttp、Sanic 等）中，必须使用异步客户端：

```python
async with AsyncAnthropic() as client:
    async with client.messages.stream(...) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)
        final_message = await stream.get_final_message()
```

关键点：
- 使用 `AsyncAnthropic` 而非 `Anthropic`
- `async with` 替代 `with`
- `async for` 替代 `for`
- `await stream.get_final_message()` 需要 await

异步版本的 API 与同步版本完全对称，方法名相同，只是需要加 `await` 和 `async` 前缀。

### 流式事件生命周期

一个完整的流式响应事件序列：

```
message_start
  └─ content_block_start (index=0, type="text")
       └─ content_block_delta (text_delta, 重复多次)
       └─ content_block_stop
  └─ message_delta (usage 统计更新)
message_stop
```

多个内容块时（如工具调用+文本），会有多个 `content_block_start → ... → content_block_stop` 循环。

### 多轮流式聊天的关键点

与非流式多轮对话一样，需要维护 `messages` 列表累积历史。流式只是**响应的传输方式**变了，对话历史管理的逻辑完全相同：

```python
messages.append({"role": "user", "content": user_input})
# ... 流式获取回复 ...
messages.append({"role": "assistant", "content": assistant_reply})  # 仍然需要累积
```

## 常见问题

1. **为什么我的流式输出不是逐字显示，而是一下子出来？** 检查是否加了 `flush=True`。Python 的 print 默认会缓冲输出。

2. **可以在流结束后继续追加对话吗？** 可以。用 `get_final_message()` 获取完整响应后，按普通多轮对话方式处理即可。

3. **流式模式下如何处理错误？** 与非流式相同，捕获 `APIStatusError`、`APIConnectionError` 等异常。网络中断时迭代器会抛出异常。

4. **text_stream 和手动迭代事件性能有差异吗？** 几乎没有。`text_stream` 是在事件迭代基础上的轻量封装，过滤出文本增量而已。

## 相关概念

- [Messages API 基础](/python-sdk/concepts/02-messages-basics.md) — 理解非流式模式作为对比基础
- [基础对话](01-basic-chat.md) — 前一个示例：非流式对话入门
- [工具调用实战](03-tool-use.md) — 下一个示例：流式与工具调用结合
- [Anthropic Python SDK 消息 API 与流式处理参考](/python-sdk/references/messages-api.md) — 流式类和事件类型的完整 API 参考
