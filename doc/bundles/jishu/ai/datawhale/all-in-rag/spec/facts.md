---
type: spec
title: All-in-RAG 事实清单
bundle: /datawhale/all-in-rag
sources: https://github.com/datawhalechina/all-in-rag
---

# All-in-RAG 事实清单

## 项目元信息

F-001: All-in-RAG 是 Datawhale 开源的 RAG（检索增强生成）技术全栈教程，定位为"大模型应用开发实战一：RAG技术全栈指南"，旨在通过体系化学习路径和动手实践，帮助开发者掌握生产级智能问答和知识检索系统的开发技能。项目负责人为 dalvqw（FutureUnreal）。

F-002: 项目源码位于 `external/libs/ai/datawhalechina/all-in-rag`，文档位于 `docs/` 目录，采用 docsify 架构（`_sidebar.md` + `index.html`），在线阅读地址为 https://datawhalechina.github.io/all-in-rag/。Python 版本要求 3.12.7，支持 Docker 部署向量数据库。

F-003: 项目分为五大部分：RAG基础入门（第1-2章）、索引构建与优化（第3章）、检索技术进阶（第4章）、生成与评估（第5-6章）、高级应用与实战（第7-10章），另含 Extra-chapter 社区扩展章节。全书覆盖从 Naive RAG 到 Graph RAG 的完整技术演进。

F-004: 项目核心亮点包括：体系化学习路径、理论与实践并重、多模态支持（文本+图像检索）、工程化导向（性能优化与系统评估）、丰富实战项目（食谱问答系统）。

## 章节结构（与 _sidebar.md 一致）

F-005: **第一章 解锁RAG**（`docs/chapter1/`）——包含三节：RAG简介（核心定义、双阶段架构、Naive/Advanced/Modular RAG 三阶段演进、RAG vs 微调选型）、准备工作（环境配置、API Key、Docker）、四步构建RAG（LangChain/LlamaIndex 快速上手），附 Python 虚拟环境部署补充。代码位于 `code/C1/`。

F-006: **第二章 数据准备**（`docs/chapter2/`）——包含两节：数据加载（Unstructured 库多格式文档处理：PDF/Word/HTML/Markdown）、文本分块（Character Splitter、Recursive Character Splitter、Semantic Chunker 三种策略对比）。代码位于 `code/C2/`。

F-007: **第三章 索引构建**（`docs/chapter3/`）——包含五节：向量嵌入（BGE 等文本嵌入模型原理与实践）、多模态嵌入（Visual-BGE 图文跨模态检索）、向量数据库（FAISS、Milvus 等选型对比）、Milvus实践（Docker 部署、多模态集合、混合检索）、索引优化（句子窗口检索、递归检索等高级索引策略）。代码位于 `code/C3/`，含 visual_bge 子模块。

F-008: **第四章 检索优化**（`docs/chapter4/`）——包含五节：混合检索（稠密向量+稀疏BM25融合、RRF排序融合）、查询构建（元数据过滤、Text2SQL 自然语言转结构化查询）、Text2SQL（知识库+SQL生成器+Agent 完整实现）、查询重构与分发（LLM-based Routing、Embedding-based Routing）、检索进阶技术（RRF、RankLLM、Cross-Encoder、ColBERT 四种重排方法对比）。代码位于 `code/C4/`，含 text2sql 子模块。

F-009: **第五章 生成集成**（`docs/chapter5/`）——包含一节：格式化生成（Pydantic 结构化输出、Function Calling 函数调用），解决 LLM 输出格式不可控问题。代码位于 `code/C5/`。

F-010: **第六章 RAG系统评估**（`docs/chapter6/`）——包含两节：评估介绍（RAG三元组：上下文相关性、忠实度、答案相关性；检索评估指标 Precision@k/Recall@k/F1/MRR/MAP；响应评估）、评估工具（LlamaIndex Evaluation、RAGAS、TruLens 等主流框架）。代码位于 `code/C6/`。

F-011: **第七章 高级RAG架构（拓展选修篇）**（`docs/chapter7/`）——包含一节：基于知识图谱的RAG（KG-RAG 原理、图谱构建、图检索增强生成）。为 Graph RAG 实战奠定理论基础。

F-012: **第八章 项目实战一（基础篇）**（`docs/chapter8/`）——包含四节：环境配置与项目架构（基于 HowToCook 菜谱数据集的"尝尝咸淡"食谱问答系统）、数据准备模块实现（Markdown 加载、元数据提取、父子文档分块）、索引构建与检索优化（FAISS 向量索引、混合检索、元数据过滤）、生成集成与系统整合（查询路由、查询重写、流式输出、交互式问答）。代码位于 `code/C8/`，含 rag_modules 四模块（data_preparation、index_construction、retrieval_optimization、generation_integration）。

F-013: **第九章 项目实战一优化（选修篇）**（`docs/chapter9/`）——包含四节：图RAG架构设计（Neo4j + Milvus 双引擎）、图数据建模与准备（菜谱-食材-步骤关系图谱）、Milvus索引构建（向量集合管理）、智能查询路由与检索策略（Hybrid Retrieval + Graph RAG Retrieval 双引擎路由、查询复杂度分析）。代码位于 `code/C9/`，含 rag_modules 六模块（graph_data_preparation、graph_indexing、graph_rag_retrieval、hybrid_retrieval、intelligent_query_router、milvus_index_construction、generation_integration）及 AI 生成的 Agent 代码。

F-014: **第十章 项目实战二（选修篇）**——规划中，尚未发布内容。

F-015: **Extra-chapter**（`Extra-chapter/`）——社区扩展章节，包含 PowerRAG-SDK-Text-QA、Neo4J 简单应用、多模态 Omni Embedding 实践（Jina v5-omni）等社区贡献内容。

## 代码资产

F-016: 第一章代码（`code/C1/`）——`01_langchain_example.py`（LangChain RAG 快速上手）、`02_llamaIndex_example.py`（LlamaIndex RAG 快速上手）、`fix_nltk.py`（NLTK 数据修复）。

F-017: 第二章代码（`code/C2/`）——`01_unstructured_example.py`（多格式文档加载）、`02_character_splitter.py`（字符分块）、`03_recursive_character_splitter.py`（递归字符分块）、`04_semantic_chunker.py`（语义分块）。

F-018: 第三章代码（`code/C3/`）——`01_bge_visualized.py`（BGE 嵌入可视化）、`02_langchain_faiss.py`（LangChain + FAISS）、`03_llamaindex_vector.py`（LlamaIndex 向量检索）、`04_multi_milvus.py`（Milvus 多模态）、`05_sentence_window_retrieval.py`（句子窗口检索）、`06_recursive_retrieval.py`/`07_recursive_retrieval_v2.py`（递归检索）、`work_hybrid_multimodal_search.py`/`work_multimodal_dragon_search.py`（多模态混合检索作业），含 visual_bge 模型子模块。

F-019: 第四章代码（`code/C4/`）——`01_hybrid_search.py`/`01_hybrid_search_v2.py`（混合检索）、`02_text_to_metadata_filter.py`/`04_text_to_metadata_filter_v2.py`（元数据过滤）、`03_text2sql_demo.py`/`03_text2sql_demo_v2.py`（Text2SQL 演示）、`05_llm_based_routing.py`（LLM 路由）、`06_embedding_based_routing.py`（Embedding 路由）、`07_rerank_and_refine.py`/`work_rerank_and_refine.py`（重排优化），含 text2sql 子模块（knowledge_base、sql_generator、text2sql_agent）。

F-020: 第五章代码（`code/C5/`）——`01_pydantic.py`（Pydantic 结构化输出）、`02_function_calling_example.py`（Function Calling 示例）。

F-021: 第六章代码（`code/C6/`）——`01_llamaindex_evaluation_example.py`（LlamaIndex 评估示例）、`c6_response_eval_dataset.json`（评估数据集）。

F-022: 第八章代码（`code/C8/`）——完整食谱 RAG 系统：`config.py`（配置管理）、`main.py`（RecipeRAGSystem 主类，含查询路由、元数据过滤、混合检索、流式输出）、`rag_modules/data_preparation.py`（Markdown 加载、元数据提取、父子文档分块）、`rag_modules/index_construction.py`（FAISS 向量索引）、`rag_modules/retrieval_optimization.py`（混合检索）、`rag_modules/generation_integration.py`（Kimi API 调用、查询路由、重写）。使用 Kimi（Moonshot）API 作为 LLM。

F-023: 第九章代码（`code/C9/`）——图 RAG 优化版：`config.py`（GraphRAGConfig）、`main.py`（AdvancedGraphRAGSystem 主类，含智能路由、双引擎检索）、`rag_modules/graph_data_preparation.py`（Neo4j 图数据准备）、`rag_modules/graph_indexing.py`（图索引）、`rag_modules/graph_rag_retrieval.py`（图 RAG 检索、多跳遍历、子图提取）、`rag_modules/hybrid_retrieval.py`（混合检索）、`rag_modules/intelligent_query_router.py`（查询复杂度分析、策略路由）、`rag_modules/milvus_index_construction.py`（Milvus 向量索引）、`rag_modules/generation_integration.py`（自适应回答生成）。另含 `agent(代码系ai生成)/` 目录（AI 生成的菜谱 Agent，含 amount_normalizer、batch_manager、recipe_ai_agent 等）。

## 技术栈与工具

F-024: 核心框架与工具包括：LangChain、LlamaIndex（RAG 编排框架）；FAISS、Milvus（向量数据库，Milvus 通过 Docker 部署）；Neo4j（图数据库，第九章 Graph RAG 使用）；BGE、Visual-BGE（嵌入模型）；Kimi/Moonshot API（LLM，第八章实战使用）；Unstructured（文档加载）；Pydantic（结构化输出）；RAGAS、TruLens、LlamaIndex Evaluation（评估工具）。

F-025: 项目提供 `code/docker-compose.yml` 一键部署 Milvus 等向量数据库服务，`code/requirements.txt` 统一管理基础依赖，各章节代码目录可独立安装依赖。

## 学习路径

F-026: 基础路径：第1章 RAG 概念与快速上手 → 第2章 数据加载与分块 → 第3章 嵌入与向量索引 → 第4章 检索优化 → 第5章 生成集成 → 第6章 评估，构成完整的 Naive→Advanced RAG 技术链。

F-027: 进阶路径：第7章 知识图谱 RAG 理论 → 第8章 基础实战（食谱 RAG 系统）→ 第9章 Graph RAG 优化（Neo4j+Milvus 双引擎、智能路由），从单引擎向量检索演进到多引擎图结构推理。
