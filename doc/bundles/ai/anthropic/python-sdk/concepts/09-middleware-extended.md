---
type: concept
title: "中间件、扩展与错误处理"
description: "详解 Anthropic Python SDK 中间件机制、自定义中间件开发、响应装饰模式（原始响应/流式响应）、AnthropicError 异常体系层次、HTTP 状态码异常映射与错误处理最佳实践。"
tags: [middleware, extensions, errors, exceptions, raw-response, streaming-response, fallback, error-handling]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-005,F-006,F-007,F-012~F-015,F-074~F-084
    resource: /python-sdk/references/sdk-client.md
    title: "Anthropic Python SDK 客户端入口与基础设施参考"
  - id: F-085~F-090
    resource: /python-sdk/references/types-errors.md
    title: "Anthropic Python SDK 类型系统与异常体系参考"
---

# 中间件、扩展与错误处理

Anthropic Python SDK 不仅提供了开箱即用的 API 调用能力，还设计了完善的扩展机制，允许开发者在不修改 SDK 源码的情况下定制请求/响应处理流程。中间件（Middleware）提供了类 ASGI 的拦截管线模式，响应装饰器提供了原始 HTTP 响应和强制流式响应的访问能力，而结构化的异常体系则让错误处理变得可预测和可管理。这些扩展机制是构建生产级、可观测、高可靠 AI 应用的基础设施。

**本文适合谁**：需要构建生产级 AI 应用的工程师、希望添加日志/监控/重试等横切关注点的开发者、需要精细控制 HTTP 请求响应的高级用户。

## Middleware：请求/响应拦截管线

中间件是 SDK 提供的核心扩展机制，借鉴了 ASGI/WSGI、Express.js、Django 中间件等成熟框架的设计思想。通过中间件，你可以在请求发送前修改请求（添加头、记录日志、注入追踪 ID），在响应返回后处理响应（转换格式、收集指标、错误告警），甚至可以实现故障自动回退、请求重放等高级逻辑。

### Middleware 接口定义

中间件基类 `Middleware` 定义在 `anthropic._middleware` 模块，包含两个核心方法：

```python
from anthropic._middleware import Middleware
from anthropic._request import APIRequest
from anthropic._response import APIResponse, AsyncAPIResponse
from typing import Callable, Awaitable

class Middleware:
    def handle(
        self,
        request: APIRequest,
        call_next: Callable[[APIRequest], APIResponse[Any]],
    ) -> APIResponse[Any]:
        # 同步中间件方法
        # 1. 请求前处理：修改 request，记录日志等
        # 2. 调用 call_next(request) 传递给下一个中间件
        # 3. 响应后处理：修改 response，记录指标等
        return call_next(request)

    async def handle_async(
        self,
        request: APIRequest,
        call_next: Callable[[APIRequest], Awaitable[AsyncAPIResponse[Any]]],
    ) -> AsyncAPIResponse[Any]:
        # 异步中间件方法
        return await call_next(request)
```

关键类型别名：

| 类型别名 | 定义 | 说明 |
|---------|------|------|
| `CallNext` | `Callable[[APIRequest], APIResponse[Any]]` | 同步"调用下一个中间件"函数类型 |
| `AsyncCallNext` | `Callable[[APIRequest], Awaitable[AsyncAPIResponse[Any]]]` | 异步"调用下一个中间件"函数类型 |
| `MiddlewareInput` | `Union[Middleware, MiddlewareCallable, AsyncMiddlewareCallable]` | 中间件参数类型，可以是 Middleware 实例、同步可调用对象、异步可调用对象 |

### 中间件的注册与执行顺序

中间件通过客户端构造函数的 `middleware` 参数传入，可以注册多个中间件：

```python
from anthropic import Anthropic
from anthropic._middleware import Middleware

class LoggingMiddleware(Middleware):
    def handle(self, request, call_next):
        print(f"→ Request: {request.method} {request.url}")
        response = call_next(request)
        print(f"← Response: {response.status_code}")
        return response
    
    async def handle_async(self, request, call_next):
        print(f"→ Async Request: {request.method} {request.url}")
        response = await call_next(request)
        print(f"← Async Response: {response.status_code}")
        return response

class TracingMiddleware(Middleware):
    def handle(self, request, call_next):
        import uuid
        trace_id = str(uuid.uuid4())
        request.headers["X-Trace-ID"] = trace_id
        print(f"Trace ID: {trace_id}")
        return call_next(request)

# 注册多个中间件，按顺序执行（洋葱模型）
client = Anthropic(
    middleware=[
        TracingMiddleware(),  # 第一个：最外层
        LoggingMiddleware(),  # 第二个：内层
    ]
)
```

中间件执行遵循**洋葱模型**：
- 请求阶段：按列表顺序从外到内穿过中间件
- 响应阶段：按相反顺序从内到外返回
- 每个中间件必须调用 `call_next(request)` 才能将请求传递下去
- 可以选择不调用 `call_next`，直接返回响应（短路）

### 同步/异步严格分离

SDK 对中间件的同步/异步做了严格校验，在客户端初始化时通过 `validate_sync_middleware` 和 `validate_async_middleware` 函数检查：

- **同步客户端**只能使用实现了 `handle()` 方法的中间件，会拒绝异步中间件
- **异步客户端**只能使用实现了 `handle_async()` 方法的中间件，会拒绝同步中间件
- 如果你的中间件同时支持同步和异步，需要同时实现两个方法

这种严格分离是故意设计的——避免在同步代码中意外混入异步逻辑导致运行时错误，保证最佳的 IDE 类型提示体验。

### FallbackMiddleware：故障自动回退

SDK 内置了 `BetaRefusalFallbackMiddleware`（定义在 `lib/middleware/_fallbacks.py`），展示了中间件的强大能力——故障自动回退。

相关组件：
- `BetaRefusalFallbackMiddleware`：继承自 `Middleware`，实现请求失败时的自动回退逻辑
- `BetaFallbackState`：包含 `index: int | None` 属性，支持上下文管理器协议（`__enter__`/`__exit__`），跟踪当前回退状态
- `DEFAULT_BETAS = ("fallback-credit-2026-07-01",)`：默认启用的 Beta 回退标记

```python
from anthropic import Anthropic
from anthropic.lib.middleware._fallbacks import BetaRefusalFallbackMiddleware

client = Anthropic(
    middleware=[
        BetaRefusalFallbackMiddleware(),
    ]
)
```

回退中间件的典型场景：当主模型请求失败（如模型过载、拒绝回答）时，自动尝试备用模型或备用配置，提升应用的可用性。

### 自定义中间件开发

利用中间件机制，你可以实现各种横切关注点：

#### 示例 1：请求计时与指标收集

```python
import time
from anthropic._middleware import Middleware

class MetricsMiddleware(Middleware):
    def __init__(self):
        self.request_count = 0
        self.total_latency = 0.0
    
    def handle(self, request, call_next):
        start = time.perf_counter()
        try:
            response = call_next(request)
            latency = time.perf_counter() - start
            self.request_count += 1
            self.total_latency += latency
            print(f"Request completed in {latency:.3f}s")
            return response
        except Exception as e:
            latency = time.perf_counter() - start
            print(f"Request failed after {latency:.3f}s: {e}")
            raise
    
    async def handle_async(self, request, call_next):
        start = time.perf_counter()
        try:
            response = await call_next(request)
            latency = time.perf_counter() - start
            self.request_count += 1
            self.total_latency += latency
            print(f"Async request completed in {latency:.3f}s")
            return response
        except Exception as e:
            latency = time.perf_counter() - start
            print(f"Async request failed after {latency:.3f}s: {e}")
            raise
```

#### 示例 2：自动重试增强（虽然 SDK 已有内置重试，但可以定制）

```python
import time
from anthropic._middleware import Middleware
from anthropic import RateLimitError

class CustomRetryMiddleware(Middleware):
    def __init__(self, max_retries=3, base_delay=1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def handle(self, request, call_next):
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                return call_next(request)
            except RateLimitError as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)  # 指数退避
                    print(f"Rate limited, retrying in {delay}s (attempt {attempt + 1})")
                    time.sleep(delay)
                else:
                    raise
        raise last_exception
```

#### 示例 3：函数式中间件

除了继承 `Middleware` 基类，你还可以直接传入函数作为中间件：

```python
def simple_logging_middleware(request, call_next):
    print(f"Calling {request.url}")
    return call_next(request)

client = Anthropic(middleware=[simple_logging_middleware])
```

## 响应装饰模式：获取更多控制

SDK 采用**装饰器模式**（而非方法参数）来提供增强的响应格式。通过 `with_raw_response` 和 `with_streaming_response` 属性，你可以获得对 HTTP 响应更精细的控制。

### AnthropicWithRawResponse：获取原始 HTTP 响应

默认情况下，SDK 方法返回解析后的 Pydantic 模型对象（如 `Message`）。如果你需要访问原始 HTTP 响应头、状态码、原始响应体等信息，可以使用 `with_raw_response`：

```python
from anthropic import Anthropic

client = Anthropic()

# 使用 with_raw_response 获取原始 HTTP 响应
raw_response = client.with_raw_response.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)

# 访问原始 HTTP 响应信息
print(f"Status Code: {raw_response.status_code}")
print(f"Headers: {dict(raw_response.headers)}")
print(f"Request ID: {raw_response.headers.get('request-id')}")

# 获取解析后的模型对象
message = raw_response.parsed
print(f"Response: {message.content[0].text}")
```

`AnthropicWithRawResponse` 为所有资源提供了对应的 `WithRawResponse` 版本：
- `client.with_raw_response.messages` → `MessagesWithRawResponse`
- `client.with_raw_response.models` → `ModelsWithRawResponse`
- `client.with_raw_response.files` → `FilesWithRawResponse`
- `client.with_raw_response.skills` → `SkillsWithRawResponse`
- `client.with_raw_response.beta` → `BetaWithRawResponse`

原始响应用于：
- 获取 `request-id` 用于问题排查和技术支持
- 访问自定义响应头
- 需要检查 HTTP 状态码的场景
- 调试和日志记录

### AnthropicWithStreamingResponse：强制流式响应

类似地，`with_streaming_response` 可以将任何响应强制转为流式响应：

```python
from anthropic import Anthropic

client = Anthropic()

# 强制使用流式响应（即使没有显式设置 stream=True）
with client.with_streaming_response.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
) as stream:
    for event in stream:
        # 处理 SSE 事件
        if event.type == "content_block_delta":
            print(event.delta.text, end="", flush=True)
```

`AnthropicWithStreamingResponse` 同样为所有资源提供流式版本。这种模式的优势是统一流式/非流式的调用接口，在运行时动态决定是否使用流式。

### 装饰模式的设计优势

为什么使用属性装饰（`client.with_raw_response.messages.create()`）而非方法参数（`client.messages.create(..., raw_response=True)`）？

1. **类型安全**：不同响应类型返回不同的对象，IDE 可以正确推断类型
2. **链式复用**：可以保存装饰后的客户端实例重复使用
3. **组合可能性**：理论上可以组合多种装饰（虽然当前只有两种）
4. **API 整洁**：不污染每个方法的参数列表

```python
# 可以保存装饰后的客户端供多次使用
raw_client = client.with_raw_response
response1 = raw_client.messages.create(...)
response2 = raw_client.models.list(...)
```

## 异常体系详解

SDK 提供了层次清晰、分类明确的异常体系，所有异常类定义在 `anthropic._exceptions` 模块，可以从 `anthropic` 顶层包直接导入。

### AnthropicError 层次树

完整的异常继承结构如下：

```
Exception（Python 内置异常基类）
└── AnthropicError（所有 SDK 异常的基类）
    ├── APIError（API 调用过程中发生的错误）
    │   ├── APIStatusError（带有 HTTP 状态码的错误响应）
    │   │   ├── BadRequestError (400)
    │   │   ├── AuthenticationError (401)
    │   │   ├── PermissionDeniedError (403)
    │   │   ├── NotFoundError (404)
    │   │   ├── ConflictError (409)
    │   │   ├── RequestTooLargeError (413)
    │   │   ├── UnprocessableEntityError (422)
    │   │   ├── RateLimitError (429)
    │   │   ├── InternalServerError (5xx 通用)
    │   │   ├── ServiceUnavailableError (503)
    │   │   ├── DeadlineExceededError (504)
    │   │   └── OverloadedError (529)
    │   └── APIConnectionError（网络连接错误）
    │       └── APITimeoutError（请求超时）
    └── RetryableError（可重试错误标记接口）
```

### 核心异常类详解

#### AnthropicError（基类）

所有 SDK 异常的根类，继承自 Python 内置 `Exception`。用于统一捕获所有 SDK 相关异常：

```python
from anthropic import AnthropicError

try:
    client.messages.create(...)
except AnthropicError as e:
    print(f"SDK error occurred: {e}")
```

#### APIError

表示 API 调用过程中发生的错误，包含请求上下文：

| 属性 | 类型 | 说明 |
|------|------|------|
| `message` | `str` | 错误消息文本 |
| `request` | `httpx.Request` | 原始 HTTP 请求对象（可用于调试） |
| `body` | `object \| None` | 解析后的响应体（通常是 dict，包含错误详情） |

#### APIStatusError

最常用的错误类，表示服务器返回了非 2xx 的 HTTP 状态码：

| 属性 | 类型 | 说明 |
|------|------|------|
| `response` | `httpx.Response` | 原始 HTTP 响应对象 |
| `status_code` | `int` | HTTP 状态码（400、401、429、500 等） |
| `request_id` | `str \| None` | 请求 ID（排查问题时最重要，务必记录） |
| `type` | `ErrorType \| None` | 错误类型枚举 |
| `workspace_id` | `str \| None` | Workspace ID（如适用） |

#### APIConnectionError / APITimeoutError

`APIConnectionError` 表示无法连接到 API 服务器（网络断开、DNS 失败、代理问题等）。`APITimeoutError` 继承自它，表示请求超过了配置的超时时间。

#### RetryableError

一个特殊的**标记接口**（类体为空，只有 `pass`），用于标记哪些错误是可以安全重试的。SDK 的自动重试机制会检查异常是否继承自 `RetryableError`。

### HTTP 状态码 → 异常类映射表

SDK 根据 HTTP 响应状态码自动抛出对应的异常类型：

| 状态码 | 异常类 | 原因 | 建议处理方式 |
|--------|--------|------|-------------|
| **400** | `BadRequestError` | 请求参数错误（缺少必填参数、格式无效） | 检查请求参数，修正后重试 |
| **401** | `AuthenticationError` | 认证失败（无效 API Key、Token 过期） | 检查 API Key 是否正确、是否过期 |
| **403** | `PermissionDeniedError` | 权限不足 | 检查账户权限、是否被封禁、是否有 Beta 功能访问权限 |
| **404** | `NotFoundError` | 资源不存在 | 检查模型 ID、端点路径、资源 ID 是否正确 |
| **409** | `ConflictError` | 资源冲突 | 通常是并发修改冲突，重试或刷新状态 |
| **413** | `RequestTooLargeError` | 请求体过大 | 减少输入长度、减少图片数量/大小 |
| **422** | `UnprocessableEntityError` | 参数语义错误 | 检查参数值是否合法（如 temperature 范围） |
| **429** | `RateLimitError` | 请求频率超限 | 指数退避重试，降低请求速率 |
| **500** | `InternalServerError` | 服务器内部错误 | 可重试，如果持续出现联系支持 |
| **503** | `ServiceUnavailableError` | 服务暂时不可用 | 等待后重试，可能是维护窗口 |
| **504** | `DeadlineExceededError` | 网关超时 | 可重试，考虑增加超时配置 |
| **529** | `OverloadedError` | 服务过载 | 退避重试，Anthropic 服务高负载时出现 |
| **其他 5xx** | `InternalServerError` | 通用服务器错误 | 可重试 |

> **注意**：429（限流）和所有 5xx 错误默认会被 SDK 的自动重试机制重试（最多 2 次，指数退避）。

## 错误处理最佳实践

### 分层异常捕获

按照从具体到宽泛的顺序捕获异常，针对不同错误类型采取不同处理策略：

```python
from anthropic import (
    Anthropic,
    AnthropicError,
    APIStatusError,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    AuthenticationError,
    BadRequestError,
)
import logging

logger = logging.getLogger(__name__)
client = Anthropic()

def call_claude(user_message: str) -> str:
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=1024,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text
    
    except AuthenticationError:
        # 认证错误：通常是配置问题，快速失败
        logger.error("Authentication failed: check ANTHROPIC_API_KEY")
        raise  # 认证错误不重试，直接向上抛出
    
    except RateLimitError as e:
        # 限流：记录 request_id，等待后重试（SDK 已自动重试 2 次，如果还失败说明限流严重）
        logger.warning(f"Rate limited (request_id: {e.request_id})")
        # 可以在这里实现更复杂的退避策略或队列
        raise
    
    except APITimeoutError:
        # 超时：可以考虑重试，或增加超时时间
        logger.warning("Request timed out")
        raise
    
    except APIConnectionError:
        # 网络错误：检查网络连接、代理配置
        logger.error("Network connection error")
        raise
    
    except BadRequestError as e:
        # 请求错误：代码 bug，需要开发者修复
        logger.error(f"Bad request: {e.message} (request_id: {e.request_id})")
        raise ValueError(f"Invalid request: {e.message}") from e
    
    except APIStatusError as e:
        # 其他 HTTP 错误：记录 request_id 和详细信息
        logger.error(
            f"API error {e.status_code}: {e.message} "
            f"(request_id: {e.request_id})"
        )
        # 可以根据状态码决定是否重试
        if e.status_code >= 500:
            # 5xx 是服务端错误，可重试
            pass
        raise
    
    except AnthropicError as e:
        # 兜底：其他 SDK 错误
        logger.error(f"Unexpected SDK error: {e}")
        raise
```

### 始终记录 request_id

当联系 Anthropic 技术支持排查问题时，`request_id` 是最重要的信息。所有 `APIStatusError` 都包含这个属性，务必在错误日志中记录：

```python
except APIStatusError as e:
    logger.error(
        f"API Error",
        extra={
            "status_code": e.status_code,
            "request_id": e.request_id,
            "error_type": e.type,
            "message": e.message,
        }
    )
```

### 不要捕获过于宽泛的异常

避免这样写：

```python
# ❌ 不好：捕获所有异常，包括 KeyboardInterrupt、SystemExit 等
try:
    client.messages.create(...)
except Exception:
    print("Something went wrong")
```

应该捕获具体的异常类型，至少从 `AnthropicError` 开始。

## default_headers/default_query 自定义

除了中间件，客户端还提供了两个简单的扩展点用于自定义请求：

```python
client = Anthropic(
    # 为所有请求添加自定义请求头
    default_headers={
        "X-App-Name": "MyAIApp",
        "X-App-Version": "1.2.3",
        "X-Request-Source": "backend-service",
    },
    # 为所有请求添加默认查询参数
    default_query={
        "custom_param": "value",
    },
)
```

注意：`anthropic-version`、`X-Stainless-Async`、`x-api-key` 等是 SDK 自动管理的保留头，不要手动覆盖。

## _strict_response_validation：严格响应验证模式

客户端构造函数中有一个特殊参数 `_strict_response_validation`（以单下划线开头，表示内部/高级选项）：

```python
client = Anthropic(
    _strict_response_validation=True,  # 启用严格响应验证
)
```

启用后，SDK 会对 API 响应进行更严格的 Pydantic 验证，如果响应格式不符合预期会立即抛出错误。正常情况下不建议启用，因为 API 响应可能在 SDK 更新前发生变化；但在调试或需要确保数据格式完全符合预期的场景下可以使用。

## 扩展能力组合使用

这些扩展机制可以组合使用，构建强大的生产级客户端：

```python
from anthropic import Anthropic
from anthropic.lib.middleware._fallbacks import BetaRefusalFallbackMiddleware

# 生产级客户端配置
client = Anthropic(
    # 超时配置
    timeout=httpx.Timeout(timeout=300, connect=10),
    # 重试次数
    max_retries=3,
    # 中间件栈
    middleware=[
        MetricsMiddleware(),           # 指标收集
        TracingMiddleware(),           # 分布式追踪
        LoggingMiddleware(),           # 请求日志
        BetaRefusalFallbackMiddleware(),  # 故障回退
    ],
    # 默认请求头
    default_headers={
        "X-App-Version": APP_VERSION,
        "X-Environment": ENVIRONMENT,
    },
)
```

## 相关概念

- [客户端初始化与配置](/python-sdk/concepts/01-client-init.md) — 学习 timeout、max_retries 等基础配置
- [流式处理](/python-sdk/concepts/03-streaming.md) — with_streaming_response 与 Stream 类的关系
- [Beta: Agents、Memory与Skills](/python-sdk/concepts/08-beta-agents.md) — Beta API 调用同样需要错误处理
- [多云后端部署](/python-sdk/concepts/07-multi-cloud.md) — 多云客户端同样支持中间件和异常处理
- [Anthropic Python SDK 客户端入口与基础设施参考](/python-sdk/references/sdk-client.md) — 中间件基类、响应装饰类的完整 API 手册
- [Anthropic Python SDK 类型系统与异常体系参考](/python-sdk/references/types-errors.md) — 所有异常类和状态码映射的完整参考
