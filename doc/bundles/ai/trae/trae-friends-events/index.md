---
type: Index
title: TRAE Friends 社区活动
description: trae-friends-events 是 TRAE Friends 社区活动的知识包，采用 CSV CMS 模式管理活动数据，包含活动数据格式规范和贡献工作流。
tags: [trae-friends-events, trae, events, community, friends, csv-cms]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/events-source.md
    title: "Trae Friends Events 源码信源"
---

# trae-friends-events 文档

trae-friends-events 是 TRAE Friends 社区活动数据管理仓库，采用纯 Markdown + CSV + Python 脚本的零依赖架构，通过 CSV 作为唯一数据源、Python 标准库脚本自动生成双语 README 时间轴，实现轻量 CMS 模式。项目面向非技术贡献者设计，提供操作指南和 AI Prompt 示例。

## 核心概念

| 文档 | 说明 |
|------|------|
| [Trae Friends 活动仓库简介](/concepts/00-introduction.md) | 社区活动定位、零依赖架构、自动生成时间轴、品牌视觉 |
| [CSV+Python 轻量 CMS 模式](/concepts/01-csv-cms-pattern.md) | CSV 数据源 + Python 转换层 + Markdown 展示层的三层架构、标记替换机制、时间轴生成逻辑 |
| [活动数据格式](/concepts/02-event-data-format.md) | events.csv 四字段定义（Date/Type/City_EN/City_ZH）、9 种活动类型枚举与颜色映射 |
| [贡献流程](/concepts/03-contribution-workflow.md) | OPERATION_GUIDE.md 运营指南、三步更新流程、AI Prompt 辅助、PR 流程、分层贡献模型 |

## 示例

| 文档 | 说明 |
|------|------|
| [添加新活动示例](/examples/add-event.md) | 编辑 CSV 添加活动行、运行脚本、验证结果、AI 辅助操作的完整步骤 |
| [运行更新脚本示例](/examples/run-update-script.md) | python scripts/update_readme.py 执行流程、脚本逻辑、常见问题排查 |

## 参考

| 文档 | 说明 |
|------|------|
| [活动数据和脚本索引](/references/events-source.md) | 目录结构、events.csv 数据概况、update_readme.py 函数索引、时间轴展示规则 |

```{toctree}
:hidden:

concepts/00-introduction
concepts/01-csv-cms-pattern
concepts/02-event-data-format
concepts/03-contribution-workflow
examples/add-event
examples/run-update-script
references/events-source
spec/facts
spec/insights
```
