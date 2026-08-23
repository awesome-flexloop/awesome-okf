---
type: log
scope: langchain-mongodb
name: log
version: "0.11.0"
source: https://github.com/langchain-ai/langchain-mongodb
description: langchain-mongodb OKF bundle 变更日志
---

# 变更日志

## 2026-08-23 — v0.1.0（OKF v0.2 中等深度 bundle）

### 新增

- 基于 langchain-mongodb v0.11.0 源码生成 OKF v0.2 bundle。
- **spec/facts.md**：79 条编号事实，覆盖项目元信息、公共 API、MongoDBAtlasVectorSearch、索引管理、MongoDBRecordManager、双层缓存、聊天历史、文档存储、管道组件、AutoEmbeddings、五种检索器、Agent Toolkit、工具函数和 Monorepo 结构。
- **spec/insights.md**：4 个架构洞察——以 MongoDB 聚合管道为统一计算引擎（向量搜索/RRF 混合/父子 $lookup）、双嵌入模式（客户端 vs Atlas Auto-Embedding 的类型安全契约）、LangChain 契约的 MongoDB 原生实现（抽象映射/语义缓存多继承/一消息一文档/服务器时间）、平台约束与 BSON 限制工程应对。
- **concepts/overview.md**：项目总览，包含组件架构图、顶层 API、Monorepo 结构和平台要求。
- **concepts/vector-store.md**：向量存储深度解析，包含文档结构、双嵌入模式对比、搜索管道、MMR 算法、批量写入、索引管理、五种检索器、$rerank 原生重排序、ID 处理。
- **concepts/chat-history-cache.md**：缓存与聊天历史解析，包含精确缓存/语义缓存/聊天历史的存储结构、工作流程、序列化机制和对比表。
- **references/api.md**：完整 API 参考，覆盖 MongoDBAtlasVectorSearch、MongoDBChatMessageHistory、MongoDBCache、MongoDBAtlasSemanticCache、MongoDBRecordManager、MongoDBDocStore、五种检索器、Agent Toolkit、索引与管道函数。
- **examples/basic-usage.md**：10 个代码示例，覆盖向量存储 CRUD、聊天历史、精确/语义缓存、全文/混合检索器、索引创建、记录管理器和完整 RAG 链。
- 各目录 index.md 导航文件。

### 验证

- API 名称和方法签名已通过源码阅读验证（见 facts.md 中的文件路径和行号引用）。
- 所有交叉链接以 `/langchain-ai/langchain-mongodb/` 开头。
- frontmatter 包含 `okf_version: "0.2"`。
