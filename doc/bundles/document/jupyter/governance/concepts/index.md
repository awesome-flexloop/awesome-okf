---
type: Index
title: "Jupyter Governance 概念文档索引"
description: "Jupyter 治理模型的概念文档导航，按入门篇、核心篇、制度篇分类。"
tags: [index, concepts, governance]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: overview
    resource: /references/index.md
    title: "信源文档索引"
---

# Jupyter Governance 概念文档

本目录包含 Jupyter 治理模型的概念化解读文档，基于 [jupyter/governance](https://github.com/jupyter/governance) 仓库原始文档萃取而成。

## 📂 入门篇：了解 Jupyter 治理

| 编号 | 文档 | 内容 |
|------|------|------|
| 00 | [Jupyter Governance 仓库简介](00-introduction.md) | 仓库定位、内容结构、构建方式、许可证 |
| 01 | [三主体治理模型](01-governance-model.md) | EC + SSC + Foundation 三层架构总览 |
| 02 | [从 BDFL 到分布式治理的历史演进](02-history-and-evolution.md) | 2022年治理转型的背景、过程和意义 |

## 🏛️ 核心篇：理解治理架构

| 编号 | 文档 | 内容 |
|------|------|------|
| 03 | [执行委员会（EC）](03-executive-council.md) | 最高决策机构的职责、选举、运作机制 |
| 04 | [软件指导委员会（SSC）](04-software-steering-council.md) | 跨项目软件决策、JEP 流程、安全管理 |
| 05 | [Jupyter 基金会](05-jupyter-foundation.md) | Linux Foundation 定向基金、理事会构成、资金管理 |
| 06 | [软件子项目体系](06-software-subprojects.md) | 子项目分类、自治原则、共同责任 |
| 07 | [常设委员会与工作组](07-committees-and-working-groups.md) | 非软件工作的组织方式、DEI/CoC/社区建设 |
| 08 | [理事会联盟（UoC）与选举人团](08-union-of-councils.md) | EC 选举的投票主体、民主基础 |

## 📜 制度篇：掌握运作规则

| 编号 | 文档 | 内容 |
|------|------|------|
| 09 | [决策制定流程](09-decision-making.md) | 共识寻求→投票兜底、7天投票期、50%法定人数 |
| 10 | [选举与投票机制](10-elections-and-voting.md) | 排序复选制(STV)、Apache STeVe 计票工具链 |
| 11 | [新子项目准入与孵化](11-new-subprojects.md) | 直接创建vs外部并入、incubator孵化、毕业流程 |
| 12 | [杰出贡献者制度](12-distinguished-contributors.md) | 终身荣誉、自我延续选举机制 |
| 13 | [行为准则与执行机制](13-code-of-conduct.md) | CoC期望行为、举报渠道、事件响应、申诉 |
| 14 | [商标政策与许可证](14-trademarks-and-licensing.md) | 3-Clause BSD、商标使用规则、共享版权模型 |
| 15 | [学术论文流程](15-academic-papers.md) | 论文公告、作者多样性、社区共识要求 |
| 16 | [文档基础设施与构建系统](16-doc-infrastructure.md) | MyST Markdown、nox构建、YAML数据驱动、CC0许可 |

## 阅读路径建议

### 🔰 新贡献者快速入门
00 → 01 → 09（决策流程）→ 06（子项目体系）

### 🏛️ 想参与治理
01 → 03 → 04 → 08 → 10（选举机制）→ 07（委员会与工作组）

### 📖 研究者/借鉴者
02（历史演进）→ 01 → 03 → 04 → 09 → 14（商标许可）→ 13（CoC）

## 信源溯源

所有概念文档的事实依据来自 [references/](../references/index.md) 目录中的原始信源文档。每个概念文档的 frontmatter `sources` 字段标注了其依据的信源。

```{toctree}
:hidden:

00-introduction
01-governance-model
02-history-and-evolution
03-executive-council
04-software-steering-council
05-jupyter-foundation
06-software-subprojects
07-committees-and-working-groups
08-union-of-councils
09-decision-making
10-elections-and-voting
11-new-subprojects
12-distinguished-contributors
13-code-of-conduct
14-trademarks-and-licensing
15-academic-papers
16-doc-infrastructure
```
