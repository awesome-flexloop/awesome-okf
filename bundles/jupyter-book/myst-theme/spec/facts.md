---
type: facts
bundle: myst-theme
version: "1.3.0"
generated: 2026-08-23
sources:
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\myst-theme\package.json
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\myst-theme\styles\index.js
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\myst-theme\packages\myst-to-react\src\index.tsx
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\myst-theme\packages\providers\src\index.tsx
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\myst-theme\packages\site\src\index.ts
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\myst-theme\themes\book\
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\myst-theme\themes\article\
---

# myst-theme 事实清单

## 项目结构

- F-001：myst-theme 是一个 monorepo（pnpm/turbo 工作空间），包含 packages/（可复用组件库）、themes/（Book 和 Article 两个主题）、styles/（CSS 组件库）三个主要区域。
- F-002：构建工具使用 Turbo 进行任务编排，themes/ 基于 Remix 框架（@remix-run/react ~1.17.0），CSS 使用 Tailwind CSS + @tailwindcss/typography。
- F-003：两个主题：Book（多页面书籍/文档，带侧边栏导航）和 Article（单页文章），均为 Remix 应用。
- F-004：CSS 组件入口为 styles/index.js，定义了 Tailwind 扩展（自定义颜色、网格模板、typography 覆盖、动画），供主题和包使用。

## Packages（packages/）

- F-005：**myst-to-react** — 核心 MDAST→React 组件渲染器，将 MyST AST 节点映射为 React 组件（admonition、card、code、crossReference、dropdown、exercise、footer、grid、heading、image、math、proof、tabs 等）。
- F-006：**providers** — React Context Provider 集合（ArticleProvider、ThemeProvider、TabStateProvider、SiteProvider、ProjectProvider、GridProvider、SearchProvider、LinkProvider、XrefProvider、BaseurlProvider、BannerProvider、UIProvider）。
- F-007：**site** — 站点级组件和 Remix loader：Navigation（TopNav、PrimarySidebar、InlineTableOfContents）、ContentBlocks、FrontmatterParts、Footer、Bibliography、Error 页面（404/ProjectNotFound/DocumentNotFound/Unhandled）、SEO（sitemap、robots、meta、analytics）、themeCSS。
- F-008：**frontmatter** — FrontmatterBlock 组件（Authors、Affiliations、AuthorPopover、Downloads、Licenses、LaunchButton）。
- F-009：**jupyter** — Jupyter 集成组件（Output、Outputs、BinderBadge、ConnectionStatusTray、ErrorTray、NotebookToolbar、execute/ 子模块包含 Reducer/Hooks/Provider 用于 thebe 交互执行）。
- F-010：**diagrams** — Mermaid 等图表渲染组件。
- F-011：**icons** — MyST logo 图标组件。
- F-012：**search** / **search-minisearch** — 搜索功能核心和 MiniSearch 实现。
- F-013：**common** — 公共类型和工具函数。
- F-014：**landing-pages** — 着陆页组件（CenteredBlock、SplitImageBlock、LogoCloudBlock 等）。
- F-015：**anywidget** — AnyWidget Jupyter 小部件支持。
- F-016：**myst-demo** — 演示组件。

## 样式系统（styles/）

- F-017：CSS 自定义属性（CSS Variables）系统，颜色以 `--myst-color-*` 命名空间组织：链接色、主色、背景色、文本色、边框色、语义色（info/success/tip/warning/danger/error/theorem/example/proof）。
- F-018：Tailwind themeExtensions 注册了 `myst-*` 颜色命名空间，映射到 CSS 变量。
- F-019：网格系统通过 `gridTemplateColumns` 定义了多套响应式列模板：article-sm/md/lg/xl/2xl（默认文章布局）、article-left-*（左侧 TOC 布局）、article-center-*（居中布局）。
- F-020：`gridColumn` 快捷类映射到命名网格线：col-screen、col-page、col-body、col-gutter-left/right、col-body-outset/inset、col-middle 等。
- F-021：Typography 覆盖配置（tailwind typography 插件），移除 code 前后的反引号、调整链接颜色到 myst CSS 变量、设置列表间距、补充 h5/h6 样式。
- F-022：关键帧动画：load（加载进度条）、fadeIn（淡入）。
- F-023：safelist 包含大量动态生成的类名（col-*、row-span-*、sphinx-* 等）防止 Tailwind purge 误删。
- F-024：CSS 文件分类：app.css（主应用）、typography.css（排版）、code-highlight.css（代码高亮 light/dark）、proof.css（证明环境）、cross-references.css（引用）、citations.css（引用）、figures.css（图片）、grid.css（网格）、details.css（折叠块）、tasklists.css（任务列表）、jupyter.css（Jupyter 输出）、math.css（数学）、button.css（按钮）、hover.css（悬停效果）、toc.css（目录）、search.css（搜索）、block-styles.css（块样式）、backmatter.css（后页）、ansi.css（ANSI 颜色）、sphinx.css（Sphinx 兼容）、text-spacers.css、grid-system.css、landing-pages.css。

## 主题系统（themes/）

- F-025：**Book 主题**（themes/book/）：多页面书籍/文档主题，基于 Remix，包含 Banner、Footer、SidebarFooter、ArticlePage 组件，支持多项目（路由 `($project)`），文件路由结构：`$.tsx`（根布局）、`($project)_.($a).($b).($c).($d).$slug[.json].tsx`（页面路由）。
- F-026：**Article 主题**（themes/article/）：单页文章主题，基于 Remix，包含 Article、ArticlePage、ArticlePageAndNavigation、Downloads 组件，更简洁，无侧边栏。
- F-027：两个主题都有 app/（Remix app 目录：entry.client.tsx、entry.server.tsx、root.tsx、routes/、components/）、styles/app.css（主题级 CSS）、tailwind.config.js、remix.config.dev/prod.js、server.js（Express 生产服务器）、template.yml（MyST 主题模板配置）。
- F-028：主题通过 myst-theme[.css].ts 路由提供 CSS 静态资源，api.theme.ts 提供主题 API。
- F-029：loader 逻辑在 app/utils/loaders.server.ts 中处理 MyST 站点数据加载。

## myst-to-react 组件

- F-030：核心入口 `<MyST ast={mdast} />` 组件遍历 MDAST 节点并映射到对应 React 组件。
- F-031：节点组件：Basic（段落、强调、删除线、行内代码、换行、分隔线、HTML、Mention）、admonitions（提示/警告/注意等）、block（块容器）、card（卡片）、cite（引用）、code（代码块，含语法高亮和复制按钮）、crossReference（交叉引用）、dropdown（折叠）、exercise（练习）、footnotes（脚注）、grid/grid-item（网格）、hashLink（锚链接）、heading（标题，带锚点）、iframe（嵌入）、image（图片）、inlineError/inlineExpression（内联表达式）、math（数学公式）、proof（证明）、tabs/tabItem（标签页）、reactive（响应式）、unknown（未知节点）。
- F-032：扩展组件（extensions/）：chemicalFormula（化学式）、siunits（SI 单位）。
- F-033：链接组件（links/）：github（GitHub 链接解析）、ror（研究组织注册表）、rrid（研究资源标识符）、wiki（维基链接）。
- F-034：子组件：CopyIcon（复制按钮）、HoverPopover（悬停弹出）、LinkCard（链接卡片）。

## Provider 系统

- F-035：ThemeProvider 提供主题上下文（light/dark）、Link 组件自定义、renderers 自定义渲染器映射、setTheme 回调。
- F-036：ArticleProvider 提供文档级上下文：kind（Article/Notebook）、references（引用数据）、frontmatter、headings。
- F-037：TabStateProvider 管理 sync-tab 状态（跨标签页同步选中）。
- F-038：SiteProvider/ProjectProvider 提供多站点/多项目导航上下文。
- F-039：LinkProvider/XrefProvider 处理内部链接和跨项目引用解析。
- F-040：BaseurlProvider 处理部署在子路径时的 base URL。
- F-041：SearchProvider 集成搜索功能。
- F-042：GridProvider 提供网格布局上下文。
- F-043：BannerProvider 管理顶部横幅（公告、通知等）。
- F-044：UIProvider 提供 UI 状态（暗色/亮色模式等）。

## Jupyter 集成（packages/jupyter/）

- F-045：提供基于 thebe 的 React 组件用于代码执行交互。
- F-046：execute/ 子模块实现了 Reducer 模式的执行状态管理：actions.ts（动作定义）、reducer.ts（状态规约）、provider.tsx（ExecutionProvider）、hooks.ts（useExecutionState 等）、selectors.ts（状态选择器）、types.ts（类型定义）、busy.tsx（忙碌指示器）、leaf.tsx（叶子节点）。
- F-047：输出渲染：Output.tsx（单输出）、Outputs.tsx（多输出）、output.spec.ts、stream.tsx（流式输出）、error.tsx（错误输出）、figure.tsx（图形输出）、plotly.ts（Plotly 图表）、convertImages.ts（图片转换）、safe.tsx（安全包装）、decoration.tsx（装饰）。
- F-048：UI 组件：BinderBadge.tsx（Binder 连接按钮）、ConnectionStatusTray.tsx（连接状态）、ErrorTray.tsx（错误显示）、NotebookToolbar.tsx/NotebookCellControls.tsx/ArticleCellControls.tsx（工具栏）、Spinner.tsx（加载动画）、Buttons.tsx（控制按钮）。
- F-049：renderers.ts 注册 Jupyter 输出的自定义渲染器。
- F-050：block.tsx/embed.tsx/passive.tsx/active.tsx/jupyter.tsx/providers.tsx/hooks.ts/utils.ts 提供 Jupyter 单元块和工具钩子。
