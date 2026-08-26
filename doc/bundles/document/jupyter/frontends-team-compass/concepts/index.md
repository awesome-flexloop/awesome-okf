---
type: Index
title: "Frontends Team Compass 概念文档索引"
description: "frontends-team-compass bundle 概念文档导航，按入门篇、核心篇、实践篇分类。"
tags: [index, concepts, team-compass]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T11:40:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:40:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: index
    resource: /references/index.md
    title: "信源文档索引"
---

# 概念文档

本目录包含 Jupyter Frontends Team Compass 的概念化解读文档，基于 [jupyterlab/frontends-team-compass](https://github.com/jupyterlab/frontends-team-compass) 仓库原始文档萃取而成。

## 📂 入门篇：了解团队罗盘

| 编号 | 文档 | 内容 |
|------|------|------|
| 00 | [仓库简介](00-introduction.md) | 仓库定位、四大内容类型、文档结构、技术栈、"同舟共济"理念、与Jupyter治理的关系 |
| 01 | [Frontends Council 架构](01-team-council.md) | 三层成员体系（Council/Release/Admin）、加入流程、半年活跃确认、SSC代表 |
| 02 | [双周会议制度](02-meetings.md) | 周三Frontends会+周二Triage会、HackMD记录归档、on/off-record录制、主持开放制度 |

## 🏛️ 核心篇：理解运作机制

| 编号 | 文档 | 内容 |
|------|------|------|
| 03 | [决策制定流程](03-decision-making.md) | 非正式共识→投票兜底、Council无人数上限、5条决策文化原则、与SSC的衔接 |
| 04 | [成员行为指南与沟通规范](04-member-guide.md) | 4种沟通渠道分工、5项基本职责、PR合并5条原则、开放包容文化 |
| 05 | [会议主持指南](05-host-guide.md) | 主持人6项职责、协助者配合、反录制机器人机制、标准开场脚本、会后2项工作 |

## 📖 实践篇：参与和贡献

| 编号 | 文档 | 内容 |
|------|------|------|
| 06 | [扩展贡献到JupyterLab组织](06-extension-contribution.md) | 4步贡献流程、jupyterlab-contrib vs 核心组织、评审标准、npm权限配置 |
| 07 | [文档基础设施与构建系统](07-doc-infrastructure.md) | Sphinx+MyST+sphinx-book-theme、ReadTheDocs CI/CD、gen_contributors.py自动生成 |
| 08 | [2020年JupyterLab用户调查](08-community-survey.md) | 6大维度20题结构、Q7矩阵题设计、Likert量表、数据驱动路线图方法论 |

## 阅读路径建议

### 🔰 新贡献者快速入门
00 → 02 → 04（沟通渠道+成员职责）

### 🏛️ 想参与团队治理
01 → 03 → 05（主持会议）→ [examples/nominating-new-member.md](../examples/nominating-new-member.md)

### 📖 扩展作者/集成者
00 → 06（扩展贡献流程）→ 04（PR合并指南）→ 07（文档构建）

### 🔍 社区运营/研究者
08（用户调查方法论）→ 03（决策流程）→ 01（治理架构）

## 信源溯源

所有概念文档的事实依据来自 [references/](../references/index.md) 目录中的原始信源文档。每个概念文档的 frontmatter `sources` 字段标注了其依据的信源。

```{toctree}
:maxdepth: 7

00-introduction
01-team-council
02-meetings
03-decision-making
04-member-guide
05-host-guide
06-extension-contribution
07-doc-infrastructure
08-community-survey
```
