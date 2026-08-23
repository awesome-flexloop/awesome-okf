---
type: Concept
title: 活动数据格式
description: events.csv 定义 Date/Type/City_EN/City_ZH 四字段，包含 9 种活动类型枚举与对应的颜色映射规则。
tags: [trae-friends-events, trae, events, data-format, csv, event-types]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/events-source.md
    title: "Trae Friends Events 源码信源"
---

# 活动数据格式

本文档详细说明 `data/events.csv` 的字段定义、格式要求和活动类型枚举。

## CSV 文件结构

`data/events.csv` 是项目的唯一数据源（SSOT），使用 UTF-8 编码，逗号分隔。

### 表头

```csv
Date,Type,City_EN,City_ZH
```

共 4 个字段：

| 字段 | 必填 | 格式 | 说明 | 示例 |
|------|------|------|------|------|
| `Date` | 是 | `YYYY-MM-DD` | 活动日期 | `2026-02-09` |
| `Type` | 是 | 字符串（枚举值） | 活动类型，自动匹配 badge 颜色 | `Meetup` |
| `City_EN` | 是 | 字符串 | 城市英文名 | `Beijing` |
| `City_ZH` | 是 | 字符串 | 城市中文名 | `北京` |

### 字段详细说明

#### Date（日期）

- **格式**：`YYYY-MM-DD`（ISO 8601 日期格式）
- **规则**：
  - 年份 4 位，月份 2 位（01-12），日期 2 位（01-31）
  - 使用短横线 `-` 分隔，不要使用斜杠 `/` 或点 `.`
- **示例**：
  - `2025-09-07`（2025 年 9 月 7 日）
  - `2026-02-09`（2026 年 2 月 9 日）

#### Type（活动类型）

当前支持 9 种活动类型：

| 类型 | 中文 | badge 颜色 | 说明 |
|------|------|-----------|------|
| `Meetup` | 见面会 | 靛蓝（8C9EFF） | 常规线下聚会交流 |
| `Workshop` | 工作坊 | 橙色（FFB74D） | 动手实践的教学活动 |
| `Demoday` | 演示日 | 青色（4DB6AC） | 项目展示和 Demo 活动 |
| `Hackathon` | 黑客松 | 浅蓝（4DD0E1） | 编程马拉松 |
| `Talk` | 分享会 | 黄色（F0FFD54F） | 主题演讲分享 |
| `Open Mic` | 开放麦 | 黄色（F0FFD54F） | 自由分享/闪电演讲 |
| `Tea Talk` | 茶话会 | 绿色（4CAF50） | 轻松交流活动 |
| `Family Day` | 家庭日 | 粉色（F06292） | 社区家庭日活动 |
| `Outdoor Exploration` | 户外探索 | 棕色（795548） | 户外活动 |

> ⚠️ Type 字段必须使用上述英文字符串（区分大小写），否则会使用默认黄色 badge 且无法正确分类。

#### City_EN（城市英文名）

- 使用英文城市名，如 `Beijing`、`Shanghai`、`Shenzhen`、`Hong Kong`
- 包含 `TRAE Friends@` 前缀在 README 中显示，CSV 中只需填写城市名
- 城市名首字母大写，多个单词使用空格分隔

#### City_ZH（城市中文名）

- 使用中文城市名，如 `北京`、`上海`、`深圳`、`香港`
- 与 City_EN 对应，用于中文版 README 显示

## 数据示例

以下是 events.csv 中的数据行示例：

```csv
2026-02-09,Meetup,Beijing,北京
2026-02-08,Workshop,Shanghai,上海
2026-01-25,Hackathon,Shenzhen,深圳
2025-12-20,Demoday,Hangzhou,杭州
2025-11-15,Tea Talk,Chengdu,成都
2025-10-10,Talk,Guangzhou,广州
2025-09-07,Outdoor Exploration,Hong Kong,香港
```

## 数据排序约定

新活动添加到 CSV 文件中时，建议按日期降序排列（最新的在前面），虽然脚本会自动排序，但保持文件有序便于人工查阅。

## 数据统计

当前数据覆盖情况：

- **时间跨度**：2025-09-07 至 2026-02-09
- **2025 年数据**：60 条（09 月 5 条、10 月 10 条、11 月 30 条、12 月 15 条）
- **2026 年数据**：38 条（01 月 28 条、02 月 10 条）
- **总记录数**：97 条（不含表头）

## 相关链接

- [CSV+Python 轻量 CMS 模式](/concepts/01-csv-cms-pattern.md)
- [贡献流程](/concepts/03-contribution-workflow.md)
- [添加新活动示例](/examples/add-event.md)
- [运行更新脚本示例](/examples/run-update-script.md)
