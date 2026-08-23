---
okf_version: "0.2"
type: index
title: "All-in-RAG：RAG技术全栈指南"
bundle: all-in-rag
description: "Datawhale 开源的 RAG 技术全栈教程——从 RAG 基础概念到数据准备、索引构建、检索进阶、生成优化、系统评估，最终通过食谱问答项目实战完成从基础 RAG 到 Graph RAG 的技术跃迁"
concepts:
  - /datawhale/all-in-rag/concepts/rag-overview
  - /datawhale/all-in-rag/concepts/data-preparation
  - /datawhale/all-in-rag/concepts/index-construction
  - /datawhale/all-in-rag/concepts/retrieval-advanced
  - /datawhale/all-in-rag/concepts/generation-rerank
  - /datawhale/all-in-rag/concepts/evaluation-system
  - /datawhale/all-in-rag/concepts/project-practice
references:
  - /datawhale/all-in-rag/references/chapter1-rag-intro
  - /datawhale/all-in-rag/references/chapter2-data-preparation
  - /datawhale/all-in-rag/references/chapter3-index-construction
  - /datawhale/all-in-rag/references/chapter4-retrieval-optimization
  - /datawhale/all-in-rag/references/chapter5-generation
  - /datawhale/all-in-rag/references/chapter6-evaluation
  - /datawhale/all-in-rag/references/chapter7-advanced-rag
  - /datawhale/all-in-rag/references/chapter8-project-basic
  - /datawhale/all-in-rag/references/chapter9-project-graph-rag
  - /datawhale/all-in-rag/references/chapter10-project-two
examples:
  - /datawhale/all-in-rag/examples/c8-basic-rag
  - /datawhale/all-in-rag/examples/c9-graph-rag
sources: https://github.com/datawhalechina/all-in-rag
generated:
  by: okf-wiki-bot
  at: "2026-08-23T00:00:00Z"
verified:
  by: process:seven-concepts-v
  at: "2026-08-23T00:00:00Z"
status: stable
stale_after: "2027-08-23"
---

# All-in-RAG：RAG技术全栈指南

[All-in-RAG](https://github.com/datawhalechina/all-in-rag) 是 Datawhale 开源的 RAG（检索增强生成）技术全栈教程，定位为"大模型应用开发实战一：RAG技术全栈指南"。全书 10 章，从 RAG 核心概念出发，沿"数据准备→索引构建→检索优化→生成集成→系统评估"的完整链路逐层深入，最终通过"尝尝咸淡"食谱问答系统的两个版本（基础 RAG 与 Graph RAG），将理论知识串联为生产级可运行系统。

## 知识地图

```
📖 基础入门（第1-2章）
  ├── 解锁RAG → 核心定义、双阶段架构、Naive/Advanced/Modular三阶段演进
  └── 数据准备 → 多格式文档加载、Character/Recursive/Semantic三种分块策略
        ↓
🗂️ 索引与检索（第3-4章）
  ├── 索引构建 → BGE嵌入、Visual-BGE多模态、FAISS/Milvus、句子窗口/递归检索
  └── 检索优化 → 混合检索(稠密+稀疏)、Text2SQL、查询路由、RRF/Cross-Encoder/ColBERT重排
        ↓
🤖 生成与评估（第5-6章）
  ├── 生成集成 → Pydantic结构化输出、Function Calling、查询路由差异化生成
  └── 系统评估 → RAG三元组(上下文相关性/忠实度/答案相关性)、RAGAS/TruLens
        ↓
🚀 高级实战（第7-10章）
  ├── 高级RAG架构 → 知识图谱RAG(KG-RAG)理论
  ├── 项目实战一(基础) → FAISS+LangChain+Kimi食谱问答系统
  ├── 项目实战一(优化) → Neo4j+Milvus双引擎Graph RAG、智能路由、多跳推理
  └── 项目实战二 → 规划中
```

## 核心概念（concepts/）

* [RAG 概述与架构](concepts/rag-overview.md) — RAG 核心定义、双阶段架构、Naive/Advanced/Modular 三阶段演进、RAG vs 微调选型。对应第一章。
* [数据准备与处理](concepts/data-preparation.md) — Unstructured 多格式加载、三种分块策略、父子文档分块。对应第二章。
* [索引构建](concepts/index-construction.md) — BGE 向量嵌入、Visual-BGE 多模态嵌入、FAISS/Milvus 向量数据库、句子窗口与递归检索。对应第三章。
* [检索进阶技术](concepts/retrieval-advanced.md) — 混合检索、Text2SQL、查询重写与路由、RRF/RankLLM/Cross-Encoder/ColBERT 四种重排。对应第四章。
* [生成与重排](concepts/generation-rerank.md) — Pydantic 结构化输出、Function Calling、查询路由驱动差异化生成、重排与生成协同。对应第五章。
* [评估体系](concepts/evaluation-system.md) — RAG 三元组方法论、Precision@k/Recall@k/F1/MRR/MAP 指标、RAGAS/TruLens/LlamaIndex 工具。对应第六章。
* [项目实战](concepts/project-practice.md) — 从基础 RAG（C8）到 Graph RAG（C9）的完整实战，Neo4j+Milvus 双引擎与智能路由。对应第八、九章。

## 实战示例（examples/）

* [基础RAG食谱问答系统](examples/c8-basic-rag.md) — 第八章 `code/C8/`：FAISS + LangChain + Kimi，涵盖父子文档分块、混合检索、元数据过滤、查询路由、流式生成全链路。
* [Graph RAG食谱问答系统](examples/c9-graph-rag.md) — 第九章 `code/C9/`：Neo4j 知识图谱 + Milvus 向量库双引擎，支持智能查询路由、多跳推理、子图提取与自适应生成。

## 信源登记（references/）

* [第一章 解锁RAG](references/chapter1-rag-intro.md) — RAG 概念、架构、三阶段演进、快速上手。
* [第二章 数据准备](references/chapter2-data-preparation.md) — 数据加载与文本分块。
* [第三章 索引构建](references/chapter3-index-construction.md) — 向量嵌入、多模态嵌入、向量数据库、索引优化。
* [第四章 检索优化](references/chapter4-retrieval-optimization.md) — 混合检索、查询构建、Text2SQL、重排技术。
* [第五章 生成集成](references/chapter5-generation.md) — 格式化生成、Pydantic、Function Calling。
* [第六章 RAG系统评估](references/chapter6-evaluation.md) — RAG 三元组、评估指标、评估工具。
* [第七章 高级RAG架构（拓展选修篇）](references/chapter7-advanced-rag.md) — 知识图谱 RAG 理论。
* [第八章 项目实战一（基础篇）](references/chapter8-project-basic.md) — 基础食谱 RAG 系统。
* [第九章 项目实战一优化（选修篇）](references/chapter9-project-graph-rag.md) — Graph RAG 优化系统。
* [第十章 项目实战二（选修篇）](references/chapter10-project-two.md) — 规划中。

## 深度洞察

本知识束的设计决策与核心洞察详见 [spec/insights.md](spec/insights.md)，包括：

1. **RAG 全栈链路——从数据到生成的模块化工程**——数据→索引→检索→生成→评估的可独立优化链路，RAG 三元组精准定位瓶颈
2. **检索与生成的解耦——RAG 的架构基石**——知识可更新、能力可组合、幻觉可控制，从 Naive 到 Modular 的解耦深化
3. **评估驱动的迭代闭环——RAG 三元组方法论**——评估→定位→优化→再评估的白盒可观测迭代
4. **从基础到进阶 RAG——向量检索到图结构推理的技术跃迁**——Naive→Advanced→Modular→Graph RAG 的复杂度递进曲线

## 目录结构

```
all-in-rag/
├── spec/
│   ├── facts.md              # 章节结构与代码资产事实清单（27条事实）
│   └── insights.md           # 4 个核心设计洞察
├── concepts/                 # 7 个核心概念
│   ├── index.md
│   ├── rag-overview.md
│   ├── data-preparation.md
│   ├── index-construction.md
│   ├── retrieval-advanced.md
│   ├── generation-rerank.md
│   ├── evaluation-system.md
│   └── project-practice.md
├── examples/                 # 2 个综合实战示例
│   ├── index.md
│   ├── c8-basic-rag.md
│   └── c9-graph-rag.md
├── references/               # 10 章信源登记
│   ├── index.md
│   └── chapter1-10 ... .md
├── index.md                  # 本文件
└── log.md                    # 更新日志
```

---

> **源码位置**：`external/libs/ai/datawhalechina/all-in-rag/`
>
> **在线阅读**：https://datawhalechina.github.io/all-in-rag/
>
> **开源协议**：CC BY-NC-SA 4.0
>
> **生成时间**：2026-08-23 | **维护者**：OKF Wiki Bot
