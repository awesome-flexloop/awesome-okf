# TRAE Friends Events 源码事实清单

## 项目基本信息

- F-001: 项目无 package.json，是一个纯 Markdown + CSV + Python 脚本的数据驱动仓库。来源：目录结构 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-friends-events\`
- F-002: 根目录包含 README.md（英文）、README.zh-CN.md（中文）、OPERATION_GUIDE.md（中文运营指南）、LICENSE 文件。来源：目录结构 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-friends-events\`
- F-003: 项目资源目录 `assets/images/` 包含 Friends.gif 和 trae-friends-logo.png 两个图片文件。来源：目录结构 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-friends-events\assets\images\`
- F-004: 项目品牌色为 `#00E599`（绿色），在 README 中用于 badge 和链接颜色。来源：README.md

## README 内容结构

- F-005: README.md 顶部展示 Friends.gif 横幅图片（width="100%"，圆角 10px），以及 GitHub TRAE Community badge。来源：README.md
- F-006: README.md 提供语言切换链接：English 指向 ./README.md，中文指向 ./README.zh-CN.md。来源：README.md
- F-007: README.md 描述 TRAE Friends 是由 TRAE Fellows 发起的城市社区活动，连接本地开发者和 AI 爱好者；线下组织 Meetups/Workshops/Demo Days/Hackathons/Family Days 等活动，线上每周邀请嘉宾分享 AI 编程实践经验。来源：README.md
- F-008: README.md 展示三项统计数据：70+ 城市覆盖、100+ 总活动数、10000+ 参与开发者，均使用 `#00E599` 颜色大字体显示。来源：README.md
- F-009: README.md 导航链接指向 Home（trae-community GitHub）、Discussions（trae-community/discussions）、Learning Resources（trae-learning 仓库）。来源：README.md
- F-010: README.md "Upcoming Events" 部分列出了 48 个城市名称（Anyang 到 Zunyi，含 Hong Kong 和 Taiwan），并通过飞书文档链接提供报名入口。来源：README.md
- F-011: README.md "Past Events" 部分列出了 4 篇微信公众号回顾文章链接：51 场年终回顾、30 城 11 月回顾、10 月回顾、9 月回顾。来源：README.md
- F-012: README.md "Get Involved" 部分包含 4 个参与方式：Host Events（TRAE Fellow 申请表）、Become a Speaker（TRAE Expert 话题提交表）、Become a Volunteer（志愿者报名表）、Join Community（查找活动），均为飞书表单/文档链接。来源：README.md
- F-013: README.md 底部注明仓库由 TRAE Friends Community 维护管理，通过 PR 提交内容更新，贡献者指南链接指向 `.github/profile/CONTRIBUTING.md`。来源：README.md

## 活动时间轴

- F-014: README.md 时间轴区域由 `<!-- TIMELINE_START -->` 和 `<!-- TIMELINE_END -->` HTML 注释标记包裹，是脚本自动生成区域。来源：README.md
- F-015: 时间轴按年份分组，当前年份（2026）直接展开显示，往年（2025）折叠在 `<details>` 标签内（标题为 "📂 Click to expand 2025 Events (Archive)"）。来源：README.md
- F-016: 时间轴内按月份使用 `<details>` 折叠，当前年份最新月份（February）设置 `open` 属性默认展开，其余月份折叠。来源：README.md
- F-017: 时间轴表格三列：Date（MM.DD 格式）、Event Type（带颜色 badge）、City（TRAE Friends@城市名）。来源：README.md
- F-018: 2026 年时间轴记录了 February（10 条活动）和 January（20 条活动）共 30 条活动数据。来源：README.md
- F-019: 2025 年归档时间轴记录了 September（5 条）、October（10 条）、November（31 条）、December（14 条）共 60 条活动数据。来源：README.md

## CSV 数据文件

- F-020: `data/events.csv` 表头为 `Date,Type,City_EN,City_ZH` 四个字段。来源：events.csv
- F-021: `events.csv` Date 字段格式为 `YYYY-MM-DD`，数据涵盖 2025-09-07 至 2026-02-09 的活动记录。来源：events.csv
- F-022: `events.csv` 中出现的活动类型（Type 字段）包括：Outdoor Exploration、Workshop、Demoday、Meetup、Hackathon、Tea Talk、Talk、Open Mic、Family Day，共 9 种类型。来源：events.csv
- F-023: `events.csv` 中 2025 年数据 60 条（09 月 5 条、10 月 10 条、11 月 30 条、12 月 15 条），2026 年数据 38 条（01 月 28 条、02 月 10 条），共 97 条记录（不含表头）。来源：events.csv

## Python 自动更新脚本

- F-024: `scripts/update_readme.py` 使用 Python 标准库（csv、datetime、os），无第三方依赖。来源：update_readme.py
- F-025: 脚本定义了 COLORS 字典，为 9 种活动类型分配 shields.io badge 颜色：Talk/Open Mic=F0FFD54F、Workshop=FFB74D、Meetup=8C9EFF、Demoday=4DB6AC、Family Day=F06292、Hackathon=4DD0E1、Tea Talk=4CAF50、Outdoor Exploration=795548，未知类型默认 FFD54F。来源：update_readme.py
- F-026: 脚本定义了英文月份名（MONTH_NAMES_EN：January-December）和中文月份名（MONTH_NAMES_ZH：1月-12月）。来源：update_readme.py
- F-027: `get_badge()` 函数生成 `<img src="https://img.shields.io/badge/{event_type}-{color}?style=flat-square">` 格式的 HTML badge。来源：update_readme.py
- F-028: `format_date()` 函数将 `YYYY-MM-DD` 格式转为 `MM.DD` 格式输出。来源：update_readme.py
- F-029: `generate_markdown()` 函数将事件列表按日期降序排列，按年份分组，当前年份直接展开，往年放入 `<details>` 折叠归档。来源：update_readme.py
- F-030: `generate_year_content()` 函数将事件按月份分组、降序排列，当前年份第一个（最新）月份 `<details open>` 默认展开，其余折叠；表格表头根据语言选择英文（Date/Event Type/City）或中文（举办日期/活动类型/城市）。来源：update_readme.py
- F-031: `update_readme()` 函数读取 `data/events.csv`，生成 Markdown 内容，然后通过查找 `<!-- TIMELINE_START -->` 和 `<!-- TIMELINE_END -->` 标记替换 README 文件中对应区域。来源：update_readme.py
- F-032: 脚本主入口依次调用 `update_readme('README.md', 'en')` 和 `update_readme('README.zh-CN.md', 'zh')`，同时更新中英文 README。来源：update_readme.py

## 运营维护指南

- F-033: OPERATION_GUIDE.md 描述了"数据驱动"的更新流程：编辑 `data/events.csv` 添加新行 → 运行 `python scripts/update_readme.py` → 脚本自动更新中英文 README 时间轴 → Commit 并 Push。来源：OPERATION_GUIDE.md
- F-034: OPERATION_GUIDE.md 详细说明了 CSV 四个字段的含义：Date（YYYY-MM-DD 格式）、Type（活动类型，自动匹配颜色标签）、City_EN（城市英文名）、City_ZH（城市中文名）。来源：OPERATION_GUIDE.md
- F-035: OPERATION_GUIDE.md 提供了使用 Trae 修改文档的三个 Prompt 示例：修改介绍文案、更新统计数据、替换链接，并给出三条最佳实践（明确文件、提供原文和新文案、检查 Diff）。来源：OPERATION_GUIDE.md
- F-036: OPERATION_GUIDE.md 列出了目录结构说明：data/events.csv 为数据源、scripts/update_readme.py 为更新脚本、README.md/README.zh-CN.md 为双语主页。来源：OPERATION_GUIDE.md
