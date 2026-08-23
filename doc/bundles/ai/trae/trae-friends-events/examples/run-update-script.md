---
type: Example
title: 运行更新脚本示例
description: 执行 python scripts/update_readme.py 更新 README 时间轴的操作流程，包含脚本逻辑说明和常见问题排查。
tags: [trae-friends-events, events, example, python-script, readme-generation, cms]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/events-source.md
    title: "Trae Friends Events 源码信源"
---

# 运行更新脚本示例

本示例演示如何运行 `scripts/update_readme.py` 脚本来自动更新 README 时间轴。

## 前置条件

- 已安装 Python 3（脚本仅使用标准库，无需 pip install 任何包）
- 已编辑 `data/events.csv` 添加或修改了活动数据
- 当前工作目录为项目根目录

## 运行脚本

在项目根目录下执行：

```bash
python scripts/update_readme.py
```

脚本运行无输出即表示成功。如果有错误，会显示 Python 异常信息。

## 脚本执行流程

脚本依次执行以下操作：

1. **读取 CSV**：解析 `data/events.csv`，加载所有活动记录
2. **数据排序**：按日期降序排列所有活动
3. **按年分组**：将活动分为"当前年份"和"往年"两组
4. **生成 Markdown**：
   - 当前年份：直接展开显示
   - 往年：放入 `<details>` 折叠归档
   - 每月分组，最新月份默认 `<details open>` 展开
   - 每个活动生成表格行，包含日期（MM.DD）、类型 badge、城市
5. **替换 README**：
   - 查找 `<!-- TIMELINE_START -->` 和 `<!-- TIMELINE_END -->` 标记
   - 替换两个标记之间的内容为新生成的时间轴
   - 标记外的内容保持不变
6. **双语更新**：先更新 README.md（英文），再更新 README.zh-CN.md（中文）

## 脚本核心逻辑说明

### 颜色映射

脚本内置了 9 种活动类型到 shields.io badge 颜色的映射字典。未匹配的类型使用默认黄色。

### Badge 生成

每个活动类型生成一个 shields.io 图片 badge：

```html
<img src="https://img.shields.io/badge/Meetup-8C9EFF?style=flat-square">
```

### 时间轴折叠规则

- **年份级别**：当前年份（系统当前年份）直接展开；往年折叠在 `<details>` 中
- **月份级别**：当前年份中最新的月份默认展开（`open` 属性），其余月份折叠
- **表头语言**：英文版使用 Date/Event Type/City；中文版使用 举办日期/活动类型/城市

## 验证结果

脚本运行后，打开 README.md 检查：

1. 时间轴区域是否包含最新添加的活动
2. 活动是否在正确的年份/月份分组中
3. Badge 颜色是否与活动类型匹配
4. 折叠/展开状态是否符合预期
5. 中英文版本都已更新

同样检查 README.zh-CN.md 中文版。

## 常见问题

| 问题 | 原因 | 解决方法 |
|------|------|---------|
| `python: command not found` | Python 未安装或不在 PATH 中 | 安装 Python 3 或使用 `python3` 命令 |
| `FileNotFoundError: data/events.csv` | 不在项目根目录运行 | 切换到项目根目录后执行 |
| `UnicodeDecodeError` | CSV 文件编码不是 UTF-8 | 确保 CSV 文件以 UTF-8 编码保存 |
| README 中时间轴未更新 | 标记被意外删除或修改 | 检查 `<!-- TIMELINE_START -->` 和 `<!-- TIMELINE_END -->` 标记是否完整 |

## 注意事项

- 脚本会直接修改 README.md 和 README.zh-CN.md 文件，运行前确保已提交或备份不需要覆盖的更改
- 不要手动编辑 `<!-- TIMELINE_START -->` 和 `<!-- TIMELINE_END -->` 之间的内容——它们会在下次运行脚本时被覆盖
- 如果需要修改时间轴之外的内容（介绍文案、统计数据、链接等），直接编辑 README 中标记外的区域即可

## 相关链接

- [CSV+Python 轻量 CMS 模式](/concepts/01-csv-cms-pattern.md)
- [活动数据格式](/concepts/02-event-data-format.md)
- [添加新活动示例](/examples/add-event.md)
- [活动数据和脚本索引](/references/events-source.md)
