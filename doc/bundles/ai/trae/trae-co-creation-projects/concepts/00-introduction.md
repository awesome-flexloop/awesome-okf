---
type: Concept
title: 共创项目仓库定位与协作核心理念
description: trae-co-creation-projects 作为协作编程项目展示平台的定位、Issue 表单驱动投稿模式和 Collaboration 30% 权重的审核设计
tags: [co-creation, trae, issue-driven, human-ai-collaboration, trae-co-creation]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/co-creation-source.md
    title: "Trae 共创项目源码信源"
---

# 共创项目仓库定位与协作核心理念

## 仓库定位

trae-co-creation-projects 是 TRAE 社区的**协作 AI 编程项目展示平台**，MIT 许可证。与 trae-demos 展示"用 TRAE 构建的项目"不同，本仓库聚焦于**"用 TRAE 共创的项目"**——核心关键词是"协作"（co-creation）。

当前仓库处于初始化阶段：README 中仅展示投稿指引和分类说明，尚无已收录项目列表。

## "共创"的定义扩展

"共创"（co-creation）在本仓库中有前瞻性的定义拓展：

- **团队协作**：多人团队使用 TRAE 协作开发项目
- **结对编程**：两人结对，TRAE 作为辅助工具
- **AI 结对编程**：个人开发者使用 TRAE 编程，这本身就是"人与 AI 的协作共创"

这意味着**个人项目也可以投稿**，只要能展示 TRAE 如何在开发过程中充当协作伙伴（如 AI 代码审查、AI 辅助调试、AI 生成代码等）。这种定义将"人机协作"纳入共创范畴，是 AI 编程社区的一个前瞻性定位。

## Issue 表单驱动投稿

与 trae-demos 类似，本仓库采用 **Issue 表单驱动**而非 PR 驱动的投稿模式：

- 投稿者**不需要 Fork 仓库**
- 投稿者**不需要编写 Markdown 文件**
- 投稿者只需在 GitHub 网页上填写 Issue 模板表单
- 维护者审核通过后，由维护者负责添加展示内容

这种模式大幅降低了贡献门槛——非开发者社区成员也能轻松提交项目。

## 与 trae-demos 的定位差异

两个仓库的核心差异体现在审核权重设计上：

| 维度 | trae-demos | trae-co-creation-projects |
|------|-----------|--------------------------|
| 核心聚焦 | 项目展示（Demo） | 协作展示（Co-creation） |
| TRAE Usage | 40% | 40% |
| **Collaboration** | **0%（不评估）** | **30%（第二高权重）** |
| Code Quality | 25% | 20% |
| Completeness/Documentation | 35%（20%+15%） | 10% |
| 接受个人项目 | 可以 | 可以，但需展示 AI 协作 |
| 项目阶段 | polished 成品 | 从想法到生产都接受 |

Collaboration 占 30% 是"共创"与"演示"的本质区别。

## 投稿流程

```
检查要求 → 创建 Issue（选择 Project Submission 模板）→ 24h 确认 → 3-5 工作日审核 → 通过后展示
```

时间线与 trae-demos 一致：24 小时确认、3-5 工作日审核。

## 联系方式

社区成员可通过三种渠道联系：
1. GitHub Issues（投稿和问题反馈）
2. GitHub Discussions（讨论交流）
3. TRAE Discord（实时聊天）

## 相关链接

- [项目提交流程与 Issue 表单](01-project-submission.md)
- [审核标准与 Collaboration 权重](02-review-criteria.md)
- [提交共创项目示例](../examples/submit-project.md)
- [共创项目仓库资源索引](../references/co-creation-source.md)
