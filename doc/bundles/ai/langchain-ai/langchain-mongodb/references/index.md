# 参考文档索引

## API 参考

- [核心 API 参考](/ai/langchain-ai/langchain-mongodb/references/api) — MongoDBAtlasVectorSearch、缓存、聊天历史、记录管理器、文档存储、检索器、Agent Toolkit 的完整类与方法签名

## 源码结构

```
langchain_mongodb/
├── __init__.py              # 顶层导出四个核心类
├── vectorstores.py          # MongoDBAtlasVectorSearch
├── cache.py                 # MongoDBCache / MongoDBAtlasSemanticCache
├── chat_message_histories.py# MongoDBChatMessageHistory
├── indexes.py               # MongoDBRecordManager
├── index.py                 # 索引创建/更新/删除函数
├── docstores.py             # MongoDBDocStore
├── embeddings.py            # AutoEmbeddings
├── pipelines.py             # 聚合管道组件
├── utils.py                 # MMR、ObjectId 转换、序列化工具
├── retrievers/              # 五种检索器
│   ├── full_text_search.py
│   ├── hybrid_search.py
│   ├── parent_document.py
│   ├── self_querying.py
│   └── graphrag.py
├── agent_toolkit/           # MongoDB Agent 工具包
└── graphrag/                # GraphRAG 实现
```

```{toctree}
:hidden:

api
```
