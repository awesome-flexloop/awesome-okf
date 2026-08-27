---
type: Example
title: Python 对话补全示例
description: 最基础的非流式对话补全示例，演示如何使用OpenAI SDK调用AgnesAI文本模型
tags: [示例, Python, 对话补全, 基础调用]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T21:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T21:40:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: official-readme
    resource: /references/readme.md
    title: Agnes AI 官方README
  - id: example-chat
    resource: ../../../external/libs/models/AgnesAI/AgnesAI-Models/examples/python/chat_completion.py
    title: 官方chat_completion.py示例
---

# Python 对话补全示例

本示例演示最基础的非流式对话补全调用，适合后端服务等不需要实时输出的场景。

## 前置条件

- Python 3.9+
- 已安装 `openai>=1.40.0`
- 已设置 `AGNES_API_KEY` 环境变量

## 完整代码

```python
import os
from openai import OpenAI

# 初始化客户端
client = OpenAI(
    api_key=os.environ["AGNES_API_KEY"],
    base_url="https://apihub.agnes-ai.com/v1",
)

# 发送对话补全请求（非流式）
response = client.chat.completions.create(
    model="agnes-2.5-flash",  # 推荐使用最新模型
    messages=[
        {
            "role": "user",
            "content": "写一个API集成测试的简短检查清单。",
        }
    ],
    temperature=0.7,
    max_tokens=500,
)

# 打印完整回复
print("AI回复：")
print(response.choices[0].message.content)
```

> 代码基于官方示例修改，将模型升级为推荐的 `agnes-2.5-flash`。

## 运行方式

```bash
# 设置环境变量
export AGNES_API_KEY="your_api_key_here"

# 运行示例
python chat_completion.py
```

## 响应结构说明

非流式调用返回的 `response` 对象核心字段：

```python
# 回复内容
content = response.choices[0].message.content

# 完成原因："stop"=正常结束, "length"=达到max_tokens截断
finish_reason = response.choices[0].finish_reason

# token用量统计
usage = response.usage
print(f"Prompt tokens: {usage.prompt_tokens}")
print(f"Completion tokens: {usage.completion_tokens}")
print(f"Total tokens: {usage.total_tokens}")

# 请求ID（用于问题排查）
request_id = response.id
```

## 带System Prompt的版本

可以通过system消息设定AI的行为：

```python
response = client.chat.completions.create(
    model="agnes-2.5-flash",
    messages=[
        {
            "role": "system",
            "content": "你是一个简洁的API集成助手，回答不超过三点。",
        },
        {
            "role": "user",
            "content": "API集成上线前需要检查哪三点？",
        },
    ],
)
```

## 多轮对话示例

将历史消息都传入messages数组即可实现多轮对话：

```python
messages = [
    {"role": "system", "content": "你是一个Python编程助手。"},
    {"role": "user", "content": "什么是列表推导式？"},
    {"role": "assistant", "content": "列表推导式是Python中创建列表的简洁语法..."},
    {"role": "user", "content": "给我一个例子。"},  # 模型可以看到上下文
]

response = client.chat.completions.create(
    model="agnes-2.5-flash",
    messages=messages,
)
```

## 常见问题

**Q: 为什么不直接打印response？**
A: response对象包含很多元数据，直接打印会输出大量调试信息。通常只需要 `response.choices[0].message.content` 获取文本内容。

**Q: temperature参数怎么选？**
A: 事实性问答用0.1-0.3（更确定），创意写作用0.7-1.0（更多样），代码生成用0.0-0.2。

## 相关示例

- 流式对话示例 — 逐字输出效果
- [OpenAI兼容客户端配置](openai-compatible.md) — 最小化客户端配置
- [Agent工作流示例](agent-workflow.md) — 工具调用完整流程

## 相关概念

- [对话补全 API](../concepts/03-chat-completions.md)
- [API认证与安全](../concepts/02-api-authentication.md)
- [错误处理与调试](../concepts/07-error-handling.md)
