---
type: reference
title: "框架集成参考"
description: "CozeLoop Python SDK 框架集成参考：@observe 装饰器、OpenAI 自动埋点、LangChain/LangGraph Callback Handler、手动 Span API。"
tags: [integration, decorator, openai, langchain, observe, wrapper]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T03:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T03:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cl-078
    title: "@observe 装饰器"
  - id: F-cl-084
    title: "OpenAI 集成"
  - id: F-cl-089
    title: "LangChain Callback Handler"
---

# 框架集成参考

本文档描述 CozeLoop Python SDK 提供的框架集成方式，包括通用 @observe 装饰器、OpenAI 自动埋点 Wrapper 和 LangChain/LangGraph Callback Handler。

## @observe 装饰器

`@observe` 是 CozeLoop 最通用的集成方式，可用于装饰任意 Python 函数，自动为函数执行创建 span。

### 基本用法

```python
from cozeloop.decorator import observe

@observe
def my_function(arg1, arg2):
    return "result"

# 自定义 span 名称和类型
@observe(name="custom_name", span_type="model")
def llm_call(prompt):
    return "response"
```

### 完整参数

```python
@observe(
    func=None,                          # 被装饰函数（装饰器模式下无需传）
    name=None,                          # Span 名称，默认使用函数名
    span_type="custom",                 # Span 类型，默认 "custom"
    tags=None,                          # 静态标签 Dict[str, Any]
    baggage=None,                       # 静态 Baggage Dict[str, str]
    client=None,                        # 指定 Client 实例，默认使用全局默认客户端
    process_inputs=None,                # 输入处理回调 Callable[[dict], Any]
    process_outputs=None,               # 输出处理回调 Callable[[Any], Any]
    process_iterator_outputs=None,      # 迭代器输出处理回调 Callable[[List], Any]
)
```

### 参数详解

**name**: Span 名称，默认为被装饰函数的 `__name__`。

**span_type**: Span 类型，默认为 `"custom"`。对 LLM 调用函数推荐使用 `"model"`。

**tags**: 静态标签字典，在装饰时定义，优先级高于自动生成的标签。例如：

```python
@observe(
    span_type="model",
    tags={"model_provider": "openai", "model_name": "gpt-4"},
)
def call_llm(prompt):
    ...
```

**baggage**: 静态 Baggage 字典，自动传递给所有子 span。同时也设置为当前 span 的标签。

```python
@observe(baggage={"request_id": "abc123"})
def handle_request():
    # request_id 会自动传递给此函数内创建的所有子 span
    call_llm("hello")
```

**client**: 指定使用的 Client 实例。如果不传，使用全局默认客户端（自动从环境变量初始化）。

**process_inputs**: 输入处理函数，接收 `{"args": args, "kwargs": kwargs}` 字典，返回处理后的值作为 span 的 input 标签。可用于过滤敏感信息：

```python
def sanitize_input(input_dict):
    args = input_dict["args"]
    kwargs = input_dict["kwargs"]
    # 移除敏感字段
    kwargs.pop("api_key", None)
    return {"args": args, "kwargs": kwargs}

@observe(process_inputs=sanitize_input)
def call_api(api_key, query):
    ...
```

**process_outputs**: 输出处理函数，接收函数返回值，返回处理后的值作为 span 的 output 标签。

```python
def extract_output(result):
    return {"text": result.choices[0].message.content}

@observe(process_outputs=extract_output)
def call_llm(prompt):
    return openai_client.chat.completions.create(...)
```

**process_iterator_outputs**: 迭代器/流输出处理函数。当函数返回迭代器（如流式 LLM 响应）时，装饰器会自动收集所有迭代元素到 List 中，传入此回调处理。**此参数的存在会触发流式包装模式**，返回 `_CozeLoopTraceStream`（同步）或 `_CozeLoopAsyncTraceStream`（异步）对象，在迭代完全结束后才上报 span。

```python
def process_stream(chunks):
    # chunks 是所有流式 chunk 的列表
    full_text = "".join(c.choices[0].delta.content or "" for c in chunks)
    return {"text": full_text}

@observe(
    span_type="model",
    process_iterator_outputs=process_stream,
)
def stream_llm(prompt):
    return openai_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-4",
        stream=True,
    )
```

### 支持的函数类型

`@observe` 自动检测函数类型并选择合适的 wrapper：

| 函数类型 | 检测方法 | Wrapper |
|---------|---------|---------|
| 同步函数 | `inspect.iscoroutinefunction()` 为 False | sync_wrapper |
| 异步函数 | `inspect.iscoroutinefunction()` 为 True | async_wrapper |
| 同步生成器 | `inspect.isgeneratorfunction()` | gen_wrapper |
| 异步生成器 | `inspect.isasyncgenfunction()` | async_gen_wrapper |
| 同步流（有 process_iterator_outputs） | 检测到 `__iter__` | sync_stream_wrapper |
| 异步流（有 process_iterator_outputs） | 检测到 `__aiter__` | async_stream_wrapper |

### 异步函数支持

`@observe` 完整支持 async/await：

```python
@observe(name="async_llm", span_type="model")
async def async_llm_call(prompt):
    response = await async_openai.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-4",
    )
    return response
```

### 流式首包延迟

当 span_type 为 `"model"` 且使用流式包装（process_iterator_outputs），装饰器会在收到第一个 chunk 时自动记录 `start_time_first_resp`（首包时间戳，微秒），用于计算 TTFT（首 Token 延迟）。

### @to_runnable 装饰器（LangChain 专用）

`@to_runnable` 将普通函数包装为 LangChain `RunnableLambda`，使其可以在 LCEL 链中被追踪：

```python
from cozeloop.decorator import to_runnable

@to_runnable
def my_tool(input: dict) -> str:
    return input["text"].upper()

# 使用时必须传入 config 参数（含 LoopTracer callback）
from langchain_core.runnables import RunnableConfig
result = my_tool({"text": "hello"}, config=RunnableConfig(callbacks=[callback_handler]))
```

## OpenAI 自动埋点

`openai_wrapper()` 提供 OpenAI 客户端的零侵入自动埋点，通过 monkey-patch 方式包装 `chat.completions.create` 和 `responses.create` 方法。

### 基本用法

```python
from openai import OpenAI
from cozeloop.integration.wrapper import openai_wrapper
import cozeloop

# 初始化 CozeLoop 客户端
client = cozeloop.new_client()

# 创建并包装 OpenAI 客户端
openai_client = openai_wrapper(OpenAI(
    api_key="your-openai-key",
    base_url="https://api.openai.com/v1",
))

# 之后正常使用 OpenAI 客户端，所有调用自动被 trace
response = openai_client.chat.completions.create(
    messages=[{"role": "user", "content": "你好"}],
    model="gpt-4",
)
```

### 函数签名

```python
def openai_wrapper(client: Any, *, chat_name: str = "ChatOpenAI") -> Any:
```

**参数**：
- `client`: OpenAI 客户端实例，支持 `OpenAI`、`AsyncOpenAI`、`AzureOpenAI`、`AsyncAzureOpenAI`
- `chat_name`: Span 名称，默认 "ChatOpenAI"；Azure 客户端默认改为 "AzureChatOpenAI"

**返回值**：包装后的客户端（原对象被 in-place 修改）。

### 自动提取的标签

openai_wrapper 自动从调用参数中提取以下标签：

| 标签 Key | 提取来源 |
|----------|---------|
| `model_provider` | 自动检测：OpenAI → "openai"，Azure → "azure" |
| `model_name` | kwargs 中的 `model` 参数 |
| `call_options` | JSON 序列化的 ModelCallOption（temperature, max_tokens, stop, top_p, n, frequency_penalty, presence_penalty） |
| `stream` | kwargs 中的 `stream` 参数 |
| `input` | 传入 create 的 kwargs（通过 process_inputs 提取） |
| `output` | 响应内容（非流式）或聚合后的流式内容 |
| `input_tokens` / `output_tokens` | 从响应 usage 中提取（prompt_tokens/completion_tokens） |

### 流式支持

`stream=True` 时自动使用流式包装：
- 同步流：收集所有 `ChatCompletionChunk`，聚合成完整响应后上报
- 异步流：同理
- 自动聚合 tool_calls 和 reasoning_content
- 从最后一个 chunk 的 usage 字段（需 `stream_options={"include_usage": True}`）提取 token 用量
- 自动记录首包延迟

### 支持的 API

- `client.chat.completions.create()`：Chat Completion API（同步/异步/流式）
- `client.responses.create()`：Responses API（同步/异步/流式），如果客户端存在此方法

### Azure OpenAI

```python
from openai import AzureOpenAI

azure_client = openai_wrapper(AzureOpenAI(
    api_key="your-azure-key",
    api_version="2024-02-01",
    azure_endpoint="https://your-resource.openai.azure.com/",
))
# model_provider 自动设为 "azure"，span 名称为 "AzureChatOpenAI"
```

## LangChain / LangGraph 集成

LangChain 集成通过 `LoopTracer` 获取 Callback Handler，作为 callbacks 传入 LCEL 链的 invoke/stream 调用。

### LoopTracer.get_callback_handler()

```python
from cozeloop.integration.langchain.trace_callback import LoopTracer

handler = LoopTracer.get_callback_handler(
    client=None,                          # 可选，指定 Client 实例
    modify_name_fn=None,                  # 可选，自定义 span 名称函数 Callable[[str], str]
    add_tags_fn=None,                     # 可选，自定义标签函数 Callable[[str], Dict[str, Any]]
    tags=None,                            # 可选，全局标签 Dict[str, Any]
    child_of=None,                        # 可选，父 Span
    state_span_ctx_key=None,              # 可选，LangGraph state 中 span context 的字段名
)
```

### 基本用法（LCEL）

```python
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from cozeloop import new_client, set_log_level
from cozeloop.integration.langchain.trace_callback import LoopTracer
import logging

set_log_level(logging.INFO)
client = new_client()

trace_handler = LoopTracer.get_callback_handler(client)

llm = ChatOpenAI(model="gpt-4")
chain = llm | StrOutputParser()

output = chain.invoke(
    input="你好",
    config=RunnableConfig(callbacks=[trace_handler]),
)
```

### 自定义 Span 名称和标签

```python
def modify_name(node_name: str) -> str:
    # node_name 是 LangChain 节点名（如 "RunnableSequence"、"ChatOpenAI"）
    if node_name == "RunnableSequence":
        return "MyChain"
    return node_name

def add_tags(node_name: str) -> dict:
    if node_name == "ChatOpenAI":
        return {"custom_tag": "llm_call"}
    return {}

handler = LoopTracer.get_callback_handler(
    modify_name_fn=modify_name,
    add_tags_fn=add_tags,
    tags={"service": "my-app"},
)
```

### LangGraph 集成

使用 `state_span_ctx_key` 参数可以在 LangGraph state 中传递 span context，供异步节点创建子 span：

```python
handler = LoopTracer.get_callback_handler(
    state_span_ctx_key="span_ctx",  # state 中的字段名
)

# 在节点中可以从 state 获取 span context 创建子 span
def my_node(state):
    parent_ctx = state.get("span_ctx")
    span = client.start_span("my_node", "tool", child_of=parent_ctx)
    try:
        # 业务逻辑
        pass
    finally:
        span.finish()
```

### 自动映射的 Span 类型

| LangChain 组件 | span_type |
|---------------|-----------|
| ChatPromptTemplate | "prompt" |
| LLM/ChatModel（ChatOpenAI等） | "model" |
| RunnableSequence/Chain | "chain" |
| LangGraph | "graph" |
| Tool | "tool" |
| ReActSingleInputOutputParser | "parser" |

### 自动提取的信息

- **LLM 节点**：自动从 invocation_params 提取 model_name、call_options（temperature/top_p/max_tokens 等）、stream 标记；从 LLMResult 提取 token 用量（input_tokens/output_tokens/tokens/reasoning_tokens/input_cached_tokens）；on_llm_new_token 回调自动记录首包延迟。
- **Chain 节点**：自动记录 inputs 和 outputs。
- **Tool 节点**：自动记录 input_str 和 output。
- **Prompt 节点**：自动解析模板内容、变量和 partial_variables，记录 prompt_key/prompt_version（从 tags 或 LangSmith Hub 元数据提取）。
- **错误处理**：on_chain_error/on_tool_error 自动设置 error 和 error_trace 标签。

### 注意事项

- **每次请求创建新的 handler**：`LoopTracer.get_callback_handler()` 返回的 handler 维护 run_map 状态，不应在多个请求间复用。
- handler 不是线程安全的，每个请求应获取新实例。
- 需要安装 langchain-core 和相关集成包（langchain-openai 等）才能使用。

## 手动 Span API（对比）

当装饰器和自动集成无法满足需求时，始终可以使用手动 Span API：

```python
import cozeloop

span = cozeloop.start_span("custom_operation", "custom")
try:
    span.set_input({"query": "search"})
    # 业务逻辑
    result = do_work()
    span.set_output(result)
    span.set_tags({"key": "value"})
except Exception as e:
    span.set_error(e)
    span.set_status_code(500)
    raise
finally:
    span.finish()
```

三种集成方式可以混合使用——@observe 和 openai_wrapper 创建的 span 与手动 start_span 创建的 span 在同一 context 中自动建立父子关系。
