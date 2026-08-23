---
title: Vibe Coding 理念
type: concept
bundle: /datawhale/easy-vibe
description: Easy-Vibe 把"用自然语言描述需求、由 AI 实现、人来决策与迭代"作为编程新范式，并以三阶段路径把零基础学习者带到可交付产品的水平。
related:
  - /datawhale/easy-vibe/concepts/multilingual-docs-architecture
  - /datawhale/easy-vibe/concepts/deployment-toolchain
sources:
  - https://github.com/datawhalechina/easy-vibe
---

## 什么是 Vibe Coding

Vibe Coding 是 Easy-Vibe 课程的核心理念，指在 AI 时代**编程从"描述你想要什么"开始**，而不是从手写语法开始。README 中的原文是：

> "In the AI era, programming starts by describing what you want."
> （在 AI 时代，编程从描述你的需求开始。）

`llms.txt` 将其直接注释为"用自然语言编程"。学习者在 AI IDE（如 Cursor、Claude Code、Trae）中用对话方式表达意图，AI 生成代码，人负责判断方向、验证结果、提出修改。这把人的角色从"逐行写代码的实现者"转变为"描述需求、审查产出、迭代方向的决策者"。

Easy-Vibe 用一句话概括课程目标："Learn AI coding from zero by shipping real products.（从零开始学 AI 编程，把想法真正做成产品。）"

## 与传统编程学习的路径差异

传统编程教育通常按"语法 → 数据结构 → 算法 → 工程"的线性顺序组织，把基础视为不可跳过的前置门槛。Easy-Vibe 反转了这一顺序：

| 维度 | 传统路径 | Vibe Coding 路径（Easy-Vibe） |
|------|---------|------------------------------|
| 第一动作 | 学习变量、循环、函数语法 | 用自然语言让 AI 做出贪吃蛇游戏 |
| 第一阶段产出 | 控制台练习题 | 可演示的产品原型 |
| 产品思维位置 | 高级/职业阶段才涉及 | Stage 1 前置（找创意、用户访谈、双钻模型） |
| 基础知识位置 | 前置必修课 | 附录知识库，按需查阅 |
| 人的角色 | 代码实现者 | 需求描述者 + 结果审查者 |

课程押注的判断是：AI 时代"描述需求与验证想法"的能力比"手写语法"的能力更稀缺。因此它把计算机基础、网络协议、数据结构等内容下沉到 `appendix/`（附录），作为"遇到阻塞才查阅"的参考资料，而非入学门槛。

## 三阶段能力递进

Easy-Vibe 采用 3+1 阶段的渐进式路径，每个阶段都有可交付产出：

### Stage 1：新手入门与产品原型

目录 `docs/{locale}/stage-1/`（含部分 `stage-0/` 内容）。目标是建立编程思维、掌握 AI IDE、快速构建产品原型。章节包括：

- 学习地图（learning-map）
- AI 时代，会说话就会编程（通过贪吃蛇等小游戏体验）
- 认识 AI IDE 工具
- 找到好创意（finding-great-idea）
- 动手做出原型（building-prototype）
- 给原型加上 AI 能力（文本、图片、视频 API 接入）
- 完整项目实战（接受用户反馈并迭代）

附录补充产品思维：双钻模型（Double Diamond）、Jobs to Be Done、The Mom Test 用户访谈法、产品思维框架、常见报错排查。

### Stage 2：初中级全栈开发

目录 `docs/{locale}/stage-2/`，分为 `frontend/`、`backend/`、`ai-capabilities/`、`assignments/`。目标是从原型走到可上线的全栈 AI 应用：

- 前端：Lovart 素材、Figma/MasterGo、UI 设计、现代组件库、设计转代码
- 后端：Git 工作流、Supabase 数据库、API 设计、Zeabur 部署、现代 CLI、Stripe 支付
- AI 能力：Dify 知识库、多模态 API
- 大作业：AI 文案生成 SaaS 全栈应用、在线考试系统

### Stage 3：高级开发

目录 `docs/{locale}/stage-3/`，含 `core-skills/`、`cross-platform/`、`ai-advanced/`。聚焦 Claude Code 深度使用与跨平台交付：

- Claude Code 核心技能：basics、MCP、Skills、long-running-tasks、agent-teams、superpowers、workflow、mobile-development、spec-coding、claude-agent-sdk
- 跨平台：微信小程序（含后端）、Android、iOS、PWA、浏览器 AI 插件、Electron 语音转文字、NFT 铸造、VS Code 插件、Qt 工业 HMI
- AI 进阶：RAG 入门、LangGraph 高级 RAG

### 附录：知识体系

目录 `docs/{locale}/appendix/`，覆盖 9 大领域、80+ 交互式专题：

1. 计算机基础（晶体管到 CPU、操作系统、网络、数据结构、算法、编译原理、类型系统）
2. 开发工具（IDE、命令行、Git、环境变量、包管理器、SSH、调试、正则）
3. 浏览器与前端（HTML/CSS、JavaScript、TypeScript、框架、工程化、渲染、路由、状态管理、性能、无障碍）
4. 服务器与后端（语言、分层架构、API、Web 框架、HTTP、认证、缓存、消息队列、限流）
5. 数据（数据库、数据模型、分析、可视化、A/B 测试、埋点、治理）
6. 架构与系统设计（方法论、分布式、高可用、微服务）
7. 基础设施与运维（Linux、Docker、K8s、CI/CD、云平台、IAM、DNS/HTTPS、监控）
8. 人工智能（AI 史、神经网络、Transformer、LLM、Prompt、RAG、Agent、多模态、MCP 协议）
9. 工程卓越（代码质量、测试、设计模式、技术选型、开源协作、安全、技术写作）

附录的特色是 200+ 个交互式 Vue 组件（如 `<TokenizationDemo />`、`<GitCommitFlow />`、`<DiffusionProcessDemo />`），在 Markdown 中直接以标签引用，把抽象原理做成可点击的可视化演示。

## 目标读者分层

课程明确面向五类人群，并为不同人群推荐不同入口：

- **完全零基础**：从 Stage 1 的小游戏体验开始，先建立"AI 编程是什么感觉"
- **产品经理/创始人**：Stage 1 重点学习创意验证、MVP 原型、低成本验证
- **学生**：系统走完三阶段，建立 AI 时代实用技能
- **初中级开发者**：Stage 2 补齐全栈（数据库、部署、支付），Stage 3 学习 Claude Code 工作流
- **中高级开发者**：Stage 3 的 MCP、Agent Teams、Spec Coding、跨平台交付

## AI 友好的教学设计

Vibe Coding 理念不仅是教学内容，也体现在课程本身的工程设计中——课程仓库同时为人类读者和 AI Agent 服务：

- 根目录 `llms.txt` 是一份 1380 行的 AI 导航地图，含决策树、关键词倒排索引、每篇文章的文件路径与回答规则，让 Cursor/Claude/Trae 等 AI IDE 能准确定位章节。
- `CLAUDE.md` 为 Claude Code 提供项目结构与命令指南。
- `AGENTS.md` 为通用 AI Agent 提供仓库规范。
- `examples/` 下每个练习项目都附带 `prompt.txt`，沉淀了可直接复用的 AI 提示词。

这种"AI 可读性"设计本身是 Vibe Coding 工作流的基础设施：当学习者在 AI IDE 中打开本仓库时，AI 能先读 llms.txt 理解课程结构，再把对应章节推给学习者。

## 相关概念

- [多语言文档站架构](/ai/datawhale/easy-vibe/concepts/02-multilingual-docs-architecture.md)：Vibe Coding 教程如何以 10 语言交付，以及其构建系统如何保障确定性。
- [部署与工具链](/ai/datawhale/easy-vibe/concepts/03-deployment-toolchain.md)：从本地开发到多平台部署、电子书发布的完整工具链。
