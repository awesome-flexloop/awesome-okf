---
type: Concept
title: 审核标准与 Collaboration 权重差异化
description: trae-co-creation-projects 的 6 项目分类体系、4 维权重评分以及 Collaboration 30% 权重如何体现"共创"定位
tags: [co-creation, review-criteria, collaboration-weight, categories, trae-co-creation, trae]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/co-creation-source.md
    title: "Trae 共创项目源码信源"
---

# 审核标准与 Collaboration 权重差异化

## 6 个项目分类

trae-co-creation-projects 定义了 6 个项目分类，覆盖从全栈应用到艺术装置的广泛场景：

| 分类 | Emoji | 收录范围 |
|------|-------|---------|
| Web Applications | 🌐 | 全栈 Web 应用、前端项目、后端服务 |
| Tools & Utilities | 🛠️ | 开发者工具、CLI 工具、效率工具 |
| AI & Machine Learning | 🤖 | AI/ML 项目、模型应用、数据科学 |
| Open Source Libraries | 📦 | 可复用库、框架、SDK |
| Learning Resources | 📚 | 教程、指南、教育内容、学习笔记 |
| Other | 🎨 | 游戏、移动应用、IoT、艺术装置等无法归入以上类别的项目 |

6 个分类比 trae-demos 的 5 分类多了 Open Source Libraries 和 Learning Resources，少了 Games 作为独立分类（归入 Other），体现了共创平台对开源库和教育内容的重视。

## 4 项 Must Have 准入标准

投稿项目必须满足：

1. **使用 TRAE 作为核心协作工具**：TRAE 不只是偶尔使用，而是协作过程的核心
2. **展示有意义的协作**：团队协作、结对编程，或 AI 结对编程（人机协作）
3. **可访问**：公开仓库或在线演示
4. **有基础文档**：README 或文档说明项目

第 2 条"展示有意义的协作"是本仓库独有的准入要求，trae-demos 没有这条标准。

## 审核权重：Collaboration 为核心差异化维度

评分权重设计体现了"共创"的核心定位：

| 维度 | 权重 | 评估要点 |
|------|------|---------|
| **TRAE Usage** | **40%** | TRAE 在协作中的使用深度和核心性 |
| **Collaboration** | **30%** | 协作质量、协作模式的展示度、TRAE 如何促进协作 |
| Code Quality | 20% | 代码质量、工程规范 |
| Documentation | 10% | 文档完整性和清晰度 |

### 与 trae-demos 的权重对比

| 维度 | trae-demos | trae-co-creation-projects | 差异说明 |
|------|-----------|--------------------------|---------|
| TRAE Usage | 40% | 40% | 一致——都是 TRAE 生态平台 |
| Collaboration | 0% | **30%** | **核心差异**：共创要求展示协作 |
| Code Quality | 25% | 20% | 共创降低了纯代码质量权重 |
| Completeness | 20% | - | demos 更看重完成度 |
| Documentation | 15% | 10% | 共创对文档要求略低（接受早期项目） |

### Collaboration 维度评什么

Collaboration 维度的 30% 权重主要评估：

1. **协作模式清晰度**：是什么样的协作？（团队/结对/AI 结对）
2. **TRAE 的协作角色**：TRAE 在协作中具体做了什么？
3. **协作故事性**：是否有具体的协作场景和案例？
4. **可复制性**：其他开发者能否从中学到协作经验？

## 人机协作的审核标准扩展

对于个人项目（AI 结对编程），Collaboration 维度重点关注：

- TRAE 是否在开发过程中扮演了明确的"伙伴"角色（如代码审查者、结对编程伙伴、技术顾问）
- 是否有具体的"人机协作"场景描述（不只是"用了 TRAE"）
- 能否展示 AI 协作带来的独特价值（效率提升、新思路、降低门槛等）

这意味着即使是单人项目，只要能清楚展示"与 TRAE 协作"的过程和价值，也能获得较高的 Collaboration 评分。

## 项目阶段包容性

共创项目接受从想法到生产的所有阶段项目，不同阶段的审核侧重不同：

| 阶段 | 审核侧重 |
|------|---------|
| 想法阶段 | 协作计划的可行性、创意价值 |
| 开发中 | 协作过程的展示、TRAE 使用经验 |
| 已完成 | 协作成果、代码质量、文档 |
| 生产中 | 实际效果、协作模式的可复制性 |

## 相关链接

- [共创项目仓库定位与协作核心理念](00-introduction.md)
- [项目提交流程与 Issue 表单](01-project-submission.md)
- [提交共创项目示例](../examples/submit-project.md)
- [共创项目仓库资源索引](../references/co-creation-source.md)
