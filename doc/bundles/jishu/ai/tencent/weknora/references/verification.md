---
type: Reference
title: "WeKnora 核验报告"
description: "对博文能力声明进行官方 README 与 API 文档交叉核验，并记录作者观点边界"
tags: [WeKnora, 官方核验, README, API]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-20T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20T12:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: official-readme
    resource: https://github.com/Tencent/WeKnora/blob/main/README.md
  - id: official-api
    resource: https://github.com/Tencent/WeKnora/blob/main/docs/api/README.md
---

# WeKnora 核验报告

## 核验结论

| 范围 | 结论 | 说明 |
|---|---|---|
| 项目定位 | ✅ | 官方 README 支持文档理解、语义检索和自主推理的定位（F-015）。 |
| RAG/Agent/Wiki | ✅ | 官方 README 明确列出三种能力及知识图谱、修订历史和回滚（F-016）。 |
| 多源接入与格式 | ✅ | 官方 README 列出文章所述主要数据源，并概括为 10+ 文档格式（F-017）。 |
| Chunk 管理 | ⚠️ | 官方 README 支持 chunk 编辑、差异和回滚；博文的“重新建立索引”未在本轮 README 片段中逐字核对，正文以“支持维护与版本操作”表述。 |
| REST API | ✅ | 官方 API 文档列出知识库、检索、模型、分块、Agent、聊天等 API，以及 `/api/v1` 和 `X-API-Key`（F-018）。 |
| 赛道门槛上升 | 不适用 | 这是作者分析，不是可由官方文档证实的产品事实。 |

## 勘误与边界

本次未发现文章中的数字、日期或版本号硬错误；文章没有给出价格、性能倍数或市场份额等 P0 数字。需要保留的边界有三项：

1. “三项核心基础”“数据汇聚平台”“赛道门槛抬高”是作者分析框架。
2. 官方 README 的能力清单随主分支更新，本文核验以 2026-09-20 读取结果为准。
3. “支持某格式/数据源”不等于每个连接器在所有部署方式下均已达到生产可用程度。

