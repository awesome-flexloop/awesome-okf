---
type: Example
title: 添加新活动示例
description: 编辑 events.csv 添加活动行、运行 Python 更新脚本、验证结果和 AI 辅助操作的完整步骤示例。
tags: [trae-friends-events, events, example, csv, contribution, workflow]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/events-source.md
    title: "Trae Friends Events 源码信源"
---

# 添加新活动示例

本示例演示如何向 trae-friends-events 仓库添加一个新活动。

## 前置条件

- 已克隆项目仓库
- 已安装 Python 3（运行更新脚本需要）
- 了解新活动的日期、类型、城市信息

## 步骤 1：确定活动信息

准备新活动的四个字段信息：

| 字段 | 示例值 | 注意事项 |
|------|--------|---------|
| Date | `2026-03-15` | YYYY-MM-DD 格式 |
| Type | `Workshop` | 必须是 9 种支持类型之一（区分大小写） |
| City_EN | `Hangzhou` | 英文城市名，首字母大写 |
| City_ZH | `杭州` | 中文城市名 |

支持的活动类型：Meetup、Workshop、Demoday、Hackathon、Talk、Open Mic、Tea Talk、Family Day、Outdoor Exploration。

## 步骤 2：编辑 events.csv

打开 `data/events.csv`，在文件中添加一行新记录：

```csv
Date,Type,City_EN,City_ZH
2026-02-09,Meetup,Beijing,北京
2026-02-08,Workshop,Shanghai,上海
2026-03-15,Workshop,Hangzhou,杭州
```

> 💡 建议按日期降序排列（最新的活动在前面），但脚本运行时会自动排序，所以位置不影响最终结果。

### 格式检查

- Date 字段使用 `YYYY-MM-DD` 格式（不要用 YYYY/MM/DD 或 YYYY.MM.DD）
- Type 字段使用英文类型名（首字母大写），不要用中文
- City_EN 和 City_ZH 对应同一城市的英文名和中文名
- 字段之间用英文逗号 `,` 分隔，不要有多余空格

## 步骤 3：运行更新脚本

在项目根目录下执行：

```bash
python scripts/update_readme.py
```

脚本会：
1. 读取 `data/events.csv` 中的所有活动数据
2. 按年月分组排序
3. 生成带彩色 badge 的时间轴 Markdown
4. 自动更新 `README.md`（英文版）中 `<!-- TIMELINE_START -->` 和 `<!-- TIMELINE_END -->` 之间的区域
5. 自动更新 `README.zh-CN.md`（中文版）中对应区域
6. 标记外的内容（横幅、介绍、统计、参与方式等）保持不变

运行成功后没有报错即表示更新完成。

## 步骤 4：验证更新结果

打开 README.md 和 README.zh-CN.md，检查时间轴区域：

- 新活动是否出现在正确的年份和月份分组中
- 活动类型 badge 颜色是否正确
- 日期格式是否为 MM.DD
- 城市名显示为 "TRAE Friends@城市名"
- 当前年份最新月份是否默认展开

## 步骤 5：提交并创建 PR

```bash
git add data/events.csv README.md README.zh-CN.md
git commit -m "docs: add Hangzhou Workshop event on 2026-03-15"
git push origin your-branch
```

然后在 GitHub 上创建 Pull Request。

## 使用 AI 辅助操作

如果不熟悉 CSV 编辑或 Python 脚本，可以使用 OPERATION_GUIDE.md 中提供的 Trae AI Prompt 辅助操作。在 Trae 中打开项目后，直接用自然语言描述你的需求，例如：

> "帮我在 data/events.csv 中添加一个 2026 年 3 月 15 日在杭州的 Workshop 活动，然后运行更新脚本。"

AI 会帮你完成 CSV 编辑和脚本运行，你只需要检查 Diff 确认变更正确即可。

## 常见错误排查

| 问题 | 原因 | 解决方法 |
|------|------|---------|
| 脚本报错 FileNotFoundError | 不在项目根目录运行 | `cd` 到项目根目录后再执行 |
| badge 颜色不对 | Type 字段拼写错误 | 检查 Type 是否为 9 种类型之一，注意大小写 |
| 日期显示不正确 | Date 格式错误 | 确保使用 YYYY-MM-DD 格式 |
| 中文乱码 | CSV 文件编码问题 | 确保文件使用 UTF-8 编码保存 |

## 相关链接

- [活动数据格式](/concepts/02-event-data-format.md)
- [CSV+Python 轻量 CMS 模式](/concepts/01-csv-cms-pattern.md)
- [贡献流程](/concepts/03-contribution-workflow.md)
- [运行更新脚本示例](/examples/run-update-script.md)
