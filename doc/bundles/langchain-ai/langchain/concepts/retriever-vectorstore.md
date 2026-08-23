---
type: concept
title: 检索器与向量库
description: BaseRetriever 检索协议、VectorStore 向量存储抽象、Embeddings 嵌入接口与 as_retriever 桥接机制
tags: [langchain, retriever, vectorstore, embeddings, rag]
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

# 检索器与向量库

检索（Retrieval）是 RAG（Retrieval-Augmented Generation）的核心环节。langchain-core 定义了三个相互协作的抽象：`Embeddings`（将文本转为向量）、`VectorStore`（存储和搜索向量）、`BaseRetriever`（根据查询返回相关文档）。三者都是独立抽象，`VectorStore` 通过 `as_retriever()` 桥接为 `BaseRetriever`。

## Embeddings 嵌入接口

`Embeddings`（`embeddings/embeddings.py:8`）是抽象基类，定义两个核心方法：

| 方法 | 行号 | 说明 |
|---|---|---|
| `embed_documents(texts: list[str]) -> list[list[float]]`（抽象） | 37 | 批量嵌入文档文本 |
| `embed_query(text: str) -> list[float]`（抽象） | 48 | 嵌入查询文本 |
| `aembed_documents(texts)` | 58 | 异步文档嵌入（默认线程池） |
| `aembed_query(text)` | 69 | 异步查询嵌入（默认线程池） |

文档嵌入和查询嵌入分开设计，因为某些模型对查询和文档使用不同的嵌入策略（如对称 vs 非对称嵌入）。两者默认返回相同维度的向量。

## Document 数据单元

`Document`（`documents/base.py:288`）继承 `BaseMedia`（继承 `Serializable`），是检索工作流的基本数据单元：

| 字段 | 类型 | 行号 | 说明 |
|---|---|---|---|
| `page_content` | `str` | 306 | 文本内容（必填，位置参数） |
| `metadata` | `dict` | 继承 | 元数据（来源、页码等） |
| `id` | `str \| None` | 继承 | 文档 ID |
| `type` | `Literal["Document"]` | 309 | 序列化鉴别字段 |

注意文档明确说明：`Document` 用于**检索工作流**，而非对话 I/O；向 LLM 发送文本应使用消息类型（`HumanMessage` 等）。`get_lc_namespace` 返回 `["langchain", "schema", "document"]`。

`Blob`（`documents/base.py:59`）是二进制大对象抽象，支持 `as_string`/`as_bytes`/`as_bytes_io` 读取，通过 `from_path`/`from_data` 构造，用于文档加载器处理二进制文件。

## BaseRetriever 检索协议

`BaseRetriever`（`retrievers.py:55`）定义为：

```python
class BaseRetriever(RunnableSerializable[RetrieverInput, RetrieverOutput], ABC):
```

输入为字符串查询，输出为 `list[Document]`。它是 Runnable，因此支持 `invoke`/`ainvoke`/`batch`/`stream` 和管道组合。

### 字段

| 字段 | 行号 | 说明 |
|---|---|---|
| `tags: list[str] \| None` | 125 | 标签，关联每次检索调用 |
| `metadata: dict \| None` | 135 | 元数据，传给回调 |

### 核心方法

| 方法 | 行号 | 说明 |
|---|---|---|
| `invoke(input: str, config=None) -> list[Document]` | 179 | 同步检索入口 |
| `ainvoke(input, config)` | 237 | 异步检索入口 |
| `_get_relevant_documents(query, *, run_manager)`（抽象） | 298 | 子类实现的同步检索逻辑 |
| `_aget_relevant_documents(query, *, run_manager)` | 311 | 异步检索逻辑（默认抛 NotImplementedError） |
| `_get_ls_params(**kwargs)` | 167 | LangSmith 追踪参数，从类名推导检索器名 |

### 子类自动适配

`__init_subclass__`（第146行）在子类创建时自动：
1. 检查 `_get_relevant_documents` 签名是否含 `run_manager` 参数，设置 `_new_arg_supported`。
2. 如果子类未重写 `_aget_relevant_documents`，自动生成一个在线程池中调用同步版本的 async 实现。
3. 检查是否有额外参数，设置 `_expects_other_args`。

这意味着自定义检索器只需实现 `_get_relevant_documents`，即可自动获得异步支持。

## VectorStore 向量库

`VectorStore`（`vectorstores/base.py:43`）是抽象基类，定义向量存储的标准接口。注意它**不继承 Runnable**，而是通过 `as_retriever()` 适配。

### 写入方法

| 方法 | 行号 | 说明 |
|---|---|---|
| `add_texts(texts, metadatas, *, ids, **kwargs) -> list[str]` | 46 | 添加文本，默认委托 `add_documents` |
| `add_documents(documents, **kwargs) -> list[str]` | 234 | 添加 Document 列表 |
| `aadd_texts` / `aadd_documents` | 185 / 265 | 异步版本 |
| `delete(ids, **kwargs) -> bool \| None` | 108 | 按 ID 删除（子类实现） |
| `get_by_ids(ids) -> list[Document]` | 122 | 按 ID 获取 |
| `from_texts(texts, ...)`（抽象类方法） | 848 | 从文本构造实例 |
| `from_documents(documents, ...)` | 787 | 从 Document 构造 |

### 搜索方法

| 方法 | 行号 | 说明 |
|---|---|---|
| `similarity_search(query, k=4, **kwargs) -> list[Document]`（抽象） | 361 | 相似度搜索 |
| `similarity_search_with_score(query, **kwargs)` | 417 | 带距离分数 |
| `similarity_search_with_relevance_scores(query, k, **kwargs)` | 506 | 带相关性分数 [0,1] |
| `max_marginal_relevance_search(query, k, fetch_k, lambda_mult, **kwargs)` | 659 | MMR 多样性搜索 |
| `search(query, search_type, **kwargs)` | 293 | 统一搜索入口 |

`search` 方法根据 `search_type` 分派：
- `"similarity"` → `similarity_search`
- `"mmr"` → `max_marginal_relevance_search`
- `"similarity_score_threshold"` → `similarity_search_with_relevance_scores`（带阈值过滤）

### 相关性分数函数

向量距离到相关性分数 [0,1] 的转换由子类选择：
- `_euclidean_relevance_score_fn(distance)`（第376行）：`1.0 - distance / sqrt(2)`
- `_cosine_relevance_score_fn(distance)`（第391行）：`1.0 - distance`
- `_max_inner_product_relevance_score_fn(distance)`（第396行）：正距离用 `1-d`，负距离取反
- `_select_relevance_score_fn()`（第403行）：子类实现，选择正确的转换函数

### embeddings 属性

`embeddings` 属性（第100行）返回 `Embeddings | None`，默认返回 `None` 并记录 debug 日志。支持嵌入的向量库 override 此属性。

## as_retriever 桥接

`as_retriever(**kwargs) -> VectorStoreRetriever`（第905行）是 VectorStore 到 BaseRetriever 的桥接：

```python
def as_retriever(self, **kwargs):
    tags = kwargs.pop("tags", None) or [*self._get_retriever_tags()]
    return VectorStoreRetriever(vectorstore=self, tags=tags, **kwargs)
```

`search_type` 和 `search_kwargs` 通过 kwargs 传入：

| 参数 | 说明 |
|---|---|
| `search_type` | `"similarity"`（默认）、`"mmr"`、`"similarity_score_threshold"` |
| `search_kwargs.k` | 返回文档数，默认 4 |
| `search_kwargs.score_threshold` | 相似度阈值（score_threshold 模式） |
| `search_kwargs.fetch_k` | MMR 候选数，默认 20 |
| `search_kwargs.lambda_mult` | MMR 多样性，0 最大多样、1 最小，默认 0.5 |
| `search_kwargs.filter` | 元数据过滤 |

### VectorStoreRetriever

`VectorStoreRetriever`（第964行）继承 `BaseRetriever`：
- 持有 `vectorstore: VectorStore`。
- `validate_search_type`（第988行）类方法校验 search_type 取值。
- `_get_relevant_documents`（第1040行）委托 `vectorstore.search(query, search_type, **search_kwargs)`。
- `_aget_relevant_documents`（第1061行）委托异步 `asearch`。

## RAG 典型流程

```
Document 列表
    │ add_documents
    ▼
VectorStore（内部用 Embeddings 向量化）
    │ as_retriever → VectorStoreRetriever
    ▼
BaseRetriever.invoke(query) → list[Document]
    │ （作为 Runnable 接入链）
    ▼
prompt | model | parser
```

## 代码示例

```python
from langchain_core.documents import Document

# 1. 构造文档
docs = [
    Document(page_content="巴黎是法国首都", metadata={"source": "wiki"}),
    Document(page_content="柏林是德国首都", metadata={"source": "wiki"}),
]

# 2. 自定义检索器
from langchain_core.retrievers import BaseRetriever

class SimpleRetriever(BaseRetriever):
    docs: list[Document]
    k: int = 2

    def _get_relevant_documents(self, query, *, run_manager=None):
        return self.docs[: self.k]

retriever = SimpleRetriever(docs=docs)
results = retriever.invoke("法国首都")

# 3. 向量库检索（以具体实现为例，如 InMemoryVectorStore）
# vectorstore = InMemoryVectorStore.from_documents(docs, embedding=embeddings)
# retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 3})
# results = retriever.invoke("首都")

# 4. 作为 Runnable 接入链
# chain = prompt | model | StrOutputParser()
# rag_chain = RunnablePassthrough.assign(context=retriever) | prompt | model | parser
```

## 相关概念

- [总览](/langchain-ai/langchain/concepts/overview) —— 检索器与向量库在能力层中的位置
- [Runnable 协议](/langchain-ai/langchain/concepts/runnable-protocol) —— BaseRetriever 是 RunnableSerializable
- [回调系统](/langchain-ai/langchain/concepts/callback-system) —— 检索触发 on_retriever_start/end
- [文档与加载器](/langchain-ai/langchain/concepts/document-loader) —— Document 与 Blob 的数据模型
