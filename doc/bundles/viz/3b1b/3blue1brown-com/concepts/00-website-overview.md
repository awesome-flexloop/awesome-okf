---
type: Concept
title: 官网技术栈总览
description: 3Blue1Brown.com 是什么、核心技术选型理由（为什么选 React Router v7 而非 Next.js）、架构特色概览与本地开发快速上手。
tags: [3blue1brown, overview, react, react-router, nextjs, ssg, getting-started]
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
  - id: tech-stack
    resource: /references/tech-stack.md
    title: 3Blue1Brown.com 完整技术栈清单
  - id: component-index
    resource: /references/component-index.md
    title: 3Blue1Brown.com 核心组件索引
---

# 官网技术栈总览

3Blue1Brown.com 是 Grant Sanderson（3Blue1Brown）的官方视频网站源码，承载了线性代数、微积分、神经网络等数百个高质量数学科普视频课程与配套交互式内容。该站点是一个"内容优先、工程极简、性能极致"的纯静态内容站点典范，采用 React 19 + React Router v8 + Vite 8 + Tailwind CSS v4 + MDX 构建（F-004 ~ F-008）。

## 核心洞察：为什么选 React Router v7 框架模式而非 Next.js？

在 Next.js 占据 React Meta 框架绝对主流的 2025-2026 年，3Blue1Brown 故意选择了一条"非主流"路线——React Router 框架模式（对应 v7，项目实际使用 v8 后续版本），而非 Next.js/App Router（洞察 I-01）。这不是技术偏好问题，而是基于内容站点本质的理性选择：

### 反常识的选型逻辑

**内容站点根本不需要 SSR/ISR/RSC**。3Blue1Brown.com 的所有内容——课程视频、博客文章、课程介绍——都是构建时已知的静态 MDX 文件，不存在用户登录、个性化推荐、实时数据等需要服务端动态渲染的场景。

明确设置 `ssr: false` 完全禁用服务器端渲染（Server-Side Rendering, SSR）（F-039），通过 `prerender` 函数在构建时用 `import.meta.glob` 收集所有路由——包括动态路由 `/lessons/:id`、`/blog/:id`、`/talent/:id`——全部预渲染（Prerendering，即 SSG，Static Site Generation）为静态 HTML（F-040），最终部署到 Netlify，产物为纯静态文件，**无 Node.js 服务器运行时依赖**（F-130）。

### 不选 Next.js 的三个具体理由

1. **避免 Vercel 生态锁定**：Next.js 深度绑定 Vercel 部署平台，自托管或部署到其他平台会遇到各种问题；React Router 框架模式产出标准静态文件，可部署到任意静态托管服务（Netlify、Cloudflare Pages、GitHub Pages、Nginx 等）。

2. **避免 RSC 的复杂度**：React Server Components 带来了全新的心智模型、序列化边界、`"use client"` 指令等复杂度，而纯内容站点完全用不到这些特性——所有组件都在客户端运行，不需要服务端组件的数据获取能力。

3. **架构更轻量**：React Router 框架模式本质上是"路由 + 约定 + Vite 插件"，没有 Next.js 那么多层抽象；对于纯内容站点，"文件系统路由 + 构建时预渲染"这两个 Next.js 最有吸引力的特性，React Router v7 已经完整提供。

## 架构特色概览

3Blue1Brown.com 的架构围绕"构建速度快、首屏加载快、维护成本低"三个目标设计，有六大核心特色：

### 1. 纯 SSG 预渲染（ssr: false）

禁用所有服务端渲染，构建时遍历所有 MDX 内容生成静态 HTML，每个页面都是独立的 `.html` 文件，CDN 可缓存到边缘节点，首屏加载速度极快。动态路由（如 `/lessons/linear-transformations`）在构建时已知，通过 `import.meta.glob` 收集后批量预渲染（F-040）。

### 2. MDX 双阶段数学渲染

数学公式不采用常见的"构建时 KaTeX 渲染"方案，而是"构建时标记 + 运行时 CDN 渲染"双阶段策略（洞察 I-03）：
- **构建时**：remark-math 仅将 `$...$` 和 `$$...$$` 标记为 `<code class="language-math">` 元素，不做实际渲染（显著提升构建速度）
- **运行时**：客户端从 CDN 加载 MathJax 4，通过 MutationObserver 监听 DOM 变化，手动调用 `tex2svg` 将数学代码转换为高质量 SVG

这种方案既解决了构建时渲染数学导致编译速度慢的问题，又利用了 MathJax SVG 渲染质量优于 KaTeX 的优势，同时 CDN 加载可跨站点复用缓存。

### 3. Web Components 视频播放器

YouTube/Vimeo 播放器不用 React 组件封装 SDK，而是直接使用 `youtube-video-element` 和 `vimeo-video-element` 这两个 Custom Elements（自定义元素，Web Components 标准）（洞察 I-04）。它们镜像原生 `<video>` API——会用原生 `<video>` 就会用 `<youtube-video>`，不需要学习新的 React 封装 API；Custom Elements 生命周期与 React 无关，不会因 React 重渲染导致播放器重新加载。

### 4. Jotai 原子化状态管理

全局状态使用 Jotai（F-010）而非 Redux/Zustand/Context API：
- `videoPlayingAtom`：单个布尔原子跟踪站点是否有视频正在播放，实现"一个视频播放时自动停止其他视频"的互斥逻辑（F-069）
- `darkModeAtom`：`atomWithStorage` 持久化暗模式偏好到 localStorage（F-073）
- `headingsAtom`：页面标题列表，供 TableOfContents 自动生成目录（F-084）
- `openAtom`：移动端导航菜单开关状态（F-078）

原子模型的优势在于：单个状态对应单个原子，不需要 reducer/action/selector 这些仪式感代码，按需订阅不会导致无关组件重渲染。

### 5. Tailwind v4 CSS-first 零配置

完全抛弃 Tailwind v3 的 JS 配置文件（tailwind.config.js），采用 Tailwind CSS v4 的 CSS-first 配置模式（洞察 I-02）：
- `@theme` 块在 CSS 中定义设计令牌：断点、字体、字重、oklch 颜色系统
- `@custom-variant` 定义自定义状态变体：`dark`（暗模式）、`playing`（视频播放中）、`hocus`（hover 或 focus-visible 复合状态）
- `@utility` 定义自定义工具类：宽度控制、图标尺寸、打印隐藏、视频播放淡出等
- 暗模式通过 CSS 变量覆盖实现（`.dark` 类切换颜色变量值），不是 Tailwind 内置的 dark 策略

### 6. MDX frontmatter 与内容分离加载

MDX 内容采用两阶段导入的性能优化模式（洞察 I-05）：
- **列表页**：`import.meta.glob("./**/index.mdx", { eager: true, query: "frontmatter-only" })` 仅导入所有 MDX 的 frontmatter 元数据（标题、日期、描述、缩略图等），JS 体积仅几十 KB
- **详情页**：懒加载 `import.meta.glob("./**/index.mdx")`（无 eager）配合 `importAssetsAsync` 缓存 Promise，使用 React 19 的 `use()` API 按需消费完整 MDX 组件（F-091、F-108）

这一模式利用了 `@mdx-js/rollup` 提供的 `query: "frontmatter-only"` 特殊查询参数，构建时分别生成"仅元数据"和"完整内容"两个产物，完美解决了"列表页需要所有文章标题但不需要内容"的性能矛盾。

## 前置知识要求

学习本项目源码需要以下基础知识：

- **React 基础**：函数组件、Hooks（useState/useEffect/useRef/useContext）、React 19 新特性 `use()` API
- **TypeScript 基础**：类型标注、接口、泛型，项目启用 `strict: true` 严格模式（F-128）
- **MDX 基础**：Markdown + JSX 的混合写法、frontmatter 元数据、Markdown 组件映射
- **Vite 基础概念**：插件系统、import.meta.glob 批量导入、资源处理
- **Tailwind CSS 基础**：工具类思维，v4 新特性 CSS-first 配置更佳

不要求提前掌握 React Router v7 框架模式、Jotai、Custom Elements 等——这些会在后续概念文档中详细讲解。

## 本地开发快速启动

项目首选 Bun 作为包管理器（F-129），但所有命令兼容 npm/yarn/pnpm。

### 环境要求

- Bun 1.0+（推荐）或 Node.js 18+
- Git

### 启动步骤

```bash
# 1. 克隆仓库
git clone https://github.com/3b1b/3blue1brown.com.git
cd 3blue1brown.com

# 2. 安装依赖（bun）
bun install

# 或使用 npm
npm install

# 3. 启动开发服务器
bun dev

# 或使用 npm
npm run dev
```

开发服务器启动在端口 **31415**（π 的前几位，3B1B 特色），启动时自动打开浏览器（F-002）：

```bash
# 开发命令（package.json）
react-router dev --open --port 31415
```

### 常用命令

```bash
# 生产构建（产物输出到 build/client/）
bun run build

# 本地预览生产构建
bun run preview
# 等价于：bunx serve ./build/client -p 31415
```

构建完成后，`build/client/` 目录包含纯静态 HTML/CSS/JS 文件，可直接部署到任意静态托管服务。

## 技术栈全景图

| 层级 | 技术选型 | 版本 | 核心作用 |
|------|----------|------|----------|
| UI 框架 | React | ^19.2.7 | 组件化 UI 渲染 |
| Meta 框架 | React Router | ^8.2.0 | 路由、预渲染、文件约定 |
| 构建工具 | Vite | ^8.1.5 | 开发服务器、生产构建 |
| 样式方案 | Tailwind CSS | ^4.3.3 | CSS-first 零配置工具类 |
| 内容格式 | MDX + Remark | ^3.1.1 | Markdown + JSX 混合内容 |
| 数学渲染 | MathJax | 4（CDN） | 运行时 TeX → SVG 转换 |
| 状态管理 | Jotai | ^2.20.2 | 原子化全局状态 |
| 视频播放 | Custom Elements | - | youtube/vimeo-video-element 镜像原生 video API |
| 3D/可视化 | Three.js + R3F + D3 + GSAP + p5 | - | 课程中的交互式演示 |
| 包管理 | Bun（首选） | - | 兼容 npm/yarn 的快速包管理 |
| 部署目标 | Netlify | - | 静态文件托管，无 Node 运行时 |

完整依赖清单见 [完整技术栈清单](../references/tech-stack.md)。

## 学习路径建议

```
入门（1小时跑通本地开发）：
  本文档 → 01-项目结构 → 02-路由与SSG预渲染
       ↓
核心（3小时理解内容系统骨架）：
  03-MDX内容系统 → 04-核心组件与状态 → 05-Tailwind v4样式
       ↓
进阶（掌握构建部署）：
  06-构建配置与部署 → examples/ 动手实践
```

## 相关概念

- [01 项目结构与目录组织](01-project-structure.md)
- [02 路由与 SSG 预渲染](02-routing-and-pages.md)
- [完整技术栈清单](../references/tech-stack.md)
- [核心组件路径索引](../references/component-index.md)
