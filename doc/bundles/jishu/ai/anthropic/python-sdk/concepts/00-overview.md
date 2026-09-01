---
type: concept
title: "Anthropic Python SDK 整体架构概览"
description: "一文理解 Anthropic Python SDK 的设计哲学、Stainless 代码生成机制、同步/异步双轨架构、四层模块分层与六大核心能力，快速建立 SDK 全局认知。"
tags: [overview, architecture, stainless, sync, async, module-layers]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-001~F-090
    resource: /python-sdk/references/source.md
    title: "Anthropic Python SDK 源码版本与目录结构参考"
  - id: F-001~F-015,F-074~F-084
    resource: /python-sdk/references/sdk-client.md
    title: "Anthropic Python SDK 客户端入口与基础设施参考"
  - id: F-016~F-037
    resource: /python-sdk/references/messages-api.md
    title: "Anthropic Python SDK 消息 API 与流式处理参考"
  - id: F-038~F-058
    resource: /python-sdk/references/tools-beta.md
    title: "Anthropic Python SDK 工具系统与 Beta API 参考"
  - id: F-059~F-073
    resource: /python-sdk/references/multi-cloud.md
    title: "Anthropic Python SDK 多云后端认证参考"
  - id: F-085~F-090
    resource: /python-sdk/references/types-errors.md
    title: "Anthropic Python SDK 类型系统与异常体系参考"
---

# Anthropic Python SDK 整体架构概览

Anthropic Python SDK 是 Anthropic 官方提供的 Python 开发工具包，用于访问 Claude 系列大语言模型的 REST API。无论你是构建 AI 聊天机器人、开发智能体应用、集成代码助手，还是在多云环境（AWS Bedrock / Google Vertex AI）中部署 Claude，这个 SDK 都能提供类型安全、体验一致的编程接口。

**本文适合谁**：第一次接触 Anthropic Python SDK 的开发者、希望快速理解 SDK 全局架构的工程师、需要在项目中选型 Claude 接入方案的技术负责人。

## SDK 设计哲学

SDK 基于 [Stainless](https://stainlessapi.com/) 代码生成平台构建，核心设计理念可以概括为三点：

1. **同步/异步完全对称**：提供 `Anthropic` 和 `AsyncAnthropic` 两套完全对等的客户端，从顶层类到资源类再到流处理类一一对应，同步用户不会被异步方法干扰，异步用户也能获得完整的类型提示
2. **生成代码与手动扩展清晰分离**：`resources/` 目录下与 REST API 一一对应的基础代码由 Stainless 自动生成，保证与 API 规范的一致性；`lib/` 目录下的高级功能（工具运行器、多云适配、中间件等）由人工维护，提供更便捷的开发体验
3. **多云后端零学习成本**：`AnthropicBedrock`、`AnthropicVertex` 等多云客户端通过继承核心客户端实现，上层 API（`messages.create` 等）用法与官方客户端 100% 兼容，仅初始化参数不同

## 四层模块分层架构

SDK 采用清晰的四层架构设计，职责划分明确：

```
┌─────────────────────────────────────────────────────────────┐
│  lib/ 扩展层 (手动维护)                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ streaming │ │  tools   │ │middleware│ │aws/bedrock/   │  │
│  │MessageStr│ │ToolRunner│ │FallbackM│ │vertex/gcp     │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  resources/ 资源层 (自动生成)                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ messages │ │  models  │ │  files   │ │     beta      │  │
│  │  .create │ │  .list   │ │  .upload │ │agents/session│  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  types/ 类型层                                               │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Message, MessageParam, ContentBlock, ToolParam...    │ │
│  │  (基于 Pydantic BaseModel，提供完整类型校验)           │ │
│  └───────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  _client.py / _base_client.py 客户端层 (自动生成)            │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  HTTP 客户端、重试机制、超时控制、连接池、认证签名     │ │
│  │  default_headers、中间件管线、异常映射                 │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

- **客户端层**：处理 HTTP 通信、认证、重试、超时、连接池等基础设施，对应 `_client.py`、`_base_client.py`、`_constants.py` 等顶层模块
- **资源层**：每个 REST API 端点对应一个资源类（如 `Messages` 对应 `/v1/messages`），提供 `.create()`、`.list()` 等方法，全部由 Stainless 自动生成，位于 `resources/` 目录
- **类型层**：所有请求/响应对象均继承自 Pydantic `BaseModel`，提供类型安全和自动序列化/反序列化，位于 `types/` 目录
- **lib 扩展层**：在基础 API 之上提供更高层级的便捷功能，位于 `lib/` 目录，这部分不会被代码生成覆盖

## 同步/异步双轨设计

SDK 最显著的架构特征是同步/异步双轨完全对称：

- `Anthropic`（同步）继承自 `SyncAPIClient`，所有方法直接返回结果
- `AsyncAnthropic`（异步）继承自 `AsyncAPIClient`，所有方法返回协程，需要 `await`
- 两套客户端的 API 一一对应：`client.messages.create()` ↔ `await async_client.messages.create()`
- 通过 `X-Stainless-Async` 请求头自动标识请求类型，用户无需手动设置
- `Client` 是 `Anthropic` 的别名，`AsyncClient` 是 `AsyncAnthropic` 的别名，两者完全等价

```python
# 同步用法
from anthropic import Anthropic
client = Anthropic()
message = client.messages.create(...)

# 异步用法（API 完全对称）
from anthropic import AsyncAnthropic
async_client = AsyncAnthropic()
message = await async_client.messages.create(...)
```

这种设计看似有代码重复，但保证了最佳的 IDE 体验——同步代码中不会出现异步方法的类型提示，反之亦然，避免了误用。

## 六大核心能力速览

### 1. Messages API — Claude 的核心对话接口

Messages API 是与 Claude 交互的主要入口，取代了早期的 Completions API。支持多轮对话、系统提示词、文本生成、流式输出等基础功能，所有对话场景都通过 `client.messages.create()` 发起。

### 2. Streaming 流式响应

支持 SSE（Server-Sent Events）流式输出，提供两种使用方式：
- 基础 `Stream` 类：逐个迭代 SSE 事件（`message_start`、`content_block_delta` 等）
- 高级 `MessageStream` 类：提供 `text_stream` 文本流迭代器、`get_final_message()` 累积完整消息等便捷接口

### 3. Tools 工具调用（Function Calling）

内置完整的工具调用框架：
- `@beta_tool` / `@beta_async_tool` 装饰器：将普通 Python 函数包装为 Claude 可调用的工具
- `ToolRunner`：自动处理多轮工具调用循环，无需手动管理"模型返回 tool_use → 执行工具 → 回传结果"的流程
- 支持同步和异步工具，内置 Memory 等官方工具

### 4. Multi-Cloud 多云后端支持

除了直接访问 Anthropic 官方 API，SDK 还内置支持主流云平台的 Claude 托管服务：
- `AnthropicBedrock`：AWS Bedrock 平台，使用 AWS SigV4 签名
- `AnthropicVertex`：Google Cloud Vertex AI，支持区域路由
- `AnthropicAWS`：原生 AWS endpoint
- `AnthropicGoogleCloud`：Google Cloud 平台

所有多云客户端继承自核心客户端，`messages.create()` 等 API 用法完全一致。

### 5. Beta API 实验性功能

实验性 API 统一挂在 `client.beta` 独立命名空间下，自动添加对应的 `anthropic-beta` 请求头，包括：
- Agents：托管智能体管理
- Memory Stores：长期记忆存储
- Sessions：会话状态管理
- Skills：可复用技能
- 更多实验性功能持续迭代中

> ⚠️ Beta API 是实验性的，可能在未来版本中发生破坏性变更。

### 6. Middleware 中间件扩展

提供类 ASGI 的中间件机制，支持请求/响应拦截：
- 继承 `Middleware` 基类，实现 `handle()`（同步）或 `handle_async()`（异步）方法
- 中间件严格区分同步/异步，不允许混用
- 内置 `BetaRefusalFallbackMiddleware` 等官方中间件
- 可用于日志记录、请求重试、自定义认证、响应转换等场景

## 安装与快速开始

### 安装

使用 pip 安装：

```bash
pip install anthropic
```

### 最小可运行示例

首先设置 API Key 环境变量：

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-..."

# Linux/macOS
export ANTHROPIC_API_KEY="sk-ant-..."
```

然后运行第一个对话：

```python
from anthropic import Anthropic

client = Anthropic()

message = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]
)

print(message.content[0].text)
```

这就是一个完整的 Claude 对话——导入客户端、初始化、调用 `messages.create`、解析响应。

### 资源懒加载机制

需要注意的是，`client.messages`、`client.models`、`client.beta` 等资源属性都是**懒加载**的：客户端初始化时不会创建任何资源实例，首次访问时才动态实例化并缓存。这意味着：
- 初始化客户端开销很小
- 资源实例是线程安全的（只创建一次）
- 不要在初始化前尝试访问资源属性

## 文档导航

本 bundle 包含三类文档，形成完整的学习路径：

### concepts/ — 概念文档（你正在阅读的部分）

按难度分为三篇：
- **入门篇**：建立基础认知（本文 + 客户端初始化 + Messages API 基础）
- **核心篇**：掌握常用场景（流式处理、工具调用、视觉理解、分页与模型）
- **高级篇**：扩展能力（多云后端、Beta Agents/Memory、中间件与错误处理）

### references/ — API 参考文档

按模块组织的完整 API 手册，包含所有类、方法、参数、返回值的详细说明：
- [sdk-client.md](../references/sdk-client.md)：客户端与基础设施
- [messages-api.md](../references/messages-api.md)：消息与流式
- [tools-beta.md](../references/tools-beta.md)：工具与 Beta
- [multi-cloud.md](../references/multi-cloud.md)：多云后端
- [types-errors.md](../references/types-errors.md)：类型与异常
- [source.md](../references/source.md)：源码结构

### examples/ — 可运行示例

每个核心场景对应一个可直接复制运行的代码示例。

## 学习路径建议

推荐按以下顺序学习：

1. **本文（00-overview）**：建立全局认知，理解架构分层和核心能力
2. **[01-client-init.md](01-client-init.md)**：学习如何正确初始化和配置客户端
3. **[02-messages-basics.md](02-messages-basics.md)**：掌握 Messages API 的基础用法
4. 核心篇：流式、工具调用、视觉、分页
5. 高级篇：多云、Beta、中间件

## 相关概念

- [客户端初始化与配置](01-client-init.md) — 学习如何正确配置 Anthropic 客户端
- [Messages API 基础](02-messages-basics.md) — Claude 核心对话接口详解
- [流式处理](03-streaming.md) — 学习流式输出的两种使用方式
- [Anthropic Python SDK 客户端入口与基础设施参考](../references/sdk-client.md) — 客户端完整 API 手册
- [Anthropic Python SDK 源码版本与目录结构参考](../references/source.md) — 深入理解源码组织方式
