---
title: Agent Learning Hub
type: index
bundle: Agent-Learning-Hub
description: Datawhale 出品的 AI Agent 学习路线图，将社区优秀分享、官方博客、论文、开源项目和工程经验整理成可照着执行的 9 阶段学习 todo list 和 11 级项目阶梯。
concepts:
  - /datawhale/Agent-Learning-Hub/concepts/agent-learning-roadmap
  - /datawhale/Agent-Learning-Hub/concepts/resource-curation
references:
  - /datawhale/Agent-Learning-Hub/references/source-repo
examples:
  - /datawhale/Agent-Learning-Hub/examples/index
---

# Agent Learning Hub

**A curated AI Agent learning roadmap for people who want to build useful, reliable agents instead of collecting random links.**

Agent Learning Hub 是 Datawhale 出品的 AI Agent 学习路线图。项目的核心目标不是收集随机链接，而是把社区里优秀的分享、官方博客、论文、开源项目和真实工程经验，整理成一份**可以照着执行的 AI Agent 学习 todo list**。

仓库由陈思州（Datawhale 成员）维护，包含两个核心文件：`README.md`（Markdown 格式完整内容）和 `index.html`（带进度追踪、搜索、笔记功能的交互式 Web 版本）。

## 知识地图

### 核心概念

- [Agent 学习路线图](/datawhale/Agent-Learning-Hub/concepts/agent-learning-roadmap.md)——9 阶段递进式 Learning Todo List（Stage 0-8）与 11 级 Project Ladder，每阶段配有 checklist、推荐阅读和可交付产出物
- [核心资源分类](/datawhale/Agent-Learning-Hub/concepts/resource-curation.md)——官方指南、项目地图、Skills/协议、现代 Agent 系统、论文、GitHub 仓库等九大资源分类体系

### 示例

- [示例索引](/datawhale/Agent-Learning-Hub/examples/index.md)——阶段产出物与项目阶梯实践指引（本项目为路线图类项目，不含可运行源代码）

### 信源

- [GitHub 仓库信源](/datawhale/Agent-Learning-Hub/references/source-repo.md)——项目官方仓库地址、README.md 与 index.html 文件结构说明

## 快速上手

1. 根据自身基础选择起点：新手从 Stage 0 开始，有 LLM 经验者从 Stage 2/3 切入
2. 按 Learning Todo List 逐项完成 checklist，每个阶段交付对应产出物
3. 需要追踪进度和做笔记时，打开 `index.html` 使用交互式 Web 版本
4. 想做项目时参考 Project Ladder，从 Calculator Agent 逐步进阶到 Production Harness
5. 找资料时浏览 Curated Resources，优先读官方文档和经典论文

## 项目特点

- **可执行而非可阅读**：每个阶段有 checklist 和产出物，学没学会以能否交付作品为准
- **观点鲜明**：明确标注当前 5 个优先方向，同时指出不建议重押的老式框架
- **资源分层**：开源项目按学习目的分层（从零构建/个人 Agent/Coding Agent/Harness/Deep Research 等），而非按 star 数排列
- **交互增强**：index.html 提供进度追踪、搜索、暗色主题、Markdown 笔记等学习辅助功能
- **轻量实现**：单文件 HTML、无前端框架、仅依赖 marked.js CDN

## 8 条学习原则

1. Build first, then read deeper.
2. Prefer small reliable agents over impressive demos.
3. Use tools with strict schemas.
4. Add evals before you add more agents.
5. Trace every important run.
6. Treat multi-agent as a coordination problem.
7. Keep humans in the loop for risky actions.
8. Respect platform rules, copyrights, and data access boundaries.

## 外部链接

- GitHub 仓库：https://github.com/datawhalechina/Agent-Learning-Hub
- 维护者：[陈思州](https://github.com/jjyaoao)（Datawhale 成员）
