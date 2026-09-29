---
type: Concept
title: "OpenSEO：软件开源与数据按量付费"
description: "将关键词、排名、竞品、反链、审计和 AI 可见性工作流自托管，并通过 MCP 暴露给 Agent"
tags: [OpenSEO, SEO, MCP, DataForSEO]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-11-30
sources:
  - { id: article, resource: "/references/article-source.md" }
  - { id: github, resource: "https://github.com/every-app/open-seo" }
  - { id: site, resource: "https://openseo.so/" }
---

# OpenSEO：软件开源与数据按量付费

OpenSEO 将关键词研究、排名追踪、竞品、反向链接、站点审计和 AI 可见性放入一个可自托管工作区，并通过 MCP 与 Agent 连接。[F-021][F-023]

关键架构边界是：OpenSEO 提供界面、工作流、存储和 Agent 接口；SEO 数据依赖 DataForSEO key。[F-024] 因此它把 Semrush/Ahrefs 的固定套件费拆成软件自托管、上游数据按量、部署与维护几层，不能宣传为零成本或覆盖等价。

## 选择标准

适合愿意管理 key、部署和预算的人；不适合需要开箱即用、统一数据覆盖和企业 SLA 的团队。Docker 适合本地试用，Cloudflare 更适合公开部署，但默认本地无认证模式不能直接暴露公网。[F-025]

文章中的 129–139 美元套件价格、10 美元托管版和 28% 加价均需按当前官方计划与 DataForSEO 账单复核。[F-028][F-030]
