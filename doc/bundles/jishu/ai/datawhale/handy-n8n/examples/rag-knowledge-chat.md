---
type: example
title: "RAG 知识库对话"
bundle: /datawhale/handy-n8n
description: "C04 实践：Form Trigger 文件上传 → Embedding → Vector Store 构建知识库，Chat Trigger + AI Agent 检索增强问答"
sources: https://github.com/datawhalechina/handy-n8n/blob/main/c04/n8n-ai-concepts.md
related:
  - /datawhale/handy-n8n/concepts/ai-api-integration
tags: [rag, vector-store, embedding, agent, chat]
status: stable
---

# RAG 知识库对话

## 概述

本示例对应 handy-n8n 第四章 AI 相关概念中的 RAG 实践，工作流 JSON 位于 `workflows/c04/n8n_rag.json`。RAG（检索增强生成）通过向量存储将外部文档知识注入 LLM，使 AI 能够基于特定文档回答问题，缓解幻觉和知识过时问题。示例以"chat 嬛嬛.txt"为文档，构建了一个可对话的知识库。

## 架构：两个工作流

RAG 系统在 n8n 中分为**内容上传**和**内容检索**两个独立工作流。

### 工作流一：内容上传

```
On Form Submission（表单触发，文件上传）
  → Default Data Loader（文档加载与解析）
    → Input Data Field Name 与表单字段名一致
  → Embedding Model（文本向量化，如 Gemini text-embedding-004）
  → Simple Vector Store（Insert Documents 存储向量）
```

**关键配置**：
- Form Trigger 添加文件类型字段，n8n 自动弹出上传表单
- Default Data Loader 的 `Input Data Field Name` 必须与 Form Trigger 的字段名一致
- Simple Vector Store 是集群节点，需关联 Embedding Model 子节点
- 执行后选择文件提交，文档被转化为向量并存储

### 工作流二：内容检索

```
On Chat Message（聊天触发）
  → AI Agent（智能体根节点）
    ├── LLM 子节点（大语言模型）
    ├── Memory 子节点（对话记忆）
    └── Simple Vector Store（Retrieve Documents (As Tool for AI Agent)）
          └── Embedding Model（与上传时相同的模型）
```

**关键配置**：
- Vector Store 操作选择 "Retrieve Documents (As Tool for AI Agent)"，作为 Agent 的工具
- Embedding Model 必须与内容上传工作流使用**相同的模型**，否则向量空间不匹配
- Agent 自主决定何时调用检索工具——用户提问时，Agent 判断需要外部知识则自动检索

## 效果对比

**无 RAG**：AI 只能依赖训练数据回答，对上传文档中的内容一无所知。

**有 RAG**：Agent 从 Vector Store 检索相关文档片段，基于检索内容生成准确回答。对比截图清晰展示了 RAG 对回答质量的提升。

## 配套工作流

- `n8n_rag.json`：完整 RAG 工作流
- `n8n_chat_with_memory.json`：带记忆的聊天（Memory 机制演示）
- `n8n_tools.json`：Agent 多工具调用（Date & Time Tool + Calculator）

## 扩展思路

- **多格式文档**：Default Data Loader 支持多种文档格式，可批量上传
- **向量存储选择**：Simple Vector Store 适合演示，生产环境可替换为 Pinecone、Qdrant、Postgres pgvector 等
- **分块策略**：调整文档分块大小和重叠度，优化检索精度
- **多轮对话**：添加 Memory 节点（生产环境用 Redis/Postgres Chat Memory），支持追问和上下文引用
- **混合检索**：结合关键词检索和向量检索提升召回率

## 学习要点

1. RAG 的两阶段架构：离线索引（上传→向量化→存储）和在线查询（问题→检索→生成）
2. Embedding Model 的一致性：上传和检索必须使用相同模型
3. 集群节点的依赖关系：Simple Vector Store 需要关联 Embedding Model 子节点
4. Agent + Tool 模式：Vector Store 作为 Agent 的工具，Agent 自主决定调用时机

## 延伸阅读

- [AI 与 API 集成](../concepts/ai-api-integration.md)——集群节点、Memory、RAG、MCP 完整概念
- [C04 n8n 高阶用法](../references/c04-advanced-usage.md)——完整信源
- [n8n 官方 RAG 文档](https://docs.n8n.io/advanced-ai/rag-in-n8n/)
