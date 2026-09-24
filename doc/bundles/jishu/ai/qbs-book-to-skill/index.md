---
okf_version: "0.2"
type: bundle
title: QBS 书籍驱动技能构建法 OKF 知识包
description: 微信公众号博文经 OKF v0.2 七阶段转化——QBS（Question→Book→Skill）方法论、提示词模板与《Make Time》注意力管理框架（Highlight、两大陷阱、Time Craters），含 3 则源文勘误（非操作教程）
tags: [qbs, agent-skills, make-time, attention-management, methodology, blog-article]
generated:
  by: seven-concepts-cmd+blog-article-to-okf-wiki
  at: "2026-09-20T21:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-20T21:00:00+08:00"
status: stable
stale_after: "2026-12-31"
sources:
  - id: blog-article
    url: https://mp.weixin.qq.com/s/cyiP8goJJrB5-Fi_F96GKA
  - id: official-make-time
    url: https://maketime.blog/make-time-book/
  - id: official-make-time-authors
    url: https://maketime.blog/about-us/
  - id: official-penguin-make-time
    url: https://penguinrandomhousehighereducation.com/book/?isbn=9780525572428
  - id: official-jake-knapp
    url: https://jakeknapp.com/
  - id: official-john-zeratsky
    url: https://www.johnzeratsky.com/about
  - id: official-qbs-repo
    url: https://github.com/LearnPrompt/qbs
  - id: official-openai-gpt6
    url: https://openai.com/zh-Hans-CN/index/gpt-6-astra/
---

# QBS 书籍驱动技能构建法

> **类型**：方法论文/实践叙述（非操作教程，无 `examples/`）
> **信源**：微信公众号"卡尔的AI沃茨"《分享一个帮我快速把陌生领域方法论做成skill的新技巧》，2026-09-19 12:04 发布（F-001~F-003）
> **P0 核验**：7 项声明中 ✅ 4 项 / ⚠️ 3 项勘误 / ❌ 0 项 → `status: stable`

## 本文概要

文章讲一套名为 **QBS** 的方法：遇到一个具体卡住的问题（**Q**uestion），让模型找一本真书并自己读完相关章节（**B**ook），再把书里的方法提炼成能直接用的规则 skill，最后拿新任务试跑验证（**S**kill）（F-006/F-008）。

文章的示例应用是时间管理——模型找到的书是《**Make Time**》。作者据此展开书中框架：每天选一件 **Highlight**、识别 **Busy Bandwagon**（忙碌花车）与 **Infinity Pools**（无底洞）这对注意力陷阱、以及 **Time Craters**（时间陨石坑）与切换成本构成的损耗模型（F-016~F-026）。

作者把方法与产物一起开源为 `github.com/LearnPrompt/qbs`，内含 `make-time`、`the-debugging-book`、`shape-up` 三个 skill（F-049/F-050）。

## ⚠️ 勘误说明（3 则）

正文一律呈现**核实后的正确值**，源文口径留档于 [verification.md](references/verification.md)：

| 项 | 源文表述 | 核实值 | 编号 |
|----|---------|--------|------|
| 切换成本 | 15 到 20 分钟 | Gloria Mark（UC Irvine）：**23 分 15 秒** | F-026 → F-048 |
| Time Craters | 砸出比自身体积**大 30 倍**的坑 | 一条小推文可砸出 **30 分钟**的坑（thirty-minute crater） | F-025 → F-047 |
| Knapp 任职 | 在 **Google** 待了十年 | 在 **Google 与 Google Ventures** 共 10 年 | F-013 → F-054 |

三项均为**转述/口径偏差**，非核心声明失败，故 bundle 状态为 `stable` 而非 `flagged`。

## 文档结构

### concepts/ — 概念解析

| 文档 | 主题 |
|------|------|
| [00-qbs-method.md](concepts/00-qbs-method.md) | 方法本体：QBS 三段式、可复制提示词模板与五条交付要求、作者实践背景 |
| [01-make-time-framework.md](concepts/01-make-time-framework.md) | 书中知识：官方四步循环、Highlight 三问、两大陷阱成对机制、Time Craters 与切换成本 |
| [02-attention-tactics.md](concepts/02-attention-tactics.md) | 战术与实践：三条具体战术、开源仓库三个 skill、安装方式与读书闭环 |

### references/ — 信源登记

| 文档 | 说明 |
|------|------|
| [article-source.md](references/article-source.md) | 博文原文事实清单（F-001 至 F-056，含核验补充事实） |
| [verification.md](references/verification.md) | P0 权威核验报告（7 项 P0、3 则勘误、四张清单过筛记录、核验边界） |

## 主题关联

- [mattpocock-skills](../mattpocock-skills/index.md)：Agent Skills 生态与分发生态（QBS 产出的 skill 走同类分发路径，F-051）
- [ai-agent/book-to-skill](../ai-agent/book-to-skill/index.md)：同名的**开源工具**路线（书籍转 skill 的工程化实现，与本篇**方法论**路线互为对照）
- [codex-agent-workflow-practices](../codex-agent-workflow-practices/index.md)：Codex 多任务并行工作流（与作者所述"后台挂着七八个任务"的处境同源，F-035）

## 已知边界

- **非操作教程**：文章给出的是自然语言提示词模板（F-009），无安装/配置/代码类可复现流程，故不设 `examples/`。
- **覆盖率**：Make Time 官方为四步循环（F-046），文章仅展开 Highlight 一步；Laser / Energize / Reflect 的具体战术不在本 bundle 范围。
- **作者自述不可外推**：F-035~F-040、F-042 为一手个人经验；时间损耗推算依赖已勘误的切换成本数字。
- **中文译名为作者意译**："忙碌花车""无底洞"非官方译名（见 [verification.md](references/verification.md) §五）。
- **时效性**：模型称呼（GPT-6 / Fable 5.1，F-041）与仓库内容随时间变化，`stale_after` 设为 2026-12-31。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```