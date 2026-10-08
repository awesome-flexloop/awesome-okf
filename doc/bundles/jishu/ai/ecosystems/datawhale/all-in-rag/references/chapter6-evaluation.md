---
type: reference
title: "第六章 RAG系统评估"
bundle: /datawhale/all-in-rag
description: "RAG三元组评估方法论（上下文相关性/忠实度/答案相关性）、检索评估指标（Precision@k/Recall@k/F1/MRR/MAP）、响应评估及主流工具（RAGAS/TruLens/LlamaIndex Evaluation）"
source: https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter6/
path: docs/chapter6/
code:
  - code/C6/
tags: [evaluation, ragas, trulens, llamaindex, precision, recall, mrr, faithfulness]
status: stable
---

# 第六章 RAG系统评估

## 信源信息

- **章节路径**：`docs/chapter6/`
- **代码路径**：`code/C6/`
- **小节列表**：
  - 第一节 评估介绍（`18_system_evaluation.md`）
  - 第二节 评估工具（`19_common_tools.md`）

## 内容概要

### 第一节 评估介绍

**RAG 三元组（RAG Triad）**：

1. **上下文相关性（Context Relevance）**：评估检索器性能——检索到的上下文是否与查询相关
2. **忠实度（Faithfulness/Groundedness）**：评估生成器可靠性——答案是否完全基于上下文，量化幻觉程度
3. **答案相关性（Answer Relevance）**：评估端到端表现——答案是否直接、完整、有效回答问题

**检索评估指标**（白盒测试，需标注数据集）：
- Precision@k（上下文精确率）
- Recall@k（上下文召回率）
- F1-Score（精确率与召回率调和平均）
- MRR（Mean Reciprocal Rank，平均倒数排名）
- MAP（Mean Average Precision，平均准确率均值）

**响应评估**（端到端测试）：忠实度评估 + 答案相关性评估，可采用 LLM-as-Judge、人工评估、参考答案对比。

### 第二节 评估工具

- **RAGAS**：RAG 专用自动化评估框架，核心指标 Faithfulness/Answer Relevancy/Context Precision/Context Recall
- **TruLens**：深度应用 RAG 三元组，提供反馈函数和可视化追踪
- **LlamaIndex Evaluation**：内置响应评估和检索评估模块，支持批量评估数据集

## 代码资产

| 文件 | 职责 |
|------|------|
| `code/C6/01_llamaindex_evaluation_example.py` | LlamaIndex 评估框架示例 |
| `code/C6/c6_response_eval_dataset.json` | 响应评估数据集 |

## 对应概念

- [评估体系](../concepts/evaluation-system.md)
