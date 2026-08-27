---
type: example
title: RAG 检索增强生成
description: 使用 Document、InMemoryVectorStore、DeterministicFakeEmbedding 与 as_retriever 构建端到端 RAG 链
tags: [langchain, rag, retriever, vectorstore, embeddings]
generated: { by: "reference_agent/trae-solo", at: 2026-08-23 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23 }
status: stable
stale_after: 2027-02-23
sources:
  - id: ref-rc
    resource: /references/runnables-callbacks.md
    title: 回调、追踪与检索源码信源
  - id: ref-po
    resource: /references/prompts-output.md
    title: 提示词、模型与输出解析源码信源
---

# RAG 检索增强生成

本示例演示检索增强生成（Retrieval-Augmented Generation）的核心流程：准备文档 → 存入向量库 → 转为检索器 → 接入 LCEL 链。示例使用 langchain-core 内置的 `InMemoryVectorStore` 和 `DeterministicFakeEmbedding`，无需外部服务或 API key；真实场景替换为 Chroma、Pinecone 等向量库和真实嵌入模型。

## 前置条件

- Python ≥ 3.10
- 已安装 `langchain-core`（含 `numpy`，`DeterministicFakeEmbedding` 依赖）

## 第一步：准备文档

```python
from langchain_core.documents import Document

documents = [
    Document(
        page_content="LangChain 是一个用于构建 LLM 应用的框架，核心抽象是 Runnable 协议。",
        metadata={"source": "intro", "section": 1},
    ),
    Document(
        page_content="Runnable 协议统一了 invoke、batch、stream 四种执行模式，所有组件都实现该协议。",
        metadata={"source": "runnable", "section": 2},
    ),
    Document(
        page_content="向量库通过 similarity_search 检索与查询语义最相似的文档，支持 MMR 多样性搜索。",
        metadata={"source": "vectorstore", "section": 3},
    ),
    Document(
        page_content="提示词模板使用 format 方法将变量填入模板，ChatPromptTemplate 产生消息列表。",
        metadata={"source": "prompt", "section": 4},
    ),
]
```

`Document`（`documents/base.py:288`）含 `page_content: str`、`metadata: dict`、`id`，是检索工作流的数据单元。

## 第二步：构建向量库

```python
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.embeddings import DeterministicFakeEmbedding

# 使用确定性假嵌入（仅用于演示，生产环境替换为真实嵌入模型）
embeddings = DeterministicFakeEmbedding(size=64)

# 从文档构造内存向量库（内部对每个文档调用 embeddings.embed_documents）
vectorstore = InMemoryVectorStore.from_documents(
    documents,
    embedding=embeddings,
)
```

`InMemoryVectorStore`（`vectorstores/in_memory.py:34`）继承 `VectorStore`：
- 构造函数 `__init__(self, embedding: Embeddings)`（第161行）。
- 类方法 `from_documents`（第787行继承自 `VectorStore`）批量添加文档。
- `embeddings` 属性（第174行）返回嵌入模型。

> **注意**：`DeterministicFakeEmbedding` 是玩具模型，基于文本哈希和正态分布生成向量，不具备真实语义。生产环境应使用 `langchain-openai.OpenAIEmbeddings` 等真实嵌入。

## 第三步：转为检索器

```python
# 基本相似度检索，返回 top 2
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# MMR 多样性检索
mmr_retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 2, "fetch_k": 4, "lambda_mult": 0.5},
)

# 带分数阈值的检索
threshold_retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 2, "score_threshold": 0.5},
)
```

`as_retriever`（`vectorstores/base.py:905`）返回 `VectorStoreRetriever`（第964行），它继承 `BaseRetriever`。`search_type` 支持：
- `"similarity"`（默认）：相似度搜索
- `"mmr"`：最大边际相关性，平衡相关性与多样性
- `"similarity_score_threshold"`：仅返回超过阈值的文档

## 第四步：检索文档

```python
# 检索器是 Runnable，输入 str 输出 list[Document]
results = retriever.invoke("Runnable 协议支持哪些执行模式？")

for doc in results:
    print(f"[{doc.metadata['source']}] {doc.page_content}")
```

`BaseRetriever.invoke`（`retrievers.py:179`）调用子类的 `_get_relevant_documents`。`VectorStoreRetriever._get_relevant_documents`（第1040行）委托 `vectorstore.search(query, search_type, **search_kwargs)`。

也可直接用向量库搜索：

```python
docs = vectorstore.similarity_search("什么是提示词模板？", k=1)
docs_with_scores = vectorstore.similarity_search_with_score("向量库怎么检索？", k=2)
```

## 第五步：接入 LCEL 链

将检索器作为链的一环，用 `RunnablePassthrough.assign` 将检索结果注入输入：

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.language_models.fake_chat_models import FakeListChatModel

# 构造提示词
prompt = ChatPromptTemplate.from_template(
    "基于以下上下文回答问题。\n\n"
    "上下文：\n{context}\n\n"
    "问题：{question}\n\n"
    "回答："
)

# 假模型（生产环境替换为真实 ChatModel）
model = FakeListChatModel(responses=[
    "Runnable 协议统一了 invoke、batch、stream 三种核心执行模式及其异步版本。",
])

# 格式化检索结果为文本
def format_docs(docs):
    return "\n".join(f"- {d.page_content}" for d in docs)

# 构建 RAG 链
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

answer = rag_chain.invoke("Runnable 协议支持哪些执行模式？")
print(answer)
```

### 数据流说明

1. 输入 `"Runnable 协议支持哪些执行模式？"` 传入字典构造的 `RunnableParallel`。
2. `context` 分支：`retriever | format_docs` 将查询转为相关文档文本。
3. `question` 分支：`RunnablePassthrough()` 透传原始查询。
4. 字典输出传给 `prompt` 格式化为消息列表。
5. `model` 生成回答（`AIMessage`）。
6. `StrOutputParser` 提取文本。

## 异步与流式

```python
import asyncio

async def main():
    # 异步检索
    results = await retriever.ainvoke("什么是向量库？")
    print(f"检索到 {len(results)} 个文档")

    # 流式生成
    async for chunk in rag_chain.astream("提示词模板怎么用？"):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

`BaseRetriever` 自动提供 `ainvoke`（`retrievers.py:237`）；如果子类未实现 `_aget_relevant_documents`，`__init_subclass__`（第146行）自动包装为在线程池中调用同步版本。

## 添加更多文档

```python
new_docs = [
    Document(page_content="BaseTool 是工具基类，通过 @tool 装饰器创建工具。",
             metadata={"source": "tools"}),
]
ids = vectorstore.add_documents(new_docs)
print(f"添加了 {len(ids)} 个文档，ID: {ids}")

# 按 ID 删除
vectorstore.delete(ids)
```

`add_documents`（`vectorstores/base.py:234`）返回文档 ID 列表。`delete`（第108行）按 ID 删除。

## 自定义检索器

除了 `as_retriever`，也可直接继承 `BaseRetriever`：

```python
from langchain_core.retrievers import BaseRetriever

class KeywordRetriever(BaseRetriever):
    docs: list[Document]
    k: int = 3

    def _get_relevant_documents(self, query, *, run_manager=None):
        keywords = query.lower().split()
        scored = []
        for doc in self.docs:
            score = sum(1 for kw in keywords if kw in doc.page_content.lower())
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: -x[0])
        return [d for _, d in scored[: self.k]]

kw_retriever = KeywordRetriever(docs=documents, k=2)
results = kw_retriever.invoke("Runnable 执行模式")
```

只需实现 `_get_relevant_documents`，自动获得 `invoke`/`ainvoke`/`batch`/`stream` 全套 Runnable 能力。

## 相关概念

- 检索器与向量库
- 文档与加载器
- Runnable 协议
- 提示词系统
- 输出解析器
