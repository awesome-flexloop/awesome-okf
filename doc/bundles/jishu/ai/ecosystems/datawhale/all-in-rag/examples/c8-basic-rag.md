---
type: example
title: "基础RAG食谱问答系统"
bundle: /datawhale/all-in-rag
description: "第八章项目实战：基于FAISS+LangChain+Kimi的食谱RAG系统，涵盖数据准备、索引构建、混合检索、查询路由、流式生成全链路"
sources: https://github.com/datawhalechina/all-in-rag/tree/main/code/C8
related:
  - /datawhale/all-in-rag/concepts/project-practice
  - /datawhale/all-in-rag/concepts/data-preparation
  - /datawhale/all-in-rag/concepts/index-construction
  - /datawhale/all-in-rag/concepts/retrieval-advanced
  - /datawhale/all-in-rag/concepts/generation-rerank
tags: [rag, faiss, langchain, kimi, recipe, hybrid-search, query-routing, streaming]
status: stable
---

# 基础RAG食谱问答系统

## 概述

本示例对应 All-in-RAG 第八章项目实战（基础篇），代码位于 `code/C8/`。项目名为"尝尝咸淡RAG系统"，基于 [HowToCook](https://github.com/Anduin2017/HowToCook) 开源菜谱数据集（约 300+ Markdown 文件），构建一个智能食谱问答系统，解决"今天吃什么"的选择困难症。

这是一个将前七章理论知识串联为完整可运行系统的综合实战，展示了从数据加载到交互式问答的完整 RAG 工程链路。

## 环境准备

```bash
conda create -n cook-rag-1 python=3.12.7
conda activate cook-rag-1
cd code/C8
pip install -r requirements.txt
cp .env.example .env  # 配置 MOONSHOT_API_KEY
python main.py
```

需要申请 [Kimi（Moonshot）API Key](https://platform.moonshot.cn/console/api-keys)。

## 代码结构

```
code/C8/
├── config.py                          # RAGConfig 配置类（嵌入模型、LLM、chunk参数、top_k等）
├── main.py                            # RecipeRAGSystem 主类与交互式入口
├── requirements.txt                   # 项目依赖
└── rag_modules/
    ├── __init__.py
    ├── data_preparation.py            # 数据准备：Markdown加载、元数据提取、父子文档分块
    ├── index_construction.py          # 索引构建：FAISS向量索引、保存/加载
    ├── retrieval_optimization.py      # 检索优化：混合检索、元数据过滤搜索
    └── generation_integration.py      # 生成集成：Kimi API、查询路由、查询重写、多模式生成
```

## 核心流程

### 1. 系统初始化

```python
class RecipeRAGSystem:
    def __init__(self, config: RAGConfig = None):
        self.config = config or DEFAULT_CONFIG
        self.data_module = None
        self.index_module = None
        self.retrieval_module = None
        self.generation_module = None
```

系统检查数据路径和 API Key 后，依次初始化四个模块。

### 2. 知识库构建（离线）

```python
def build_knowledge_base(self):
    # 尝试加载已保存的索引
    vectorstore = self.index_module.load_index()
    if vectorstore is not None:
        # 加载已有索引，仍需加载文档和分块用于检索
        self.data_module.load_documents()
        chunks = self.data_module.chunk_documents()
    else:
        # 全新构建：加载→分块→向量化→保存
        self.data_module.load_documents()
        chunks = self.data_module.chunk_documents()
        vectorstore = self.index_module.build_vector_index(chunks)
        self.index_module.save_index()

    # 初始化检索模块
    self.retrieval_module = RetrievalOptimizationModule(vectorstore, chunks)
```

### 3. 问答流程（在线）

```python
def ask_question(self, question: str, stream: bool = False):
    # 步骤1：查询路由——判断查询类型（list/detail/general）
    route_type = self.generation_module.query_router(question)

    # 步骤2：智能查询重写（列表查询保持原样）
    if route_type == 'list':
        rewritten_query = question
    else:
        rewritten_query = self.generation_module.query_rewrite(question)

    # 步骤3：元数据过滤 + 混合检索
    filters = self._extract_filters_from_query(question)
    if filters:
        relevant_chunks = self.retrieval_module.metadata_filtered_search(
            rewritten_query, filters, top_k=self.config.top_k)
    else:
        relevant_chunks = self.retrieval_module.hybrid_search(
            rewritten_query, top_k=self.config.top_k)

    # 步骤4：获取父文档
    relevant_docs = self.data_module.get_parent_documents(relevant_chunks)

    # 步骤5：根据路由类型差异化生成
    if route_type == 'list':
        return self.generation_module.generate_list_answer(question, relevant_docs)
    elif route_type == 'detail':
        return self.generation_module.generate_step_by_step_answer(...)
    else:
        return self.generation_module.generate_basic_answer(...)
```

### 4. 元数据过滤

```python
def _extract_filters_from_query(self, query: str) -> dict:
    filters = {}
    # 提取分类关键词（水产、早餐、甜点、饮品、肉菜等）
    for cat in category_keywords:
        if cat in query:
            filters['category'] = cat
    # 提取难度关键词（简单、中等、困难等）
    for diff in difficulty_keywords:
        if diff in query:
            filters['difficulty'] = diff
    return filters
```

## 关键技术点

1. **父子文档分块**：小块用于精准向量检索，命中后返回完整菜谱文档给 LLM，平衡检索精度与上下文完整性
2. **元数据驱动过滤**：从文件名和内容提取菜品名、分类、难度，检索时结合条件过滤缩小范围
3. **查询路由**：LLM 判断 list/detail/general 三种查询类型，差异化处理——列表查询不重写、详细查询分步指导
4. **查询重写**：对非列表查询，LLM 智能扩展和优化检索词
5. **流式输出**：支持 Streaming 逐 token 返回，降低首字延迟
6. **索引持久化**：FAISS 索引保存到本地，避免每次重新构建

## 学习要点

- RAG 系统的模块化设计：数据、索引、检索、生成四模块解耦，可独立替换升级
- 结构化数据（规整 Markdown）在 RAG 中的优势：元数据提取和过滤显著提升检索精度
- 查询路由不是"锦上添花"，而是根据用户意图选择合适检索和生成策略的核心机制
- 生产级 RAG 需要考虑索引持久化、错误处理、用户交互等工程问题

## 延伸阅读

- [Graph RAG 优化系统](c9-graph-rag.md)——第九章对本系统的图 RAG 升级
- [项目实战概念](../concepts/project-practice.md)——完整架构对比
- [检索进阶技术](../concepts/retrieval-advanced.md)——混合检索和查询路由原理
