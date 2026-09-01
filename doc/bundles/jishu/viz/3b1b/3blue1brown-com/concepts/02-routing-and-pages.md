---
type: Concept
title: 路由与 SSG 预渲染
description: React Router v7 框架模式路由系统详解、ssr:false 纯预渲染配置、prerender 动态路由收集、root.tsx 根布局、页面组件模式与 Next.js 对比。
tags: [3blue1brown, routing, ssg, prerender, react-router, ssr, spa, root.tsx, loader]
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

# 路由与 SSG 预渲染

React Router 框架模式（v7/v8）提供了与 Next.js 类似的 Meta 框架能力——文件系统路由、布局嵌套、数据加载、错误边界——但它保持了"可选增强"的设计哲学：你可以只用到自己需要的特性。3Blue1Brown.com 选择了其中的"纯预渲染（SSG）"模式，完全禁用 SSR，所有页面在构建时生成静态 HTML。

## React Router 框架模式 vs SPA 模式

很多人对 React Router 的印象停留在"SPA 路由库"——但 v7 之后 React Router 提供了两种使用模式：

| 模式 | 定位 | 特点 | 适用场景 |
|------|------|------|----------|
| **SPA 模式**（传统） | 客户端路由库 | `BrowserRouter` + `Routes` + `Route` 手动配置；纯客户端渲染，无构建时优化；一个 HTML 入口，JS 渲染所有内容 | 后台管理系统、登录后应用、强交互 Web App |
| **框架模式**（v7+） | 全栈 Meta 框架 | 基于 Vite 的 `app/` 目录约定；文件系统路由；支持 SSR/SSG/SPA 混合；`loader`/`action` 数据加载；`root.tsx` 根布局；错误边界；类型生成 | 内容站点、营销页、博客、文档站（即 3Blue1Brown 的选择） |

3Blue1Brown.com 明确使用框架模式——目录结构遵循 `app/` 约定（F-023），使用 `react-router dev`/`react-router build` 命令（F-002、F-003），通过 `react-router.config.ts` 配置框架行为。

## 核心配置：ssr: false 纯预渲染

`react-router.config.ts` 是框架模式的配置文件，其中最关键的一行是（F-039）：

```ts
// react-router.config.ts
import type { Config } from "@react-router/dev/config";

export default {
  ssr: false,  // 完全禁用服务端渲染
  async prerender() {
    // 构建时收集所有需要预渲染的路由
    // ...
  },
} satisfies Config;
```

### ssr: false 意味着什么？

设置 `ssr: false` 后（洞察 I-01）：

1. **无 Node.js 服务器运行时**：构建产物是纯静态 HTML/CSS/JS，可部署到任意静态托管（Netlify、Cloudflare Pages、GitHub Pages、Nginx、S3 等）（F-130）
2. **构建时生成所有 HTML**：每个路由对应一个 `.html` 文件，CDN 可缓存到边缘节点，首屏加载极快
3. **客户端水合（Hydration）**：HTML 发送到浏览器后，React 仍然会下载 JS 进行水合，使页面可交互——这和 Next.js 的 SSG 输出本质相同
4. **无 RSC（React Server Components）**：所有组件都是客户端组件，不需要 `"use client"` 指令，没有服务端/客户端组件的边界复杂度

这与 Next.js 的 `output: "export"` 静态导出功能等价，但 React Router 框架模式的设计更简单——静态导出不是"可选功能"，而是框架的一等公民模式。

## prerender：动态路由静态化

对于静态路由（如 `/about`、`/extras`），React Router 可自动发现并预渲染。但**动态路由**（路径中带参数，如 `/lessons/:id`）需要在 `prerender` 函数中显式告诉框架要渲染哪些路径（F-040）。

3Blue1Brown 的 prerender 实现：

```ts
// react-router.config.ts（简化示意）
async function prerender() {
  // 1. 静态路由（自动收集，但显式列出更清晰）
  const staticRoutes = [
    "/", "/about", "/extras", "/talent", "/testbed", "/sitemap.xml"
  ];

  // 2. 动态路由：通过 import.meta.glob 在构建时收集所有 MDX 文件
  // eager: true 表示构建时直接导入，不懒加载
  const lessons = import.meta.glob("./app/pages/lessons/20[0-9][0-9]/**/index.mdx", {
    eager: true
  });
  const talent = import.meta.glob("./app/pages/talent/**/index.mdx", { eager: true });
  const blog = import.meta.glob("./app/pages/blog/**/index.mdx", { eager: true });

  // 3. 从文件路径派生路由参数
  const lessonRoutes = Object.keys(lessons).map((path) => {
    // ./app/pages/lessons/2016/linear-transformations/index.mdx
    // → /lessons/linear-transformations
    const slug = path.split("/").slice(-2, -1)[0];
    return `/lessons/${slug}`;
  });

  // 4. 合并所有路由 + 404
  const allRoutes = [
    ...staticRoutes,
    ...lessonRoutes,
    ...talentRoutes,
    ...blogRoutes,
    "/404"
  ];

  // 5. 导出路由列表供 E2E 测试使用
  await fs.writeFile("./tests/routes.json", JSON.stringify(allRoutes, null, 2));

  return allRoutes;
}
```

**关键技术点**：
- `import.meta.glob(pattern, { eager: true })` 是 Vite 提供的构建时批量导入功能，在构建阶段扫描文件系统匹配模式，不是运行时 API
- 课程目录按年份组织（`2015/`、`2016/`...），glob 模式 `20[0-9][0-9]` 匹配 2000-2099 年份（F-029）
- 路由列表写入 `tests/routes.json`（F-041），Playwright E2E 测试遍历所有路由验证页面可访问

## 路由定义：app/routes.ts

路由映射表在 `app/routes.ts` 中定义，使用框架模式提供的 `index` 和 `route` 辅助函数（F-042）：

```tsx
// app/routes.ts
import { index, route } from "@react-router/dev/routes";

export default [
  // 首页：/
  index("pages/home/Home.tsx"),

  // 动态路由：/lessons/:id
  route("lessons/:id", "pages/lessons/Lesson.tsx"),

  // 静态路由：MDX 直接作为路由组件
  route("about", "pages/about/About.mdx"),
  route("extras", "pages/extras/Extras.tsx"),
  route("talent", "pages/talent/Talent.tsx"),
  route("talent/:id", "pages/talent/Partner.tsx"),
  route("blog/:id", "pages/blog/Post.tsx"),
  route("testbed", "pages/testbed/Testbed.mdx"),
  route("sitemap.xml", "sitemap.xml.ts"),

  // 通配符路由：匹配所有未命中路径，显示 404
  route("*", "pages/NotFound.tsx"),
] satisfies RouteConfig;
```

（F-043 ~ F-046）

### 路由定义辅助函数

| 函数 | 用法 | 作用 |
|------|------|------|
| `index(file)` | `index("pages/home/Home.tsx")` | 定义根路径 `/` 对应的页面组件 |
| `route(path, file)` | `route("lessons/:id", "pages/lessons/Lesson.tsx")` | 定义路由，支持 `:param` 动态参数 |
| `route("*", file)` | `route("*", "pages/NotFound.tsx")` | 通配符路由，必须放在最后，匹配所有未命中路径 |

### 路由参数获取

动态路由参数（如 `/lessons/:id` 中的 `id`）通过 React Router 的 `useParams` Hook 或路由组件 Props 获取。3Blue1Brown 使用类型生成（typegen）功能（F-107）：

```tsx
// app/pages/lessons/Lesson.tsx
import type { Route } from "./+types/Lesson";  // 自动生成的类型

export default function Lesson({ params }: Route.ComponentProps) {
  const { id } = params;  // id 类型为 string，有完整类型提示
  // ...
}
```

`./+types/Lesson` 是 React Router dev 服务器自动生成的类型文件，包含路由参数、loader 数据、action 数据等类型信息。

### MDX 直接作为路由组件

一个有趣的特性是：`.mdx` 文件可以直接作为路由组件（F-045），不需要写一层 TSX 包装：

```ts
route("about", "pages/about/About.mdx"),  // 直接指向 .mdx 文件
```

React Router 框架模式知道如何处理 MDX 文件（通过 vite.config.ts 中的 MDX 插件链配置），MDX 导出的 default 组件会被直接作为路由页面渲染。

## root.tsx：根布局与全局结构

`app/root.tsx` 是整个应用的根组件，负责渲染 HTML 文档结构、全局布局、错误边界等（F-047 ~ F-054）。这是 React Router 框架模式的约定文件——每个应用必须有一个。

### root.tsx 的核心结构

```tsx
// app/root.tsx（简化示意）
import "~/styles.css";
import "@fontsource-variable/figtree";
// ... 其他字体导入

import { IconContext } from "@phosphor-icons/react";
import { Outlet, useLocation, Links, Scripts, ScrollRestoration } from "react-router";

export default function App() {
  // 路由变化时的滚动处理（F-049）
  const location = useLocation();
  // ... hash 滚动、滚动到锚点逻辑

  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* 暗模式 FOUC 预防脚本：必须在 <head> 最前面执行 */}
        <script dangerouslySetInnerHTML={{ __html: loadDarkMode }} />
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Links />  {/* React Router 管理的 link 标签 */}
      </head>
      <body>
        {/* 无障碍跳转链接 */}
        <a href="#main-content" className="skip-link">Skip to content</a>

        {/* 子路由渲染出口：嵌套路由的内容在这里渲染 */}
        <Outlet />

        {/* 全局组件：不在 Outlet 内部，所有页面都显示 */}
        <ViewCorner />
        <Navigate />
        <MathJax />        {/* 数学公式渲染（不渲染DOM，只执行副作用） */}
        <Celebrate />      {/* 庆祝动画 */}

        {/* 滚动恢复：getKey 基于 pathname，hash 变化不恢复滚动位置 */}
        <ScrollRestoration getKey={(location) => location.pathname} />

        <Scripts />  {/* React Router 管理的 script 标签 */}
      </body>
    </html>
  );
}
```

（F-050 ~ F-052）

### 关键技术细节

1. **`<html>` 和 `<body>` 标签在 React 中渲染**：框架模式下，root.tsx 负责渲染完整的 HTML 文档结构，包括 `<html>`、`<head>`、`<body>`，这和传统 SPA 只有一个 `<div id="root">` 不同。`suppressHydrationWarning` 用于暗模式——因为 dark 类在水合前已由内联脚本设置，React 水合时会看到属性不匹配，这个属性抑制警告。

2. **暗模式 FOUC 预防**（F-052）：在 `<head>` 中使用 `<script dangerouslySetInnerHTML>` 注入内联脚本，在 HTML 解析阶段立即执行：
   ```ts
   // DarkMode.tsx 导出的 load 脚本（F-076）
   const load = `
     if (localStorage.getItem("dark-mode") === "true") {
       document.documentElement.classList.add("dark");
     }
   `;
   ```
   如果等 React 水合后再设置 dark 类，用户会看到短暂的白屏闪烁（FOUC，Flash of Unstyled Content）。内联脚本在浏览器解析到 `<head>` 时立即执行，在页面渲染前就设置好 dark 类。

3. **`<Outlet />`**：子路由渲染出口，类似于 Next.js 的 `{children}` 或 Vue Router 的 `<router-view />`。当前路由匹配的页面组件（Home、Lesson、About 等）在这里渲染。

4. **`<Links />` 和 `<Scripts />`**：React Router 框架管理的资源标签，框架自动注入路由拆分所需的 CSS/JS 预加载、预取等资源标签。

5. **ScrollRestoration**（F-051）：路由切换时恢复滚动位置。`getKey` 配置基于 `pathname`（不含 hash），意味着同页面不同 hash（锚点跳转）不会触发滚动恢复——这是正确的，因为锚点跳转是页面内导航，不需要恢复位置。

## 错误边界：ErrorBoundary

root.tsx 还导出 `ErrorBoundary` 组件处理子路由中未捕获的错误（F-053）：

```tsx
// app/root.tsx
export function ErrorBoundary() {
  const error = useRouteError();
  return (
    <html lang="en">
      <head><title>Error</title></head>
      <body>
        <main>
          <h1>Something went wrong</h1>
          <p>{error.message}</p>
          {error.stack && <pre>{error.stack}</pre>}
          <a href="https://github.com/3b1b/3blue1brown.com/issues/new">
            Report this issue on GitHub
          </a>
        </main>
        <Scripts />
      </body>
    </html>
  );
}
```

当任何子路由在渲染、loader、action 中抛出错误且没有自己的 ErrorBoundary 时，错误会冒泡到根 ErrorBoundary，展示友好的错误页面而非白屏。

## 生产构建优化：vite:preloadError 处理

root.tsx 还有一个容易被忽略但很重要的生产优化（F-054）：

```tsx
useEffect(() => {
  window.addEventListener("vite:preloadError", (event) => {
    event.preventDefault();
    // 使用 sessionStorage 去重，避免无限刷新循环
    if (!sessionStorage.getItem("reloaded")) {
      sessionStorage.setItem("reloaded", "true");
      window.location.reload();
    }
  });
}, []);
```

**解决的问题**：部署新版本后，旧的 JS chunk 文件名（含 hash）不再存在（被新的替换），但用户浏览器中可能还缓存着旧的 HTML，尝试加载旧 chunk 时 404——这会导致页面白屏。监听 `vite:preloadError` 事件，发生时强制刷新页面获取新 HTML，使用 sessionStorage 标记防止无限刷新循环。

## 页面组件模式：以 Lesson.tsx 为例

页面组件是路由直接渲染的组件，放在 `app/pages/` 对应目录下。课程详情页 `Lesson.tsx` 是最复杂的页面，展示了页面组件的典型模式（F-107 ~ F-115）：

```tsx
// app/pages/lessons/Lesson.tsx（简化示意）
import type { Route } from "./+types/Lesson";
import { use } from "react";
import { Meta } from "@react-router/dev/components";
import { getFullLesson } from "./lessons";

export default function Lesson({ params }: Route.ComponentProps) {
  const { id } = params;

  // 使用 React 19 use() API 直接消费异步 import 的 Promise（F-108）
  // getFullLesson 返回 Promise<{ default: Component, frontmatter, ... }>
  const lesson = use(getFullLesson(id));
  const { default: Component, title, video, description, credits } = lesson;

  return (
    <>
      {/* SEO Meta 标签 + JSON-LD 结构化数据（F-109） */}
      <Meta>
        <title>{title} | 3Blue1Brown</title>
        <meta name="description" content={description} />
        <script type="application/ld+json">{/* Article + VideoObject JSON-LD */}</script>
      </Meta>

      <Header />

      <Main className="striped">
        <article>
          {/* 视频区域：有 video 显示 YouTube，否则显示封面图（F-111） */}
          {video ? <YouTube id={video} /> : <Image image={lesson.image} />}

          {/* 自动目录组件（F-112） */}
          <TableOfContents />

          {/* MDX 内容：直接渲染 MDX 转换后的 React 组件（F-113） */}
          <Component />

          {/* 前后课程导航卡片（F-114） */}
          <nav className="prev-next">
            {prev && <Card lesson={prev} direction="prev" />}
            {next && <Card lesson={next} direction="next" />}
          </nav>

          {/* 赞助者感谢区：ShowPartial 折叠/展开（F-115） */}
          {patrons && (
            <section className="patrons bg-secondary/10">
              <ShowPartial>
                <PatronsGrid patrons={patrons} />
              </ShowPartial>
            </section>
          )}
        </article>
      </Main>

      <Footer />
    </>
  );
}
```

### 页面组件的典型特征

1. **类型安全**：从 `./+types/Lesson` 导入自动生成的 `Route` 类型，`params`、`loaderData` 等都有完整类型提示（F-107）
2. **React 19 `use()` API**（F-108）：直接消费 Promise，不需要 `useEffect` + `useState` 手动管理异步状态，也不需要 `<Suspense>` 包裹每层
3. **MDX 作为组件**：MDX 文件导入后，`default` 导出就是一个 React 组件，直接 `<Component />` 渲染（F-113）
4. **SEO 处理**：使用 `<Meta>` 组件设置页面标题、描述，注入 JSON-LD 结构化数据（F-109）
5. **striped 交替背景**：`<Main className="striped">` 配合 CSS `main.striped > section:nth-of-type(odd)` 实现奇数 section 交替背景色（F-110）

## 与 Next.js 的对比

React Router 框架模式和 Next.js 有很多相似概念，但也有关键差异：

| 概念 | React Router 框架模式 | Next.js |
|------|----------------------|---------|
| 应用目录 | `app/` | `app/` |
| 根布局 | `app/root.tsx` | `app/layout.tsx` |
| 路由定义 | `app/routes.ts` 手动配置（或文件系统约定插件） | 文件系统路由（`app/xxx/page.tsx`） |
| 动态参数 | `:param` 语法（`route("lessons/:id", ...)`） | `[param]` 文件夹命名 |
| 数据加载 | `loader` 函数导出 | `async` 组件直接 `fetch`（Server Components） |
| SSG 配置 | `ssr: false` + `prerender()` 返回路由列表 | `generateStaticParams()` |
| SSR | 默认开启，可 `ssr: false` 关闭 | 默认开启，可 `dynamic = "force-static"` |
| 部署目标 | 任意静态托管 / Node 服务器 / 边缘 | Vercel 优先，支持 Node/边缘但自托管复杂 |
| RSC | 无（所有组件都是客户端） | 一等公民，默认 Server Component |
| 构建工具 | Vite | Turbopack（Webpack 兼容） |
| 锁定程度 | 轻量，可迁移性强 | 深度生态绑定，迁移成本高 |

### 核心差异的本质

Next.js 是一个"全功能 batteries-included 框架"，默认假设你需要 SSR/RSC/ISR 等全套能力；React Router 框架模式是一个"可选增强"的元框架——你可以只用自己需要的部分。对于 3Blue1Brown.com 这种纯内容站点，SSR 和 RSC 都是不必要的复杂度，React Router 框架模式让你可以"关掉"这些特性，得到一个极简的纯 SSG 架构。

## 路由相关 Checklist

- [ ] 理解 React Router 框架模式 vs 传统 SPA 模式的区别
- [ ] 理解 `ssr: false` 意味着纯静态输出，无 Node.js 运行时依赖
- [ ] 掌握 `prerender()` 函数如何通过 `import.meta.glob` 收集动态路由
- [ ] 理解 `app/routes.ts` 中 `index()`/`route()`/`route("*")` 的用法
- [ ] 理解 root.tsx 渲染完整 HTML 文档结构、暗模式 FOUC 预防、错误边界的作用
- [ ] 了解 React 19 `use()` API 在页面组件中消费异步 MDX 导入的模式
- [ ] 能对比 React Router 框架模式与 Next.js 的差异和适用场景

## 相关概念

- [00 官网技术栈总览](00-website-overview.md)
- [01 项目结构与目录组织](01-project-structure.md)
- [完整技术栈清单](../references/tech-stack.md)
- [核心组件路径索引](../references/component-index.md)
