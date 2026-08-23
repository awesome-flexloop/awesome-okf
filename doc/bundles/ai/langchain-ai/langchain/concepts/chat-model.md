---
type: concept
title: 聊天模型
description: BaseChatModel 抽象基类、_generate 核心方法、bind_tools 工具绑定、with_structured_output 结构化输出与流式事件
tags: [langchain, chat-model, base-chat-model, bind-tools, structured-output]
generated: { by: "reference_agent/trae-solo", at: 2026-08-23 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23 }
status: stable
stale_after: 2027-02-23
sources:
  - id: ref-po
    resource: /references/prompts-output.md
    title: 提示词、模型与输出解析源码信源
  - id: ref-msg
    resource: /references/messages-tools.md
    title: 消息与工具源码信源
---

# 聊天模型

`BaseChatModel`（`language_models/chat_models.py:284`）是所有聊天模型的抽象基类，继承自 `BaseLanguageModel[AIMessage]`。聊天模型接收消息列表（或字符串/PromptValue），返回 `AIMessage`。它是 Runnable 协议在模型层的核心实现，提供同步/异步/批量/流式四种执行模式，以及工具绑定、结构化输出等声明式能力。

## 类层级

```
Runnable(ABC, Generic[Input, Output])
└── RunnableSerializable(Serializable, Runnable)
    └── BaseLanguageModel(RunnableSerializable[LanguageModelInput, LanguageModelOutputVar], ABC)  base.py:181
        └── BaseChatModel(BaseLanguageModel[AIMessage], ABC)                                    chat_models.py:284
            ├── SimpleChatModel(BaseChatModel)                                                  chat_models.py:2657
            └── _ChatModelBinding(RunnableBinding)                                              chat_models.py:2568
```

## 输入输出类型

`language_models/base.py` 定义了类型别名：
- `LanguageModelInput = PromptValue | str | Sequence[MessageLikeRepresentation]`（第140行）
- `LanguageModelOutput = BaseMessage | str`（第143行）
- `LanguageModelOutputVar = TypeVar("LanguageModelOutputVar", AIMessage, str)`（第149行）

`BaseChatModel` 固定输出类型为 `AIMessage`（`OutputType` 属性，第457行）。

## BaseLanguageModel 基础字段

`BaseLanguageModel`（`base.py:181`）定义：

| 字段 | 类型 | 行号 | 说明 |
|---|---|---|---|
| `cache` | `BaseCache \| bool \| None` | 190 | 缓存配置，流式不支持缓存 |
| `verbose` | `bool` | 201 | 详细模式，默认全局设置 |
| `callbacks` | `Callbacks` | 204 | 回调（exclude） |
| `tags` | `list[str] \| None` | 207 | 标签（exclude） |
| `metadata` | `dict \| None` | 210 | 元数据（exclude） |
| `custom_get_token_ids` | `Callable[[str], list[int]] \| None` | 213 | 自定义 token 编码器 |

`model_post_init`（第222行）自动在 `metadata["lc_versions"]` 中记录 `langchain-core` 和 `langchain` 的版本号；partner 包通过 `_add_version(pkg, version)`（第253行）追加自身版本。

## BaseChatModel 字段

| 字段 | 类型 | 行号 | 说明 |
|---|---|---|---|
| `rate_limiter` | `BaseRateLimiter \| None` | 334 | 可选限流器 |
| `disable_streaming` | `bool \| Literal["tool_calling"]` | 337 | 禁用流式：`True` 始终禁用；`"tool_calling"` 仅绑工具时禁用；`False` 默认启用 |
| `output_version` | `str \| None` | 355 | AIMessage 内容格式版本：`"v0"` provider 格式、`"v1"` 标准化格式，可由环境变量 `LC_OUTPUT_VERSION` 设置 |

## 实现自定义聊天模型

自定义模型需实现以下成员（第323-330行文档表格）：

| 成员 | 必需 | 说明 |
|---|---|---|
| `_generate(messages, stop, run_manager, **kwargs)` | 是 | 核心同步生成逻辑，返回 `ChatResult` |
| `_llm_type`（属性） | 是 | 唯一标识模型类型，用于日志 |
| `_identifying_params`（属性） | 可选 | 模型参数表示，用于追踪 |
| `_stream(messages, stop, run_manager, **kwargs)` | 可选 | 实现原生流式 |
| `_agenerate(...)` | 可选 | 原生异步生成 |
| `_astream(...)` | 可选 | 原生异步流式 |

### SimpleChatModel

`SimpleChatModel`（第2657行）是更简单的基类，只需实现 `_call(messages, stop, run_manager, **kwargs) -> str`（第2679行抽象方法），框架自动将字符串包装为 `AIMessage`。

## 执行方法

| 方法 | 行号 | 输入 | 输出 |
|---|---|---|---|
| `invoke(input, config, *, stop, **kwargs)` | 475 | `LanguageModelInput` | `AIMessage` |
| `stream(input, config, *, stop, **kwargs)` | 727 | 同上 | `Iterator[AIMessageChunk]` |
| `stream_events(...)` | 1287 | 同上 | `Iterator[StreamEvent]` |
| `astream_events(...)` | 1361 | 同上 | `AsyncIterator[StreamEvent]` |
| `generate(messages, stop, callbacks, **kwargs)` | 1592 | `list[list[BaseMessage]]` | `LLMResult` |
| `generate_prompt(prompts, ...)` | 1869 | `list[PromptValue]` | `LLMResult` |
| `_convert_input(model_input)` | 461 | `LanguageModelInput` | `PromptValue` |

`_convert_input` 将 str 或消息表示统一转为 `PromptValue`，然后 `generate_prompt` 调用 `_generate` 完成实际推理。

### 流式事件

`astream_events(version="v2")` 产生的事件类型包括 `on_chat_model_start`、`on_chat_model_stream`、`on_chat_model_end`（第298行文档）。这是构建实时 UI 和流式处理的标准接口。

## 声明式方法

### bind_tools

`bind_tools(tools, *, tool_choice=None, **kwargs)`（第2366行）将工具绑定到模型，返回 `Runnable[LanguageModelInput, AIMessage]`：

```python
model_with_tools = model.bind_tools([get_weather, search_web])
result = model_with_tools.invoke("北京天气")
# result.tool_calls 包含工具调用请求
```

`tools` 参数接受序列，每个元素可以是 dict schema、Pydantic 类、Callable 或 `BaseTool`。基类抛出 `NotImplementedError`，由具体 partner 实现（如 OpenAI 将工具转为 function calling 格式）。

### with_structured_output

`with_structured_output(schema, *, include_raw=False, **kwargs)`（第2385行）返回一个 Runnable，输出按 schema 结构化：

```python
class Person(BaseModel):
    name: str
    age: int

structured_llm = model.with_structured_output(Person)
person = structured_llm.invoke("张三今年30岁")  # Person(name="张三", age=30)
```

`schema` 支持 OpenAI function/tool schema、JSON Schema、`TypedDict` 或 Pydantic 类。Pydantic 类时输出为该类实例并校验；否则输出 dict。`include_raw=True` 时返回 `{"raw": BaseMessage, "parsed": ..., "parsing_error": ...}`。基类抛出 `NotImplementedError`。

### bind

`bind(**kwargs)`（第2355行）重写了 `Runnable.bind`，返回 `_ChatModelBinding`（第2568行）而非通用 `RunnableBinding`，以保留 chat-model 特定的 `stream_events`/`astream_events` 类型重载。常用 kwargs 包括 `stop`、`temperature`、`tools` 等。

### 继承的装饰器方法

从 `Runnable` 继承：`with_retry`、`with_fallbacks`、`with_config`、`configurable_fields`、`configurable_alternatives`、`as_tool`。

## 输出内部表示

模型调用内部通过 `Generation`/`ChatGeneration` 表示结果：
- `ChatGeneration`（`outputs/chat_generation.py:17`）持有 `message: BaseMessage` 和 `text`，`set_text` 验证器从 message 同步 text。
- `ChatGenerationChunk`（第87行）用于流式，`message: BaseMessageChunk`，支持 `__add__` 合并。
- `ChatResult`（`outputs/chat_result.py`）包含 `generations: list[ChatGeneration]` 和 `llm_output`。

用户通常通过 Runnable 接口获取 `AIMessage`，不直接接触这些内部类；它们主要在 callbacks 和 tracing 中可见。

## token 计数

- `get_token_ids(text) -> list[int]`（`base.py:434`）：文本的 token ID 列表。
- `get_num_tokens(text) -> int`（第448行）：文本 token 数。
- `get_num_tokens_from_messages(messages) -> int`（第465行）：消息列表的 token 数。

## 代码示例

```python
from langchain_core.messages import HumanMessage, SystemMessage

# 1. 基本调用（model 为具体实现，如 ChatOpenAI）
messages = [
    SystemMessage("你是翻译官"),
    HumanMessage("把'hello'翻译成中文"),
]
ai_msg = model.invoke(messages)
print(ai_msg.text)

# 2. 流式
for chunk in model.stream(messages):
    print(chunk.text, end="", flush=True)

# 3. 绑定工具
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """查询城市天气"""
    return f"{city} 晴"

model_with_tools = model.bind_tools([get_weather])
response = model_with_tools.invoke("北京天气怎么样？")
if response.tool_calls:
    for tc in response.tool_calls:
        print(tc["name"], tc["args"])

# 4. 结构化输出
from pydantic import BaseModel
class Movie(BaseModel):
    title: str
    year: int
    genre: str

structured = model.with_structured_output(Movie)
movie = structured.invoke("推荐一部2024年的科幻电影")

# 5. with_retry / with_fallbacks
robust = model.with_retry(stop_after_attempt=3).with_fallbacks([backup_model])
```

## 相关概念

- [消息类型](/ai/langchain-ai/langchain/concepts/message-types) —— AIMessage 是输出，HumanMessage/SystemMessage 是输入
- [提示词系统](/ai/langchain-ai/langchain/concepts/prompt-system) —— ChatPromptValue 是输入桥梁
- [工具抽象](/ai/langchain-ai/langchain/concepts/tool-abstraction) —— bind_tools 接受 BaseTool
- [Runnable 协议](/ai/langchain-ai/langchain/concepts/runnable-protocol) —— BaseChatModel 是 RunnableSerializable
- [输出解析器](/ai/langchain-ai/langchain/concepts/output-parser) —— with_structured_output 的底层机制
