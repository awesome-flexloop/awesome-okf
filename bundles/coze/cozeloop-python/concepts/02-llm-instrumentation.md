---
type: concept
title: "LLM 埋点模式"
description: "掌握 CozeLoop 的三种 LLM 埋点方式：@observe 装饰器、OpenAI 自动 Instrumentation、手动 Span 创建，以及流式调用、Token 统计等最佳实践。"
tags: [llm, instrumentation, decorator, openai, manual, span, integration]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T03:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T03:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cl-078
    title: "@observe 装饰器"
  - id: F-cl-084
    title: "OpenAI Wrapper"
  - id: F-cl-089
    title: "LangChain Callback"
---

# LLM 埋点模式

CozeLoop 提供三种递进式的 LLM 应用埋点方式，从最简单的装饰器到零侵入的自动 Instrumentation，再到灵活的手动 Span 创建。开发者可以根据场景选择合适的方式，也可以组合使用。

## 方式一：@observe 装饰器

`@observe` 是最通用的埋点方式，适合追踪任意 Python 函数。它自动处理函数的输入记录、输出记录、异常捕获、span 生命周期管理。

### 基本用法

```python
from cozeloop.decorator import observe

@observe
def my_function(arg1, arg2):
    """最简用法——span 名称默认为函数名，span_type 默认为 'custom'"""
    return do_something(arg1, arg2)
```

### LLM 调用追踪

对 LLM 调用函数，建议设置 `span_type="model"` 并配置相关标签：

```python
from cozeloop.decorator import observe
from cozeloop import get_span_from_context

@observe(
    name="call_gpt4",
    span_type="model",
    tags={
        "model_provider": "openai",
        "model_name": "gpt-4-1106-preview",
    },
)
def call_llm(prompt: str) -> str:
    response = openai_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-4-1106-preview",
    )
    # 如果需要在运行时动态设置标签
    span = get_span_from_context()
    span.set_input_tokens(response.usage.prompt_tokens)
    span.set_output_tokens(response.usage.completion_tokens)
    return response.choices[0].message.content
```

### 输入输出处理

通过 `process_inputs` 和 `process_outputs` 钩子控制记录的内容（如过滤敏感信息、提取关键字段）：

```python
def sanitize_input(input_dict):
    """input_dict 格式: {"args": (positional_args), "kwargs": {keyword_args}}"""
    kwargs = input_dict["kwargs"].copy()
    kwargs.pop("api_key", None)  # 移除敏感字段
    return {"args": input_dict["args"], "kwargs": kwargs}

def extract_content(result):
    """从 OpenAI 响应中提取文本内容"""
    return result.choices[0].message.content

@observe(
    span_type="model",
    process_inputs=sanitize_input,
    process_outputs=extract_content,
)
def safe_llm_call(prompt, api_key=None):
    return openai_client.chat.completions.create(...)
```

### 支持的函数类型

`@observe` 自动检测并适配以下函数类型：

| 函数类型 | 示例 | 说明 |
|---------|------|------|
| 同步函数 | `def func():` | 标准同步函数 |
| 异步函数 | `async def func():` | async/await 函数 |
| 同步生成器 | `def func(): yield` | 生成器函数，收集所有 yield 值 |
| 异步生成器 | `async def func(): yield` | async generator |
| 类方法 | `def method(self):` | 自动忽略 self 参数 |

装饰器内部通过 `inspect` 模块检测函数类型，选择对应的 wrapper。对类方法，自动从 args 中移除 `self` 后再记录 input。

## 方式二：OpenAI 自动 Instrumentation（openai_wrapper）

对于使用 OpenAI Python SDK 的应用，`openai_wrapper` 提供了零侵入的自动埋点——只需一行代码包装客户端，所有后续调用自动被追踪。

### 基本用法

```python
from openai import OpenAI
from cozeloop.integration.wrapper import openai_wrapper
import cozeloop

# 初始化 CozeLoop（环境变量配置或显式传参）
cozeloop.new_client()

# 包装 OpenAI 客户端
client = openai_wrapper(OpenAI(api_key="your-key"))

# 之后正常使用——所有 chat.completions.create 调用自动 trace
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "你好"}],
    model="gpt-4",
)
print(response.choices[0].message.content)
```

### 支持的客户端类型

| 客户端类 | model_provider |
|---------|---------------|
| `OpenAI` | "openai" |
| `AsyncOpenAI` | "openai" |
| `AzureOpenAI` | "azure" |
| `AsyncAzureOpenAI` | "azure" |

### 自动提取的信息

openai_wrapper 自动从调用参数和响应中提取：

- **调用参数**：model、temperature、max_tokens、top_p、n、stop、frequency_penalty、presence_penalty、stream
- **响应数据**：完整的 choices 列表（含 message、tool_calls、finish_reason）
- **Token 用量**：从 usage.prompt_tokens 和 usage.completion_tokens 提取
- **流式聚合**：stream=True 时自动聚合所有 chunk，重建完整响应，从最后一个 chunk 的 usage 提取 token（需 `stream_options={"include_usage": True}`）
- **首包延迟**：流式调用时自动记录第一个 token 的到达时间

### Responses API 支持

openai_wrapper 也支持 OpenAI 的新 Responses API：

```python
response = client.responses.create(
    model="gpt-4o",
    input="你好",
)
```

### Azure OpenAI

```python
from openai import AzureOpenAI

azure_client = openai_wrapper(AzureOpenAI(
    api_key="your-azure-key",
    api_version="2024-02-01",
    azure_endpoint="https://your-resource.openai.azure.com/",
), chat_name="AzureChatOpenAI")
```

### 流式调用

```python
stream = client.chat.completions.create(
    messages=[{"role": "user", "content": "写一首诗"}],
    model="gpt-4",
    stream=True,
    stream_options={"include_usage": True},  # 重要：让最后一个 chunk 包含 usage
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
# 流消费完毕后 span 自动 finish，token 统计自动记录
```

### 异步调用

```python
from openai import AsyncOpenAI

async_client = openai_wrapper(AsyncOpenAI(api_key="your-key"))

async def chat():
    response = await async_client.chat.completions.create(
        messages=[{"role": "user", "content": "你好"}],
        model="gpt-4",
    )
    return response.choices[0].message.content
```

## 方式三：手动 Span 创建

当装饰器和自动 Instrumentation 无法满足需求时（如复杂条件逻辑、跨多个函数的操作、自定义标签逻辑），使用手动 Span API。

### 基本模式

```python
import cozeloop

def complex_operation(input_data):
    span = cozeloop.start_span("complex_operation", "custom")
    try:
        span.set_input(input_data)

        # 步骤1：预处理
        preprocessed = preprocess(input_data)

        # 步骤2：LLM 调用（子 span 自动嵌套）
        llm_span = cozeloop.start_span("llm_step", "model")
        try:
            llm_span.set_model_provider("openai")
            llm_span.set_model_name("gpt-4")
            result = call_llm(preprocessed)
            llm_span.set_output(result)
            llm_span.set_input_tokens(100)
            llm_span.set_output_tokens(50)
        except Exception as e:
            llm_span.set_error(e)
            raise
        finally:
            llm_span.finish()

        span.set_output(result)
        return result
    except Exception as e:
        span.set_error(e)
        span.set_status_code(500)
        raise
    finally:
        span.finish()
```

### 使用 with 语句简化

```python
def complex_operation(input_data):
    with cozeloop.start_span("complex_operation", "custom") as span:
        span.set_input(input_data)
        result = do_work(input_data)
        span.set_output(result)
        return result
    # 退出 with 块时自动 finish，异常自动记录
```

### 嵌套 Span

在同一线程/协程中，`start_span()` 自动从 context 获取当前 span 作为父 span：

```python
with cozeloop.start_span("root", "main_span") as root:
    # 自动成为 root 的子 span
    with cozeloop.start_span("step1", "custom") as step1:
        step1.set_output("done")

    with cozeloop.start_span("step2", "model") as step2:
        step2.set_model_provider("openai")
        step2.set_output("llm result")
```

### LLM Span 标准标签

对 model 类型 span，建议设置以下标准标签以获得最佳平台展示：

```python
with cozeloop.start_span("llm_call", "model") as span:
    span.set_input("用户的问题")              # 输入（字符串或 ModelInput）
    span.set_output("模型的回答")              # 输出（字符串或 ModelOutput）
    span.set_model_provider("openai")        # 提供商
    span.set_model_name("gpt-4-1106-preview")  # 模型名
    span.set_input_tokens(232)               # 输入 token 数
    span.set_output_tokens(1211)             # 输出 token 数（自动计算 tokens 总和）
    span.set_start_time_first_resp(          # 首包时间（微秒时间戳）
        int(time.time() * 1000000)
    )
```

## LangChain / LangGraph 集成

对于使用 LangChain 框架的应用，通过 Callback Handler 方式集成：

```python
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from cozeloop.integration.langchain.trace_callback import LoopTracer
import cozeloop

client = cozeloop.new_client()
handler = LoopTracer.get_callback_handler(client)

llm = ChatOpenAI(model="gpt-4")
chain = llm | StrOutputParser()

result = chain.invoke(
    input="你好",
    config=RunnableConfig(callbacks=[handler]),
)
```

LangChain 集成自动为每个组件（LLM、Chain、Tool、Prompt）创建对应类型的 span，自动提取模型参数、token 用量、输入输出。详见 [框架集成参考](/references/integrations.md)。

## 三种方式对比

| 特性 | @observe 装饰器 | openai_wrapper | 手动 Span | LangChain Handler |
|------|----------------|----------------|----------|-------------------|
| 侵入性 | 低（加装饰器） | 极低（一行包装） | 高（手动管理） | 低（传 callback） |
| 灵活性 | 中 | 低（固定模式） | 高 | 中 |
| 自动 input/output | ✅ | ✅ | ❌ 手动设置 | ✅ |
| 流式支持 | ✅ (process_iterator_outputs) | ✅ 自动 | 需手动处理 | ✅ |
| 异常捕获 | ✅ 自动 | ✅ 自动 | ❌ try/except | ✅ 自动 |
| 适用场景 | 任意函数 | OpenAI 调用 | 复杂逻辑/跨函数 | LangChain LCEL |
| 异步支持 | ✅ | ✅ | ✅ | ✅ |
| Token 统计 | ❌ 手动设置 | ✅ 自动提取 | ❌ 手动设置 | ✅ 自动提取 |

## 最佳实践

1. **优先使用自动集成**：能用 openai_wrapper 或 LangChain Handler 就不用手动创建 span
2. **函数级用 @observe**：对自定义函数用 @observe 装饰器，减少样板代码
3. **model span 设置标准标签**：LLM 调用务必设置 model_provider、model_name、input/output tokens
4. **使用 with 语句**：手动 span 始终用 with 语句确保 finish 被调用
5. **合理使用 baggage**：对需要全局传播的信息（如 user_id、request_id）使用 baggage 而非普通 tags
6. **流式调用传 stream_options**：使用 OpenAI 流式 API 时设置 `stream_options={"include_usage": True}` 以获取 token 统计
7. **process_inputs 过滤敏感信息**：对含密码、API Key 等的函数使用 process_inputs 过滤
8. **混合使用**：三种方式可以混合——openai_wrapper 创建的 span 和 @observe/手动 span 在同一 context 中自动建立父子关系
