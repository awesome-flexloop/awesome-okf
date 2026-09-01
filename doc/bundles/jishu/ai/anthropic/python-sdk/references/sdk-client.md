---
type: reference
title: "Anthropic Python SDK 客户端入口与基础设施参考"
description: "Anthropic/AsyncAnthropic 同步/异步客户端、配置常量、别名机制、响应装饰模式与中间件基础设施的完整 API 参考。"
tags: [client, config, middleware, sync, async, retry, timeout]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-001~F-015,F-074~F-084
    resource: /python-sdk/references/sdk-client.md
    title: "Anthropic Python SDK 客户端入口与基础设施参考"
---

# Anthropic Python SDK 客户端入口与基础设施参考

本文档登记 Anthropic Python SDK 的核心入口类与基础设施层，包括同步/异步客户端、配置常量、客户端别名、原始/流式响应装饰模式、资源基类与中间件机制。

## 版本与配置常量

所有常量定义在 `anthropic._constants` 模块中：

| 常量 | 值 | 说明 |
|------|----|------|
| `DEFAULT_TIMEOUT` | `httpx.Timeout(timeout=600, connect=5.0)` | 默认请求超时：总超时 10 分钟，连接超时 5 秒 |
| `DEFAULT_MAX_RETRIES` | `2` | 默认最大重试次数 |
| `DEFAULT_CONNECTION_LIMITS` | `httpx.Limits(max_connections=1000, max_keepalive_connections=100)` | 默认连接池配置：最大连接数 1000，keep-alive 连接数 100 |
| `INITIAL_RETRY_DELAY` | `0.5` | 初始重试延迟（秒） |
| `MAX_RETRY_DELAY` | `8.0` | 最大重试延迟（秒） |

## Anthropic（同步客户端）

**类路径**：`anthropic.Anthropic`

`Anthropic` 类继承自 `SyncAPIClient`，是 SDK 的同步入口点，定义在 `anthropic._client` 模块。

### 构造函数

```python
Anthropic(
    api_key: str | None = None,
    auth_token: str | None = None,
    credentials: Credentials | None = None,
    config: Config | None = None,
    profile: str | None = None,
    webhook_key: str | None = None,
    base_url: str | None = None,
    timeout: httpx.Timeout | float | None = DEFAULT_TIMEOUT,
    max_retries: int = DEFAULT_MAX_RETRIES,
    default_headers: Mapping[str, str] | None = None,
    default_query: Mapping[str, object] | None = None,
    http_client: httpx.Client | None = None,
    middleware: Sequence[MiddlewareInput] | None = None,
    _strict_response_validation: bool = False,
    _token_cache: TokenCache | None = None,
)
```

**核心参数**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `api_key` | `str \| None` | `None` | Anthropic API 密钥，未提供时从环境变量读取 |
| `auth_token` | `str \| None` | `None` | 认证 Token |
| `base_url` | `str \| None` | `None` | 自定义 API 基础 URL |
| `timeout` | `httpx.Timeout \| float \| None` | `DEFAULT_TIMEOUT` | 请求超时配置 |
| `max_retries` | `int` | `2` | 最大重试次数 |
| `default_headers` | `Mapping[str, str] \| None` | `None` | 默认请求头 |
| `http_client` | `httpx.Client \| None` | `None` | 自定义 httpx 同步客户端 |
| `middleware` | `Sequence[MiddlewareInput] \| None` | `None` | 中间件序列 |

### 默认请求头

`Anthropic.default_headers` 属性返回包含以下固定头的字典：

```python
{
    "anthropic-version": "2023-06-01",
    "X-Stainless-Async": "false",
}
```

### 服务属性（懒加载）

`Anthropic` 实例通过 `@cached_property` 定义以下懒加载资源属性，首次访问时实例化并缓存：

| 属性 | 类型 | 说明 |
|------|------|------|
| `.messages` | `Messages` | 消息 API（Messages）资源 |
| `.models` | `Models` | 模型管理资源 |
| `.files` | `Files` | 文件上传资源 |
| `.skills` | `Skills` | 技能（Skills）资源 |
| `.beta` | `Beta` | Beta API 命名空间（实验性功能） |

> **注意**：所有资源属性均为懒加载，客户端初始化时不创建任何资源实例，首次访问时才动态生成并缓存。

## AsyncAnthropic（异步客户端）

**类路径**：`anthropic.AsyncAnthropic`

`AsyncAnthropic` 类继承自 `AsyncAPIClient`，是 SDK 的异步入口点，与同步客户端 `Anthropic` 完全对称。

### 构造函数

```python
AsyncAnthropic(
    api_key: str | None = None,
    auth_token: str | None = None,
    credentials: Credentials | None = None,
    config: Config | None = None,
    profile: str | None = None,
    webhook_key: str | None = None,
    base_url: str | None = None,
    timeout: httpx.Timeout | float | None = DEFAULT_TIMEOUT,
    max_retries: int = DEFAULT_MAX_RETRIES,
    default_headers: Mapping[str, str] | None = None,
    default_query: Mapping[str, object] | None = None,
    http_client: httpx.AsyncClient | None = None,
    middleware: Sequence[MiddlewareInput] | None = None,
    _strict_response_validation: bool = False,
    _token_cache: TokenCache | None = None,
)
```

参数与 `Anthropic` 相同，但 `http_client` 类型为 `httpx.AsyncClient`。

### 默认请求头

`AsyncAnthropic.default_headers` 属性返回包含以下头的字典：

```python
{
    "anthropic-version": "2023-06-01",
    "X-Stainless-Async": f"async:{get_async_library()}",
}
```

`X-Stainless-Async` 头会自动检测当前使用的异步库（如 `asyncio`）。

### 服务属性（懒加载）

与 `Anthropic` 完全对称，拥有 `.messages`、`.models`、`.files`、`.skills`、`.beta` 等懒加载属性，返回对应的异步资源类实例。

## 客户端别名

为兼容历史用法，SDK 提供了以下类型别名：

| 别名 | 实际类型 | 说明 |
|------|---------|------|
| `Client` | `Anthropic` | 同步客户端别名 |
| `AsyncClient` | `AsyncAnthropic` | 异步客户端别名 |

别名定义在 `anthropic._client` 模块末尾，与原类完全等价。

## 响应装饰模式

SDK 采用装饰器模式而非方法参数来控制响应格式，提供两种增强响应包装类。

### AnthropicWithRawResponse

**类路径**：`anthropic.AnthropicWithRawResponse`

原始响应包装类，将所有资源方法的返回值包装为包含原始 HTTP 响应的对象。

| 属性 | 返回类型 | 说明 |
|------|---------|------|
| `.messages` | `MessagesWithRawResponse` | 返回原始 HTTP 响应的 Messages 资源 |
| `.models` | `ModelsWithRawResponse` | 返回原始 HTTP 响应的 Models 资源 |
| `.files` | `FilesWithRawResponse` | 返回原始 HTTP 响应的 Files 资源 |
| `.skills` | `SkillsWithRawResponse` | 返回原始 HTTP 响应的 Skills 资源 |
| `.beta` | `BetaWithRawResponse` | 返回原始 HTTP 响应的 Beta 资源 |

**使用示例**：

```python
client = Anthropic()
raw_response = client.with_raw_response.messages.create(...)
# raw_response 包含 .headers, .status_code, .parsed 等属性
```

### AnthropicWithStreamingResponse

**类路径**：`anthropic.AnthropicWithStreamedResponse`

流式响应包装类，将所有资源方法的返回值包装为流式响应对象。

| 属性 | 返回类型 | 说明 |
|------|---------|------|
| `.messages` | `MessagesWithStreamingResponse` | 返回流式响应的 Messages 资源 |
| `.models` | `ModelsWithStreamingResponse` | 返回流式响应的 Models 资源 |
| `.files` | `FilesWithStreamingResponse` | 返回流式响应的 Files 资源 |
| `.skills` | `SkillsWithStreamingResponse` | 返回流式响应的 Skills 资源 |
| `.beta` | `BetaWithStreamingResponse` | 返回流式响应的 Beta 资源 |

## 资源基类

### SyncAPIResource

**类路径**：`anthropic._resource.SyncAPIResource`

所有同步资源类的基类，在 `__init__` 中绑定以下 HTTP 方法到客户端：

| 绑定方法 | 对应客户端方法 |
|---------|--------------|
| `_get` | `client.get` |
| `_post` | `client.post` |
| `_patch` | `client.patch` |
| `_put` | `client.put` |
| `_delete` | `client.delete` |
| `_get_api_list` | `client.get_api_list` |

包含 `_client: SyncAPIClient` 属性，持有对同步客户端的引用。

### AsyncAPIResource

**类路径**：`anthropic._resource.AsyncAPIResource`

所有异步资源类的基类，包含 `_client: AsyncAPIClient` 属性。提供 `_sleep` 方法使用 `anyio.sleep` 进行异步等待。

## 中间件机制

### Middleware 基类

**类路径**：`anthropic._middleware.Middleware`

中间件基类，定义在 `_middleware.py` 模块，支持请求/响应拦截与处理。

```python
class Middleware:
    def handle(
        self,
        request: APIRequest,
        call_next: CallNext,
    ) -> APIResponse[Any]:
        ...

    async def handle_async(
        self,
        request: APIRequest,
        call_next: AsyncCallNext,
    ) -> AsyncAPIResponse[Any]:
        ...
```

### 类型别名

| 类型别名 | 定义 | 说明 |
|---------|------|------|
| `CallNext` | `Callable[[APIRequest], "APIResponse[Any]"]` | 同步下一个中间件调用类型 |
| `AsyncCallNext` | `Callable[[APIRequest], Awaitable["AsyncAPIResponse[Any]"]]` | 异步下一个中间件调用类型 |
| `MiddlewareInput` | `Union[Middleware, MiddlewareCallable, AsyncMiddlewareCallable]` | 中间件输入类型，可以是 Middleware 实例或可调用对象 |

### 中间件验证函数

| 函数 | 签名 | 说明 |
|------|------|------|
| `validate_sync_middleware` | `(middleware: MiddlewareInput) -> None` | 验证同步中间件，拒绝异步中间件和未实现 `handle()` 的 Middleware 子类 |
| `validate_async_middleware` | `(middleware: MiddlewareInput) -> None` | 验证异步中间件，拒绝同步中间件和未实现 `handle_async()` 的 Middleware 子类 |

> **重要**：中间件严格区分同步/异步，不允许混用。

### 内置中间件

**BetaRefusalFallbackMiddleware**（`anthropic.lib.middleware._fallbacks.BetaRefusalFallbackMiddleware`）：

- 继承自 `Middleware`
- 关联类 `BetaFallbackState` 包含 `index: int | None` 属性，支持上下文管理器协议
- 默认 Beta 标记 `DEFAULT_BETAS = ("fallback-credit-2026-07-01",)`
