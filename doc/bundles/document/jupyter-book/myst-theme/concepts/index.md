# Concepts

myst-theme 概念文档按学习路径编号，建议按顺序阅读。

## 主题架构基础

- [00 主题架构：三层分离与组件组合](00-theme-architecture.md) — styles/packages/themes 三层架构、依赖方向、组合模式
- [01 CSS 变量与主题切换](01-css-variables-theming.md) — `--myst-color-*` 颜色系统、暗色模式、品牌定制
- [02 命名网格线响应式布局](02-grid-layout-system.md) — CSS Grid 命名网格线、col-body/page/gutter 布局

## 核心渲染系统

- [03 MDAST 到 React 的组件渲染](03-myst-to-react-rendering.md) — `<MyST>` 组件、节点映射、渲染器覆盖
- [04 React Context Provider 分层](04-theme-providers.md) — Theme/Article/Site/Project 等多层 Provider

## 主题与框架

- [05 Book 主题：多页面文档站点](05-book-theme.md) — Remix SSR、多项目路由、侧边栏导航
- [06 Article 主题：单页文章布局](06-article-theme.md) — 论文/报告布局、frontmatter 渲染
- [07 Remix 路由与 SSR 架构](07-remix-routing.md) — 文件路由、loader/action、SSR 管线

```{toctree}
:maxdepth: 7

00-theme-architecture
01-css-variables-theming
02-grid-layout-system
03-myst-to-react-rendering
04-theme-providers
05-book-theme
06-article-theme
07-remix-routing
```
