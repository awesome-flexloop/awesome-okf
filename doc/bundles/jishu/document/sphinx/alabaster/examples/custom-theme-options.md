---
type: Example
title: 主题选项定制示例
description: 常见定制场景的 html_theme_options 配置——GitHub 集成、配色方案、固定侧边栏、捐赠链接等
tags: [sphinx, theme, alabaster, example, customization, options]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: alabaster-source
    resource: /references/alabaster-source.md
    title: Alabaster 源码路径映射
---

# 主题选项定制示例

本文档提供常见定制场景的 `html_theme_options` 配置片段，可直接复制组合使用。

## 场景一：开源项目标准配置

适用于托管在 GitHub 上的 Python 开源项目，包含 GitHub 按钮/角标、描述、固定侧边栏。

```python
html_theme_options = {
    'description': '一个强大的 Python 工具库',
    'github_user': 'your-username',
    'github_repo': 'your-project',
    'github_button': True,
    'github_type': 'star',
    'github_count': True,
    'github_banner': True,              # 右上角 "Fork me" 角标
    'fixed_sidebar': True,              # 固定侧边栏
    'show_powered_by': False,
    'show_related': False,
    'sidebar_collapse': True,
    'extra_nav_links': {
        'PyPI': 'https://pypi.org/project/your-project',
        'Issue Tracker': 'https://github.com/your-username/your-project/issues',
        '源码': 'https://github.com/your-username/your-project',
    },
}
```

## 场景二：蓝色主题配色

替换默认的青色/棕色链接为蓝色系，代码块使用浅色背景。

```python
html_theme_options = {
    'description': '蓝色风格文档',

    # 链接色
    'link': '#2c5aa0',
    'link_hover': '#1a3a70',

    # 侧边栏
    'sidebar_text': '#444',
    'sidebar_link': '#2c5aa0',
    'sidebar_link_underscore': '#a0c0e0',
    'sidebar_header': '#1a3a70',

    # 代码块
    'code_bg': '#f0f4f8',
    'code_text': '#1a1a2e',
    'code_highlight': '#d0e8ff',

    # 提示框
    'note_bg': '#e7f3ff',
    'note_border': '#2196F3',
    'seealso_bg': '#e7f3ff',
    'seealso_border': '#2196F3',
    'warn_bg': '#fff3cd',
    'warn_border': '#ffc107',

    # 页脚
    'footer_text': '#888',
}
```

## 场景三：深色代码主题

正文保持浅色，代码块使用深色背景（类似 Monokai/Dracula 风格）。

```python
html_theme_options = {
    'description': '深色代码主题',

    # 注意：Alabaster 的代码高亮背景通过 code_bg 设置
    # 深色代码块需要配合 custom.css 设置 pre/code 的前景色
    'code_bg': '#282c34',
    'code_text': '#abb2bf',
    'highlight_bg': '#282c34',
    'code_highlight': '#3e4451',

    # 其他配色保持默认
    'anchor': '#3e4451',
    'anchor_hover_bg': '#3e4451',
}
```

配合 `_static/custom.css` 完善深色代码块：

```css
/* 深色代码块文字颜色 */
pre {
    color: #abb2bf !important;
    border: none;
    border-radius: 6px;
    padding: 16px;
}

pre .k { color: #c678dd !important; }  /* Keyword */
pre .s { color: #98c379 !important; }  /* String */
pre .n { color: #e06c75 !important; }  /* Name */
pre .c { color: #5c6370 !important; font-style: italic; }  /* Comment */
pre .nb { color: #61afef !important; } /* Name.Builtin */
pre .nf { color: #61afef !important; } /* Name.Function */
pre .m { color: #d19a66 !important; }  /* Number */
```

## 场景四：宽屏文档布局

增大页面宽度，适合 API 文档或教程。

```python
html_theme_options = {
    'description': '宽屏布局示例',

    # 页面宽度
    'page_width': '1200px',
    'sidebar_width': '260px',
    'body_min_width': 'auto',

    # 正文字号
    'font_size': '16px',
    'code_font_size': '0.85em',

    # 字体
    'font_family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    'code_font_family': '"Fira Code", "JetBrains Mono", Consolas, monospace',
    'head_font_family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',

    'fixed_sidebar': True,
}
```

## 场景五：文档站配置（无 GitHub 按钮）

适用于公司内部文档站或非 GitHub 托管项目。

```python
html_theme_options = {
    'description': '内部工具库文档',
    'logo': 'company-logo.png',
    'logo_name': False,

    # 禁用 GitHub 相关功能
    'github_button': False,
    'github_banner': False,

    # 外部导航链接替代
    'extra_nav_links': {
        '公司主页': 'https://example.com',
        'API 文档': '/api/',
        '更新日志': '/changelog.html',
    },

    'show_powered_by': False,
    'show_related': True,
    'fixed_sidebar': True,

    # 公司品牌色
    'link': '#e74c3c',
    'link_hover': '#c0392b',
}
```

## 场景六：带捐赠/支持链接

适用于接受社区捐赠的开源项目。

```python
html_theme_options = {
    'description': '开源项目文档',
    'github_user': 'your-username',
    'github_repo': 'your-project',
    'github_button': True,

    # 捐赠方式
    'donate_url': 'https://github.com/sponsors/your-username',
    # 或使用 Open Collective
    # 'opencollective': 'your-project',
    # 'opencollective_button_color': 'white',

    # Tidelift 商业支持
    # 'tidelift_url': 'https://tidelift.com/subscription/pkg/pypi-your-project',

    'fixed_sidebar': True,
    'show_powered_by': False,
}
```

注意：需要在 `html_sidebars` 中包含 `donate.html` 才能显示捐赠区块。

## 场景七：文档多版本导航（配合 custom.css）

通过 `extra_nav_links` 模拟版本切换器（真正的版本切换需要 JavaScript）。

```python
html_theme_options = {
    'description': '多版本文档',
    'github_user': 'your-username',
    'github_repo': 'your-project',
    'extra_nav_links': {
        '📄 最新版 (stable)': '/en/stable/',
        '🧪 开发版 (dev)': '/en/latest/',
        '📚 v1.0': '/en/v1.0/',
        '📚 v0.9': '/en/v0.9/',
    },
    'fixed_sidebar': True,
}
```

## 选项组合注意事项

1. **布尔选项的字符串值**：`theme.conf` 中所有选项都是字符串。在模板中通过 `|lower == 'true'` 判断，但在 `conf.py` 的 `html_theme_options` 中使用 Python 布尔值 `True`/`False` 即可。

2. **`show_powered_by` 已废弃**：Alabaster 0.17.14+ 推荐在 `conf.py` 顶层设置 `html_show_sphinx = False`，而不是在 `html_theme_options` 中设置 `show_powered_by`。

3. **`canonical_url` 已废弃**：使用 Sphinx 内置的 `html_baseurl = 'https://docs.example.com/'` 代替。

4. **颜色值格式**：使用 CSS 标准格式——十六进制（`#004B6B`）、RGB（`rgb(0, 75, 107)`）或颜色名。十六进制推荐 6 位完整格式。

5. **`extra_nav_links` 的顺序**：字典在 Python 3.7+ 中保持插入顺序，链接按代码中书写的顺序显示。

## 相关概念

- [主题配置选项体系](../concepts/04-theme-options.md)：50+ 选项完整参考
- [基础配置示例](basic-setup.md)：完整 conf.py 模板
- [自定义 CSS 与品牌化](custom-css-and-branding.md)：CSS 覆盖进阶
