---
okf_version: "0.2"
type: bundle
title: Matt Pocock Skills 项目 OKF 知识包
description: 分析 Matt Pocock 开源的 mattpocock/skills Agent Skills 项目——GitHub 25.8 万 Star、skills.sh 安装量 2140 万，解读 Skills 技术机制与生态竞争格局（非操作教程）
tags: [agent-skills, mattpocock, skills-sh, github, vercel, claude-code, cursor]
generated:
  by: agnes-2.5-flash
  at: "2026-09-09T15:22:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-09T15:22:00+08:00"
status: stable
stale_after: "2027-03-09"
sources:
  - id: blog-article
    url: https://mp.weixin.qq.com/s/7ox6ioOtGI2TNyFs4UpL4Q
  - id: github-mattpocock-skills
    url: https://github.com/mattpocock/skills
  - id: github-mattpocock
    url: https://github.com/mattpocock
  - id: skills-sh
    url: https://www.skills.sh/
---

# Matt Pocock Skills 项目

> **类型**：技术综述/资讯盘点（非操作教程，无 examples/）
> **数据时点**：2026-09-09（博文发布时口径为 23 万 Star / 1800 万安装）
> **P0 核验**：12 项 P0 中 ✅ 8 项 / ⚠️ 4 项（均为增长差异或单源，无 ❌）

## 本文概要

本文介绍 Matt Pocock 主导的开源项目 `mattpocock/skills`——一个面向 AI Agent 的标准化 Skills 集。文章核心围绕三个维度展开：**项目背景与数据**（作者个人品牌 + 开源成就）、**技术机制**（动态工具注入、跨平台多模型支持）、**生态格局**（标准库路线 vs 平台路线）。

## ⚠️ 数据来源说明

本文涉及的 Star 数（25.8 万）和安装量（2140 万）均来自公开可验证数据源（GitHub API、skills.sh 官网），但数值随时间持续增长，**博文发布时口径为 23 万 Star / 1800 万安装**，属发布时较保守口径，非错误。

Total TypeScript 订阅者约 6 万（F-010）、skills.sh 收录超 1000 个 Skills（F-015）为博文单源数据，未找到独立精确统计，已在正文标注。

## 文档结构

### concepts/ — 概念解析

| 文档 | 主题 |
|------|------|
| [00-intro.md](concepts/00-intro.md) | 项目概述：背景、定位、核心数据、Matt Pocock 个人飞轮 |
| [01-skills-concept.md](concepts/01-skills-concept.md) | 技术机制：动态工具注入原理、安装命令、跨平台多模型支持 |
| [02-ecosystem.md](concepts/02-ecosystem.md) | 生态格局：skills.sh 平台、竞争路线分析、三种范式对比 |

### references/ — 信源登记

| 文档 | 说明 |
|------|------|
| [article-source.md](references/article-source.md) | 博文原文事实清单（F-001 至 F-025） |
| [verification.md](references/verification.md) | P0 权威核验报告 |

## 主题关联

- [agent-industry-research](../../agent-industry-research/index.md)：AI Agent 行业研究，涵盖 Agent 技术栈全景（与本 bundle 形成"行业→项目"视角互补）
- [free-llm-api-roundup](../../free-llm-api-roundup/index.md)：LLM API 聚合资源盘点（与本 bundle 的"多模型支持"话题相关）

## 已知边界

- **非操作教程**：本文为资讯综述，无代码演练步骤
- **数据时效**：Star 数/安装量持续变化，stale_after 设为 2027-03-09
- **单源数据**：F-010（订阅者数）、F-015（收录量）仅博文单源

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
