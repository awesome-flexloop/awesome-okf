---
okf_version: "0.2"
type: bundle
title: "sphinx-book-theme — 交互式书籍主题"
description: "sphinx-book-theme 是 Executable Books 团队维护的 Sphinx 书籍主题，基于 pydata-sphinx-theme 与 Bootstrap 5，提供 Tufte 式边注、Notebook 单元格样式、Binder/Colab/Thebe 启动按钮与可深度定制的页面分区"
tags: [sphinx, theme, book, jupyter, myst, bootstrap, pydata, executable-books]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-repo
    resource: https://github.com/executablebooks/sphinx-book-theme
    title: sphinx-book-theme GitHub Repository
    author: team:executablebooks
  - id: sbt-docs
    resource: https://sphinx-book-theme.readthedocs.io/
    title: sphinx-book-theme Documentation
  - id: sbt-local
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme
    title: 本地源码快照（1.5.0.dev）
---

# sphinx-book-theme — 交互式书籍主题

`sphinx-book-theme` 是 [Executable Books](https://executablebooks.org/) 团队为 Sphinx 打造的**书籍式 HTML 主题**。它继承 [pydata-sphinx-theme](../pydata-sphinx-theme/index.md) 的布局与 Bootstrap 5 组件，在其上叠加 Tufte 风格边注、Jupyter Notebook 单元格样式、页面源文件按钮与 Binder/Colab/Thebe 等交互启动按钮，是 [Jupyter Book](https://jupyterbook.org) 的默认主题。

> **定位一句话**：把"一页页技术文档"排成"一本可交互的书"——单列阅读流 + 左侧全书目录 + 右侧页内目录 + 页眉工具箱。

> **维护状态**：README 明确标注 **Maintenance Mode**。团队接受缺陷修复，但不保证新功能开发；源码版本号为 `1.5.0.dev`，最近正式发布为 `1.4.0`（2026-07-19）。

## 知识地图

```
sphinx-book-theme/
├── concepts/       概念文档（9 篇）
│   ├── 入门：定位与生态、安装与最小站点
│   ├── 架构：主题骨架、页面分区与导航、配置选项
│   ├── 机制：页眉按钮、边注与 margin、Notebook 交互
│   └── 进阶：定制、子主题与主题开发
├── examples/       实战示例（5 篇）
│   ├── 从零搭建书籍站点
│   ├── 仓库按钮与在线启动按钮
│   ├── 边注、margin 与全宽内容
│   ├── Notebook 内容流水线
│   └── 子主题与模板覆盖
├── references/     信源参考（3 篇）
│   ├── 源码路径映射
│   ├── 主题选项速查
│   └── 版本与发布注记
└── spec/           R/I 阶段工作稿
    ├── facts.md    源码事实清单
    └── insights.md 架构洞察
```

## 推荐学习路径

### 30 分钟上手

1. [定位与生态](concepts/00-introduction.md) → 弄清它与 pydata-sphinx-theme、Jupyter Book 的关系（5 分钟）
2. [安装与最小站点](concepts/01-getting-started.md) → 装包、改 `html_theme`、构建（10 分钟）
3. [从零搭建书籍站点](examples/01-basic-book-site.md) → 复制完整 `conf.py` 与目录骨架（15 分钟）

### 理解主题结构（1–2 小时）

4. [主题骨架与构建链](concepts/02-theme-architecture.md) → sphinx-theme-builder、模板继承、SCSS/JS 编译
5. [页面分区与导航](concepts/03-layout-and-navigation.md) → primary/secondary sidebar、navbar、footer、announcement
6. [配置选项全解](concepts/04-theme-options.md) → `theme.conf` 与 `html_theme_options` 的映射关系
7. [页眉按钮机制](concepts/05-header-buttons.md) → 下载、源码、仓库、启动按钮的生成链路

### 内容表现力与交互（1 小时）

8. [边注、margin 与全宽内容](concepts/06-sidenotes-margin.md) → 脚注转边注的 post-transform 与 `{margin}` 指令
9. [Notebook 与在线交互](concepts/07-jupyter-interactivity.md) → MyST-NB、单元格标签、Thebe/Binder/Colab
10. [边注、margin 与全宽内容示例](examples/03-margin-notes-and-custom-css.md) → 可直接复制的页面片段

### 定制与二次开发（1–2 小时）

11. [定制、子主题与主题开发](concepts/08-customization-and-development.md) → 自定义 CSS、模板覆盖、子主题、国际化与测试
12. [子主题与模板覆盖](examples/05-subtheme-and-template-override.md) → 最小子主题包与页面分区替换
13. [源码路径映射](references/source-map.md) → 出问题时按图索骥

## 核心洞察

| # | 洞察 | 一句话总结 |
|---|------|-----------|
| 1 | 继承而非重写 | 主题只覆盖 pydata-sphinx-theme 的差异部分，`layout.html` 仅 3 个 block |
| 2 | 主题即扩展 | `setup()` 同时注册主题、指令、节点、post-transform 与事件钩子 |
| 3 | 配置三层映射 | `theme.conf` 默认值 → `html_theme_options` 用户值 → 模板 `theme_*` 变量 |
| 4 | 按钮由数据驱动 | 页眉按钮先生成 Python 字典列表，再由 Jinja 宏统一渲染 |
| 5 | 边注是文档树变换 | 脚注不是 CSS 挪位，而是 post-transform 把内容搬到引用点旁 |
| 6 | 构建期资产管线 | SCSS/JS 由 sphinx-theme-builder + webpack 编译，产物不入库 |
| 7 | 交互按钮只做 URL 拼装 | Binder/Colab/Thebe 按钮不执行代码，只按仓库信息生成链接 |

## 架构速查

| 层次 | 关键文件/机制 | 作用 |
|------|-------------|------|
| 包注册 | `pyproject.toml` 的 `sphinx.html_themes` entry point | 让 Sphinx 发现 `sphinx_book_theme` |
| 主题声明 | `theme/sphinx_book_theme/theme.conf` | 声明继承 `pydata_sphinx_theme`、侧边栏、样式表与默认选项 |
| Python 入口 | `src/sphinx_book_theme/__init__.py` 的 `setup(app)` | 注册主题、JS、翻译目录、节点、指令、post-transform、事件 |
| 模板骨架 | `theme/sphinx_book_theme/layout.html` | 继承 pydata 布局，控制 navbar 是否渲染、插入打印目录 |
| 页面分区 | `theme/sphinx_book_theme/sections/`、`components/` | footer-content、page-toc、sidebar-nav、article-header-buttons 等 |
| 页眉按钮 | `header_buttons/*.py` + `macros/buttons.html` | 生成下载/源码/启动按钮的数据结构与 HTML |
| 样式资产 | `assets/styles/**.scss` → `static/styles/*.css` | 构建期编译，按 sections/components/content/extensions 分层 |
| 交互脚本 | `assets/scripts/index.js` → `static/scripts/*.js` | 全屏、滚动监听、边注开关、Thebe 初始化 |

## 相关知识包

| 知识包 | 关系 |
|--------|------|
| [sphinx](../sphinx/index.md) | 底层框架——主题系统、事件、doctree 与 builder |
| [pydata-sphinx-theme](../pydata-sphinx-theme/index.md) | 直接父主题——布局、导航、搜索、主题切换器的来源 |
| [alabaster](../alabaster/index.md) | 对照学习——最小 Sphinx 主题的另一种范式 |
| [sphinx-autobuild](../sphinx-autobuild/index.md) | 开发主题时的热重载预览工具 |
| [Jupyter Book v2 / MySTmd 生态](../../jupyter-book/index.md) | 下游消费者——书籍工具链与主题协作方式 |
| [MyST Markdown 与 Executable Books 生态](../../myst/index.md) | 内容语法层——MyST 指令、角色与 Notebook 解析 |

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
