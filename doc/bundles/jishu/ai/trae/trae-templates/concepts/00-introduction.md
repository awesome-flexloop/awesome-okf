---
type: Concept
title: Trae Templates 简介
description: Trae Templates 是 TRAE IDE 的社区项目模板仓库，采用五维分面分类体系组织 23 个极简启动模板，覆盖 Web 前端、后端服务、移动桌面、数据 AI、工具 DevOps 五大领域，模板定位为"复制即用"的起点而非完整脚手架。
tags: [trae-templates, introduction, templates, project-scaffolding]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/templates-source.md
    title: Trae Templates 源码信源
---

## 什么是 Trae Templates

Trae Templates 是 TRAE IDE 的社区维护项目模板集合，采用 MIT 许可证开源。它提供了 23 个极简启动模板，帮助开发者快速开始各种类型的项目开发。

与传统的项目脚手架工具不同，Trae Templates 的核心理念是**"最小可用"（Minimal Viable）**——每个模板仅包含该技术栈启动并运行所必需的最少文件，不包含多余的配置文件、依赖锁定文件或示例代码。

## 模板仓库定位

Trae Templates 不是一个 CLI 工具或包管理器，而是一个**模板文件集合**。使用方式极其简单：

1. 浏览 `templates/` 目录，选择适合的模板
2. 复制模板文件夹到目标位置，或复制特定配置文件到已有项目
3. 按模板内的 `README.md`（及 `README.zh-CN.md`）自定义项目

每个模板目录都包含双语 README（README.md + README.zh-CN.md），详细说明技术栈、文件结构和启动命令。

## 五大分类体系

23 个模板按**应用形态**分为五大类（五维分面分类法）：

| 分类 | 数量 | 覆盖范围 |
|------|------|----------|
| **Web 前端**（web-frontend） | 8 个 | 纯 HTML/CSS/JS、React、Vue、Next.js、Nuxt、Svelte、Angular、Tailwind CSS |
| **后端服务**（backend-service） | 5 个 | FastAPI（Python）、Express（Node.js）、Gin（Go）、Spring Boot（Java）、Actix（Rust） |
| **移动与桌面**（mobile-desktop） | 3 个 | React Native/Expo、Flutter、Electron |
| **数据与 AI**（data-ai） | 3 个 | Python 脚本、Jupyter Notebook、PyTorch 训练 |
| **工具与 DevOps**（tools-devops） | 4 个 | Docker Compose、.editorconfig、.gitignore、superpowers-trae-init |

五维分面的第一维度是**应用形态**而非编程语言，这意味着同一框架（如 React）可能同时出现在不同分类中（react-starter 在 Web 前端，react-native 在移动桌面），但分类语义已区分了使用场景。

## 模板与项目脚手架的区别

理解 Trae Templates 与传统项目脚手架的区别至关重要：

| 维度 | Trae Templates | 传统脚手架（create-react-app/vue-cli 等） |
|------|---------------|------------------------------------------|
| **设计哲学** | 最小可用，仅提供起点 | 功能完整，开箱即用 |
| **文件数量** | 极少（3-8 个文件） | 数十个文件+配置 |
| **依赖锁定** | 不含 lock 文件 | 包含 package-lock.json/yarn.lock |
| **技术决策** | 不替开发者做选择（无路由库、状态管理、测试框架） | 预设全套技术方案 |
| **使用方式** | 复制文件夹即可 | CLI 命令生成 |
| **AI 协作支持** | 包含 superpowers-trae-init 等 AI 工作流配置 | 无 AI 相关配置 |
| **适用场景** | AI Agent 辅助开发、快速原型、学习技术栈 | 生产项目初始化 |

核心差异：Trae Templates **不替开发者做技术决策**。例如 react-starter 仅包含 React+Vite+CSS Modules，不包含路由库、状态管理方案、测试框架或 CSS 方案的选择；python-script 仅提供 venv+logging 的最小约定，不指定 argparse/click/typer 等 CLI 框架。

## 特殊模板：superpowers-trae-init

tools-devops 分类下的 `superpowers-trae-init` 不是传统意义上的"项目模板"，而是一个 **AI 开发工作流配置包**。它通过 `.trae/` 目录下的规则文件和技能目录实现 TRAE IDE 的行为定制：

- **4 条铁律**：NO FIX WITHOUT ROOT CAUSE / NO PRODUCTION CODE WITHOUT RED TEST / NO BLIND MOCKING / NO GUESSING THE OUTPUT
- **工具适配映射**：将 Agent 通用工具映射到 TRAE 特定实现
- **触发器字典**：将开发场景分类并路由到对应技能
- **25+ 技能集**：包含 brainstorming、test-driven-development、systematic-debugging 等完整技能生态

它被纳入模板库是因为其使用方式与项目模板一致——**复制即用**（复制 `.trae/` 目录到项目根即可生效）。

详见 [AGENTS.md 开发契约](07-agents-contract.md)。

## 模板设计原则

所有 23 个模板遵循以下设计原则：

1. **最小可用**：每个模板仅包含启动所必需的最少文件
2. **单入口可运行**：提供一个主入口文件，直接可运行或编译
3. **双语 README**：中英文说明文档，降低使用门槛
4. **零依赖锁定**：不提供 lock 文件，避免过时依赖安全问题
5. **不替用户选辅助库**：不预设路由、状态管理、测试框架等
6. **AI 友好**：简洁的文件结构不会干扰 AI Agent 生成代码

## 如何选择模板

```
你要创建什么类型的项目？
├── Web 前端应用
│   ├── 纯静态页面 → web-basic
│   ├── React 单页应用 → react-starter
│   ├── Vue 单页应用 → vue-starter
│   ├── Next.js 全栈/SSR → nextjs-starter
│   ├── Nuxt 全栈/SSR → nuxtjs-starter
│   ├── Svelte 应用 → svelte-starter
│   ├── Angular 企业应用 → angular-starter
│   └── Tailwind CSS 页面 → tailwind-starter
├── 后端 API 服务
│   ├── Python/FastAPI → fastapi-service
│   ├── Node.js/Express → nodejs-express
│   ├── Go/Gin → go-gin-service
│   ├── Java/Spring Boot → java-springboot
│   └── Rust/Actix → rust-actix
├── 移动端/桌面应用
│   ├── 跨平台移动 App → react-native（Expo）
│   ├── Flutter 应用 → flutter-starter
│   └── 桌面应用 → electron-starter
├── 数据/AI 项目
│   ├── Python 脚本 → python-script
│   ├── 数据分析 Notebook → jupyter-notebook
│   └── 深度学习训练 → pytorch-starter
└── 工具/DevOps 配置
    ├── Docker 编排 → docker-compose
    ├── 编辑器统一配置 → editor-config
    ├── .gitignore 模板 → gitignore
    └── AI 辅助开发工作流 → superpowers-trae-init
```

## 相关概念

- [五维分面分类体系](01-template-classification.md)
- [Web 前端模板](02-web-frontend-templates.md)
- [后端服务模板](03-backend-templates.md)
- [移动端和桌面端模板](04-mobile-desktop-templates.md)
- [数据与 AI 模板](05-data-ai-templates.md)
- [工具与 DevOps 模板](06-tools-devops-templates.md)
- [AGENTS.md 开发契约](07-agents-contract.md)

## 相关内容

- [源码信源索引](../references/templates-source.md)
- [使用 Next.js 模板创建项目](../examples/use-nextjs-template.md)
