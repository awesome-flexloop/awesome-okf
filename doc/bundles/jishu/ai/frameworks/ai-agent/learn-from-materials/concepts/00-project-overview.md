# 00 项目概览：learn-from-materials 是什么

> 对应事实：F-001~F-009
> 核验状态：✅ 仓库元数据经 GitHub API 逐项核实

## 一句话定位

**learn-from-materials** 是一个开源学习 Skill：把 PDF、EPUB、Word、PPT 等材料，**转换成可交互的学习网页**——不是简单摘要，而是保留来源可追溯、可自测、可做笔记的学习产物。

> 官方仓库一句话（API `description` 逐字）："Turn PDFs, books and papers into interactive learning webpages｜将复杂材料转化为可追溯、可测验、可做笔记的学习网页"

## 它解决什么问题

原文开门见山地描述痛点（F-001 上下文）：

- 读懂一份几十页的报告或长篇论文**需要花费大量时间**
- 遇到专业名词还得**到处查找解释**
- 读完想核对原文、想复习，**缺少结构化抓手**

learn-from-materials 的思路是把"读材料"变成"读一张为这份材料定制生成的学习网页"。

## 仓库画像

| 项 | 值 | 核验 |
|----|----|------|
| 仓库 | `dmoshehun-prog/learn-from-materials` | ✅ GitHub API（id 1361079582、public、非 fork） |
| 许可证 | MIT License | ✅ API `license.spdx_id = MIT` |
| 实现语言 | Python | ✅ API `language = Python` |
| 创建时间 | 2026-09-08T07:48:21Z | ✅ API `created_at` |
| 当前版本 | 1.1.0 | ✅ 官方 badge + 正文章节 |
| 时点热度 | star 1280 / fork 121（**核验时点快照，非稳定值**） | ✅ API 时点快照 |
| topics | `agent-skills`、`ai-agent`、`book`、`claude-code`、`codex`、`education`、`knowledge-base`、`learning`、`markdown`、`workbuddy` | ✅ API topics |

> ⚠️ star/fork 是核验时点（2026-11-04）的一次性快照，会随社区活跃快速变化，**不应作为结论性表述引用**。

## 关键技术立场：跨 Agent 的开放规范

本 Skill **基于开放 Agent Skills 规范构建**（F-013，README 首段），这意味着：

- 它的宿主不绑定单一 AI 客户端，而是任何识别 `SKILL.md` 的 Agent 环境
- Skill 目录结构、frontmatter 元数据、脚本调用方式都遵循同一套开放约定
- 与同族知识包 [claude-vision-skill](../../claude-vision-skill/index.md)、[book-to-skill](../../book-to-skill/index.md) 属同一 Agent Skill 谱系

## 与同族项目的关系

| 项目 | 关系 |
|------|------|
| [book-to-skill](../../book-to-skill/index.md) | 同为"材料→Skill/学习产物"的编译器思路，最直接的功能类比 |
| [claude-vision-skill](../../claude-vision-skill/index.md) | 同属 Agent Skill 工具教程先例；那一个给纯文本模型"装上眼睛"，本包给材料"装上学习界面" |
| [show-me-skill](../../show-me-skill/index.md) | 同组 Agent Skill 工具教程 |

## 相关知识包

- [book-to-skill](../../book-to-skill/index.md) — 书籍转 Skill 的编译器方法论
- [claude-vision-skill](../../claude-vision-skill/index.md) — Agent Skill 工具教程先例
