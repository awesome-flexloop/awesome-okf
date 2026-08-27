---
type: Concept
title: 项目提交流程与 Issue 表单字段
description: trae-co-creation-projects 的 Issue 驱动提交流程、中英双语 Markdown Issue 模板和 4 类必填信息字段
tags: [co-creation, submission, issue-form, bilingual, trae-co-creation, trae]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/co-creation-source.md
    title: "Trae 共创项目源码信源"
---

# 项目提交流程与 Issue 表单字段

## Issue 驱动投稿模式

trae-co-creation-projects 采用 **GitHub Issue 作为唯一投稿入口**，与传统的 Fork → 编写文件 → PR 流程不同：

| 传统 PR 流程 | Issue 表单流程 |
|-------------|---------------|
| 需要 Fork 仓库 | 不需要 Fork |
| 需要克隆到本地 | 不需要克隆 |
| 需要编写 Markdown 文件 | 只需在网页填表 |
| 需要 Git 操作知识 | 会用 GitHub 即可 |
| 贡献者负责格式 | 维护者负责格式 |

这种"投稿者填表单/维护者整合展示"的分工模式，大幅降低了贡献摩擦。

## 中英双语 Issue 模板

`.github/ISSUE_TEMPLATE/` 目录提供两个 Markdown 格式的 Issue 模板：

| 模板文件 | 语言 |
|---------|------|
| `project-submission.md` | 英文 |
| `project-submission-zh.md` | 中文 |

投稿者选择自己熟悉的语言填写即可。

## 投稿 4 步流程

1. **检查 Must Have 标准**：确认项目满足 4 项准入要求
2. **创建 Issue**：点击 "New Issue"，选择 "Project Submission"（中文为"项目投稿"）模板
3. **填写表单**：按模板字段填写项目信息
4. **等待审核**：24 小时内确认，3-5 工作日完成审核

## 4 类必填信息字段

Issue 模板要求投稿者填写 4 类结构化信息：

### 1. Project Information（项目基本信息）

| 字段 | 说明 |
|------|------|
| Project Name | 项目名称 |
| Repository Link | GitHub 仓库链接 |
| Demo Link | 在线演示链接（如有） |
| Project Type | 项目分类（6 选 1） |

### 2. Description（项目描述）

| 字段 | 说明 |
|------|------|
| One-line Description | 一句话描述项目是什么 |
| Detailed Description | 详细描述项目功能、特色和背景 |

### 3. Collaboration Details（协作细节）—— 核心字段

这是共创项目最关键的信息类别，也是与 trae-demos 投稿的核心区别：

| 字段 | 说明 |
|------|------|
| Team Size | 团队规模（个人/2-3人/更多） |
| Collaboration Type | 协作类型（团队协作/结对编程/AI 结对编程等） |
| How TRAE Was Used | 详细描述 TRAE 在协作中扮演的角色和使用场景 |

> 💡 "How TRAE Was Used" 是审核的重点关注字段，直接影响 Collaboration 维度的 30% 评分。个人项目需要在这里清楚说明 TRAE 如何作为"AI 协作伙伴"参与开发。

### 4. Technical Details（技术细节）

| 字段 | 说明 |
|------|------|
| Tech Stack | 使用的技术栈 |
| Key Features | 核心功能列表 |
| Screenshots | 项目截图 |

## 个人项目投稿指南

个人开发者投稿时，Collaboration Details 的填写要点：

1. **Team Size**：选择 "Solo with AI" 或 "Individual"
2. **Collaboration Type**：描述为 "AI Pair Programming"（AI 结对编程）
3. **How TRAE Was Used**：具体说明 TRAE 如何充当协作伙伴，例如：
   - TRAE 辅助了哪些具体任务（代码生成/调试/重构/文档）
   - TRAE 在开发流程中扮演的角色（结对编程伙伴/代码审查者/技术顾问）
   - 使用 TRAE 前后的效率对比或体验差异
   - 具体的协作场景示例

## 接受的项目阶段

与 trae-demos 要求 polished 成品不同，共创项目接受**任何阶段**的项目：

- 💡 想法阶段（Idea）：有创意和 TRAE 协作计划
- 🔧 开发中（In Progress）：正在使用 TRAE 协作开发
- ✅ 已完成（Complete）：项目已发布可用
- 🚀 生产中（Production）：已在生产环境使用

这意味着你可以在项目早期就提交分享 TRAE 协作经验，不必等到项目完全完成。

## 相关链接

- [共创项目仓库定位与协作核心理念](00-introduction.md)
- [审核标准与 Collaboration 权重](02-review-criteria.md)
- [提交共创项目示例](../examples/submit-project.md)
- [共创项目仓库资源索引](../references/co-creation-source.md)
