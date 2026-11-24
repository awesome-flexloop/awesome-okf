---
type: Concept
title: 布局与模板区段
description: 三栏布局、九个页面区段、模板过滤机制与自定义模板接入
tags: [sphinx, theme, pydata, layout, templates]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T02:58:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-source-map
    resource: /references/source-map.md
    title: 源码路径映射
---

# 布局与模板区段

## 1. 页面骨架

PST 的页面是一个三层结构：

```text
┌─────────────────────────────────────────────────────────────┐
│ announcement（可选，可 sticky）                              │
├─────────────────────────────────────────────────────────────┤
│ header: navbar_start | navbar_center | navbar_persistent | navbar_end │
├───────────────┬─────────────────────────────┬───────────────┤
│ primary       │ article header              │ secondary     │
│ sidebar       │ article body                │ sidebar       │
│ (章节导航)     │ prev / next                 │ (页内 TOC)     │
├───────────────┴─────────────────────────────┴───────────────┤
│ footer-content                                              │
├─────────────────────────────────────────────────────────────┤
│ footer: footer_start | footer_center | footer_end            │
└─────────────────────────────────────────────────────────────┘
```

- 三栏默认固定宽度：主侧栏靠左、次侧栏靠右、正文居中。
- 缺一个侧栏时，正文在剩余空间居中；两个都缺时正文居中整页。
- 正文默认最大宽度 `60em`，整页容器 `88rem`。要放宽需分别覆盖 `.bd-article-container` 与 `.bd-page-width`，且保持为两条独立规则，否则选择器特异性不足。

## 2. 九个区段

| 区段文件 | 配置键 | 作用 |
|---|---|---|
| `sections/announcement.html` | `announcement` | 顶部公告条，可 sticky |
| `sections/header.html` | `navbar_start/center/end/persistent` | 站点级导航 |
| `sections/header-article.html` | `article_header_start/end` | 正文上方的面包屑/工具条 |
| `sections/sidebar-primary.html` | `sidebars`、`primary_sidebar_end` | 左侧章节导航与底部固定项 |
| `sections/sidebar-secondary.html` | `secondary_sidebar_items` | 右侧页内目录/编辑/源码链接 |
| `sections/footer-article.html` | `article_footer_items` | 正文之后的附加项 |
| `sections/footer-content.html` | `content_footer_items` | 正文与次侧栏下方的窄条 |
| `sections/footer.html` | `footer_start/center/end` | 页脚三区 |
| `sections/article.html` | — | 正文容器（通常不配置） |

每个区段的值都是**模板名列表**，列表顺序就是渲染顺序；`.html` 后缀可省略。

## 3. 模板过滤：空渲染即移除

`update_and_remove_templates` 对每个区段执行：

1. 字符串按逗号拆分为列表。
2. 无后缀的模板名补 `.html`。
3. 用当前页面上下文逐个渲染。
4. 渲染结果为空白（`len(rendered.strip()) == 0`）的模板被剔除。
5. `templates_skip_empty_check` 中的模板跳过第 4 步（避免昂贵渲染）。

这带来两个重要后果：

- **组件可以"自我隐藏"**：例如没有子页时 `sidebar-nav-bs.html` 渲染为空，侧栏自动让出空间。
- **配置错误可能静默**：模板名拼错时通常渲染为空并被移除，而不是报错。调试时应先单独渲染该模板。

默认跳过空检查的是 `sidebar-nav-bs.html` 与 `navbar-nav.html`，因为它们在大站点上渲染较慢，且总是期望存在。

## 4. 内置组件一览

| 组件 | 典型位置 | 说明 |
|---|---|---|
| `navbar-logo` | `navbar_start` | logo + 标题/替代文本 |
| `navbar-nav` | `navbar_center` | 顶层章节链接 + 外链 + More 下拉 |
| `navbar-icon-links` | `navbar_end` | FontAwesome/本地图片图标链接 |
| `theme-switcher` | `navbar_end` | light/dark/auto 切换 |
| `version-switcher` | 任意区段 | 多版本文档下拉 |
| `search-button-field` | `navbar_persistent` | 带快捷键提示的搜索按钮 |
| `search-button` | 任意区段 | 仅图标搜索按钮 |
| `search-field` | 侧栏/页脚 | 常驻搜索输入框 |
| `breadcrumbs` | `article_header_start` | 父页面链 |
| `page-toc` | `secondary_sidebar_items` | 页内目录 |
| `edit-this-page` | `secondary_sidebar_items` | 编辑链接 |
| `sourcelink` | `secondary_sidebar_items` | 查看源文件 |
| `prev-next` | 正文底部 | 上一页/下一页 |
| `copyright` / `sphinx-version` / `theme-version` | `footer_*` | 版权与版本信息 |
| `last-updated` | 任意区段 | 构建日期（需配合 `html_last_updated_fmt`） |
| `indices` | `primary_sidebar_end` | genindex/modindex 入口 |
| `sidebar-collapse` | `sidebars` | 侧栏折叠按钮 |
| `sidebar-nav-bs` | `sidebars` | Bootstrap 化章节树 |
| `sidebar-ethical-ads` | `primary_sidebar_end` | Read the Docs 伦理广告位 |
| `announcement` 相关 | — | 公告条渲染逻辑 |

## 5. 接入自定义模板

### 5.1 新建模板

在文档源目录创建 `_templates/`，并确保 `templates_path = ["_templates"]`（Sphinx 默认已包含）。

`_templates/build-info.html`：

```html+jinja
<div class="build-info">
  Built with Sphinx {{ sphinx_version }} · theme {{ theme_version }}
</div>
```

### 5.2 放入区段

```python
html_theme_options = {
    "footer_center": ["build-info"],
}
```

### 5.3 覆盖内置组件

用 `!` 前缀继承原模板，只改一个块：

```html+jinja
{% extends "!components/edit-this-page.html" %}

{% block edit_this_page_text %}
  Edit this page
{% endblock %}
```

### 5.4 自定义主侧栏

`html_sidebars` 是 Sphinx 原生配置，按页面模式指定主侧栏模板：

```python
html_sidebars = {
    "**": ["sidebar-collapse", "sidebar-nav-bs"],
    "reference/api/*": ["sidebar-nav-bs"],  # 去掉折叠按钮
}
```

要彻底移除某页主侧栏：`"pagename": []`；移除全站：`"**": []`。

## 6. 常见布局调整

| 目标 | 配置 |
|---|---|
| 顶部导航内容左对齐 | `"navbar_align": "left"` |
| 顶部导航右对齐 | `"navbar_align": "right"` |
| 隐藏上一页/下一页 | `"show_prev_next": False` |
| 页脚横向排列 | CSS：`.footer-items__start, .footer-items__end { flex-direction: row; }` |
| 正文占满整宽 | 两条独立 CSS 规则，分别覆盖 `.bd-article-container` 与 `.bd-page-width` |
| 某页去掉右侧栏 | 页面元数据 `html_theme.sidebar_secondary.remove: true` |
| 某页自定义右侧栏 | `"secondary_sidebar_items": {"path/*": ["page-toc"]}` |

## 7. 排错顺序

1. 页面是否包含 `pst-` 类名？否则主题未生效。
2. 区段配置是否是列表（或可解析的逗号字符串）？
3. 模板文件是否在 `templates_path` 可达目录？
4. 单独渲染该模板是否为空？
5. 是否被 `templates_skip_empty_check` 影响？
6. 是否被页面级元数据覆盖（如 `sidebar_secondary.remove`）？

## 相关概念

- [导航与 toctree](04-navigation-and-toctree.md)
- [页内目录与次级侧栏](05-page-toc-and-secondary-sidebar.md)
- [主题配置项](06-theme-options.md)
- [自定义组件示例](../examples/05-custom-components.md)
