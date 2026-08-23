---
type: concept
title: "评估体系"
bundle: /datawhale/all-in-rag
description: "RAG三元组（上下文相关性、忠实度、答案相关性）、检索评估指标（Precision@k/Recall@k/F1/MRR/MAP）、响应评估方法及主流评估工具（RAGAS/TruLens/LlamaIndex Evaluation）"
sources: https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter6/
related:
  - /datawhale/all-in-rag/concepts/rag-overview
  - /datawhale/all-in-rag/concepts/retrieval-advanced
  - /datawhale/all-in-rag/concepts/generation-rerank
tags: [evaluation, ragas, trulens, precision, recall, mrr, faithfulness, context-relevance]
status: stable
---

# 评估体系

## 核心理解

评估是 RAG 开发闭环中的关键环节——"无法度量就无法改进"。第六章围绕 **RAG 三元组（RAG Triad）** 展开，提供了一套科学评估 RAG 系统的方法论和工具集。评估不仅回答"系统好不好"，更能定位"哪个环节出了问题"，是驱动迭代优化的核心机制。

## RAG 三元组

RAG 评估架构包含三个维度：

### 1. 上下文相关性（Context Relevance）

- **评估目标**：检索器（Retriever）的性能
- **核心问题**：检索到的上下文是否与用户查询高度相关？
- **重要性**：检索是 RAG 的第一步，如果上下文充满噪声，后续生成模型再强也无法给出正确答案
- **问题定位**：上下文相关性低 → 优化分块策略、嵌入模型、混合检索、重排

### 2. 忠实度 / 可信度（Faithfulness / Groundedness）

- **评估目标**：生成器的可靠性
- **核心问题**：生成的答案是否完全基于所提供的上下文？
- **重要性**：量化 LLM 的"幻觉"程度。高忠实度意味着模型严格遵守上下文，没有捏造事实
- **问题定位**：忠实度低 → 优化 Prompt 约束、增加重排过滤噪声、调整生成参数

### 3. 答案相关性（Answer Relevance）

- **评估目标**：系统端到端表现
- **核心问题**：最终答案是否直接、完整且有效地回答了用户原始问题？
- **重要性**：用户最直观的感受。答案可能忠实于上下文（高忠实度），但答非所问或只回答了一部分（低答案相关性）
- **问题定位**：答案相关性低 → 查询重写、路由分发、多轮对话管理

> 忠实度关注"是否严格遵循上下文"，答案相关性关注"是否直接回答问题"——两者侧重不同。

## 评估工作流

评估过程拆解为两个主要环节：

### 检索评估（白盒测试）

聚焦上下文相关性，需要标注数据集（查询 + 真实相关文档），使用信息检索经典指标：

- **Precision@k（上下文精确率）**：前 k 个检索结果中相关文档所占比例。高精确率 = 噪声少
  $$P@k = \frac{\text{前k个结果中的相关文档数}}{k}$$

- **Recall@k（上下文召回率）**：前 k 个结果中找到的相关文档占所有真实相关文档的比例。高召回率 = 不遗漏
  $$R@k = \frac{\text{前k个结果中的相关文档数}}{\text{所有相关文档总数}}$$

- **F1-Score**：精确率和召回率的调和平均，兼顾两者
  $$F_1 = 2 \cdot \frac{P \times R}{P + R}$$

- **MRR（Mean Reciprocal Rank，平均倒数排名）**：评估第一个相关文档的排名位置。适用于用户只关心第一个正确答案的场景
  $$MRR = \frac{1}{|Q|}\sum_{q=1}^{|Q|}\frac{1}{rank_q}$$

- **MAP（Mean Average Precision，平均准确率均值）**：综合评估精确率和相关文档排名，先计算每查询的 AP 再取均值

### 响应评估（端到端测试）

覆盖忠实度和答案相关性，通常采用端到端范式：

- **忠实度评估**：检查答案中的每个陈述是否能在上下文中找到依据
- **答案相关性评估**：评估答案是否切题、完整、有效
- 评估方式：LLM-as-Judge（用强 LLM 评分）、人工评估、参考答案对比

## 主流评估工具

### RAGAS

RAGAS（RAG Assessment）是专门针对 RAG 的自动化评估框架，核心指标包括：
- **Faithfulness**：忠实度
- **Answer Relevancy**：答案相关性
- **Context Precision**：上下文精确率
- **Context Recall**：上下文召回率

无需大量标注数据，可利用 LLM 自动生成评估信号。

### TruLens

TruLens 深度应用 RAG 三元组方法论，提供：
- 三个维度的可视化追踪
- 反馈函数（Feedback Functions）机制
- 与 LangChain/LlamaIndex 的集成

### LlamaIndex Evaluation

LlamaIndex 内置评估模块（第六章代码示例使用）：
- 响应评估（Response Evaluation）
- 检索评估（Retrieval Evaluation）
- 批量评估数据集支持

代码示例位于 `code/C6/01_llamaindex_evaluation_example.py`，评估数据集为 `c6_response_eval_dataset.json`。

## 评估驱动的迭代

评估的最终目的是指导优化，形成闭环：

```
构建基线 RAG
  → 三元组评估
    → 上下文相关性低？→ 优化分块/嵌入/混合检索/重排
    → 忠实度低？→ 优化 Prompt/增加重排/降低 temperature
    → 答案相关性低？→ 查询重写/路由/多轮对话
  → 重新评估
  → 指标达标？→ 部署
```

这一闭环在项目实战中得到体现：第八章构建基础 RAG 系统后，第九章通过图 RAG 优化检索能力，正是"评估→定位瓶颈→针对性优化"工程思维的实践。

## 代码实践

第六章代码位于 `code/C6/`：
- `01_llamaindex_evaluation_example.py`——LlamaIndex 评估框架示例
- `c6_response_eval_dataset.json`——响应评估数据集

## 延伸阅读

- [RAG 概述与架构](rag-overview.md)——评估在 RAG 链路中的位置
- [检索进阶技术](retrieval-advanced.md)——检索优化是提升上下文相关性的关键
- [生成与重排](generation-rerank.md)——忠实度与答案相关性的生成侧优化
