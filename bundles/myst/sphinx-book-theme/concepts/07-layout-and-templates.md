---
type: concept
title: 07 - 布局与模板定制
description: SBT的页面布局结构、Jinja2模板继承机制、组件覆盖方法、自定义侧边栏和页脚
tags:
- sphinx-book-theme
- layout
- templates
- jinja2
- customization
generated: 2026-08-23
status: stable
stale_after: 2027-08-23
sources:
- src/sphinx_book_theme/theme/sphinx_book_theme/layout.html
- src/sphinx_book_theme/theme/sphinx_book_theme/components/
- src/sphinx_book_theme/theme/sphinx_book_theme/macros/buttons.html
---

# 布局与模板定制

sphinx-book-theme 使用 Jinja2 模板引擎渲染HTML，模板继承自 pydata-sphinx-theme（PST）。理解模板结构和覆盖机制是深度定制主题外观的关键。

## 页面布局结构

SBT继承PST的三栏布局，整体结构如下：

```
┌──────────────────────────────────────────────────┐
│  bd-header-announcement (公告栏，可选)            │
├──────────────────────────────────────────────────┤
│  bd-header (顶部导航栏，SBT清空默认组件)           │
├──────────┬───────────────────────┬───────────────┤
│          │  bd-header-article    │               │
│          │  (文章头部：切换按钮 + │               │
│ bd-      │   头部按钮组 + 搜索)  │ bd-sidebar-   │
│ sidebar- ├───────────────────────┤ secondary     │
│ primary  │                       │ (页内目录)    │
│ (主侧    │  bd-article (正文区)   │               │
│  边栏)   │                       │               │
│          ├───────────────────────┤               │
│          │  bd-footer-article    │               │
├──────────┴───────────────────────┴───────────────┤
│  bd-footer-content (页脚内容区)                   │
├──────────────────────────────────────────────────┤
│  bd-footer (底部页脚，SBT清空默认组件)            │
└──────────────────────────────────────────────────┘
```

SBT对PST布局的两处修改：
1. 在docs_main顶部添加 `.sbt-scroll-pixel-helper` 用于滚动检测
2. 在docs_body中添加打印专用目录 `#jb-print-docs-body`

## 模板目录结构

SBT的模板文件位于 `theme/sphinx_book_theme/`：

```
theme/sphinx_book_theme/
├── theme.conf              # 主题配置（继承、默认选项、组件列表）
├── layout.html             # 根布局模板（继承PST layout）
├── components/             # 可复用组件（添加到templates_path）
│   ├── article-header-buttons.html  # 文章头部按钮容器
│   ├── author.html                  # 作者信息
│   ├── extra-footer.html            # 额外页脚
│   ├── page-toc.html                # 页面目录
│   ├── sbt-sidebar-nav.html         # SBT定制侧边栏导航
│   ├── toggle-primary-sidebar.html  # 主侧边栏切换
│   └── toggle-secondary-sidebar.html# 次级侧边栏切换
├── macros/
│   └── buttons.html        # 按钮渲染宏（link/js/group）
├── sections/
│   └── footer-content.html # 页脚内容区域
└── static/                 # 静态资源
    ├── images/             # 平台Logo图标
    ├── scripts/            # 编译后的JS
    ├── styles/             # 编译后的CSS
    └── locales/            # 翻译文件
```

## Jinja2 模板继承与覆盖

### 模板搜索路径

SBT通过 `update_general_config` 将 `components/` 目录添加到 `templates_path`（F-073、F-185）。Sphinx的模板搜索顺序为：

1. 用户项目的 `_templates/` 目录
2. 扩展注册的 templates_path（包括SBT的components/）
3. 主题的模板目录（theme/sphinx_book_theme/）
4. 父主题（PST）的模板目录

这意味着用户可以在自己的 `_templates/` 目录中创建同名模板来覆盖SBT或PST的组件。

### 覆盖组件示例

要自定义文章头部按钮，在项目的 `_templates/` 目录创建 `article-header-buttons.html`：

```html
{% from "../macros/buttons.html" import render_funcs with context %}

<div class="article-header-buttons">
<!-- 自定义内容 -->
<a href="{{ pathto('genindex') }}" class="btn btn-sm" title="索引">
  <i class="fas fa-list"></i>
</a>

{%- for button in header_buttons -%}
{% set btype = button.get("type") %}
{% set bopts = button.copy() %}
{% set _ = bopts.pop("type") %}
{{ render_funcs``[btype](**bopts.md)`` }}
{%- endfor -%}

{% include "theme-switcher.html" %}
{% include "search-button.html" %}
{% include "toggle-secondary-sidebar.html" %}
</div>
```

### 覆盖layout.html

如果需要更大幅度的布局修改，可以创建 `_templates/layout.html`：

```html
{% extends "!sphinx_book_theme/layout.html" %}

{# 添加自定义CSS/JS #}
{% block extrahead %}
{{ super() }}
<link rel="stylesheet" href="{{ pathto('_static/custom.css', 1) }}">
{% endblock %}

{# 在正文前添加公告 #}
{% block docs_body %}
<div class="custom-banner">我的自定义横幅</div>
{{ super() }}
{% endblock %}
```

> 注意 `"!"` 前缀：`{% extends "!sphinx_book_theme/layout.html" %}` 中的感叹号告诉Jinja2从主题目录加载而非当前目录。

## 按钮宏系统

按钮的渲染由 `macros/buttons.html` 中的三个宏和一个分发字典组成（F-153-F-157）：

```jinja2
{# 分发字典 #}
{%- set render_funcs = {
  "group" : render_button_group,
  "javascript" : render_js_button,
  "link": render_link_button,
} -%}
```

所有按钮遵循统一的属性约定：
- `icon`：Font Awesome类名（以"fa"开头）或图片路径
- `text`：按钮文字（下拉项中显示，单图标按钮可为空）
- `tooltip`：鼠标悬停提示（通过 `translate()` 翻译）
- `label`：生成CSS类 `btn-{label}`
- `classes`：额外CSS类

## 侧边栏导航

`sbt-sidebar-nav.html` 是SBT定制的主侧边栏导航组件（F-158-F-160）：

1. 如果 `theme_home_page_in_toc == True`，在顶部添加首页链接
2. 调用PST的 `generate_toctree_html()` 函数渲染目录树

`generate_toctree_html()` 的参数映射：

| 参数 | 配置项 | 默认值 | 说明 |
|------|--------|--------|------|
| `startdepth` | - | 0 | 起始深度 |
| `kind` | - | "sidebar" | 渲染类型 |
| `maxdepth` | `max_navbar_depth` | 4 | 最大深度 |
| `collapse` | `collapse_navbar` | False | 是否折叠 |
| `includehidden` | - | True | 包含隐藏toctree |
| `titles_only` | - | True | 仅显示标题 |
| `show_nav_level` | `show_navbar_depth` | 1 | 默认展开层级 |

## 页脚定制

页脚由 `footer_content_items` 配置控制（F-038）：

```ini
footer_content_items = author.html, copyright.html, last-updated.html, extra-footer.html
```

`update_templates` 函数处理模板名格式化（F-074-F-076）：
- 逗号分隔字符串自动拆分为列表
- 无 `.html` 后缀的自动添加

自定义页脚组件：创建 `_templates/my-footer.html`，然后在conf.py中：

```python
html_theme_options = {
    "extra_footer": "<p>自定义HTML内容</p>",
    "footer_content_items": "author.html, copyright.html, my-footer.html",
}
```

## 模板上下文变量

`add_metadata_to_page` 向模板上下文注入以下变量（F-055-F-074）：

| 变量 | 说明 |
|------|------|
| `root_doc` / `master_doc` | 根文档名（兼容Sphinx 4.x重命名） |
| `root_title` | 根文档标题 |
| `pagetitle` | 当前页面标题 |
| `page_description` | 页面描述（前160字符，从section提取） |
| `author` | 作者名（conf.py中的author配置） |
| `translate` | 翻译函数 |
| `theme_search_bar_text` | 搜索框占位文字 |
| `header_buttons` | 头部按钮字典列表 |
| `use_thebe` | 是否启用Thebe |

## 相关概念

- [主题架构与PST继承](/concepts/02-theme-architecture.md)
- [配置系统详解](/concepts/03-configuration.md)
- [头部按钮系统](/concepts/04-header-buttons.md)
- [样式定制与第三方扩展适配](/concepts/08-customization.md)
