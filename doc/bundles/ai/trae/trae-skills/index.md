---
type: Index
title: Trae Skills 文档索引
description: trae-skills 社区技能仓库完整文档，涵盖 SKILL.md 格式规范、三类技能模式（纯Prompt/脚本辅助/Workflow编排）、社区积分机制和自定义技能编写指南。
tags: [trae-skills, index, documentation]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/skills-source.md
    title: Trae Skills 源码信源
---

# Trae Skills 文档

Trae Skills 是 TRAE IDE 的社区维护 Agent Skills 集合，采用 MIT 许可证。每个 Skill 的核心是 `SKILL.md`——一个 YAML frontmatter + Markdown 指令体构成的提示词包（Prompt Package），通过自然语言指令指导 Agent 行为。

## 概念文档

| 文档 | 说明 |
|------|------|
| [00-introduction.md](/concepts/00-introduction.md) | Trae Skills 简介：什么是 Skill、社区仓库定位、Skill vs 插件 vs MCP 区别 |
| [01-skill-format.md](/concepts/01-skill-format.md) | SKILL.md 格式规范：frontmatter 字段（name/description/author/version/tags）、章节结构、版本管理 |
| [02-skill-categories.md](/concepts/02-skill-categories.md) | 技能分类与三种模板模式：纯 Prompt 型/脚本辅助型/Workflow 编排型对比 |
| [03-prompt-only-skills.md](/concepts/03-prompt-only-skills.md) | 纯 Prompt 型技能：cn-punctuation-checker、git-commit-generator、web-design-teroop 等编写模式 |
| [04-script-assisted-skills.md](/concepts/04-script-assisted-skills.md) | 脚本辅助型技能：daily-hot-news 四层数据源、video-to-keyframes dHash 算法、zopia API 集成 |
| [05-workflow-skills.md](/concepts/05-workflow-skills.md) | Workflow 编排型技能：daily-trend-writer 六阶段流水线、kz-article-deep-analysis 结构化标签、trae-claw-install 跨平台部署 |
| [06-community-points.md](/concepts/06-community-points.md) | 社区积分机制：points ledger、GitHub Actions 自动化、幂等键去重、community-points-data 分支 |
| [07-write-skill.md](/concepts/07-write-skill.md) | 编写自定义 Skill：_template 使用、触发条件设计、脚本集成、测试与提交 PR |

## 示例文档

| 文档 | 说明 |
|------|------|
| [create-first-skill.md](/examples/create-first-skill.md) | 创建第一个 Skill 完整示例（readme-checker，基于 _template） |
| [skill-with-python-script.md](/examples/skill-with-python-script.md) | 带 Python 脚本的 Skill 示例（weather-report，参考 daily-hot-news 模式） |
| [trigger-condition-design.md](/examples/trigger-condition-design.md) | 触发条件设计示例：正面触发词、反面排除、约束条款的正反案例对比 |
| [points-contribution.md](/examples/points-contribution.md) | 社区积分贡献示例：PR 合并、Issue 解决、手动加分、幂等性验证全链路 |

## 参考文档

| 文档 | 说明 |
|------|------|
| [skills-source.md](/references/skills-source.md) | 源码信源索引：12 个技能目录、Python/JS 脚本、GitHub Actions 工作流完整映射 |

## 快速开始

1. 阅读 [简介](/concepts/00-introduction.md) 理解 Skill 的本质
2. 阅读 [SKILL.md 格式规范](/concepts/01-skill-format.md) 掌握文件结构
3. 阅读 [创建第一个 Skill](/examples/create-first-skill.md) 动手实践
4. 参考 [编写自定义 Skill](/concepts/07-write-skill.md) 深入学习高级模式

```{toctree}
:maxdepth: 7

concepts/00-introduction
concepts/01-skill-format
concepts/02-skill-categories
concepts/03-prompt-only-skills
concepts/04-script-assisted-skills
concepts/05-workflow-skills
concepts/06-community-points
concepts/07-write-skill
examples/create-first-skill
examples/points-contribution
examples/skill-with-python-script
examples/trigger-condition-design
references/skills-source
spec/facts
spec/insights
```
