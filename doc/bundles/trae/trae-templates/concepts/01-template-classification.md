---
type: Concept
title: 五维分面分类体系
description: trae-templates 采用五维分面分类法（Faceted Classification）组织 23 个模板，按应用形态分为 web-frontend/backend-service/mobile-desktop/data-ai/tools-devops 五大类，同一技术领域的模板分散在不同分面中，用户按目标平台+技术栈双维度定位模板。
tags: [trae-templates, classification, faceted, categories, taxonomy]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/templates-source.md
    title: Trae Templates 源码信源
---

## 什么是分面分类法

传统的树状分类法将事物放入一个层级结构中（如"编程语言→JavaScript→框架→React"），每样东西只能属于一个位置。而**分面分类法（Faceted Classification）**使用多个独立的"维度"（分面）来描述事物，用户可以从任意维度切入查找。

trae-templates 采用的第一分面是**应用形态**——即这个模板用来创建什么类型的应用：

| 分面 | 目录名 | 数量 | 核心问题 |
|------|--------|------|----------|
| Web 前端 | `web-frontend/` | 8 | 要在浏览器中运行的用户界面 |
| 后端服务 | `backend-service/` | 5 | 要在服务器上运行的 API/服务 |
| 移动与桌面 | `mobile-desktop/` | 3 | 要在手机或桌面运行的原生/跨平台应用 |
| 数据与 AI | `data-ai/` | 3 | 要做数据分析、机器学习或脚本自动化 |
| 工具与 DevOps | `tools-devops/` | 4 | 要配置开发工具、容器或 AI 工作流 |

## 为什么按应用形态而非语言分类

与常见的"按编程语言分类"（Python 模板/JS 模板/Go 模板）不同，trae-templates 的第一维度是应用形态。这带来几个优势：

1. **符合开发者思维习惯**：开发者通常先知道"我要做一个网站"，再决定"用 React 还是 Vue"
2. **跨语言对比更方便**：同一分面下可以看到不同语言/框架的方案对比
3. **避免分类歧义**：React 既可以做 Web 前端（react-starter）也可以做移动端（react-native），按语言分类无法体现这种区别

### 同一技术跨分面示例

| 技术 | Web 前端 | 移动桌面 |
|------|----------|----------|
| React | react-starter（React 18 + Vite） | react-native（React Native + Expo） |
| JavaScript/TypeScript | 多个前端模板 | electron-starter（Electron 桌面） |

分面语义天然区分了使用场景，不会造成混淆。

## 五大分面详解

### web-frontend（Web 前端）—— 8 个模板

| 模板 | 技术栈 | 构建工具 | 语言 | 特点 |
|------|--------|----------|------|------|
| web-basic | 纯 HTML/CSS/JS | 无 | JS | 零构建，浏览器直接打开 |
| react-starter | React 18 | Vite | JSX + CSS Modules | 主流 React 起点 |
| vue-starter | Vue 3 | Vite | SFC + Composition API | 主流 Vue 起点 |
| nextjs-starter | Next.js 14 | Next.js | TypeScript（App Router） | React SSR/全栈 |
| nuxtjs-starter | Nuxt 3 | Nuxt | TypeScript | Vue SSR/全栈 |
| svelte-starter | Svelte | Vite | Svelte | 编译时框架 |
| angular-starter | Angular | Angular CLI | TypeScript | 企业级框架 |
| tailwind-starter | Tailwind CSS | Tailwind CLI | HTML | 原子化 CSS |

选择建议：需要 SSR/SEO → Next.js/Nuxt；快速原型 → web-basic 或 react/vue-starter；喜欢编译时框架 → Svelte；企业项目 → Angular。

### backend-service（后端服务）—— 5 个模板

| 模板 | 语言 | 框架 | 启动命令 | 默认端口 |
|------|------|------|----------|----------|
| fastapi-service | Python | FastAPI + Uvicorn | `uvicorn app.main:app --reload` | 8000 |
| nodejs-express | Node.js | Express | `npm start` | 3000 |
| go-gin-service | Go | Gin | `go run main.go` | 8080 |
| java-springboot | Java 17+ | Spring Boot | `mvn spring-boot:run` | 8080 |
| rust-actix | Rust | Actix-web | `cargo run` | 8080（127.0.0.1） |

选择建议：高性能 API/自动文档 → FastAPI；快速原型/全栈 JS → Express；高并发微服务 → Go/Gin；企业级 Java 生态 → Spring Boot；安全/系统编程 → Rust/Actix。

### mobile-desktop（移动与桌面）—— 3 个模板

| 模板 | 技术栈 | 平台 | 开发方式 |
|------|--------|------|----------|
| react-native | React Native + Expo | iOS/Android/Web | Expo Go 扫码调试 |
| flutter-starter | Flutter + Dart | iOS/Android/Web/Desktop | Flutter SDK |
| electron-starter | Electron + Node.js | Windows/macOS/Linux | 网页技术栈开发桌面应用 |

选择建议：已有 React 经验 → React Native；追求多端一致性和性能 → Flutter；用网页技术开发桌面应用 → Electron。

### data-ai（数据与 AI）—— 3 个模板

| 模板 | 技术栈 | 用途 | 启动方式 |
|------|--------|------|----------|
| python-script | Python 3.8+ + venv + logging | 通用 Python 脚本 | `python main.py` |
| jupyter-notebook | Python + Jupyter | 数据分析/探索 | `jupyter notebook` |
| pytorch-starter | Python + PyTorch | 深度学习训练 | `python train.py`（自动 GPU） |

选择建议：自动化脚本/工具 → python-script；数据探索/可视化 → jupyter-notebook；模型训练 → pytorch-starter。

### tools-devops（工具与 DevOps）—— 4 个模板

| 模板 | 类型 | 用途 | 使用方式 |
|------|------|------|----------|
| docker-compose | 容器编排 | Nginx + PostgreSQL 本地开发环境 | `docker-compose up -d` |
| editor-config | 编辑器配置 | 统一团队代码格式 | 复制 `.editorconfig` 到项目根 |
| gitignore | 版本控制 | Node.js/Python 的 .gitignore | 复制对应文件并重命名 |
| superpowers-trae-init | AI 工作流 | TRAE AI 辅助开发约束（4条铁律+25+技能） | 复制 `.trae/` 目录到项目根 |

注意：tools-devops 中的模板不是"可运行项目"，而是"复制即用"的配置文件。superpowers-trae-init 尤其特殊，它是 AI 开发工作流配置包而非项目代码。

## 分面分类的使用方法

### 按分面定位模板

```
确定应用形态 → 在对应分面下选择技术栈 → 复制模板
```

示例：
1. "我要做一个 Python 后端 API" → backend-service → fastapi-service
2. "我要做一个 React 网站" → web-frontend → react-starter
3. "我要训练一个 PyTorch 模型" → data-ai → pytorch-starter

### 跨分面组合

实际项目中往往需要组合多个模板：
- 全栈项目：nextjs-starter（前端）+ fastapi-service（后端）
- 带 AI 辅助的 Web 项目：react-starter + superpowers-trae-init
- 数据分析项目：jupyter-notebook + editor-config + gitignore
- 桌面应用后端：electron-starter + nodejs-express

### 配置模板可叠加使用

tools-devops 下的模板（docker-compose、editor-config、gitignore）可以与任何项目模板组合使用。建议每个项目至少添加：
- `.editorconfig`（统一编辑器行为）
- 对应语言的 `.gitignore`
- 如果使用 TRAE 开发，添加 `superpowers-trae-init` 的 `.trae/` 配置

## 新增模板的分类原则

贡献新模板时判断所属分面：

1. **主要运行环境是什么？**
   - 浏览器 → web-frontend
   - 服务器/容器 → backend-service
   - 手机/桌面原生 → mobile-desktop
   - 数据处理/模型训练 → data-ai
   - 开发工具/配置/AI 工作流 → tools-devops

2. **跨分面模板如何处理？**
   - 全栈模板（如包含前后端）应考虑拆分为前后端两个模板
   - 配置类模板统一放入 tools-devops
   - 不要为了一个模板创建新分类——五维分面已覆盖主流场景

## 与 superpowers-trae-init 的特殊关系

tools-devops 分类的存在本身就是分面分类灵活性的体现——它不是"项目模板"，但因为"复制即用"的使用方式而被纳入。superpowers-trae-init 作为 AI 工作流配置包，是唯一一个不是代码起点而是行为起点的模板。

详见 [AGENTS.md 开发契约](/concepts/07-agents-contract.md)。

## 相关概念

- [Trae Templates 简介](/concepts/00-introduction.md)
- [Web 前端模板](/concepts/02-web-frontend-templates.md)
- [后端服务模板](/concepts/03-backend-templates.md)
- [移动端和桌面端模板](/concepts/04-mobile-desktop-templates.md)
- [数据与 AI 模板](/concepts/05-data-ai-templates.md)
- [工具与 DevOps 模板](/concepts/06-tools-devops-templates.md)
- [AGENTS.md 开发契约](/concepts/07-agents-contract.md)

## 相关内容

- [源码信源索引](/references/templates-source.md)
- [使用 Next.js 模板创建项目](/examples/use-nextjs-template.md)
- [创建自定义模板](/examples/create-custom-template.md)
