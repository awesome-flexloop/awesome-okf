---
type: Index
title: TRAE 共创项目
description: trae-co-creation-projects 是 TRAE 社区共创项目集合，采用社区驱动的协作模式，包含项目提交规范、评审标准和贡献工作流。
tags: [trae-co-creation, trae, co-creation, community, collaboration, projects]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/co-creation-source.md
    title: "Trae 共创项目源码信源"
---

# TRAE 共创项目知识包

本知识包系统介绍 [trae-co-creation-projects](https://github.com/trae-community/trae-co-creation-projects) 仓库——社区驱动的 TRAE 协作 AI 编程项目展示平台。内容涵盖仓库定位、Issue 表单驱动投稿、Collaboration 30% 权重的差异化审核体系，以及共创项目提交实战。

## 概念篇（concepts/）

- [共创项目仓库定位与协作核心理念](/concepts/00-introduction.md) — 协作编程展示平台定位（vs trae-demos 项目展示）、"共创"定义拓展（团队协作/结对编程/AI 结对编程）、Issue 表单驱动低门槛投稿、接受从想法到生产的所有项目阶段。
- [项目提交流程与 Issue 表单字段](/concepts/01-project-submission.md) — Issue 驱动投稿（无需 Fork/PR/Markdown）、中英双语 Markdown 模板、4 类必填信息字段（项目信息/描述/协作细节/技术细节）、个人项目投稿指南、Collaboration Details 核心字段填写要点。
- [审核标准与 Collaboration 权重差异化](/concepts/02-review-criteria.md) — 6 大项目分类（Web/Tools/AI/Libraries/Learning/Other）、4 项 Must Have 准入（含"展示有意义的协作"独有要求）、4 维权重（TRAE Usage 40% + Collaboration 30% + Code Quality 20% + Documentation 10%）、人机协作审核标准扩展、不同项目阶段的审核侧重。

## 示例篇（examples/）

- [提交共创项目示例](/examples/submit-project.md) — 个人项目（trae-todo CLI 工具，AI 结对编程）和团队项目两种场景的完整投稿演示，含 Issue 表单填写示例、Collaboration 字段写作要点、常见问题解答。

## 信源登记簿（references/）

- [共创项目仓库资源索引](/references/co-creation-source.md) — 仓库基本信息、目录结构、6 分类速查表、Must Have 标准、审核权重对比表、投稿 4 类信息字段映射。

## 关键事实

- trae-co-creation-projects 目前处于**初始化阶段**，README 尚无已收录项目列表
- **Collaboration 占 30% 权重**是与 trae-demos 的核心差异（demos 不评估协作维度），体现"共创"定位
- 将 **"AI 结对编程"纳入共创定义**——个人开发者用 TRAE 编程本身就是人机协作，个人项目可投稿
- 采用 **Issue 表单驱动投稿**：只需在 GitHub 网页填写表单，维护者审核通过后负责展示
- **接受任何阶段的项目**：从想法到生产环境都可分享，区别于 trae-demos 要求 polished 成品
- 提供中英双语 Markdown Issue 模板（project-submission.md / project-submission-zh.md）

```{toctree}
:hidden:
:maxdepth: 7

concepts/00-introduction
concepts/01-project-submission
concepts/02-review-criteria
examples/submit-project
references/co-creation-source
spec/facts
spec/insights
```
