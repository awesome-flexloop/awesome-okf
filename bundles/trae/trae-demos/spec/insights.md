# TRAE Demos 核心洞察与知识地图

## 核心洞察（四元组）

### 洞察 1：期数制（Period-based）Demo 展示的 Markdown 驱动模式

**陈述**：项目采用"期"（period）作为内容组织单位，Demo 文件按 `demos/period-N/demo-N.md` 和 `demo-N.zh-CN.md` 双语存放，每个 Demo Markdown 文件头部标注 Issue 编号和发布时间，形成类似"杂志期刊"的定期发布节奏。Demo 文件本身是结构化的展示页，包含元数据（作者/类型/技术栈）、仓库链接、在线演示、核心亮点、本地运行方式、预览图片，README 中的"Past Issues"表格按Issue 编号汇总每期内容。

**证据**：F-011（demos/period-N/ 目录组织）、F-012（demo-N.md + demo-N.zh-CN.md 双语命名）、F-013~F-014（README Past Issues/往期内容表格，按 Issue/期数汇总）、F-015~F-020（Demo #1 完整字段：作者/类型/技术栈/仓库/演示/亮点/运行/截图）、F-021~F-026（Demo #2 类似结构）

**反常识**：Demo 展示平台通常采用"分类列表"或"标签筛选"的组织方式（如 awesome-list 的分类），但本项目采用"期数制"——按时间批次发布，类似技术期刊/周刊。这种模式天然制造了"发布事件"（每期发布即是一次社区推广），也让内容消费有了"追更"感，缺点是跨期查找需要额外索引。

**行动**：理解期数制内容组织的节奏优势（定期发布制造仪式感）；分析 Demo Markdown 文件的字段设计（元数据/链接/亮点/运行/截图）；复刻"主 README 汇总表格 + 每期独立 Markdown 文件"的双层结构。

---

### 洞察 2：多场景 Issue 模板驱动的投稿-报告-更新闭环

**陈述**：项目配置了 7 个 YAML Issue 模板文件，覆盖 5 种场景：submit_demo（中英双语投稿）、report_demo（中英双语问题反馈）、update_demo（Demo 信息更新）、want_demo（Demo 需求征集），并通过 config.yml 禁用空 Issue（`blank_issues_enabled: false`）和提供 Discussions 联系链接，将所有社区互动引导至结构化表单，确保每个 Demo 提交都包含审核所需的完整信息。

**证据**：F-006（投稿流程：检查→Issue 提交→确认→审核→展示）、F-009（禁用空 Issue + Discussions 引导）、F-010（7 个 YAML 模板文件覆盖 5 种场景）、F-007~F-008（5 个项目分类 + 4 维权重评分：TRAE Usage 40% 最高权重）

**反常识**：多数展示类项目只用一个"submit"模板处理投稿，但本项目区分了"投稿/报告问题/更新信息/需求征集"四种社区行为，特别是"want_demo"模板让社区可以投票/提出想看的 Demo 类型，形成需求侧驱动，而非仅维护者侧驱动。

**行动**：分析 TRAE Usage 40% 最高权重如何确保平台聚焦"用 TRAE 构建"而非泛项目展示；理解禁用空 Issue 如何减少低质量互动；复刻多场景 Issue 模板的设计思路。

## 知识地图

### 学习路径

```
阶段1：期数制内容组织
  ├─ period-based-demo-organization.md → 期数制 Demo 展示的目录与命名规范
  └─ demo-markdown-schema.md → Demo Markdown 文件的结构化字段设计

阶段2：社区投稿机制
  └─ multi-scenario-issue-templates.md → 多场景 Issue 模板驱动的投稿闭环
```

### 概念-事实映射

| 概念文档 | 核心事实 | 关键文件 |
|---------|---------|---------|
| period-based-demo-organization.md | F-011~F-014 | `demos/` 目录, `README.md` |
| demo-markdown-schema.md | F-015~F-026 | `demos/period-1/demo-1.md`, `demo-2.md` |
| multi-scenario-issue-templates.md | F-005~F-010 | `.github/ISSUE_TEMPLATE/`, `CONTRIBUTING.md` |

### 示例/引用规划

| 示例文件 | 来源 | 说明 |
|---------|------|------|
| Demo #1 展示页 | `demos/period-1/demo-1.md` | 完整 Demo 结构化字段示例 |
| 多场景 Issue 模板 | `.github/ISSUE_TEMPLATE/` | 投稿/报告/更新/需求四类模板 |
