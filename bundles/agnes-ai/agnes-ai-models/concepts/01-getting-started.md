---
type: Concept
title: 5分钟快速开始
description: 从环境准备到第一个API调用，快速完成AgnesAI API接入，包含Python和curl两种方式
tags: [快速开始, 环境准备, 第一个调用, Python SDK]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T21:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T21:40:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: official-readme
    resource: /references/readme.md
    title: Agnes AI 官方README
---

# 5分钟快速开始

本教程将引导你在5分钟内完成AgnesAI API的环境准备并发送第一个请求。

## 前置条件

- Python 3.9 或更高版本
- 有效的AgnesAI API密钥（从 https://platform.agnes-ai.com/ 获取）
- 能够访问 `https://apihub.agnes-ai.com` 的网络环境

> 事实溯源：F-005、F-007

## 步骤1：安装依赖

AgnesAI使用OpenAI兼容接口，因此可以直接使用官方OpenAI Python SDK：

```bash
pip install openai>=1.40.0 requests>=2.32.0
```

或者通过requirements.txt安装：

```bash
pip install -r requirements.txt
```

> 事实溯源：F-007

## 步骤2：配置API密钥

**安全提示：永远不要将API密钥硬编码在代码中或提交到版本控制系统。** 使用环境变量管理密钥：

```bash
# Linux/macOS
export AGNES_API_KEY="your_api_key_here"

# Windows PowerShell
$env:AGNES_API_KEY="your_api_key_here"
```

> 事实溯源：F-013、F-015

## 步骤3：第一个Python调用（流式对话）

创建 `quickstart.py` 文件：

```python
import os
from openai import OpenAI

# 初始化客户端 - 只需要修改base_url和api_key
client = OpenAI(
    api_key=os.getenv("AGNES_API_KEY"),
    base_url="https://apihub.agnes-ai.com/v1",
)

# 发送流式对话请求
response = client.chat.completions.create(
    model="agnes-2.5-flash",
    messages=[
        {"role": "user", "content": "用一句话介绍你自己。"}
    ],
    stream=True,
)

# 逐块打印流式响应
for chunk in response:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
print()
```

运行脚本：

```bash
python quickstart.py
```

> 事实溯源：F-005、F-008、README.md L75-95

## 步骤4：curl命令快速验证

如果你不想写代码，可以直接用curl快速验证API是否正常工作：

```bash
curl https://apihub.agnes-ai.com/v1/chat/completions \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-2.0-flash",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "stream": false
  }'
```

> 事实溯源：README.md L131-145

## 模型选择建议

| 使用场景 | 推荐模型 |
|---------|---------|
| 快速测试、高吞吐对话 | `agnes-1.5-flash` |
| 编码、工具调用、Agent工作流（推荐） | `agnes-2.5-flash` |
| 旧系统兼容、稳定版本 | `agnes-2.0-flash` |

> 事实溯源：F-016~F-018

## 常见问题快速排查

| 问题 | 可能原因 | 快速解决 |
|------|---------|---------|
| 401 Unauthorized | API密钥错误或未加载 | 检查环境变量名是否正确，密钥是否复制完整 |
| 429 Too Many Requests | 触发速率限制 | 降低并发，添加重试逻辑，参考[速率限制](/concepts/06-rate-limits.md) |
| 连接超时 | 网络问题 | 检查网络连接，确认可以访问apihub.agnes-ai.com |

## 相关概念

- [Agnes AI 简介](/concepts/00-introduction.md)
- [API认证与安全](/concepts/02-api-authentication.md) — 深入了解认证机制与安全规范
- [对话补全API](/concepts/03-chat-completions.md) — 对话接口完整参数说明
- [Python基础对话示例](/examples/chat-completion.md) — 可直接运行的完整示例
