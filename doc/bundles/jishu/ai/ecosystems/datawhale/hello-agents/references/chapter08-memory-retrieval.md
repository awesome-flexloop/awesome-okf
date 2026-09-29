---
title: 第八章 记忆与检索
type: reference
bundle: /datawhale/hello-agents
chapter: 8
part: 第三部分：高级知识扩展
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter8/第八章%20记忆与检索.md
---

# 第八章 记忆与检索

## 章节概要

本章为HelloAgents增加记忆系统和RAG两大核心能力，借鉴认知科学的人类记忆模型，设计四层记忆架构。

## 核心知识点

### LLM两大根本局限
1. **无状态导致对话遗忘**：上下文丢失、个性化缺失、学习受限、一致性问题
2. **内置知识静态有限**：时效性差、专业深度不足、幻觉问题、缺乏来源

### 人类记忆系统启发
| 记忆类型 | 持续时间 | 容量 |
|---------|---------|------|
| 感觉记忆 | 0.5-3秒 | 巨大 |
| 工作记忆 | 15-30秒 | 7±2项 |
| 长期-程序性 | 终生 | 无限（技能习惯） |
| 长期-语义 | 终生 | 无限（一般知识） |
| 长期-情景 | 终生 | 无限（个人经历） |

### 记忆系统四层架构

**基础设施层**：
- MemoryManager：统一调度协调
- MemoryItem：标准化记忆数据结构
- MemoryConfig：系统参数配置
- BaseMemory：通用接口定义

**记忆类型层**：
- **WorkingMemory**：临时信息，TTL管理，纯内存
- **EpisodicMemory**：具体事件，时间序列，SQLite+Qdrant
- **SemanticMemory**：抽象知识，图谱关系，Qdrant+Neo4j
- **PerceptualMemory**：多模态数据，SQLite+Qdrant

**存储后端层**：
- QdrantVectorStore：高性能向量语义检索
- Neo4jGraphStore：知识图谱关系管理
- SQLiteDocumentStore：结构化持久化

**嵌入服务层**：
- DashScopeEmbedding：通义千问云端
- LocalTransformerEmbedding：本地离线
- TFIDFEmbedding：轻量兜底

### RAG系统架构
```
文档处理层 → 嵌入表示层 → 向量存储层 → 智能问答层
```
- DocumentProcessor：多格式文档解析
- Pipeline：端到端RAG管道
- 多策略检索：向量检索 + MQE（多查询扩展）+ HyDE（假设文档嵌入）
- 智能片段合并与截断
- LLM增强生成

### 工具化设计
- **memory_tool**：Agent的记忆能力（存储、检索、维护交互信息）
- **rag_tool**：Agent的知识检索能力（从外部知识库检索，可自动存入记忆）

### 记忆与RAG的区别
- **记忆**：存储Agent自身的交互历史和经验（"我做过什么"）
- **RAG**：检索外部知识库的信息（"世界知道什么"）
- 两者互补：RAG检索结果可存入记忆，记忆也可增强RAG查询

## 相关概念
- 记忆系统
- 上下文工程
