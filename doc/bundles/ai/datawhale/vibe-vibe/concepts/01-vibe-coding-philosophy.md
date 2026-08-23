---
title: Vibe 开发理念
type: concept
bundle: /datawhale/vibe-vibe
description: Vibe Vibe 以 Andrej Karpathy 提出的 Vibe Coding 为核心理念，主张从 Coder 到 Commander 的角色转变，用自然语言描述需求、AI 负责实现、人负责决策与迭代，并通过 llms.txt 把教程本身构建为 AI 可导航的学习系统。
related:
  - /datawhale/vibe-vibe/concepts/02-basic-getting-started
  - /datawhale/vibe-vibe/concepts/03-multilingual-docs-architecture
sources:
  - https://github.com/datawhalechina/vibe-vibe
---

## 什么是 Vibe Coding

Vibe Coding 是 OpenAI 联合创始人 Andrej Karpathy 于 2025 年提出的编程范式，也是 Collins 词典年度词汇。Karpathy 的原始定义是：

> "There's a new kind of coding I call 'vibe coding', where you fully give in to the vibes, embrace exponentials, and forget that the code even exists."
>
> — Andrej Karpathy, 2025

Vibe Vibe 将这一理念作为课程基石，在 README 中概括为**"从 Coder 到 Commander"**：

> "通过自然语言与 AI 对话，让编程从'写代码'转变为'对话式创作'。"

在 Vibe Vibe 的定位中，Vibe Coding 不是"乱写代码"的借口，而是更大的**AI 创造**概念的子集：

- **用自然语言描述目标与需求**，而不是所有步骤都亲手完成
- **让 AI 参与实现、组织和迭代**，你负责验收、判断和调整
- **更快把想法变成真实成果**，因为做出东西往往比空想和完美规划更能推动学习

一句话概括：**你负责方向、判断和审美，AI 帮你把作品做出来。**

## 从 Coder 到 Commander 的角色转变

传统编程中，人的角色是"代码实现者"——逐行编写语法、调试逻辑、管理架构。Vibe Coding 将人的角色转变为"指挥官"（Commander）：

| 维度 | 传统 Coder | Vibe Commander |
|------|-----------|----------------|
| 核心动作 | 手写代码 | 描述需求 |
| 与 AI 的关系 | AI 是补全工具 | AI 是执行伙伴 |
| 主要精力 | 语法实现与细节调试 | 方向判断、结果审查、迭代决策 |
| 产出方式 | 逐行构建 | 对话式生成 + 多轮修正 |
| 知识要求 | 精通语法与框架 | 清楚想要什么、能判断结果对错 |

课程明确声明它"不是为了把你一次训练成资深工程师"，而是培养三种实际能力：

1. 把想法做成真实作品的能力
2. 一套可重复使用的 AI 协作方法
3. 更强的产品判断、迭代习惯和上线信心

## MVP 思维与减法原则

Vibe Vibe 把产品思维前置到编程入门之前。基础篇第 2 章"心法"专门训练：

- **MVP 思维**：如何设计一个"能跑的最小版本"，用最少时间验证想法
- **拒绝功能堆砌**：为什么你的 AI 写不出复杂的 App——因为功能蔓延
- **灵魂三问**：用户是谁？痛点在哪？为何用你？
- **功能优先级 P0/P1/P2**：学会对 AI 说"这个先不做"

这些不是高级产品经理的专属技能，而是零基础学习者在写第一行代码之前就需要建立的思维方式。课程押注的判断是：AI 时代"描述需求与验证想法"的能力比"手写语法"的能力更稀缺。

## AI 创造工作流

Vibe Vibe 定义的 AI 创造工作流不是"让 AI 写代码"这么简单，而是一个完整的创造闭环：

1. **梳理想法**：用灵魂三问和用户旅程地图把模糊想法变成清晰路径
2. **编写 PRD**：写第一份产品需求文档，让 AI 不再胡编乱造
3. **搭原型**：先生成静态页面"看脸"，再注入逻辑"长脑"
4. **补内容**：用 AI 补充文案、数据、素材
5. **改交互**：多轮对话优化界面与体验
6. **推上线**：部署到公网，获取真实用户反馈
7. **迭代**：根据反馈持续优化

在这个工作流中，AI 不只是代码生成器，而是参与了从想法到产品的全流程。

## 四大板块的能力递进

课程按四大板块组织渐进式学习路径：

| 板块 | 能力目标 | 产出 |
|------|---------|------|
| 基础篇 | 理解 AI 创造工作流、用 AI 做出第一个作品、掌握 MVP 思维 | 个人主页 + 数字分身（公网可访问） |
| 进阶篇 | 全栈架构、生产级部署、协作迭代、工程判断力 | 完整全栈产品（Next.js + PostgreSQL） |
| 实践篇 | 分人群项目实战、AI Agent 开发、全栈项目 | 多个可交付项目 |
| 优质文章篇 | 行业前沿追踪、持续学习 | 知识体系更新 |

进阶篇的技术栈明确为：Next.js 16 · React · TypeScript · Tailwind CSS · shadcn/ui · Drizzle ORM · PostgreSQL，部署平台推荐 Vercel / EdgeOne Pages。

## llms.txt：AI 助教路由表

Vibe Vibe 的 Vibe Coding 理念不仅体现在教学内容中，也体现在课程本身的工程设计里。`docs/public/llms.txt` 是一份专门为 AI 助手设计的"教学路由表"，而非传统的仓库结构文档。

### 它教 AI 如何教学

llms.txt 要求 AI 助手在帮助学习者时：

1. **先问三个诊断问题**：
   - 你有编程背景吗？
   - 你想做什么（学概念/做项目/解决具体问题）？
   - 你用过哪些 AI 工具（Cursor/Windsurf/Bolt.new/Claude/ChatGPT）？

2. **按人群推荐章节**：

| 用户类型 | 推荐起点 |
|---------|---------|
| 完全零基础 | Basic/00-preface/ |
| 用过 ChatGPT 但没做过项目 | Basic/02-mindset/ |
| 有编程背景 | Advanced/01-environment-setup/ |
| 想直接动手做项目 | Basic/04-practice-0-to-1/ |
| 想找练手项目 | Practice/ |

3. **按任务给出章节链接**：写 PRD → `/Advanced/03-prd-doc-driven/`，数据库设计 → `/Advanced/06-data-persistence-database/`，部署 → `/Advanced/12-serverless-deploy-cicd/` 等。

4. **遵循回答原则**：给具体章节链接而非泛泛而谈、结合用户目标推荐路径、鼓励动手实践。

### 设计意图

这体现了一个反常识的设计判断：当用户通过 Cursor/Claude/Trae 等 AI IDE 学习时，第一个"阅读"教程的往往是 AI。AI 能否准确找到并引用对应章节，直接决定学习体验。因此课程设计者把"AI 助教的教学法"本身作为教程的一部分进行工程化——课程教人用自然语言指挥 AI，同时也教 AI 如何教人。

## 目标读者

课程明确面向多类人群，并为不同人群推荐不同入口：

- **完全零基础者**：从基础篇第 1 章开始，先建立"AI 编程是什么感觉"
- **文科生/商科生/设计师/产品经理**：基础篇，零代码基础也能做出可运行原型
- **前端开发者**：进阶篇，扩展后端能力成为全栈工程师
- **后端开发者**：进阶篇，了解现代前端生态和 Next.js
- **创业者/独立开发者**：基础篇 + 进阶篇，快速搭建 MVP 独立完成产品
- **想提升效率的开发者**：系统学习 AI 辅助开发工作流

## 相关概念

- [Basic 入门教学设计](/ai/datawhale/vibe-vibe/concepts/02-basic-getting-started.md)：Vibe 理念如何在基础篇中通过单一连续案例落地。
- [多语言文档架构](/ai/datawhale/vibe-vibe/concepts/03-multilingual-docs-architecture.md)：承载 Vibe 教学内容的中英文双语文档站工程实现。
