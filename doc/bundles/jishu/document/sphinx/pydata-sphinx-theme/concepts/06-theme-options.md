---
type: Concept
title: 主题配置项
description: html_theme_options 的分组参考、默认值、联动行为与废弃键迁移
tags: [sphinx, theme, pydata, configuration, theme-options]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T03:08:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-theme-conf
    resource: /references/theme-options-quickref.md
    title: 主题配置项速查表
  - id: pst-source-map
    resource: /references/source-map.md
    title: 源码路径映射
---

# 主题配置项

所有主题配置都写在 `conf.py` 的 `html_theme_options` 字典中。`theme.conf` 的 `[options]` 段定义默认值；`update_config()` 在 `builder-inited` 阶段做迁移、补全与校验。

```python
html_theme_options = {
    "navbar_align": "content",
    "show_nav_level": 2,
    "logo": {"text": "My Project", "image_dark": "_static/logo-dark.svg"},
}
```

## 1. 通用与布局

| 键 | 默认 | 作用 |
|---|---|---|
| `sidebar_includehidden` | `True` | 侧栏是否包含隐藏 toctree 条目 |
| `show_prev_next` | `True` | 正文底部上一页/下一页 |
| `navigation_with_keys` | `False` | 是否允许方向键翻页 |
| `collapse_navigation` | `False` | 关闭可折叠导航 |
| `navigation_depth` | `4` | 侧栏最大层级 |
| `show_nav_level` | `1` | 首屏展开层级；`0` 表示按 caption 折叠 |
| `show_toc_level` | `1` | 页内 TOC 首屏展开层级 |
| `navbar_align` | `content` | `content` / `left` / `right` |
| `header_links_before_dropdown` | `5` | 进入 More 下拉前的链接数 |
| `header_dropdown_text` | `More` | 下拉按钮文案 |
| `back_to_top_button` | `True` | 滚动后显示回到顶部按钮 |
| `shorten_urls` | `True` | 缩短 GitHub/GitLab 链接显示文本 |
| `surface_warnings` | `True` | 主题告警输出为 warning；`False` 降为 info |

## 2. 导航与链接

| 键 | 默认 | 作用 |
|---|---|---|
| `external_links` | 空 | 顶部外链列表 `[{name,url}]` |
| `icon_links` | 空 | 图标链接列表，支持 fontawesome/url/local |
| `icon_links_label` | `Icon Links` | 图标链接区的无障碍标签 |
| `github_url` / `gitlab_url` / `bitbucket_url` / `twitter_url` | 空 | 旧式单链接快捷配置，会转成 `icon_links` |
| `logo` | 空 | `{text, alt_text, image_light, image_dark, link}` |
| `logo_link` | 空 | 旧式 logo 链接，会写入 `logo["link"]` |
| `switcher` | 空 | `{json_url, version_match}` 版本切换器 |
| `check_switcher` | `True` | 构建期校验 switcher JSON |
| `show_version_warning_banner` | `False` | 非稳定版警告横幅 |
| `sticky_banners` | `False` | 公告与版本横幅固定在视口顶部 |
| `announcement` | 空 | 公告 HTML 或远程 URL |

## 3. 搜索

| 键 | 默认 | 作用 |
|---|---|---|
| `search_bar_text` | `Search the docs ...` | 搜索框占位文本 |
| `search_as_you_type` | `False` | 输入时即时返回结果 |
| `disable_search` | `False` | 移除搜索对话框；未显式设置时同时清空 `navbar_persistent` |

搜索按钮的放置由模板决定，默认在 `navbar_persistent = search-button-field`。若要常驻输入框，把 `search-field` 放进 `html_sidebars` 或 `navbar_end`。

## 4. 代码高亮

| 键 | 默认 | 作用 |
|---|---|---|
| `pygments_light_style` | `a11y-high-contrast-light` | light 模式高亮 |
| `pygments_dark_style` | `a11y-high-contrast-dark` | dark 模式高亮 |
| `pygment_light_style` / `pygment_dark_style` | 空 | 废弃别名，自动迁移并告警 |

主题会在 `build-finished` 用这两个样式生成双前缀的 `_static/pygments.css`；Sphinx 原生 `pygments_style` 会被覆盖。

## 5. 编辑与模板区段

| 键 | 默认 | 作用 |
|---|---|---|
| `use_edit_page_button` | `False` | 显示“编辑此页” |
| `navbar_start` | `navbar-logo` | 顶部左区 |
| `navbar_center` | `navbar-nav` | 顶部中区 |
| `navbar_end` | `theme-switcher, navbar-icon-links` | 顶部右区 |
| `navbar_persistent` | `search-button-field` | 窄屏也保留的右区 |
| `article_header_start` | `breadcrumbs` | 正文上方左区 |
| `article_header_end` | 空 | 正文上方右区 |
| `article_footer_items` | 空 | 正文之后 |
| `content_footer_items` | 空 | 正文与次侧栏下方 |
| `primary_sidebar_end` | `sidebar-ethical-ads` | 主侧栏底部 |
| `secondary_sidebar_items` | `page-toc, edit-this-page, sourcelink` | 次侧栏，支持按页字典 |
| `footer_start` | `copyright, sphinx-version` | 页脚左区 |
| `footer_center` | 空 | 页脚中区 |
| `footer_end` | `theme-version` | 页脚右区 |
| `templates_skip_empty_check` | `sidebar-nav-bs.html, navbar-nav.html` | 跳过空渲染检查的模板 |

## 6. 分析与第三方

| 键 | 默认 | 作用 |
|---|---|---|
| `analytics` | 空 | `{plausible_analytics_domain, plausible_analytics_url}` 或 `{google_analytics_id}` |

Plausible 会注册 defer 脚本；Google Analytics 会注入 consent 默认拒绝的 gtag 脚本。ABlog 场景下若未显式配置 `fontawesome_included`，主题会自动设为 `True`。

## 7. update_config 的联动行为

这些不是独立配置项，而是容易让人意外的副作用：

1. `disable_search=True` 且用户未设置 `navbar_persistent` → 设为 `[]`。
2. 用户未设置 `html_permalinks_icon` → 主题改为 `"#"`。
3. `github_url` 等四个快捷键 → 插入 `icon_links` 头部。
4. `theme_logo_link` → 写入 `logo["link"]`。
5. `switcher` 存在且 `check_switcher=True` → 构建期读取并校验 JSON。
6. `pygment_*_style` → 自动改名为 `pygments_*_style`。

## 8. 配置优先级

```text
html_theme_options（用户）
    > theme.conf [options]（主题默认）
    > Sphinx 内置默认
```

但要注意：

- `app.builder.theme_options` 是运行时权威副本；在 `builder-inited` 之后修改 `app.config.html_theme_options` 不会影响 Jinja 的 `theme_*` 变量。
- 页面级元数据（如 `html_theme.sidebar_secondary.remove`）优先级高于全局配置。
- `html_sidebars` 是 Sphinx 配置，不是 `html_theme_options` 的键。

## 9. 调试技巧

```python
# conf.py 临时打印最终主题选项
def setup(app):
    def dump(app):
        print(dict(app.builder.theme_options))
    app.connect("builder-inited", dump)
```

或在模板中输出：

```html+jinja
<!-- theme_navbar_align = {{ theme_navbar_align }} -->
```

## 相关概念

- [布局与模板区段](03-layout-and-sections.md)
- [品牌、样式与暗色模式](07-branding-styling-and-dark-mode.md)
- [搜索、版本切换与公告](08-search-versioning-and-announcements.md)
- [主题配置项速查表](../references/theme-options-quickref.md)
