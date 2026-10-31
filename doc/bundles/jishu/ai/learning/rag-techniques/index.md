---
okf_version: "0.2"
type: bundle
title: RAG_Techniques 项目 OKF 知识包
description: 拆解 NirDiamant/RAG_Techniques 仓库——约 3 万 Star、42 个可运行 notebook，按 RAG pipeline 七阶段组织的「可执行故障对照表」；含技术机制解读、企业落地建议与 License 非商用约束（非操作教程）
tags: [rag, rag-techniques, nirdiamant, graph-rag, lightrag, retrieval-augmented-generation, license]
generated:
  by: seven-concepts-cmd
  at: "2026-10-31T11:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-31T11:00:00+08:00"
status: stable
stale_after: "2027-04-30"
sources:
  - id: blog-article
    url: https://mp.weixin.qq.com/s/WsgnBpEtTytatRFkKUlfeA
  - id: github-rag-techniques
    url: https://github.com/NirDiamant/RAG_Techniques
---

# RAG_Techniques 项目

> **类型**：技术综述/资讯盘点（非操作教程，无 examples/）
> **数据时点**：2026-10-31（博文发布时口径为 30,003 Star）
> **P0 核验**：22 项 P0 中无 ❌；6 项 ⚠️ 为口径/时效差异（Star 增长、七段篇数归并、CI 工作流时效、配套书自述数字）
> **合规提示**：仓库 License 为 **Custom License Agreement（非商用）**，商业用途须作者书面许可

## 本文概要

本文介绍 Nir Diamant 维护的开源仓库 `NirDiamant/RAG_Techniques`——约 3 万 Star、**42 个可运行 notebook**，按 RAG pipeline 阶段组织，作者称其为「**一张可执行的 RAG 故障对照表**」而非框架。文章围绕三个维度展开：**项目定位与结构**（七段 pipeline 划分、notebook 与脚本双轨、软件工程化维护）、**技术机制**（Graph RAG 双阶段双路扩图、LightRAG 双层关键词）、**落地与边界**（安装现状、企业团队四步用法、License 非商用约束与五项局限）。

## ⚠️ 数据来源说明

本文 Star 数（30,149）来自 GitHub 实时数据，博文发布时（2026-10-27）口径为 **30,003**，属项目增长的时点差异，非错误。

两项需特别提示：
- **「42 个 notebook」与七段篇数之和 35 不等**：核验确认七段逐类篇数与 README 完全吻合，但七段是**按 pipeline 阶段的归并视图**；`all_rag_techniques/` 下 `.ipynb` 实测确为 **42 个**。仓库 README 自身亦同时存在「42 notebooks」与表格 38 行 / 10 分类标签的口径张力（F-007 / F-051）。
- **「400 页」「Amazon 生成式 AI 畅销书」为作者自述式标注**，非独立第三方统计；第三方书目站各版本页数为 250 / 427（F-054 / F-055）。

## 文档结构

### concepts/ — 概念解析

| 文档 | 主题 |
|------|------|
| [00-intro.md](concepts/00-intro.md) | 项目概述：身份、定位、核心数据、七段结构、双轨设计与作者生态 |
| [01-techniques.md](concepts/01-techniques.md) | 技术机制：七段 pipeline 归因、Graph RAG 双路扩图、LightRAG 双层关键词 |
| [02-practice.md](concepts/02-practice.md) | 安装现状、企业落地四步、五类场景、五项局限与 License 非商用约束 |

### references/ — 信源登记

| 文档 | 说明 |
|------|------|
| [article-source.md](references/article-source.md) | 博文原文事实清单（F-001 至 F-057） |
| [verification.md](references/verification.md) | P0 权威核验报告与勘误记录 |

## 主题关联

- [qbs-book-to-skill](../qbs-book-to-skill/index.md)：书籍驱动技能构建法（同为「学习资源如何转化为能力」的方法论视角）
- [mattpocock-skills](../mattpocock-skills/index.md)：Skills 生态解读（同属开源项目盘点类知识包）
- [free-llm-api-roundup](../free-llm-api-roundup/index.md)：免费大模型 API 盘点（RAG 落地时的模型成本相关话题）

## 已知边界

- **非操作教程**：本篇为技术综述/资讯盘点，无逐步可复现的本地环境搭建步骤（仓库本身亦无 requirements.txt，不具备开箱复现条件）
- **机制解说为作者解读**：Graph RAG / LightRAG 的机制描述来自博文作者对特定 notebook 的解读，非仓库官方文档口径
- **数据时效**：Star 数、CI 工作流清单持续变化，stale_after 设为 2027-04-30
- **合规红线**：License 为非商用协议，禁止将 notebook 代码直接用于商业产品

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
