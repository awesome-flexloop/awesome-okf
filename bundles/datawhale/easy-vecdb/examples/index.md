# EasyVecDB 实践示例索引

本目录包含向量数据库的实践示例，建议配合概念文档阅读。

## 基础实现

| 示例 | 说明 |
|------|------|
| [mini-vector-db.md](mini-vector-db.md) | 用 numpy + sklearn 手写向量数据库，含 CRUD、暴力检索、IVF 索引、持久化 |

## 检索应用

| 示例 | 说明 |
|------|------|
| [rag-with-faiss.md](rag-with-faiss.md) | 基于 FAISS 构建 RAG 系统：文档分块、嵌入、索引、检索、LLM 生成全流程 |

## 工程工具

| 示例 | 说明 |
|------|------|
| [milvus-getting-started.md](milvus-getting-started.md) | PyMilvus 核心 API 实战：Collection 管理、数据插入、IVF_PQ 索引、向量搜索、元数据过滤 |
