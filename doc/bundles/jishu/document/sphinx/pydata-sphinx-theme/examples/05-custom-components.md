---
type: Example
title: 自定义组件与静态资源
description: 从零添加一个构建信息组件、覆盖内置模板、按页注入 CSS/JS 并避免常见陷阱
tags: [sphinx, theme, pydata, example, templates, static-assets]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T03:34:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-source-map
    resource: /references/source-map.md
    title: 源码路径映射
---

# 自定义组件与静态资源

## 目标

1. 在页脚添加一个“构建信息”组件。
2. 覆盖“编辑此页”的文案。
3. 只在 API 页面加载一个自定义 JS。
4. 用模板变量显示当前页面名。

## 1. 目录

```text
docs/
├── conf.py
├── _templates/
│   ├── build-info.html
│   └── edit-this-page.html
└── _static/
    └── js/
        └── api-helper.js
```

```python
templates_path = ["_templates"]
html_static_path = ["_static"]
```

## 2. 构建信息组件

`_templates/build-info.html`：

```html+jinja
<div class="build-info">
  <span>Built {{ last_updated or "just now" }}</span>
  <span>· Sphinx {{ sphinx_version }}</span>
  <span>· Theme {{ theme_version }}</span>
  <span>· Page {{ pagename }}</span>
</div>
```

放入页脚中区：

```python
html_theme_options = {
    "footer_center": ["build-info"],
    "footer_start": ["copyright"],
    "footer_end": ["theme-version"],
}
html_last_updated_fmt = "%Y-%m-%d"
```

说明：

- `theme_version` 由主题注入。
- `last_updated` 只有设置 `html_last_updated_fmt` 后才有值。
- 组件渲染为空时会被自动移除；这里始终有内容。

## 3. 覆盖内置组件

`_templates/edit-this-page.html`：

```html+jinja
{% extends "!components/edit-this-page.html" %}

{% block edit_this_page_text %}
  在 GitHub 上改进本页
{% endblock %}
```

`!` 前缀表示“找到原始模板并继承”，避免递归。

## 4. 只给 API 页加载 JS

```python
def setup(app):
    def add_api_assets(app, pagename, templatename, context, doctree):
        if pagename.startswith("reference/api/"):
            app.add_js_file("js/api-helper.js", loading_method="defer")

    app.connect("html-page-context", add_api_assets)
```

`app.add_js_file` 在 `html-page-context` 中调用时只作用于当前页。

## 5. 使用模板函数

主题向上下文注入了多个函数：

```html+jinja
{# 顶部导航 #}
{{ generate_header_nav_html(n_links_before_dropdown=4) }}

{# 侧栏树（通常由 sidebar-nav-bs 调用） #}
{{ generate_toctree_html("sidebar", startdepth=1, show_nav_level=2) }}

{# 页内目录 #}
{{ generate_toc_html() }}

{# 编辑链接 #}
{% set provider, url = get_edit_provider_and_url() %}
<a href="{{ url }}">Edit on {{ provider }}</a>
```

不要在每个页面手工调用 `generate_toctree_html` 并缓存结果；主题已按构建上下文做了缓存与当前页标记处理。

## 6. 静态资源路径

- `html_static_path` 中的目录会保留相对结构复制到输出的 `_static/`。
- 引用资源用 `pathto`：

```html+jinja
<link rel="stylesheet" href="{{ pathto('_static/css/custom.css', 1) }}">
<script src="{{ pathto('_static/js/api-helper.js', 1) }}" defer></script>
```

- `html_css_files` / `html_js_files` 中的路径相对 `html_static_path` 的**输出**位置。
- 带 `defer` 的元组写法：`("js/x.js", {"defer": "defer"})`。

## 7. 常见陷阱

| 陷阱 | 后果 | 正确做法 |
|---|---|---|
| 组件放在 `_static` | Jinja 找不到模板 | 放 `_templates` 并配置 `templates_path` |
| 扩展名写成 `.html` 又配置 `foo.html` | 正常；但 `foo.html.html` 会失败 | 统一省略或统一带后缀 |
| 组件输出只有空白 | 被自动移除 | 确保有可见内容，或加入 `templates_skip_empty_check` |
| 覆盖 `layout.html` 丢掉 `data-content_root` | 即时搜索链接 404 | 用 `{% extends %}` 并保留原 `<html>` 属性 |
| 在 `builder-inited` 之前读 `app.builder` | `AttributeError` | 在回调里做，或先判空 |
| 用 `:root` 改颜色 | 不生效 | 用 `html[data-theme]` |

## 8. 验收

- [ ] 页脚出现构建信息，且日期随 `html_last_updated_fmt` 变化。
- [ ] “编辑此页”文案已替换，链接仍正确。
- [ ] 只有 API 页加载 `api-helper.js`。
- [ ] 模板函数在自定义组件中可用。
- [ ] 构建无模板找不到/变量未定义警告。

## 相关概念

- [布局与模板区段](../concepts/03-layout-and-sections.md)
- [内部实现与扩展点](../concepts/09-internals-and-extension-points.md)
- [品牌、样式与暗色模式](../concepts/07-branding-styling-and-dark-mode.md)
