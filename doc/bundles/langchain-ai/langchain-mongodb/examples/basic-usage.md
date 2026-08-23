---
type: example
scope: langchain-mongodb
name: basic-usage
version: "0.11.0"
source: https://github.com/langchain-ai/langchain-mongodb
description: langchain-mongodb 基础使用示例——向量存储、聊天历史、缓存和检索器
---

# 基础使用示例

本示例展示 langchain-mongodb 核心组件的典型用法。所有代码假设你已有一个 MongoDB Atlas 集群连接字符串。

## 前置条件

```bash
pip install -U langchain-mongodb langchain-openai
```

设置连接字符串：

```python
import os

MONGODB_URI = os.environ["MONGODB_ATLAS_CONNECTION_STRING"]
```

## 1. 向量存储：创建、写入与搜索

### 从连接字符串创建

```python
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings

vectorstore = MongoDBAtlasVectorSearch.from_connection_string(
    connection_string=MONGODB_URI,
    namespace="mydocdb.articles",       # database.collection
    embedding=OpenAIEmbeddings(),
    index_name="vector_index",
    text_key="text",
    embedding_key="embedding",
    relevance_score_fn="cosine",
    dimensions=1536,
)
```

### 添加文档

```python
from langchain_core.documents import Document

documents = [
    Document(page_content="MongoDB Atlas 支持向量搜索", metadata={"category": "database"}),
    Document(page_content="LangChain 是一个 LLM 应用框架", metadata={"category": "ai"}),
    Document(page_content="HNSW 是一种近似最近邻算法", metadata={"category": "algorithm"}),
]

ids = vectorstore.add_documents(documents)
```

### 相似度搜索

```python
results = vectorstore.similarity_search("什么是向量搜索？", k=2)
for doc in results:
    print(f"* {doc.page_content} [{doc.metadata}]")
```

### 带分数搜索

```python
results = vectorstore.similarity_search_with_score("什么是向量搜索？", k=2)
for doc, score in results:
    print(f"* [SIM={score:.4f}] {doc.page_content}")
```

### 带元数据过滤

```python
results = vectorstore.similarity_search(
    "AI 技术",
    k=2,
    pre_filter={"category": {"$eq": "ai"}},
)
```

### MMR 搜索（多样性感知）

```python
results = vectorstore.max_marginal_relevance_search(
    "数据库技术",
    k=2,
    fetch_k=10,
    lambda_mult=0.5,
)
```

## 2. 聊天消息历史

```python
from langchain_mongodb import MongoDBChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

history = MongoDBChatMessageHistory(
    connection_string=MONGODB_URI,
    session_id="user-123-conversation-1",
    database_name="chat_history",
    collection_name="message_store",
    history_size=50,  # 只保留最近 50 条
)

history.add_message(HumanMessage(content="你好，请介绍一下 MongoDB"))
history.add_message(AIMessage(content="MongoDB 是一个文档型 NoSQL 数据库..."))

messages = history.messages
for msg in messages:
    print(f"{msg.type}: {msg.content}")
```

复用已有 MongoClient：

```python
from pymongo import MongoClient

client = MongoClient(MONGODB_URI)
history = MongoDBChatMessageHistory(
    connection_string=None,
    session_id="session-2",
    client=client,
)
```

## 3. 精确缓存

```python
from langchain_mongodb import MongoDBCache
from langchain_openai import ChatOpenAI
from langchain_core.globals import set_llm_cache

cache = MongoDBCache(
    connection_string=MONGODB_URI,
    database_name="llm_cache",
    collection_name="exact_cache",
)

set_llm_cache(cache)

llm = ChatOpenAI(model="gpt-4")

response1 = llm.invoke("解释什么是 RAG")
response2 = llm.invoke("解释什么是 RAG")
```

## 4. 语义缓存

```python
from langchain_mongodb import MongoDBAtlasSemanticCache

semantic_cache = MongoDBAtlasSemanticCache(
    connection_string=MONGODB_URI,
    embedding=OpenAIEmbeddings(),
    database_name="llm_cache",
    collection_name="semantic_cache",
    index_name="semantic_index",
    score_threshold=0.95,
    wait_until_ready=10,
)

set_llm_cache(semantic_cache)

response1 = llm.invoke("解释什么是 RAG")
response2 = llm.invoke("RAG 是什么意思？")
```

## 5. 作为 Retriever 使用

```python
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3, "fetch_k": 10, "lambda_mult": 0.5},
)

docs = retriever.invoke("MongoDB 向量搜索")
```

## 6. 全文搜索检索器

```python
from langchain_mongodb.retrievers import MongoDBAtlasFullTextSearchRetriever
from pymongo import MongoClient

client = MongoClient(MONGODB_URI)
collection = client["mydocdb"]["articles"]

fulltext_retriever = MongoDBAtlasFullTextSearchRetriever(
    collection=collection,
    search_index_name="text_index",
    search_field="text",
    k=5,
)

docs = fulltext_retriever.invoke("HNSW 算法")
```

## 7. 混合搜索检索器

```python
from langchain_mongodb.retrievers import MongoDBAtlasHybridSearchRetriever

hybrid_retriever = MongoDBAtlasHybridSearchRetriever(
    vectorstore=vectorstore,
    search_index_name="text_index",
    k=5,
    vector_penalty=60.0,
    fulltext_penalty=60.0,
    vector_weight=1.0,
    fulltext_weight=1.0,
)

docs = hybrid_retriever.invoke("MongoDB 向量搜索")
```

## 8. 编程式创建向量索引

```python
vectorstore.create_vector_search_index(
    dimensions=1536,
    filters=["category", "year"],
    wait_until_complete=60,
)
```

这会创建包含 vector 字段和 filter 字段的 Atlas Vector Search 索引，并等待索引状态变为 READY。

## 9. 记录管理器（增量索引）

```python
from langchain_mongodb.indexes import MongoDBRecordManager
from pymongo import MongoClient
from langchain.indexes import index

client = MongoClient(MONGODB_URI)
record_collection = client["mydocdb"]["index_records"]

record_manager = MongoDBRecordManager(collection=record_collection)

docs = [
    Document(page_content="文档1", metadata={"source": "web"}),
    Document(page_content="文档2", metadata={"source": "web"}),
]

index(
    docs,
    record_manager,
    vector_store=vectorstore,
    cleanup="incremental",
    source_id_key="source",
)
```

## 10. 完整 RAG 链示例

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4", temperature=0)

prompt = ChatPromptTemplate.from_template(
    "基于以下上下文回答问题。\n\n上下文：{context}\n\n问题：{question}"
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

answer = rag_chain.invoke("MongoDB Atlas 的向量搜索使用什么算法？")
print(answer)
```

## 相关阅读

- [API 参考](/langchain-ai/langchain-mongodb/references/api)
- [向量存储架构](/langchain-ai/langchain-mongodb/concepts/vector-store)
- [缓存与聊天历史](/langchain-ai/langchain-mongodb/concepts/chat-history-cache)
