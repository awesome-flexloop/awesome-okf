---
type: Concept
title: CSV+Python 轻量 CMS 模式
description: 采用 CSV 数据源 + Python 转换层 + Markdown 展示层的三层 CMS 架构，通过标记替换机制自动生成双语 README 时间轴。
tags: [trae-friends-events, trae, csv-cms, architecture, python-script, markdown-generation]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/events-source.md
    title: "Trae Friends Events 源码信源"
---

# CSV+Python 轻量 CMS 模式

trae-friends-events 项目采用了一种极简的数据管理模式：**CSV 作为数据源 + Python 脚本作为转换层 + Markdown 作为展示层**，实现了零依赖的轻量 CMS（内容管理系统）。

## 三层架构

```
┌─────────────────────────────────────────────┐
│  展示层（Markdown）                           │
│  README.md / README.zh-CN.md                │
│  HTML 注释标记包裹自动生成区域                  │
├─────────────────────────────────────────────┤
│  转换层（Python 脚本）                        │
│  scripts/update_readme.py                   │
│  读取 CSV → 分组排序 → 生成 Markdown → 替换区域 │
├─────────────────────────────────────────────┤
│  数据层（CSV）                               │
│  data/events.csv                            │
│  SSOT（唯一事实来源），4 字段平面列表            │
└─────────────────────────────────────────────┘
```

## 数据层：CSV 作为唯一数据源

`data/events.csv` 是项目的唯一数据来源（SSOT, Single Source of Truth），所有展示内容都由此生成。

CSV 的优势：
- **零依赖**：任何文本编辑器都可编辑
- **易理解**：表格格式直观，非技术人员也能操作
- **易版本控制**：Git 可直接追踪逐行变更
- **易批量处理**：Python csv 模块原生支持

## 转换层：Python 标准库脚本

`scripts/update_readme.py` 仅使用 Python 标准库（csv、datetime、os），无第三方依赖，核心流程：

### 1. 颜色映射

脚本定义了 `COLORS` 字典，为 9 种活动类型分配 shields.io badge 颜色：

| 活动类型 | 颜色 |
|---------|------|
| Talk / Open Mic | F0FFD54F（黄色） |
| Workshop | FFB74D（橙色） |
| Meetup | 8C9EFF（靛蓝） |
| Demoday | 4DB6AC（青色） |
| Family Day | F06292（粉色） |
| Hackathon | 4DD0E1（浅蓝） |
| Tea Talk | 4CAF50（绿色） |
| Outdoor Exploration | 795548（棕色） |
| 未知类型 | FFD54F（默认黄色） |

### 2. Badge 生成

`get_badge()` 函数生成 shields.io badge 的 HTML：

```html
<img src="https://img.shields.io/badge/{event_type}-{color}?style=flat-square">
```

### 3. 日期格式化

`format_date()` 将 `YYYY-MM-DD` 转为 `MM.DD` 格式用于表格展示。

### 4. Markdown 生成

`generate_markdown()` 函数的核心逻辑：

1. 将事件按日期降序排列
2. 按年份分组
3. 当前年份直接展开显示
4. 往年放入 `<details>` 折叠归档（标题为 "📂 Click to expand {year} Events (Archive)"）

`generate_year_content()` 函数：

1. 将事件按月份分组、降序排列
2. 中英文表头切换（Date/Event Type/City 或 举办日期/活动类型/城市）
3. 当前年份第一个（最新）月份 `<details open>` 默认展开
4. 其余月份折叠显示

### 5. 标记替换

`update_readme()` 函数通过查找 HTML 注释标记来替换 README 中的自动生成区域：

```
<!-- TIMELINE_START -->
（自动生成的时间轴内容）
<!-- TIMELINE_END -->
```

脚本读取整个 README 文件，找到两个标记之间的内容，替换为新生成的 Markdown，然后写回文件。标记之外的内容（横幅、介绍、统计、参与方式等）保持不变。

### 6. 双语支持

脚本主入口依次调用：

```python
update_readme('README.md', 'en')      # 更新英文版
update_readme('README.zh-CN.md', 'zh') # 更新中文版
```

一次运行同时维护中英文两个 README。

## 展示层：Markdown 时间轴

生成的时间轴具有以下特性：

- **年份折叠**：往年归档在 `<details>` 中，减少页面长度
- **月份折叠**：除最新月份外，其余月份折叠显示
- **彩色 badge**：每种活动类型使用不同颜色，便于快速识别
- **三列表格**：Date（MM.DD）、Event Type（badge）、City（TRAE Friends@城市名）
- **响应式**：使用 Markdown 原生表格，GitHub 自动渲染

## 为什么不用框架

在"数据结构简单（平面列表）、展示格式固定（表格时间轴）、更新频率不高（活动后更新）"的场景下，CSV+脚本+Markdown 的组合比任何框架都更轻量：

- 无需数据库、无需构建工具、无需前端框架
- 运营者甚至不需要理解 HTML，只需按格式在 CSV 中追加一行
- Git 直接追踪数据变更，PR 审核清晰可见
- GitHub 原生渲染 Markdown，无需部署

## 适用场景

这种模式适用于：
- 数据结构为简单平面列表（无复杂关联）
- 展示格式相对固定
- 更新频率不高（非实时）
- 贡献者可能是非技术人员
- 希望零依赖、易维护

## 相关链接

- [Trae Friends 活动仓库简介](/concepts/00-introduction.md)
- [活动数据格式](/concepts/02-event-data-format.md)
- [贡献流程](/concepts/03-contribution-workflow.md)
- [运行更新脚本示例](/examples/run-update-script.md)
- [添加新活动示例](/examples/add-event.md)
