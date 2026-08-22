---
type: concept
title: "客户端初始化与配置"
description: "掌握 Coze/AsyncCoze 客户端的初始化方式、base_url 选择、http_client 自定义、超时配置、连接池和日志设置。"
tags: [client, init, config, timeout, base-url, http-client, logging]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cp-001
    resource: /references/coze-client.md
    title: "Coze 客户端入口与基础设施参考"
  - id: F-cp-002
    resource: /references/auth-model.md
    title: "认证体系参考"
---

# 客户端初始化与配置

`Coze`（同步）和 `AsyncCoze`（异步）是使用 SDK 的入口。正确初始化客户端是所有后续操作的基础。本文档介绍如何选择 base URL、配置超时和连接池、自定义 HTTP 客户端，以及设置日志。

## 最简初始化

最简单的初始化只需要提供认证实例：

```python
from cozepy import Coze, TokenAuth

coze = Coze(auth=TokenAuth(token="your_pat_token"))
```

这会使用默认配置：连接国际区 `https://api.coze.com`，600 秒总超时，5 秒连接超时，最大 1000 连接/100 保活连接。

异步版本完全对应：

```python
from cozepy import AsyncCoze, AsyncTokenAuth

coze = AsyncCoze(auth=AsyncTokenAuth(token="your_pat_token"))
```

## base_url 选择

SDK 提供两个预定义的基础 URL 常量：

| 常量 | 值 | 适用区域 |
|------|----|---------|
| `COZE_COM_BASE_URL` | `https://api.coze.com` | 国际版（默认） |
| `COZE_CN_BASE_URL` | `https://api.coze.cn` | 中国版 |

中国用户必须使用 `COZE_CN_BASE_URL`，否则会遇到连接问题：

```python
from cozepy import Coze, TokenAuth, COZE_CN_BASE_URL

coze = Coze(
    auth=TokenAuth(token="pat_xxxxxxxxxxxx"),
    base_url=COZE_CN_BASE_URL,
)
```

## 默认超时与连接池

SDK 的默认配置适用于大多数场景：

```python
# config.py 中的默认值
DEFAULT_TIMEOUT = httpx.Timeout(timeout=600.0, connect=5.0)
DEFAULT_CONNECTION_LIMITS = httpx.Limits(
    max_connections=1000,
    max_keepalive_connections=100,
)
```

- **总超时 600 秒**：Coze 的对话和工作流可能涉及多轮 LLM 调用，响应时间较长，600 秒是合理的上限
- **连接超时 5 秒**：TCP 连接建立的超时时间
- **最大连接数 1000**：高并发场景的连接池上限
- **保活连接 100**：保持长连接复用的数量

## 自定义 http_client

当你需要更精细地控制 HTTP 行为时（如配置代理、自定义超时、添加中间件、使用特殊 SSL 证书），可以传入自定义的 httpx 客户端实例：

```python
import httpx
from cozepy import Coze, TokenAuth, COZE_CN_BASE_URL

# 自定义超时和代理
custom_client = httpx.Client(
    timeout=httpx.Timeout(timeout=300.0, connect=10.0),
    proxy="http://proxy.example.com:8080",
    limits=httpx.Limits(max_connections=500, max_keepalive_connections=50),
)

coze = Coze(
    auth=TokenAuth(token="your_token"),
    base_url=COZE_CN_BASE_URL,
    http_client=custom_client,
)
```

异步版本同理，传入 `httpx.AsyncClient`：

```python
import httpx
from cozepy import AsyncCoze, AsyncTokenAuth, COZE_CN_BASE_URL

custom_async_client = httpx.AsyncClient(
    timeout=httpx.Timeout(timeout=300.0, connect=10.0),
    proxy="http://proxy.example.com:8080",
)

coze = AsyncCoze(
    auth=AsyncTokenAuth(token="your_token"),
    base_url=COZE_CN_BASE_URL,
    http_client=custom_async_client,
)
```

> **注意**：当传入自定义 `http_client` 时，SDK 不会在客户端关闭时自动关闭它，你需要自行管理自定义客户端的生命周期（在适当时机调用 `.close()`）。

## 自定义请求头

所有服务客户端方法都支持通过 `**kwargs` 传递 `headers` 参数，用于添加自定义请求头：

```python
# 在具体 API 调用中添加自定义 header
for event in coze.chat.stream(
    bot_id="bot_id",
    user_id="user_id",
    additional_messages=[Message.build_user_question_text("你好")],
    headers={"X-Custom-Header": "value"},
):
    ...
```

## 日志配置

SDK 使用 Python 标准 `logging` 模块。提供了便捷的日志设置函数和快捷方法：

```python
from cozepy import setup_logging, log_debug, log_info, log_warning, log_error, log_fatal
import logging

# 设置 SDK 日志级别为 DEBUG（排查问题时使用）
setup_logging(logging.DEBUG)

# 设置为 WARNING（生产环境，只输出警告和错误）
setup_logging(logging.WARNING)

# 使用 SDK 的日志快捷方法
log_info("这是一条信息日志")
log_error("这是一条错误日志")
log_debug("调试信息: %s", some_variable)
```

日志级别说明：

| 级别 | 用途 |
|------|------|
| `DEBUG` | 详细的请求/响应信息，用于排查问题 |
| `INFO` | 关键操作信息 |
| `WARNING` | 废弃警告、重试提示等 |
| `ERROR` | API 调用失败等错误 |
| `FATAL` | 不可恢复的严重错误 |

## User-Agent

SDK 自动在每个请求中设置 User-Agent 头，格式为：

```
cozepy/0.20.0 python/3.x.x {os}/{os_version}
```

通过 `user_agent()` 函数可以获取这个字符串。服务端通过 User-Agent 识别 SDK 版本和运行环境，有助于问题排查。

## URL 工具函数

SDK 提供两个 URL 处理工具函数：

```python
from cozepy.util import remove_url_trailing_slash, http_base_url_to_ws

# 移除 URL 末尾斜杠
url = remove_url_trailing_slash("https://api.coze.cn/")
# → "https://api.coze.cn"

# 将 HTTP URL 转换为 WebSocket URL
ws_url = http_base_url_to_ws("https://api.coze.cn")
# → "wss://api.coze.cn"
```

`http_base_url_to_ws` 在 WebSocket 连接时自动使用，你通常不需要手动调用它。

## 初始化最佳实践

1. **根据区域选择 base_url**：中国用户始终使用 `COZE_CN_BASE_URL`
2. **生产环境调小日志级别**：使用 `setup_logging(logging.WARNING)` 避免日志过多
3. **需要代理时自定义 http_client**：在企业内网环境下，通过自定义 httpx.Client 配置代理
4. **异步客户端在 FastAPI 等框架中使用**：避免在异步框架中使用同步客户端导致事件循环阻塞
5. **Token 安全**：不要将 token 硬编码在代码中，使用环境变量或配置文件管理

```python
# 生产环境推荐写法
import os
from cozepy import Coze, TokenAuth, COZE_CN_BASE_URL

coze = Coze(
    auth=TokenAuth(token=os.environ["COZE_API_TOKEN"]),
    base_url=COZE_CN_BASE_URL,
)
```

## 相关概念

- [整体架构概览](/concepts/00-overview-architecture.md) — 理解双轨设计和懒加载模式
- [认证体系](/concepts/01-auth-system.md) — 认证方式的选择和配置
- [对话与流式](/concepts/03-chat-streaming.md) — 初始化后如何发起对话
- [基础对话示例](/examples/basic-chat.md) — 完整的初始化+对话示例
- [Coze 客户端入口与基础设施参考](/references/coze-client.md) — 配置常量和工具函数的完整 API
