---
type: example
title: "基础对话"
description: "最简单的非流式文本对话示例，包含单轮对话、多轮对话、系统提示词用法和错误处理。"
tags: [chat, basic, messages, system-prompt, multi-turn, non-streaming]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-001~F-009
    resource: /python-sdk/references/sdk-client.md
    title: "Anthropic Python SDK 客户端入口与基础设施参考"
  - id: F-016~F-023
    resource: /python-sdk/references/messages-api.md
    title: "Anthropic Python SDK 消息 API 与流式处理参考"
  - id: concept-01
    resource: /python-sdk/concepts/01-client-init.md
    title: "客户端初始化与配置"
  - id: concept-02
    resource: /python-sdk/concepts/02-messages-basics.md
    title: "Messages API 基础"
---

# 基础对话

本示例演示使用 Anthropic Python SDK 进行最基础的非流式文本对话，包括：环境准备、单轮对话、多轮对话、系统提示词配置，以及完整的错误处理。这是你学习使用 Claude API 的起点。

## 前置准备

1. 在 [Anthropic Console](https://console.anthropic.com/) 注册账号并获取 API Key
2. 安装 SDK：`pip install anthropic`
3. 设置环境变量 `ANTHROPIC_API_KEY`

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-api03-..."

# Windows CMD
set ANTHROPIC_API_KEY=sk-ant-api03-...

# Linux/macOS
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

## 完整代码

```python
import os
from anthropic import Anthropic, APIStatusError, APIConnectionError


def single_turn_chat(client: Anthropic, question: str) -> str:
    """
    单轮对话示例：发送一个问题，获取 Claude 的完整回复。

    Args:
        client: Anthropic 客户端实例
        question: 用户问题

    Returns:
        Claude 的回复文本
    """
    # 调用 messages.create 发起对话，三个必填参数：model、max_tokens、messages
    message = client.messages.create(
        model="claude-3-5-sonnet-latest",  # 使用 Claude 3.5 Sonnet 模型
        max_tokens=1024,                    # 最多生成 1024 个 token
        messages=[
            {"role": "user", "content": question}
        ]
    )

    # 提取回复文本：message.content 是内容块列表，简单对话只有一个文本块
    reply_text = message.content[0].text

    # 打印 token 使用统计
    print(f"[单轮对话] 输入 token：{message.usage.input_tokens}，输出 token：{message.usage.output_tokens}")

    return reply_text


def multi_turn_chat(client: Anthropic, system_prompt: str) -> None:
    """
    多轮对话示例：在同一会话中连续提问，保持上下文记忆。

    Args:
        client: Anthropic 客户端实例
        system_prompt: 系统提示词
    """
    # messages 列表累积对话历史
    messages = []

    # 第一轮提问
    messages.append({"role": "user", "content": "你好，我叫小明，我是一名 Python 初学者。"})

    message1 = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    reply1 = message1.content[0].text
    print(f"\n【第1轮】\n你：你好，我叫小明，我是一名 Python 初学者。\nClaude：{reply1}")

    # 将助手回复加入历史，这是多轮对话保持上下文的关键
    messages.append({"role": "assistant", "content": reply1})

    # 第二轮提问：Claude 应该记得"小明"这个名字
    messages.append({"role": "user", "content": "你还记得我的名字吗？我刚才说我是做什么的？"})

    message2 = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    reply2 = message2.content[0].text
    print(f"\n【第2轮】\n你：你还记得我的名字吗？我刚才说我是做什么的？\nClaude：{reply2}")

    messages.append({"role": "assistant", "content": reply2})

    # 第三轮提问：基于上下文推荐学习资源
    messages.append({"role": "user", "content": "推荐一本适合我的入门书吧。"})

    message3 = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    reply3 = message3.content[0].text
    print(f"\n【第3轮】\n你：推荐一本适合我的入门书吧。\nClaude：{reply3}")


def interactive_chat(client: Anthropic) -> None:
    """
    交互式聊天：命令行下与 Claude 持续对话，类似 ChatGPT 界面。
    """
    system_prompt = "你是一位友好、耐心的 AI 助手，用中文回答问题，回答要简洁明了。"
    messages = []

    print("=" * 60)
    print("Claude 交互式聊天（输入 'quit' 或 'exit' 退出）")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("再见！")
            break

        # 添加用户消息到历史
        messages.append({"role": "user", "content": user_input})

        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=2048,
                system=system_prompt,
                messages=messages,
            )

            reply = message.content[0].text
            print(f"\nClaude：{reply}")

            # 添加助手回复到历史
            messages.append({"role": "assistant", "content": reply})

            # 显示 token 用量和停止原因
            print(f"\n[token：输入 {message.usage.input_tokens} / 输出 {message.usage.output_tokens} | "
                  f"停止原因：{message.stop_reason}]")

        except APIStatusError as e:
            # API 状态错误：4xx/5xx 响应
            if e.status_code == 401:
                print("\n❌ 认证失败：请检查 ANTHROPIC_API_KEY 环境变量是否正确设置")
            elif e.status_code == 403:
                print("\n❌ 权限不足：你的账号可能没有访问该模型的权限")
            elif e.status_code == 429:
                print("\n❌ 请求过于频繁：请稍后再试（触发速率限制）")
            elif e.status_code == 500:
                print("\n❌ 服务器错误：Anthropic 服务端出现问题，请稍后重试")
            else:
                print(f"\n❌ API 错误（状态码 {e.status_code}）：{e.message}")
            print(f"请求 ID：{e.request_id}")
            break

        except APIConnectionError:
            print("\n❌ 网络连接失败：请检查网络连接或代理设置")
            break

        except Exception as e:
            print(f"\n❌ 未知错误：{type(e).__name__}: {e}")
            break


if __name__ == "__main__":
    # 检查环境变量
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("错误：请先设置 ANTHROPIC_API_KEY 环境变量")
        print("Windows PowerShell: $env:ANTHROPIC_API_KEY=\"sk-ant-api03-...\"")
        print("Linux/macOS: export ANTHROPIC_API_KEY=\"sk-ant-api03-...\"")
        exit(1)

    # 初始化客户端：自动从环境变量读取 ANTHROPIC_API_KEY
    client = Anthropic()

    # 1. 演示单轮对话
    print("=" * 60)
    print("1. 单轮对话演示")
    print("=" * 60)
    reply = single_turn_chat(client, "用一句话解释什么是 Python 装饰器")
    print(f"问题：用一句话解释什么是 Python 装饰器")
    print(f"回答：{reply}")

    # 2. 演示多轮对话
    print("\n" + "=" * 60)
    print("2. 多轮对话演示")
    print("=" * 60)
    system_prompt = "你是一位友好的 Python 编程导师，回答简洁，适合初学者。"
    multi_turn_chat(client, system_prompt)

    # 3. 启动交互式聊天（注释掉可以直接运行前两个演示）
    # print("\n" + "=" * 60)
    # print("3. 启动交互式聊天")
    # print("=" * 60)
    # interactive_chat(client)
```

## 运行方式

```bash
# 确保已设置环境变量
python 01-basic-chat.py
```

## 代码解析

### 客户端初始化

```python
client = Anthropic()
```

这是最简初始化方式，SDK 会自动从 `ANTHROPIC_API_KEY` 环境变量读取 API Key。一个应用通常只需要创建一个客户端实例，在整个生命周期中复用。

### messages.create 三个必填参数

| 参数 | 说明 | 示例值 |
|------|------|--------|
| `model` | 使用的模型 ID | `"claude-3-5-sonnet-latest"` |
| `max_tokens` | 最大生成 token 数 | `1024` |
| `messages` | 对话消息列表 | `[{"role": "user", "content": "..."}]` |

`-latest` 后缀会自动指向该系列的最新版本，生产环境建议使用固定日期版本号（如 `"claude-3-5-sonnet-20241022"`）以保证稳定性。

### 消息格式规则

`messages` 列表必须遵循以下规则：
1. **以 user 开头**：第一条消息必须是用户消息，Claude 不能先说话
2. **角色交替**：`user → assistant → user → assistant...`，不能连续两条同一角色
3. **以 user 结尾**：最后一条消息必须是用户提问

### 系统提示词（system 参数）

`system` 参数用于设置 Claude 的行为人设、回答风格、约束条件，在整个对话中持续生效。系统提示词与普通消息的区别：
- **system**：定义"你是谁，你应该怎么做"，是背景规则
- **user**：具体的问题或指令

### 多轮对话的关键：累积历史

多轮对话的核心是维护 `messages` 列表，每次收到回复后都要将 `assistant` 消息追加到列表中，这样 Claude 才能"记住"之前的对话内容。

```python
messages.append({"role": "user", "content": user_input})
# ... 调用 API ...
messages.append({"role": "assistant", "content": reply})  # 关键！
```

### 错误处理

SDK 提供了分层的异常类：
- `APIStatusError`：HTTP 4xx/5xx 错误，包含 `status_code`、`request_id` 等信息
- `APIConnectionError`：网络连接失败、超时等
- `AnthropicError`：所有 SDK 异常的基类

生产环境务必添加错误处理，特别是 401（认证失败）、429（限流）、5xx（服务端错误）这几种常见情况。`request_id` 在排查问题时非常重要，出现问题时可以提供给 Anthropic 技术支持。

### stop_reason 字段

`message.stop_reason` 告诉你生成为什么结束：
- `"end_turn"`：正常结束，回答完整
- `"max_tokens"`：达到 token 限制被截断，可继续追问"请继续"
- `"stop_sequence"`：匹配到停止序列
- `"tool_use"`：需要调用工具（见工具调用示例）

## 常见问题

1. **为什么要传 max_tokens？** 这是 API 要求的必选参数，没有默认值。它限制单次响应的最大长度，避免意外消耗过多 token。

2. **content 为什么是列表而不是字符串？** 因为 Claude 的响应可能包含多种内容块：文本、工具调用、思考过程等。简单场景下只有一个文本块，使用 `message.content[0].text` 即可。

3. **如何处理长回复被截断？** 检查 `stop_reason == "max_tokens"`，将已生成的内容加入历史，再发送"请继续"追问。

## 相关概念

- [客户端初始化与配置](/python-sdk/concepts/01-client-init.md) — 深入了解客户端配置选项、超时、重试、中间件
- [Messages API 基础](/python-sdk/concepts/02-messages-basics.md) — 详细理解消息格式、响应结构、stop_reason
- [流式对话](02-streaming-chat.md) — 下一个示例：实时打字效果的流式输出
- [Anthropic Python SDK 客户端入口与基础设施参考](/python-sdk/references/sdk-client.md) — 构造函数完整参数参考
- [Anthropic Python SDK 消息 API 与流式处理参考](/python-sdk/references/messages-api.md) — messages.create 所有参数的 API 参考
