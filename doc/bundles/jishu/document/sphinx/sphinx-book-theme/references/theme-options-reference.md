---
type: Reference
title: "主题选项速查"
description: "sphinx_book_theme 的 theme.conf 全部选项、默认值、模板变量与类型注意事项，附继承自 pydata-sphinx-theme 的常用选项"
tags: [sphinx, theme, reference, options, theme.conf, html_theme_options]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-theme-conf
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme/src/sphinx_book_theme/theme/sphinx_book_theme/theme.conf
    title: theme.conf
---

# 主题选项速查

所有选项写在 `conf.py` 的 `html_theme_options` 字典中。模板中通过 `theme_<选项名>` 读取。

## 声明在本书主题 theme.conf 的选项

| 选项 | 默认值 | 模板变量 | 类型 | 备注 |
|------|--------|---------|------|------|
| `announcement` | 空 | `theme_announcement` | str/HTML | 顶部公告 |
| `secondary_sidebar_items` | `page-toc.html` | `theme_secondary_sidebar_items` | str/list | 右侧栏组件 |
| `toc_title` | `Contents` | `theme_toc_title` | str | 页内目录标题 |
| `article_header_start` | `toggle-primary-sidebar.html` | `theme_article_header_start` | str/list | 工具条左侧 |
| `article_header_end` | `article-header-buttons.html` | `theme_article_header_end` | str/list | 工具条右侧 |
| `use_download_button` | `True` | `theme_use_download_button` | bool | 下载组 |
| `use_fullscreen_button` | `True` | `theme_use_fullscreen_button` | bool | 全屏按钮 |
| `use_issues_button` | `False` | `theme_use_issues_button` | bool | GitHub/GitLab |
| `use_source_button` | `False` | `theme_use_source_button` | bool | 查看源码 |
| `use_repository_button` | `False` | `theme_use_repository_button` | bool | 仓库首页 |
| `path_to_docs` | 空 | `theme_path_to_docs` | str | 相对仓库根 |
| `repository_url` | 空 | `theme_repository_url` | str | 最后两段为 org/repo |
| `repository_branch` | 空 → `main` | `theme_repository_branch` | str | 分支 |
| `repository_provider` | 空 → 推断 | `theme_repository_provider` | str | github/gitlab/bitbucket |
| `launch_buttons` | `{}` | `theme_launch_buttons` | dict | 启动服务 |
| `navbar_start` | 空 | `theme_navbar_start` | str/list | 页眉左 |
| `navbar_center` | 空 | `theme_navbar_center` | str/list | 页眉中 |
| `navbar_end` | 空 | `theme_navbar_end` | str/list | 页眉右 |
| `navbar_persistent` | 空（运行时 `[]`） | `theme_navbar_persistent` | str/list | 移动端常驻 |
| `home_page_in_toc` | `False` | `theme_home_page_in_toc` | bool | 首页入目录 |
| `show_navbar_depth` | `1` | `theme_show_navbar_depth` | int | 默认展开层数 |
| `max_navbar_depth` | `4` | `theme_max_navbar_depth` | int | 最大渲染层数 |
| `collapse_navbar` | `False` | `theme_collapse_navbar` | bool | 禁用展开 |
| `extra_footer` | 空 | `theme_extra_footer` | HTML | 内容页脚追加 |
| `footer_content_items` | `author.html, copyright.html, last-updated.html, extra-footer.html` | `theme_footer_content_items` | str/list | 内容页脚组件 |
| `footer_start` | 空 | `theme_footer_start` | str/list | 站点页脚左 |
| `footer_end` | 空 | `theme_footer_end` | str/list | 站点页脚右 |
| `use_sidenotes` | `False` | `theme_use_sidenotes` | bool | 脚注转边注 |
| `expand_toc_sections` | `[]` | `theme_expand_toc_sections` | list | 已废弃 |

## 继承自 pydata-sphinx-theme 的常用选项

| 选项 | 典型值 | 作用 |
|------|--------|------|
| `logo` | `{"image_light": "...", "image_dark": "...", "text": "..."}` | 高级 logo |
| `icon_links` | `[{"name": "...", "url": "...", "icon": "..."}]` | 侧栏图标链接 |
| `use_edit_page_button` | `True` | 建议编辑 |
| `search_as_you_type` | `True` | 搜索即输 |
| `show_toc_level` | `2` | 页内目录常驻层级 |
| `navigation_with_keys` | `True` | 键盘翻页 |
| `switcher` | `{"json_url": "...", "version_match": "..."}` | 版本切换器 |
| `check_switcher` | `True` | 版本切换器校验 |
| `analytics` | `{"google_analytics_id": "..."}` | 分析脚本 |
| `primary_sidebar_end` | `["..."]` | 主侧栏末尾组件 |

> 父主题选项随版本变化；本书主题锁定 `pydata-sphinx-theme==0.23.0`。升级父主题时以该版本文档为准。

## 类型注意事项

### 布尔值

`theme.conf` 里的布尔可能以字符串到达模板。Python 用 `as_bool()`，Jinja 用 `|tobool`：

```python
from sphinx_book_theme.header_buttons import as_bool
enabled = as_bool(opts.get("use_download_button", True))
```

```jinja
{% if theme_collapse_navbar|tobool %}...{% endif %}
```

### 列表

`footer_content_items` 支持逗号分隔字符串或列表。`update_templates` 会拆分并补 `.html`：

```python
"footer_content_items": "author.html, copyright.html"
```

```python
"footer_content_items": ["author.html", "copyright.html"]
```

### 字典

`launch_buttons` 是嵌套字典，主题直接按 key 读取。未知 key 被忽略，不报错。

### 整数

`show_navbar_depth`、`max_navbar_depth` 在模板里用 `|int` 转换。写成字符串 `"2"` 通常也能工作，但建议写整数。

## 选项与页面区域的对应

```text
announcement                  → 顶部公告
navbar_{start,center,end,persistent} → 页眉
article_header_{start,end}    → 正文工具条
secondary_sidebar_items       → 右侧栏
show_navbar_depth / max_navbar_depth / collapse_navbar → 左侧目录
home_page_in_toc              → 左侧目录首页项
toc_title / show_toc_level    → 右侧目录
use_*_button                  → 页眉按钮
repository_* / path_to_docs   → 按钮 URL
launch_buttons                → 在线运行按钮
footer_content_items / extra_footer → 内容页脚
footer_{start,end}            → 站点页脚
use_sidenotes                 → 边注变换
```

## 相关概念

- [配置选项全解](../concepts/04-theme-options.md)
- [页面分区与导航](../concepts/03-layout-and-navigation.md)
- [页眉按钮机制](../concepts/05-header-buttons.md)
