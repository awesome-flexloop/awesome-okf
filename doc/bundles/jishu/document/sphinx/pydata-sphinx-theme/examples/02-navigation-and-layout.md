---
type: Example
title: 导航与布局定制
description: 顶层导航分组、More 下拉、侧栏折叠、按页侧栏与面包屑的实战配置
tags: [sphinx, theme, pydata, example, navigation, layout]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T03:28:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-source-map
    resource: /references/source-map.md
    title: 源码路径映射
---

# 导航与布局定制

## 场景

一个中型项目有 9 个顶层章节，希望：

- 顶部只直接显示 4 个，其余进“更多”。
- 左侧默认展开到第 2 层，最多 3 层。
- 首页与搜索页不显示主侧栏。
- API 页面只保留页内目录，不显示编辑链接。
- 页脚显示构建信息。

## 目录结构

```text
docs/
├── index.md
├── overview/
├── install/
├── tutorial/
├── howto/
├── reference/
│   ├── index.md
│   └── api/
├── changelog.md
├── community.md
└── faq.md
```

## 顶层导航

`index.md` 中的 toctree 决定顶部顺序：

````markdown
```{toctree}
:hidden:
:maxdepth: 1

overview/index
install/index
tutorial/index
howto/index
reference/index
changelog
community
faq
```
````

配置：

```python
html_theme_options = {
    "header_links_before_dropdown": 4,
    "header_dropdown_text": "更多",
    "external_links": [
        {"name": "官网", "url": "https://acme.example"},
        {"name": "博客", "url": "https://blog.acme.example"},
    ],
}
```

效果：前 4 个章节直接显示，其余 4 个 + 2 个外链进入“更多”。

## 左侧章节树

```python
html_theme_options = {
    "show_nav_level": 2,
    "navigation_depth": 3,
    "collapse_navigation": False,
}
```

- `show_nav_level=2`：首屏展开顶层与第二层。
- `navigation_depth=3`：第三层可见，第四层及更深不渲染。
- `collapse_navigation=False`：保留 `<details>` 折叠交互。

若希望按 caption 折叠整段：

```python
html_theme_options = {"show_nav_level": 0}
```

此时 `reference/index.md` 中的 `:caption:` 才有意义：

````markdown
```{toctree}
:caption: Reference

api/index
cli
config
```
````

## 按页移除主侧栏

```python
html_sidebars = {
    "**": ["sidebar-collapse", "sidebar-nav-bs"],
    "index": [],
    "search": [],
}
```

首页与搜索页不再有左侧栏，正文自动居中。

## 按页定制右侧栏

```python
html_theme_options = {
    "secondary_sidebar_items": {
        "**": ["page-toc", "edit-this-page", "sourcelink"],
        "reference/api/*": ["page-toc"],
        "index": [],
    },
}
```

- API 页只保留页内目录。
- 首页不显示右侧栏。

## 面包屑与页脚

```python
html_theme_options = {
    "article_header_start": ["breadcrumbs"],
    "footer_start": ["copyright"],
    "footer_center": ["sphinx-version"],
    "footer_end": ["theme-version", "last-updated"],
}
html_last_updated_fmt = "%Y-%m-%d"
```

注意：`last-updated` 只有在 `html_last_updated_fmt` 设置后才有内容。

## 页脚横向排列

```css
/* _static/css/custom.css */
.footer-items__start,
.footer-items__end {
  flex-direction: row;
  gap: 1rem;
}
```

```python
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
```

## 验收

- [ ] 顶部只显示 4 项 + “更多”。
- [ ] “更多”中点开其余章节可跳转。
- [ ] 首页无左右侧栏。
- [ ] API 页右侧只有页内目录。
- [ ] 页脚出现构建日期。
- [ ] 窄屏下汉堡按钮可打开章节树。

## 相关概念

- [导航与 toctree](../concepts/04-navigation-and-toctree.md)
- [布局与模板区段](../concepts/03-layout-and-sections.md)
- [主题配置项](../concepts/06-theme-options.md)
