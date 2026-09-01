---
type: Concept
title: "Frontends Team Compass 仓库简介"
description: "了解 frontends-team-compass 仓库的定位、核心内容、文档结构和在 Jupyter 生态中的角色。"
tags: [jupyter, frontends, team-compass, introduction, overview]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T11:36:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:36:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: "README 文档信源"
  - id: conf-py
    resource: /references/conf-py-source.md
    title: "文档构建配置信源"
---

# Frontends Team Compass 仓库简介

`frontends-team-compass` 是 Jupyter Frontends 团队（JupyterLab 前端团队）的**团队罗盘**仓库——一个纯文档性质的运营手册，用于团队交互、同步进展和归档会议记录。它不包含可执行的产品代码，而是承载团队治理、运作流程和社区协作的全部"软件基础设施"。

## 仓库定位

在 Jupyter 治理体系中，每个官方子项目都维护自己的 Team Compass 仓库。frontends-team-compass 服务于 JupyterLab 生态系统的前端方向，覆盖 JupyterLab、Jupyter Notebook（v7+）等前端项目的团队运作。其核心目标是**持续的团队和项目改进**（continuous team and project improvement）。

仓库包含四大类内容：

| 内容类型 | 说明 |
|---------|------|
| 团队会议议程与归档 | 周会议程、会议记录、Triage 记录 |
| 方向与行动计划 | 路线图、里程碑、优先级决策 |
| 沟通与团队文化 | 尊重协作的沟通规范、行为准则 |
| 认可与团队庆祝 | 贡献者认可、里程碑庆祝 |

## 文档结构

```
frontends-team-compass/
├── README.md                     # 仓库入口（会议信息+扩展贡献流程）
├── .readthedocs.yml              # ReadTheDocs 构建配置
├── docs/
│   ├── index.rst                 # Sphinx 文档入口（MyST+reStructuredText）
│   ├── conf.py                   # Sphinx 构建配置
│   ├── requirements.txt          # 文档构建依赖
│   ├── Makefile / make.bat       # 构建脚本
│   ├── team.md                   # 现任 Council 成员列表
│   ├── host-guide.md             # 会议主持指南
│   ├── team/
│   │   ├── becoming-member.md    # 成为 Council 成员的流程
│   │   ├── decision-making.md    # 决策制定流程
│   │   ├── member-guide.md       # 成员行为指南
│   │   ├── contributors.yaml     # 成员数据（自动生成）
│   │   └── active.txt            # 成员 HTML 表格（构建时生成）
│   ├── surveys/
│   │   └── 2020-jupyterlab-survey.md  # 2020年用户调查问卷
│   ├── scripts/
│   │   └── gen_contributors.py   # 贡献者表格自动生成脚本
│   └── _static/                  # 静态资源（logo、favicon、CSS）
```

## 技术栈

文档使用 **Sphinx + sphinx_book_theme + MyST Parser** 构建：

- **Sphinx** ≥ 3.0：Python 生态最成熟的文档构建工具
- **MyST Parser**：允许在 Sphinx 中使用 Markdown（.md 文件），与 reStructuredText（.rst）并存
- **sphinx_book_theme**：现代化的文档主题，与 Jupyter Book 视觉风格统一
- **ReadTheDocs**：自动构建和托管，Ubuntu 22.04 + Python 3.11 环境
- **自动化脚本**：`gen_contributors.py` 在构建时从 YAML 数据生成 HTML 成员表格

## 核心团队理念

仓库以一句话总结团队精神：

> **"We sail together"**（我们同舟共济）

团队重视每个成员的个人优势和贡献，但无论修复 Bug 还是获得表彰，**团队而非个人**承担责任和荣誉。这一理念贯穿所有运作规则——从共识优先的决策方式，到开放包容的讨论氛围。

## 与其他 Jupyter 仓库的关系

frontends-team-compass 在 Jupyter 生态中处于"治理层"位置：

```
┌─────────────────────────────────────────────────────┐
│  jupyter/governance（全局治理：EC/SSC/Foundation）   │
└───────────────────────┬─────────────────────────────┘
                        │ 指导
┌───────────────────────▼─────────────────────────────┐
│  jupyterlab/frontends-team-compass（本仓库）         │
│  前端子项目团队罗盘：会议/成员/决策/PR规范            │
└───────────────────────┬─────────────────────────────┘
                        │ 管理
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ jupyterlab   │ │ notebook     │ │ lumino等     │
│ （主前端IDE） │ │ （v7+前端）  │ │ （底层组件库）│
└──────────────┘ └──────────────┘ └──────────────┘
```

## 相关概念

- [Frontends Council 架构](01-team-council.md) — 了解三层成员体系（Council/Release/Admin）
- [双周会议制度](02-meetings.md) — 周三团队会 + 周二 Triage 会的运作细节
- [文档构建系统](07-doc-infrastructure.md) — Sphinx + MyST 构建配置和自动化脚本
