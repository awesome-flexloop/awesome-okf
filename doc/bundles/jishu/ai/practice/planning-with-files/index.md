---
okf_version: "0.2"
type: group
title: "planning-with-files：像 Manus 一样工作"
description: "AI Agent 上下文工程方法论——3-File Pattern 文件系统外存 + Hooks 自动化机制，源自 Manus（Meta 20 亿美元收购）的开源实践"
sources:
  - id: wechat-article
    resource: https://mp.weixin.qq.com/s/fBpL-pwFfxfj80mnP5JoYA
    title: "planning-with-files:像 Manus 一样工作"
    author: "叽半斤"
  - id: github-repo
    resource: https://github.com/OthmanAdi/planning-with-files
    title: "OthmanAdi/planning-with-files"
    author: "OthmanAdi"
tags:
  - planning-with-files
  - context-engineering
  - ai-agent
  - hooks
  - 3-file-pattern
  - manus
  - context-window
  - 文件系统外存
generated:
  by: "agent:seven-concepts-cmd"
  at: "2026-09-08T00:00:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-09-08T00:00:00+08:00"
status: stable
stale_after: 2027-09-08
---

# planning-with-files：像 Manus 一样工作

本知识束（bundle）记录 AI Agent 上下文工程方法论的开源实践——planning-with-files 项目。该项目由开发者 OthmanAdi 于 2026 年 1 月在 GitHub 开源，其 Slogan 为"Work like Manus — the AI agent company Meta acquired for $2 billion"。项目将 Manus 团队价值 20 亿美元的工作方法浓缩为一套可复用的工程模式：对于每个复杂任务，创建三个 Markdown 文件（task_plan.md / findings.md / progress.md），将文件系统当作 AI 的"外接硬盘"，弥补上下文窗口易失、有限的根本缺陷。

planning-with-files 发展至 v2.43.0 后，已从文件模板升级为一套 Hooks（钩子）机制——在 AI 工作流的关键节点（任务开始、重大决策、阶段完成、停止前验证）自动触发固定动作，将"先建计划""每 2 次操作存盘""停止前验证"等规则从依赖 AI 自觉遵守转变为确定性代码触发。本束通过 R→I→E→V→C 五阶段链路（七概念方法论·场景 4 知识沉淀）提炼其可迁移模式，供 SpecWeave 及其他 AI Agent 工作流参考。

> **关键提醒**：planning-with-files 的 Hooks 机制是 Claude Code 特有的，Cursor 等编辑器不支持自动 Hooks，但核心的文件规划工作流完全适用。适用边界为 3 步以上复杂任务，简单问题、单文件编辑和快速查询无需启用。

## 工作文档

* [facts.md](facts.md) — 事实清单（35 条零推测事实）
* [insights.md](insights.md) — 核心洞察（3 条四元组）
* [patterns.md](patterns.md) — 可迁移模式（2 个模式 + V 阶段对抗审查记录）
* [log.md](log.md) — 执行日志（CMD-LOG 格式）

```{toctree}
:hidden:
:maxdepth: 3

facts
insights
patterns
log
```
