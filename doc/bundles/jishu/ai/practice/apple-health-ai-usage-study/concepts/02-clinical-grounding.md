---
type: concept
title: 02 · 临床接地：OpenEvidence 与可回溯引文
description: 临床 AI 平台 OpenEvidence 在本研究中的角色、官方点名的期刊源、通俗化改写与同行评议引文的双轨结构
tags: [apple, openevidence, clinical-grounding, citation, nejm, jama, nature, health-ai]
generated:
  by: workbuddy/seven-concepts-cmd
  at: "2026-11-17T12:30:00+08:00"
status: stable
stale_after: 2027-05-17
sources:
  - id: apple-newsroom-2026-11-15
    resource: https://www.apple.com/newsroom/2026/11/apple-launches-research-study-to-explore-the-use-of-ai-for-health/
    title: Apple Newsroom 官方公告（2026-11-15 UPDATE）
  - id: openevidence-series-b
    resource: https://www.openevidence.com/announcements/openevidence-the-fastest-growing-application-for-physicians-in-history-announces-dollar210-million-round-at-dollar35-billion-valuation
    title: OpenEvidence 2025-07-15 Series B 官方公告（背景，非本研究口径）
---

# 02 · 临床接地：OpenEvidence 与可回溯引文

「临床接地」指回答不是自由生成的一段话，而是挂靠在可查证的临床文献上。本研究把它做成了一条可读、可点、可回溯的链。

## 三层结构

| 层 | 官方稿内容 | 事实编号 |
|----|------------|----------|
| 引擎层 | 与 OpenEvidence 合作；其为被医疗专业人员广泛使用的临床 AI 平台 | F-015、F-016 |
| 语料层 | 回答所依据的医学信息来自 *The New England Journal of Medicine*、*Journal of the American Medical Association*、*Nature* 等既有来源 | F-017 |
| 呈现层 | 复杂医学信息以通俗语言（approachable language）表达；每个回答附可链接的同行评议临床引文 | F-020、F-021 |

Apple 侧提供的是「研究体验」设计，OpenEvidence 侧提供的是「医学接地的 AI 技术」，两者在官方稿里被明确分工（F-018）。参与者在研究 App 中提出日常健康问题（F-019），并可查看支撑每个回答的引文链接。

> 💡 **双轨为什么重要**：只给白话，读者无从判断依据；只给论文，多数人读不动。通俗改写与原文引文并列，把「能读懂」和「能核查」放在同一屏上。这条结构是 [06 篇](06-transferable-pattern.md) 模式里「可回溯链」检查项的原型。

## 合作方背景与研究口径要分开

OpenEvidence 官网与其 2025-07-15 融资公告列出的内容合作方，比本研究公告点名的三家更多：NEJM、JAMA 及 JAMA Network 专科期刊、NCCN、Cochrane、Nature Portfolio 等（S10、S11）。公司规模、注册医师数、融资与估值等数字属于**合作方自述或百科口径**（S10、S14）。

本束采取的处理：

- 本研究公告**只点名** NEJM / JAMA / Nature 三家（F-017），正文以官方稿为准；
- 更广的合作方清单与商业数据放在 [信源清单](../references/source-manifest.md) 的「背景层」，不写入本研究事实；
- 模型在 USMLE 上的分数（S14）**不作为**本研究测量指标，理由见 [01 篇](01-four-measurement-axes.md)。

## 个人数据进入回答后会发生什么

官方稿写明参与者可选择分享 HealthKit 数据类型——静息心率、活动、睡眠、化验结果等（F-022、F-023），以探索「个人数据整合如何影响相关性与理解」（F-024）。这相当于给「临床接地」再加一层**个人语境**，但两者性质不同：

| 类型 | 来源 | 在本研究中的角色 |
|------|------|------------------|
| 群体证据 | 同行评议文献 | 回答的依据与引文链 |
| 个人语境 | 参与者自选的 HealthKit 数据 | 被研究的相关性/理解变量 |

媒体补充称研究 App 可把健康数据放入语境、帮助理解症状或状况、生成个性化运动或膳食计划（F-025，MacRumors 单源）。这一组能力**未见于 Apple 官方稿**，本束按二手单源登记，不写成官方承诺。

## 一条容易踩的读法

不要把「有引文」等同于「回答正确」。官方稿自己承认 LLM 健康工具可能给出不完整或不清晰的回答（F-013），并设置了引文与护栏；引文提供的是**可核查路径**，不是正确性保证。这也是 [03 篇](03-privacy-and-guardrails.md) 非诊断边界存在的原因。
