---
type: Concept
title: "WeKnora 的三项能力基础"
description: "从 AI、数据接入和知识管理三个维度理解 WeKnora 的产品边界"
tags: [WeKnora, RAG, Agent, 知识管理]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-20T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20T12:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: article-source
    resource: /references/article-source.md
  - id: official-readme
    resource: https://github.com/Tencent/WeKnora/blob/main/README.md
---

# WeKnora 的三项能力基础

> 本文是技术综述，不是官方产品文档。F-002 的“三项基础”是作者的分析框架；F-015~F-017 是官方资料核验后的能力边界。

作者将 WeKnora 拆成三项基础：**AI 能力、数据导入与接入、知识管理**（F-002）。这个拆分有助于避免把知识库理解成单一的“上传 PDF 后问答”界面。

## AI 能力

博文列举了 Embedding、全文检索、向量检索、混合检索、Rerank、Query Rewrite、Agent 和知识图谱（F-003）。官方 README 进一步将产品定位为支持 RAG 快速问答、ReAct Agent 与 Wiki Mode 的 LLM 知识框架（F-015、F-016）。

因此可以把 AI 能力理解成从召回到任务执行的连续层次：

```text
模型配置 → 查询改写 → 多路检索 → 重排 → RAG 生成 → Agent 工具编排 → Wiki/图谱组织
```

上图是解释性抽象，不是官方内部调用顺序。

## 数据接入

文章列举多种文档格式和外部数据源（F-006、F-007）。官方 README 也列出 Feishu、GitLab、腾讯 IMA、Notion、语雀、钉钉文档、RSS 等来源，并概括支持 10+ 文档格式（F-017）。这说明知识库的输入边界不应只看本地文件上传，而应看持续同步能力。

## 知识管理

文章列举 Document、FAQ、Wiki、文件夹、标签、在线录入和 Chunk 管理（F-009、F-010、F-011）。官方资料明确支持 Wiki、知识图谱、人工编辑、修订历史和回滚（F-016）。因此，知识进入检索链路后仍应有维护、追踪和回退机制。
