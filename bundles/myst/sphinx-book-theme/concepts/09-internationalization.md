---
type: concept
title: 09 - 国际化与高级主题
description: 翻译系统使用方法、资产哈希缓存机制、子主题开发、与sphinx-external-toc/sphinx-copybutton等扩展协作
tags:
- sphinx-book-theme
- i18n
- translation
- sub-theme
- caching
generated: 2026-08-23
status: stable
stale_after: 2027-08-23
sources:
- src/sphinx_book_theme/__init__.py
- src/sphinx_book_theme/header_buttons/__init__.py
- src/sphinx_book_theme/assets/translations/
---

# 国际化与高级主题

## 国际化（i18n）

sphinx-book-theme 内置多语言支持，使用Sphinx的消息目录（message catalog）系统。

### 翻译系统架构

- **消息目录名**：`MESSAGE_CATALOG_NAME = "booktheme"`（F-032）
- **翻译目录**：`theme/sphinx_book_theme/static/locales/`（F-045）
- **构建时编译**：pyproject.toml 中 `additional-compiled-static-assets = ["locales/"]` 指定翻译在构建时编译（F-009）
- **翻译函数**：通过 `get_translation(MESSAGE_CATALOG_NAME)` 获取，注入 `context["translate"]`（F-068-F-069）

翻译文件源位于 `assets/translations/jsons/` 目录，以JSON格式存储（F-186）。

### 内置翻译键

SBT翻译了界面上的所有用户可见文字（F-187）：

| 翻译键 | 英文 |
|--------|------|
| Download notebook file | Download notebook file |
| Download source file | Download source file |
| Download this page | Download this page |
| Print to PDF | Print to PDF |
| Fullscreen mode | Fullscreen mode |
| Launch on | Launch on |
| Launch interactive content | Launch interactive content |
| Live Code | Live Code |
| Source repository | Source repository |
| Repository | Repository |
| Show source | Show source |
| Suggest edit | Suggest edit |
| Open an issue | Open an issue |
| Contents | Contents |
| Search | Search |
| By the | By the |
| Copyright | Copyright |
| Last updated on | Last updated on |
| Theme by the | Theme by the |
| Toggle navigation | Toggle navigation |
| next page | next page |
| previous page | previous page |
| Download notebook file | Download notebook file |

### 按钮翻译

按钮宏中所有用户可见文字通过 `translate()` 函数处理（F-153）：

```jinja2
{% if text %}<span class="btn__text-container">{{ translate(text) }}</span>{% endif %}
{% if tooltip %}title="{{ translate(tooltip) }}"{% endif %}
```

这意味着在模板中硬编码的文字也会被翻译。

### 添加自定义翻译

要添加新语言的翻译：

1. 在Sphinx项目中配置语言：
   ```python
   language = "zh_CN"
   ```
2. 使用Sphinx的 `sphinx-intl` 工具提取和翻译消息
3. SBT自带的翻译文件位于其 `static/locales/` 目录

## 资产哈希与缓存清除

SBT通过SHA-1哈希实现静态资源的缓存清除（cache busting），确保用户在CSS/JS更新后始终加载最新版本。

### 工作机制

1. `_gen_hash(path)` 计算文件内容的SHA-1哈希值，使用 `@lru_cache(maxsize=None)` 缓存结果避免重复计算（F-078-F-079）
2. `hash_html_assets` 在每个页面渲染时被调用（F-121-F-132）
3. `hash_assets_for_files` 遍历资源列表：
   - 根据扩展名判断资源类型（.css → css_files，其他 → script_files）
   - 在context的资源列表中查找匹配项
   - 删除旧条目
   - 使用 `app.add_css_file()` / `app.add_js_file()` 重新添加带 `digest` 参数的版本（F-114-F-118）

### 哈希的资源列表

- 默认哈希：`scripts/sphinx-book-theme.js`（始终哈希）
- 条件哈希：`styles/sphinx-book-theme.css`（仅当 `html_theme == "sphinx_book_theme"` 时，避免影响子主题）（F-066）

### 子主题兼容

子主题继承SBT但使用自己的CSS文件时，SBT的CSS哈希不会执行——因为 `app.config.html_theme` 不等于 `"sphinx_book_theme"`（F-130）。这是一个重要的保护措施，避免子主题的CSS被错误地加上SBT CSS的哈希。

## 子主题开发

SBT基于PST，支持子主题开发。关键要点：

1. **theme.conf继承**：
   ```ini
   [theme]
   inherit = sphinx_book_theme
   ```

2. **CSS注意事项**：
   - SBT的CSS哈希仅在直接使用SBT主题时执行
   - 子主题需自行处理CSS缓存清除
   - 可以覆盖SBT的SCSS变量

3. **模板覆盖**：
   - 在子主题的templates目录创建同名模板即可覆盖SBT组件
   - 使用 `{% extends "!sphinx_book_theme/..." %}` 继承SBT模板

4. **静态资源**：
   - SBT的JS文件始终被注册和哈希
   - 子主题可以添加自己的JS文件
   - 平台Logo图标位于 `static/images/`

## 与其他Sphinx扩展协作

### sphinx-external-toc（外部目录）

SBT自身使用PST的 `generate_toctree_html()` 渲染侧边栏（`sbt-sidebar-nav.html`），与 sphinx-external-toc 可以配合使用。如果使用 sphinx-external-toc 替代Sphinx原生toctree，需要：

1. 确保 sphinx-external-toc 在 SBT 之后加载
2. 侧边栏导航由 sphinx-external-toc 的SiteMap控制

### sphinx-copybutton（代码复制按钮）

SBT的 `_code.scss` 内容样式与 sphinx-copybutton 兼容，两者可以无冲突地配合使用。

### sphinx-togglebutton（内容折叠）

SBT通过 `_sphinx-togglebutton.scss` 内置样式适配，直接安装使用即可：

```python
extensions = [
    "sphinx_book_theme",
    "sphinx_togglebutton",
]
```

### myst-nb（Jupyter笔记本执行）

SBT深度适配myst-nb：
- 自动检测笔记本页面（kernelspec元数据）显示启动按钮（F-252-F-262）
- MD文件笔记本自动复制ipynb到_sources目录（F-067-F-082）
- ipynb下载按钮自动出现
- `_myst-nb.scss` 样式适配
- 代码单元输出区域样式协调

### ablog（博客扩展）

ablog在SBT的doc依赖中列出（F-066），SBT与ablog兼容，可用于构建博客式文档站点。

## 已弃用功能

SBT会检查并警告已弃用的配置键（F-169-F-179）：

- `single_page`：从v0.3.4起弃用，会发出警告并链接到CHANGELOG

`expand_toc_sections` 也标记为待弃用（F-041）。

## 版本信息

- 当前版本：1.5.0.dev（开发版）（F-001）
- 开发状态：Beta（F-053）
- Python要求：>= 3.11（F-005）
- 核心依赖版本锁定：pydata-sphinx-theme == 0.20.0（F-044）

> **注意**：PST版本被严格锁定（`==0.20.0`），升级PST版本可能导致兼容性问题。SBT依赖PST的内部函数（如 `generate_toctree_html`、`config_provided_by_user`、`get_theme_options_dict`）和模板结构，PST的API变更可能导致SBT故障。

## 相关概念

- [主题概述](/concepts/00-introduction.md)
- [主题架构与PST继承](/concepts/02-theme-architecture.md)
- [布局与模板定制](/concepts/07-layout-and-templates.md)
- [样式定制与第三方扩展适配](/concepts/08-customization.md)
- [源码路径映射与配置速查](/references/sbt-source.md)
