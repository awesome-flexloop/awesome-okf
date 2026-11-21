---
okf_version: "0.2"
type: Concept
title: "Univer 是什么：身份、谱系与信源距离"
description: "Univer 的项目身份、Luckysheet 谱系、许可证、Star 时点与信源距离判定（事实层，动态数字均带核验时点）"
tags: [univer, office-sdk, project-profile, provenance, apache-2.0]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-11-20T10:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/7WCDC4R7mxqFRHMP0Zf9hA
  - id: github-api
    url: https://api.github.com/repos/dream-num/univer
  - id: official-readme
    url: https://github.com/dream-num/univer/blob/dev/README.md
---

# Univer 是什么：身份、谱系与信源距离

> 事实层（What / When / Who）。本文只陈述可核验事实；作者观点见 [05-选型与可迁移模式](05-selection-and-transferable-patterns.md)，逐条核验见 [核验报告](../references/verification.md)。

## 一句话定位

[Univer](https://github.com/dream-num/univer) 是一套**嵌入式的 Office SDK**：把电子表格与文档编辑能力放进自己的产品，数据、权限和持久化都由应用侧掌握（F-004/F-058）。官方仓库自述为：

> "Build your own AI office with Univer Office SDK. Bring editing, calculation, collaboration, and file processing into your product **for people and AI agents**. Built on an extensible open-source core."（F-058）

请留意后半句——**"人和 AI agent 共用"是官方定位，不是推介文的发挥**。这也是本知识包归入 AI 产品域、并在 [04-agent-governance](04-agent-governance-and-ecosystem.md) 单独讨论 agent 治理的依据。

## 身份卡片

| 项目 | 值 | 出处 |
|------|-----|------|
| 仓库 / 归属 | `dream-num/univer`，owner 为 Organization（非个人号） | F-056 |
| 创建时间 | 2022-09-29（GitHub API `created_at`）；默认分支 `dev`，未归档 | F-056 |
| 主语言 | TypeScript | F-003/F-056 |
| 许可证 | **Apache-2.0**（`license.spdx_id`），可用于商业应用 | F-003/F-056/F-061 |
| 项目主页 | https://univer.ai | F-058 |
| 开源范围 | 仅 **Web SDK 核心**（详见 [01-三 SDK 分层](01-three-sdk-layers-and-license-boundary.md)） | F-061 |
| 社区数据 | **Star 30,434**、Fork 2,755、open issues 198、subscribers 849 | F-057，2026-11-20 时点 |

## 热度数字怎么读（本知识包第一条勘误）

博文标题写「Github **26k star**」，2026-11-19 发布；官方 API 在 2026-11-20 实测为 **30,434**（F-057）。两者相隔一天，Star 不可能增长约 4.4k，因此这不是"时点自然增长"，而是**博文采用了滞后快照**。

结论：本知识包统一采用官方现值 30,434 并标注时点，**不沿用 26k**。引用任何动态数字时都须带日期——Star、版本、功能矩阵都会变，把标题数字写进正文等于给知识库埋一个过期断言。

## 谱系：Luckysheet → Univer

博文称"Luckysheet 团队重写的新一代表格引擎，Luckysheet 已归档，官方说法是升级成了 Univer"（F-002）。官方一手材料逐项印证：

- `dream-num/Luckysheet` 的 `archived=true`，最后 push 为 2025-08-19；
- 仓库 description 逐字为 **"Luckysheet upgraded to Univer"**；
- homepage 直接指向 `github.com/dream-num/univer/`（F-059）。

所以"归档 + 官方升级口径"属实。但要注意措辞边界：Univer 是**重写**而非 Luckysheet 的同一代码库延续——前者为 TypeScript + 插件化架构，后者为 JavaScript、MIT 许可（F-056/F-059）。做许可证继承或 API 迁移判断时，不能把两者当同一项目。

## 信源距离（读这份教程前应先知道）

| 层 | 内容 | 可信度处理 |
|----|------|-----------|
| 博文 | 公众号「Github喵」2026-11-19 推介文，第三方转述 | 观点与营销式标题单独标注，不升格为官方结论 |
| 官方一手 | GitHub REST API、`dev` 分支 README、安装文档、功能对比页、`dream-num/skills` | 本知识包所有数字/命令/API 均回溯至此 |
| 官方观点 | 对比页、选型建议、demos 说明 | 标注为「官方口径」，不与第三方评测混同 |

**学习要点**：把「推介文 → 官方一手」的距离显式写出来，是二手内容入库的第一道防线。本知识包 24 项 P0/P1 核验中 17 项完全一致、7 项为口径或时效差异、0 项核心造假——但若不核验，7 项差异会原样固化。

## 阅读下一篇

- [01 · 三 SDK 分层与授权边界](01-three-sdk-layers-and-license-boundary.md)——为什么"开源版够用"只在特定范围内成立
- [02 · 嵌入表格与 Facade API](02-embed-and-facade-api.md)——从十几行代码到业务数据打通
