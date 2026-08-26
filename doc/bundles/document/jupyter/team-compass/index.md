---
okf_version: "0.2"
type: bundle
title: "🧭 Jupyter Server Team Compass"
description: "Jupyter Server 团队罗盘 OKF Wiki 教程，基于 jupyter-server/team-compass 仓库萃取，包含团队成员体系、加入流程、决策机制、成员指南、周会制度和文档基础设施。"
tags: [jupyter, jupyter-server, team-compass, governance, meetings, membership, okf-wiki, bundle-index]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: repo
    type: git
    url: https://github.com/jupyter-server/team-compass
    ref: main
    path: /
  - id: docs
    type: website
    url: https://jupyter-server-team-compass.readthedocs.io
---

# 🧭 Jupyter Server Team Compass 教程

> 基于 [jupyter-server/team-compass](https://github.com/jupyter-server/team-compass) 仓库的 OKF Wiki 结构化教程，系统讲解 Jupyter Server 子项目的团队运作机制、治理实践和协作规范。

## Bundle 概览

Jupyter Server Team Compass 是 Jupyter Server 子项目的"团队罗盘"——一个纯文档仓库，承载团队周会信息、成员管理、决策流程、PR合并规范和沟通渠道策略。它虽然规模精炼（4个核心文档页面），但完整覆盖了开源子项目团队运作的关键机制，是理解 Jupyter 子项目层面治理实践的优秀样本。

本 bundle 通过 7 篇概念文档和 1 篇实操示例，将 Jupyter Server 团队"同舟共济"的协作文化结构化呈现。

## 目录结构

```
team-compass/
├── index.md                    ← 你在这里
├── log.md                      ← 变更日志
├── references/                 ← 信源文档（原始资料摘录）
│   ├── index.md                ← 信源索引
│   ├── readme-source.md
│   ├── team-source.md
│   ├── becoming-member-source.md
│   ├── decision-making-source.md
│   ├── member-guide-source.md
│   ├── conf-py-source.md
│   └── gen-contributors-source.md
├── concepts/                   ← 概念文档（结构化知识）
│   ├── index.md                ← 概念索引
│   ├── 00-introduction.md
│   ├── 01-team-membership.md
│   ├── 02-becoming-member.md
│   ├── 03-decision-making.md
│   ├── 04-member-guide.md
│   ├── 05-weekly-meetings.md
│   └── 06-doc-infrastructure.md
└── examples/                   ← 实操示例
    ├── index.md                ← 示例索引
    └── nominating-new-member.md
```

## 核心知识图谱

```
                ┌──────────────────────────┐
                │ Jupyter Server Team      │
                │ Compass                  │
                │ "We sail together"       │
                └──────────┬───────────────┘
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                   ▼
┌──────────────┐  ┌───────────────┐   ┌────────────────┐
│  成员体系     │  │  决策机制      │   │  协作规范       │
│              │  │               │   │                │
│ 活跃/不活跃   │  │ 共识→投票     │   │ 4种沟通渠道    │
│ SSC代表1年制  │  │ 无团队上限    │   │ 5项成员职责    │
│ YAML+自动生成 │  │ 遵循全局治理  │   │ PR合并5原则    │
│ 半年确认     │  └───────┬───────┘   └───────┬────────┘
└──────┬───────┘          │                   │
       │                  ▼                   ▼
       │         ┌───────────────┐   ┌────────────────┐
       │         │  加入流程      │   │  周会制度       │
       │         │               │   │                │
       │         │ 内部共识→     │   │ 周四8am PT     │
       │         │ 私下联系→     │   │ Zoom+HackMD    │
       │         │ 公开提名→     │   │ GitHub归档     │
       │         │ 7天讨论→      │   │ 同步/异步参与  │
       │         │ 无反对加入    │   │                │
       │         └───────────────┘   └────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│  文档基础设施：Sphinx + MyST + RTD             │
│  构建时自动生成贡献者HTML表格                   │
│  从GitHub自动获取头像                          │
│  pre-commit仅end-of-file-fixer               │
└──────────────────────────────────────────────┘
```

## 关键洞察

1. **精炼而完整**：只有4个核心文档页面，但覆盖了团队运作的全部关键环节（成员、决策、指南、会议），是子项目Team Compass的精简范本
2. **与Frontends的差异**：相比 JupyterLab Frontends Team Compass 的三层Council、主持指南、社区调查等丰富内容，Server Team Compass 更加轻量，体现了子项目规模与治理复杂度的匹配
3. **信任判断优先**：PR合并指南明确"信任你的判断"+"不要害怕合并"，流程是辅助而非阻碍
4. **低门槛回归**：不活跃成员可随时自行重新激活，不需要重新提名，最大程度降低贡献者的离开成本
5. **数据驱动展示**：成员列表用YAML维护，构建时Python脚本自动生成HTML表格并从GitHub拉取头像，避免手动维护过期

## 快速开始

- **新手入门**：从 [concepts/00-introduction.md](concepts/00-introduction.md) 开始
- **想加入团队**：阅读 [concepts/02-becoming-member.md](concepts/02-becoming-member.md)，然后实操 [examples/nominating-new-member.md](examples/nominating-new-member.md)
- **理解治理**：阅读 [concepts/03-decision-making.md](concepts/03-decision-making.md) → [concepts/01-team-membership.md](concepts/01-team-membership.md)
- **成员操作**：阅读 [concepts/04-member-guide.md](concepts/04-member-guide.md) → [concepts/05-weekly-meetings.md](concepts/05-weekly-meetings.md)
- **技术实现**：阅读 [concepts/06-doc-infrastructure.md](concepts/06-doc-infrastructure.md)
- **信源查阅**：查看 [references/index.md](references/index.md) 获取原始资料

## 与其他 Bundle 的关系

| Bundle | 关系 |
|--------|------|
| [governance](../governance/index.md) | Jupyter 全局治理（EC/SSC/Foundation），本 bundle 嵌套在其下，引用其决策流程和CoC |
| [frontends-team-compass](../frontends-team-compass/index.md) | JupyterLab Frontends 团队罗盘，规模更大（三层Council/主持指南），本bundle是更轻量的子项目Team Compass范例 |
| [jupyter](../jupyter/index.md) | Jupyter 元包和核心组件概览 |
| [jupyter-core](../jupyter-core/index.md) | Jupyter Core 包，jupyter-server 依赖的核心组件 |
| [jupyter-client](../jupyter-client/concepts/index.md) | Jupyter Client 包，jupyter-server 的客户端通信组件 |

## 外部资源

- 🌐 在线文档：[jupyter-server-team-compass.readthedocs.io](https://jupyter-server-team-compass.readthedocs.io)
- 📦 GitHub 仓库：[jupyter-server/team-compass](https://github.com/jupyter-server/team-compass)
- 🧭 Jupyter 全局治理：[jupyter.org/governance](https://jupyter.org/governance)
- 🧭 Frontends Team Compass：[jupyterlab/frontends-team-compass](https://github.com/jupyterlab/frontends-team-compass)

## 文档信息

- **生成方法**：source-code-to-okf-wiki skill（R→I→E→V→C 五阶段工作流）
- **方法论**：seven-concepts-cmd（R-I-E-C-A-F-V 七概念编排，知识沉淀场景）
- **原始信源版本**：2025-02 数据快照（contributors last-check-in）
- **内容级别**：公开（Public）
- **许可证说明**：原始文档遵循 Jupyter 项目许可证（3-Clause BSD），本 bundle OKF 格式

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
