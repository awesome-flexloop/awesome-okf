---
type: Concept
title: 侧边栏组件化设计
description: Alabaster 侧边栏的 5 个独立模板组件——about、navigation、relations、donate、searchfield 的职责与定制
tags: [sphinx, theme, alabaster, sidebar, jinja2, components]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:57:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: alabaster-source
    resource: /references/alabaster-source.md
    title: Alabaster 源码路径映射
---

# 侧边栏组件化设计

Alabaster 将侧边栏拆分为 5 个职责单一的 Jinja2 模板组件，用户通过 `conf.py` 中的 `html_sidebars` 配置自由组合、增删组件。这种组件化设计是 Alabaster 灵活性的核心。

## 默认侧边栏组件

`theme.conf` 中定义的默认侧边栏：

```ini
sidebars = about.html, searchfield.html, navigation.html, relations.html, donate.html
```

在 `conf.py` 中显式配置（推荐，可自定义顺序和内容）：

```python
html_sidebars = {
    '**': [
        'about.html',       # Logo + 项目信息 + GitHub 按钮
        'searchfield.html', # 搜索框
        'navigation.html',  # 目录树 + 自定义链接
        'relations.html',   # 上下页/面包屑
        'donate.html',      # 捐赠链接
    ]
}
```

`'**'` 表示匹配所有页面，也可以为特定页面指定不同的侧边栏组合：

```python
html_sidebars = {
    '**': ['about.html', 'searchfield.html', 'navigation.html'],
    'api/*': ['about.html', 'searchfield.html', 'localtoc.html'],  # API 页面用本地目录
    'index': ['about.html', 'searchfield.html', 'navigation.html', 'donate.html'],
}
```

## 组件详解

### about.html — 项目信息区

**职责**：显示项目 Logo、名称、简介、GitHub 按钮、CI 徽章。

**模板逻辑**：

```jinja2
{# 简化示意 #}
{% if theme_logo %}
  {# 显示 Logo 图片 #}
  <img src="{{ pathto('_static/' ~ theme_logo, 1) }}" alt="Logo" />
  {% if theme_logo_name|lower == 'true' %}
    <h1>{{ project }}</h1>
  {% elif theme_logo_name|lower != 'false' %}
    <h1>{{ theme_logo_name }}</h1>
  {% endif %}
{% else %}
  {# 无 Logo 时显示文本标题 #}
  <h1><a href="{{ pathto(master_doc) }}">{{ project }}</a></h1>
{% endif %}

{% if theme_description %}
  <p class="blurb">{{ theme_description }}</p>
{% endif %}

{% if theme_github_user and theme_github_repo and theme_github_button %}
  {# GitHub 按钮（通过 ghbtns.com iframe） #}
  <iframe src="https://ghbtns.com/github-btn.html?user=...&repo=...&type=..."></iframe>
{% endif %}
```

**相关配置项**：`logo`、`logo_name`、`logo_text_align`、`description`、`description_font_style`、`github_user`、`github_repo`、`github_button`、`github_type`、`github_count`、`travis_button`、`codecov_button`、`badge_branch`

### searchfield.html — 搜索框

**来源**：这是 Sphinx basic 主题内置的组件，不是 Alabaster 自定义的。

**职责**：提供全文搜索输入框。

**自定义**：通常不需要修改。如果需要自定义搜索框样式，可以在主题中覆盖 `searchfield.html`。

### navigation.html — 目录导航

**职责**：显示文档的 toctree 目录树和额外的自定义导航链接。

**模板逻辑**：

```jinja2
<h3>{{ _('Navigation') }}</h3>
{{ toctree(includehidden=theme_sidebar_includehidden, collapse=theme_sidebar_collapse) }}
{% if theme_extra_nav_links %}
<hr />
<ul>
    {% for text, uri in theme_extra_nav_links.items() %}
    <li><a href="{{ uri }}">{{ text }}</a></li>
    {% endfor %}
</ul>
{% endif %}
```

关键调用：`{{ toctree(...) }}` 是 Sphinx 提供的 Jinja2 全局函数，生成文档目录树 HTML。

**参数说明**：

| 参数 | 对应配置项 | 说明 |
|------|-----------|------|
| `includehidden` | `sidebar_includehidden` | 是否包含 `:hidden:` 标记的 toctree 项 |
| `collapse` | `sidebar_collapse` | 是否折叠非当前页面祖先的目录项 |

**相关配置项**：`sidebar_collapse`、`sidebar_includehidden`、`extra_nav_links`

### relations.html — 相关页面导航

**职责**：显示面包屑式层级导航和上一页/下一页链接。

**模板逻辑**：

```jinja2
<div class="relations">
<h3>{{ _('Related Topics') }}</h3>
<ul>
  <li><a href="{{ pathto(master_doc) }}">{{ _('Documentation overview') }}</a><ul>
  {%- for parent in parents %}
  <li><a href="{{ parent.link|e }}">{{ parent.title }}</a><ul>
  {%- endfor %}
    {% if prev %}
      <li>{{ _('Previous') }}: <a href="{{ prev.link|e }}">{{ prev.title }}</a></li>
    {% endif %}
    {% if next %}
      <li>{{ _('Next') }}: <a href="{{ next.link|e }}">{{ next.title }}</a></li>
    {% endif %}
  {%- for parent in parents %}
  </ul></li>
  {%- endfor %}
  </ul></li>
</ul>
</div>
```

通过嵌套 `<ul>` 结构构建面包屑，`parents` 变量由 Sphinx 自动提供，包含当前页面的祖先文档链。

**相关配置项**：`show_related`（注意：此选项在 Alabaster 中**不控制** `relations.html` 是否显示，而是控制旧版 sidebar 中的相关链接区域。`relations.html` 是否加载完全由 `html_sidebars` 决定）

### donate.html — 捐赠与支持

**职责**：显示捐赠链接和商业支持信息。

**模板逻辑**：

```jinja2
{% if theme_donate_url or theme_opencollective or theme_tidelift_url %}
<h3 class="donation">Donate/support</h3>
{% endif %}

{% if theme_donate_url %}
<p><a href="{{ theme_donate_url }}">
  <img src="https://img.shields.io/badge/donate-❤-ff69b4.svg" alt="Donate">
</a></p>
{% endif %}

{% if theme_opencollective %}
<p><a href="https://opencollective.com/{{ theme_opencollective }}/donate">
  <img src="https://opencollective.com/.../donate/button.png" />
</a></p>
{% endif %}

{% if theme_tidelift_url %}
<p>Professionally-supported {{ project }} is available with the
<a href="{{ theme_tidelift_url }}">Tidelift Subscription</a>.</p>
{% endif %}
```

**相关配置项**：`donate_url`、`opencollective`、`opencollective_button_color`、`tidelift_url`

## 组件组合策略

### 最小侧边栏（极简风格）

```python
html_sidebars = {
    '**': ['about.html', 'searchfield.html', 'navigation.html'],
}
```

只保留 Logo、搜索框和目录导航，适合不需要捐赠链接和上下页导航的项目。

### 文档站标准配置

```python
html_sidebars = {
    '**': [
        'about.html',
        'searchfield.html',
        'navigation.html',
        'relations.html',
        'donate.html',
    ]
}
```

默认配置，包含所有组件。

### 首页定制

```python
html_sidebars = {
    'index': ['about.html', 'searchfield.html', 'navigation.html', 'donate.html'],
    '**': ['about.html', 'searchfield.html', 'navigation.html', 'relations.html'],
}
```

首页显示捐赠链接，内页不显示。

## 自定义侧边栏组件

开发自定义主题或深度定制 Alabaster 时，可以创建自己的侧边栏模板组件：

1. 在项目的 `_templates/` 目录下创建模板文件（如 `mytoc.html`）
2. 将其添加到 `html_sidebars` 列表中

```python
html_sidebars = {
    '**': [
        'about.html',
        'mytoc.html',       # 自定义目录组件
        'searchfield.html',
    ]
}
```

### 自定义模板示例：版本切换器

```jinja2
{# _templates/version-switcher.html #}
{% if theme_show_version_switcher %}
<div class="version-switcher">
  <h3>版本</h3>
  <select onchange="location.href=this.value">
    <option value="/en/latest/">最新版</option>
    <option value="/en/stable/">稳定版</option>
    <option value="/en/v1.0/">v1.0</option>
  </select>
</div>
{% endif %}
```

## 组件与 layout.html 的关系

侧边栏组件不直接包含在 `layout.html` 中——Sphinx 根据 `html_sidebars` 配置按顺序渲染各个组件，并将结果插入到主布局的侧边栏位置。`layout.html` 只负责整体页面骨架：

```jinja2
{# layout.html 中侧边栏渲染由 basic 主题处理 #}
{%- block sidebar1 %}
  {# Sphinx 在此处渲染 html_sidebars 中配置的组件 #}
{%- endblock %}
```

这种设计使得侧边栏组件的增删不需要修改 `layout.html`，完全通过配置控制。

## 相关概念

- [主题架构四要素](/concepts/02-theme-architecture.md)：模板继承机制
- [主题配置选项体系](/concepts/04-theme-options.md)：侧边栏相关配置项
- [高级定制开发](/concepts/06-customization-advanced.md)：自定义模板与 CSS
- [主题选项定制示例](/examples/custom-theme-options.md)
