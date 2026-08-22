---
type: Concept
title: 主题配置选项体系
description: Alabaster 的 50+ html_theme_options 完整参考——布局、颜色、字体、侧边栏、服务链接
tags: [sphinx, theme, alabaster, configuration, options, customization]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:56:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: alabaster-source
    resource: /references/alabaster-source.md
    title: Alabaster 源码路径映射
---

# 主题配置选项体系

Alabaster 通过 `html_theme_options` 字典提供 50+ 个配置选项，覆盖布局、颜色、字体、侧边栏组件、第三方服务集成等方面。这些选项在 `theme.conf` 中定义默认值，用户在 `conf.py` 中通过 `html_theme_options` 覆盖。

## 选项分类总览

| 类别 | 选项数 | 说明 |
|------|--------|------|
| 基础布局 | 8 | 页面宽度、侧边栏宽度、固定侧边栏等 |
| Logo 与描述 | 5 | Logo 图片、项目名、描述文字 |
| 服务链接与徽章 | 12 | GitHub、Travis、CodeCov、Google Analytics 等 |
| 侧边栏控制 | 4 | 目录折叠、隐藏项、相关链接、自定义链接 |
| 头部/底部选项 | 4 | Powered by、上下页导航栏 |
| 颜色配置 | 25+ | 全局色、文字色、链接色、侧边栏色、代码色、提示框色 |
| 字体配置 | 6 | 正文字体、代码字体、标题字体、字号 |

## 基础布局选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `page_width` | `940px` | 页面内容区域总宽度（CSS width 值） |
| `sidebar_width` | `220px` | 左侧边栏宽度 |
| `body_min_width` | `inherit` | body 最小宽度，移动端适配 |
| `fixed_sidebar` | `false` | 是否固定侧边栏（设为 `true` 时侧边栏不随页面滚动） |
| `body_text_align` | `left` | 正文文字对齐方式（`left`/`justify`/`center`） |

### 固定侧边栏效果

设置 `fixed_sidebar = True` 后，侧边栏在桌面端保持固定位置，正文区域独立滚动。这在长文档中非常实用——用户滚动阅读时导航始终可见。移动端（窄屏幕）不受影响，侧边栏会自动移到页面底部。

## Logo 与描述

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `logo` | （空） | Logo 图片路径，相对于 `_static/` 目录 |
| `logo_name` | `false` | 是否在 Logo 下方显示项目名。`true` 显示 `project` 配置值；字符串值显示自定义文字 |
| `logo_text_align` | `left` | Logo 文字对齐方式 |
| `description` | （空） | 项目简介文字，显示在 Logo 下方 |
| `description_font_style` | `normal` | 描述文字的 `font-style`（`normal`/`italic`） |
| `touch_icon` | （空） | iOS 主屏图标路径，相对于 `_static/` |

### Logo 配置示例

```python
html_theme_options = {
    'logo': 'logo.png',           # _static/logo.png
    'logo_name': True,            # 显示项目名
    'description': '一个强大的工具',
}
```

如果不设置 `logo`，则显示项目名称作为文本标题（链接到首页）。

## 服务链接与徽章

### GitHub 集成

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `github_user` | （空） | GitHub 用户名或组织名 |
| `github_repo` | （空） | GitHub 仓库名 |
| `github_button` | `true` | 是否显示 GitHub Star/Watch/Fork 按钮 |
| `github_type` | `watch` | 按钮类型：`watch`/`star`/`fork` |
| `github_count` | `true` | 是否显示计数（如 star 数） |
| `github_banner` | `false` | 是否显示右上角 "Fork me on GitHub" 角标。`true` 使用默认角标，字符串值为自定义图片路径 |

### CI/CD 徽章

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `travis_button` | `false` | Travis-CI 构建状态徽章。`true` 使用 github_user/repo，字符串值为 `"account/repo"` |
| `codecov_button` | `false` | CodeCov 测试覆盖率徽章。同上 |
| `badge_branch` | `master` | 徽章对应的分支名 |

### 分析与捐赠

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `analytics_id` | （空） | Google Analytics ID（如 `UA-XXXXXXX-XX`），启用页面访问追踪 |
| `donate_url` | （空） | 通用捐赠链接，显示一个 "Donate" 徽章 |
| `opencollective` | （空） | Open Collective 账户名，显示捐赠按钮 |
| `opencollective_button_color` | `white` | Open Collective 按钮颜色 |
| `tidelift_url` | （空） | Tidelift 商业支持链接 |

### 已废弃选项

- `gittip_user`/`gratipay_user`：对应服务已关闭，保留仅为向后兼容，无实际效果
- `canonical_url`：已废弃，推荐使用 Sphinx 内置 `html_baseurl` 配置
- `show_powered_by`：0.17.14 版本废弃，推荐使用 `html_show_sphinx = False`（在 `conf.py` 顶层设置，不在 `html_theme_options` 中）

## 侧边栏控制

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `sidebar_collapse` | `true` | 是否折叠非当前页面祖先的目录项 |
| `sidebar_includehidden` | `true` | 目录中是否包含 `:hidden:` 标记的 toctree 项 |
| `show_related` | `false` | 侧边栏是否显示"相关主题"（上下页）区域（`relations.html` 组件） |
| `extra_nav_links` | （空） | 额外导航链接字典，显示在目录树下方 |

### extra_nav_links 示例

```python
html_theme_options = {
    'extra_nav_links': {
        '项目主页': 'https://example.com',
        'Issue 追踪': 'https://github.com/user/repo/issues',
        'PyPI': 'https://pypi.org/project/mypackage',
    }
}
```

## 头部/底部导航

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `show_relbars` | `false` | 是否在正文区域的顶部和底部显示上下页导航栏 |
| `show_relbar_top` | （空） | 单独控制顶部导航栏，覆盖 `show_relbars` |
| `show_relbar_bottom` | （空） | 单独控制底部导航栏，覆盖 `show_relbars` |
| `relbar_border` | （空） | 导航栏与正文之间的边框颜色 |

> 💡 `show_relbars` 控制的是正文区域**内部**的上下页链接（页面顶部/底部），`show_related` 控制的是**侧边栏**中的相关链接。两者是独立的。

## 颜色配置

颜色值使用标准 CSS 颜色格式（十六进制如 `#004B6B`、RGB、颜色名）。

### 全局色板

| 选项 | 默认值 | 用途 |
|------|--------|------|
| `gray_1` | `#444` | 深灰色 |
| `gray_2` | `#EEE` | 浅灰色 |
| `gray_3` | `#AAA` | 中灰色 |
| `pink_1` | `#FCC` | 浅粉色 |
| `pink_2` | `#FAA` | 中粉色 |
| `pink_3` | `#D52C2C` | 深粉色/红色 |

### 主色

| 选项 | 默认值 | 用途 |
|------|--------|------|
| `base_bg` | `#fff` | 基础背景色 |
| `base_text` | `#000` | 基础文字色 |
| `body_bg` | （空） | body 背景色 |
| `body_text` | `#3E4349` | 正文文字色 |
| `link` | `#004B6B` | 链接颜色 |
| `link_hover` | `#6D4100` | 链接悬停颜色 |
| `footer_text` | `#888` | 页脚文字色 |
| `hr_border` | `#B1B4B6` | 水平分隔线颜色 |

### 侧边栏颜色

| 选项 | 默认值 | 用途 |
|------|--------|------|
| `sidebar_header` | （空） | 侧边栏标题色（默认继承） |
| `sidebar_text` | `#555` | 侧边栏文字色 |
| `sidebar_link` | （空） | 侧边栏链接色 |
| `sidebar_link_underscore` | `#999` | 侧边栏链接下划线色 |
| `sidebar_list` | `#000` | 侧边栏列表标记色 |
| `sidebar_hr` | （空） | 侧边栏分隔线色 |
| `sidebar_search_button` | `#CCC` | 搜索按钮背景色 |
| `narrow_sidebar_bg` | `#333` | 窄屏侧边栏背景色 |
| `narrow_sidebar_fg` | `#FFF` | 窄屏侧边栏文字色 |
| `narrow_sidebar_link` | （空） | 窄屏侧边栏链接色 |

### 代码与高亮

| 选项 | 默认值 | 用途 |
|------|--------|------|
| `code_bg` | `#ecf0f3` | 代码块/行内代码背景色 |
| `code_text` | `#222` | 代码文字色 |
| `code_hover` | `#EEE` | 代码行悬停背景色 |
| `code_highlight` | `#FFC` | `:emphasize-lines:` 高亮行背景色 |
| `highlight_bg` | `#FAF3E8` | 代码高亮区域背景色 |
| `pre_bg` | （空） | `<pre>` 块背景色 |
| `viewcode_target_bg` | `#ffd` | viewcode 扩展的目标行高亮色 |

### 锚点与表格

| 选项 | 默认值 | 用途 |
|------|--------|------|
| `anchor` | `#DDD` | 章节锚点（¶ 符号）颜色 |
| `anchor_hover_fg` | （空） | 锚点悬停前景色 |
| `anchor_hover_bg` | `#EAEAEA` | 锚点悬停背景色 |
| `table_border` | `#888` | 表格边框色 |

### 提示框（Admonition）颜色

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `admonition_bg` / `admonition_border` | （空）/ `#CCC` | 通用提示框 |
| `note_bg` / `note_border` | （空）/ `#CCC` | `.. note::` 提示 |
| `seealso_bg` / `seealso_border` | （空）/ `#CCC` | `.. seealso::` 提示 |
| `tip_bg` / `tip_border` | （空）/ `#CCC` | `.. tip::` 提示 |
| `hint_bg` / `hint_border` | （空）/ `#CCC` | `.. hint::` 提示 |
| `important_bg` / `important_border` | （空）/ `#CCC` | `.. important::` 提示 |
| `warn_bg` / `warn_border` | （空）/（空） | `.. warning::` 警告 |
| `danger_bg` / `danger_border` / `danger_shadow` | （空）| `.. danger::` 危险 |
| `error_bg` / `error_border` / `error_shadow` | （空）| `.. error::` 错误 |
| `footnote_bg` / `footnote_border` | `#FDFDFD` /（空）| 脚注块 |
| `xref_bg` / `xref_border` | `#FBFBFB` / `#fff` | 交叉引用 |

## 字体配置

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `font_family` | `Georgia, serif` | 正文字体系列 |
| `font_size` | `17px` | 正文字号 |
| `head_font_family` | （空） | 标题字体系列（默认 `Garamond, Georgia, serif`） |
| `code_font_family` | `Consolas, Menlo, DejaVu Sans Mono, ...` | 代码字体系列 |
| `code_font_size` | `0.9em` | 代码字号 |
| `caption_font_family` | `inherit` | 标题/说明文字字体系列 |
| `caption_font_size` | `inherit` | 标题/说明文字字号 |

## 在模板中访问选项

在 Jinja2 模板中，配置选项通过 `theme_<option_name>` 访问：

```jinja2
{% if theme_github_user and theme_github_repo %}
<a href="https://github.com/{{ theme_github_user }}/{{ theme_github_repo }}">
  GitHub
</a>
{% endif %}

<style>
  body { font-size: {{ theme_font_size }}; }
  a { color: {{ theme_link }}; }
</style>
```

布尔值选项需要使用 `|lower == 'true'` 或 `|tobool` 转换：

```jinja2
{%- if theme_fixed_sidebar|lower == 'true' %}
  <div class="fixed-sidebar">...</div>
{%- endif %}
```

这是因为 theme.conf 中的所有值都以字符串形式传递到模板中。

## 相关概念

- [快速开始](/concepts/01-getting-started.md)：最小配置示例
- [侧边栏组件化设计](/concepts/05-sidebar-components.md)：各侧边栏组件的选项
- [主题选项定制示例](/examples/custom-theme-options.md)：常见定制场景的完整配置
- [高级定制开发](/concepts/06-customization-advanced.md)：CSS 覆盖与主题二次开发
