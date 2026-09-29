---
type: concept
title: "RAG 概述与架构"
bundle: /datawhale/all-in-rag
description: "检索增强生成（RAG）的核心定义、双阶段架构、Naive/Advanced/Modular 三阶段演进，以及 RAG 与微调的技术选型"
sources: https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter1/01_RAG_intro.md
related:
  - /datawhale/all-in-rag/concepts/data-preparation
  - /datawhale/all-in-rag/concepts/index-construction
  - /datawhale/all-in-rag/concepts/retrieval-advanced
  - /datawhale/all-in-rag/concepts/generation-rerank
  - /datawhale/all-in-rag/concepts/evaluation-system
tags: [rag, architecture, naive-rag, advanced-rag, modular-rag, llm]
status: stable
---

# RAG 概述与架构

## 核心理解

RAG（Retrieval-Augmented Generation，检索增强生成）是一种将 LLM 的**参数化知识**（模型权重中固化的记忆）与外部知识库的**非参数化知识**（精准、可更新的外部数据）相结合的技术范式。其运作逻辑是在 LLM 生成文本前，先通过检索机制从外部知识库动态获取相关信息，并将这些"参考资料"融入生成过程，从而提升输出的准确性和时效性。

> 一句话总结：RAG 就是让 LLM 学会"开卷考试"，既能利用自身知识，也能随时查阅外部资料。

## 双阶段架构

RAG 系统通过两个阶段完成知识融合：

### 检索阶段：寻找"非参数化知识"

1. **知识向量化**：嵌入模型（Embedding Model）将外部知识库编码为向量索引，存入向量数据库
2. **语义召回**：用户发起查询时，检索模块利用同样的嵌入模型将问题向量化，通过相似度搜索从海量数据中锁定最相关的文档片段

### 生成阶段：融合两种知识

1. **上下文整合**：生成模块接收检索到的文档片段和用户原始问题
2. **指令引导生成**：遵循预设 Prompt 指令，将上下文与问题整合，引导 LLM 进行可控的、有理有据的文本生成

## RAG 技术演进三阶段

| 维度 | 初级 RAG（Naive RAG） | 高级 RAG（Advanced RAG） | 模块化 RAG（Modular RAG） |
|------|----------------------|------------------------|------------------------|
| 流程 | 离线：索引；在线：检索→生成 | 离线：索引；在线：...→检索前→...→检索后→... | 积木式可编排流程 |
| 特点 | 基础线性流程 | 增加检索前后优化步骤 | 模块化、可组合、可动态调整 |
| 关键技术 | 基础向量检索 | 查询重写、结果重排 | 动态路由、查询转换、多路融合 |
| 局限性 | 效果不稳定，难以优化 | 流程相对固定，优化点有限 | 系统复杂性高 |

"离线"指提前完成的数据预处理（如索引构建）；"在线"指用户发起请求后的实时处理流程。

## RAG vs 微调

| 维度 | RAG | 微调（SFT/LoRA） |
|------|-----|-----------------|
| 知识更新 | 实时更新文档库即可 | 需要重新训练 |
| 可解释性 | 答案可溯源到文档 | 黑盒，难以解释 |
| 成本 | 检索成本低，无需训练 | 训练成本较高 |
| 适用场景 | 动态知识、事实问答 | 风格对齐、能力习得 |
| 幻觉控制 | 显著降低 | 无法根本解决 |

实际应用中 RAG 和微调常结合使用：微调让模型学会特定领域表达方式和工具使用，RAG 提供实时准确的知识来源。

## 在 All-in-RAG 中的位置

第一章是全书的起点，建立 RAG 的核心概念框架。后续章节沿"数据准备→索引构建→检索优化→生成集成→评估"的链路逐层深入，最终在第8-9章通过实战项目将所有概念串联为完整系统。

## 延伸阅读

- [数据准备与处理](data-preparation.md)——RAG 链路的第一环
- [索引构建](index-construction.md)——向量嵌入与向量数据库
- [检索进阶技术](retrieval-advanced.md)——从 Naive 到 Advanced RAG
- [评估体系](evaluation-system.md)——RAG 三元组方法论
