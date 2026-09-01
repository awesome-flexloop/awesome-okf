---
type: spec
title: "Vibe Vibe 架构洞察（I阶段）"
---

# Vibe Vibe 架构洞察（I阶段）

> 基于 spec/facts.md 的 F-xxx 事实，提炼 3 个核心洞察。
> 每个洞察采用四元组：陈述 / 证据 / 反常识 / 行动。

---

## 洞察一：基础篇 v2 用"单一连续案例"替代"知识点章节"——教学设计从教程转向陪伴式项目

**陈述**
Vibe Vibe 基础篇在 v2 重构中放弃了传统的"觉醒→心法→技法→实战→精进"分知识点章节结构，改为围绕"个人主页 + 数字分身"这一个连续案例，按 7 个交付里程碑（0-6 章）组织：先做出 v1 原型，再带回本地，再优化界面、补全内容、校准分身、最终上线。每章的"核心交付"列明确产出物，而非知识点列表。

**证据**
- F-005：`docs/Basic/index.md` 原文"这套基础篇已经按新版主线完成重写：围绕'个人主页 + 数字分身'这一个连续案例"，并声明"这不是一本'先学语法、再学框架、最后再做项目'的传统教材"。
- F-005：v2 章节表每章都有"核心交付"列（v1 原型、本地可运行项目、视觉统一的首页、完整主页+Git 闭环、稳定的数字分身、公网链接）。
- F-005：旧版 `Basic-old/` 仍保留，其结构是 5 章 + 附录，每章含大量子目录（如 `02-mindset/` 下有 8 个子节 + appendix），与 v2 的 7 章精简结构形成对比。
- F-005：基础篇默认读者是"独立 vibe coder"，不假设身边有前端、后端、测试同事。

**反常识**
多数编程入门教程按"知识点"线性排列（变量→循环→函数→DOM→框架），Vibe Vibe v2 反其道而行：零基础学习者在第 1 章就被要求做出"能预览、能聊天的版本"，而不是先学 HTML 标签或 JavaScript 语法。知识点（Git、部署、安全、数据存储）被打散到对应里程碑中，在"需要时"才出现。这押注的判断是：对零基础学习者而言，"完整走完从想法到上线的闭环"比"系统掌握语法知识"更能建立信心与直觉。

**行动**
- 概念文档应清晰呈现 v2 的 7 里程碑结构与每阶段交付物，强调"单一案例贯穿"的设计意图。
- 区分 v1（旧版知识点结构）与 v2（案例里程碑结构），说明 `Basic-old/` 保留是为了内容迁移过渡，而非推荐学习路径。
- 在 Basic 入门概念中说明"独立 vibe coder"定位对教学方式的影响——学习者需自己承担需求描述、结果审查、方向决策三重角色。

---

## 洞察二：双语架构的简洁性源于 VitePress 稳定版——与 10 语言项目的工程复杂度形成对比

**陈述**
Vibe Vibe 仅支持简体中文与英语两种语言，其多语言架构直接依赖 VitePress 1.6.4 稳定版的原生 `locales` 配置：root locale 承载中文内容（通过 `/zh/` 路径入口），`en` locale 镜像到 `docs/en/` 目录。没有自定义多语言构建脚本、没有文件锁、没有顺序构建、没有 i18n 翻译缺失扫描工具——`pnpm build` 直接调用 `vitepress build docs` 一次完成。

**证据**
- F-006：config.mts 第 71-248 行定义两个 locale（root + en），各自独立配置 nav、docFooter、outline 文案。
- F-006：`docs/index.md` 用 10 行 `resolveLocaleEntry()` 脚本根据 `navigator.languages` 做 zh/en 二选一重定向。
- F-006：`docs/zh/index.md` 与 `docs/en/index.md` 各自是完整的首页，hero/actions/features 全部本地化。
- F-009：`package.json` build 脚本就是 `vitepress build docs`，无 `build-locales.mjs` 之类自定义编排。
- F-008：VitePress 版本为 `^1.6.4`（稳定版），而非 easy-vibe 的 `^2.0.0-alpha.16`。
- F-007：英文内容在 `docs/en/` 下完整镜像 Basic/Advanced/Articles/Practice 四大板块（Glob 确认 200+ 文件）。

**反常识**
同样是 Datawhale 出品的 Vibe Coding 教程，easy-vibe 支持 10 种语言并为此构建了顺序构建+文件锁+组件 i18n 扫描+多语言 PDF/EPUB 发布等复杂工程系统；vibe-vibe 只支持 2 种语言，工程实现极简。这并非 vibe-vibe "落后"，而是反映了两个不同的定位选择：vibe-vibe 聚焦中文社区的系统化教程深度（四大板块、16 章进阶篇、100+ 交互组件），用稳定版 VitePress 降低维护负担；easy-vibe 追求全球广度，用 alpha 版 VitePress 换取多语言能力并承担工程成本。简洁是刻意选择的结果。

**行动**
- 概念文档应说明双语架构的三层：内容层（`docs/` 根为中文、`docs/en/` 为英文）、配置层（locales 块）、重定向层（`docs/index.md` 脚本）。
- 对比说明"为什么不需要自定义构建脚本"——VitePress 稳定版原生支持多语言并发构建，无 alpha 版的 `.temp` 目录冲突问题。
- 指出 `docs/zh/index.md` 作为 `/zh/` 入口的特殊安排（root locale 的 link 为空，但中文首页同时存在于根路径与 `/zh/` 路径）。

---

## 洞察三：llms.txt 是"AI 助教路由表"而非"仓库结构文档"——把教程本身变成 AI 可导航的学习系统

**陈述**
Vibe Vibe 的 `docs/public/llms.txt` 不是传统意义上的仓库 README 或 API 文档，而是一份专门为 AI 助手设计的"教学路由表"：它教 AI 如何识别学习者背景（三个诊断问题）、如何按人群推荐章节（5 类用户映射表）、如何回答常见问题（FAQ 快答表），并给出技术栈速查与代码引用规范。文件最后更新于 2026-02-03，明确标注"GOLDEN START FOR AI ASSISTANTS"。

**证据**
- F-013：llms.txt 含"AI Assistant Collaboration Guide"章节，要求 AI 先问三个问题（编程背景、想做什么、用过哪些 AI 工具）。
- F-013：llms.txt 提供 5 类用户的推荐起点与关键章节映射表（如"Complete zero background → Basic/00-preface/"）。
- F-013：llms.txt 提供 7 行"Common Tasks Quick Links"表，将"环境搭建""写 PRD""UI 设计""数据库设计""用户认证""部署""SEO"直接映射到章节路径。
- F-013：llms.txt "Special Notes for AI"章节给出 4 条响应方法（判断学习阶段、给具体章节链接而非泛泛而谈、结合目标推荐路径、鼓励动手）。
- F-013：与 easy-vibe 不同，vibe-vibe 根目录无 CLAUDE.md/AGENTS.md，AI 导航资产集中在 llms.txt 一份文件中。
- F-013：llms.txt 公开发布在 `docs/public/llms.txt`，站点访问者与 AI IDE 均可获取。

**反常识**
传统教程的"AI 友好"通常体现为提供仓库结构说明或 API 文档，假设 AI 自己会读完整教程再回答。Vibe Vibe 的 llms.txt 反过来教 AI"如何教"——它不描述仓库文件树，而是描述教学决策树：什么背景的学习者该从哪章开始、什么问题对应哪个章节链接、回答时应遵循什么原则。这意味着课程设计者把"AI 助教的教学法"本身作为教程的一部分进行工程化，AI 不是被动检索文档，而是被引导按照课程设计的教学路径来辅助学习者。

**行动**
- 概念文档应解析 llms.txt 的四层结构：项目本质→AI 协作指南（诊断+路由）→关键链接→AI 特别注意事项。
- 在 Vibe 开发理念概念中说明"AI 助教路由表"是 Vibe Coding 教学法的自然延伸——课程教人用自然语言指挥 AI，同时也教 AI 如何教人。
- 引用 llms.txt 中的 FAQ 快答表与任务链接表作为实例，展示"章节路径即 API 端点"的设计思路。
