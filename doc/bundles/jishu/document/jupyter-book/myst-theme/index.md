---
type: bundle
title: "myst-theme 主题系统"
okf_version: "0.2"
---

# myst-theme：MyST 主题系统

myst-theme 是 MyST 生态的主题和渲染层，提供 Book（多页面文档站）和 Article（单页文章）两个基于 Remix SSR 的主题，以及一套完整的 React 组件库（MDAST→React 渲染器、Provider 系统、Jupyter 集成组件）和 CSS 变量驱动的样式系统。

## 架构核心

myst-theme 采用**三层分离**架构：

1. **styles/ 层（CSS 基础）**：CSS 自定义属性（`--myst-color-*`）、Tailwind 扩展、网格模板
2. **packages/ 层（React 组件库）**：14 个 `@myst-theme/*` 包，含 myst-to-react 渲染器、Provider 系统、站点组件、Jupyter 集成
3. **themes/ 层（Remix 应用）**：Book 和 Article 两个具体主题，组合 packages 构建完整站点

## 知识地图

```
myst-theme
├── 样式基础 ──── CSS Variables + Tailwind 扩展 + 命名网格线布局
├── 核心渲染 ──── myst-to-react（MDAST→React 组件映射）
│   ├── 节点组件（admonition/code/heading/math/...）
│   ├── 渲染器覆盖（renderers prop / unist-util-select）
│   └── 扩展（化学式/SI单位/智能链接）
├── Provider 系统 ── Theme/Article/Site/Project/Search/...
├── Jupyter 集成 ── thebe 交互式代码执行、输出渲染
├── Book 主题 ──── 多页面文档站（Remix SSR + 侧边栏导航）
└── Article 主题 ── 单页论文/报告（简洁布局 + 多格式导出）
```

## 文档导航

### 入门示例
- [定制 Book 主题](examples/01-customize-book-theme.md) — CSS 变量品牌化、渲染器替换、站点配置
- [使用 Article 主题发布论文](examples/02-use-article-theme.md) — 学术论文配置、PDF/DOCX 导出

### 核心概念（按学习路径）
1. [主题架构：三层分离与组件组合](concepts/00-theme-architecture.md) — 整体架构和依赖方向
2. [CSS 变量与主题切换](concepts/01-css-variables-theming.md) — 颜色系统和暗色模式
3. [命名网格线响应式布局](concepts/02-grid-layout-system.md) — 学术文档网格系统
4. [MDAST 到 React 的组件渲染](concepts/03-myst-to-react-rendering.md) — 核心渲染机制
5. [React Context Provider 分层](concepts/04-theme-providers.md) — 多层上下文系统
6. [Book 主题](concepts/05-book-theme.md) — 多页面文档站
7. [Article 主题](concepts/06-article-theme.md) — 单页文章
8. [Remix 路由与 SSR](concepts/07-remix-routing.md) — 文件路由和服务端渲染

### 信源参考
- [themes/book 与 themes/article](references/themes-book-article-src.md) — Remix 主题源码
- [myst-to-react 与 providers](references/myst-to-react-providers-src.md) — 渲染和状态源码
- [styles 目录](references/structure-styles-src.md) — CSS 和 Tailwind 配置

### 规格说明
- [事实清单](spec/facts.md) — 50 条编号源码事实
- [架构洞察](spec/insights.md) — 5 个核心洞察与完整知识地图

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
