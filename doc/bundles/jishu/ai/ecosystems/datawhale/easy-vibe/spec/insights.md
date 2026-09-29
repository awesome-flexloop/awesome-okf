---
type: spec
title: "Easy-Vibe 架构洞察（I阶段）"
---

# Easy-Vibe 架构洞察（I阶段）

> 基于 spec/facts.md 的 F-xxx 事实，提炼 3 个核心洞察。
> 每个洞察采用四元组：陈述 / 证据 / 反常识 / 行动。

---

## 洞察一：Vibe Coding 教育范式——"先做产品，再学技术"的路径反转

**陈述**
Easy-Vibe 把"用自然语言描述需求→AI 生成→迭代"作为编程入门的第一动作，学习路径按"产品原型→全栈交付→跨平台进阶"组织，而非传统的"语法→数据结构→算法→工程"。课程把产品思维（找创意、用户访谈、双钻模型、The Mom Test）放在编码之前，把"做出能给用户看的 Demo"作为第一阶段产出。

**证据**
- F-003：README 原文 "In the AI era, programming starts by describing what you want"；llms.txt 定义核心理念为"Vibe Coding（用自然语言编程）"。
- F-004：Stage 1 含 `finding-great-idea/`、`building-prototype/`、`integrating-ai-capabilities/`、`complete-project-practice/`，以及产品思维附录（双钻、JTBD、Mom Test）。
- F-004：附录把"计算机基础"作为参考知识库而非前置课程，学习者遇到阻塞才查阅。
- F-018：2026-08-12 改版明确"从真实问题出发，经过找机会、选方向、理解用户需求、访谈、收敛方案、做原型、集成 AI、完成可展示项目"。

**反常识**
传统编程教育把"语法基础"视为不可跳过的前置门槛，Easy-Vibe 反其道而行：零基础学习者在 Stage 1 不被要求理解 JavaScript 闭包或 HTTP 协议，而是先用 AI IDE 做出贪吃蛇和产品原型。计算机基础、网络、数据结构被下沉到附录，作为"按需查阅"的知识库。这押注的判断是：AI 时代"描述需求与验证想法"的能力比"手写语法"的能力更稀缺。

**行动**
- 概念文档应清晰呈现 3+1 阶段的能力递进逻辑与每阶段产出物，避免读者把它误当成普通的"前端教程合集"。
- 在概念中区分"Vibe Coding 工作流"与"传统编程工作流"的差异点（提示词驱动、对话式迭代、AI 作为实现者、人作为决策者）。
- 引用附录作为"背景知识补给站"而非"必修课"，传达按需学习的设计意图。

---

## 洞察二：10 语言站点的真正复杂度在构建系统，不在翻译

**陈述**
Easy-Vibe 的多语言不是简单复制目录，而是一套工程化系统：locale 感知的 base 路径自适应、按 locale 隔离的侧边栏工厂函数、SEO hreflang/OG 元数据生成、顺序构建+文件锁规避 VitePress alpha 的并发缺陷、附录 Vue 组件的 i18n 文案缺失扫描，以及基于 XeLaTeX/Puppeteer 的多语言 PDF/EPUB 电子书发布流水线。

**证据**
- F-005：config.mjs 为 10 个 locale 各配置独立 label/lang/title/description/head/nav/sidebar/docFooter。
- F-009：build-locales.mjs 默认 `groupSize=1` 顺序构建每个 locale，注释明确 VitePress 2 alpha 共享 `.temp` 目录会导致并发 `ERR_MODULE_NOT_FOUND`；使用 `build-locales.lock` 文件锁（PID 存活检测，15 分钟超时）。
- F-009：scan-appendix-component-i18n.mjs 对比两 locale 的 `<template>` 文案以发现翻译缺失；`docs/.vitepress/theme/locales/` 下按主题分目录存放组件英文文案。
- F-010：base 路径根据 `VERCEL`/`EDGEONE`/`BASE` 环境变量在 `/` 与 `/easy-vibe/` 间自动切换。
- F-010：release-books.yml 在 tag 推送时安装 texlive-xetex 及 CJK/阿拉伯/韩/日字体，执行 `npm run book:all` 产出 10 语言 PDF/EPUB 并附加到 GitHub Release。
- F-006：sidebars/index.mjs 导出 `getStage1Sidebar(locale)`、`getStage2Sidebar(locale)`、`getStage3Sidebar(locale)`、`localizeAppendixSidebar(sidebar, locale)` 等工厂函数，而非为每语言写死一份侧边栏。

**反常识**
多数团队把多语言站点的难点估计为"翻译质量"，但 Easy-Vibe 的工程投入集中在"构建确定性"：为规避 alpha 框架的并发 bug 而强制顺序构建、为跨平台部署而做 base 路径自适应、为组件内文案而写扫描工具。翻译本身依赖社区贡献，工程系统负责"不遗漏、不构建失败、产物可发布"。这说明：当内容体量达到 100+ 篇 × 10 语言时，构建与一致性保障的成本远超翻译本身。

**行动**
- 概念文档应单独讲解多语言架构的三层：内容层（`docs/{locale}/`）、配置层（localeMap + sidebar 工厂）、构建层（build-locales.mjs + 锁 + 电子书）。
- 解释"为什么顺序构建"这类反直觉决策必须引用源码注释作为证据，避免读者误以为是性能疏忽。
- 在部署与工具链概念中区分 Web 站点部署（Vercel/GitHub Pages/魔搭 Docker）与电子书发布（GitHub Release）两条独立流水线。

---

## 洞察三：文档站同时为人类读者与 AI Agent 设计——"AI 可读性"成为一等目标

**陈述**
Easy-Vibe 在常规 README 之外，额外维护了三层 AI Agent 导航资产：根目录 `llms.txt`（1380 行的导航地图，含决策树与关键词索引）、`CLAUDE.md`（Claude Code 专用指南）、`AGENTS.md`（通用 Agent 仓库规范），并在站点公开发布 `docs/public/llms.txt`。文档结构本身被设计成"AI 可定位、可引用、可按角色推荐"的形态。

**证据**
- F-013：根目录 llms.txt 含高层架构 ASCII 图、快速决策树（"问怎么开始→Stage 1""问数据库→Stage 2""问 MCP→Stage 3"）、每篇文章的文件路径+关键词+内容概要、8 条回答规则（含"引用来源""阶段匹配""不确定时先读文件"）。
- F-013：CLAUDE.md 为 Claude Code 提供项目概述、命令、架构、内容规范、多语言说明、bash 权限白名单。
- F-013：AGENTS.md 为通用 Agent 提供模块组织、构建命令、编码风格、测试、PR 规范。
- F-013：README 2026-03-02 新闻明确"Added llms.txt so OpenClaw, Claude, Cursor, Trae, and other AI agents can quickly understand the repository structure"。
- F-014：首页用浏览器语言自动重定向，降低人类读者的语言选择成本。
- F-008：附录 200+ 交互组件本身被组织成可在 Markdown 中直接引用的标签（如 `<TokenizationDemo />`），AI 可据此生成含交互演示的回答。

**反常识**
传统文档站默认读者是人，AI 消费文档只是"副作用"。Easy-Vibe 把 AI Agent 视为一等读者：专门为 AI 写"决策树+关键词倒排+回答规则"，把每篇文章标注关键词以便 AI 检索匹配，甚至在根目录同时放三份面向不同 Agent 的说明文件。这背后的判断是：当用户通过 Cursor/Claude/Trae 等 AI IDE 学习时，第一个"阅读"教程的往往是 AI，AI 能否准确找到并引用对应章节，直接决定学习体验。

**行动**
- 概念文档应解释 llms.txt 的结构（决策树→目录索引→文章元数据→回答规则）及其与 README/CLAUDE.md/AGENTS.md 的分工。
- 在 Vibe Coding 理念概念中说明"AI 友好文档"本身是 Vibe Coding 工作流的基础设施——AI IDE 需要可读的仓库结构才能辅助开发。
- 引用 examples/ 中每个项目的 `prompt.txt`（F-017）作为"可复现提示词"的实例，说明项目不仅教方法，还沉淀可直接复用的 AI 协作资产。
