---
type: Concept
title: 贡献指南与权重评分审核机制
description: awesome-trae 的贡献准入标准、4 项 Must Have 门槛、6 类提交类别、审核时间线与 4 维权重评分体系
tags: [contribution, review-criteria, weighted-scoring, pr-workflow, awesome-trae, trae]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/awesome-source.md
    title: "Awesome TRAE 源码信源"
---

# 贡献指南与权重评分审核机制

## 贡献准入门槛（Must Have）

向 awesome-trae 提交资源必须满足 4 项硬性标准，缺一不可：

| 标准 | 说明 | 反例 |
|------|------|------|
| **TRAE Related** | 资源必须与 TRAE 生态直接相关 | 通用编程工具未使用 TRAE |
| **Accessible** | 必须公开可访问（公开 GitHub 仓库或在线演示链接） | 私有仓库、需登录访问的内容 |
| **Quality** | 精心制作且功能完整，非半成品或原型 | Hello World 级别的示例项目 |
| **Documented** | 必须有基本的文档说明使用方式 | 无 README、无使用说明的仓库 |

这 4 项标准构成第一道过滤门槛，不满足的 PR 将直接被关闭，不进入评分环节。

## 提交类别

贡献分为 6 个类别，提交时需在 PR 中注明所属类别：

1. **Projects** — 基于 TRAE 构建的项目和应用
2. **Agents** — TRAE 自定义智能体配置
3. **Tools** — TRAE 相关工具和扩展
4. **Tutorials** — 教程、指南和最佳实践文章
5. **Templates** — 项目模板和脚手架
6. **Resources** — 学习资源（视频、博客、书籍等）

## 审核时间线

```
提交 PR → 24h 内确认收到 → 3-5 工作日审核 → 通过/退回 → 收录
```

- **24 小时确认**：维护者在 24 小时内回应 PR，表示已收到并开始审核
- **3-5 工作日审核**：完整的审核评估周期，包含权重评分和讨论
- **审核通过**：合并 PR，资源条目出现在 README 对应分类中

## 4 维权重评分体系

审核通过 Must Have 门槛后，维护者按以下 4 个维度对资源进行评分，总分 100 分：

| 维度 | 权重 | 评估要点 |
|------|------|---------|
| **Relevance（相关性）** | 30% | 与 TRAE 的关联程度，是否体现 TRAE 独特价值 |
| **Quality（质量）** | 30% | 完成度、代码质量、用户体验、创新性 |
| **Documentation（文档）** | 20% | README 完整性、使用说明清晰度、截图/演示 |
| **Impact（影响力）** | 20% | 对社区的价值、潜在用户规模、示范效应 |

Relevance 和 Quality 各占 30%，是最重要的两个维度。这确保了收录的资源既"真正属于 TRAE 生态"，又"质量过硬"。Documentation 和 Impact 各占 20%，作为辅助评估。

## 双语贡献要求

awesome-trae 维护中英双语 README，贡献者提交 PR 时需要：

1. 同时更新 `README.md`（英文）和 `README_zh.md`（中文）
2. 英文条目的描述使用英文
3. 中文条目可提供中文翻译，也可直接使用英文描述

## 设计理念

引入权重评分体系的核心目的是将"什么是好资源"从维护者的主观偏好转化为**可讨论的客观维度**。当审核意见出现分歧时，可以回到 4 个维度逐一讨论，降低审核争议，也让贡献者在提交前有明确的质量优化方向。

## 相关链接

- [Awesome List 定位与双层分类](00-introduction.md)
- [资源分类详解](02-resource-categories.md)
- [添加资源条目示例](../examples/add-resource.md)
- [Awesome TRAE 仓库资源索引](../references/awesome-source.md)
