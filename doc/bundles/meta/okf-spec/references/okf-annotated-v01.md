---
type: Reference
title: OKF v0.1 注释版开发者指南（An Annotated Guide）
description: OKF v0.1 Draft 的开发者带注释走查版，包含设计原则阐释、实践建议、代码示例与作者观点，作为 v0.2 规范的补充参考。
tags: [okf, spec, reference, v0.1, annotated-guide]
resource: https://okf.md/spec
generated: { by: reference_agent/trae-glm, at: 2026-08-21T08:00:00Z }
status: draft
stale_after: 2027-06-30T00:00:00Z
sources:
  - id: okf-md-spec
    resource: https://okf.md/spec
    title: Open Knowledge Format (OKF) — An Annotated Guide, Version 0.1 Draft
---

# OKF v0.1 注释版开发者指南

本文件登记 [okf.md/spec](https://okf.md/spec) 上发布的 OKF v0.1 Draft 注释版开发者指南（*An Annotated Guide*）作为参考信源。

## v0.1 与 v0.2 的关系

- **v0.2**（[okf-spec.md](okf-spec.md)）是正式规范文档，采用标准化 RFC 风格，精确规定 MUST/SHOULD/MAY 要求。
- **v0.1 Annotated Guide** 是 v0.1 版本的开发者走查文档，作者（fabricioctelles）以"A developer's walkthrough. Opinions included."为定位，在规范条文之外提供了：
  - 三大设计原则（Design Principles）的详细阐释
  - 对每个设计决策的个人观点和理由说明
  - 丰富的实践建议（type 字段治理、扩展字段用法、自动化脚本等）
  - 额外的代码示例（Metric 概念 LTV 90d 示例、自动化 index.md bash 脚本）
  - 与 Obsidian 等工具的对比说明
  - "断链即特性"等设计意图的解释

## v0.1 注释版中 v0.2 未直接收录的增量内容

以下内容来源于 v0.1 Annotated Guide，在 v0.2 正式规范中没有直接对应章节，但对理解和使用 OKF 具有重要参考价值：

| 内容主题 | 说明 | 收录位置 |
|---|---|---|
| 三大设计原则 | Minimally opinionated / Producer-consumer independence / Format not platform | [concepts/design-principles.md](../concepts/design-principles.md) |
| type 字段治理建议 | "自由但危险"——团队应约定 type 命名规范 | [concepts/practical-guidance.md](../concepts/practical-guidance.md) |
| 扩展字段实用示例 | `owner`、`freshness_sla` 等自定义字段 | [concepts/practical-guidance.md](../concepts/practical-guidance.md) |
| 自动化 index.md 脚本 | bash 脚本自动生成索引 | [concepts/practical-guidance.md](../concepts/practical-guidance.md) |
| 断链即特性解释 | 允许先引用后补全的设计意图 | [concepts/practical-guidance.md](../concepts/practical-guidance.md) |
| 结构化 Markdown 对 RAG 的重要性 | LLM+RAG 场景下标题结构对减少幻觉的作用 | [concepts/practical-guidance.md](../concepts/practical-guidance.md) |
| log.md vs git log 区别 | 受众不同，log.md 是人工 CHANGELOG | [concepts/practical-guidance.md](../concepts/practical-guidance.md) |
| Obsidian 用户对比 | Bundle≈vault, Concept≈note, Link≈wikilink | [concepts/practical-guidance.md](../concepts/practical-guidance.md) |
| v0.1 Citations → v0.2 footnotes 演进 | 引用机制从 # Citations 到 sources+footnotes 的变化 | [concepts/practical-guidance.md](../concepts/practical-guidance.md) |
| 实践目录放置建议 | `knowledge/` 或 `docs/catalog/` 目录 | [concepts/practical-guidance.md](../concepts/practical-guidance.md) |
| Metric 概念完整示例 | Revenue per Customer (LTV 90d) | v0.2 规范 Appendix A 已包含损益表示例 |
| 非目标的 proto 解释 | "If you already have a .proto..." | [concepts/motivation.md](../concepts/motivation.md) 非目标章节已覆盖 |

## 注意事项

- v0.1 Annotated Guide 中的部分内容（如 `timestamp` frontmatter 字段、`# Citations` 正文引用列表）在 v0.2 中已被新字段族取代（`generated.at`、`sources` + footnotes），使用时请注意版本差异。
- 本信源登记不收录 v0.1 注释版全文（因其为带观点的注释文档而非正式规范），而是将其增量价值提炼到对应的概念文档中。
- 如需查阅 v0.1 注释版原文，请访问 [okf.md/spec](https://okf.md/spec)。

## 相关信源

- [OKF v0.2 正式规范](okf-spec.md) - 本 bundle 的权威信源
- [SaaS Metrics Quickstart 示例来源](https://okf.md/quickstart) - 快速入门教程
- [OKF Agent Skill 文档](https://okf.md/skill) - 智能体技能安装与使用
- [OKF Validator](https://okf.md/validator) - 在线验证工具
