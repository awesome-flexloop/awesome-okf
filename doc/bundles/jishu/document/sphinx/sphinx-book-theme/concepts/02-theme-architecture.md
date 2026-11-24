---
type: Concept
title: "主题骨架与构建链：从源码到一页 HTML"
description: "sphinx-theme-builder 的仓库布局、Python setup() 的注册与事件时序、Jinja 模板分层、SCSS/JS 资产编译，以及一次页面渲染的完整调用链"
tags: [sphinx, theme, architecture, jinja2, scss, sphinx-theme-builder]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-arch
    resource: https://github.com/executablebooks/sphinx-book-theme/blob/main/ARCHITECTURE.md
    title: Architecture of the repository
  - id: sbt-init
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme/src/sphinx_book_theme/__init__.py
    title: sphinx_book_theme/__init__.py
  - id: sbt-theme-conf
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme/src/sphinx_book_theme/theme/sphinx_book_theme/theme.conf
    title: theme.conf
---

# 主题骨架与构建链：从源码到一页 HTML

## 仓库布局

本项目遵循 [sphinx-theme-builder](https://sphinx-theme-builder.readthedocs.io/) 推荐的文件系统布局：

```text
sphinx-book-theme/
├── pyproject.toml                 # 构建后端、依赖、主题元数据、entry point
├── webpack.config.js              # SCSS/JS 打包配置
├── package.json                   # 前端依赖与脚本
├── src/sphinx_book_theme/
│   ├── __init__.py                # setup(app)：一切注册的起点
│   ├── directives.py              # {margin} 指令
│   ├── nodes.py                   # SideNoteNode 及 HTML visitor
│   ├── _transforms.py             # 脚注 → 边注的 post-transform
│   ├── header_buttons/
│   │   ├── __init__.py            # 下载/全屏按钮、仓库信息注入
│   │   ├── source.py              # 源码/编辑/issue 按钮
│   │   └── launch.py              # Binder/Colab/Thebe 等启动按钮
│   ├── assets/
│   │   ├── scripts/index.js       # JS 入口
│   │   ├── styles/**.scss         # SCSS 源文件
│   │   └── translations/          # 主题文案的翻译源
│   └── theme/sphinx_book_theme/   # 真正打包发布的主题目录
│       ├── theme.conf
│       ├── layout.html
│       ├── sections/              # 页面大分区模板
│       ├── components/            # 小组件模板
│       ├── macros/                # Jinja 宏
│       └── static/                # 编译产物（不入 git）
├── docs/                          # 主题自己的文档站
└── tests/                         # pytest + BeautifulSoup + 回归快照
```

关键点：`src/sphinx_book_theme/theme/sphinx_book_theme/` 才是 Sphinx 认识的主题目录；`assets/` 里的 SCSS/JS 只是源文件，构建时才编译进 `static/`。

## 构建后端

`pyproject.toml` 指定：

```toml
[build-system]
requires = ["sphinx-theme-builder >= 0.2.0a7"]
build-backend = "sphinx_theme_builder"

[tool.sphinx-theme-builder]
node-version = "20.9.0"
theme-name = "sphinx_book_theme"
additional-compiled-static-assets = ["locales/"]
```

由此得到两条开发命令：

```bash
stb compile     # 编译 SCSS/JS/翻译，产出到 theme/.../static/
tox -e compile  # 项目封装的等价入口
```

编译产物（`static/styles/`、`static/scripts/`、`static/locales/`）**不进入 git**，由发布流水线生成。

## Python 入口：setup(app) 做了什么

`setup(app)` 是主题与扩展的共同入口。按执行顺序：

| 步骤 | 代码 | 作用 |
|------|------|------|
| 1 | `app.add_html_theme("sphinx_book_theme", theme_dir)` | 注册主题目录 |
| 2 | `app.add_js_file("scripts/sphinx-book-theme.js")` | 注入主题 JS |
| 3 | `app.add_message_catalog("booktheme", locale_dir)` | 注册翻译目录 |
| 4 | `builder-inited` 事件 × 5 | navbar 默认值、Thebe 配置、废弃项检查、源文件后缀、仓库上下文 |
| 5 | `html-page-context` 事件 × 3 | 页面元数据、资产哈希、footer 模板名归一 |
| 6 | `app.connect("config-inited", update_general_config)` | 把主题 `components/` 加入模板搜索路径 |
| 7 | `SideNoteNode.add_node(app)` | 注册自定义节点及 HTML visitor |
| 8 | `html-page-context` 按钮链 | 预置空列表 → 启动按钮 → 源码按钮 → 下载/全屏按钮 |
| 9 | `app.add_directive("margin", Margin)` | 注册 `{margin}` 指令 |
| 10 | `app.add_post_transform(HandleFootnoteTransform)` | 注册脚注转边注变换 |
| 11 | 返回并行安全标记 | `parallel_read_safe` / `parallel_write_safe` 均为 True |

### 为什么 `update_general_config` 注册两次

主题在 Sphinx 中"立即初始化"，而扩展先初始化、再让配置覆盖。只调用一次会丢配置，因此代码同时：

- 在 `setup(app)` 中直接调用一次，保证主题路径立刻生效；
- 再挂到 `config-inited`，保证用户配置读取后仍生效。

这是本项目里最容易看漏的时序细节。

### 事件优先级

| 事件 | 处理函数 | 优先级 | 原因 |
|------|---------|--------|------|
| `builder-inited` | `update_navbar_defaults` | 400 | 必须早于父主题，阻止它往 navbar 塞搜索按钮 |
| `html-page-context` | `prep_header_buttons` | 默认 | 先创建空 `header_buttons` 列表 |
| `html-page-context` | `add_launch_buttons` | 501 | 晚于父主题设置编辑 URL 的函数 |
| `html-page-context` | `add_source_buttons` | 501 | 同上 |
| `html-page-context` | `add_header_buttons` | 501 | 最后追加下载/全屏按钮 |

## 模板分层

模板遵循 [sphinx-basic-ng](https://sphinx-basic-ng.readthedocs.io/) 的结构约定：

| 层级 | 目录 | 职责 | 例子 |
|------|------|------|------|
| 布局 | 根 | 继承父主题、决定大区块是否渲染 | `layout.html` |
| 分区 | `sections/` | 页面级大块 | `footer-content.html` |
| 组件 | `components/` | 可复用的小块 | `sbt-sidebar-nav.html`、`article-header-buttons.html`、`page-toc.html` |
| 宏 | `macros/` | 纯函数式 HTML 片段 | `buttons.html` 的 `render_link_button` |

`layout.html` 全文只覆盖三个 block：

```jinja
{% extends "pydata_sphinx_theme/layout.html" %}

{% block docs_navbar %}
{%- if theme_navbar_start or theme_navbar_center or theme_navbar_end or theme_navbar_persistent %}
{{ super() }}
{%- endif %}
{% endblock docs_navbar %}

{% block docs_main %}
<div class="sbt-scroll-pixel-helper"></div>
{{ super() }}
{% endblock %}

{% block docs_body %}
<div id="jb-print-docs-body" class="onlyprint"> ... 打印目录 ... </div>
{{ super() }}
{% endblock %}
```

含义：

- **默认没有页眉**。只有用户配置了任一 navbar 区域，才调用父模板渲染 `<header>`。
- 一个不可见像素用于 JS 判断"页面是否已滚动"。
- 打印时插入完整页内目录，屏幕阅读时不显示。

## 资产管线

### SCSS

`assets/styles/index.scss` 是入口，按职责分层：

```text
styles/
├── abstracts/    变量与 mixin
├── base/         基础排版、打印
├── components/   返回顶部、图标链接、logo、搜索
├── content/      提示框、代码、图片、margin、Notebook、引用
├── extensions/   myst-nb、sphinx-design、sphinx-tabs、togglebutton、thebe、comments
└── sections/    公告、article、footer、header、双 sidebar
```

命名遵循 BEM 风格（`block__element--modifier`），但项目自述"仍是努力方向"。

### JavaScript

`assets/scripts/index.js` 负责：

- 全屏切换 `toggleFullScreen()`（含 Safari `webkit` 前缀分支）；
- 滚动监听：侧栏内容进入视口时隐藏页内目录；
- 边注在窄屏下的展开/收起；
- Thebe 初始化 `initThebeSBT()`。

### 缓存失效

`hash_html_assets` 在 `html-page-context` 阶段为主题 CSS/JS 追加 SHA-1 摘要：

```python
assets = ["scripts/sphinx-book-theme.js"]
if app.config.html_theme == "sphinx_book_theme":
    assets.append("styles/sphinx-book-theme.css")
```

只有**直接使用本书主题**时才追加主题 CSS；子主题会提供自己的 CSS，避免重复加载。

## 翻译

- 主题文案的 message catalog 名为 `booktheme`。
- 源文案在 `assets/translations/`，编译后进入 `static/locales/`。
- `__init__.py` 在 `html-page-context` 中把 `translate` 函数注入模板上下文。
- 当前翻译源包含 22 个词条（`Search`、`Download this page`、`Launch on` 等），支持多语言。

## 测试

测试栈：

- `pytest` 驱动构建；
- `beautifulsoup4` 解析生成的 HTML；
- `pytest-regressions` 对比 `tests/test_build/*.html` 快照；
- `tests/sites/` 提供多种最小站点：base、notitle、parallel-build、titles 等。

修改模板或按钮逻辑后，回归快照通常会变化。不要盲目 `--force-regen`，先确认差异符合预期。

## 一次页面渲染的调用链

```text
Sphinx 读取 conf.py
  → 加载 entry point，调用 setup(app)
  → builder-inited：navbar 默认值 / 仓库上下文 / Thebe 配置
  → 读取源文件，构建 doctree
  → post-transform：HandleFootnoteTransform（可选，脚注转边注）
  → html-page-context：
       add_metadata_to_page
       hash_html_assets
       update_templates
       prep_header_buttons
       add_launch_buttons
       add_source_buttons
       add_header_buttons
  → Jinja 渲染 layout.html
       → pydata 布局
       → sections/ 与 components/
       → macros/buttons.html 渲染 header_buttons
  → 写出 HTML
```

## 相关概念

- [页面分区与导航](03-layout-and-navigation.md)
- [配置选项全解](04-theme-options.md)
- [页眉按钮机制](05-header-buttons.md)
- [源码路径映射](../references/source-map.md)
