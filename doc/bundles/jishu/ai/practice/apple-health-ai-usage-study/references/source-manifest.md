---
type: reference
title: 信源清单与证据分层（S1～S14）
description: Apple 健康 AI 使用研究知识包的全部信源登记、一手/二手/背景分层，以及媒体单源细节白名单
tags: [sources, provenance, apple, openevidence, source-layering, okf-wiki]
generated:
  by: workbuddy/seven-concepts-cmd
  at: "2026-11-17T12:30:00+08:00"
status: stable
stale_after: 2027-05-17
---

# 信源清单与证据分层（S1～S14）

> **分层原则**：一手信源确定「官方说了什么」；二手信源只用于补充语境与交叉比对；背景信源用于谱系定位，不进入本研究的事实结论。多家媒体转引同一原始出处时，仍按**一个独立信源**计数。

## 一手层（S1～S3）

| ID | 信源 | 用途 | 距离 |
|----|------|------|------|
| S1 | [Apple Newsroom：Apple launches research study to explore the use of AI for health](https://www.apple.com/newsroom/2026/11/apple-launches-research-study-to-explore-the-use-of-ai-for-health/)（2026-11-15 UPDATE） | 全束主信源；F-001～F-024、F-029～F-033、F-037～F-040 的直接出处 | 官方原文，全文抓取 |
| S2 | 同页面三处图片资源与图注（hero / visit-prep-summary / survey） | F-027、F-028 的出处（问卷控制权、就诊准备摘要图注） | 官方同页资产 |
| S3 | [Apple Health AI Study App（美国区 App Store）](https://apps.apple.com/us/app/apple-health-ai-study-app/id6800060365) | F-041 中 App 条目 id 的核对 | 官方商店条目 |

## 二手层（S4～S9）

| ID | 信源 | 用途 | 说明 |
|----|------|------|------|
| S4 | [MacRumors, 2026-11-16](https://www.macrumors.com/2026/11/16/apple-seeks-200000-people-for-ai-health-study/) | F-025、F-026、F-035、F-036 | 媒体单源细节的**唯一直接出处** |
| S5 | 9to5Mac / CNET 相关转引（经其他报道转述，未直接取证） | F-036 的转引链 | 二手转引，不单独计独立信源 |
| S6 | [iClarified 103551](https://iclarified.com/103551) | F-014、F-034、F-048 | 明确区分 2025 Apple Health Study 与本研究 |
| S7 | [PCMag](https://www.pcmag.com/news/apples-new-iphone-app-is-an-ai-health-trial-exclusive-to-200k-people) | F-014、F-034 交叉比对 | 标题使用 "AI health trial" 措辞 |
| S8 | [Data Studios 分析](https://www.datastudios.org/post/apple-health-ai-study-app-200000-us-iphone-users-openevidence) | 未披露项清单的交叉参照 | 指出官方稿未说明时长、补偿、撤回、端到端数据流 |
| S9 | 其他二手报道组：Health AI Central、iPhone Wired、AI Affairs、The Latent Daily、Storyboard18 | F-036 转引链、谱系背景、媒体措辞对照 | 其中「12 个月」「KFF 调查」「IRB 监督」「基线/月度问卷」等细节**不见于 S1**，列入未披露项 |

## 背景层（S10～S14）

| ID | 信源 | 用途 | 边界 |
|----|------|------|------|
| S10 | [OpenEvidence 2025-07-15 Series B 官方公告](https://www.openevidence.com/announcements/openevidence-the-fastest-growing-application-for-physicians-in-history-announces-dollar210-million-round-at-dollar35-billion-valuation) | 合作方内容合作方清单与规模数字 | 公司自述；与本研究公告口径不混用 |
| S11 | [OpenEvidence 官网](https://www.openevidence.com/) | NEJM / JAMA / NCCN / Cochrane / Nature Portfolio 合作方列表 | 公司自述；本研究公告只点名三家（F-017） |
| S12 | [Apple Health Study 官网（BWH）](https://applehealthstudy.bwh.harvard.edu/) | 2025 研究的时长、退出机制、参与条件 | 属于**另一个研究**，不跨对象套用 |
| S13 | [Apple 2025-02-12 新闻稿转载](https://www.marketscreener.com/quote/stock/APPLE-INC-4849/news/Apple-New-holistic-Apple-Health-Study-launches-today-in-the-Research-app-49036221/) 及 HLTH / AppleMagazine 谱系报道 | F-042～F-047 谱系背景 | 转载与媒体背景，非本研究一手 |
| S14 | [Wikiwand：OpenEvidence 条目](https://www.wikiwand.com/en/articles/OpenEvidence) | 公司成立、融资、USMLE 分数等百科口径 | 百科三层来源，只作背景，不作本研究事实 |

## 媒体单源细节白名单（不得升格为官方口径）

| 细节 | 唯一直接出处 | 登记编号 | 本束处置 |
|------|--------------|----------|----------|
| 问题送达合作方前去标识化 | S4 | F-035 | 事实清单登记，正文标「媒体单源、官方未证实」 |
| 24 小时内删除问答数据 | S4（S5、S9 转引） | F-036 | 同上，并注明转引链 |
| 评分与偶尔问卷 | S4 | F-026 | 二手登记，不写成官方承诺 |
| 个性化运动/膳食计划等症状语境能力 | S4 | F-025 | 二手登记，不写成官方承诺 |
| 研究时长 12 个月 / KFF 调查 / IRB / 基线月度问卷 | S9 | 未编号（未披露项） | 仅登记于 [verification.md](verification.md)，不支撑结论 |

## 信源距离预判（写入教程前的前置判断）

- S1 属**厂商官方发布稿**：事实密度高，但目标表述（F-004、F-005）为厂商意图陈述，按「官方声明」而非「已验证效果」使用。
- S4～S9 属**媒体转述**：对官方稿的直译部分可交叉比对；新增细节一律按单源处理。
- S10、S11、S14 属**合作方自述/百科**：商业与能力数字与本研究测量目标分属不同问题，[01 篇](../concepts/01-four-measurement-axes.md) 已隔离。
