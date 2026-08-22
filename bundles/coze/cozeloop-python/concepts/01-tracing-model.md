---
type: concept
title: "Tracing 模型"
description: "深入理解 CozeLoop 的 Span、Trace、SpanContext、Attributes（标签）、事件与状态模型，以及数据如何被结构化上报。"
tags: [tracing, span, trace, context, attributes, tags, model]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T03:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T03:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cl-031
    title: "SpanContext 接口"
  - id: F-cl-032
    title: "CommonSpanSetter 接口"
  - id: F-cl-033
    title: "Span 接口"
  - id: F-cl-034
    title: "内部 Span 实现"
---

# Tracing 模型

本文档深入讲解 CozeLoop 的 Tracing 数据模型，包括 Span、Trace、SpanContext、标签系统、状态码和 Span 生命周期。

## Trace 与 Span 的关系

### Trace（调用链）

一个 **Trace** 代表一次完整的请求/操作链路，由一个或多个 Span 组成的树形结构。同一个 Trace 中的所有 Span 共享同一个 `trace_id`（32 字符十六进制字符串）。

例如，一次用户提问可能产生以下 Trace 结构：

```
root_span (main_span)
├── llmCall (model)          ← 第一次 LLM 调用
│   └── prompt_template (prompt)  ← Prompt 格式化
├── retriever (retriever)    ← 知识检索
└── llmCall (model)          ← 第二次 LLM 调用（带检索结果）
```

### Span（跨度/操作单元）

**Span** 是 Trace 中的基本单元，代表一次具体操作。每个 Span 包含以下核心字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `trace_id` | str | 32 字符十六进制，标识所属 Trace |
| `span_id` | str | 16 字符十六进制，唯一标识此 Span |
| `parent_span_id` | str | 父 Span 的 span_id，根 Span 为 `"0"` |
| `name` | str | Span 名称，描述操作内容 |
| `span_type` | str | Span 类型，如 "model"、"tool"、"custom" |
| `start_time` | datetime | 开始时间 |
| `finish_time` | datetime | 结束时间 |
| `duration` | int | 持续时间（微秒），finish 时自动计算 |
| `status_code` | int | 状态码，0=成功，非零=异常 |
| `space_id` | str | 工作空间 ID |
| `flags` | int | 标志位，默认 1（已采样） |

## SpanContext

`SpanContext` 是 Span 的轻量级不可变引用，只包含 Trace 标识信息，用于跨线程/跨服务传播：

```python
class SpanContext:
    span_id: str       # 16字符十六进制
    trace_id: str      # 32字符十六进制
    baggage: Dict[str, str]  # 传播的键值对
```

SpanContext 的作用：
- **跨线程传播**：在新线程中创建子 Span 时，通过 `child_of=SpanContext` 传入
- **跨服务传播**：序列化为 HTTP header 在服务间传递
- **不包含业务数据**：仅包含 trace 标识和 baggage，不携带 tags 或 input/output

## 标签系统（Tags & Baggage）

### 标签（Tags）

标签是附加在 Span 上的键值对，用于记录操作的元数据。CozeLoop 将标签分为两类：

**系统保留标签**：通过专门的 setter 方法设置，有预定义的 key 和类型约束：

| 方法 | Key | 类型 | 说明 |
|------|-----|------|------|
| `set_input()` | `input` | Any | 输入数据 |
| `set_output()` | `output` | Any | 输出数据 |
| `set_error()` | `error` | str | 错误信息 |
| `set_status_code()` | `_status_code` | int | 状态码 |
| `set_model_provider()` | `model_provider` | str | LLM 提供商 |
| `set_model_name()` | `model_name` | str | 模型名称 |
| `set_model_call_options()` | `call_options` | Any | 模型调用参数 |
| `set_input_tokens()` | `input_tokens` | int | 输入 Token 数 |
| `set_output_tokens()` | `output_tokens` | int | 输出 Token 数 |
| `set_start_time_first_resp()` | `start_time_first_resp` | int | 首包时间戳（微秒） |
| `set_user_id()` | `user_id` | str | 用户 ID |
| `set_message_id()` | `message_id` | str | 消息 ID |
| `set_thread_id()` | `thread_id` | str | 会话/线程 ID |
| `set_prompt()` | `prompt_key`/`prompt_version` | str | Prompt 关联 |
| `set_service_name()` | — | str | 服务名（Span 属性） |
| `set_log_id()` | — | str | 日志 ID（Span 属性） |
| `set_deployment_env()` | `deployment_env` | str | 部署环境 |

**自定义标签**：通过 `set_tags()` 方法设置，可以使用任意 key：

```python
span.set_tags({
    "node_id": 6076665,
    "mode": "simple",
    "is_first_node": True,
    "score": 0.95,
})
```

自定义标签值支持以下类型：
- `str`、`int`、`float`、`bool`
- `Sequence[str]`、`Sequence[int]`、`Sequence[float]`、`Sequence[bool]`

系统保留标签有类型校验（`RESERVE_FIELD_TYPES`），类型不匹配时记录错误日志并跳过该标签。

### 自动计算标签

finish 时自动计算以下标签：

| 标签 | 计算方式 |
|------|---------|
| `tokens` | `input_tokens + output_tokens` |
| `latency_first_resp` | `start_time_first_resp - start_time`（微秒） |
| `duration` | `finish_time - start_time`（微秒） |
| `runtime` | 自动设置 language=python、loop_sdk_version=v0.1.27 |

### Baggage（传播标签）

Baggage 是一种特殊的标签，它不仅记录在当前 Span 上，还会自动传播到所有子 Span（包括跨线程和跨服务）：

```python
# Baggage 会自动传递给所有子 span
span.set_baggage({
    "product_id": "123456",
    "request_id": "abc-789",
})

# 便捷方法：同时设置标签和 baggage
span.set_user_id_baggage("user_123")
span.set_message_id_baggage("msg_456")
span.set_thread_id_baggage("thread_789")
```

Baggage 的传播路径：
1. 在当前 Span 设置 baggage → 自动设置为当前 Span 的标签
2. 创建子 Span 时 → 自动继承父 Span 的 baggage
3. `to_header()` → baggage 序列化为 X-Cozeloop-Tracestate header
4. `from_header()` → 从 header 解析 baggage 到新 SpanContext

Baggage 的 key 不能包含 `=` 和 `,`（这两个字符用于序列化格式）。

### 标签分类上报

上报时，标签按值类型分为四组（优化后端存储和查询）：

| 分组 | 类型 | 说明 |
|------|------|------|
| `tags_string` | str | 字符串标签 |
| `tags_long` | int | 整数标签 |
| `tags_double` | float | 浮点标签 |
| `tags_bool` | bool | 布尔标签 |

系统标签同理分为 `system_tags_string`/`system_tags_long`/`system_tags_double`。

### 标签大小限制

| 限制项 | 默认值 | 说明 |
|--------|--------|------|
| 单 Span 最大标签数 | 50 | 超出后新标签被忽略 |
| 标签 Key 最大长度 | 1024 字节 | 超出截断 |
| 普通标签值最大长度 | 1024 字节 | 超出截断 |
| input/output 值最大长度 | 1MB | ultra_large_report=False 时截断，True 时上传文件 |
| 截断保留长度 | 1000 字符 | 超大数据截断后保留的字符数 |

## Span 类型（span_type）

span_type 是区分 Span 用途的字符串标识，预定义值包括：

| 类型值 | 用途 | 典型标签 |
|--------|------|---------|
| `"custom"` | 自定义操作 | 任意自定义标签 |
| `"model"` | LLM 调用 | input、output、model_provider、model_name、input_tokens、output_tokens、call_options |
| `"tool"` | 工具调用 | input、output |
| `"chain"` | 链式/编排操作 | input、output |
| `"prompt"` | Prompt 模板 | prompt_key、prompt_version、prompt_provider |
| `"retriever"` | 检索操作 | retriever_provider 等 |
| `"graph"` | LangGraph 图 | 类似 chain |
| `"parser"` | 解析器操作 | input、output |

span_type 是字符串类型，你可以使用任意自定义值。预定义值有助于 CozeLoop 平台进行标准化展示和分析。

## 标准数据模型（spec/tracespec）

对于 model 类型的 Span，SDK 提供了标准化的输入输出数据模型，推荐使用以获得最佳平台展示效果：

### ModelInput

```python
from cozeloop.spec.tracespec import ModelInput, ModelMessage, ModelMessagePart, ModelMessagePartType

# 纯文本输入
input_data = ModelInput(messages=[
    ModelMessage(role="system", content="You are a helpful assistant."),
    ModelMessage(role="user", content="你好"),
])
span.set_input(input_data)

# 多模态输入（图片）
from cozeloop.spec.tracespec import ModelImageURL
multi_input = ModelInput(messages=[
    ModelMessage(role="user", parts=[
        ModelMessagePart(
            type=ModelMessagePartType.IMAGE,
            image_url=ModelImageURL(url="data:image/png;base64,...", name="photo.png"),
        ),
        ModelMessagePart(type=ModelMessagePartType.TEXT, text="描述这张图片"),
    ]),
])
span.set_input(multi_input)
```

### ModelOutput

```python
from cozeloop.spec.tracespec import ModelOutput, ModelChoice

output_data = ModelOutput(choices=[
    ModelChoice(
        index=0,
        finish_reason="stop",
        message=ModelMessage(role="assistant", content="这是一张..."),
    ),
])
span.set_output(output_data)
```

### ModelCallOption

```python
from cozeloop.spec.tracespec import ModelCallOption

options = ModelCallOption(
    temperature=0.7,
    max_tokens=2048,
    top_p=0.9,
    stop=["\n\n"],
    frequency_penalty=0.0,
    presence_penalty=0.0,
)
span.set_model_call_options(options)
```

### Runtime（系统标签）

Runtime 标签自动设置，一般不需要手动操作：

```python
class Runtime:
    language: str           # "python"
    library: str            # 如 "langchain"
    scene: str              # "custom"、"integration" 等
    library_version: str    # 集成库版本
    loop_sdk_version: str   # SDK 版本
    extra: dict             # 额外信息
```

## 状态码与错误处理

- `status_code = 0`：成功（默认）
- `status_code = -1`：默认错误码（`set_error()` 自动设置）
- `status_code = 其他非零值`：自定义错误码

```python
try:
    result = do_something()
except Exception as e:
    span.set_error(e)           # 自动设置 status_code=-1
    span.set_status_code(500)   # 覆盖为自定义错误码
    raise
```

注意：如果先设置了 `set_status_code()` 再调用 `set_error()`，不会覆盖已设置的非零状态码。

## Span 生命周期

```
start_span() → 设置标签/属性 → finish() → 进入队列 → 批量上报
    │                              │
    │                              └── 自动计算 duration/tokens/latency
    └── 自动写入 Context               设置 runtime 系统标签
```

1. **创建**：`start_span()` 生成 span_id 和 trace_id，记录 start_time，写入 context
2. **填充**：通过各种 setter 设置标签、属性、input/output
3. **完成**：`finish()` 计算 duration、汇总 tokens、设置 runtime，将 span 放入上报队列
4. **上报**：后台线程批量消费队列，通过 HTTP POST 上报到 CozeLoop 平台

使用 `with` 语句自动管理生命周期：

```python
with client.start_span("operation", "custom") as span:
    span.set_input(data)
    # 业务逻辑
    span.set_output(result)
# 退出 with 块时自动调用 finish()
```

使用 `discard()` 可以丢弃 span（不进入上报队列）：

```python
span = client.start_span("operation", "custom")
if should_skip:
    span.discard()  # 不上报
    return
span.finish()
```

## 上报数据格式

Span 最终序列化为 `UploadSpan` 结构上报：

```python
class UploadSpan:
    started_at_micros: int           # 开始时间（微秒时间戳）
    log_id: str                      # 日志 ID
    span_id: str                     # Span ID
    parent_id: str                   # 父 Span ID
    trace_id: str                    # Trace ID
    duration_micros: int             # 持续时间（微秒）
    service_name: str                # 服务名
    workspace_id: str                # 工作空间 ID
    span_name: str                   # Span 名称
    span_type: str                   # Span 类型
    status_code: int                 # 状态码
    input: str                       # 输入（JSON 字符串或对象存储 key）
    output: str                      # 输出
    object_storage: str              # 大文件/多模态对象存储信息（JSON）
    system_tags_string: Dict[str,str]
    system_tags_long: Dict[str,int]
    system_tags_double: Dict[str,float]
    tags_string: Dict[str,str]
    tags_long: Dict[str,int]
    tags_double: Dict[str,float]
    tags_bool: Dict[str,bool]
```
