---
type: Concept
title: 对话补全 API
description: 对话补全接口（/v1/chat/completions）完整说明，包含消息格式、流式输出、工具调用、图像理解等核心功能
tags: [对话补全, Chat Completions, 流式输出, 工具调用, 多模态]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T21:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T21:40:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: official-readme
    resource: /references/readme.md
    title: Agnes AI 官方README
  - id: model-catalog
    resource: /references/model-catalog.md
    title: Agnes AI 模型目录
---

# 对话补全 API

对话补全接口是AgnesAI最核心的API，提供文本生成、多轮对话、流式输出、工具调用、图像理解等能力，完全兼容OpenAI Chat Completions API规范。

**端点**：`POST https://apihub.agnes-ai.com/v1/chat/completions`

**支持模型**：
- `agnes-2.5-flash`（推荐）：512K上下文，65.5K最大输出，支持工具调用、推理、图像理解
- `agnes-2.0-flash`：256K上下文，64K最大输出，稳定版本
- `agnes-1.5-flash`：256K上下文，低延迟、高吞吐

> 事实溯源：F-008、F-009、F-016~F-018

## 基础请求格式

### 请求体核心字段

```json
{
  "model": "agnes-2.5-flash",
  "messages": [
    {"role": "system", "content": "你是一个有用的助手。"},
    {"role": "user", "content": "你好，请介绍一下自己。"}
  ],
  "stream": false,
  "temperature": 0.7,
  "max_tokens": 1024
}
```

### messages消息格式

| 角色（role） | 作用 | content类型 |
|------------|------|------------|
| `system` | 系统提示词，设定AI行为和身份 | 字符串 |
| `user` | 用户输入的消息 | 字符串或多模态内容数组 |
| `assistant` | AI的回复消息（多轮对话上下文） | 字符串 |
| `tool` | 工具调用返回结果（Function Calling场景） | 字符串 |

## 基础Python调用

```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://apihub.agnes-ai.com/v1",
)

response = client.chat.completions.create(
    model="agnes-2.5-flash",
    messages=[
        {"role": "system", "content": "你是一个专业的Python编程助手。"},
        {"role": "user", "content": "解释一下Python中的GIL是什么？"}
    ],
    temperature=0.7,
    max_tokens=500,
    stream=False,
)

print(response.choices[0].message.content)
```

## 流式输出（Streaming）

设置 `stream: true` 启用流式输出，模型会逐块返回生成内容，显著降低首字延迟：

```python
response = client.chat.completions.create(
    model="agnes-2.5-flash",
    messages=[{"role": "user", "content": "写一首关于AI的短诗。"}],
    stream=True,  # 启用流式
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()
```

流式响应中每个chunk的结构：
```json
{
  "id": "chatcmpl-xxx",
  "choices": [
    {
      "delta": {"content": "部分内容"},
      "finish_reason": null,
      "index": 0
    }
  ]
}
```

最后一个chunk的 `finish_reason` 为 `stop`，表示生成完成。

> 事实溯源：README.md L83-95

## 工具调用（Function Calling / Tool Calling）

`agnes-2.5-flash` 和 `agnes-2.0-flash` 支持工具调用能力，模型可以根据用户问题自动选择调用预定义的工具。

定义工具格式：

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的当前天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，如北京、上海"},
                },
                "required": ["city"]
            }
        }
    }
]
```

发起工具调用请求：

```python
response = client.chat.completions.create(
    model="agnes-2.5-flash",
    messages=[{"role": "user", "content": "北京今天天气怎么样？"}],
    tools=tools,
    tool_choice="auto",
)
```

模型返回工具调用时，需要执行工具并将结果返回给模型，形成完整的Agent工作流。完整示例见 [Agent工作流示例](/examples/agent-workflow.md)。

> 事实溯源：F-008、README.md L105

## 图像理解（视觉能力）

支持在user消息中传入图像URL，实现图像理解：

```python
messages=[
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "这张图片里有什么？"},
            {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
        ]
    }
]
```

## 关键参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | string | 必填 | 模型ID，如 `agnes-2.5-flash` |
| `messages` | array | 必填 | 对话消息数组 |
| `stream` | boolean | false | 是否启用流式输出 |
| `temperature` | float | 0.7 | 采样温度，0=确定性输出，1=更有创造性 |
| `max_tokens` | integer | null | 最大生成token数，不填则自动决定 |
| `tools` | array | null | 可用工具定义列表 |
| `tool_choice` | string/object | "auto" | 工具选择策略 |

## 相关概念

- [5分钟快速开始](/concepts/01-getting-started.md)
- [API认证与安全](/concepts/02-api-authentication.md)
- [图像生成API](/concepts/04-image-generation.md)
- [视频生成API](/concepts/05-video-generation.md)
- [Python对话示例](/examples/chat-completion.md)
