---
type: reference
title: "myst-theme 项目结构与样式系统源码"
description: "monorepo 结构、styles/index.js Tailwind 配置、CSS 变量系统和 CSS 模块"
source_path: "external/libs/ai/jupyter-book/myst-theme/"
key_exports:
  - styles/index.js（Tailwind 配置入口）
  - CSS 模块（typography/code-highlight/proof/grid/jupyter 等）
  - CSS Variables（--myst-color-*）
facts: [F-001, F-002, F-004, F-017, F-018, F-019, F-020, F-021, F-022, F-023, F-024]
tags: [myst-theme, reference]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/myst-theme/"
    facts: []
---

# myst-theme 项目结构与样式系统

## Monorepo 结构

```
myst-theme/
├── packages/           # 可复用 React 组件库（14 个子包）
│   ├── myst-to-react/  # MDAST→React 渲染器
│   ├── providers/      # React Context Provider
│   ├── site/           # 站点级组件（Remix）
│   ├── frontmatter/    # Frontmatter 渲染
│   ├── jupyter/        # Jupyter/thebe 集成
│   ├── diagrams/       # 图表（Mermaid）
│   ├── icons/          # 图标
│   ├── search/         # 搜索核心
│   ├── search-minisearch/  # MiniSearch 实现
│   ├── common/         # 公共类型和工具
│   ├── landing-pages/  # 着陆页组件
│   ├── anywidget/      # AnyWidget 支持
│   └── myst-demo/      # 演示组件
├── themes/             # Remix 主题应用
│   ├── book/           # 书籍/文档主题（多页+侧边栏）
│   └── article/        # 文章主题（单页）
├── styles/             # CSS 样式库（独立包）
│   ├── index.js        # Tailwind 配置入口
│   ├── tailwind.config.js
│   ├── package.json
│   └── *.css           # CSS 模块
└── package.json        # monorepo 根配置（turbo + pnpm workspaces）
```

构建工具链：
- **Turbo**：任务编排（dev/build/compile/lint/test）
- **pnpm workspaces**：包管理
- **Remix**：主题应用的 SSR 框架
- **Tailwind CSS**：样式框架
- **@tailwindcss/typography**：排版插件

## styles/index.js：Tailwind 配置

### content 路径

```js
const content = [
  './app/**/*.{js,ts,jsx,tsx}',
  '../../packages/myst-to-react/{src,dist}/**/*.{js,ts,jsx,tsx}',
  '../../packages/site/{src,dist}/**/*.{js,ts,jsx,tsx}',
  '../../packages/frontmatter/{src,dist}/**/*.{js,ts,jsx,tsx}',
  '../../packages/jupyter/{src,dist}/**/*.{js,ts,jsx,tsx}',
  '../../packages/icons/{src,dist}/**/*.{js,ts,jsx,tsx}',
  '../../packages/landing-pages/{src,dist}/**/*.{js,ts,jsx,tsx}',
  // ...
];
```

同时包含 `node_modules/` 和 `../../packages/` 路径，确保 pnpm 和 submodule 两种使用方式都能正确扫描。

### 颜色系统

约 50 个 CSS 自定义属性，按命名空间分组：

**链接色**：
- `--myst-color-link`、`--myst-color-link-hover`、`--myst-color-link-underline`

**主色/焦点**：
- `--myst-color-primary`、`--myst-color-primary-hover`
- `--myst-color-focus-ring`、`--myst-color-focus-outline`
- `--myst-color-active`、`--myst-color-active-bg`、`--myst-color-active-surface`

**中性色**：
- `--myst-color-bg`、`--myst-color-bg-secondary`（背景）
- `--myst-color-surface`、`--myst-color-surface-hover`（表面）
- `--myst-color-text`、`--myst-color-text-secondary`、`--myst-color-text-tertiary`（文本）
- `--myst-color-prose-body`（排版正文）
- `--myst-color-border`、`--myst-color-border-strong`（边框）
- `--myst-color-inverse-bg`、`--myst-color-inverse-text`（反色）
- `--myst-color-code`、`--myst-color-kbd-shadow`（代码）

**语义色（admonition/proof 等）**：
- `--myst-color-info/info-bg/info-text`
- `--myst-color-success/success-bg/success-text`
- `--myst-color-tip/tip-bg/tip-text`
- `--myst-color-warning/warning-bg/warning-text`
- `--myst-color-danger/danger-bg/danger-text`
- `--myst-color-error/error-bg/error-text`
- `--myst-color-theorem/theorem-bg/theorem-text`
- `--myst-color-example/example-bg/example-text`
- `--myst-color-proof/proof-bg/proof-text`

Tailwind 中注册为 `myst-*` 颜色（如 `bg-myst-info-bg`、`text-myst-link`）。

### 网格模板（gridTemplateColumns）

定义了 3 种布局模式 × 5 种响应式断点 = 15 套网格模板：

| 布局模式 | sm | md | lg | xl | 2xl |
|---------|-----|-----|-----|-----|------|
| article（默认） | article-sm | article-md | article-lg | article-xl | article-2xl |
| article-left（左侧TOC） | article-left-md | article-left-lg | article-left-xl | article-left-2xl |
| article-center（居中） | article-center-sm | article-center-md | article-center-lg | article-center-xl | article-center-2xl |

网格线命名：screen / screen-inset / page / page-inset / body-outset / body / body-inset / gutter-left / middle / gutter-right

### gridColumn 快捷类

映射到命名网格线：
- `col-screen`、`col-screen-inset`、`col-page`、`col-page-inset`
- `col-body`、`col-body-outset`、`col-body-inset`、`col-body-left/right`
- `col-gutter-left/right`、`col-gutter-outset-left/right`
- `col-page-left/right`、`col-screen-left/right`、`col-margin-left/right`

### Typography 覆盖

覆盖 @tailwindcss/typography 的 `--tw-prose-*` CSS 变量指向 myst CSS 变量：
- `--tw-prose-links` → `var(--myst-color-link)`
- `--tw-prose-body` → `var(--myst-color-prose-body)`
- `--tw-prose-code` → `var(--myst-color-code)`
- 移除 code::before/after 的反引号
- 补充 h5/h6 样式
- 调整链接 hover 颜色
- 设置列表项间距（0.25rem）

### 动画

```js
keyframes: {
  load: { '0%': { width: '0%' }, '100%': { width: '50%' } },
  fadeIn: { '0%': { opacity: 0 }, '100%': { opacity: 1 } },
},
animation: {
  load: 'load 2.5s ease-out',
  'fadein-fast': 'fadeIn 1s ease-out',
}
```

### Safelist

包含动态生成的类名防止 Tailwind JIT purge 误删：
- 所有 col-* 网格类
- col-span-* 和 row-span-*
- shaded/framed/shaded-children/rounded-children 工具类
- sphinx-* 类（Sphinx 文档兼容）

## CSS 模块

| 文件 | 用途 |
|------|------|
| app.css | 主应用样式基础 |
| typography.css | 排版增强 |
| code-highlight.css / code-highlight-light.css / code-highlight-dark.css | 代码语法高亮 |
| proof.css | 证明/定理/练习环境 |
| cross-references.css | 交叉引用样式 |
| citations.css | 引用样式 |
| figures.css | 图片/图表 |
| grid.css | 网格布局基础 |
| grid-system.css | 网格系统定义（主题级） |
| details.css | `<details>` 折叠块 |
| tasklists.css | 任务列表复选框 |
| jupyter.css | Jupyter 输出样式 |
| math.css | 数学公式 |
| button.css | 按钮 |
| hover.css | 悬停效果 |
| toc.css | 目录（TOC） |
| search.css | 搜索 UI |
| block-styles.css | 块级元素样式 |
| backmatter.css | 后页/参考文献 |
| ansi.css | ANSI 终端颜色 |
| sphinx.css | Sphinx 域/签名样式 |
| text-spacers.css | 文本间距工具类 |
| landing-pages.css | 着陆页样式 |
