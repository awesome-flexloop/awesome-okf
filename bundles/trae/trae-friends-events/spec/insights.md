# TRAE Friends Events 核心洞察与知识地图

## 核心洞察（四元组）

### 洞察 1：CSV + Python 脚本 = 零依赖轻量 CMS 模式

**陈述**：项目无 package.json、无构建工具、无前端框架，采用纯 CSV 文件（`data/events.csv`，4 字段：Date/Type/City_EN/City_ZH）作为唯一数据源，通过 Python 标准库脚本（`scripts/update_readme.py`，仅依赖 csv/datetime/os）读取 CSV、按年月分组、生成带 shields.io badge 的 HTML 时间轴表格，并通过 `<!-- TIMELINE_START -->`/`<!-- TIMELINE_END -->` 注释标记自动替换中英文 README 中的对应区域。整个数据→展示的流水线零第三方依赖，运营者只需编辑 CSV 一行即可完成活动更新。

**证据**：F-001（无 package.json，纯 Markdown+CSV+Python）、F-014（HTML 注释标记包裹自动生成区域）、F-015~F-019（时间轴按年折叠/按月分组/当前月默认展开）、F-020~F-023（CSV 四字段结构，97 条记录，9 种活动类型）、F-024（仅用 Python 标准库）、F-025~F-031（脚本核心逻辑：颜色映射→badge 生成→日期格式化→Markdown 生成→标记替换）、F-032（同时更新中英文 README）

**反常识**：构建活动展示页面的常见方案是使用静态站点生成器（如 Jekyll/Hugo）、Headless CMS（如 Contentful）、或数据库+前端渲染，但本项目证明了在"数据结构简单（平面列表）、展示格式固定（表格时间轴）、更新频率不高（活动后更新）"的场景下，CSV+脚本+Markdown 的组合比任何框架都更轻量、更易维护、更易贡献——运营者甚至不需要理解 HTML，只需按格式在 CSV 中追加一行。

**行动**：理解"数据与展示分离"在零框架场景下的实现方式（CSV 为 SSOT，脚本为转换层，Markdown 为展示层）；学习 HTML 注释标记作为自动生成区域锚点的模式；掌握 Python 标准库 csv 模块的读写和分组聚合；复刻"按年月分组+折叠归档+当前月默认展开"的时间轴生成逻辑；理解 shields.io badge 的动态 URL 生成方式。

---

### 洞察 2：运营指南文档化 + AI Prompt 示例大幅降低非技术贡献门槛

**陈述**：项目提供 `OPERATION_GUIDE.md`（中文运营指南），将"编辑 CSV→运行脚本→提交 PR"的完整更新流程文档化，详细说明每个字段的含义和格式要求，甚至提供了 3 个即用型 Trae AI Prompt 示例（修改介绍文案/更新统计数据/替换链接），让不熟悉 Git/Python 的运营人员也能通过 AI 辅助完成内容更新。运营指南还列出了目录结构和各文件职责，形成"操作手册"而非"开发者文档"。

**证据**：F-033（三步更新流程：编辑 CSV→运行脚本→Commit Push）、F-034（CSV 四字段详细说明）、F-035（3 个 Trae Prompt 示例 + 3 条最佳实践：明确文件/提供原文/检查 Diff）、F-036（目录结构说明）、F-012（4 种参与方式均通过飞书表单降低门槛）、F-013（贡献者指南链接）

**反常识**：多数开源项目假设贡献者具备 Git/Markdown/命令行基础，运营指南常被忽略或写成"给开发者看的 README"。本项目反向思考：社区活动的运营者（城市组织者、志愿者）往往是营销/运营背景而非开发者，因此提供了面向非技术人员的操作手册，并直接给出 AI Prompt 示例来弥补技术能力差距——这在 AI 辅助编程时代是一种新颖的"文档即 Prompt 入口"模式。

**行动**：理解"面向非技术贡献者"的文档写作原则（步骤编号/字段说明/示例先行）；分析 AI Prompt 示例如何将"编辑 Markdown"这种模糊任务转化为可复制的指令；复刻"操作指南+AI Prompt"的双轨文档模式；思考如何为社区运营类项目设计贡献者分层（开发者改脚本/运营者改数据）。

## 知识地图

### 学习路径

```
阶段1：数据驱动架构
  ├─ csv-as-cms.md → CSV 作为轻量 CMS 的数据源模式
  ├─ scripted-readme-generation.md → Python 脚本生成 Markdown 的标记替换机制
  └─ timeline-generation-pattern.md → 按年月分组折叠的时间轴生成逻辑

阶段2：运营与社区
  ├─ operation-guide-pattern.md → 面向非技术贡献者的运营指南设计
  └─ ai-assisted-contribution.md → AI Prompt 示例降低贡献门槛的模式
```

### 概念-事实映射

| 概念文档 | 核心事实 | 关键文件 |
|---------|---------|---------|
| csv-as-cms.md | F-020~F-023 | `data/events.csv` |
| scripted-readme-generation.md | F-014, F-024~F-032 | `scripts/update_readme.py` |
| timeline-generation-pattern.md | F-015~F-019, F-029~F-030 | `scripts/update_readme.py`, `README.md` |
| operation-guide-pattern.md | F-033~F-036 | `OPERATION_GUIDE.md` |
| ai-assisted-contribution.md | F-035 | `OPERATION_GUIDE.md` |

### 示例/引用规划

| 示例文件 | 来源 | 说明 |
|---------|------|------|
| CSV 数据文件 | `data/events.csv` | 四字段活动数据格式规范 |
| README 更新脚本 | `scripts/update_readme.py` | 零依赖 Python 脚本生成双语时间轴 |
| 运营指南 | `OPERATION_GUIDE.md` | 面向非技术人员的操作手册 + AI Prompt 示例 |
