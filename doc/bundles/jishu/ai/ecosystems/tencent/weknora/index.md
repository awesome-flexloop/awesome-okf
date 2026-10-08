---
okf_version: "0.2"
type: bundle
title: "腾讯开源 WeKnora：从 RAG 到可演进知识资产"
description: "基于公开博文与腾讯官方资料，梳理 WeKnora 的 AI、数据接入、知识管理能力及开源知识库选型维度"
tags: [WeKnora, 腾讯, RAG, Agent, Wiki, 知识图谱, 技术综述]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-20T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20T12:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article
    resource: https://mp.weixin.qq.com/s/rfeZV_I7BgXaHDLsRM0YNw
    title: "腾讯开源 WeKnora 一出，开源 AI 知识库赛道哀嚎一片"
  - id: official-readme
    resource: https://github.com/Tencent/WeKnora/blob/main/README.md
    title: "Tencent/WeKnora 官方 README"
  - id: official-api
    resource: https://github.com/Tencent/WeKnora/blob/main/docs/api/README.md
    title: "WeKnora 官方 API 文档"
---

# 腾讯开源 WeKnora：从 RAG 到可演进知识资产

> **性质声明**：本 bundle 是技术综述/选型观察，非源码教程、非官方技术文档。文章中的“赛道门槛被抬高”等判断属于作者观点；官方能力核验与边界见 [核验报告](references/verification.md)。

WeKnora 的关键观察点不只是“支持 RAG”，而是把多源数据接入、知识维护和 AI 使用放进同一套开源框架。官方资料支持其文档理解、语义检索、自主推理、Wiki Mode、知识图谱和 REST API 等能力（F-015~F-018）。

## 学习路径

1. [三项能力基础](concepts/00-weknora-capability-foundation.md)：建立 AI、数据接入和知识管理的概念地图。
2. [可演进知识资产](concepts/01-integrated-knowledge-system.md)：理解从导入、索引到 Wiki 维护的闭环。
3. [开源知识库选型维度](concepts/02-open-source-knowledge-base-selection.md)：把文章观点转成可复用的评估检查单。
4. [事实清单](references/article-source.md) 与 [核验报告](references/verification.md)：追溯每项声明。

## 已知边界

- 本文没有可复现实操步骤，因此不设 `examples/`。
- 博文是单篇作者文章，能力清单以官方主分支 README/API 文档交叉核验为准。
- “支持某格式或数据源”不等于在所有版本和部署方式下均达到生产可用。
- `stale_after: 2026-12-31`：WeKnora 主分支和连接器能力持续变化，届时应重新核验。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
