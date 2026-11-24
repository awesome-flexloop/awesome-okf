---
type: Concept
title: 导航与 toctree
description: 顶部导航、左侧章节树、折叠层级、缓存与常见错位问题
tags: [sphinx, theme, pydata, navigation, toctree, sidebar]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T03:02:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-source-map
    resource: /references/source-map.md
    title: 源码路径映射
---

# 导航与 toctree

PST 的导航分成三个独立系统：顶部导航、左侧章节树、右侧页内目录。本文讲前两个；页内目录见下一篇。

## 1. 顶部导航从哪里来

顶部导航不是"全站 toctree 的前两层"，而是 **`root_doc` 的 toctree 顶层条目**，加上 `external_links`。

```text
root_doc (通常是 index)
├── guide/          → 顶部第 1 项 "Guide"
├── reference/      → 顶部第 2 项 "Reference"
└── changelog       → 顶部第 3 项 "Changelog"

external_links:      → 追加在末尾，带外链图标
```

实现上，`_generate_nav_info` 遍历 `app.env.tocs[root_doc]` 中的 toctree 节点，取 `entries` 的 `(title, page)`，再按当前页计算 `is_current`。标题缺失时依次回退到文档标题、`Index`、`Python Module Index`、`Search`。

### 1.1 下拉折叠

默认 `header_links_before_dropdown = 5`：

- 若链接总数 ≤ `n+1`，全部直接显示（避免只有一个条目的下拉）。
- 否则前 `n` 个显示，其余进入标题为 `header_dropdown_text`（默认 `More`）的下拉。

```python
html_theme_options = {
    "header_links_before_dropdown": 4,
    "header_dropdown_text": "更多",
}
```

### 1.2 对齐方式

```python
html_theme_options = {
    "navbar_align": "content",  # content | left | right
}
```

`content` 让导航中部与正文对齐（三栏网格），`left` 贴近 logo，`right` 贴近右侧组件。实现为返回 Bootstrap 的 `col-lg-*` 与 `me-auto`/`ms-auto` 类。

### 1.3 外链与图标

```python
html_theme_options = {
    "external_links": [
        {"name": "PyData", "url": "https://pydata.org"},
    ],
    "icon_links": [
        {"name": "GitHub", "url": "https://github.com/org/repo",
         "icon": "fa-brands fa-square-github", "type": "fontawesome"},
        {"name": "PyPI", "url": "https://pypi.org/project/x/",
         "icon": "fa-custom fa-pypi", "type": "fontawesome"},
    ],
}
```

`icon_links` 支持三种类型：`fontawesome`、`url`（远程图片）、`local`（相对文档根的本地图片）。`github_url` 等旧快捷键仍可用，会在 `update_config` 中被转成 `icon_links` 并插入列表头部。

## 2. 左侧章节树

左侧只显示"当前顶层章节"的子树，而不是全站树。这是 PST 与 SphinxBook/Furo 最大的导航差异。

```text
顶部选中 Guide
└── 左侧显示 Guide 及其子页
    ├── install
    ├── usage
    └── advanced/
        ├── caching
        └── plugins
```

实现分三步：

1. `_get_ancestor_pagename(app, pagename, startdepth=1)` 找到当前页的顶层祖先。
2. `get_nonroot_toctree(...)` 以该祖先为根解析 toctree 子树。
3. BeautifulSoup 改写：加 `nav bd-sidenav`、`has-children`、`<details>/<summary>`，并同步 `current/active` 与 `aria-current`。

### 2.1 展开层级

```python
html_theme_options = {
    "show_nav_level": 2,      # 首屏展开到第 2 层
    "navigation_depth": 4,    # 最多显示 4 层
}
```

- `show_nav_level = 1`（默认）：只展开顶层，其余折叠。
- `show_nav_level = 0`：按 toctree 的 `:caption:` 折叠整段；只有带 caption 的 toctree 才能这样折叠。
- `navigation_depth`：控制树的最大深度，超过部分不渲染。

### 2.2 关闭折叠交互

```python
html_theme_options = {
    "collapse_navigation": True,
}
```

关闭后每页的侧栏结构可能不同，主题因此**不再使用侧栏缓存**（缓存条件要求 `collapse=False`）。

### 2.3 侧栏组成

```python
html_sidebars = {
    "**": ["sidebar-collapse", "sidebar-nav-bs"],
}
```

- `sidebar-collapse`：折叠整个主侧栏的按钮。
- `sidebar-nav-bs`：章节树；无内容时渲染为空并被自动移除。
- `primary_sidebar_end`：贴在侧栏底部的固定项，默认 `sidebar-ethical-ads`，可换成 `indices` 等。

## 3. 侧栏缓存与"当前页标记搬运"

大站点上解析 toctree 很贵。主题的优化是：

- 仅当 `kind == "sidebar"`、`collapse=False`、存在祖先、页面 URI 不以 `/` 结尾时缓存。
- 缓存键 = `(祖先页, 输出目录, show_nav_level, 排序后的 kwargs)`。
- 同一目录下、同一祖先下的页面共享同一份侧栏 HTML。
- 命中缓存后，`_move_current_markers` 把 `current/active` 类、`aria-current="page"`、`<details open>` 从旧页条目搬到当前页条目。

因此：

- `dirhtml` builder 的页面 URI 以 `/` 结尾，**不会命中缓存**，也不会出现"标记搬错"。
- 如果自定义模板直接复用 `generate_toctree_html` 的返回值并缓存，必须自己处理当前页标记。

## 4. 面包屑

`article_header_start` 默认是 `breadcrumbs`，显示当前页的祖先链。它读取 Sphinx 的 `parents` 上下文，不依赖侧栏计算。若页面不在任何 toctree 中，面包屑可能为空。

## 5. 常见问题

| 现象 | 根因 | 处理 |
|---|---|---|
| 顶部导航项缺失 | 条目只在隐藏 toctree 中，或不在 `root_doc` 的 toctree 里 | 把顶层条目放进 `root_doc` 的可见 toctree |
| 顶部导航项过多 | 所有页面都挂在根 toctree | 用一层目录页收拢，或调小 `header_links_before_dropdown` |
| 左侧显示全站树 | 当前页没有祖先（如根页、genindex、search） | 属预期；根页不显示章节树 |
| 左侧高亮错页 | 用了自定义缓存或 `dirhtml` 下手工复用 HTML | 关闭自定义缓存；改用 `generate_toctree_html` |
| 折叠按钮点了没反应 | `collapse_navigation=True` 或 `<details>` 被自定义 CSS 隐藏 | 检查配置与 CSS |
| caption 不能折叠 | toctree 没有 `:caption:` | 加 caption，或把 `show_nav_level` 调回 1 |
| 侧栏空白 | `html_sidebars` 为空，或 `sidebar-nav-bs` 渲染为空 | 检查页面是否有子页/祖先 |

## 6. 设计建议

1. **顶层不超过 7 项**：超过就分组或依赖 More 下拉。
2. **每个顶层章节有落地页**：否则顶部链接与左侧树都缺少锚点。
3. **API 页面用 `sphinx-remove-toctrees` 排除**：避免数千个 stub 页拖慢侧栏构建。
4. **深树用 caption 分段**：`show_nav_level=0` 时可按段折叠，阅读负担更低。
5. **不要把 `navigation_depth` 设得过大**：渲染成本与视觉噪音都会上升。

## 相关概念

- [布局与模板区段](03-layout-and-sections.md)
- [页内目录与次级侧栏](05-page-toc-and-secondary-sidebar.md)
- [主题配置项](06-theme-options.md)
- [导航与布局示例](../examples/02-navigation-and-layout.md)
- [Sphinx toctree 文档](../../sphinx/concepts/08-project-and-docutils.md)
