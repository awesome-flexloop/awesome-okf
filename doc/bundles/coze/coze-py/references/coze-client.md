---
type: reference
title: "Coze 客户端入口与基础设施参考"
description: "Coze/AsyncCoze 入口类、Requester 请求器、配置常量、版本信息、日志工具、异常体系与 HTTP 层的完整 API 参考。"
tags: [client, config, http, exception, logging, version]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cp-001
    resource: /references/coze-client.md
    title: "Coze 客户端入口与基础设施参考"
---

# Coze 客户端入口与基础设施参考

本文档登记 Coze Python SDK 的核心入口类与基础设施层，包括同步/异步客户端、请求器、配置常量、版本、日志、异常体系和 HTTP 传输层。

## 版本常量

| 常量 | 值 | 来源 |
|------|----|------|
| `VERSION` | `"0.20.0"` | version.py L6 |
| `COZE_COM_BASE_URL` | `"https://api.coze.com"` | config.py L4 |
| `COZE_CN_BASE_URL` | `"https://api.coze.cn"` | config.py L6 |
| `DEFAULT_TIMEOUT` | `httpx.Timeout(timeout=600.0, connect=5.0)` | config.py L9 |
| `DEFAULT_CONNECTION_LIMITS` | `httpx.Limits(max_connections=1000, max_keepalive_connections=100)` | config.py L10 |

## Coze（同步客户端）

**类路径**：`cozepy.Coze`

### 构造函数

```python
Coze(auth: Auth, base_url: str = COZE_COM_BASE_URL, http_client: httpx.Client | None = None)
```

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `auth` | `Auth` | 必填 | 认证实例，如 `TokenAuth`、`JWTAuth`、`OAuthApp` 等 |
| `base_url` | `str` | `COZE_COM_BASE_URL` | API 基础 URL，中国区使用 `COZE_CN_BASE_URL` |
| `http_client` | `httpx.Client \| None` | `None` | 自定义 httpx 客户端，为 None 时使用默认配置 |

### 服务属性（懒加载）

`Coze` 实例通过 20 个懒加载属性访问各业务服务客户端：

| 属性 | 类型 | 说明 |
|------|------|------|
| `.bots` | `BotsClient` | Bot 管理 |
| `.workspaces` | `WorkspacesClient` | 工作空间管理 |
| `.conversations` | `ConversationsClient` | 会话管理 |
| `.chat` | `ChatClient` | 对话（Chat） |
| `.connectors` | `ConnectorsClient` | 连接器 |
| `.files` | `FilesClient` | 文件上传 |
| `.workflows` | `WorkflowsClient` | 工作流 |
| `.knowledge` | `KnowledgeClient` | ⚠️ **已废弃**，使用 `.datasets` 替代 |
| `.datasets` | `DatasetsClient` | 数据集（知识库） |
| `.audio` | `AudioClient` | 音频（TTS/ASR/房间等） |
| `.templates` | `TemplatesClient` | 模板 |
| `.users` | `UsersClient` | 用户 |
| `.websockets` | `WebsocketsClient` | WebSocket 实时通信 |
| `.variables` | `VariablesClient` | 变量 |
| `.apps` | Apps 相关客户端 | 应用 |
| `.enterprises` | Enterprises 相关客户端 | 企业 |
| `.api_apps` | APIApps 相关客户端 | API 应用 |
| `.folders` | `FoldersClient` | 文件夹 |
| `.benefit_limitations` | BenefitLimitations 客户端 | 权益限制 |
| `.benefits` | Benefits 客户端 | 权益 |
| `.bill_tasks` | BillTasks 客户端 | 账单任务 |

> 所有服务客户端方法均接受 `headers: Optional[dict]` 参数（通过 `**kwargs` 传递自定义请求头）。

## AsyncCoze（异步客户端）

**类路径**：`cozepy.AsyncCoze`

### 构造函数

```python
AsyncCoze(auth: Auth, base_url: str = COZE_COM_BASE_URL, http_client: httpx.AsyncClient | None = None)
```

参数与 `Coze` 相同，但 `http_client` 类型为 `httpx.AsyncClient`。同样拥有上述 20 个懒加载服务属性，返回对应的 `Async*Client`。

## Requester（请求器）

**类路径**：内部 `Requester` 类（request.py）

### 构造函数

```python
Requester(auth: Auth, sync_client: SyncHTTPClient, async_client: AsyncHTTPClient)
```

### 方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `request` | `request(method: str, url: str, **kwargs) -> HTTPResponse` | 发送同步 HTTP 请求 |
| `arequest` | `arequest(method: str, url: str, **kwargs) -> HTTPResponse` | 发送异步 HTTP 请求 |

## HTTP 层

### SyncHTTPClient / AsyncHTTPClient

封装 httpx 的同步/异步 HTTP 客户端，处理认证注入、超时配置、连接池管理等。

### HTTPRequest

HTTP 请求模型，封装 method、url、headers、params、json body、files 等。

### HTTPResponse

HTTP 响应模型，封装 status_code、headers、content（bytes）、json() 解析方法。

### Stream / AsyncStream

**类路径**：`cozepy.Stream[T]` / `cozepy.AsyncStream[T]`

泛型流式响应包装器。

```python
Stream(raw_response: httpx.Response, data: Iterator[str], fields: List[str], handler: Callable)
```

- `raw_response`：原始 httpx 响应对象
- `data`：SSE 文本行迭代器
- `fields`：需要从 SSE 事件中提取的字段列表
- `handler`：事件处理回调，将原始 SSE 数据转换为具体事件类型

支持迭代协议：`for event in stream:` 逐个获取解析后的事件对象。

### IteratorHTTPResponse / AsyncIteratorHTTPResponse

HTTP 流式响应包装器，提供可迭代的响应体访问。

### FileHTTPResponse

文件下载响应包装器，用于文件下载场景。

## 异常体系

### CozeError

```python
class CozeError(Exception):
    """所有 Coze SDK 异常的基类。"""
```

### CozeAPIError

```python
class CozeAPIError(CozeError):
    code: int          # 错误码
    msg: str           # 错误消息
    logid: str         # 请求日志 ID（用于排查问题）
    debug_url: str     # 调试链接
```

API 调用返回错误状态码时抛出。

### CozePKCEAuthError

```python
class CozePKCEAuthError(CozeError):
    """PKCE OAuth 流程中的认证错误。"""
```

### CozePKCEAuthErrorType

PKCE 认证错误类型枚举：

| 值 | 说明 |
|----|------|
| `AUTHORIZATION_PENDING` | 授权待处理 |
| `SLOW_DOWN` | 请求过于频繁 |
| `ACCESS_DENIED` | 访问被拒绝 |
| `EXPIRED_TOKEN` | Token 已过期 |

### CozeInvalidEventError

```python
class CozeInvalidEventError(CozeError):
    """SSE/WebSocket 事件解析失败时抛出。"""
```

## 工具函数

### 配置相关

| 函数 | 签名 | 说明 |
|------|------|------|
| `remove_url_trailing_slash` | `(url: str) -> str` | 移除 URL 末尾斜杠 |
| `http_base_url_to_ws` | `(url: str) -> str` | 将 HTTP URL 转换为 WebSocket URL（http→ws, https→wss） |

### 编码与安全

| 函数 | 签名 | 说明 |
|------|------|------|
| `base64_encode_string` | `(s: str) -> str` | Base64 编码字符串 |
| `gen_s256_code_challenge` | `(code_verifier: str) -> str` | 生成 PKCE S256 code challenge |

### 数据处理

| 函数 | 签名 | 说明 |
|------|------|------|
| `remove_none_values` | `(d: dict) -> dict` | 移除字典中值为 None 的键 |
| `dump_exclude_none` | `(obj: CozeModel) -> dict` | 序列化模型时排除 None 值字段 |

### 日志

| 函数/常量 | 签名 | 说明 |
|-----------|------|------|
| `setup_logging` | `(level: int) -> None` | 配置 SDK 日志级别 |
| `log_fatal` | `(msg, *args) -> None` | 输出 FATAL 级别日志 |
| `log_error` | `(msg, *args) -> None` | 输出 ERROR 级别日志 |
| `log_warning` | `(msg, *args) -> None` | 输出 WARNING 级别日志 |
| `log_info` | `(msg, *args) -> None` | 输出 INFO 级别日志 |
| `log_debug` | `(msg, *args) -> None` | 输出 DEBUG 级别日志 |

### User-Agent

```python
user_agent() -> str
# 返回格式: "cozepy/{VERSION} python/{python_version} {os}/{os_version}"
```
