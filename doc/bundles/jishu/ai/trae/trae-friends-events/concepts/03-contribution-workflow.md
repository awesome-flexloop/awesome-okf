---
type: Concept
title: 贡献流程
description: 基于 OPERATION_GUIDE.md 运营指南的三步更新流程，配合 AI Prompt 辅助非技术贡献者参与，支持分层贡献模型。
tags: [trae-friends-events, trae, contribution, workflow, ai-assisted, community]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/events-source.md
    title: "Trae Friends Events 源码信源"
---

# 贡献流程

trae-friends-events 设计了面向非技术贡献者的运营流程，通过操作指南文档化和 AI Prompt 示例，大幅降低贡献门槛。

## 运营指南：OPERATION_GUIDE.md

`OPERATION_GUIDE.md` 是中文运营指南，将更新流程文档化为面向非技术人员的操作手册，包含以下内容：

### 三步更新流程

更新活动数据的标准流程：

1. **编辑 CSV**：在 `data/events.csv` 中添加新活动行（按格式填写 Date/Type/City_EN/City_ZH）
2. **运行脚本**：执行 `python scripts/update_readme.py`，脚本自动更新中英文 README 的时间轴区域
3. **提交推送**：Commit 并 Push 到仓库，提交 PR

### 目录结构说明

| 文件/目录 | 职责 |
|----------|------|
| `data/events.csv` | 数据源（唯一需要手动编辑的数据文件） |
| `scripts/update_readme.py` | 更新脚本（自动生成时间轴） |
| `README.md` | 英文主页（脚本自动更新时间轴部分） |
| `README.zh-CN.md` | 中文主页（脚本自动更新时间轴部分） |

## AI Prompt 辅助

OPERATION_GUIDE.md 提供了 3 个即用型 Trae AI Prompt 示例，让不熟悉技术的运营人员也能通过 AI 辅助完成内容更新：

### Prompt 1：修改介绍文案

直接告诉 AI 要修改的文件、原文和新文案，AI 会精准定位并替换。

### Prompt 2：更新统计数据

告诉 AI 更新统计数字（城市覆盖数、活动数、参与开发者数），AI 会找到对应位置修改。

### Prompt 3：替换链接

告诉 AI 需要替换的旧链接和新链接，AI 会全局替换。

### 三条最佳实践

1. **明确文件**：告诉 AI 要修改哪个文件
2. **提供原文和新文案**：给出要替换的原文和替换后的内容，避免 AI 猜测
3. **检查 Diff**：修改后仔细检查变更内容是否正确

## 数据更新的分层贡献模型

项目设计了贡献者分层：

| 贡献者类型 | 操作范围 | 所需技能 |
|-----------|---------|---------|
| **运营者/城市组织者** | 编辑 `data/events.csv` 添加活动 | 基本 CSV 格式知识（或通过 AI Prompt 辅助） |
| **开发者** | 修改 `scripts/update_readme.py` 脚本逻辑、调整 README 非自动生成区域 | Python、Markdown、Git |
| **内容贡献者** | 修改 README 介绍文案、统计数据、链接等（通过 AI Prompt 辅助） | 基本文字编辑（或通过 AI Prompt 辅助） |

## PR 流程

仓库通过 PR（Pull Request）提交内容更新，README 底部注明：

- 仓库由 TRAE Friends Community 维护管理
- 通过 PR 提交内容更新
- 贡献者指南链接指向 `.github/profile/CONTRIBUTING.md`

## 活动参与入口

除了代码/数据贡献外，社区还提供 4 种参与方式（均通过飞书表单降低门槛）：

| 参与方式 | 入口 | 适合人群 |
|---------|------|---------|
| Host Events | TRAE Fellow 申请表 | 想在自己城市主办活动的开发者 |
| Become a Speaker | TRAE Expert 话题提交表 | 想分享 AI 编程实践经验的讲师 |
| Become a Volunteer | 志愿者报名表 | 想参与活动组织的志愿者 |
| Join Community | 活动查找入口 | 想参加活动的开发者 |

未来活动通过飞书文档链接提供报名入口。

## 相关链接

- [Trae Friends 活动仓库简介](00-introduction.md)
- [CSV+Python 轻量 CMS 模式](01-csv-cms-pattern.md)
- [活动数据格式](02-event-data-format.md)
- [添加新活动示例](../examples/add-event.md)
- [运行更新脚本示例](../examples/run-update-script.md)
