---
type: Concept
title: "页面分区与导航：双 sidebar、页眉与页脚"
description: "sphinx-book-theme 的页面区域模型：主/次侧边栏、默认侧栏组件、navbar 四区、article header、内容页脚、站点页脚与公告条，以及 html_sidebars 的页面级覆盖"
tags: [sphinx, theme, layout, navigation, sidebar, navbar, footer]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-sections
    resource: https://sphinx-book-theme.readthedocs.io/en/latest/sections/index.html
    title: Layout and major sections
  - id: sbt-theme-conf
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme/src/sphinx_book_theme/theme/sphinx_book_theme/theme.conf
    title: theme.conf
---

# 页面分区与导航：双 sidebar、页眉与页脚

## 页面区域模型

```text
┌──────────────────────────────────────────────────────────────┐
│ announcement（可选，滚动后消失）                              │
├──────────────┬───────────────────────────────┬───────────────┤
│              │ article header（工具按钮）     │               │
│ primary      ├───────────────────────────────┤ secondary     │
│ sidebar      │                               │ sidebar       │
│（左，全书）  │ 正文（单列阅读流）             │（右，页内 TOC）│
│              │                               │               │
│              ├───────────────────────────────┤               │
│              │ content footer（作者/版权/更新）│               │
├──────────────┴───────────────────────────────┴───────────────┤
│ site footer（footer_start / footer_end，可选）                │
└──────────────────────────────────────────────────────────────┘
```

默认是**两栏**：左侧栏 + 正文。右侧栏在有大纲的页面自动出现；没有二级标题时正文会占满宽度（这是父主题的行为）。

## 主侧边栏（Primary sidebar）

位于左侧，承载"全书导航"。默认组件由 `theme.conf` 的 `sidebars` 声明：

```ini
sidebars = navbar-logo.html, icon-links.html, search-button-field.html, sbt-sidebar-nav.html
```

| 组件 | 作用 |
|------|------|
| `navbar-logo.html` | 显示 `html_logo` 与 `html_title`；来自父主题 |
| `icon-links.html` | 显示 `html_theme_options["icon_links"]` 的图标链接与徽章 |
| `search-button-field.html` | Bootstrap 搜索框 |
| `sbt-sidebar-nav.html` | 本书主题的全书目录树 |

`sbt-sidebar-nav.html` 的核心是一次 `generate_toctree_html` 调用：

```jinja
{{ generate_toctree_html(
    startdepth=0,
    kind="sidebar",
    maxdepth=theme_max_navbar_depth|int,
    collapse=theme_collapse_navbar|tobool,
    includehidden=True,
    titles_only=True,
    show_nav_level=theme_show_navbar_depth|int) }}
```

它还负责可选的"首页入口"：当 `home_page_in_toc: True` 时，在目录最上方插入根文档链接。

### 页面级覆盖：html_sidebars

`html_sidebars` 用"文件名模式 → 侧栏组件列表"控制哪些页面显示哪些组件：

```python
html_sidebars = {
    "posts/*": ["sbt-sidebar-nav.html"],
    "**": [
        "navbar-logo.html",
        "icon-links.html",
        "search-button-field.html",
        "sbt-sidebar-nav.html",
    ],
}
```

- `*` 匹配单层，`**` 匹配所有页面。
- 列表顺序就是渲染顺序。
- 只列 `sbt-sidebar-nav.html` 会去掉 logo、图标链接和搜索框。
- 可以混入其他扩展提供的侧栏模板（如 ABlog 的 `ablog/recentposts.html`）。

### 目录展开深度

| 选项 | 默认 | 作用 |
|------|------|------|
| `show_navbar_depth` | `1` | 默认展开到第几层 |
| `max_navbar_depth` | `4` | 最多渲染到第几层 |
| `collapse_navbar` | `False` | `True` 时禁止展开/折叠，全部平铺 |

`show_navbar_depth` 控制"初始展开"，`max_navbar_depth` 控制"能展开到多深"。两者不要混淆。

## 次侧边栏（Secondary sidebar）

位于右侧，承载"当前页信息"。`theme.conf` 默认：

```ini
secondary_sidebar_items = page-toc.html
toc_title = Contents
```

| 选项 | 默认 | 作用 |
|------|------|------|
| `secondary_sidebar_items` | `page-toc.html` | 右侧栏组件列表 |
| `toc_title` | `Contents` | 页内目录标题 |
| `show_toc_level` | 未设置 | 默认展示到第几级标题；设置后更深层也常驻显示 |

`show_toc_level: 2` 表示二级标题始终显示；不设置时，深层标题只在滚动到对应位置时出现。

## 页眉 / navbar

**默认没有页眉**。`layout.html` 只有在四个 navbar 区域任一有内容时才渲染 `<header>`。

| 区域 | 位置 | 移动端行为 | 典型用途 |
|------|------|-----------|---------|
| `navbar_start` | 最左 | 始终可见 | 持久 logo |
| `navbar_center` | 中间（无 start 时靠左） | 移入侧栏 | 外部导航链接 |
| `navbar_end` | 最右 | 移入侧栏 | 社交链接、按钮 |
| `navbar_persistent` | 最右 | 始终可见 | 必须常驻的图标 |

示例：往页眉右侧放一个自定义按钮：

```python
# _templates/mybutton.html
# <button class="btn btn-sm btn-primary">Try it</button>

templates_path = ["_templates"]
html_theme_options = {
    "navbar_end": ["mybutton.html"],
}
```

`navbar_persistent` 在 `builder-inited` 阶段被强制设为 `[]`（除非用户显式提供），目的是阻止父主题默认往 navbar 塞搜索按钮。

### 整体覆盖页眉

在 `_templates/sections/header.html` 放自定义模板，即可替换整个 header 分区。这是比分区域拼装更彻底的做法。

## Article header（正文工具条）

正文上方的按钮条由两个选项控制：

```ini
article_header_start = toggle-primary-sidebar.html
article_header_end = article-header-buttons.html
```

- 左侧默认是"折叠主侧栏"按钮（移动端尤其有用）。
- 右侧是 `article-header-buttons.html`，渲染 `header_buttons` 列表，并追加主题切换器、搜索按钮、次侧栏开关。
- 下载、全屏、源码、仓库、启动按钮都挂在这里。

## 内容页脚（Content footer）

位于正文末尾、跨正文宽度。默认组件：

```ini
footer_content_items = author.html, copyright.html, last-updated.html, extra-footer.html
```

| 组件 | 内容 |
|------|------|
| `author.html` | 页面作者（若存在） |
| `copyright.html` | `copyright` 配置 |
| `last-updated.html` | 最后更新时间 |
| `extra-footer.html` | 自定义 HTML 占位 |

`update_templates` 会把逗号分隔的字符串拆成列表，并给无后缀项补 `.html`。因此下面两种写法等价：

```python
html_theme_options = {
    "footer_content_items": "author.html, copyright.html",
}
```

```python
html_theme_options = {
    "footer_content_items": ["author.html", "copyright.html"],
}
```

### 追加自定义 HTML

```python
html_theme_options = {
    "extra_footer": "<div>© 2026 My Team · Built with Sphinx</div>",
}
```

> 源码 `docs/conf.py` 把 `extra_footer` 注释为 `DEPRECATED KEY`，但 `theme.conf` 与文档页面仍保留该能力。新项目若需要更可控的结构，优先用 `footer_content_items` 指向自己的模板。

## 站点页脚（Site footer）

位于整页最底部，跨全宽，默认空。两个入口：

```python
html_theme_options = {
    "footer_start": ["test.html"],   # 左
    "footer_end": ["test.html"],     # 右
}
```

模板放在 `templates_path` 中。适合放许可证、备案号、赞助方 logo。

## 公告条（Announcement）

页面顶部的高对比横幅，用户向下滚动后消失：

```python
html_theme_options = {
    "announcement": "New edition released! Read the migration guide.",
}
```

支持任意 HTML：

```python
html_theme_options = {
    "announcement": "<p class='my-announce'>Version 2.0 is out.</p>",
}
```

适合"新版本""迁移提醒""征稿"等一次性信息，不适合长期导航。

## 移动端行为

| 区域 | 窄屏表现 |
|------|---------|
| primary sidebar | 折叠为抽屉，由 `toggle-primary-sidebar.html` 打开 |
| secondary sidebar | 折叠，由 `toggle-secondary-sidebar.html` 打开 |
| `navbar_start` | 保持可见 |
| `navbar_center` / `navbar_end` | 移入侧栏 |
| `navbar_persistent` | 保持可见 |
| 边注 / margin | 默认隐藏，点击编号或符号展开 |

## 常见配置组合

### 极简阅读模式

```python
html_sidebars = {"**": ["sbt-sidebar-nav.html"]}
html_theme_options = {
    "show_navbar_depth": 1,
    "secondary_sidebar_items": ["page-toc.html"],
}
```

### 带完整工具箱的教程站

```python
html_theme_options = {
    "repository_url": "https://github.com/org/repo",
    "use_repository_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
    "use_download_button": True,
    "use_fullscreen_button": True,
    "show_toc_level": 2,
    "show_navbar_depth": 2,
    "footer_content_items": ["author.html", "copyright.html", "last-updated.html"],
}
```

### 多分组长书

```python
# index.md 中用多个 toctree + caption 分组
html_theme_options = {
    "show_navbar_depth": 1,
    "max_navbar_depth": 3,
    "collapse_navbar": False,
    "home_page_in_toc": True,
}
```

## 相关概念

- [配置选项全解](04-theme-options.md)
- [页眉按钮机制](05-header-buttons.md)
- [定制、子主题与主题开发](08-customization-and-development.md)
