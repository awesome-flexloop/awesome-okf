---
type: reference
title: "第七章 高级RAG架构（拓展选修篇）"
bundle: /datawhale/all-in-rag
description: "基于知识图谱的RAG（KG-RAG）原理，图谱构建、图检索增强生成，为Graph RAG实战奠定理论基础"
source: https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter7/
path: docs/chapter7/
code: []
tags: [kg-rag, knowledge-graph, graph-rag, advanced-rag, neo4j]
status: stable
---

# 第七章 高级RAG架构（拓展选修篇）

## 信源信息

- **章节路径**：`docs/chapter7/`
- **代码路径**：无独立代码（理论章节，实战见第九章）
- **小节列表**：
  - 第一节 基于知识图谱的RAG（`20_kg_rag.md`）

## 内容概要

### 第一节 基于知识图谱的RAG

- **KG-RAG 动机**：向量检索擅长语义匹配但无法捕捉实体间显式关系，知识图谱补充结构化关系信息
- **知识图谱构建**：实体抽取、关系抽取、图谱存储（Neo4j）
- **图检索增强**：基于图结构的遍历、多跳推理、子图提取
- **Graph RAG 架构**：向量检索与图检索的结合，为第九章实战提供理论基础

## 对应概念

- [项目实战](../concepts/project-practice.md)——第九章 Graph RAG 实战
- [检索进阶技术](../concepts/retrieval-advanced.md)——查询路由与多路融合
