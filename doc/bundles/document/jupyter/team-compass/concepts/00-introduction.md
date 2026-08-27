---
type: Concept
title: "Jupyter Server Team Compass 仓库简介"
description: "Jupyter Server 团队罗盘仓库的定位、内容结构、在线发布地址，以及与 Jupyter 全局治理体系的关系。"
tags: [introduction, overview, team-compass, repository, jupyter-server]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: readme
    resource: /references/readme-source.md
    title: "README.md 信源"
  - id: index-rst
    resource: /references/conf-py-source.md
    title: "Sphinx 配置信源"
---

## 什么是 Jupyter Server Team Compass

Jupyter Server Team Compass 是 Jupyter Server 子项目的**团队运作文档仓库**。它不是代码库，而是一个纯文档仓库，承载团队讨论、同步和会议记录，为团队设定每周的项目活动方向。

该仓库的在线文档发布地址为 Read the Docs：[jupyter-server-team-compass.readthedocs.io](https://jupyter-server-team-compass.readthedocs.io)。

## 仓库包含什么

Team Compass 仓库涵盖 Jupyter Server 团队运作的核心机制：

| 主题 | 文档 | 核心内容 |
|------|------|---------|
| 团队成员列表 | [team.md](01-team-membership.md) | 活跃/不活跃成员、SSC代表 |
| 成为成员 | [becoming-member.md](02-becoming-member.md) | 提名流程、活跃/不活跃状态、半年维护 |
| 决策机制 | [decision-making.md](03-decision-making.md) | 共识优先、投票兜底、团队规模原则 |
| 成员指南 | [member-guide.md](04-member-guide.md) | 沟通渠道、成员职责、PR合并原则 |
| 周会制度 | [weekly-meetings.md](05-weekly-meetings.md) | 会议时间、地点、议程与记录 |
| 文档构建 | [doc-infrastructure.md](06-doc-infrastructure.md) | Sphinx+MyST+RTD+自动生成脚本 |

## "We sail together"（同舟共济）

文档引用了 Jupyter 社区的核心理念：

> While we value each others individual strengths and contributions, we succeed or fail as a team. Whether taking corrective actions for a bug or being recognized for good work, the team, instead of an individual, shoulders the burden and success.
>
> （虽然我们珍视每个人的个人优势和贡献，但我们作为一个团队共担成败。无论是修复 Bug 还是因出色工作获得认可，承担责任和享受成功的都是团队而非个人。）

这体现了 Jupyter 社区的协作文化——贡献属于集体，责任也由集体承担。

## 仓库目的

根据文档描述，该仓库帮助 Jupyter Server 团队：

- 设定项目方向并根据需要调整路线
- 记录团队会议议程和归档
- 制定方向和行动计划
- 建立尊重协作的沟通文化
- 认可和庆祝团队成就

## 行为准则

Jupyter Server 社区遵循更广泛的 [Jupyter 社区行为准则](https://jupyter.org/governance/conduct/code_of_conduct.html)。

## 与 Jupyter 生态的关系

Team Compass 是 Jupyter 治理体系中**子项目层**的运作手册：

- 上层：[Jupyter 全局治理](../../governance/concepts/01-governance-model.md)定义三主体模型（EC/SSC/Foundation）
- 本层：Jupyter Server Team Compass 定义子项目内部的日常运作
- 平行：其他子项目（如 JupyterLab Frontends）也有各自的 Team Compass

它遵循 Jupyter 全局治理文档中规定的决策流程和行为准则，但聚焦于 Jupyter Server 子项目的具体操作细节。

## 相关概念

- [团队成员体系](01-team-membership.md)
- [成为团队成员](02-becoming-member.md)
- [决策机制](03-decision-making.md)
- [文档构建基础设施](06-doc-infrastructure.md)
