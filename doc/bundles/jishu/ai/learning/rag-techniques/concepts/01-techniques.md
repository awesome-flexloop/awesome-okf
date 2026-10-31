---
okf_version: "0.2"
type: concept
title: RAG 技术机制详解——七段 pipeline 与代表性架构
description: 42 篇 notebook 的七段分类机制、Graph RAG 双阶段双路扩图、LightRAG 双层关键词（F-007~F-011、F-021~F-024）
tags: [rag, graph-rag, lightrag, retrieval, chunking, reranking]
generated:
  by: seven-concepts-cmd
  at: "2026-10-31T11:00:00+08:00"
sources:
  - id: blog-article
    url: https://mp.weixin.qq.com/s/WsgnBpEtTytatRFkKUlfeA
  - id: github-rag-techniques
    url: https://github.com/NirDiamant/RAG_Techniques
---

# RAG 技术机制详解

> **口径提示**：本篇的机制解说（Graph RAG 双路扩图、LightRAG 双层关键词）为**博文作者对仓库特定 notebook 实现的解读**（F-021~F-024），非仓库官方文档口径；技术分类与篇目名为仓库 README 口径（F-051）。

## 为什么要按 pipeline 分段

常规 RAG 排查的困境：文档明明在库里、用户问的也是文档里的原话，模型答出来就是偏的。网友给的招数通常是「换 embedding 模型」「调 chunk size」「把 top_k 从 3 加到 10」，但试完一轮会发现「两三个问题好了，更多的问题又冒出来」，且「没人说得清为什么好了」（F-022 语境）。

博文的判断：**RAG 的坑不在于难，在于没有对照表**——不确定自己踩的是哪一类，就只能一个个试。本仓库的价值正是把失败模式摊开，按 pipeline 阶段归类。

## 七段 pipeline（归并视图）

| 段 | 篇数 | 解决的问题域 |
|----|------|-------------|
| 基础 | 6 | 最小可用 RAG 起点、数据形态（CSV）、chunk 大小选择、切分策略（命题切分）、文档解析（Mistral OCR） |
| 查询改写 | 3 | 用户问题与文档表述不对齐——查询变换、HyDE（假设性文档）、HyPE（假设性提问） |
| 上下文增强 | 6 | 检索到的块缺上下文——块头上下文、相关片段抽取、窗口扩展、语义切分、上下文压缩、文档增强 |
| 高级检索 | 6 | 单路向量相似度召回不足——融合检索、重排序、多面过滤、层级索引、飞镖盘检索、多模态描述 |
| 迭代与自适应 | 2 | 一次检索不够——反馈回路、自适应检索 |
| 评估 | 4 | 效果无法量化——DeepEval、GroUSE、端到端评估、Open-RAG-Eval |
| 进阶架构 | 8 | 多跳、可验证、自适应等复杂需求——Graph RAG、微软 GraphRAG、RAPTOR、Agentic RAG、Self-RAG、CRAG、可验证归因的本地 Graph RAG、LightRAG |

> ⚠️ 七段篇数之和为 35，与 42 个 `.ipynb` 不等，详见 [00-intro](./00-intro.md#组织结构七段-pipeline-归并视图) 的口径说明（F-007 / F-051）。

## 代表性架构一：Graph RAG（双阶段 + 双路扩图）

**问题**：常规 RAG 的检索是一次向量相似度，遇到「A 公司的 CEO 之前在哪家公司」这类**多跳问题**向量检索会散——因为答案不在任何一个和问题最像的块里（F-022）。

**仓库实现的机制**（F-021）：

```{mermaid}
flowchart TD
    subgraph 离线加载
        A1[语料] --> A2[抽实体和关系] --> A3[(建库)]
    end
    subgraph 在线检索
        B1[Query] --> B2[向量库]
        B2 --> C1[实体检索: 命中节点后向外扩 1 度邻居]
        B2 --> C2[关系检索: 命中边后同样扩 1 度]
        C1 --> D[合并两路子图]
        C2 --> D
        D --> E[LLM 重排]
        E --> F[生成]
    end
    A3 --> B2
```

设计意图的解读：**实体解决「这个词指的是谁」，关系解决「它们之间怎么连」**。纯向量只做前者，多跳问题必然断——这也是图检索在关系型问答上比纯向量稳的原因（F-021）。

## 代表性架构二：LightRAG（双层关键词）

LightRAG 的实现更轻（F-023）：

1. **索引阶段**：抽实体和关系，建**实体索引**与**关系索引**两个向量索引；
2. **检索阶段**：不直接拿用户问题去查，而是先让 LLM 把问题拆成 **low-level 关键词** 与 **high-level 关键词**，分别查两个索引，最后组装上下文。

- low-level 对应**具体实体**（人名、产品名）；
- high-level 对应**抽象主题**（行业、趋势）；
- 该拆法出自 LightRAG 论文，notebook 中完整实现（F-024）。

好处：**不用建完整图数据库，成本比 Graph RAG 低一截**。

## 评估与进阶架构

- **评估段（4 篇）**：DeepEval、GroUSE、端到端评估、Open-RAG-Eval——对应「效果无法量化」这一失效模式；
- **进阶架构段（8 篇）**：Graph RAG / 微软 GraphRAG / RAPTOR / Agentic RAG / Self-RAG / CRAG / 可验证归因的本地 Graph RAG / LightRAG——对应多跳、自适应、可验证归因等复杂需求。

> 仓库最近新增内容包括 Mistral OCR 4 文档解析、MemoRAG、端到端评估、JSON RAG（F-019，时点性信息）。

## 主题关联

- [00-intro](./00-intro.md)：项目定位、双轨设计与组织结构
- [02-practice](./02-practice.md)：安装现状、企业落地四步与边界约束
