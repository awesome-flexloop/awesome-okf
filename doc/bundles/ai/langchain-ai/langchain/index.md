---
type: bundle
okf_version: "0.2"
scope: langchain
name: langchain
version: "1.6.1"
source: https://github.com/langchain-ai/langchain
description: langchain-core——LangChain Python 的核心抽象层，定义 Runnable 协议、消息体系、提示词、聊天模型、工具、回调、检索器与向量库等基础接口，所有上层组件和 partner 集成都依赖此包
---

# langchain-core

**langchain-core** 是 LangChain Python 生态的基础包，定义了构建 LLM 应用所需的全部核心抽象和接口。它本身不包含任何具体模型厂商实现，只提供协议、数据结构和组合原语；具体的模型、向量库等实现由 `langchain-openai`、`langchain-anthropic` 等 partner 包提供。

- **版本**：1.6.1
- **源码**：`libs/core/langchain_core/`
- **核心依赖**： Pydantic v2、PyYAML、JSONPatch
- **定位**：monorepo 中的 core 层，用户通常不直接感知，但所有上层组件都依赖它

## 核心理念：一切皆 Runnable

langchain-core 围绕统一的 **Runnable 协议**构建。所有组件（提示词、模型、输出解析器、检索器、工具）都是 `Runnable`，自动具备同步/异步/批量/流式四种执行模式，并可通过 `|` 运算符声明式组合成链。组合后的链同样自动支持全部执行模式和统一的配置、回调、追踪传播。

## 核心特性

- **Runnable 协议**：统一的 `invoke`/`ainvoke`/`batch`/`stream`/`astream_events` 接口，子类只需实现 `invoke` 即可获得全套能力。
- **LCEL 组合**：`RunnableSequence`（`|` 管道）、`RunnableParallel`（字典并行）、`RunnableLambda`（函数适配）等原语，配合 `bind`/`with_retry`/`with_fallbacks`/`as_tool` 装饰器链。
- **标准化消息体系**：`HumanMessage`/`SystemMessage`/`AIMessage`/`ToolMessage` 四种角色，`AIMessage` 标准化 `tool_calls` 和 `usage_metadata`，`ContentBlock` 支持多模态内容。
- **工具抽象**：`BaseTool`/`StructuredTool` + `@tool` 装饰器，自动从类型注解推断参数 schema，支持错误处理和依赖注入。
- **聊天模型接口**：`BaseChatModel` 定义 `_generate`/`_stream`，提供 `bind_tools`（工具调用）和 `with_structured_output`（结构化输出）。
- **回调与追踪**：`BaseCallbackHandler` 通过 Mixin 组合定义生命周期事件，`CallbackManager`/`AsyncCallbackManager` 双树传播，`BaseTracer` 构建 Run 追踪树。
- **检索抽象**：`Embeddings`（文本向量化）、`VectorStore`（存储与搜索）、`BaseRetriever`（检索协议），通过 `as_retriever` 桥接。
- **声明式序列化**：`Serializable` 基类基于 Pydantic，通过 `lc_id`/`lc_secrets`/`lc_attributes` 实现跨版本 JSON 序列化与密钥脱敏。

## 快速开始

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

# 用 RunnableLambda 模拟模型（真实场景用 ChatOpenAI 等）
model = RunnableLambda(lambda x: "装饰器是 Python 的语法糖，用于扩展函数功能。")

# LCEL 链：提示词 | 模型 | 解析器
prompt = ChatPromptTemplate.from_template("解释什么是 {topic}")
chain = prompt | model | StrOutputParser()

result = chain.invoke({"topic": "Python 装饰器"})
```

## 文档导航

### 核心概念

- [总览](/ai/langchain-ai/langchain/concepts/overview) — 核心抽象分层与架构概览
- [Runnable 协议](/ai/langchain-ai/langchain/concepts/runnable-protocol) — 执行接口、组合原语、装饰器链与配置传播
- [消息类型体系](/ai/langchain-ai/langchain/concepts/message-types) — BaseMessage、AIMessage、ToolMessage、ContentBlock
- [工具抽象](/ai/langchain-ai/langchain/concepts/tool-abstraction) — BaseTool、StructuredTool、@tool、错误处理
- [提示词系统](/ai/langchain-ai/langchain/concepts/prompt-system) — PromptTemplate、ChatPromptTemplate、PromptValue
- [聊天模型](/ai/langchain-ai/langchain/concepts/chat-model) — BaseChatModel、bind_tools、结构化输出
- [输出解析器](/ai/langchain-ai/langchain/concepts/output-parser) — BaseOutputParser、parse_result
- [回调系统](/ai/langchain-ai/langchain/concepts/callback-system) — Handler、Manager、Tracer
- [检索器与向量库](/ai/langchain-ai/langchain/concepts/retriever-vectorstore) — BaseRetriever、VectorStore、Embeddings
- [文档与加载器](/ai/langchain-ai/langchain/concepts/document-loader) — Document、Blob、BaseLoader

### 信源参考

- [核心抽象源码信源](/ai/langchain-ai/langchain/references/core-abstractions) — Runnable、Serializable、RunnableConfig
- [消息与工具源码信源](/ai/langchain-ai/langchain/references/messages-tools) — 消息体系与工具抽象
- [提示词、模型与输出解析源码信源](/ai/langchain-ai/langchain/references/prompts-output) — Prompts、ChatModel、OutputParser、Document
- [回调、追踪与检索源码信源](/ai/langchain-ai/langchain/references/runnables-callbacks) — Callbacks、Tracers、Retriever、VectorStore

### 使用示例

- [LCEL 基础链](/ai/langchain-ai/langchain/examples/basic-lcel-chain) — 第一条链：提示词 → 模型 → 解析器
- [工具调用](/ai/langchain-ai/langchain/examples/tool-calling) — 工具定义、调用与结果回传完整流程
- [RAG 检索增强生成](/ai/langchain-ai/langchain/examples/rag-retrieval) — 文档入库、检索、接入链

## 目录结构

```
langchain/
├── spec/
│   ├── facts.md           # 源码事实验证清单（F-lc-001~073）
│   └── insights.md        # 架构洞察四元组
├── concepts/              # 核心概念（10 篇）
├── references/            # 源码信源登记（4 篇）
├── examples/              # 使用示例（3 篇）
├── log.md                 # 变更日志
└── index.md               # 本文件
```

## 相关生态

| 包 | 关系 |
|---|---|
| `langchain-openai` | OpenAI 聊天/嵌入模型实现 |
| `langchain-anthropic` | Anthropic Claude 模型实现 |
| `langchain-text-splitters` | 文档切分工具（`RecursiveCharacterTextSplitter`） |
| `langchain` (classic) | 高层 Agent/Chain 实现（legacy） |

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
