---
type: concept
title: "Remix 路由与 SSR 架构"
description: "myst-theme 使用 Remix 框架的文件路由、loader/action 和 SSR 能力构建文档站点"
tags: [myst-theme, remix, ssr, routing, file-based-routing]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "themes/book/app/"
    facts: [F-025, F-027, F-029]
  - path: "themes/article/app/"
    facts: [F-026]
---

# Remix 路由与 SSR 架构

## 为什么选择 Remix

myst-theme 的两个主题都基于 [Remix](https://remix.run/)（~1.17.0），一个全栈 React 框架。选择 Remix 的关键原因：

1. **SSR 优先**：文档站需要 SEO 和首屏快速渲染，SSR 天然满足
2. **文件路由**：路由结构由文件系统约定，直观且无需配置
3. **Loader/Action 模式**：数据加载和表单提交有清晰的服务端/客户端边界
4. **渐进增强**：JS 未加载时基础功能仍可用
5. **嵌套路由**：Book 主题的多项目层级天然映射到嵌套路由

## 文件路由约定

Remix 的文件路由通过 `app/routes/` 目录下的文件名定义 URL：

| 文件名 | URL 模式 | 说明 |
|--------|---------|------|
| `$.tsx` | `/*`（catch-all） | 根布局，匹配所有路径 |
| `sitemap[.xml].ts` | `/sitemap.xml` | 方括号表示可选段 |
| `robots[.txt].ts` | `/robots.txt` | 同上 |
| `myst-theme[.css].ts` | `/myst-theme.css` | CSS 资源路由 |
| `api.theme.ts` | `/api/theme` | API 端点 |
| `($project)/_.$slug.tsx` | `/:project/*slug` | 可选项目段+splat |

### 路由约定符号

- `$param`：动态参数段（如 `$slug` → `:slug`）
- `($param)`：可选动态段（括号表示）
- `_`：Splat route（匹配剩余所有路径）
- `[param]`：可选字段（如 `[.json]` → 可选 `.json` 后缀）
- 文件夹：路由组（不影响 URL 路径）

## Loader：服务端数据加载

每个路由可以导出 `loader` 函数，在服务端执行并向组件提供数据：

```tsx
// themes/book/app/routes/($project)/_.$slug.tsx
import { json } from '@remix-run/node';
import { useLoaderData } from '@remix-run/react';

export async function loader({ params, request }) {
  const { project, slug } = params;
  // 从构建产物加载页面数据
  const page = await loadPage(project, slug);
  return json({
    mdast: page.mdast,
    frontmatter: page.frontmatter,
    references: page.references,
    nav: await buildNavigation(project),
  });
}

export default function Page() {
  const { mdast, frontmatter } = useLoaderData<typeof loader>();
  return <MyST ast={mdast} />;
}
```

### loaders.server.ts

实际的数据加载逻辑集中在 `app/utils/loaders.server.ts`，职责包括：
- 从 JSON 构建产物读取页面数据
- 路径到文件的映射解析
- 导航树构建（前后页面、面包屑）
- 引用解析（文献、交叉引用、跨项目引用）
- SEO 元数据组装
- 错误处理（页面不存在、项目不存在）

## Action：服务端变更

路由可以导出 `action` 函数处理 POST/PUT/DELETE 请求。myst-theme 中 action 用于：
- 搜索查询
- 主题切换（可选）
- 横幅关闭状态

## 根布局（root.tsx / $.tsx）

根路由定义 HTML 文档骨架：

```tsx
export default function App() {
  return (
    <html lang="en">
      <head>
        <Meta />
        <Links />
      </head>
      <body>
        <ThemeProvider>
          <SiteProvider>
            <Outlet />  {/* 子路由渲染位置 */}
          </SiteProvider>
        </ThemeProvider>
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}
```

`<Outlet />` 是嵌套路由的渲染位置，子路由的内容在这里注入。

## 开发与生产

### 开发模式（remix.config.dev.js）

- 使用 Remix 开发服务器
- 热模块替换（HMR）
- 未压缩的 JS/CSS
- React DevTools 支持

### 生产模式（remix.config.prod.js + server.js）

- `remix build` 编译为静态资源 + 服务端 bundle
- Express 服务器（`server.js`）处理 SSR
- 资源压缩、缓存头
- 可部署到任意 Node.js 宿主

## 与 myst CLI 的集成

myst CLI 的 `start` 命令启动主题开发服务器，`build --html` 生成静态站点。构建过程：
1. MyST 解析和转换所有页面 → JSON 数据
2. Remix 编译器构建主题应用
3. 服务端渲染每个路由为静态 HTML
4. 输出 HTML + JS + CSS 到 `_build/` 目录
