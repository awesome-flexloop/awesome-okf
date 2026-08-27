---
type: concept
title: "Messages API 基础"
description: "掌握 Claude 核心对话接口 Messages API 的必选参数、消息格式、系统提示词、响应结构、stop_reason 含义，完成你的第一个完整对话。"
tags: [messages, chat, conversation, system-prompt, response, stop-reason]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-016~F-023,F-085~F-090
    resource: /python-sdk/references/messages-api.md
    title: "Anthropic Python SDK 消息 API 与流式处理参考"
  - id: F-005~F-015
    resource: /python-sdk/references/sdk-client.md
    title: "Anthropic Python SDK 客户端入口与基础设施参考"
  - id: F-085~F-090
    resource: /python-sdk/references/types-errors.md
    title: "Anthropic Python SDK 类型系统与异常体系参考"
---

# Messages API 基础

Messages API 是与 Claude 交互的核心接口，也是你使用 SDK 时最常调用的 API。无论是简单的问答、多轮对话、内容生成还是工具调用，都通过 `client.messages.create()` 方法发起。本文档将讲解 Messages API 的核心概念、必选参数、消息格式、系统提示词、响应解析，以及如何判断对话结束的原因。

## Messages API 与 Completions API 的区别

如果你之前使用过早期的 Anthropic API 或其他大模型 API，可能对 Completions API 比较熟悉。Anthropic 现在推荐使用 Messages API，两者有以下关键区别：

| 维度 | Completions API（旧） | Messages API（推荐） |
|------|---------------------|---------------------|
| 接口风格 | 纯文本补全 | 结构化消息列表（role + content） |
| 对话支持 | 需要手动拼接提示词 | 原生支持多轮对话 |
| 系统提示词 | 混入用户消息 | 独立的 `system` 参数 |
| 工具调用 | 需要自行实现 | 原生支持 `tools`/`tool_choice` |
| 内容块 | 仅文本 | 支持文本、图片、工具调用、思考等多种内容块 |
| 端点 | `/v1/complete` | `/v1/messages` |

Messages API 的设计更贴近现代大模型的对话范式，也是所有新功能（工具调用、视觉、Extended Thinking 等）的唯一支持接口。所有新代码都应使用 Messages API。

## messages.create 必选参数

`client.messages.create()` 有三个必选参数，缺一不可：

| 参数 | 类型 | 说明 |
|------|------|------|
| `model` | `str` | 模型标识符，指定使用哪个 Claude 模型 |
| `max_tokens` | `int` | 生成响应的最大 token 数 |
| `messages` | `Iterable[MessageParam]` | 对话消息列表，包含历史对话 |

### model：选择模型

`model` 参数指定要调用的 Claude 模型。常用模型标识符：

| 模型 ID | 说明 |
|---------|------|
| `"claude-3-5-sonnet-latest"` | Claude 3.5 Sonnet（推荐，平衡性能与速度） |
| `"claude-3-5-haiku-latest"` | Claude 3.5 Haiku（最快，适合简单任务） |
| `"claude-opus-4-latest"` | Claude Opus 4（最强推理能力） |
| `"claude-3-5-sonnet-20241022"` | 固定版本，避免自动更新 |

使用 `-latest` 后缀会自动指向该模型系列的最新版本，适合大多数场景；如果需要生产环境稳定性，可以使用固定日期版本号。

### max_tokens：控制输出长度

`max_tokens` 设置 Claude 单次响应最多生成的 token 数量。这是一个**必选**参数，没有默认值：

- 短对话/问答：`1024` 或 `2048`
- 长文本生成：`4096` 或更高
- 需要注意：部分模型非流式模式有 8192 token 的上限

token 数量与中文字数的粗略换算：1 个中文字符约 1-2 个 token，1 个英文单词约 1-1.5 个 token。

### messages：对话消息列表

`messages` 参数是一个消息数组，按时间顺序排列，代表对话历史。每条消息是一个字典，包含两个必填字段：

- `role`：消息角色，只能是 `"user"`（用户）或 `"assistant"`（Claude）
- `content`：消息内容，可以是字符串（简单文本）或内容块数组（复杂内容）

## 消息格式详解

### 单轮对话：最简单的形式

单轮对话只需要一条 user 消息：

```python
from anthropic import Anthropic

client = Anthropic()

message = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "什么是 Python 列表推导式？"}
    ]
)

print(message.content[0].text)
```

### 多轮对话：带上历史

多轮对话需要按顺序交替排列 user 和 assistant 消息：

```python
message = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "我想学习 Python，从哪里开始？"},
        {"role": "assistant", "content": "学习 Python 可以从以下几个方面开始：1. 安装 Python 环境；2. 学习基础语法..."},
        {"role": "user", "content": "能推荐一本适合初学者的书吗？"}
    ]
)
```

**重要规则**：
1. 消息必须以 `user` 角色开头（Claude 不能先说话）
2. 角色必须交替出现：`user → assistant → user → assistant...`
3. 不能连续两条消息都是同一角色
4. 最后一条消息必须是 `user`（你向 Claude 提问）

如果对话历史不符合上述规则，API 会返回错误。

## system：系统提示词

`system` 参数是可选的，但非常重要——它用于设置 Claude 的行为人设、回答风格、约束条件等，在整个对话过程中持续生效。

系统提示词与 user 消息的区别：
- **system**：定义"你是谁，你应该怎么做"，是对话的背景规则
- **user**：具体的问题或指令

```python
message = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    system="你是一位资深 Python 编程导师，回答要简洁、专业，代码示例要符合 PEP 8 规范，适合初学者理解。",
    messages=[
        {"role": "user", "content": "解释一下什么是装饰器"}
    ]
)
```

系统提示词可以是字符串，也可以是内容块数组（支持缓存等高级功能）。好的系统提示词能显著提升 Claude 回答的质量和一致性。

## 响应结构：解析 Message 对象

`messages.create()` 在非流式模式（默认）下返回一个 `Message` 对象，包含完整的响应信息。

### Message 对象核心字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `str` | 消息唯一标识符，格式如 `"msg_0123456789abcdef"` |
| `type` | `str` | 固定为 `"message"` |
| `role` | `str` | 固定为 `"assistant"`（响应都是 Claude 发出的） |
| `content` | `list[ContentBlock]` | 内容块列表，包含 Claude 的回复 |
| `model` | `str` | 实际使用的模型 ID |
| `stop_reason` | `str \| None` | 停止原因，表明生成为什么结束 |
| `stop_sequence` | `str \| None` | 如果触发了停止序列，这里是匹配到的序列 |
| `usage` | `Usage` | Token 使用统计 |

### 提取回复文本

在大多数简单对话场景下，`content` 列表中只有一个文本块，通过 `message.content[0].text` 获取：

```python
message = client.messages.create(...)

# 获取回复文本
reply_text = message.content[0].text
print(f"Claude 回复：{reply_text}")

# 获取 token 使用情况
print(f"输入 token：{message.usage.input_tokens}")
print(f"输出 token：{message.usage.output_tokens}")
print(f"请求 ID：{message.id}")
print(f"停止原因：{message.stop_reason}")
```

`content` 是一个列表而不是单个字符串，是因为 Claude 的响应可能包含多种类型的内容块：
- `TextBlock`：文本内容（最常见）
- `ToolUseBlock`：工具调用请求（使用 tools 时出现）
- `ThinkingBlock`：Extended Thinking 思考过程
- 其他特殊内容块

在入门阶段，我们只需要关注文本块。

## 第一个完整对话示例

让我们来看一个包含多轮对话、系统提示词、错误处理的完整示例：

```python
from anthropic import Anthropic, APIStatusError, APIConnectionError

def chat_with_claude():
    client = Anthropic()
    
    # 对话历史（可以保存在变量中，实现多轮对话）
    messages = []
    system_prompt = "你是一位友好、耐心的编程助手，用中文回答问题。"
    
    print("=== Claude 对话助手（输入 'quit' 退出）===")
    
    while True:
        user_input = input("\n你：")
        if user_input.lower() == "quit":
            break
        
        # 添加用户消息到历史
        messages.append({"role": "user", "content": user_input})
        
        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=1024,
                system=system_prompt,
                messages=messages,
            )
            
            # 提取回复
            reply = message.content[0].text
            print(f"\nClaude：{reply}")
            
            # 添加助手回复到历史，继续多轮对话
            messages.append({"role": "assistant", "content": reply})
            
            # 打印 token 消耗
            print(f"\n[token 使用] 输入：{message.usage.input_tokens}，输出：{message.usage.output_tokens}")
            
        except APIStatusError as e:
            if e.status_code == 401:
                print("错误：API Key 无效，请检查 ANTHROPIC_API_KEY 环境变量")
            elif e.status_code == 429:
                print("错误：请求过于频繁，请稍后再试")
            else:
                print(f"API 错误（{e.status_code}）：{e.message}")
            break
        except APIConnectionError:
            print("错误：网络连接失败，请检查网络")
            break
        except Exception as e:
            print(f"未知错误：{e}")
            break

if __name__ == "__main__":
    chat_with_claude()
```

## stop_reason：理解对话为什么结束

`stop_reason` 字段告诉你 Claude 为什么停止生成，这在应用逻辑中非常重要。可能的值：

| stop_reason | 含义 | 应用场景处理 |
|------------|------|-------------|
| `"end_turn"` | Claude 认为回答完整，主动结束 | 正常情况，对话轮次结束 |
| `"max_tokens"` | 达到了 `max_tokens` 限制 | 回复可能被截断，可以继续追问"请继续" |
| `"stop_sequence"` | 匹配到了你设置的自定义停止序列 | 根据你定义的停止逻辑处理 |
| `"tool_use"` | Claude 想要调用工具 | 需要执行工具并将结果返回，详见工具调用文档 |

### 处理 max_tokens 截断

当 `stop_reason` 为 `"max_tokens"` 时，说明回复还没说完就被截断了：

```python
message = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=100,  # 故意设置很小，演示截断
    messages=[{"role": "user", "content": "写一篇 500 字的关于人工智能的短文"}]
)

if message.stop_reason == "max_tokens":
    print("⚠️ 回复被截断，正在继续...")
    # 将已生成的内容加入历史，继续追问
    messages = [
        {"role": "user", "content": "写一篇 500 字的关于人工智能的短文"},
        {"role": "assistant", "content": message.content[0].text},
        {"role": "user", "content": "请继续"}
    ]
    continuation = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=messages,
    )
    full_reply = message.content[0].text + continuation.content[0].text
else:
    full_reply = message.content[0].text
```

## 非流式 vs 流式：如何选择

`messages.create` 支持两种响应模式：

- **非流式（默认）**：等待 Claude 生成完整回复后一次性返回，适合脚本、简单问答、不需要实时输出的场景
- **流式（`stream=True`）**：通过 SSE 逐个返回 token，适合聊天界面、实时展示生成过程、长文本生成场景

### 什么时候用哪种？

| 场景 | 推荐模式 |
|------|---------|
| 脚本/批处理 | 非流式 |
| API 后端（前端自行处理流式） | 非流式 |
| 命令行聊天工具 | 流式 |
| Web 聊天界面（实时打字效果） | 流式 |
| 长文本生成（减少感知等待时间） | 流式 |

流式模式的具体用法将在 [03-streaming.md](/python-sdk/concepts/03-streaming.md) 中详细讲解。入门阶段使用非流式即可，简单直接。

## 可选参数预览

除了必选参数和 `system`，`messages.create` 还支持很多可选参数，这里列出常用的几个，后续文档会详细讲解：

| 参数 | 用途 | 对应概念文档 |
|------|------|-------------|
| `stream` | 启用流式响应 | [03-streaming.md](/python-sdk/concepts/03-streaming.md) |
| `tools`/`tool_choice` | 定义工具和工具选择策略 | [04-tool-use.md](/python-sdk/concepts/04-tool-use.md) |
| `thinking` | Extended Thinking 思考模式 | 示例文档 |
| `stop_sequences` | 自定义停止序列 | API 参考 |
| `metadata` | 请求元数据（如 user_id） | API 参考 |
| `temperature`/`top_p` | 采样参数（控制随机性） | API 参考 |

入门阶段你只需要掌握 `model`、`max_tokens`、`messages`、`system` 这四个参数，就可以完成 80% 的对话场景。

## 常见错误与排查

1. **`max_tokens` is required**：忘记传 `max_tokens` 参数，这是必选的
2. **messages must start with a user message**：消息列表第一条不是 user
3. **messages must alternate roles**：连续两条消息是同一角色
4. **invalid api key**：API Key 错误或未设置，检查 `ANTHROPIC_API_KEY` 环境变量
5. **model not found**：模型 ID 拼写错误，或你没有该模型的访问权限

## 相关概念

- [客户端初始化与配置](/python-sdk/concepts/01-client-init.md) — 学习如何正确初始化客户端
- [流式处理](/python-sdk/concepts/03-streaming.md) — 实时流式输出的两种使用方式
- [工具调用（Function Calling）](/python-sdk/concepts/04-tool-use.md) — 让 Claude 调用函数获取外部数据
- [Anthropic Python SDK 消息 API 与流式处理参考](/python-sdk/references/messages-api.md) — `messages.create` 所有参数的完整 API 参考
- [Anthropic Python SDK 类型系统与异常体系参考](/python-sdk/references/types-errors.md) — 错误处理的完整异常类列表
