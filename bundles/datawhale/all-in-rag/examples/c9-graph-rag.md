---
type: example
title: "Graph RAG食谱问答系统"
bundle: /datawhale/all-in-rag
description: "第九章项目实战优化：基于Neo4j知识图谱+Milvus向量库的双引擎图RAG系统，支持智能查询路由、多跳推理、子图提取与自适应生成"
sources: https://github.com/datawhalechina/all-in-rag/tree/main/code/C9
related:
  - /datawhale/all-in-rag/concepts/project-practice
  - /datawhale/all-in-rag/concepts/retrieval-advanced
  - /datawhale/all-in-rag/concepts/index-construction
  - /datawhale/all-in-rag/concepts/generation-rerank
tags: [graph-rag, neo4j, milvus, knowledge-graph, query-routing, multi-hop, hybrid-retrieval]
status: stable
---

# Graph RAG食谱问答系统

## 概述

本示例对应 All-in-RAG 第九章项目实战优化（选修篇），代码位于 `code/C9/`。在第八章基础 RAG 系统之上，引入 Neo4j 知识图谱和 Milvus 向量数据库，构建双引擎图 RAG 系统，解决向量检索无法处理关系推理和多跳查询的局限。

## 优化动机

第八章基础 RAG 基于 FAISS 向量相似度检索，存在以下局限：
- 无法捕捉菜品-食材-步骤间的**显式关系**
- 难以回答跨文档的**多跳问题**（如"小龙虾和油焖大虾用了哪些相同食材？"）
- 对关系密集型查询的语义理解不足

第九章通过知识图谱补充结构化关系信息，通过智能路由器根据查询特征自动选择检索策略。

## 环境准备

```bash
# 启动 Milvus 向量数据库
cd code
docker-compose up -d

# 安装依赖
cd C9
conda create -n cook-rag-2 python=3.12.7
conda activate cook-rag-2
pip install -r requirements.txt

# 配置环境变量（Neo4j连接、Milvus连接、Kimi API Key）
cp .env.example .env

python main.py
```

需要同时运行 Neo4j 图数据库和 Milvus 向量数据库服务。

## 代码结构

```
code/C9/
├── config.py                              # GraphRAGConfig（Neo4j/Milvus/LLM/图检索参数）
├── main.py                                # AdvancedGraphRAGSystem 主类
├── .env.example                           # 环境变量模板
├── requirements.txt
├── rag_modules/
│   ├── graph_data_preparation.py          # Neo4j图数据加载、菜谱文档构建、分块
│   ├── graph_indexing.py                  # 图索引构建
│   ├── graph_rag_retrieval.py             # 图RAG检索：多跳遍历、子图提取、关系推理
│   ├── hybrid_retrieval.py                # 传统混合检索（向量+稀疏）
│   ├── intelligent_query_router.py        # 智能查询路由器
│   ├── milvus_index_construction.py       # Milvus向量索引管理
│   └── generation_integration.py          # 自适应回答生成
└── agent(代码系ai生成)/                    # AI生成的菜谱Agent（扩展功能）
    ├── recipe_ai_agent.py
    ├── amount_normalizer.py
    ├── batch_manager.py
    └── ...
```

## 核心架构

### 双引擎检索

系统维护两套并行的检索引擎：

1. **传统混合检索引擎**（`HybridRetrievalModule`）
   - 基于 Milvus 向量检索 + 稀疏检索
   - 适合简单语义查询（"宫保鸡丁怎么做"）
   - 速度快，延迟低

2. **图 RAG 检索引擎**（`GraphRAGRetrieval`）
   - 基于 Neo4j 知识图谱
   - 支持多跳遍历、子图提取、关系推理
   - 适合关系密集型查询（"哪些菜同时用了花椒和辣椒"）

### 智能查询路由器

```python
class IntelligentQueryRouter:
    def route_query(self, question: str, top_k: int):
        # 分析查询特征
        analysis = self.analyze_query(question)
        # analysis.query_complexity: 查询复杂度分数
        # analysis.relationship_intensity: 关系密集度分数
        # analysis.recommended_strategy: 推荐策略

        if analysis.recommended_strategy == "hybrid_traditional":
            return self.traditional_retrieval.search(question, top_k), analysis
        elif analysis.recommended_strategy == "graph_rag":
            return self.graph_rag_retrieval.retrieve(question, top_k), analysis
        else:  # combined
            traditional_results = self.traditional_retrieval.search(...)
            graph_results = self.graph_rag_retrieval.retrieve(...)
            return self._merge_results(traditional_results, graph_results), analysis
```

三种路由策略：
- `hybrid_traditional`：简单查询，仅用传统混合检索
- `graph_rag`：关系密集查询，仅用图检索
- `combined`：复杂查询，融合双引擎结果

### 主系统流程

```python
class AdvancedGraphRAGSystem:
    def ask_question_with_routing(self, question, stream=False, explain_routing=False):
        # 1. 智能路由检索（自动选择策略）
        relevant_docs, analysis = self.query_router.route_query(question, top_k)

        # 2. 显示路由信息
        strategy_icon = {"hybrid_traditional": "🔍", "graph_rag": "🕸️", "combined": "🔄"}
        print(f"策略: {analysis.recommended_strategy.value}")
        print(f"复杂度: {analysis.query_complexity:.2f}, 关系密集度: {analysis.relationship_intensity:.2f}")

        # 3. 自适应生成回答
        if stream:
            return self.generation_module.generate_adaptive_answer_stream(question, relevant_docs)
        else:
            return self.generation_module.generate_adaptive_answer(question, relevant_docs)
```

## 知识库构建

```python
def build_knowledge_base(self):
    # 1. 从Neo4j加载图数据（菜品、食材、步骤实体及关系）
    self.data_module.load_graph_data()

    # 2. 构建菜谱文档（将图结构数据转为可检索文档）
    self.data_module.build_recipe_documents()

    # 3. 文档分块
    chunks = self.data_module.chunk_documents(chunk_size, chunk_overlap)

    # 4. 构建Milvus向量索引
    self.index_module.build_vector_index(chunks)

    # 5. 初始化双引擎检索器
    self.traditional_retrieval.initialize(chunks)
    self.graph_rag_retrieval.initialize()
```

## 关键技术点

1. **知识图谱建模**：将菜谱数据建模为实体（菜品、食材、步骤、分类）和关系（包含、需要、属于），支持图查询语言（Cypher）遍历
2. **双引擎架构**：向量检索（语义相似）与图检索（关系推理）优势互补
3. **查询复杂度量化**：不是简单的 LLM 分类，而是通过量化指标（复杂度、关系密集度）驱动路由决策
4. **路由决策可解释**：`explain_routing_decision()` 方法可展示为何选择某策略
5. **结果融合**：组合策略下融合双引擎结果，合并去重并按综合分数排序
6. **系统统计与反馈**：记录各策略使用比例，支持持续优化路由阈值
7. **Milvus 服务化**：替代 FAISS，支持集合管理、持久化、元数据过滤

## 交互式功能

```python
def run_interactive(self):
    # 支持命令：
    # - 普通问答：直接输入问题
    # - stats：查看系统统计（路由分布、知识库规模）
    # - rebuild：重建知识库
    # - quit：退出
```

系统统计展示：
- 总查询次数、各策略使用比例
- 菜谱/食材/步骤数量
- Milvus 向量索引记录数

## 与第八章的对比

| 维度 | 第八章（C8） | 第九章（C9） |
|------|-------------|-------------|
| 向量库 | FAISS（本地文件） | Milvus（Docker 服务） |
| 知识表示 | 扁平文档分块 | Neo4j 知识图谱 + 文档 |
| 检索引擎 | 单引擎混合检索 | 双引擎（向量+图） |
| 查询理解 | LLM 三分类路由 | 复杂度+关系密集度量化路由 |
| 推理能力 | 单跳语义匹配 | 多跳遍历、子图提取 |
| 部署复杂度 | 低（单进程） | 高（Neo4j+Milvus 双数据库） |

## 学习要点

- Graph RAG 不是替代向量 RAG，而是补充——通过智能路由实现优势互补
- 知识图谱构建成本高，但对关系密集型查询有不可替代的价值
- 查询路由是 Modular RAG 的核心能力——根据查询特征动态编排检索模块
- 生产系统需要可观测性（路由统计、性能计时）和运维能力（重建、清理）

## 延伸阅读

- [基础RAG食谱问答系统](c8-basic-rag.md)——第八章基础版本
- [项目实战概念](../concepts/project-practice.md)——完整架构解析
- [检索进阶技术](../concepts/retrieval-advanced.md)——查询路由与混合检索原理
