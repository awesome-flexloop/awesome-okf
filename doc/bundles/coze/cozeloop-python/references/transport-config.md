---
type: reference
title: "传输层与配置参考"
description: "CozeLoop Python SDK 传输层与配置参考：HTTP 客户端、认证方式、环境变量、批量上报参数、采样配置、超大数据上报。"
tags: [transport, http, auth, configuration, batching, environment, sampling]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T03:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T03:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cl-025
    title: "认证体系"
  - id: F-cl-072
    title: "HTTP 客户端层"
  - id: F-cl-053
    title: "TraceProvider 与批量上报"
  - id: F-cl-101
    title: "配置与环境变量"
---

# 传输层与配置参考

本文档描述 CozeLoop Python SDK 的传输层实现、认证配置、环境变量、批量上报参数和高级配置选项。

## HTTP 客户端层

### 底层实现

SDK 使用 `httpx` 库作为 HTTP 客户端（同步模式）。HTTP 层封装在 `cozeloop.internal.httpclient` 模块中。

### 默认端点

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| API Base URL | `https://api.coze.cn` (`CN_BASE_URL`) | CozeLoop 中国区 API 地址 |
| Span 上报路径 | `/v1/loop/traces/ingest` | Span 数据批量上报端点 |
| 文件上传路径 | `/v1/loop/files/upload` | 大文本/多模态文件上传端点 |

### 请求头

每个请求自动携带以下 HTTP 头：

| 头名称 | 值来源 | 说明 |
|--------|--------|------|
| `Authorization` | `Bearer <token>` | 认证令牌，由 Auth 实现提供 |
| `User-Agent` | `user_agent_header()` | SDK 标识，含版本信息 |
| `Content-Type` | `application/json`（POST 请求） | 请求内容类型 |
| `x-tt-logid` | 自动生成 | 请求日志 ID |
| `x-tt-env` | 环境变量 `x_tt_env` | 可选，内部环境路由 |
| `x-use-ppe` | 环境变量 `x_use_ppe` | 可选，PPE 环境标识 |
| `X-Cozeloop-Traceparent` | span.to_header() | 自动注入当前 span 上下文（header_injector） |
| `X-Cozeloop-Tracestate` | span.to_header() | 自动注入当前 span baggage（header_injector） |

### 超时配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `timeout` | 3 秒 | 普通 API 请求（span 上报等）的读取超时 |
| `upload_timeout` | 30 秒 | 文件上传请求的超时 |
| execute_prompt timeout | 600 秒（10分钟） | PTaaS 执行超时，独立参数 |

### 自定义 HTTP 客户端

可以传入自定义的 `httpx.Client` 实例：

```python
import httpx
import cozeloop

custom_http = httpx.Client(
    timeout=httpx.Timeout(10.0, connect=5.0),
    proxies="http://proxy.example.com:8080",
)
client = cozeloop.new_client(http_client=custom_http)
```

### HTTP 方法

内部 `httpclient.Client` 提供以下方法（一般不直接使用）：

| 方法 | 说明 |
|------|------|
| `get(path, response_model, params)` | GET 请求 |
| `post(path, response_model, json)` | POST JSON 请求 |
| `upload_file(path, response_model, file, file_name, form)` | multipart 文件上传 |
| `post_stream(path, json, timeout)` | 流式 POST 请求（SSE） |
| `arequest(...)` | 异步请求 |
| `apost_stream(...)` | 异步流式请求 |

### 响应解析

所有响应解析为 `BaseResponse` 模型（含 `code` 和 `msg` 字段）。`code != 0` 时抛出 `RemoteServiceError`，包含 http_code、error_code、error_message 和 log_id。

### 网络错误

httpx 抛出的 `HTTPError` 被捕获并包装为 `NetworkError`（LoopError 子类）。

## 认证方式

### PAT Token 认证（TokenAuth）

使用个人访问令牌（Personal Access Token）认证，最简单的方式：

```python
import cozeloop

# 方式 1：通过参数传入
client = cozeloop.new_client(
    api_token="your_pat_token",
    workspace_id="your_workspace_id",
)

# 方式 2：通过环境变量
# export COZELOOP_API_TOKEN=your_pat_token
# export COZELOOP_WORKSPACE_ID=your_workspace_id
client = cozeloop.new_client()
```

Token 获取地址：https://www.coze.cn/open/oauth/pat

### JWT OAuth 认证（JWTAuth）

使用 OAuth JWT 流程，适合服务端应用，自动管理 token 刷新：

```python
client = cozeloop.new_client(
    jwt_oauth_client_id="your_client_id",
    jwt_oauth_private_key="your_private_key",
    jwt_oauth_public_key_id="your_public_key_id",
    workspace_id="your_workspace_id",
)
```

或通过环境变量：
```bash
export COZELOOP_JWT_OAUTH_CLIENT_ID=your_client_id
export COZELOOP_JWT_OAUTH_PRIVATE_KEY=your_private_key
export COZELOOP_JWT_OAUTH_PUBLIC_KEY_ID=your_public_key_id
export COZELOOP_WORKSPACE_ID=your_workspace_id
```

**JWT Token 管理**：
- Token 默认 TTL 为 900 秒（15分钟）
- 提前 60 秒自动刷新
- 通过 `JWTOAuthApp`（authlib 库）与 Coze OAuth 端点交互获取 access_token
- Token 为懒刷新模式：每次请求时检查是否需要刷新

应用创建地址：https://www.coze.cn/open/oauth/apps

### 认证优先级

创建客户端时，认证方式按以下优先级选择：
1. 如果提供了 JWT OAuth 三个参数（client_id + private_key + public_key_id）→ 使用 JWTAuth
2. 否则如果提供了 api_token → 使用 TokenAuth
3. 都没有 → 抛出 `AuthInfoRequiredError`

## 环境变量

所有环境变量均以 `COZELOOP_` 为前缀：

| 环境变量 | 对应参数 | 说明 |
|----------|---------|------|
| `COZELOOP_API_BASE_URL` | `api_base_url` | API 基础 URL，默认 https://api.coze.cn |
| `COZELOOP_WORKSPACE_ID` | `workspace_id` | **必填**，工作空间 ID |
| `COZELOOP_API_TOKEN` | `api_token` | PAT Token |
| `COZELOOP_JWT_OAUTH_CLIENT_ID` | `jwt_oauth_client_id` | JWT OAuth Client ID |
| `COZELOOP_JWT_OAUTH_PRIVATE_KEY` | `jwt_oauth_private_key` | JWT OAuth 私钥 |
| `COZELOOP_JWT_OAUTH_PUBLIC_KEY_ID` | `jwt_oauth_public_key_id` | JWT OAuth 公钥 ID |
| `COZELOOP_SCENE` | runtime.scene | 覆盖运行时场景标签 |
| `x_tt_env` | — | 内部环境路由头 |
| `x_use_ppe` | — | PPE 环境标识头 |

环境变量的优先级**低于**显式传入的参数。如果参数和环境变量都设置了，使用参数值。

## 批量上报配置

### 队列架构

`BatchSpanProcessor` 维护四个独立队列，每个队列由一个 daemon 后台线程消费：

| 队列 | 名称 | 默认最大长度 | 批量大小 | 调度间隔 | 单批大小限制 |
|------|------|-------------|---------|---------|------------|
| Span 主队列 | span | 1024 | 100 | 1000ms | 4MB |
| Span 重试队列 | span_retry | 512 | 50 | 1000ms | 4MB |
| File 主队列 | file | 512 | 1 | 5000ms | 100MB |
| File 重试队列 | file_retry | 512 | 1 | 5000ms | 100MB |

### 上报流程

1. Span finish 后进入 span 主队列
2. 后台线程等待调度间隔（1秒）或攒满批量大小（100条/4MB），触发批量上报
3. 上报成功 → 如果 span 包含多模态/大文件数据，文件进入 file 队列
4. 上报失败 → span 进入重试队列
5. 重试队列上报失败 → 丢弃 span
6. File 队列同理：失败进入 file_retry，二次失败丢弃

### 自定义队列配置

使用 `QueueConf` 自定义 span 队列参数：

```python
from cozeloop.internal.trace.model.model import QueueConf
import cozeloop

qconf = QueueConf(
    span_queue_length=2048,              # span 队列最大长度，默认 1024
    span_max_export_batch_length=200,    # 单批最大 span 数，默认 100
)
client = cozeloop.new_client(trace_queue_conf=qconf)
```

### 强制刷新

```python
# 模块级
cozeloop.flush()

# 客户端级
client.flush()
```

`flush()` 会阻塞等待所有队列排空并完成上报。通常在程序退出前调用。

### 关闭客户端

```python
# 模块级（关闭默认客户端）
cozeloop.close()

# 客户端级
client.close()
```

`close()` 执行以下操作：
1. 设置停止事件
2. 唤醒所有队列工作线程
3. 排空队列中的剩余 span
4. 等待工作线程结束
5. 将全局客户端替换为 NoopClient

程序退出时 atexit 钩子自动调用 close。

## 超大数据上报（ultra_large_report）

### 机制

当 span 的 input/output 数据超过 1MB（`MAX_BYTES_OF_ONE_TAG_VALUE_OF_INPUT_OUTPUT`）时：

- **ultra_large_report=False**（默认）：数据被截断到 1000 字符，截断的 key 记录在 `cut_off` 系统标签中。
- **ultra_large_report=True**：截断文本部分（1000字符）保留在 span 中，完整数据通过文件上传接口（/v1/loop/files/upload）单独上传，span 中存储对象存储 key（ObjectStorage）。

```python
client = cozeloop.new_client(ultra_large_report=True)
```

### 多模态数据

当 input/output 使用 `ModelInput`/`ModelOutput` 格式并包含 base64 编码的图片（ModelImageURL）或文件（ModelFileURL）时：
- 图片/文件的 base64 数据自动提取为独立附件上传
- span 中图片/文件 URL 替换为对象存储 key
- 附件信息记录在 ObjectStorage.attachments 中
- 支持的类型：image_url（图片）、file_url（文件）
- URL 形式的图片/文件（http:// 或 https:// 开头）不上传，保留原始 URL

### Tag 值截断配置

使用 `TagTruncateConf` 自定义标签截断阈值：

```python
from cozeloop.internal.trace.model.model import TagTruncateConf

tconf = TagTruncateConf(
    normal_field_max_byte=4096,               # 普通标签值最大字节数，默认 1024
    input_output_field_max_byte=2*1024*1024,  # input/output 最大字节数，默认 1MB
)
client = cozeloop.new_client(tag_truncate_conf=tconf)
```

### 截断限制常量

| 常量 | 默认值 | 说明 |
|------|--------|------|
| MAX_TAG_KV_COUNT_IN_ONE_SPAN | 50 | 单个 span 最大标签数 |
| MAX_BYTES_OF_ONE_TAG_VALUE_DEFAULT | 1024 | 普通标签值最大字节数 |
| MAX_BYTES_OF_ONE_TAG_KEY_DEFAULT | 1024 | 标签 key 最大字节数 |
| MAX_BYTES_OF_ONE_TAG_VALUE_OF_INPUT_OUTPUT | 1MB | input/output 最大字节数 |
| TEXT_TRUNCATE_CHAR_LENGTH | 1000 | 超大数据截断保留字符数 |

## 采样

### 默认行为

所有 span 默认被采样上报（flags=1）。当前版本 SDK **未实现**基于概率的采样器（Sampler），所有 span 在 finish 后都会进入上报队列。

### 丢弃 Span

可以通过 `span.discard()` 主动丢弃 span，不上报：

```python
span = client.start_span("operation", "custom")
if should_not_trace():
    span.discard()
    return
# 正常逻辑
span.finish()
```

## 自定义 API 路径

使用 `APIBasePath` 自定义上报端点（适用于私有部署或代理场景）：

```python
from cozeloop._client import APIBasePath

path = APIBasePath(
    trace_span_upload_path="/custom/api/v1/traces",
    trace_file_upload_path="/custom/api/v1/files",
)
client = cozeloop.new_client(api_base_path=path)
```

## 完成事件回调

可以注册自定义的 finish 事件处理器，用于监控上报状态：

```python
from cozeloop.internal.trace.model.model import FinishEventInfo

def on_finish_event(info: FinishEventInfo):
    """
    event_type: "queue_manager.span_entry.rate" | "queue_manager.file_entry.rate" |
                "exporter.span_flush.rate" | "exporter.file_flush.rate"
    is_event_fail: bool
    item_num: int
    detail_msg: str
    extra_params: FinishEventInfoExtra (is_root_span, latency_ms)
    """
    if info.is_event_fail:
        print(f"上报失败: {info.event_type}, {info.detail_msg}")

client = cozeloop.new_client(trace_finish_event_processor=on_finish_event)
```

## 客户端缓存

`new_client()` 内部使用基于 MD5 的缓存键（由所有参数拼接后取 MD5），相同参数重复调用返回缓存实例。如果需要多个不同配置的客户端，确保参数不同。

## 异常体系

| 异常类 | 触发场景 |
|--------|---------|
| `InvalidParamError` | 参数无效（如缺少 workspace_id/api_base_url） |
| `AuthInfoRequiredError` | 未提供 api_token 也未提供 JWT OAuth 信息 |
| `NetworkError` | HTTP 请求网络错误（包装 httpx.HTTPError） |
| `RemoteServiceError` | 远端服务返回 code != 0（含 http_code, error_code, error_message, log_id） |
| `AuthError` | 认证失败（含 http_code, code, params, log_id） |
| `ClientClosedError` | 客户端已关闭后仍尝试操作 |
| `ParsePrivateKeyError` | JWT 私钥解析失败 |
| `HeaderParentError` | traceparent header 格式无效 |
| `InternalError` | 内部错误 |

所有异常继承自 `LoopError` 基类。
