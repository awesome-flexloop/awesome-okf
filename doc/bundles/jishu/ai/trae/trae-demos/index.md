---
type: Index
title: TRAE Demos 项目演示
description: trae-demos 是 TRAE 社区维护的项目演示仓库，收录基于 TRAE 构建的 Web 应用、工具、游戏和 AI 应用，提供 Demo 格式规范和贡献提交流程。
tags: [trae-demos, trae, demo, showcase, examples, projects]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/demos-source.md
    title: "Trae Demos 源码信源"
---

# TRAE Demos 知识包

本知识包系统介绍 [trae-demos](https://github.com/trae-community/trae-demos) 仓库——社区驱动的 TRAE 构建项目展示平台。内容涵盖期数制内容组织、Demo Markdown 格式、多场景 Issue 模板投稿机制和审核权重体系。

## 概念篇（concepts/）

- [TRAE Demos 定位与期数制组织](concepts/00-introduction.md) — 深度展示平台定位（vs awesome-trae 索引定位）、period-N 期数制组织模式（类似技术期刊的定期发布节奏）、双层展示结构、Markdown 驱动与中英双语策略。
- [Demo Markdown 文档格式](concepts/01-demo-format.md) — Demo 文件结构化字段设计（作者/类型/技术栈/仓库/演示/亮点/运行/截图）、中英双语文件对格式、两个已收录 Demo（Minecraft Guilin City Walk / TraeClaw）的形态对比。
- [投稿流程与多场景 Issue 模板](concepts/02-contribution-process.md) — Issue 驱动投稿（无需 Fork/PR）、4 项 Must Have 准入、TRAE Usage 40% 最高权重的审核体系、7 个 YAML 模板覆盖 5 种场景（投稿/报告/更新/需求）、禁用空 Issue 策略。

## 示例篇（examples/）

- [提交 Demo 示例](examples/submit-demo.md) — 以 AI 诗词生成器项目为例，演示完整投稿流程：自检准入→选择模板→填写 Issue 表单→等待审核→收录展示，含表单填写示例、提高通过率建议和常见拒绝原因。

## 信源登记簿（references/）

- [TRAE Demos 仓库资源索引](references/demos-source.md) — 仓库基本信息、目录结构、期数速查表、Must Have 标准、5 项目分类、审核权重表、7 模板映射、已收录 Demo 信息。

## 关键事实

- trae-demos 采用**期数制（period-based）**组织内容，类似技术期刊，定期发布制造仪式感和追更体验
- 采用 **Issue 驱动投稿**：投稿者只需在 GitHub 网页填写表单，无需 Fork/写 Markdown/PR，维护者审核通过后负责创建展示文件
- **TRAE Usage 占 40% 最高权重**，确保平台聚焦"用 TRAE 构建"而非泛项目展示
- 配置 **7 个 YAML Issue 模板**覆盖 5 种社区行为（投稿/报告问题/更新信息/需求征集），并禁用空 Issue
- 当前已收录 2 个 Demo（Minecraft Guilin City Walk、TraeClaw），Demo #2 期数标注与 README 汇总存在不一致
- 两个 Demo 展示了平台接受多种项目形态：传统 Web App（命令行运行）和 AI 插件（自然语言安装）

```{toctree}
:hidden:
:maxdepth: 7

concepts/00-introduction
concepts/01-demo-format
concepts/02-contribution-process
examples/submit-demo
references/demos-source
spec/facts
spec/insights
```
