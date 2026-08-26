---
type: Index
title: "Jupyter Governance Bundle"
description: "Jupyter 治理模型 OKF Wiki 教程，基于 jupyter/governance 仓库萃取，包含治理架构、决策流程、委员会体系、商标许可等完整知识。"
tags: [jupyter, governance, okf-wiki, bundle-index]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: repo
    type: git
    url: https://github.com/jupyter/governance
    ref: main
    path: /
  - id: docs
    type: website
    url: https://jupyter.org/governance
---

# Jupyter Governance 教程

> 基于 [jupyter/governance](https://github.com/jupyter/governance) 仓库的 OKF Wiki 结构化教程，系统讲解 Project Jupyter 的治理架构与运作机制。

## Bundle 概览

Jupyter 是全球最大的开源数据科学生态系统之一。2022年12月，Jupyter 完成了从 BDFL（创始人独裁）模式向**三主体分布式治理**的转型，成为大型开源项目治理演进的重要案例。本 bundle 通过17篇概念文档系统梳理 Jupyter 的治理体系。

## 目录结构

```
governance/
├── index.md                    ← 你在这里
├── references/                 ← 信源文档（原始资料摘录）
│   ├── index.md                ← 信源索引
│   ├── overview-source.md
│   ├── executive-council-source.md
│   ├── ssc-source.md
│   ├── decision-making-source.md
│   ├── subprojects-source.md
│   ├── committees-source.md
│   ├── coc-source.md
│   ├── trademarks-license-source.md
│   ├── foundation-dc-source.md
│   ├── elections-papers-source.md
│   └── infrastructure-history-source.md
└── concepts/                   ← 概念文档（结构化知识）
    ├── index.md                ← 概念索引
    ├── 00-introduction.md
    ├── 01-governance-model.md
    ├── 02-history-and-evolution.md
    ├── 03-executive-council.md
    ├── 04-software-steering-council.md
    ├── 05-jupyter-foundation.md
    ├── 06-software-subprojects.md
    ├── 07-committees-and-working-groups.md
    ├── 08-union-of-councils.md
    ├── 09-decision-making.md
    ├── 10-elections-and-voting.md
    ├── 11-new-subprojects.md
    ├── 12-distinguished-contributors.md
    ├── 13-code-of-conduct.md
    ├── 14-trademarks-and-licensing.md
    ├── 15-academic-papers.md
    └── 16-doc-infrastructure.md
```

## 核心知识图谱

```
                    ┌─────────────────────┐
                    │  Jupyter Governance  │
                    │   三主体治理模型      │
                    └──────────┬──────────┘
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                    ▼
    ┌──────────────┐  ┌───────────────┐   ┌────────────────┐
    │     EC       │  │      SSC      │   │    Foundation  │
    │ 执行委员会    │  │ 软件指导委员会 │   │   基金会        │
    │ (6人, 2年任期)│  │ (子项目代表制) │   │ (LF定向基金)    │
    └──────┬───────┘  └───────┬───────┘   └────────────────┘
           │                  │
    ┌──────┴──────┐    ┌──────┴──────┐
    ▼             ▼    ▼              ▼
┌────────┐ ┌──────────┐ ┌────────────────────┐
│常设委员│ │ 工作组    │ │  软件子项目         │
│会(永久)│ │(临时)    │ │ (Frontends/Hub/    │
│DEI/CoC │ │商标/社区 │ │  Server/Widgets/   │
│/利益冲 │ │/媒体/文档│ │  Kernels等)        │
│突/CAP  │ │          │ │                    │
└────────┘ └──────────┘ └────────────────────┘

    决策流程：寻求共识 → 投票兜底（7天/50%法定人数/排序复选）
    选举机制：UoC（选举人团）→ 排序复选制（STV）→ Apache STeVe 计票
```

## 快速开始

- **新手入门**：从 [concepts/00-introduction.md](concepts/00-introduction.md) 开始
- **总览架构**：阅读 [concepts/01-governance-model.md](concepts/01-governance-model.md)
- **信源查阅**：查看 [references/index.md](references/index.md) 获取原始资料

## 关键洞察

1. **三权分立而非技术独裁**：最终决策权在全维度治理的 EC，而非纯技术机构 SSC
2. **委派与自治**：EC 大量委派日常工作，子项目高度自治
3. **共识优先投票兜底**：投票是升级机制而非日常手段，优先通过讨论达成共识
4. **DEI/CoC 制度化**：多元公平包容和行为准则拥有与软件工程同等的常设委员会地位
5. **创始人主动放权**：Fernando Pérez 自愿放弃 BDFL 角色，推动制度化权力分散

## 外部资源

- 🌐 在线文档：[jupyter.org/governance](https://jupyter.org/governance)
- 📦 GitHub 仓库：[jupyter/governance](https://github.com/jupyter/governance)
- 🧭 EC Team Compass：[ec.jupyter.org](https://ec.jupyter.org)
- 🧭 SSC Team Compass：[software-steering-council-team-compass](https://github.com/jupyter/software-steering-council-team-compass/)
- 🧭 Foundation Team Compass：[jupyter-foundation-governing-board](https://jupyter-governance.github.io/jupyter-foundation-governing-board)

## 文档信息

- **生成方法**：source-code-to-okf-wiki skill (R-I-E-V-C 工作流)
- **方法论**：seven-concepts-cmd (R-I-E-C-A-F-V 七概念编排)
- **原始信源版本**：2026年8月 main 分支
- **内容级别**：公开（Public）
- **许可证说明**：原始文档 CC0，本 bundle OKF 格式

```{toctree}
:maxdepth: 7

concepts/index
references/index
facts
insights
log
```
