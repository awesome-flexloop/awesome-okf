---
type: Concept
title: Web 前端模板
description: web-frontend 分类包含 8 个模板，覆盖从纯 HTML/CSS/JS 到 React/Vue/Next.js/Nuxt/Svelte/Angular/Tailwind 的全主流前端生态，每个模板遵循最小可用原则，提供单入口可运行的起点。
tags: [trae-templates, web-frontend, react, vue, nextjs, nuxt, svelte, angular, tailwind]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/templates-source.md
    title: Trae Templates 源码信源
---

## Web 前端模板总览

web-frontend 分类包含 8 个模板，覆盖从零构建工具的纯静态页面到现代前端框架的完整生态：

| 模板 | 技术栈 | 构建工具 | TypeScript | 开发端口 |
|------|--------|----------|------------|----------|
| web-basic | HTML/CSS/JS | 无 | 否 | 直接打开文件 |
| react-starter | React 18 | Vite | 否 | localhost:5173 |
| vue-starter | Vue 3 | Vite | 否 | localhost:5173 |
| nextjs-starter | Next.js 14 (App Router) | Next.js | 是 | localhost:3000 |
| nuxtjs-starter | Nuxt 3 | Nuxt | 是 | localhost:3000 |
| svelte-starter | Svelte | Vite | 否 | Vite 默认 |
| angular-starter | Angular | Angular CLI | 是 | localhost:4200 |
| tailwind-starter | Tailwind CSS + HTML | Tailwind CLI | 否 | 直接打开文件 |

## web-basic：零构建起点

**路径**：`templates/web-frontend/web-basic/`

最简单的前端模板，不依赖任何构建工具，适合快速原型和静态页面。

**文件结构**（5 个文件）：
```
web-basic/
├── index.html    # HTML5 语义化结构
├── style.css     # 基础 CSS reset 和样式
├── script.js     # 空 JS 文件已链接
├── README.md
└── README.zh-CN.md
```

**特性**：
- HTML5 语义化标签（header/main/footer/section 等）
- 基础 CSS reset 消除浏览器默认样式差异
- 空 JS 文件已在 HTML 中通过 `<script>` 引入
- 零配置、零依赖、零安装

**启动**：直接在浏览器打开 `index.html`

## react-starter：Vite + React 18

**路径**：`templates/web-frontend/react-starter/`

基于 Vite 的 React 18 快速启动模板，是最常用的前端起点。

**文件结构**（8 个文件）：
```
react-starter/
├── index.html        # Vite 入口 HTML
├── package.json      # 依赖声明（React 18、Vite、@vitejs/plugin-react）
├── vite.config.js    # Vite 配置（React 插件）
├── src/
│   ├── App.jsx       # 根组件
│   ├── main.jsx      # React 入口
│   └── index.css     # 全局样式（CSS Modules 可用）
├── README.md
└── README.zh-CN.md
```

**技术栈**：React 18、Vite、CSS Modules、Node.js 16+

**npm scripts**：
```bash
npm run dev      # 启动开发服务器（localhost:5173，HMR）
npm run build    # 生产构建（输出到 dist/）
npm run preview  # 预览生产构建
```

**注意**：模板不包含 React Router、状态管理（Redux/Zustand）、测试框架等，需要开发者自行添加。

## vue-starter：Vite + Vue 3

**路径**：`templates/web-frontend/vue-starter/`

基于 Vite 的 Vue 3 启动模板，使用 Composition API。

**文件结构**（8 个文件）：
```
vue-starter/
├── index.html
├── package.json      # 依赖声明（Vue 3、Vite、@vitejs/plugin-vue）
├── vite.config.js    # Vite 配置（Vue 插件）
├── src/
│   ├── App.vue       # 根组件（SFC 单文件组件）
│   ├── main.js       # Vue 入口（createApp）
│   └── style.css     # 全局样式
├── README.md
└── README.zh-CN.md
```

**技术栈**：Vue 3（Composition API）、Vite、CSS、Node.js 16+

**npm scripts**：与 react-starter 相同（dev/build/preview），开发端口 localhost:5173。

## nextjs-starter：Next.js 14 + TypeScript

**路径**：`templates/web-frontend/nextjs-starter/`

Next.js 14 全栈 React 框架模板，使用 App Router 和 TypeScript。

**文件结构**（8 个文件）：
```
nextjs-starter/
├── package.json
├── tsconfig.json         # TypeScript 配置（Module Resolution: Bundler）
├── next.config.mjs       # Next.js 配置
├── .gitignore
├── app/
│   ├── layout.tsx        # 根布局（App Router）
│   └── page.tsx          # 首页组件
├── README.md
└── README.zh-CN.md
```

**技术栈**：React 18、Next.js 14（App Router）、TypeScript

**启动**：
```bash
npm install    # 或 yarn / pnpm install
npm run dev    # localhost:3000
```

**特性**：服务端渲染（SSR）、静态生成（SSG）、API Routes、文件系统路由、App Router 布局系统。模板不包含 app/globals.css 或 components/ 示例目录。

## nuxtjs-starter：Nuxt 3 + TypeScript

**路径**：`templates/web-frontend/nuxtjs-starter/`

Nuxt 3 全栈 Vue 框架模板。

**文件结构**（7 个文件）：
```
nuxtjs-starter/
├── package.json
├── tsconfig.json
├── nuxt.config.ts    # Nuxt 配置
├── app.vue           # 根组件
├── .gitignore
├── README.md
└── README.zh-CN.md
```

**技术栈**：Vue 3、Nuxt 3、TypeScript

**npm scripts**：
```bash
npm run dev      # 开发服务器（localhost:3000，自动导入、HMR）
npm run build    # 生产构建
```

## svelte-starter：Svelte + Vite

**路径**：`templates/web-frontend/svelte-starter/`

Svelte 编译时框架的 Vite 启动模板。

**文件结构**（7 个文件）：
```
svelte-starter/
├── index.html
├── package.json      # Svelte、@sveltejs/vite-plugin-svelte
├── vite.config.js    # Vite 配置（Svelte 插件）
├── src/
│   ├── App.svelte    # 根组件
│   └── main.js       # Svelte 入口
├── .gitignore
├── README.md
└── README.zh-CN.md
```

**技术栈**：Svelte、Vite

**npm scripts**：`npm run dev`（开发）、`npm run build`（生产构建）

**注意**：README 首行存在复制遗留——描述为"This template provides a minimal setup to get React working in Vite"，实际是 Svelte 模板，不影响功能。

## angular-starter：Angular CLI

**路径**：`templates/web-frontend/angular-starter/`

由 Angular CLI 生成的启动模板，使用 standalone 组件模式。

**文件结构**（8 个文件）：
```
angular-starter/
├── package.json
├── tsconfig.json
├── .gitignore
├── src/
│   ├── main.ts                    # 应用入口（bootstrapApplication）
│   └── app/
│       ├── app.component.ts       # 根组件（standalone: true）
│       ├── app.config.ts          # 应用配置（provideRouter 等）
│       └── app.routes.ts          # 路由配置
├── README.md
└── README.zh-CN.md
```

**技术栈**：Angular、TypeScript

**npm scripts**：
```bash
npm start          # 开发服务器（localhost:4200，自动重载）
npm run build      # 生产构建（输出到 dist/）
npm test           # Karma 单元测试
```

## tailwind-starter：Tailwind CSS + HTML

**路径**：`templates/web-frontend/tailwind-starter/`

Tailwind CSS 原子化 CSS 框架的 HTML 启动模板。

**文件结构**（7 个文件）：
```
tailwind-starter/
├── package.json
├── tailwind.config.js    # Tailwind 配置（content 路径）
├── .gitignore
├── src/
│   ├── index.html        # HTML 页面（引入 Tailwind 类名）
│   └── input.css         # Tailwind 指令（@tailwind base/components/utilities）
├── README.md
└── README.zh-CN.md
```

**技术栈**：HTML、Tailwind CSS

**npm scripts**：
```bash
npm run build    # watch 模式编译 CSS，输出到 dist/output.css
```

**启动流程**：
```bash
npm install
npm run build    # 持续监听 input.css 变化
# 在浏览器打开 src/index.html
```

## 前端模板对比与选择

| 场景 | 推荐模板 | 理由 |
|------|----------|------|
| 快速原型/静态页面 | web-basic | 零构建、零配置 |
| React SPA 开发 | react-starter | Vite 极速 HMR、生态最广 |
| Vue SPA 开发 | vue-starter | Composition API、简洁直观 |
| React SSR/全栈/SEO | nextjs-starter | App Router、性能最佳 |
| Vue SSR/全栈/SEO | nuxtjs-starter | 自动导入、约定优于配置 |
| 轻量/编译时/小体积 | svelte-starter | 无虚拟 DOM、运行时极小 |
| 企业级/TypeScript/大团队 | angular-starter | 完整框架、强约定 |
| 快速样式原型 | tailwind-starter | 原子化 CSS、无需写自定义 CSS |

## 最小可用设计在前端模板中的体现

所有 8 个前端模板都遵循"最小可用"原则：
- react-starter/vue-starter 不包含 router/store/test 配置
- nextjs-starter/nuxtjs-starter 不包含示例 components 目录
- 不提供 eslint/prettier 配置
- 不包含 lock 文件
- 单文件/少文件入口，结构清晰

这种设计让 AI Agent 基于模板生成代码时不会被多余脚手架干扰，开发者按需添加路由、状态管理、测试等依赖。

## 相关概念

- [五维分面分类体系](01-template-classification.md)
- [后端服务模板](03-backend-templates.md)
- [工具与 DevOps 模板](06-tools-devops-templates.md)
- [AGENTS.md 开发契约](07-agents-contract.md)

## 相关内容

- [源码信源索引](../references/templates-source.md)
- [使用 Next.js 模板创建项目](../examples/use-nextjs-template.md)
