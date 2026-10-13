---
okf_version: "0.2"
type: Concept
title: "视图、文档、统计与需求入口"
description: "五种布局视图（同数据多版式）、Pages 与 Wiki 双层文档、跨项目统计面板、Intake 外部需求待审队列、官方集成与 AI 能力"
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/KCjLFr72qwngPyyI1b2ENg
  - id: official-integrations
    resource: https://docs.plane.so/integrations
---

# 03 · 视图、文档、统计与需求入口

## 1. 五种布局：同一批任务，五种版式

博文口径为「看板、列表、日历、甘特图、表格」，官方命名与用途如下（F-022 / V13）：

| 博文口径 | 官方命名 | 最适合 |
|---------|---------|--------|
| 列表 | **List** | 按属性分组、看父子层级、批量改属性 |
| 看板 | **Board / Kanban** | 拖拽改状态、站会与流程可视化 |
| 日历 | **Calendar** | 看截止日期与排期冲突 |
| 甘特图 | **Timeline / Gantt** | 依赖与里程碑、发现工作重叠 |
| 表格 | **Spreadsheet / Table** | 类 Excel 批量编辑与数据分析 |

关键性质：**五种版式底下是同一份数据**（F-022），切换布局不产生数据副本。官方明确「五个布局在**所有方案档位（含免费档）**全部提供」（F-024 / V14）。

视图（View）= 布局 + 筛选条件 + 显示选项的组合，**可保存并分享给团队其他人**（F-023）。常见用法：按角色建视图（「我的本周活跃工作」「按标签+截止日」），避免每次重配筛选。

## 2. 文档：Pages（项目级）+ Wiki（工作区级）

| 层 | 对象 | 范围 | 出处 |
|----|------|------|------|
| 项目级 | **Pages** | 单个项目内的文档 | F-031 / V16 |
| 工作区级 | **Wiki** | 跨项目的知识库 | F-031 / V16 |

能力（F-030、F-031）：

- 富文本编辑器，可嵌入**图片、视频、Figma 设计稿**
- 写完的文档可**一键转成任务**
- 官方补充：可嵌入 Draw.io 图表；Marketplace 提供 Confluence / Notion 导入器

> 博文判断：以前 Jira + Confluence 两头开的团队可以省掉一个工具（F-031 语境）。这是**作者观点**，实际能否替代取决于团队对 Confluence 宏、权限模型、空间结构的依赖深度。

## 3. 统计：跨项目实时面板

一块跨项目的实时面板（F-032）：

- 任务按**负责人 / 状态 / 优先级**摊开
- 带**趋势图**
- 官方另有 Cycles 与 Modules 各自的进度分析（燃尽图、速度）

博文用法建议：开站会前扫一眼，哪块落后心里有数（F-032 语境）。

## 4. Intake：外部需求先落待审队列

机制（F-025）：

1. 客户或其他部门同事**无需注册账号**
2. 通过**一张表单**提交需求或 bug
3. 提交内容先落进**待审队列**
4. 内部评审通过后**才转成正式任务**

价值在于**入口收在一处**，任务列表不会被外部提交塞乱（F-025）。

> ⚠️ **核验状态**：该机制获第三方综述旁证支持，但本轮**未核到官方一手文档页**（V26）。用作选型依据前建议实测确认。

## 5. 集成与 AI

官方原生集成（docs.plane.so《Native Integrations》，F-026 / V15）：

| 集成 | 作用 |
|------|------|
| **GitHub** / GitHub Enterprise | Issue、PR、commit 双向同步；代码合并可带动任务状态变化（F-027） |
| **GitLab** / GitLab Enterprise | MR 与 Issue 同步 |
| **Slack** | 在 Slack 内创建工作项、同步讨论（F-028） |
| **Sentry** | 报错自动建工作项、状态同步 |
| **Draw.io** | 在 Pages 内嵌图表 |

> 官方集成面**大于**博文所列四项（另含 GitHub Enterprise、Draw.io、VS Code MCP、Claude/Cursor Agent、Jira/Asana/Linear/Notion/ClickUp 导入器等）。

AI 能力（F-029）：可问项目进度、整理任务描述；**自部署实例挂自己的模型 Key，请求不出自己那台机器**。官方配置文档补充：Plane AI 支持通过 `.env` 配置 OpenAI / Anthropic / AWS Bedrock / OpenAI 兼容端点（如 Ollama），提示词、响应与用量日志留在本机边界内。

## 6. 已知边界

- Intake 为「博文 + 旁证」（V26）
- AI 的「问进度」能力口径博文未展开，本包不作能力断言
- 集成清单为 2026-10 快照，Marketplace 持续扩充

下一篇 → [04 部署架构与运维要点](04-deployment-and-operations.md)
