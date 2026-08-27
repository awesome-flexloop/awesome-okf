---
type: concept
title: "客户端初始化与配置"
description: "详解 Anthropic/AsyncAnthropic 构造函数参数、API Key 获取方式、超时与重试配置、自定义 HTTP 客户端、中间件配置以及异步客户端的初始化差异。"
tags: [client, init, config, api-key, timeout, retry, middleware, async]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-005,F-006,F-007,F-012~F-015,F-074~F-084
    resource: /python-sdk/references/sdk-client.md
    title: "Anthropic Python SDK 客户端入口与基础设施参考"
---

# 客户端初始化与配置

客户端初始化是使用 Anthropic Python SDK 的第一步。所有 API 调用都通过客户端实例发起，正确配置客户端不仅能保证功能正常运行，还能优化性能、提高可靠性、增强安全性。本文档将详细讲解同步/异步客户端的构造参数、认证方式、超时重试、自定义 HTTP 客户端、中间件等配置选项。

## 为什么客户端初始化是第一步

在 Anthropic Python SDK 中，`Anthropic`（同步）和 `AsyncAnthropic`（异步）客户端是所有操作的入口：
- 它持有 API Key、base URL、超时配置等全局设置
- 它管理 HTTP 连接池，复用 TCP 连接提升性能
- 它通过懒加载提供 `.messages`、`.models`、`.beta` 等资源访问入口
- 它内置自动重试、错误处理、中间件管线等基础设施

通常一个应用只需要创建一个客户端实例，在整个应用生命周期中复用。

## 最简初始化：使用环境变量

最简单也是最推荐的初始化方式是通过环境变量 `ANTHROPIC_API_KEY` 提供 API Key，客户端会自动读取：

```python
from anthropic import Anthropic

# 自动从 ANTHROPIC_API_KEY 环境变量读取 API Key
client = Anthropic()

# 发起第一个请求
message = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```

设置环境变量的方式：

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-api03-..."

# Windows CMD
set ANTHROPIC_API_KEY=sk-ant-api03-...

# Linux/macOS
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

使用环境变量的优势：
- API Key 不会硬编码在代码中，避免意外提交到版本控制
- 不同环境（开发/测试/生产）可以使用不同的 Key 而无需修改代码
- 符合 12-Factor App 配置最佳实践

## 显式传入 API Key

如果需要在代码中显式指定 API Key（例如从密钥管理服务动态获取），可以通过 `api_key` 参数传入：

```python
from anthropic import Anthropic

# 从环境变量、配置文件或密钥管理服务获取
import os
api_key = os.getenv("MY_APP_ANTHROPIC_KEY")

client = Anthropic(api_key=api_key)
```

> ⚠️ **安全提示**：永远不要将 API Key 硬编码在代码中，也不要将其提交到 Git 仓库。如果使用显式传入方式，请确保 Key 来自安全的配置源（环境变量、密钥管理服务如 AWS Secrets Manager、HashiCorp Vault 等）。

## 超时与重试配置

SDK 提供了合理的默认值，但你可以根据应用场景调整超时和重试策略。

### 默认配置常量

| 常量 | 默认值 | 说明 |
|------|--------|------|
| `DEFAULT_TIMEOUT` | `httpx.Timeout(timeout=600, connect=5.0)` | 总超时 10 分钟，连接超时 5 秒 |
| `DEFAULT_MAX_RETRIES` | `2` | 默认最大重试 2 次 |
| `INITIAL_RETRY_DELAY` | `0.5` 秒 | 初始重试延迟 |
| `MAX_RETRY_DELAY` | `8.0` 秒 | 最大重试延迟（指数退避） |
| `DEFAULT_CONNECTION_LIMITS` | `max_connections=1000, max_keepalive_connections=100` | 连接池配置 |

### 自定义超时

`timeout` 参数接受三种类型的值：

```python
from anthropic import Anthropic
import httpx

# 1. 传入浮点数：设置总超时（秒）
client = Anthropic(timeout=30.0)  # 30 秒总超时

# 2. 传入 httpx.Timeout 对象：细粒度控制
client = Anthropic(
    timeout=httpx.Timeout(
        timeout=300.0,    # 总超时 5 分钟
        connect=10.0,     # 连接超时 10 秒
        read=300.0,       # 读取超时
        write=10.0,       # 写入超时
        pool=10.0,        # 从连接池获取连接超时
    )
)

# 3. 传入 None：禁用超时（不推荐）
client = Anthropic(timeout=None)
```

对于长文本生成、工具调用等可能耗时较长的场景，可以适当增大超时时间。

### 自定义重试次数

通过 `max_retries` 参数调整自动重试次数：

```python
# 最多重试 5 次
client = Anthropic(max_retries=5)

# 禁用自动重试（不推荐，网络波动可能导致请求失败）
client = Anthropic(max_retries=0)
```

SDK 会自动重试可重试的错误（标记为 `RetryableError` 的异常，包括 429 限流、5xx 服务错误、网络连接错误等），使用指数退避策略（初始 0.5 秒，最大 8 秒）。

## 自定义请求头与查询参数

### default_headers：添加默认请求头

如果需要为所有请求添加自定义请求头（例如用于追踪、代理认证等）：

```python
client = Anthropic(
    default_headers={
        "X-App-Name": "MyAIApp",
        "X-Request-Source": "backend-service",
    }
)
```

注意：`anthropic-version` 和 `X-Stainless-Async` 是 SDK 自动设置的保留头，不要手动覆盖。

### default_query：添加默认查询参数

类似地，可以为所有请求添加默认查询参数：

```python
client = Anthropic(
    default_query={
        "custom_param": "value",
    }
)
```

## 自定义 HTTP 客户端

高级用户可以传入自定义的 `httpx.Client`（同步）或 `httpx.AsyncClient`（异步）实例，完全控制 HTTP 层行为：

```python
from anthropic import Anthropic
import httpx

# 自定义 httpx 客户端
http_client = httpx.Client(
    proxies="http://proxy.example.com:8080",  # 配置代理
    limits=httpx.Limits(
        max_connections=500,
        max_keepalive_connections=50,
    ),
    verify="/path/to/ca-bundle.crt",  # 自定义 CA 证书
)

client = Anthropic(http_client=http_client)

# 使用完毕后记得关闭自定义的 http_client
# client.close()  # 或者使用上下文管理器
```

> **注意**：如果传入自定义 `http_client`，你需要自行管理其生命周期（调用 `.close()` 或使用上下文管理器）。SDK 不会关闭你传入的外部客户端实例。

使用上下文管理器确保资源正确释放：

```python
with httpx.Client(proxies="...") as http_client:
    client = Anthropic(http_client=http_client)
    # 使用 client 发起请求
# http_client 自动关闭
```

## 配置中间件

中间件（Middleware）允许你在请求发送前和响应返回后插入自定义逻辑，例如日志记录、指标收集、请求转换等。

```python
from anthropic import Anthropic
from anthropic._middleware import Middleware

# 定义一个简单的日志中间件
class LoggingMiddleware(Middleware):
    def handle(self, request, call_next):
        print(f"Request: {request.method} {request.url}")
        response = call_next(request)
        print(f"Response: {response.status_code}")
        return response
    
    async def handle_async(self, request, call_next):
        print(f"Async Request: {request.method} {request.url}")
        response = await call_next(request)
        print(f"Async Response: {response.status_code}")
        return response

# 注册中间件
client = Anthropic(
    middleware=[
        LoggingMiddleware(),
        # 可以添加多个中间件，按顺序执行
    ]
)
```

中间件执行顺序类似洋葱模型：请求按中间件列表顺序穿过，响应按相反顺序返回。

> **重要**：中间件严格区分同步/异步。同步客户端只能使用实现了 `handle()` 方法的中间件，异步客户端只能使用实现了 `handle_async()` 方法的中间件。SDK 在初始化时会通过 `validate_sync_middleware`/`validate_async_middleware` 进行校验。

## Client 别名：历史兼容性

为了兼容历史版本，SDK 提供了类型别名：`Client` 等价于 `Anthropic`，`AsyncClient` 等价于 `AsyncAnthropic`：

```python
from anthropic import Client, AsyncClient

# 以下两种写法完全等价
client = Client()          # 等价于 Anthropic()
async_client = AsyncClient()  # 等价于 AsyncAnthropic()
```

新代码推荐使用 `Anthropic`/`AsyncAnthropic`，名称更清晰；`Client`/`AsyncClient` 仅用于兼容旧代码。

## 异步客户端初始化差异

`AsyncAnthropic` 的初始化参数与同步版本**几乎完全相同**，只有两个关键差异：

1. **`http_client` 类型**：异步客户端接受 `httpx.AsyncClient` 而非 `httpx.Client`
2. **`X-Stainless-Async` 头**：自动设置为 `async:{async_library}`（如 `async:asyncio`），用户无需手动处理

```python
import asyncio
from anthropic import AsyncAnthropic
import httpx

async def main():
    # 最简初始化（同样自动从环境变量读取 API Key）
    async_client = AsyncAnthropic()
    
    # 自定义异步 HTTP 客户端
    async_http_client = httpx.AsyncClient(
        proxies="http://proxy.example.com:8080",
    )
    async_client = AsyncAnthropic(http_client=async_http_client)
    
    # 使用异步客户端
    message = await async_client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello"}],
    )
    
    # 记得关闭客户端
    await async_client.close()

asyncio.run(main())
```

异步客户端同样支持上下文管理器：

```python
async def main():
    async with AsyncAnthropic() as client:
        message = await client.messages.create(...)
        # 退出 async with 时自动关闭
```

## 认证与安全最佳实践

1. **优先使用环境变量**：通过 `ANTHROPIC_API_KEY` 环境变量传递密钥，避免硬编码
2. **最小权限原则**：为不同的应用/环境使用不同的 API Key，定期轮换
3. **不要提交密钥到版本控制**：确保 `.env` 文件、配置文件等在 `.gitignore` 中
4. **使用安全的密钥管理**：生产环境使用 AWS Secrets Manager、HashiCorp Vault、GCP Secret Manager 等专业密钥管理服务
5. **自定义 CA 证书**：企业内网环境通过自定义 `http_client` 配置内部 CA 证书
6. **网络代理**：需要通过代理访问时，通过 `http_client` 的 `proxies` 参数配置

## 初始化完整示例

以下是一个生产环境推荐的初始化示例：

```python
from anthropic import Anthropic
import httpx
import os

def create_anthropic_client() -> Anthropic:
    """创建生产环境可用的 Anthropic 客户端"""
    return Anthropic(
        # API Key 从环境变量读取，不硬编码
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        # 合理的超时配置
        timeout=httpx.Timeout(
            timeout=300.0,  # 5 分钟总超时
            connect=10.0,   # 10 秒连接超时
        ),
        # 适当的重试次数
        max_retries=3,
        # 应用标识头
        default_headers={
            "X-App-Version": os.getenv("APP_VERSION", "unknown"),
        },
        # 可选：自定义连接池
        # http_client=httpx.Client(
        #     limits=httpx.Limits(max_connections=200),
        # ),
    )

# 使用
client = create_anthropic_client()
```

## 相关概念

- [整体架构概览](/python-sdk/concepts/00-overview.md) — 理解客户端在 SDK 四层架构中的位置
- [Messages API 基础](/python-sdk/concepts/02-messages-basics.md) — 客户端初始化后如何发起第一个对话
- [中间件、扩展与错误处理](/python-sdk/concepts/09-middleware-extended.md) — 深入学习中间件开发和错误处理最佳实践
- [多云后端支持](/python-sdk/concepts/07-multi-cloud.md) — Bedrock/Vertex 等多云客户端的初始化差异
- [Anthropic Python SDK 客户端入口与基础设施参考](/python-sdk/references/sdk-client.md) — 构造函数所有参数的完整 API 参考
