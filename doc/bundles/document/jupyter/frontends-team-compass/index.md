---
okf_version: "0.2"
type: bundle
title: "🧭 Jupyter Frontends Team Compass"
description: "Jupyter Frontends 团队罗盘 OKF Wiki 教程，基于 jupyterlab/frontends-team-compass 仓库萃取，包含团队治理架构、会议制度、决策流程、成员指南、主持规范、扩展贡献和文档基础设施。"
tags: [jupyter, jupyterlab, frontends, team-compass, governance, meetings, okf-wiki, bundle-index]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T11:40:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:40:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: repo
    type: git
    url: https://github.com/jupyterlab/frontends-team-compass
    ref: main
    path: /
  - id: docs
    type: website
    url: https://jupyterlab-team-compass.readthedocs.io
---

# 🧭 Jupyter Frontends Team Compass 教程

> 基于 [jupyterlab/frontends-team-compass](https://github.com/jupyterlab/frontends-team-compass) 仓库的 OKF Wiki 结构化教程，系统讲解 Jupyter Frontends 团队（JupyterLab/Jupyter Notebook 前端方向）的运作机制、治理架构和协作规范。

## Bundle 概览

frontends-team-compass 是 Jupyter Frontends 团队的"团队罗盘"——一个纯文档仓库，承载团队会议记录、成员管理、决策流程、PR 合并规范、会议主持指南和扩展贡献流程。它体现了 Jupyter 开源社区"共识优先、包容开放、同舟共济"的协作文化。

本 bundle 通过 9 篇概念文档和 2 篇实操示例，将团队运作的隐性知识显性化、结构化。

## 目录结构

```
frontends-team-compass/
├── index.md                    ← 你在这里
├── log.md                      ← 变更日志
├── references/                 ← 信源文档（原始资料摘录）
│   ├── index.md                ← 信源索引
│   ├── readme-source.md
│   ├── team-source.md
│   ├── becoming-member-source.md
│   ├── decision-making-source.md
│   ├── member-guide-source.md
│   ├── host-guide-source.md
│   ├── survey-source.md
│   └── conf-py-source.md
├── concepts/                   ← 概念文档（结构化知识）
│   ├── index.md                ← 概念索引
│   ├── 00-introduction.md
│   ├── 01-team-council.md
│   ├── 02-meetings.md
│   ├── 03-decision-making.md
│   ├── 04-member-guide.md
│   ├── 05-host-guide.md
│   ├── 06-extension-contribution.md
│   ├── 07-doc-infrastructure.md
│   └── 08-community-survey.md
└── examples/                   ← 实操示例
    ├── index.md                ← 示例索引
    ├── hosting-a-meeting.md
    └── nominating-new-member.md
```

## 核心知识图谱

```
                ┌─────────────────────────┐
                │  Frontends Team Compass │
                │    "We sail together"   │
                └───────────┬─────────────┘
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                    ▼
┌──────────────┐  ┌───────────────┐   ┌────────────────┐
│  治理架构     │  │  会议制度      │   │  协作规范       │
│              │  │               │   │                │
│ Council三层  │  │ 周三Frontends │   │ 4种沟通渠道    │
│ (Member/     │  │ 周二Triage    │   │ 5项成员职责    │
│  Release/    │  │ on/off-record │   │ PR合并5原则    │
│  Admin)      │  │ HackMD归档    │   │ 开放包容文化   │
│ 无人数上限    │  │ 主持开放制度  │   │                │
│ 半年确认     │  └───────┬───────┘   └───────┬────────┘
└──────┬───────┘          │                   │
       │                  ▼                   ▼
       │         ┌───────────────┐   ┌────────────────┐
       │         │  主持指南      │   │  贡献流程       │
       │         │               │   │                │
       │         │ 6项主持职责   │   │ 扩展4步并入    │
       │         │ 开场脚本      │   │ 调查方法论     │
       │         │ 录制分段管理  │   │ 文档构建系统   │
       │         │ 反机器人机制  │   │ (Sphinx+MyST) │
       │         └───────────────┘   └────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│  决策机制：非正式共识 → 投票兜底               │
│  信任判断 > 流程繁琐                         │
│  慢讨论快执行                                │
│  公开优先，团队共担                          │
└──────────────────────────────────────────────┘
```

## 关键洞察

1. **这是操作手册而非代码库**：frontends-team-compass 是"软件"——团队运作的软件基础设施，包含流程、规范、角色定义，但不包含产品代码
2. **三层金字塔权限**：Council（无上限）→ Release Team（发布权限）→ Admin Team（≤7人，Owner），权限递增但所有决策共识优先
3. **双会议节奏**：周三方向会议 + 周二 Triage 操作会议，on/off-record 分段保护敏感讨论
4. **信源自动生成**：成员列表由 GitHub Actions 从 council 仓库同步，构建时脚本自动生成 HTML 表格，避免手动维护过期
5. **渐进式贡献路径**：扩展作者有 jupyterlab-contrib（社区）→ JupyterLab 核心组织两条路径，不强制并入官方

## 快速开始

- **新手入门**：从 [concepts/00-introduction.md](concepts/00-introduction.md) 开始
- **想主持会议**：阅读 [concepts/05-host-guide.md](concepts/05-host-guide.md)，然后实操 [examples/hosting-a-meeting.md](examples/hosting-a-meeting.md)
- **想贡献扩展**：阅读 [concepts/06-extension-contribution.md](concepts/06-extension-contribution.md)
- **理解治理**：阅读 [concepts/01-team-council.md](concepts/01-team-council.md) → [concepts/03-decision-making.md](concepts/03-decision-making.md)
- **信源查阅**：查看 [references/index.md](references/index.md) 获取原始资料

## 与其他 Bundle 的关系

| Bundle | 关系 |
|--------|------|
| [governance](../governance/index.md) | Jupyter 全局治理（EC/SSC/Foundation），本 bundle 是 Frontends 子项目层的 Team Compass，嵌套在全局治理之下 |
| [jupyter](../jupyter/index.md) | Jupyter 元包和核心组件 |
| [jupyter-notebook](../jupyter-notebook/index.md) | Jupyter Notebook v7，本仓库管理的前端项目之一 |

## 外部资源

- 🌐 在线文档：[jupyterlab-team-compass.readthedocs.io](https://jupyterlab-team-compass.readthedocs.io)
- 📦 GitHub 仓库：[jupyterlab/frontends-team-compass](https://github.com/jupyterlab/frontends-team-compass)
- 🧭 SSC Team Compass：[software-steering-council-team-compass](https://github.com/jupyter/software-steering-council-team-compass)
- 🧭 EC Team Compass：[ec.jupyter.org](https://ec.jupyter.org)

## 文档信息

- **生成方法**：source-code-to-okf-wiki skill（R→I→E→V→C 五阶段工作流）
- **方法论**：seven-concepts-cmd（R-I-E-C-A-F-V 七概念编排，知识沉淀场景）
- **原始信源版本**：2026年8月 main 分支
- **内容级别**：公开（Public）
- **许可证说明**：原始文档遵循 Jupyter 项目许可证（3-Clause BSD），本 bundle OKF 格式
