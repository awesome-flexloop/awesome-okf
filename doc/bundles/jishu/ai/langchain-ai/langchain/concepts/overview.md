---
type: concept
title: langchain-core 总览
description: langchain-core 是什么、核心抽象分层、Runnable 协议如何统御一切组件
tags: [langchain, overview, architecture]
generated: { by: "reference_agent/trae-solo", at: 2026-08-23 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23 }
status: stable
stale_after: 2027-02-23
sources:
  - id: ref-core
    resource: /references/core-abstractions.md
    title: 核心抽象源码信源
  - id: ref-msg
    resource: /references/messages-tools.md
    title: 消息与工具源码信源
  - id: ref-po
    resource: /references/prompts-output.md
    title: 提示词、模型与输出解析源码信源
  - id: ref-rc
    resource: /references/runnables-callbacks.md
    title: 回调、追踪与检索源码信源
---

# langchain-core 总览

`langchain-core` 是 LangChain Python 生态的基础包，定义了构建 LLM 应用所需的全部核心抽象和接口。它本身不包含任何具体模型厂商实现，只提供协议、数据结构和组合原语；具体的模型、向量库等实现由 `langchain-openai`、`langchain-anthropic` 等 partner 包提供。

- **版本**：1.6.1（见 `version.py`）
- **定位**：monorepo 中的 core 层，用户通常不直接感知，但所有上层组件都依赖它
- **核心依赖**：Pydantic v2、PyYAML、JSONPatch 等

## 核心设计理念

langchain-core 围绕一个统一协议——Runnable 协议——构建。所有组件（提示词、模型、输出解析器、检索器、工具）都是 `Runnable`，因此都自动具备：

- 同步 `invoke` / 异步 `ainvoke`
- 批量 `batch` / `abatch`
- 流式 `stream` / `astream`
- 事件流 `astream_events`
- 通过 `|` 运算符组合成链
- 统一的配置（`RunnableConfig`）、回调（callbacks）和追踪（tracing）传播

这种"一切皆 Runnable"的设计使得组件可以任意组合，且组合后的链自动继承全部执行模式。详见 Runnable 协议。

## 抽象分层

```
┌─────────────────────────────────────────────────┐
│  组合层  RunnableSequence / RunnableParallel    │  │ 管道、并行、分支
│          RunnableLambda / RunnableBinding        │  │ 函数适配、装饰器
├─────────────────────────────────────────────────┤
│  能力层  PromptTemplate / BaseChatModel          │  │ 提示词、聊天模型
│          BaseTool / BaseOutputParser             │  │ 工具、输出解析
│          BaseRetriever / VectorStore / Embeddings│  │ 检索、向量库
├─────────────────────────────────────────────────┤
│  数据层  BaseMessage (Human/AI/Tool/System)      │  │ 消息、工具调用
│          Document / Generation / PromptValue     │  │ 文档、生成结果
│          UsageMetadata / ContentBlock            │  │ 用量、多模态内容
├─────────────────────────────────────────────────┤
│  基座层  Runnable(ABC) / Serializable(Pydantic)  │  │ 执行协议、序列化
│          RunnableConfig / CallbackManager        │  │ 配置、回调横切
└─────────────────────────────────────────────────┘
```

### 基座层

- **`Runnable`**（`runnables/base.py:133`）：泛型抽象基类 `Generic[Input, Output]`，定义 `invoke` 等执行方法和 `|`/`pipe`/`bind`/`with_retry` 等组合原语。
- **`Serializable`**（`load/serializable.py:106`）：基于 Pydantic v2 的序列化基类，通过 `lc_id`/`lc_namespace`/`lc_secrets`/`lc_attributes` 实现声明式 JSON 序列化，默认不可序列化（opt-in）。
- **`RunnableConfig`**（`runnables/config.py:57`）：TypedDict，含 `tags`/`metadata`/`callbacks`/`max_concurrency`/`recursion_limit`/`configurable` 等字段，通过 ContextVar 自动向子组件传播。

### 数据层

- **消息体系**：`BaseMessage` 派生 `HumanMessage`、`SystemMessage`、`AIMessage`（含 `tool_calls`、`usage_metadata`）、`ToolMessage`（通过 `tool_call_id` 关联结果）。所有消息有对应的 `*Chunk` 变体支持流式拼接。`content_blocks` 属性将 provider 特定内容懒解析为统一的 `ContentBlock` 联合类型。详见 消息类型。
- **`Document`**（`documents/base.py:288`）：检索工作流的数据单元，含 `page_content: str`、`metadata`、`id`。注意它用于检索而非对话 I/O。
- **`Generation`/`ChatGeneration`**：模型输出的内部表示，`ChatGeneration` 持有 `BaseMessage`，最终映射为 `AIMessage`。
- **`PromptValue`**：提示词格式化结果，可 `to_string()` 或 `to_messages()`。

### 能力层

| 组件 | 基类 | 核心方法 | 概念文档 |
|---|---|---|---|
| 提示词 | `BasePromptTemplate` | `format`/`format_prompt` | 提示词系统 |
| 聊天模型 | `BaseChatModel` | `_generate`/`invoke`/`bind_tools` | 聊天模型 |
| 工具 | `BaseTool` | `_run`/`invoke` | 工具抽象 |
| 输出解析 | `BaseOutputParser` | `parse`/`parse_result` | 输出解析器 |
| 检索器 | `BaseRetriever` | `_get_relevant_documents` | 检索器与向量库 |
| 向量库 | `VectorStore` | `add_texts`/`similarity_search` | 检索器与向量库 |
| 嵌入 | `Embeddings` | `embed_documents`/`embed_query` | 检索器与向量库 |

### 组合层

- **`RunnableSequence`**：顺序执行，`a | b | c` 构造，前一个的输出是后一个的输入。
- **`RunnableParallel`**：并行执行，`{"key": runnable}` 字典构造，所有分支接收相同输入。
- **`RunnableLambda`**：将任意 Python 函数包装为 Runnable。
- **`RunnableBinding`**：`bind`/`with_config` 的产物，持有 bound runnable + kwargs + config。
- **装饰器方法**：`with_retry`、`with_fallbacks`、`with_listeners`、`map`、`assign`、`as_tool` 等返回新的包装 Runnable。

### 横切层

- **Callbacks**：`BaseCallbackHandler` 通过多 Mixin 组合定义 `on_<component>_start/end/error` 生命周期方法；`CallbackManager`/`AsyncCallbackManager` 两棵独立的树管理 handler 传播。详见 回调系统。
- **Tracers**：`BaseTracer`/`AsyncBaseTracer` 继承 callback handler，将事件构建为 `Run` 对象树并持久化。

## 典型 LCEL 链

LangChain Expression Language（LCEL）即基于 Runnable 协议的声明式链构造：

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("讲一个关于 {topic} 的笑话")
# model 来自具体 partner 包，如 langchain_openai.ChatOpenAI
chain = prompt | model | StrOutputParser()

chain.invoke({"topic": "程序员"})
```

`prompt`、`model`、`StrOutputParser` 都是 Runnable，`|` 构造 `RunnableSequence`，整条链自动支持 `ainvoke`/`batch`/`stream`。

## 序列化与版本追踪

所有核心类继承 `Serializable`，可通过 `to_json()` 序列化为包含 `lc_id`（类路径）和 `kwargs` 的 JSON 结构。`BaseLanguageModel.model_post_init` 会在 `metadata["lc_versions"]` 中自动记录 `langchain-core`、`langchain` 和 partner 包的版本号，便于追踪每次调用的软件版本。

## 进一步阅读

- Runnable 协议 —— 执行接口、组合原语、配置传播
- 消息类型 —— BaseMessage 体系、ContentBlock、ToolCall
- 提示词系统 —— PromptTemplate、ChatPromptTemplate
- 聊天模型 —— BaseChatModel、bind_tools、结构化输出
- 工具抽象 —— BaseTool、@tool、StructuredTool
- 回调系统 —— Handler、Manager、Tracer
- 检索器与向量库 —— BaseRetriever、VectorStore、Embeddings
- 输出解析器 —— BaseOutputParser、parse_result
