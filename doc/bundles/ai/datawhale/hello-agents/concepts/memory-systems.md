---
title: 记忆系统
type: concept
bundle: /datawhale/hello-agents
related:
  - /datawhale/hello-agents/concepts/context-engineering
  - /datawhale/hello-agents/concepts/agent-framework-development
  - /datawhale/hello-agents/references/chapter08-memory-retrieval
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter8/第八章%20记忆与检索.md
---

# 记忆系统

记忆系统（Memory System）使智能体能够记住之前的交互内容并从历史经验中学习。Hello-Agents教程借鉴认知科学的人类记忆模型，设计了四层记忆架构，并与RAG（检索增强生成）系统协同工作。

## 为何需要记忆

基于LLM的智能体面临两个根本性局限：

1. **无状态导致对话遗忘**：每次API调用都是独立计算，模型不自动记住上一次对话
   - 上下文丢失：长对话中早期重要信息因窗口限制丢失
   - 个性化缺失：无法记住用户偏好和习惯
   - 学习能力受限：无法从成功/失败经验中改进
   - 一致性问题：多轮对话中可能前后矛盾

2. **内置知识的局限性**：知识是静态的、有限的
   - 知识时效性：训练数据有截止点
   - 专业领域深度不足
   - 事实准确性：需要检索验证减少幻觉
   - 可解释性：需要信息来源增强可信度

## 认知科学启发

人类记忆系统的层次结构：

| 记忆类型 | 持续时间 | 容量 | 对应工程实现 |
|---------|---------|------|-------------|
| 感觉记忆 | 0.5-3秒 | 巨大 | 原始输入缓冲 |
| 工作记忆 | 15-30秒 | 7±2项 | TTL内存缓存 |
| 长期记忆-程序性 | 可达终生 | 几乎无限 | 技能/习惯存储 |
| 长期记忆-语义 | 可达终生 | 几乎无限 | 知识图谱 |
| 长期记忆-情景 | 可达终生 | 几乎无限 | 事件序列存储 |

## HelloAgents四层记忆架构

### 基础设施层
- **MemoryManager**：记忆管理器，统一调度和协调
- **MemoryItem**：标准化记忆数据结构
- **MemoryConfig**：系统参数配置
- **BaseMemory**：记忆基类，定义通用接口

### 记忆类型层

1. **WorkingMemory（工作记忆）**
   - 临时信息存储，TTL（生存时间）管理
   - 纯内存实现，快速访问
   - 对应人类的短期注意力焦点

2. **EpisodicMemory（情景记忆）**
   - 存储具体事件和交互经历
   - 时间序列组织
   - SQLite持久化 + Qdrant向量检索

3. **SemanticMemory（语义记忆）**
   - 存储抽象知识和概念关系
   - 知识图谱管理（Neo4j图存储）
   - 对应人类的一般世界知识

4. **PerceptualMemory（感知记忆）**
   - 多模态数据存储（图像、音频等）
   - SQLite + Qdrant混合存储

### 存储后端层
- **QdrantVectorStore**：高性能向量语义检索
- **Neo4jGraphStore**：知识图谱关系管理
- **SQLiteDocumentStore**：结构化数据持久化

### 嵌入服务层
- **DashScopeEmbedding**：通义千问云端API
- **LocalTransformerEmbedding**：本地离线部署
- **TFIDFEmbedding**：轻量级兜底方案

## RAG检索增强生成

RAG系统专注于外部知识的获取和利用，与记忆系统互补：

```
文档处理层 → 嵌入表示层 → 向量存储层 → 智能问答层
```

### 关键技术
- **多策略检索**：向量检索 + MQE（多查询扩展）+ HyDE（假设文档嵌入）
- **智能片段合并与截断**：上下文构建优化
- **LLM增强生成**：基于检索上下文的准确问答

### 记忆与RAG的分工
- **memory_tool**：存储和维护对话过程中的交互信息
- **rag_tool**：从用户提供的知识库中检索相关信息，可将重要检索结果自动存入记忆

## 设计洞察

记忆系统的关键不是"存什么"，而是**"何时检索、何时遗忘"**。HelloAgents将记忆和RAG都设计为工具（Tool），这意味着Agent与记忆的交互模式和与外部工具完全相同——请求-响应，这体现了"万物皆工具"的统一抽象理念。

## 相关阅读

- [第八章 记忆与检索](/ai/datawhale/hello-agents/references/chapter08-memory-retrieval)
- [上下文工程](/ai/datawhale/hello-agents/concepts/context-engineering)
- [Agent框架开发](/ai/datawhale/hello-agents/concepts/agent-framework-development)
