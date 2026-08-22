---
type: concept
title: "Book 主题：多页面文档站点"
description: "Book 主题的 Remix 架构、多项目路由、侧边栏导航和完整文档站点功能"
tags: [myst-theme, book-theme, remix, ssr, navigation]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "themes/book/"
    facts: [F-025, F-027, F-028, F-029]
---

# Book 主题：多页面文档站点

## 概述

Book 主题是 myst-theme 的主力主题，面向多页面技术文档、书籍和课程材料。基于 Remix 框架实现 SSR（Server-Side Rendering），提供完整的文档站点体验：侧边栏导航、全文搜索、多项目支持、SEO 优化。

## 目录结构

```
themes/book/
├── app/
│   ├── components/          # 主题级组件
│   │   ├── ArticlePage.tsx  # 文章页面布局（内容+右侧TOC）
│   │   ├── Banner.tsx       # 顶部公告横幅
│   │   ├── Footer.tsx       # 页脚
│   │   ├── SidebarFooter.tsx# 侧边栏底部
│   │   └── NotFound.tsx     # 404 页面
│   ├── routes/              # Remix 文件路由
│   │   ├── $.tsx            # 根布局（catch-all）
│   │   ├── myst-theme[.css].ts  # CSS 资源
│   │   ├── api.theme.ts     # 主题 API
│   │   ├── sitemap[.xml].ts # SEO sitemap
│   │   ├── robots[.txt].ts  # robots.txt
│   │   └── ($project)/      # 多项目路由组
│   │       └── _.($a).($b).($c).($d).$slug[.json].tsx
│   ├── utils/
│   │   └── loaders.server.ts # 服务器端数据加载
│   ├── entry.client.tsx     # 客户端入口
│   ├── entry.server.tsx     # 服务器入口
│   └── root.tsx             # HTML 根组件
├── styles/
│   ├── app.css              # 主题级 CSS
│   └── grid-system.css      # 网格系统
├── public/                  # 静态资源
├── tailwind.config.js
├── remix.config.dev.js
├── remix.config.prod.js
├── server.js                # Express 生产服务器
└── template.yml             # MyST 主题配置
```

## 多项目路由

Book 主题支持在一个站点中托管多个文档项目。路由使用 Remix 的可选段和 splat 路由：

```
/                           → 站点首页
/guide/                     → guide 项目首页
/guide/getting-started      → guide 项目的具体页面
/api/                       → api 项目首页
/api/reference/module       → api 项目的深层页面
```

路由文件 `($project)/_.($a).($b).($c).($d).$slug[.json].tsx` 的含义：

| 段 | 含义 |
|----|------|
| `($project)` | 可选项目名（括号表示可选） |
| `_` | Splat route（匹配剩余路径） |
| `($a).($b).($c).($d)` | 最多 4 层可选路径段 |
| `$slug` | 页面 slug |
| `[.json]` | 可选 `.json` 后缀（API 数据请求） |

`[.json]` 后缀使得同一路由既能渲染 HTML 页面，又能返回 JSON 数据（用于客户端导航）。

## 服务器端数据加载

`loaders.server.ts` 是 Book 主题的数据核心，在每次请求时：

1. 根据 URL 路径解析当前项目和页面 slug
2. 从 MyST 构建输出（JSON 文件）加载页面 MDAST 和 frontmatter
3. 构建导航树（项目 TOC、页面间前后链接）
4. 解析跨项目引用（`[](xref:other-project/page)`）
5. 收集 SEO 元数据（title、description、og tags、canonical URL）
6. 返回数据给路由组件

SSR 确保首屏快速渲染和 SEO 友好，客户端 hydrate 后获得 SPA 导航体验。

## 导航系统

Book 主题提供三层导航：

1. **TopNav（顶部导航栏）**：站点级链接、项目切换器、搜索框、暗色模式切换、GitHub 链接
2. **PrimarySidebar（主侧边栏）**：当前项目的完整 TOC，支持折叠/展开、活动项高亮
3. **InlineTableOfContents（页内目录）**：当前页面的标题树（h2/h3），通常显示在右侧 gutter

## 生产部署

`server.js` 是一个 Express 服务器，用于生产环境：

- 服务端渲染 Remix 应用
- 提供静态资源（CSS、JS、图片）
- 缓存构建产物
- 可部署到 Node.js 宿主、Docker 容器等

开发时使用 Remix 开发服务器（`remix.config.dev.js`），支持热更新。

## template.yml

```yaml
template: book
build:
  engine: remix
```

该文件告诉 myst CLI 这是一个 Book 主题模板，使用 Remix 引擎构建。myst build 时会根据此配置选择主题和构建管线。
