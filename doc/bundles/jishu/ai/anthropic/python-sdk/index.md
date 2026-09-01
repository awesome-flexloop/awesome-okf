---
okf_version: "0.2"
type: index
title: "Anthropic Python SDK Wiki"
description: "Anthropic 官方 Python SDK 中文 Wiki——同步/异步双轨客户端、Messages API、流式处理、工具调用（Function Calling）、多模态视觉、多云后端（AWS Bedrock/Google Vertex）、Beta Agents/Memory/Skills、中间件扩展的完整中文文档与示例。"
tags: [anthropic, claude, python, sdk, llm, messages, streaming, tool-use, vision, bedrock, vertex, agents]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-001~F-090
    resource: /python-sdk/references/sdk-client.md
    title: "Anthropic Python SDK 客户端入口与基础设施参考"
---

# Anthropic Python SDK Wiki

**Anthropic Python SDK** 是 [Anthropic](https://www.anthropic.com) 官方提供的 Python 客户端库（基于 `external/libs/anthropics/anthropic-sdk-python` 源码，由 Stainless 代码生成器构建），提供同步（`Anthropic`）和异步（`AsyncAnthropic`）双轨 API，覆盖 Messages API、流式处理（SSE）、工具调用（Function Calling）、多模态视觉、文件管理、分页查询、多云后端支持（AWS Bedrock / Google Vertex AI）、Beta Agents/Memory/Sessions/Skills、中间件扩展等完整功能。

## 快速开始

```python
from anthropic import Anthropic

client = Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "你好"}]
)
print(message.content[0].text)
```

安装：`pip install anthropic`

## 文档导航

### 📚 概念文档（按学习路径排列）

| 序号 | 主题 | 说明 |
|------|------|------|
| 00 | [整体架构概览](concepts/00-overview.md) | 同步/异步双轨设计、Stainless 生成架构、懒加载代理、模块组织 |
| 01 | [客户端初始化与配置](concepts/01-client-init.md) | API Key、base_url、超时、自定义 http_client、重试、代理 |
| 02 | [Messages API 基础](concepts/02-messages-basics.md) | 消息结构、角色、content blocks、token 计数、系统提示 |
| 03 | [流式处理](concepts/03-streaming.md) | SSE 流式、MessageStream、事件类型、上下文管理器、stream() 辅助方法 |
| 04 | [工具调用（Function Calling）](concepts/04-tool-use.md) | 工具定义、tool_use/tool_result、并行调用、强制工具选择 |
| 05 | [视觉与文件处理](concepts/05-vision-files.md) | 图片输入（base64/URL）、文档理解、文件上传 API |
| 06 | [分页与模型列表](concepts/06-pagination-models.md) | SyncPage/AsyncPage 分页器、models.list()、自动分页迭代 |
| 07 | [多云后端支持](concepts/07-multi-cloud.md) | AWS Bedrock 继承、Google Vertex AI 继承、认证差异、模型映射 |
| 08 | [Beta Agents 体系](concepts/08-beta-agents.md) | Agents SDK、Memory 记忆、Sessions 会话、Skills 技能、版本化 Beta API |
| 09 | [中间件与扩展机制](concepts/09-middleware-extended.md) | 中间件管线、请求/响应拦截、自定义传输、错误处理、重试策略 |

### 💡 示例文档

| 示例 | 说明 |
|------|------|
| [基础对话](examples/01-basic-chat.md) | 客户端初始化 → 同步 messages.create → 解析响应 → 多轮对话 |
| [流式对话](examples/02-streaming-chat.md) | stream() 上下文管理器 → 事件处理 → 增量文本拼接 → 最终消息聚合 |
| [工具调用](examples/03-tool-use.md) | 工具定义 → 模型选择工具 → 执行工具 → 返回 tool_result 闭环 |
| [多模态视觉](examples/04-vision.md) | 图片 base64 编码 → image content block → 文档理解示例 |
| [Bedrock/Vertex 多云](examples/05-bedrock-vertex.md) | AnthropicBedrock/AnthropicVertex 初始化 → 认证配置 → 跨云调用 |
| [Thinking 与扩展思考](examples/06-thinking-extended.md) | extended thinking 配置 → reasoning content → 思考预算控制 |

### 📖 API 参考

| 参考文档 | 覆盖范围 |
|----------|---------|
| [客户端入口与基础设施](references/sdk-client.md) | Anthropic/AsyncAnthropic、配置常量、HTTP 传输层、Stream 基类、异常体系 |
| [Messages API](references/messages-api.md) | messages.create、消息类型、ContentBlock、Usage、StopReason、Token 计数 |
| [工具调用与 Beta API](references/tools-beta.md) | Tool 定义、ToolUseBlock、Beta 命名空间、Agents/Memory/Sessions/Skills |
| [多云后端](references/multi-cloud.md) | AnthropicBedrock、AnthropicVertex、认证提供者、区域配置、模型 ARN |
| [类型定义与错误处理](references/types-errors.md) | 核心类型模型、APIError 家族、错误码、重试判定、RateLimit |
| [源码结构与扩展点](references/source.md) | Stainless 生成结构、资源类组织、中间件接口、自定义扩展指南 |

## SDK 能力速查表

| 能力域 | 同步入口 | 异步入口 | 传输方式 |
|--------|---------|---------|---------|
| Messages（对话） | `client.messages` | `async_client.messages` | HTTP REST / SSE |
| Streaming（流式） | `client.messages.stream(...)` | `async_client.messages.stream(...)` | HTTP SSE |
| Tools（工具调用） | `client.messages.create(tools=[...])` | 异步版本 | HTTP REST / SSE |
| Vision（视觉） | `client.messages.create(messages=[...image...])` | 异步版本 | HTTP (JSON/base64) |
| Files（文件） | `client.files` | `async_client.files` | HTTP multipart |
| Models（模型列表） | `client.models` | `async_client.models` | HTTP REST (分页) |
| Beta Agents | `client.beta.agents` | `async_client.beta.agents` | HTTP REST / SSE |
| Beta Memory Stores | `client.beta.memory_stores` | `async_client.beta.memory_stores` | HTTP REST |
| Beta Sessions | `client.beta.sessions` | `async_client.beta.sessions` | HTTP REST / SSE |
| Beta Skills | `client.beta.skills` | `async_client.beta.skills` | HTTP REST |
| Multi-Cloud (Bedrock) | `AnthropicBedrock(...)` | `AsyncAnthropicBedrock(...)` | AWS SigV4 签名 |
| Multi-Cloud (Vertex) | `AnthropicVertex(...)` | `AsyncAnthropicVertex(...)` | Google OAuth |
| Middleware（中间件） | 自定义 `httpx.BaseTransport` / 中间件链 | 同左 | 传输层拦截 |

## 链接索引

- [概念文档索引](concepts/index.md)
- [示例文档索引](examples/index.md)
- [API 参考索引](references/index.md)

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
