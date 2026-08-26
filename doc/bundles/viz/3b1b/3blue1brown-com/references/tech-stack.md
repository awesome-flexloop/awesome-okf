---
type: Reference
title: 3Blue1Brown.com 完整技术栈清单
description: 3Blue1Brown.com 所有核心 npm 依赖的完整清单，区分 dependencies/devDependencies，标注版本、用途与在项目中的角色。
tags: [3blue1brown, tech-stack, dependencies, npm, react, react-router, vite, tailwind, mdx]
generated: { by: "source-code-to-okf-wiki/e-phase", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: 3Blue1Brown.com 源码事实采集
  - id: insights
    resource: /spec/insights.md
    title: 3Blue1Brown.com 前端架构洞察
---

# 3Blue1Brown.com 完整技术栈清单

本文档基于 `package.json` 登记所有核心依赖（F-001 ~ F-022），区分生产依赖与开发依赖，标注每个技术的版本号、核心用途以及在 3Blue1Brown.com 项目架构中的角色。

项目使用 ES Modules 规范（F-001），包管理首选 Bun（F-129），但所有脚本兼容 npm/yarn/node。

## 生产依赖（dependencies）

### 核心框架层

| 包名 | 版本 | 核心用途 | 项目角色 | 事实依据 |
|------|------|----------|----------|----------|
| `@react-router/node` | ^8.2.0 | React Router 框架模式 Node.js 适配器 | 提供 SSR/预渲染所需的 Node.js 运行时 API，配合 `ssr: false` 配置实现纯 SSG | F-004 |
| `react` | ^19.2.7 | React 核心库 | UI 渲染核心，使用 React 19 最新特性如 `use()` API 消费异步组件 | F-005 |
| `react-dom` | ^19.2.7 | React DOM 渲染器 | 客户端水合与 DOM 操作，配合 React 19 的并发渲染特性 | F-005 |
| `react-router` | ^8.2.0 | React Router 核心库 | 路由系统核心，提供框架模式的路由定义、数据加载、错误边界等能力 | F-004 |

### 样式与 UI 层

| 包名 | 版本 | 核心用途 | 项目角色 | 事实依据 |
|------|------|----------|----------|----------|
| `@tailwindcss/vite` | ^4.3.3 | Tailwind CSS v4 Vite 插件 | Tailwind v4 零配置集成入口，通过 Vite 插件链在构建时处理 Tailwind 指令 | F-007 |
| `@base-ui/react` | ^1.6.0 | Base UI 无样式组件库 | 提供 Dialog、Tooltip、Tabs 等基础无样式可访问组件，项目自定义样式 | F-018 |
| `@phosphor-icons/react` | ^2.1.10 | Phosphor 图标库 React 封装 | 全站图标系统，通过 IconContext.Provider 统一设置默认 className 为 "icon" | F-020、F-050 |
| `@fontsource-variable/figtree` | latest | Figtree 可变无衬线字体 | 标题、UI 控件字体，通过 CSS @font-face 导入 | F-019、F-047、F-097 |
| `@fontsource-variable/source-serif-4` | latest | Source Serif 4 可变衬线字体 | 正文内容默认字体，数学与正文阅读体验优化 | F-019、F-047、F-097 |
| `@fontsource-variable/sometype-mono` | latest | Sometype Mono 可变等宽字体 | 代码块、数学公式等宽排版场景 | F-019、F-047、F-097 |

### 状态与工具层

| 包名 | 版本 | 核心用途 | 项目角色 | 事实依据 |
|------|------|----------|----------|----------|
| `jotai` | ^2.20.2 | Jotai 原子化状态管理 | 全局状态管理核心：暗模式持久化（atomWithStorage）、视频播放状态、导航菜单、目录标题等 | F-010、I-04 |
| `@reactuses/core` | ^6.4.0 | ReactUse Hooks 工具库 | 通用 React Hooks 集合，如 useMutationObserver（MathJax DOM 监听）等 | F-021、F-057 |
| `clsx` | latest | className 条件拼接 | 全站 className 条件拼接统一工具，替代 classnames/cn 等方案 | F-127 |

### 媒体与交互层

| 包名 | 版本 | 核心用途 | 项目角色 | 事实依据 |
|------|------|----------|----------|----------|
| `youtube-video-element` | ^1.9.0 | YouTube 视频 Custom Element | Web Components 封装的 YouTube 播放器，镜像原生 `<video>` API | F-011、F-061、I-04 |
| `vimeo-video-element` | ^1.7.2 | Vimeo 视频 Custom Element | Web Components 封装的 Vimeo 播放器，动态导入避免初始包体积 | F-011、F-067、I-04 |
| `three` | 0.185.1 | Three.js 3D 渲染库 | 3D 交互演示底层渲染引擎，配合 @react-three/fiber 使用 | F-012 |
| `@react-three/fiber` | 9.6.1 | React Three Fiber | Three.js 的 React 渲染器，用于课程中的 3D 交互可视化 | F-012 |
| `d3` | ^7.9.0 | D3.js 数据可视化库 | 数据驱动的图表与可视化，用于课程中的统计图表展示 | F-013 |
| `gsap` | ^3.15.0 | GSAP 动画库 | 高性能动画引擎，用于复杂交互动画和页面过渡效果 | F-014 |
| `react-p5` | ^1.4.1 | p5.js React 封装 | 创意编码与交互演示，用于课程中的 Processing 风格可视化 | F-015 |
| `fuse.js` | ^7.5.0 | Fuse.js 模糊搜索 | 客户端全文模糊搜索，用于课程/博客内容搜索功能 | F-016 |
| `comlink` | ^4.4.2 | Comlink Web Worker 通信 | 简化 Web Worker 与主线程的通信封装，用于 heavy 计算场景 | F-017 |

### MDX 内容处理（运行时）

| 包名 | 版本 | 核心用途 | 项目角色 | 事实依据 |
|------|------|----------|----------|----------|
| `react-markdown` | 间接依赖 | Markdown 运行时渲染 | Markdownify 组件底层依赖，提供 markdown 元素到 React 组件的映射 | F-087 |

### 无障碍与测试（运行时）

| 包名 | 版本 | 核心用途 | 项目角色 | 事实依据 |
|------|------|----------|----------|----------|
| `@axe-core/playwright` | ^4.12.1 | axe-core Playwright 集成 | E2E 测试中的无障碍（a11y）自动化检测 | F-022 |

## 开发依赖（devDependencies）

### 构建工具链

| 包名 | 版本 | 核心用途 | 项目角色 | 事实依据 |
|------|------|----------|----------|----------|
| `@react-router/dev` | ^8.2.0 | React Router 开发工具与 Vite 插件 | React Router 框架模式核心插件，提供类型生成、dev 服务器、构建优化 | F-004 |
| `vite` | ^8.1.5 | Vite 构建工具 | 现代前端构建工具，提供极速 HMR、Rollup 生产构建、插件系统 | F-006 |

### MDX 内容处理（构建时）

| 包名 | 版本 | 核心用途 | 项目角色 | 事实依据 |
|------|------|----------|----------|----------|
| `@mdx-js/rollup` | ^3.1.1 | MDX Rollup/Vite 插件 | MDX 编译核心，在 Vite 构建时将 .mdx 文件转换为 React 组件 | F-008 |
| `remark-frontmatter` | ^5.0.0 | Remark frontmatter 解析 | 解析 MDX 文件顶部的 YAML frontmatter 元数据 | F-009 |
| `remark-mdx-frontmatter` | ^5.2.0 | Remark MDX frontmatter 导出 | 将解析后的 frontmatter 作为 ES 模块导出，供 `import.meta.glob` 消费 | F-009 |
| `remark-math` | ^6.0.0 | Remark 数学公式解析 | 构建时标记 `$...$` 和 `$$...$$` 数学公式为 `<code class="language-math">`，供运行时 MathJax 渲染 | F-009、F-055、I-03 |
| `remark-gfm` | ^4.0.1 | Remark GitHub Flavored Markdown | 支持 GFM 扩展语法：表格、任务列表、删除线、自动链接等 | F-009 |

### 测试工具

| 包名 | 版本 | 核心用途 | 项目角色 | 事实依据 |
|------|------|----------|----------|----------|
| `@playwright/test` | ^1.61.1 | Playwright E2E 测试框架 | 端到端测试框架，预渲染路由列表写入 `tests/routes.json` 供其遍历测试 | F-022、F-041 |

## 技术栈版本策略总结

| 策略维度 | 具体选择 | 说明 |
|----------|----------|------|
| **版本范围** | 全部使用 `^`  caret 范围 | 允许兼容更新，不锁定精确版本，保持依赖新鲜度 |
| **框架版本** | React 19 + React Router 8 | 使用最新稳定版框架，充分利用 React 19 `use()` API 等新特性 |
| **构建工具** | Vite 8 + Rollup 生态 | 现代 ESM-first 构建链，插件生态丰富，构建速度快 |
| **样式方案** | Tailwind CSS v4 CSS-first | 零 JS 配置文件，纯 CSS 主题定义，自定义变体能力强（洞察 I-02） |
| **包管理器** | Bun 首选，兼容 npm/yarn | 利用 Bun 速度优势，但不使用 Bun 专有 API 保持兼容（F-129） |
| **部署目标** | Netlify 静态站点 | 纯静态 HTML/CSS/JS 产物，无 Node.js 服务器运行时依赖（F-130） |

## 相关概念

- [00 官网技术栈总览](/concepts/00-website-overview.md)
- [01 项目结构与目录组织](/concepts/01-project-structure.md)
- [02 路由与 SSG 预渲染](/concepts/02-routing-and-pages.md)
- [核心组件路径索引](/references/component-index.md)
