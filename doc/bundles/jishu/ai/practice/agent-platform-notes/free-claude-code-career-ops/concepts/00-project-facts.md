---
type: Concept
title: "两个项目分别解决什么问题"
description: "从模型访问代理与求职工作流两个层面，区分 free-claude-code 和 career-ops 的真实职责。"
tags: [free-claude-code, career-ops, Agent, 开源工具]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: stable
stale_after: 2026-10-31
sources:
  - { id: article, resource: "/references/article-source.md" }
  - { id: verification, resource: "/references/verification.md" }
---

# 两个项目分别解决什么问题

这篇文章将两个项目放在一起，但它们位于不同层次：`free-claude-code` 处理“编码 Agent 如何连接模型”，`career-ops` 处理“如何把 AI CLI 组织成求职流水线”。[F-002][F-007][F-014]

## free-claude-code：模型访问与客户端适配层

项目 README 将它描述为多 provider、多客户端的统一入口，支持 10 个编码 Agent，并可在 provider 故障时切换到下一个配置好的模型。[F-006][F-008] 它保留的是 Agent 的工具调用、上下文和客户端体验，后端模型不必是 Claude。

因此，“免费 Claude Code”更准确的理解是：使用 Claude Code 的工具链或兼容接口，连接可用的免费、付费或本地模型。它不等于免费获得 Anthropic 的 Claude 模型本身；项目也明确声明与 Anthropic 无关。[F-012]

## career-ops：求职决策与材料流水线

`career-ops` 将职位抓取、语义匹配、评分、简历 PDF 生成、投递追踪和面试准备组织成一个本地工作流。[F-015][F-018][F-019] 它的核心不是自动海投，而是把大量职位筛成少量值得人工投入的机会；README 建议低于 4.0/5 的职位不投。[F-016][F-017]

## 阅读结论

二者不是同类产品，也不存在“一个替代另一个”的关系。前者是模型/客户端接入层，后者是任务工作流层；组合时需要特别检查后端模型能力是否足以支持职位分析、PDF 生成和人工复核。

## 相关概念

- [组合闭环](01-combination-loop.md)
- [访问与风险边界](02-access-and-risk-boundaries.md)
