---
type: Concept
title: Trae Friends 活动仓库简介
description: trae-friends-events 是 TRAE Friends 社区活动数据管理仓库，采用纯 Markdown + CSV + Python 脚本的零依赖架构实现轻量 CMS 模式。
tags: [trae-friends-events, trae, events, introduction, community, zero-dependency]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/events-source.md
    title: "Trae Friends Events 源码信源"
---

# Trae Friends 活动仓库简介

## 什么是 TRAE Friends

TRAE Friends 是由 TRAE Fellows 发起的城市社区活动，连接本地开发者和 AI 爱好者。社区活动形式包括：

- **线下活动**：Meetups、Workshops、Demo Days、Hackathons、Family Days
- **线上活动**：每周邀请嘉宾分享 AI 编程实践经验

## 项目定位

trae-friends-events 是一个**数据驱动的社区活动数据管理仓库**，采用零依赖架构——无 package.json、无构建工具、无前端框架，仅通过 CSV 文件 + Python 标准库脚本 + Markdown 文件实现活动数据的管理和时间轴展示。

仓库同时提供中英文双语支持（README.md / README.zh-CN.md）。

## 核心数据

- **70+** 城市覆盖
- **100+** 总活动数
- **10000+** 参与开发者

## 项目特色

### 零依赖轻量架构

整个数据→展示的流水线零第三方依赖：

- **数据源**：`data/events.csv`（4 字段 CSV 文件）
- **转换层**：`scripts/update_readme.py`（仅用 Python 标准库 csv/datetime/os）
- **展示层**：README.md / README.zh-CN.md（Markdown 文件，含 HTML 注释标记区域）

运营者只需在 CSV 中追加一行，运行脚本即可完成活动更新。

### 自动生成时间轴

README 中的活动时间轴由脚本自动生成，具有以下特性：

- 按年份分组：当前年份直接展开，往年折叠归档
- 按月份分组：当前年份最新月份默认展开，其余月份折叠
- 活动类型使用 shields.io 彩色 badge 区分
- 中英文双语时间轴同时更新

### 面向非技术贡献者

项目提供 `OPERATION_GUIDE.md`（中文运营指南），将更新流程文档化，并提供 3 个即用型 Trae AI Prompt 示例，让不熟悉 Git/Python 的运营人员也能通过 AI 辅助完成内容更新。

## 参与方式

README 中列出 4 种参与方式（均通过飞书表单/文档降低门槛）：

1. **Host Events**：成为 TRAE Fellow 主办活动（申请表）
2. **Become a Speaker**：成为 TRAE Expert 提交话题（话题提交表）
3. **Become a Volunteer**：成为志愿者（报名表）
4. **Join Community**：查找并参加活动

## 品牌视觉

- 品牌色：`#00E599`（绿色），用于 badge 和链接颜色
- 横幅：`assets/images/Friends.gif`（圆角 10px）
- Logo：`assets/images/trae-friends-logo.png`

## 相关链接

- [CSV+Python 轻量 CMS 模式](01-csv-cms-pattern.md)
- [活动数据格式](02-event-data-format.md)
- [贡献流程](03-contribution-workflow.md)
- [添加新活动示例](../examples/add-event.md)
- [活动数据和脚本索引](../references/events-source.md)
