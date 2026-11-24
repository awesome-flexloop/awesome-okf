---
type: Reference
title: 主题配置项速查表
description: theme.conf 全部键的分组速查、默认值与所属行为
tags: [sphinx, theme, pydata, reference, options]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T03:40:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-theme-conf
    resource: https://github.com/pydata/pydata-sphinx-theme/blob/main/src/pydata_sphinx_theme/theme/pydata_sphinx_theme/theme.conf
    title: theme.conf
---

# 主题配置项速查表

来源：`theme.conf [options]`（约 50 键，含 2 个废弃别名）。用法：写入 `html_theme_options`。

## 通用

| 键 | 默认 | 说明 |
|---|---|---|
| `sidebar_includehidden` | `True` | 侧栏包含隐藏 toctree |
| `use_edit_page_button` | `False` | 显示编辑此页 |
| `show_prev_next` | `True` | 上一页/下一页 |
| `navigation_with_keys` | `False` | 方向键导航 |
| `collapse_navigation` | `False` | 关闭折叠导航 |
| `navigation_depth` | `4` | 侧栏层级 |
| `show_nav_level` | `1` | 首屏展开层级；0=按 caption 折叠 |
| `show_toc_level` | `1` | 页内 TOC 展开层级 |
| `navbar_align` | `content` | content/left/right |
| `header_links_before_dropdown` | `5` | More 下拉阈值 |
| `header_dropdown_text` | `More` | 下拉文案 |
| `back_to_top_button` | `True` | 回到顶部按钮 |
| `shorten_urls` | `True` | 缩短 GitHub/GitLab 链接 |
| `surface_warnings` | `True` | 主题告警级别 |

## 导航与链接

| 键 | 默认 | 说明 |
|---|---|---|
| `external_links` | 空 | 顶部外链列表 |
| `icon_links` | 空 | 图标链接列表 |
| `icon_links_label` | `Icon Links` | 图标区 aria-label |
| `github_url` | 空 | GitHub 快捷链接（转 icon_links） |
| `gitlab_url` | 空 | GitLab 快捷链接 |
| `bitbucket_url` | 空 | Bitbucket 快捷链接 |
| `twitter_url` | 空 | Twitter 快捷链接 |
| `logo` | 空 | 双模式 logo 字典 |
| `logo_link` | 空 | 旧式 logo 链接 |
| `switcher` | 空 | 版本切换器配置 |
| `check_switcher` | `True` | 构建期校验 switcher JSON |
| `show_version_warning_banner` | `False` | 版本警告横幅 |
| `sticky_banners` | `False` | 横幅固定顶部 |
| `announcement` | 空 | 公告 HTML 或 URL |

## 搜索

| 键 | 默认 | 说明 |
|---|---|---|
| `search_bar_text` | `Search the docs ...` | 搜索框占位 |
| `search_as_you_type` | `False` | 即时搜索 |
| `disable_search` | `False` | 禁用内置搜索 |

## 高亮

| 键 | 默认 | 说明 |
|---|---|---|
| `pygments_light_style` | `a11y-high-contrast-light` | light 高亮 |
| `pygments_dark_style` | `a11y-high-contrast-dark` | dark 高亮 |
| `pygment_light_style` | 空 | 废弃别名 |
| `pygment_dark_style` | 空 | 废弃别名 |

## 模板区段

| 键 | 默认 |
|---|---|
| `navbar_start` | `navbar-logo` |
| `navbar_center` | `navbar-nav` |
| `navbar_end` | `theme-switcher, navbar-icon-links` |
| `navbar_persistent` | `search-button-field` |
| `article_header_start` | `breadcrumbs` |
| `article_header_end` | 空 |
| `article_footer_items` | 空 |
| `content_footer_items` | 空 |
| `primary_sidebar_end` | `sidebar-ethical-ads` |
| `footer_start` | `copyright, sphinx-version` |
| `footer_center` | 空 |
| `footer_end` | `theme-version` |
| `secondary_sidebar_items` | `page-toc, edit-this-page, sourcelink` |
| `templates_skip_empty_check` | `sidebar-nav-bs.html, navbar-nav.html` |

## 分析

| 键 | 默认 | 说明 |
|---|---|---|
| `analytics` | 空 | Plausible 或 Google Analytics 配置 |

## 不在 theme.conf 但常一起用

| 配置 | 位置 | 说明 |
|---|---|---|
| `html_sidebars` | Sphinx | 主侧栏按页模板 |
| `html_logo` | Sphinx | 单 logo 回退 |
| `html_favicon` | Sphinx | favicon |
| `html_css_files` / `html_js_files` | Sphinx | 自定义资源 |
| `html_show_sourcelink` | Sphinx | 查看源码链接 |
| `html_permalinks_icon` | Sphinx | 标题锚点符号（默认被主题设为 `#`） |
| `html_last_updated_fmt` | Sphinx | 构建日期 |
| `html_baseurl` | Sphinx | canonical/sitemap 基址 |
