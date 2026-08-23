---
type: reference
title: "第一章 解锁RAG"
bundle: /datawhale/all-in-rag
description: "RAG核心概念、技术原理、三阶段演进（Naive/Advanced/Modular）、环境准备与LangChain/LlamaIndex四步快速上手"
source: https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter1/
path: docs/chapter1/
code:
  - code/C1/
tags: [rag-intro, architecture, langchain, llamaindex, environment]
status: stable
---

# 第一章 解锁RAG

## 信源信息

- **章节路径**：`docs/chapter1/`
- **代码路径**：`code/C1/`
- **小节列表**：
  - 第一节 RAG简介（`01_RAG_intro.md`）
  - 第二节 准备工作（`02_preparation.md`）
  - 第三节 四步构建RAG（`03_get_start_rag.md`）
  - 附：Python虚拟环境部署方案补充（`virtualenv.md`）

## 内容概要

### 第一节 RAG简介

- **核心定义**：RAG 将 LLM 的参数化知识与外部知识库的非参数化知识结合，生成前先检索相关信息
- **双阶段架构**：检索阶段（知识向量化→语义召回）+ 生成阶段（上下文整合→指令引导生成）
- **技术演进三阶段**：
  - Naive RAG：离线索引→在线检索→生成，基础线性流程
  - Advanced RAG：增加检索前（查询重写）和检索后（结果重排）优化
  - Modular RAG：积木式可编排，动态路由、查询转换、多路融合
- **RAG vs 微调**：知识更新、可解释性、成本、适用场景对比

### 第二节 准备工作

- Python 环境配置（3.12.7）
- API Key 申请与配置（Kimi/Moonshot 等）
- Docker 安装与向量数据库部署准备

### 第三节 四步构建RAG

- LangChain 快速上手示例
- LlamaIndex 快速上手示例
- 体验完整 RAG 流程：加载文档→构建索引→检索→生成

## 代码资产

| 文件 | 职责 |
|------|------|
| `code/C1/01_langchain_example.py` | LangChain RAG 快速上手 |
| `code/C1/02_llamaIndex_example.py` | LlamaIndex RAG 快速上手 |
| `code/C1/fix_nltk.py` | NLTK 数据修复工具 |

## 对应概念

- [RAG 概述与架构](../concepts/rag-overview.md)
