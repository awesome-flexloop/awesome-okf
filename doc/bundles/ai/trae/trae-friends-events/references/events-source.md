---
type: Reference
title: 活动数据和脚本索引
description: trae-friends-events 仓库的信源登记簿，包含 events.csv 数据格式定义、9 种活动类型枚举、update_readme.py 脚本函数索引和时间轴生成规则。
tags: [trae-friends-events, events, csv-cms, python-script, source-index, reference]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/events-source.md
    title: "Trae Friends Events 源码信源"
---

# 活动数据和脚本索引

本文档索引 trae-friends-events 项目的活动数据文件和自动更新脚本。

## 项目基本信息

| 属性 | 值 |
|------|---|
| 项目类型 | 纯 Markdown + CSV + Python 脚本（无 package.json、无构建工具） |
| License | 未明确标注（根目录含 LICENSE 文件） |
| 品牌色 | `#00E599`（绿色） |
| 定位 | TRAE Friends 社区活动数据管理与时间轴展示 |

## 目录结构

```
trae-friends-events/
├── README.md              # 英文主页（含自动生成时间轴）
├── README.zh-CN.md        # 中文主页（含自动生成时间轴）
├── OPERATION_GUIDE.md     # 中文运营指南（面向非技术贡献者）
├── LICENSE
├── assets/images/
│   ├── Friends.gif        # 横幅动图
│   └── trae-friends-logo.png # Logo
├── data/
│   └── events.csv         # 活动数据源（唯一 SSOT）
├── scripts/
│   └── update_readme.py   # Python 自动更新脚本（零第三方依赖）
└── .github/profile/
    └── CONTRIBUTING.md    # 贡献者指南
```

## 数据源：data/events.csv

- **表头**：`Date,Type,City_EN,City_ZH`
- **Date 格式**：`YYYY-MM-DD`
- **数据范围**：2025-09-07 至 2026-02-09
- **记录数**：97 条（2025 年 60 条 + 2026 年 38 条）
- **活动类型**：9 种（Outdoor Exploration、Workshop、Demoday、Meetup、Hackathon、Tea Talk、Talk、Open Mic、Family Day）

## 脚本：scripts/update_readme.py

- **Python 依赖**：仅标准库（csv、datetime、os），无第三方依赖
- **核心函数**：
  - `get_badge()`：生成 shields.io badge HTML
  - `format_date()`：将 YYYY-MM-DD 转为 MM.DD
  - `generate_markdown()`：按年分组、降序排列、当前年展开/往年折叠
  - `generate_year_content()`：按月分组、最新月份默认展开、表格生成
  - `update_readme()`：读取 CSV、生成内容、通过注释标记替换 README 区域
- **标记锚点**：`<!-- TIMELINE_START -->` 和 `<!-- TIMELINE_END -->`
- **执行结果**：同时更新 README.md（英文）和 README.zh-CN.md（中文）

## 时间轴展示规则

- 当前年份直接展开显示，往年放入 `<details>` 折叠归档
- 当前年份最新月份设置 `open` 属性默认展开，其余月份折叠
- 表格三列：Date（MM.DD 格式）、Event Type（带颜色 badge）、City（TRAE Friends@城市名）
- 9 种活动类型各分配不同的 shields.io badge 颜色

## 统计数据（README 展示）

- 70+ 城市覆盖
- 100+ 总活动数
- 10000+ 参与开发者

## 相关链接

- [Trae Friends 活动仓库简介](../concepts/00-introduction.md)
- [CSV+Python 轻量 CMS 模式](../concepts/01-csv-cms-pattern.md)
- [活动数据格式](../concepts/02-event-data-format.md)
- [贡献流程](../concepts/03-contribution-workflow.md)
- [添加新活动示例](../examples/add-event.md)
- [运行更新脚本示例](../examples/run-update-script.md)
