---
type: reference
title: "Anthropic Python SDK 源码版本与目录结构参考"
description: "anthropic-sdk-python 项目简介、src/anthropic/ 源码目录结构总览、Stainless 代码生成机制、手动扩展文件识别与版本信息的完整参考。"
tags: [source, directory, structure, stainless, codegen, version]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-001~F-090
    resource: /python-sdk/references/source.md
    title: "Anthropic Python SDK 源码版本与目录结构参考"
---

# Anthropic Python SDK 源码版本与目录结构参考

本文档登记 `anthropic-sdk-python` 项目的基本信息、源码目录结构、Stainless 代码生成机制说明、手动扩展文件识别方式以及版本号定义位置。

## 项目简介

`anthropic-sdk-python` 是 Anthropic 官方提供的 Python SDK，用于访问 Claude 系列大语言模型的 REST API。SDK 采用 [Stainless](https://stainlessapi.com/) 代码生成器自动生成，同时支持人工编写扩展代码，保持同步/异步 API 完全对称的架构设计。

**核心特性**：
- 同步/异步双客户端对称设计（`Anthropic` / `AsyncAnthropic`）
- 内置自动重试、超时控制、连接池管理
- 支持流式响应（SSE）处理
- 内置工具调用（Function Calling）运行器
- 多云后端支持（AWS Bedrock、Google Vertex AI、原生 AWS、Google Cloud）
- Beta 实验性功能命名空间隔离
- 中间件扩展机制
- Pydantic 类型系统支持

## 版本信息

SDK 版本号定义在 `src/anthropic/_version.py` 文件中，可通过以下方式访问：

```python
import anthropic
print(anthropic.__version__)
```

API 版本通过请求头 `anthropic-version` 自动设置，当前默认版本为 `"2023-06-01"`（见 F-008、F-009）。

## 源码目录结构总览

源码根目录为 `src/anthropic/`，以下是核心模块与子目录的说明：

```
src/anthropic/
├── __init__.py              # 包入口，导出所有公共 API
├── _version.py              # 版本号定义
├── _constants.py            # 全局常量（超时、重试、连接池等）
├── _client.py               # Anthropic/AsyncAnthropic 客户端主类 + 别名 + 响应装饰类
├── _base_client.py          # 基础客户端实现（SyncAPIClient/AsyncAPIClient）
├── _models.py               # BaseModel 基类与模型工具
├── _streaming.py            # Stream/AsyncStream 核心流类 + SSEDecoder/ServerSentEvent
├── _exceptions.py           # 异常体系定义
├── _middleware.py           # Middleware 基类与验证函数
├── _resource.py             # SyncAPIResource/AsyncAPIResource 资源基类
├── _compat.py               # Python 版本兼容性垫片
├── _types.py                # 内部类型定义
├── _utils.py                # 工具函数
├── _qs.py                   # 查询字符串处理
├── _files.py                # 文件上传处理
├── _multipart.py            # multipart/form-data 编码
├── py.typed                 # PEP 561 类型标记
├── resources/               # API 资源类目录
│   ├── __init__.py
│   ├── messages/            # Messages API 资源
│   │   ├── __init__.py
│   │   └── messages.py      # Messages 类 + Batches 子资源
│   ├── models/              # Models 资源
│   ├── files/               # Files 资源
│   └── beta/                # Beta API 命名空间
│       ├── __init__.py
│       ├── beta.py          # Beta 入口类
│       ├── agents/          # Agents 资源（含 versions 子资源）
│       ├── sessions/        # Sessions 资源（含 threads/events/resources）
│       ├── memory_stores/   # Memory Stores 资源（含 memories/versions）
│       └── skills/          # Skills 资源（含 versions）
├── lib/                     # 高级功能与手动扩展库（非自动生成）
│   ├── __init__.py
│   ├── streaming/           # 高级流式处理
│   │   ├── __init__.py
│   │   └── _messages.py     # MessageStream/MessageStreamManager
│   ├── tools/               # 工具调用系统
│   │   ├── __init__.py
│   │   ├── _beta_functions.py     # BetaFunctionTool + 装饰器
│   │   ├── _beta_runner.py        # BaseToolRunner 工具运行器
│   │   ├── _beta_builtin_memory_tool.py  # 内置 Memory 工具
│   │   ├── mcp.py            # MCP 协议集成
│   │   ├── agent_toolset.py  # Agent 工具集
│   │   ├── _tool_dispatch.py # 工具分发逻辑
│   │   ├── _skills.py        # Skills 集成
│   │   ├── _memories.py      # Memories 集成
│   │   └── _file_store.py    # 文件存储集成
│   ├── middleware/          # 内置中间件
│   │   └── _fallbacks.py    # BetaRefusalFallbackMiddleware
│   ├── aws/                 # AWS 原生客户端
│   │   ├── __init__.py
│   │   ├── _client.py       # AnthropicAWS/AsyncAnthropicAWS
│   │   ├── _auth.py         # SigV4 签名
│   │   └── _credentials.py  # 凭证管理
│   ├── bedrock/             # AWS Bedrock 客户端
│   │   ├── __init__.py
│   │   ├── _client.py       # AnthropicBedrock/AsyncAnthropicBedrock
│   │   ├── _beta.py         # Bedrock Beta 支持
│   │   ├── _beta_messages.py # Bedrock Beta 消息
│   │   └── _stream.py       # Bedrock 流式处理
│   ├── vertex/              # Google Vertex AI 客户端
│   │   ├── __init__.py
│   │   ├── _client.py       # AnthropicVertex/AsyncAnthropicVertex
│   │   └── ...              # Vertex Beta 支持等
│   ├── google_cloud/        # Google Cloud 客户端
│   │   └── _client.py       # AnthropicGoogleCloud/AsyncAnthropicGoogleCloud
│   └── credentials/         # 统一凭证抽象
│       ├── _providers.py    # 凭证提供者
│       ├── _chain.py        # 凭证链
│       ├── _cache.py        # 凭证缓存
│       └── _auth.py         # 认证核心
└── types/                   # 类型定义目录
    ├── __init__.py
    └── beta/                # Beta API 类型定义
```

## 核心模块说明

### 顶层核心模块（`_*.py` 文件）

这些文件构成 SDK 的基础设施层：

| 文件 | 核心内容 | 代码生成 |
|------|---------|---------|
| `__init__.py` | 公共 API 导出，`__all__` 列表 | 自动生成 + 手动维护 |
| `_client.py` | `Anthropic`/`AsyncAnthropic`/`Client`/`AsyncClient`/`AnthropicWithRawResponse`/`AnthropicWithStreamedResponse` | 自动生成 |
| `_base_client.py` | `SyncAPIClient`/`AsyncAPIClient` 基础 HTTP 客户端逻辑 | 自动生成 |
| `_constants.py` | `DEFAULT_TIMEOUT`/`DEFAULT_MAX_RETRIES`/`INITIAL_RETRY_DELAY`/`MAX_RETRY_DELAY`/`DEFAULT_CONNECTION_LIMITS`/`MODEL_NONSTREAMING_TOKENS` | 自动生成 + 手动扩展 |
| `_models.py` | `BaseModel` Pydantic 基类 | 自动生成 |
| `_streaming.py` | `Stream`/`AsyncStream`/`SSEDecoder`/`ServerSentEvent` | 自动生成 |
| `_exceptions.py` | 完整异常体系（`AnthropicError`/`APIError`/`APIStatusError` 及所有子类） | 自动生成 |
| `_middleware.py` | `Middleware` 基类/`CallNext`/`AsyncCallNext`/`validate_sync_middleware`/`validate_async_middleware` | 自动生成 + 手动扩展 |
| `_resource.py` | `SyncAPIResource`/`AsyncAPIResource` 资源基类 | 自动生成 |
| `_compat.py` | Python 版本兼容性垫片 | 自动生成 |

### resources/ 目录（自动生成）

`resources/` 目录下的所有文件均由 Stainless 代码生成器自动生成，对应 Anthropic REST API 的各个资源端点：

| 子目录 | 对应 API | 主要类 |
|-------|---------|--------|
| `messages/` | `/v1/messages` | `Messages`/`AsyncMessages`/`Batches` |
| `models/` | `/v1/models` | `Models`/`AsyncModels` |
| `files/` | `/v1/files` | `Files`/`AsyncFiles` |
| `beta/` | `/v1/*?beta=true` | `Beta`/`AsyncBeta` 及所有 Beta 子资源 |

> **重要**：`resources/` 目录下的文件**不应手动修改**，重新运行代码生成时会被覆盖。

### lib/ 目录（手动扩展）

`lib/` 目录是 SDK 的手动扩展库，包含 Stainless 代码生成范围之外的高级功能，这些文件**不会被代码生成覆盖**：

| 子目录 | 功能 | 说明 |
|-------|------|------|
| `lib/streaming/` | 高级流式处理 | `MessageStream` 提供 `text_stream`/`get_final_message()` 等便捷接口 |
| `lib/tools/` | 工具调用系统 | `beta_tool` 装饰器、`ToolRunner` 自动多轮工具调用循环、MCP 集成等 |
| `lib/middleware/` | 内置中间件 | `BetaRefusalFallbackMiddleware` 等官方中间件实现 |
| `lib/aws/` | AWS 原生客户端 | SigV4 签名、AWS 凭证链 |
| `lib/bedrock/` | AWS Bedrock 客户端 | Bedrock 特有签名与路由逻辑、Beta 支持 |
| `lib/vertex/` | Google Vertex AI 客户端 | Vertex 认证、区域路由、Beta 支持 |
| `lib/google_cloud/` | Google Cloud 客户端 | Google Cloud 平台接入 |
| `lib/credentials/` | 凭证抽象 | 统一的多平台凭证提供者链与缓存 |

### types/ 目录

`types/` 目录包含所有请求/响应的 Pydantic 模型类型定义和 TypedDict：
- `types/` 根目录：稳定版 API 类型
- `types/beta/`：Beta 实验性 API 类型

## Stainless 代码生成说明

Anthropic Python SDK 使用 [Stainless](https://stainlessapi.com/) 平台根据 OpenAPI 规范自动生成大部分客户端代码。

### 代码生成覆盖范围

自动生成的文件包括：
1. 客户端类（`_client.py`、`_base_client.py`）
2. 资源类（`resources/` 下所有文件）
3. 类型定义（`types/` 下大部分文件）
4. 基础异常类（`_exceptions.py`）
5. 基础流类（`_streaming.py` 核心）
6. 常量定义（`_constants.py` 基础部分）

### 手动维护文件标记

Stainless 生成的文件开头通常包含类似以下的标记注释：

```python
# File generated by Stainless, DO NOT EDIT.
# If you wish to contribute, please open a PR and a maintainer will help you.
```

而手动维护的文件（如 `lib/` 下的文件）则**没有**此类自动生成标记，可以安全地手动编辑。

### 代码与扩展的关系

SDK 的架构设计清晰分离了自动生成代码和手动扩展：

- **自动生成层**（`resources/`、核心 `_*.py`）：提供与 REST API 一一对应的基础能力，保证与 API 规范的一致性
- **手动扩展层**（`lib/`）：在基础 API 之上提供更高级的便捷功能，如：
  - `MessageStream` 简化流式文本提取
  - `beta_tool`/`ToolRunner` 自动化工具调用循环
  - 多云后端适配（Bedrock/Vertex/AWS/GCP）
  - 中间件实现

这种分层设计确保 API 更新时可以通过重新生成代码快速跟进，同时高级功能的迭代不受代码生成限制。

## 入口导出（__init__.py）

`src/anthropic/__init__.py` 是 SDK 的公共入口，导出所有用户需要使用的类和异常：

**主要导出类**（来自 F-001、F-002）：
- 客户端：`Anthropic`、`AsyncAnthropic`、`Client`（别名）、`AsyncClient`（别名）
- 流类：`Stream`、`AsyncStream`
- 配置：`Timeout`、`RequestOptions`
- 多云客户端：`AnthropicBedrock`、`AsyncAnthropicBedrock`、`AnthropicVertex`、`AsyncAnthropicVertex`、`AnthropicAWS`、`AsyncAnthropicAWS`、`AnthropicGoogleCloud`、`AsyncAnthropicGoogleCloud`
- 所有异常类

导入路径示例：

```python
# 核心客户端
from anthropic import Anthropic, AsyncAnthropic, Client, AsyncClient

# 多云客户端
from anthropic import AnthropicBedrock, AnthropicVertex, AnthropicAWS, AnthropicGoogleCloud

# 流类
from anthropic import Stream, AsyncStream

# 异常
from anthropic import AnthropicError, APIError, APIStatusError, RateLimitError

# 高级工具系统（从 lib 子模块导入）
from anthropic.lib.tools import beta_tool, BetaToolRunner
from anthropic.lib.streaming import MessageStream
```
