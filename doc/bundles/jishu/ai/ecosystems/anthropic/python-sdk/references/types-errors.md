---
type: reference
title: "Anthropic Python SDK 类型系统与异常体系参考"
description: "AnthropicError 异常基类、API 错误类层级、HTTP 状态码异常映射、BaseModel 基类、types/ 目录结构与兼容性模块的完整 API 参考。"
tags: [errors, exceptions, types, pydantic, status-code, compatibility]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-085~F-090
    resource: /python-sdk/references/types-errors.md
    title: "Anthropic Python SDK 类型系统与异常体系参考"
---

# Anthropic Python SDK 类型系统与异常体系参考

本文档登记 Anthropic Python SDK 的异常类继承体系、API 错误类属性、HTTP 状态码到异常类的映射、Pydantic 模型基类、types/ 类型目录结构以及兼容性模块。

## 异常体系总览

所有异常类定义在 `anthropic._exceptions` 模块中，形成清晰的继承层级：

```
Exception
  └── AnthropicError（所有 SDK 异常基类）
        ├── APIError（API 调用错误）
        │     ├── APIStatusError（带 HTTP 状态码的错误）
        │     │     ├── BadRequestError (400)
        │     │     ├── AuthenticationError (401)
        │     │     ├── PermissionDeniedError (403)
        │     │     ├── NotFoundError (404)
        │     │     ├── ConflictError (409)
        │     │     ├── RequestTooLargeError (413)
        │     │     ├── UnprocessableEntityError (422)
        │     │     ├── RateLimitError (429)
        │     │     ├── InternalServerError (5xx)
        │     │     ├── ServiceUnavailableError (503)
        │     │     ├── DeadlineExceededError (504)
        │     │     └── OverloadedError (529)
        │     └── APIConnectionError（网络连接错误）
        │           └── APITimeoutError（请求超时）
        └── RetryableError（可重试错误标记）
```

## 核心异常类

### AnthropicError（基类）

**类路径**：`anthropic.AnthropicError`

```python
class AnthropicError(Exception):
    """所有 Anthropic SDK 异常的基类。"""
```

所有 SDK 抛出的异常均继承自此类，可用于统一捕获：

```python
from anthropic import AnthropicError

try:
    client.messages.create(...)
except AnthropicError as e:
    print(f"SDK error: {e}")
```

### APIError

**类路径**：`anthropic.APIError`

继承自 `AnthropicError`，表示 API 调用过程中发生的错误：

| 属性 | 类型 | 说明 |
|------|------|------|
| `message` | `str` | 错误消息文本 |
| `request` | `httpx.Request` | 原始 HTTP 请求对象 |
| `body` | `object \| None` | 响应体内容（已解析为 Python 对象，通常为 dict） |

### APIStatusError

**类路径**：`anthropic.APIStatusError`

继承自 `APIError`，表示带有 HTTP 状态码的 API 错误响应：

| 属性 | 类型 | 说明 |
|------|------|------|
| `response` | `httpx.Response` | 原始 HTTP 响应对象 |
| `status_code` | `int` | HTTP 状态码（如 400、401、429、500 等） |
| `request_id` | `str \| None` | 请求 ID（用于向 Anthropic 支持团队排查问题） |
| `type` | `ErrorType \| None` | 错误类型枚举 |
| `workspace_id` | `str \| None` | Workspace ID（如适用） |

`APIStatusError` 是所有具体 HTTP 错误类的父类，可通过 `status_code` 属性判断具体错误类型：

```python
from anthropic import APIStatusError

try:
    client.messages.create(...)
except APIStatusError as e:
    if e.status_code == 429:
        print("Rate limited, retry after delay")
    elif e.status_code == 401:
        print("Invalid API key")
    print(f"Request ID: {e.request_id}")
```

### APIConnectionError

**类路径**：`anthropic.APIConnectionError`

继承自 `APIError`，表示无法连接到 API 服务器（网络问题、DNS 解析失败等）。

### APITimeoutError

**类路径**：`anthropic.APITimeoutError`

继承自 `APIConnectionError`，表示请求超时（超过 `DEFAULT_TIMEOUT` 配置的时间）。

### RetryableError

**类路径**：`anthropic.RetryableError`

继承自 `AnthropicError`，类体为空（仅用 `pass` 语句），用作**标记接口**，表示该错误是可重试的。SDK 的自动重试机制会识别并重试此类错误。

## HTTP 状态码 → 异常类映射

SDK 根据 HTTP 响应状态码自动抛出对应的异常类：

| HTTP 状态码 | 异常类 | 说明 |
|------------|--------|------|
| **400** | `BadRequestError` | 请求参数错误（如缺少必填参数、格式无效） |
| **401** | `AuthenticationError` | 认证失败（无效 API Key、Token 过期） |
| **403** | `PermissionDeniedError` | 权限不足（没有访问该资源的权限） |
| **404** | `NotFoundError` | 资源不存在（无效的模型 ID、请求路径错误） |
| **409** | `ConflictError` | 资源冲突（如并发修改冲突） |
| **413** | `RequestTooLargeError` | 请求体过大（超过 token 限制或请求大小限制） |
| **422** | `UnprocessableEntityError` | 请求格式正确但语义错误（如参数值不合法） |
| **429** | `RateLimitError` | 请求频率超限（需要退避重试） |
| **500** | `InternalServerError` | 服务器内部错误（Anthropic 服务端问题） |
| **503** | `ServiceUnavailableError` | 服务暂时不可用（维护或过载） |
| **504** | `DeadlineExceededError` | 网关超时 |
| **529** | `OverloadedError` | 服务过载（Anthropic 服务高负载） |
| **5xx** | `InternalServerError` | 其他 5xx 错误均映射为 InternalServerError |

> **注意**：429（RateLimitError）和 5xx 类错误默认会被 SDK 的自动重试机制重试（最多 `DEFAULT_MAX_RETRIES`=2 次）。

## 类型系统

### BaseModel

**类路径**：`anthropic._models.BaseModel`

SDK 所有数据模型的基类，基于 Pydantic 实现，提供序列化、反序列化、字典转换等功能。所有 API 请求/响应对象（如 `Message`、`MessageParam`、`ContentBlock` 等）均继承自此类。

### types/ 目录结构

`anthropic/types/` 目录包含 SDK 的所有类型定义，按功能组织：

| 子目录/文件 | 说明 |
|------------|------|
| `types/` | 稳定版 API 类型定义 |
| `types/beta/` | Beta API 类型定义（实验性功能） |

types 目录包含以下核心类型模块（不完全列表）：
- 消息相关类型：`Message`、`MessageParam`、`MessageStreamEvent` 等
- 内容块类型：`TextBlock`、`ToolUseBlock`、`ThinkingBlock` 等
- 工具相关类型：`ToolParam`、`ToolChoiceParam`、`FunctionToolParam` 等
- 错误相关类型：`ErrorType`、`APIErrorObject` 等
- 模型参数类型：`ModelParam`、`MetadataParam`、`ThinkingConfigParam` 等

### _compat.py 兼容性模块

`anthropic._compat.py` 模块提供跨 Python 版本的兼容性垫片，处理不同 Python 版本间的类型差异和运行时差异，确保 SDK 在多个 Python 版本上一致运行。

## 异常处理最佳实践

### 基础异常捕获模式

```python
from anthropic import (
    Anthropic,
    AnthropicError,
    APIStatusError,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    AuthenticationError,
)

client = Anthropic()

try:
    message = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello"}],
    )
except AuthenticationError:
    print("Authentication failed: check your API key")
except RateLimitError:
    print("Rate limited: please wait before retrying")
except APITimeoutError:
    print("Request timed out: consider increasing timeout")
except APIConnectionError:
    print("Network error: check your internet connection")
except APIStatusError as e:
    print(f"API error {e.status_code}: {e.message}")
    print(f"Request ID: {e.request_id}")
except AnthropicError as e:
    print(f"Unexpected SDK error: {e}")
```
