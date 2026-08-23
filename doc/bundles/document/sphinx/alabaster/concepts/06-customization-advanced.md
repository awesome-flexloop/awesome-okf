---
type: Concept
title: 高级定制开发
description: 从 custom.css 样式覆盖、自定义 Pygments 样式到基于 Alabaster 二次开发自定义主题
tags: [sphinx, theme, alabaster, customization, pygments, custom-css, theme-development]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:58:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: alabaster-source
    resource: /references/alabaster-source.md
    title: Alabaster 源码路径映射
---

# 高级定制开发

当 `html_theme_options` 的 50+ 配置选项无法满足需求时，Alabaster 提供了三种进阶定制方式：自定义 CSS 覆盖、自定义 Pygments 样式、基于 Alabaster 二次开发新主题。

## custom.css 样式覆盖

从 Alabaster 0.7.8 版本开始，支持通过 `_static/custom.css` 文件进行 CSS 覆盖。这是最简单、推荐的轻量定制方式。

### 启用方式

1. 在 Sphinx 项目的 `_static/` 目录下创建 `custom.css` 文件：

```css
/* _static/custom.css */

/* 修改正文文字颜色 */
div.body {
    color: #333;
    line-height: 1.8;
}

/* 修改链接颜色 */
a {
    color: #2c5aa0;
}

/* 修改侧边栏背景 */
div.sphinxsidebar {
    background: #f8f9fa;
}

/* 添加自定义字体 */
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* 自定义代码块样式 */
pre {
    border-radius: 6px;
    border: 1px solid #e1e4e8;
}
```

2. 确保 `conf.py` 中配置了 `html_static_path`：

```python
html_static_path = ['_static']
```

Alabaster 的 `layout.html` 会自动加载 `custom.css`：

```jinja2
{%- block extrahead %}
  {{ super() }}
  <link rel="stylesheet" href="{{ pathto('_static/custom.css', resource=True) }}" type="text/css" />
{% endblock %}
```

> 💡 `custom.css` 在 Alabaster 默认样式之后加载，可以覆盖任何默认样式。使用浏览器开发者工具（F12）检查元素的 CSS 类名和选择器。

### 常见 CSS 定制场景

```css
/* 1. 修改内容区域最大宽度 */
div.documentwrapper {
    max-width: 1200px;
}

/* 2. 隐藏侧边栏中的 "Related Topics" 标题 */
div.relations h3 {
    display: none;
}

/* 3. 自定义提示框样式 */
div.note {
    background: #e7f3ff;
    border-left: 4px solid #2196F3;
    border-radius: 0 4px 4px 0;
}

/* 4. 响应式调整：大屏幕更宽 */
@media screen and (min-width: 1400px) {
    div.page {
        width: 1200px;
    }
}

/* 5. 深色模式支持（基础方案） */
@media (prefers-color-scheme: dark) {
    body {
        background: #1a1a2e;
        color: #e0e0e0;
    }
    a { color: #64b5f6; }
}
```

## 自定义 Pygments 语法高亮

Alabaster 内置了自定义的 Pygments 样式类 `alabaster.support.Alabaster`。可以替换为自己的高亮样式。

### 方式一：使用 Pygments 内置样式

```python
# conf.py
pygments_style = 'sphinx'          # 浅色主题
pygments_dark_style = 'monokai'   # 深色主题（Sphinx 4.0+）
```

Pygments 内置样式包括：`monokai`、`friendly`、`fruity`、`autumn`、`tango`、`solarized-dark`、`solarized-light` 等。

### 方式二：创建自定义 Pygments 样式

1. 在项目中创建 `_ext/my_pygments_style.py`：

```python
# _ext/my_pygments_style.py
from pygments.style import Style
from pygments.token import (
    Keyword, Name, Comment, String, Number, Operator, Generic
)

class MyThemeStyle(Style):
    background_color = "#fafafa"
    default_style = ""

    styles = {
        Comment: "italic #6a737d",
        Comment.Preproc: "noitalic",
        Keyword: "bold #d73a49",
        Keyword.Type: "bold #d73a49",
        Name: "#24292e",
        Name.Function: "#6f42c1",
        Name.Class: "bold #6f42c1",
        Name.Builtin: "#005cc5",
        String: "#032f62",
        Number: "#005cc5",
        Operator: "#d73a49",
        Generic.Deleted: "#fdaeb7",
        Generic.Inserted: "#bef5cb",
    }
```

2. 在 `conf.py` 中注册：

```python
# conf.py
import sys
sys.path.insert(0, os.path.abspath('_ext'))

def setup(app):
    from my_pygments_style import MyThemeStyle
    app.add_pygments_style('my-theme-style', MyThemeStyle)

pygments_style = 'my-theme-style'
```

## 基于 Alabaster 二次开发主题

当 CSS 覆盖和配置选项不够时，可以创建一个继承 Alabaster 的新主题。这是最强大但也最复杂的定制方式。

### 主题目录结构

```
mytheme/
├── __init__.py        # 主题注册入口
├── theme.conf         # 主题配置
├── layout.html        # 覆盖的模板（可选）
├── about.html         # 覆盖的侧边栏组件（可选）
└── static/
    ├── mytheme.css_t  # Sass 样式模板（可选）
    └── custom.css     # 自定义 CSS（可选）
```

### 最简主题实现

```python
# mytheme/__init__.py
import os
import alabaster

__version__ = "0.1.0"

def setup(app):
    # 要求基础 Sphinx 版本
    app.require_sphinx("6.2")

    # 主题路径
    theme_path = os.path.abspath(os.path.dirname(__file__))

    # 注册主题（继承 alabaster）
    app.add_html_theme("mytheme", theme_path)

    # 连接 html-page-context 事件（如需注入额外变量）
    app.connect("html-page-context", update_context)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

def update_context(app, pagename, templatename, context, doctree):
    context["mytheme_version"] = __version__
```

```ini
# mytheme/theme.conf
[theme]
inherit = alabaster
stylesheet = alabaster.css, mytheme.css
pygments_style = mytheme.MyThemeStyle

[options]
# 继承 alabaster 的所有选项，并可添加新选项
my_custom_option = default_value
```

### 模板覆盖

创建与 Alabaster 同名的模板文件即可覆盖。例如覆盖 `layout.html`：

```jinja2
{# mytheme/layout.html #}
{%- extends "alabaster/layout.html" %}

{%- block extrahead %}
  {{ super() }}
  {# 添加额外的 meta 标签或 CSS #}
  <meta name="theme-color" content="#2c5aa0">
{% endblock %}

{%- block footer %}
  {{ super() }}
  {# 在页脚添加自定义内容 #}
  <div class="custom-footer">
    <p>自定义页脚内容</p>
  </div>
{%- endblock %}
```

关键技巧：
- 使用 `{% extends "alabaster/layout.html" %}` 继承 Alabaster 模板（而非 `basic/layout.html`）
- 使用 `{{ super() }}` 保留 Alabaster 的块内容，只做增量修改
- 只覆盖需要修改的块，其他块继承 Alabaster 的实现

### 覆盖侧边栏组件

```jinja2
{# mytheme/about.html #}
{%- extends "alabaster/about.html" %}

{# 在 about.html 内容后添加自定义区域 #}
{%- block extra_about %}
  <div class="my-custom-badge">
    <a href="/changelog.html">📋 更新日志</a>
  </div>
{%- endblock %}
```

> 注意：直接覆盖组件时，需要查看 Alabaster 原始模板是否定义了可扩展的 block。如果没有，可以完全重写组件内容（不 extends），或使用 Jinja2 的 `{{ super() }}` 配合 `{% block %}` 追加内容。

### entry point 配置

在新主题的 `pyproject.toml` 中注册：

```toml
[project.entry-points."sphinx.html_themes"]
mytheme = "mytheme"
```

### 使用自定义主题

```python
# conf.py
html_theme = 'mytheme'
html_theme_path = ['_themes']  # 如果主题放在项目本地

html_theme_options = {
    # 继承 Alabaster 的所有选项
    'github_user': 'your-name',
    'github_repo': 'your-repo',
    # 自定义主题的新选项
    'my_custom_option': 'custom-value',
}
```

## 模板中可用的全局变量

在编写自定义模板时，可以使用以下 Jinja2 全局变量：

### Sphinx 内置变量

| 变量 | 说明 |
|------|------|
| `project` | 项目名称（conf.py 中 `project`） |
| `copyright` | 版权信息 |
| `release` | 版本号 |
| `version` | 主版本号 |
| `sphinx_version` | Sphinx 版本 |
| `master_doc` | 主文档名（通常为 `index`） |
| `pagename` | 当前页面名 |
| `prev` / `next` | 上一页/下一页信息（`link`/`title` 属性） |
| `parents` | 当前页面的父文档链 |
| `pathto(path, resource=False)` | 生成相对路径的 URL 函数 |
| `toctree(**kwargs)` | 生成目录树的函数 |
| `has_source` / `sourcename` | 是否显示源码链接 |
| `show_copyright` | 是否显示版权 |
| `show_sphinx` | 是否显示 "Powered by Sphinx" |
| `show_source` | 是否显示 "Page source" 链接 |

### Alabaster 注入变量

| 变量 | 说明 |
|------|------|
| `alabaster_version` | Alabaster 版本字符串 |
| `alabaster_version_info` | Alabaster 版本元组 |

### 主题选项变量

所有 `html_theme_options` 中的选项可通过 `theme_<option_name>` 访问：

```jinja2
{{ theme_logo }}
{{ theme_github_user }}
{{ theme_fixed_sidebar|lower == 'true' }}
```

## 相关概念

- [主题配置选项体系](/concepts/04-theme-options.md)：50+ 内置配置选项
- [侧边栏组件化设计](/concepts/05-sidebar-components.md)：组件模板结构
- [setup 函数与注册机制](/concepts/03-setup-and-registration.md)：主题入口函数
- [自定义 CSS 与品牌化示例](/examples/custom-css-and-branding.md)：实战案例
