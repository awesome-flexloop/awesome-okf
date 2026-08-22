---
title: RAG 检索增强生成模式
type: concept
bundle: pocketflow-patterns
source: cookbook/pocketflow-rag
related:
  - /pocketflow/pocketflow-core/concepts/batch-processing
  - /pocketflow/pocketflow-patterns/concepts/map-reduce
---

# RAG 检索增强生成模式

RAG（Retrieval-Augmented Generation）将文档处理分为**离线建索引**和**在线问答**两个独立Flow，实现"先检索、后生成"的知识问答。

## 双Flow架构

```
┌───────────── 离线流程（索引构建）─────────────┐
│                                               │
│  ChunkDocuments → EmbedDocuments → CreateIndex│
│  (分块)          (向量化)        (建索引)       │
└───────────────────────────────────────────────┘
                      ↓ 索引持久化
┌───────────── 在线流程（问答）─────────────────┐
│                                               │
│  EmbedQuery → RetrieveDocs → GenerateAnswer   │
│  (查询向量化)  (检索相关文档)  (LLM生成回答)    │
└───────────────────────────────────────────────┘
```

## 离线流程节点

| 节点 | 职责 | 输入 | 输出 |
|------|------|------|------|
| ChunkDocuments | 文档分块 | 原始文档 | 文本块列表 |
| EmbedDocuments | 批量向量化 | 文本块列表 | 向量列表 |
| CreateIndex | 构建索引 | 向量+文本 | 向量索引文件 |

## 在线流程节点

| 节点 | 职责 | 输入 | 输出 |
|------|------|------|------|
| EmbedQuery | 查询向量化 | 用户问题 | 查询向量 |
| RetrieveDocument | 相似度检索 | 查询向量+索引 | 相关文档块 |
| GenerateAnswer | LLM生成回答 | 问题+相关文档 | 最终答案 |

## 流程代码骨架

```python
# 离线Flow
chunk >> embed_docs >> create_index
offline_flow = Flow(start=chunk)

# 在线Flow
embed_q >> retrieve >> answer
online_flow = Flow(start=embed_q)
```

## 变体：Agentic RAG

Agentic RAG在检索后增加决策节点，判断是否需要更多检索或直接回答：

```
Retrieve → Decide → (需要更多?) → Retrieve (循环)
              │
              └→ Answer
```

类似Agent循环模式，但检索作为工具。

## Cookbook 对应示例

- `pocketflow-rag` — 基础RAG（离线+在线双Flow）
- `pocketflow-agentic-rag` — Agent驱动的RAG
- `pocketflow-chat-memory` — 带记忆的聊天RAG
- `pocketflow-notebook-lm` — NotebookLM风格的RAG
