---
type: reference
title: "Tracing API 参考"
description: "CozeLoop Python SDK Tracing API 完整参考：客户端初始化、Tracer/Span 创建、Span 属性设置、上下文管理。"
tags: [tracing, api, span, client, context]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T03:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T03:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cl-007
    title: "公共 API 导出"
  - id: F-cl-016
    title: "Client 抽象基类"
  - id: F-cl-031
    title: "SpanContext 接口"
  - id: F-cl-032
    title: "CommonSpanSetter 接口"
  - id: F-cl-033
    title: "Span 接口"
---

# Tracing API 参考

本文档详细描述 CozeLoop Python SDK 的 Tracing API，包括客户端初始化、Span 创建与属性设置、上下文管理等核心接口。

## 客户端初始化

### new_client()

创建并返回一个 `Client` 实例。客户端是线程安全的，建议在程序生命周期内只创建一次。

```python
import cozeloop

client = cozeloop.new_client(
    api_base_url="https://api.coze.cn",     # 可选，默认 CN_BASE_URL
    workspace_id="your_workspace_id",       # 可选，可通过环境变量设置
    api_token="your_pat_token",             # 可选，PAT Token 认证
    jwt_oauth_client_id="",                 # 可选，JWT OAuth 认证
    jwt_oauth_private_key="",               # 可选，JWT OAuth 认证
    jwt_oauth_public_key_id="",             # 可选，JWT OAuth 认证
    timeout=3,                              # 请求超时（秒），默认 3
    upload_timeout=30,                      # 上传超时（秒），默认 30
    ultra_large_report=False,               # 超大数据是否分文件上传，默认 False
    prompt_cache_max_count=100,             # Prompt 缓存最大条数，默认 100
    prompt_cache_refresh_interval=60,       # Prompt 缓存刷新间隔（秒），默认 60
    prompt_trace=False,                     # Prompt 操作是否自动 trace，默认 False
    http_client=None,                       # 可选，自定义 httpx.Client
    trace_finish_event_processor=None,      # 可选，自定义完成事件回调
    tag_truncate_conf=None,                 # 可选，TagTruncateConf 自定义截断配置
    api_base_path=None,                     # 可选，APIBasePath 自定义上传路径
    trace_queue_conf=None,                  # 可选，QueueConf 自定义队列配置
)
```

**认证方式优先级**：如果提供了 JWT OAuth 三个参数则使用 JWT 认证，否则如果提供了 `api_token` 则使用 PAT Token 认证，两者都没有则抛出 `AuthInfoRequiredError`。

**环境变量回退**：未显式传入的参数会自动从环境变量读取：
- `COZELOOP_API_BASE_URL` → api_base_url
- `COZELOOP_WORKSPACE_ID` → workspace_id
- `COZELOOP_API_TOKEN` → api_token
- `COZELOOP_JWT_OAUTH_CLIENT_ID` → jwt_oauth_client_id
- `COZELOOP_JWT_OAUTH_PRIVATE_KEY` → jwt_oauth_private_key
- `COZELOOP_JWT_OAUTH_PUBLIC_KEY_ID` → jwt_oauth_public_key_id

**注意**：重复调用 `new_client()` 传入相同参数会返回缓存的客户端实例。首次创建客户端时自动设置为默认客户端，并注册 atexit 钩子进行优雅关闭。

### 模块级便捷函数

不创建客户端实例也可以直接使用模块级函数，首次调用时会自动初始化默认客户端（从环境变量读取配置）：

```python
import cozeloop

span = cozeloop.start_span("span_name", "custom")  # 自动初始化默认客户端
span.finish()
cozeloop.flush()
cozeloop.close()
```

### set_default_client(client)

设置全局默认客户端。设置新客户端时会自动关闭旧客户端。

### close() / client.close()

关闭客户端，执行 flush 并释放资源。关闭后客户端返回 NoopSpan，不可再用。程序退出前应调用。

### flush() / client.flush()

强制刷新队列中所有待上报的 span，阻塞等待上报完成。通常不需要手动调用，SDK 会自动批量上报。仅在程序退出前或需要立即查看数据时使用。

## Span 创建

### client.start_span() / cozeloop.start_span()

创建一个新的 Span，自动链接到当前上下文（context）中的父 span。

```python
span = client.start_span(
    name: str,                          # Span 名称
    span_type: str,                     # Span 类型，如 "custom"、"model"、"tool"、"chain" 等
    *,
    start_time: Optional[datetime] = None,  # 可选，自定义开始时间
    child_of: Optional[SpanContext] = None, # 可选，显式指定父 SpanContext（跨线程/服务）
    start_new_trace: bool = False,          # 可选，是否强制开启新 trace
) -> Span
```

**行为说明**：
- 如果未指定 `child_of` 且 `start_new_trace=False`，自动从当前 context 获取父 span。
- 如果指定了 `child_of`，则使用该 SpanContext 作为父级（继承 trace_id、parent_span_id、baggage）。
- 如果 `start_new_trace=True`，忽略 context 中的父 span，创建新 trace。
- 新创建的 span 自动写入当前 context，后续 `start_span()` 调用会自动将其作为父 span。
- 如果客户端已关闭或创建失败，返回 `NOOP_SPAN`（空操作 span）。

**Span 类型约定**：
- `"custom"`：自定义 span（@observe 默认值）
- `"model"`：LLM 调用 span
- `"tool"`：工具调用 span
- `"chain"`：链式调用/编排 span
- `"prompt"`：Prompt 模板处理 span
- `"retriever"`：检索器 span
- `"graph"`：LangGraph 图 span
- `"parser"`：解析器 span
- 也可以使用任意自定义字符串

### get_span_from_context()

获取当前上下文（context）中最新的 span。通常在 @observe 装饰的函数内部使用，以在运行时动态设置标签或 baggage。

```python
from cozeloop import get_span_from_context

span = get_span_from_context()
span.set_tags({"dynamic_key": "value"})
```

### get_span_from_header(header)

从 HTTP header 字典中解析 SpanContext，用于跨服务追踪。

```python
from cozeloop import get_span_from_header

# 在服务 B 接收请求时
span_context = get_span_from_header(request.headers)
span = client.start_span("service_b_root", "main_span", child_of=span_context)
```

## Span 属性设置

### 通用标签方法

| 方法 | 说明 |
|------|------|
| `span.set_tags(tag_kvs: Dict[str, Any])` | 设置自定义业务标签。值需为 JSON 可序列化类型：str、int、float、bool 及其 Sequence。单个 span 最多 50 个标签键值对。 |
| `span.set_baggage(baggage_items: Dict[str, str])` | 设置 Baggage，同时设置标签并自动传递给下游子 span。 |
| `span.set_status_code(code: int)` | 设置状态码，非零值表示异常。set_error() 自动设为 -1。 |
| `span.set_error(err: Exception)` | 设置错误信息，自动将 status_code 设为 -1（如果当前为 0）。 |

### LLM 相关标签

| 方法 | 标签 Key | 说明 |
|------|----------|------|
| `span.set_input(input: Any)` | `input` | 设置输入信息，推荐使用 ModelInput 格式，也可传任意可序列化对象。 |
| `span.set_output(output: Any)` | `output` | 设置输出信息，推荐使用 ModelOutput 格式。 |
| `span.set_model_provider(provider: str)` | `model_provider` | 设置 LLM 提供商，如 "openai"、"azure"。 |
| `span.set_model_name(name: str)` | `model_name` | 设置模型名称，如 "gpt-4-1106-preview"。 |
| `span.set_model_call_options(options: Any)` | `call_options` | 设置模型调用参数，推荐使用 ModelCallOption。 |
| `span.set_input_tokens(tokens: int)` | `input_tokens` | 设置输入 token 数，自动与 output_tokens 求和计算 tokens。 |
| `span.set_output_tokens(tokens: int)` | `output_tokens` | 设置输出 token 数。 |
| `span.set_start_time_first_resp(timestamp_us: int)` | `start_time_first_resp` | 设置首包返回时间戳（微秒），自动计算 latency_first_resp。 |

### 上下文关联标签

| 方法 | 标签 Key | Baggage |
|------|----------|---------|
| `span.set_user_id(user_id: str)` | `user_id` | 否 |
| `span.set_user_id_baggage(user_id: str)` | `user_id` | 是 |
| `span.set_message_id(message_id: str)` | `message_id` | 否 |
| `span.set_message_id_baggage(message_id: str)` | `message_id` | 是 |
| `span.set_thread_id(thread_id: str)` | `thread_id` | 否 |
| `span.set_thread_id_baggage(thread_id: str)` | `thread_id` | 是 |

### 其他系统标签

| 方法 | 说明 |
|------|------|
| `span.set_prompt(prompt: Prompt)` | 关联 PromptKey 和 PromptVersion 标签。 |
| `span.set_runtime(runtime: Runtime)` | 设置运行时信息（仅集成内部使用）。 |
| `span.set_service_name(service_name: str)` | 设置自定义服务名，标识不同服务。 |
| `span.set_log_id(log_id: str)` | 设置自定义日志 ID，标识不同请求。 |
| `span.set_deployment_env(env: str)` | 设置部署环境标签。 |
| `span.set_finish_time(finish_time: datetime)` | 自定义 span 结束时间（高级用法）。 |
| `span.set_system_tags(system_tags: Dict[str, Any])` | 设置系统保留标签（慎用）。 |

## Span 生命周期

### span.finish()

标记 span 完成，span 将被放入异步队列等待上报。**必须调用**，否则 span 不会被上报。使用 `with` 语句时自动调用。

```python
span = client.start_span("my_span", "custom")
try:
    # 业务逻辑
    span.set_input("hello")
    span.set_output("world")
except Exception as e:
    span.set_error(e)
    raise
finally:
    span.finish()
```

### span.discard()

丢弃 span，不上报。从上下文中移除但不进入上报队列。

### 上下文管理器（with 语句）

Span 支持上下文管理器协议，退出 with 块时自动调用 `finish()`：

```python
with client.start_span("my_span", "custom") as span:
    span.set_input("hello")
    span.set_output("world")
    # 嵌套 span 自动建立父子关系
    with client.start_span("child_span", "custom") as child:
        child.set_tags({"key": "value"})
# 退出 with 块时自动 finish
```

### span.to_header()

将 span 序列化为 HTTP header 字典，用于跨服务传播：

```python
headers = span.to_header()
# headers = {
#     "X-Cozeloop-Traceparent": "00-{trace_id}-{span_id}-01",
#     "X-Cozeloop-Tracestate": "key1=val1,key2=val2"
# }
```

## SpanContext 接口

`SpanContext` 是 span 的轻量级上下文引用，仅包含 trace 标识信息，用于跨线程/跨服务传递：

| 属性 | 类型 | 说明 |
|------|------|------|
| `span_id` | str | 16 字符十六进制 Span ID |
| `trace_id` | str | 32 字符十六进制 Trace ID |
| `baggage` | Dict[str, str] | Baggage 键值对 |

## 配置类

### TagTruncateConf

自定义标签值截断长度：

```python
from cozeloop.internal.trace.model.model import TagTruncateConf

conf = TagTruncateConf(
    normal_field_max_byte=2048,              # 普通字段最大字节数
    input_output_field_max_byte=2*1024*1024, # input/output 字段最大字节数
)
client = cozeloop.new_client(tag_truncate_conf=conf)
```

### QueueConf

自定义上报队列配置：

```python
from cozeloop.internal.trace.model.model import QueueConf

qconf = QueueConf(
    span_queue_length=2048,                  # span 队列最大长度
    span_max_export_batch_length=200,        # 单批最大 span 数
)
client = cozeloop.new_client(trace_queue_conf=qconf)
```

### APIBasePath

自定义 API 上传路径：

```python
from cozeloop._client import APIBasePath

path = APIBasePath(
    trace_span_upload_path="/custom/v1/traces",
    trace_file_upload_path="/custom/v1/files",
)
client = cozeloop.new_client(api_base_path=path)
```

## 日志配置

```python
import logging
from cozeloop.logger import set_log_level, add_log_handler

set_log_level(logging.DEBUG)  # 设置日志级别

# 添加自定义日志处理器
import sys
handler = logging.StreamHandler(sys.stderr)
add_log_handler(handler)
```
