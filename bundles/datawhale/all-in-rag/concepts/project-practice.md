---
type: concept
title: "项目实战"
bundle: /datawhale/all-in-rag
description: "从基础RAG到Graph RAG的完整实战——第八章'尝尝咸淡'食谱问答系统（FAISS+混合检索+查询路由），第九章图RAG优化（Neo4j+Milvus双引擎+智能路由+多跳推理）"
sources:
  - https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter8/
  - https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter9/
related:
  - /datawhale/all-in-rag/concepts/rag-overview
  - /datawhale/all-in-rag/concepts/data-preparation
  - /datawhale/all-in-rag/concepts/index-construction
  - /datawhale/all-in-rag/concepts/retrieval-advanced
  - /datawhale/all-in-rag/concepts/generation-rerank
tags: [project, graph-rag, neo4j, milvus, recipe, hybrid-retrieval, query-routing, knowledge-graph]
status: stable
---

# 项目实战

## 核心理解

第八、九章通过同一个项目——"尝尝咸淡"食谱问答系统——的两个版本，完整展示了从基础 RAG 到 Graph RAG 的技术跃迁。项目基于 [HowToCook](https://github.com/Anduin2017/HowToCook) 开源菜谱数据集（约 300+ Markdown 菜谱），目标是解决"今天吃什么"的选择困难症，支持菜品推荐、做法查询、食材咨询等场景。

## 项目一：基础 RAG 系统（第八章）

### 项目背景

基于 HowToCook 菜谱数据构建智能问答系统，用户可以：
- 询问具体菜品制作方法："宫保鸡丁怎么做？"
- 寻求菜品推荐："推荐几个简单的素菜"
- 获取食材信息："红烧肉需要什么食材？"

### 系统架构

`code/C8/` 采用模块化设计，四个核心模块对应 RAG 全链路：

| 模块 | 文件 | 职责 |
|------|------|------|
| 数据准备 | `rag_modules/data_preparation.py` | Markdown 加载、元数据提取（菜品名/分类/难度）、父子文档分块 |
| 索引构建 | `rag_modules/index_construction.py` | FAISS 向量索引构建、保存、加载 |
| 检索优化 | `rag_modules/retrieval_optimization.py` | 混合检索、元数据过滤搜索 |
| 生成集成 | `rag_modules/generation_integration.py` | Kimi API 调用、查询路由、查询重写、多模式生成 |

主类 `RecipeRAGSystem`（`main.py`）串联全流程。

### 关键技术

1. **父子文档分块**：子块用于精准向量检索，命中后返回完整父文档给 LLM，兼顾检索精度和上下文完整性

2. **元数据提取与过滤**：从 Markdown 文件名和内容提取菜品名、分类（水产/早餐/调味品/甜点/饮品/肉菜等）、难度，检索时支持条件过滤

3. **查询路由**：LLM 判断查询类型（list/detail/general），差异化处理：
   - list：保持原查询，返回菜品列表
   - detail：查询重写 + 分步指导生成
   - general：查询重写 + 基础回答

4. **查询重写**：对非列表查询，LLM 智能分析并优化检索词

5. **流式输出**：支持 Streaming 逐字返回，提升交互体验

### 技术栈

- LLM：Kimi（Moonshot API）
- 向量库：FAISS（本地文件持久化）
- 框架：LangChain
- 数据：HowToCook Markdown 菜谱

## 项目一优化：Graph RAG（第九章）

### 优化动机

基础 RAG 基于向量相似度检索，存在局限：
- 无法捕捉菜品-食材-步骤间的**显式关系**
- 难以回答跨文档的**多跳问题**（如"小龙虾和油焖大虾用了哪些相同食材？"）
- 对关系密集型查询的语义理解不足

第九章引入知识图谱和双引擎检索解决这些问题。

### 系统架构

`code/C9/` 在第八章基础上重构，六个核心模块：

| 模块 | 职责 |
|------|------|
| `graph_data_preparation.py` | Neo4j 图数据加载、菜谱文档构建、分块 |
| `graph_indexing.py` | 图索引构建 |
| `graph_rag_retrieval.py` | 图 RAG 检索、多跳遍历、子图提取、关系推理 |
| `hybrid_retrieval.py` | 传统混合检索（向量+稀疏） |
| `intelligent_query_router.py` | 查询复杂度分析、策略路由、自适应检索 |
| `milvus_index_construction.py` | Milvus 向量索引管理 |

主类 `AdvancedGraphRAGSystem`（`main.py`）整合双引擎。

### 关键技术

1. **Neo4j 知识图谱**：将菜谱数据建模为图结构（菜品-食材-步骤-分类实体及关系），支持多跳遍历和关系推理

2. **Milvus 向量引擎**：替代 FAISS，支持生产级向量检索、元数据过滤和分布式扩展

3. **双引擎检索**：
   - **传统混合检索**：适合简单语义查询
   - **图 RAG 检索**：适合关系密集、多跳推理查询
   - **组合策略**：融合两种引擎结果

4. **智能查询路由器**（`IntelligentQueryRouter`）：
   - 量化**查询复杂度**（query_complexity）
   - 量化**关系密集度**（relationship_intensity）
   - 自动推荐策略：`hybrid_traditional` / `graph_rag` / `combined`
   - 支持路由决策解释（explain_routing_decision）

5. **自适应回答生成**：根据检索策略和查询类型选择生成模式

6. **系统统计与反馈**：路由统计（各策略使用比例）、知识库统计（菜谱/食材/步骤数量）、支持重建知识库

### 技术栈

- 图数据库：Neo4j
- 向量数据库：Milvus（Docker 部署）
- LLM：Kimi（Moonshot API）
- 嵌入模型：BGE 系列
- 额外：AI 生成的 Agent 代码（`agent(代码系ai生成)/` 目录，含菜谱用量规范化、批量管理等）

## 从 C8 到 C9 的技术跃迁

| 维度 | 第八章（基础 RAG） | 第九章（Graph RAG） |
|------|-------------------|-------------------|
| 向量库 | FAISS（本地） | Milvus（服务化） |
| 数据模型 | 扁平文档 | 知识图谱（实体-关系） |
| 检索引擎 | 单引擎（混合检索） | 双引擎（向量+图） |
| 查询理解 | LLM 路由（list/detail/general） | 复杂度+关系密集度量化路由 |
| 推理能力 | 单跳语义匹配 | 多跳遍历+子图提取+关系推理 |
| 适用查询 | "宫保鸡丁怎么做" | "小龙虾和油焖大虾的共同食材" |
| 系统复杂度 | 中 | 高（Neo4j+Milvus 双数据库） |

这一跃迁体现了 RAG 技术从"语义相似度匹配"走向"结构化知识推理"的前沿方向。

## 运行方式

```bash
# 第八章
cd code/C8
pip install -r requirements.txt
cp .env.example .env  # 配置 MOONSHOT_API_KEY
python main.py

# 第九章（需先启动 Neo4j 和 Milvus）
cd code/C9
docker-compose up -d  # 启动 Milvus
pip install -r requirements.txt
cp .env.example .env  # 配置 API Key 和数据库连接
python main.py
```

## 延伸阅读

- [RAG 概述与架构](rag-overview.md)——项目实战的理论基础
- [检索进阶技术](retrieval-advanced.md)——混合检索和查询路由
- [生成与重排](generation-rerank.md)——查询路由驱动的差异化生成
- [基础RAG实战示例](../examples/c8-basic-rag.md)——第八章代码详解
- [Graph RAG优化示例](../examples/c9-graph-rag.md)——第九章代码详解
