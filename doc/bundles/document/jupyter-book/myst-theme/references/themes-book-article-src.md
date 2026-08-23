---
type: reference
title: "themes/book �?themes/article 源码"
description: "Remix SSR 主题应用的结构、路由、组件和 loader 逻辑"
source_path: "external/libs/ai/jupyter-book/myst-theme/themes/"
key_exports:
  - themes/book（书籍主题）
  - themes/article（文章主题）
  - Remix 文件路由
  - loaders.server.ts（数据加载）
facts: [F-025, F-026, F-027, F-028, F-029]
tags: [myst-theme, reference]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/myst-theme/"
    facts: []
---

# Book �?Article 主题源码

## 主题目录结构（以 book 为例�?
```
themes/book/
├── app/
�?  ├── components/
�?  �?  ├── ArticlePage.tsx       # 文章页面布局
�?  �?  ├── Banner.tsx            # 顶部公告横幅
�?  �?  ├── Footer.tsx            # 页脚
�?  �?  ├── SidebarFooter.tsx     # 侧边栏页�?�?  �?  └── (其他 UI 组件)
�?  ├── routes/
�?  �?  ├── $.tsx                 # 根布局路由（catch-all�?�?  �?  ├── myst-theme[.css].ts   # CSS 静态资源路�?�?  �?  ├── api.theme.ts          # 主题 API
�?  �?  ├── sitemap[.xml].ts      # SEO sitemap
�?  �?  ├── robots[.txt].ts       # robots.txt
�?  �?  └── ($project)/
�?  �?      └── _.($a).($b).($c).($d).$slug[.json].tsx  # 多项目页面路�?�?  ├── utils/
�?  �?  ├── loaders.server.ts     # 服务器端数据加载
�?  �?  └── (其他工具)
�?  ├── entry.client.tsx          # Remix 客户端入�?�?  ├── entry.server.tsx          # Remix 服务器入�?�?  └── root.tsx                  # 根组件（HTML 骨架�?├── styles/
�?  ├── app.css                   # 主题�?CSS
�?  └── grid-system.css           # 网格系统
├── public/                       # 静态资�?├── tailwind.config.js
├── remix.config.dev.js           # 开�?Remix 配置
├── remix.config.prod.js          # 生产 Remix 配置
├── server.js                     # Express 生产服务�?├── package.json
└── template.yml                  # MyST 主题模板配置
```

## Remix 路由模式

### Book 主题路由

- `$.tsx`（catch-all root）：应用根布局，包�?HTML 头部、全局 Provider、导航框�?- `($project)/_.($a).($b).($c).($d).$slug[.json].tsx`：多项目动态路�?  - `($project)` 可选项目参数（括号表示可选段�?  - `_` splat route 匹配任意路径
  - `($a).($b).($c).($d)` 可选路径段（最�?4 层深度）
  - `$slug` 页面 slug
  - `[.json]` 可�?`.json` 后缀（用�?API 请求�?- `myst-theme[.css].ts`：返回编译后的主�?CSS
- `api.theme.ts`：主�?API（元数据、导航等�?- `sitemap[.xml].ts` / `robots[.txt].ts`：SEO 文件

### Article 主题路由

Article 主题路由更简洁，没有多项目嵌套：
- 直接的页面路由（�?`($project)/` 前缀�?- 同样�?`$.tsx` 根布局�?myst-theme CSS 路由
- 文章内容通过单页组件渲染

## loaders.server.ts：服务器端数据加�?
两个主题都有 `app/utils/loaders.server.ts`，负责：
- �?MyST 构建输出加载站点数据（JSON 格式�?- 解析当前路径对应的页面内�?- 构建导航结构（目录、侧边栏、面包屑�?- 提供 SEO 元数据（title、description、og tags�?- 处理跨项目引用解�?- 返回 frontmatter、references、headings 等页面数据给客户�?
## 根组件结构（root.tsx�?
```tsx
// themes/book/app/root.tsx 简化结�?export default function App() {
  return (
    <html lang="en" className={dark ? 'dark' : ''}>
      <head>
        <Meta />
        <Links />
        {/* analytics, favicon, fonts */}
      </head>
      <body>
        <ThemeProvider>
          <SiteProvider>
            <BannerProvider>
              <Banner />
              <TopNav />
              <div className="book-layout">
                <PrimarySidebar />
                <main>
                  <Outlet />  {/* 页面内容 */}
                </main>
              </div>
              <Footer />
            </BannerProvider>
          </SiteProvider>
        </ThemeProvider>
        <ScrollRestoration />
        <Scripts />
        <LiveReload />
      </body>
    </html>
  );
}
```

Article 主题类似，但省略�?PrimarySidebar，布局更简洁�?
## template.yml：MyST 主题模板

```yaml
# themes/book/template.yml
template: book
build:
  engine: remix
```

定义该目录是一�?MyST 主题模板，由 myst CLI 使用�?
## 开发与构建命令

```bash
# Book 主题开�?pnpm theme:book   # turbo run dev --parallel --env-mode=loose --filter='./themes/book'

# Article 主题开�?pnpm theme:article

# 构建
pnpm build        # turbo run build（含 packages �?themes�?
# 编译 packages（tsc�?pnpm compile      # turbo run compile
```
