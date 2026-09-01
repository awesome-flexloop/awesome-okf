# 概念文档

3Blue1Brown.com 官网前端架构核心概念，共 7 篇，按学习路径组织。

## 架构总览

* [00 官网技术栈总览](00-website-overview.md) — 3Blue1Brown.com 是什么、核心技术选型理由（为什么选 React Router v7 而非 Next.js）、架构特色概览与本地开发快速上手。
* [01 项目结构与目录组织](01-project-structure.md) — 3Blue1Brown.com 完整目录树解析、app/ 目录 React Router 约定、按领域共置原则、关键配置文件职责详解。
* [02 路由与 SSG 预渲染](02-routing-and-pages.md) — React Router v7 框架模式路由系统详解、ssr:false 纯预渲染配置、prerender 动态路由收集、root.tsx 根布局、页面组件模式与 Next.js 对比。

## 内容系统

* [03 MDX内容系统与数学渲染](03-mdx-content-system.md) — 3Blue1Brown.com 的 MDX 内容架构：Vite 插件链配置、frontmatter 元数据系统、两阶段导入性能优化、MathJax 4 双阶段数学渲染、自定义组件映射与课程页面结构。
* [04 核心组件与状态管理](04-components-and-state.md) — 3Blue1Brown.com 的组件架构：Web Components 视频播放器、Jotai 原子状态管理、暗色模式 FOUC 预防、自动目录导航、Heading 锚点系统、React 19 use() API 使用。

## 样式与构建

* [05 Tailwind v4 CSS-first 样式系统](05-styling-with-tailwind4.md) — 3Blue1Brown.com 的 Tailwind CSS v4 零配置架构：@theme 设计令牌、@custom-variant 自定义状态变体、oklch 颜色系统、CSS 变量驱动的暗色模式、@layer base 全局样式、@utility 自定义工具类。
* [06 构建系统、包管理与静态部署](06-build-and-deploy.md) — 3Blue1Brown.com 的工程化体系：Bun 包管理器选型、package.json scripts 全解析、Vite 插件链架构、React Router 预渲染（SSG）配置、TypeScript 严格模式、静态托管部署方案。

```{toctree}
:hidden:
:maxdepth: 7

00-website-overview
01-project-structure
02-routing-and-pages
03-mdx-content-system
04-components-and-state
05-styling-with-tailwind4
06-build-and-deploy
```
