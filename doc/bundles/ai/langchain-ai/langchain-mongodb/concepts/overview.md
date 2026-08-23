---
type: concept
scope: langchain-mongodb
name: overview
version: "0.11.0"
source: https://github.com/langchain-ai/langchain-mongodb
description: langchain-mongodb 总览——MongoDB 与 LangChain 的全栈集成包
---

# langchain-mongodb 总览

## 什么是 langchain-mongodb

`langchain-mongodb` 是 LangChain 官方维护的 MongoDB 集成包，它将 MongoDB Atlas 的向量搜索、全文搜索、缓存、聊天历史等能力无缝接入 LangChain 生态。

- **版本**：0.11.0
- **Python 要求**：≥ 3.11
- **核心依赖**：`langchain-core>=1.2.5`、`pymongo>=4.6.1`、`pymongo-search-utils>=0.3.0`、`numpy>=1.26`
- **许可证**：MIT（仓库根 LICENSE）

该包的核心价值主张是**在一个统一的全托管平台上同时存储运营数据、元数据和向量嵌入**，无需在数据库之外维护独立的向量搜索系统。

## 解决的问题

构建 RAG（检索增强生成）应用时，开发者通常需要组合多个基础设施：

1. **向量数据库**：存储嵌入向量，执行相似度搜索
2. **文档数据库**：存储原始文档和元数据
3. **缓存层**：缓存 LLM 响应以降低成本和延迟
4. **会话存储**：持久化聊天历史
5. **搜索引擎**：支持关键词匹配和混合检索

langchain-mongodb 通过 MongoDB Atlas 的 Vector Search 和 Search 能力，在**同一个数据库集合**中提供以上所有能力，减少了基础设施复杂度和数据同步问题。

## 核心组件架构

```
┌─────────────────────────────────────────────────────┐
│                   LangChain 应用层                     │
│  Chain / Agent / Retriever / ChatModel / Memory     │
└──────┬──────┬──────┬──────┬──────┬──────┬───────────┘
       │      │      │      │      │      │
       ▼      ▼      ▼      ▼      ▼      ▼
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│VectorStore│  Cache   │ChatHistory│RecordMgr │ DocStore │
│          │(精确/语义) │          │          │(KV)      │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘
     │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────┐
│            MongoDB Atlas Collection(s)               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐  │
│  │$vector  │ │$search  │ │$rerank  │ │CRUD/Index│  │
│  │Search   │ │(BM25)   │ │(8.3+)   │ │          │  │
│  └─────────┘ └─────────┘ └─────────┘ └──────────┘  │
└─────────────────────────────────────────────────────┘
```

## 顶层公共 API

包的 `__init__.py` 仅导出四个核心类：

| 类 | 用途 |
|---|---|
| `MongoDBAtlasVectorSearch` | 向量存储，支持相似度/MMR/混合搜索 |
| `MongoDBChatMessageHistory` | 聊天消息历史持久化 |
| `MongoDBCache` | 精确匹配的 LLM 响应缓存 |
| `MongoDBAtlasSemanticCache` | 语义相似度 LLM 缓存 |

更多组件通过子模块导入：
- `langchain_mongodb.retrievers` — 五种检索器
- `langchain_mongodb.indexes.MongoDBRecordManager` — 文档索引管理器
- `langchain_mongodb.docstores.MongoDBDocStore` — KV 文档存储
- `langchain_mongodb.agent_toolkit` — MongoDB Agent 工具包

## 关键设计特征

### 1. 聚合管道为核心

所有搜索逻辑都构建为 MongoDB 聚合管道（Aggregation Pipeline），在 Atlas 服务端执行。这包括向量搜索、全文搜索、RRF 混合融合、$rerank 重排序、$lookup 父子文档关联等。详见 [向量存储架构](/ai/langchain-ai/langchain-mongodb/concepts/vector-store)。

### 2. 双嵌入模式

支持**客户端嵌入**（传入 Embeddings 实例）和 **Atlas Auto-Embedding**（传入模型名称字符串，由 Atlas 服务端生成嵌入）。两种模式在类型层面严格区分，详见 [架构洞察](/ai/langchain-ai/langchain-mongodb/spec/insights)。

### 3. 自动索引管理

VectorStore、Cache、ChatMessageHistory、各 Retriever 在构造时自动创建所需的数据库索引，并支持等待索引就绪（轮询 status=READY）。

### 4. 同步/异步双支持

VectorStore 的异步方法（`adelete`、`amax_marginal_relevance_search_by_vector` 等）通过 `run_in_executor` 包装同步方法实现。RecordManager 也提供完整的异步 API。

## Monorepo 结构

仓库 `libs/` 目录下包含四个独立包：

| 包 | 用途 |
|---|---|
| `langchain-mongodb` | 核心集成（本文档焦点） |
| `langchain-mongodb-deepagents-vfs` | DeepAgents 虚拟文件系统，支持 S3 后端和文件监视 |
| `langgraph-checkpoint-mongodb` | LangGraph 检查点持久化 |
| `langgraph-store-mongodb` | LangGraph 长期记忆存储 |

核心包还包含 `graphrag/` 子模块和 `agent_toolkit/`，提供知识图谱检索和数据库 Agent 能力。

## 平台要求

| 能力 | 要求 |
|---|---|
| Vector Search | MongoDB Atlas（全托管），自建 MongoDB 不支持 |
| Auto-Embeddings | Atlas 支持的自动嵌入模型 |
| 原生 $rerank | MongoDB 8.3+ 且 Atlas Project Settings 启用 |
| 共享 M0 集群 | 索引编程式创建可能受限，需 Atlas UI 手动操作 |
| 全文搜索 | Atlas Search（Lucene BM25） |

## 快速入口

- 想了解向量搜索的内部机制：[向量存储架构](/ai/langchain-ai/langchain-mongodb/concepts/vector-store)
- 想了解缓存和聊天历史：[缓存与聊天历史](/ai/langchain-ai/langchain-mongodb/concepts/chat-history-cache)
- 想查看完整 API：[API 参考](/ai/langchain-ai/langchain-mongodb/references/api)
- 想查看使用示例：[基础使用示例](/ai/langchain-ai/langchain-mongodb/examples/basic-usage)
