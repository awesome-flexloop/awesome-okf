---
type: bundle
okf_version: "0.2"
scope: langchain-mongodb
name: langchain-mongodb
version: "0.11.0"
source: https://github.com/langchain-ai/langchain-mongodb
description: langchain-mongodb——LangChain 官方 MongoDB 集成包，在 MongoDB Atlas 上统一提供向量搜索、全文搜索、混合检索、LLM 缓存、聊天历史和文档存储能力
---

# langchain-mongodb

**langchain-mongodb** 是 LangChain 官方维护的 MongoDB 集成包（v0.11.0）。它将 MongoDB Atlas 的 Vector Search（HNSW）、Atlas Search（BM25）、原生 $rerank 等搜索能力与 LangChain 的 VectorStore、BaseCache、BaseChatMessageHistory、BaseStore、RecordManager、BaseRetriever 等核心抽象无缝对接，使开发者可以在同一个全托管数据库平台上完成 RAG 应用的全部数据持久化和检索需求。

- **版本**：0.11.0
- **Python 要求**：≥ 3.11
- **核心依赖**：langchain-core ≥ 1.2.5、pymongo ≥ 4.6.1、pymongo-search-utils ≥ 0.3.0、numpy ≥ 1.26
- **许可证**：MIT
- **Monorepo 组成**：核心包、langchain-mongodb-deepagents-vfs、langgraph-checkpoint-mongodb、langgraph-store-mongodb

## 核心特性

- **Atlas Vector Search**：基于 HNSW 算法的向量相似度搜索，支持 cosine/euclidean/dotProduct 三种相似度函数，分数归一化到 [0,1]。
- **双嵌入模式**：客户端 Embeddings（应用层生成向量）和 Atlas Auto-Embeddings（服务端自动嵌入），通过类型系统严格区分。
- **五种检索器**：向量检索、BM25 全文检索、RRF 混合检索、父文档检索、自查询检索（LLM 推导过滤器）。
- **原生重排序**：支持 MongoDB 8.3+ 的 `$rerank` 阶段（Voyage AI 模型），可在向量/全文/混合/父文档检索中启用。
- **双层缓存**：`MongoDBCache`（精确匹配）和 `MongoDBAtlasSemanticCache`（语义相似度匹配，多继承复用 VectorStore）。
- **聊天历史持久化**：每条消息独立文档模型，支持 `history_size` 滑动窗口，字段名可自定义。
- **自动索引管理**：构造时自动创建向量索引、全文索引、复合索引，支持轮询等待 READY 状态。
- **记录管理器**：`MongoDBRecordManager` 实现 LangChain indexing API，使用服务器时间避免时钟漂移。
- **Agent Toolkit**：四个数据库工具（查询、表信息、列表、查询校验）配合 LangGraph ReAct agent。

## 快速开始

```python
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings

vectorstore = MongoDBAtlasVectorSearch.from_connection_string(
    connection_string="mongodb+srv://...",
    namespace="mydb.articles",
    embedding=OpenAIEmbeddings(),
    index_name="vector_index",
)

from langchain_core.documents import Document

vectorstore.add_documents([
    Document(page_content="MongoDB Atlas 支持向量搜索", metadata={"category": "db"}),
])

results = vectorstore.similarity_search("向量搜索", k=1)
```

## 文档导航

### 核心概念

- [总览](/ai/langchain-ai/langchain-mongodb/concepts/overview) — 项目定位、核心组件架构、平台要求、Monorepo 结构
- [向量存储架构](/ai/langchain-ai/langchain-mongodb/concepts/vector-store) — 双嵌入模式、聚合管道、MMR、索引管理、五种检索器
- [缓存与聊天历史](/ai/langchain-ai/langchain-mongodb/concepts/chat-history-cache) — 精确缓存、语义缓存、一消息一文档模型

### API 参考

- [核心 API 参考](/ai/langchain-ai/langchain-mongodb/references/api) — 所有公共类的构造函数、方法签名与参数说明

### 使用示例

- [基础使用示例](/ai/langchain-ai/langchain-mongodb/examples/basic-usage) — 向量存储 CRUD、聊天历史、缓存、检索器、RAG 链

### 规范文档

- [事实清单](/ai/langchain-ai/langchain-mongodb/spec/facts) — 源码验证的编号事实（F-001 ~ F-079）
- [深度洞察](/ai/langchain-ai/langchain-mongodb/spec/insights) — 聚合管道引擎、双嵌入模式、LangChain 契约映射

## 目录结构

```
langchain-mongodb/
├── spec/
│   ├── facts.md           # 源码事实验证清单
│   └── insights.md        # 设计决策与架构洞察
├── concepts/              # 核心概念（3 篇）
│   ├── overview.md
│   ├── vector-store.md
│   └── chat-history-cache.md
├── references/            # API 参考
│   └── api.md
├── examples/              # 使用示例
│   └── basic-usage.md
├── log.md                 # 变更日志
└── index.md               # 本文件
```

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
