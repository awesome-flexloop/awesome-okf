---
type: Index
title: TRAE Agents 智能体配置
description: trae-agents 是 TRAE 社区维护的自定义智能体配置集合仓库，采用"文档即配置"模式，通过 Markdown+YAML frontmatter 描述 Agent 的名称、提示词、工具和协作关系。
tags: [trae-agents, trae, agent, custom-agent, configuration, prompt]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/agents-source.md
    title: "Trae Agents 源码信源"
---

# TRAE Agents 知识包

本知识包系统介绍 [trae-agents](https://github.com/trae-community/trae-agents) 仓库——TRAE 社区维护的自定义智能体配置集合。内容涵盖仓库定位、"文档即配置"模式、目录结构与模板规范、Git Commit Generator 参考实现分析以及自定义 Agent 创建流程。

## 概念篇（concepts/）

- [TRAE Agents 仓库定位与"文档即配置"模式](/concepts/00-introduction.md) — 仓库定位（Agent 配置集合 vs MCP 工具服务器）、Agent 配置四要素（名称/提示词/工具/协作）、`agents/<name>/README.md` 目录约定、"文档即配置"设计取舍。
- [Agent 目录结构与模板规范](/concepts/01-agent-structure.md) — kebab-case 目录命名、README 必备 8 章节结构、`_template/` 目录作用、内置工具 5 项勾选清单、工具最小化原则、贡献自检清单。
- [Git Commit Generator 参考实现分析](/concepts/02-git-commit-agent.md) — 唯一正式 Agent 的完整分析：11 种 Conventional Commits 类型、格式规则、5 条行为原则、4 个 few-shot 示例、仅勾选"终端命令"的最小化配置、温度 0.3-0.5 的参数调优。

## 示例篇（examples/）

- [创建自定义 Agent 示例](/examples/create-agent.md) — 从零创建 Code Review Expert Agent 的完整流程：复制模板→填写 frontmatter→编写 Prompt→配置工具→编写示例→配置参数→更新列表→提交 PR，含每个步骤的具体内容示例。

## 信源登记簿（references/）

- [TRAE Agents 仓库资源索引](/references/agents-source.md) — 仓库基本信息、目录结构、Agent 配置四要素、内置工具清单、模板 8 章节结构、Git Commit Generator 配置速查表、Issue 模板字段、6 步贡献流程。

## 关键事实

- trae-agents 目前处于**初始化阶段**：仅 1 个正式 Agent（git-commit-generator，Stable）+ 1 个模板目录
- 采用**"文档即配置"模式**：纯 Markdown + YAML frontmatter，而非 JSON/YAML 结构化配置，牺牲机器可解析性换取人类可读性和 Git 友好性
- 仓库明确**区分 Agent 和 MCP**：Agent 配置在 trae-agents，工具服务器在 trae-mcp
- 遵循**质量优先于数量**的冷启动策略：先打磨 1 个高质量参考实现，再通过模板和 Issue 流程引导社区贡献
- 提供 2 个 Issue 模板：Agent Request（新 Agent 请求）和 Bug Report（问题反馈）

```{toctree}
:maxdepth: 7

concepts/00-introduction
concepts/01-agent-structure
concepts/02-git-commit-agent
examples/create-agent
references/agents-source
spec/facts
spec/insights
```
