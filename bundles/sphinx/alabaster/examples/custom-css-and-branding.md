---
type: Example
title: 自定义 CSS 与品牌化
description: 通过 custom.css 深度定制 Alabaster 外观——品牌配色、自定义字体、深色模式、布局调整
tags: [sphinx, theme, alabaster, example, css, branding, dark-mode]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:01:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: alabaster-source
    resource: /references/alabaster-source.md
    title: Alabaster 源码路径映射
---

# 自定义 CSS 与品牌化

本文档通过实战案例演示如何使用 `custom.css` 对 Alabaster 进行深度视觉定制，包括品牌配色、字体替换、深色模式和布局调整。

## 前提条件

确保 `conf.py` 中配置了静态文件路径：

```python
html_static_path = ['_static']
```

在 `_static/` 目录下创建 `custom.css`。Alabaster 会自动加载此文件（在默认样式之后加载，因此可以覆盖默认样式）。

## 案例一：品牌配色定制

将文档主题色改为品牌色（以紫色品牌为例）。

```css
/* _static/custom.css — 紫色品牌主题 */

/* 链接颜色 */
a {
    color: #7c3aed;
}
a:hover {
    color: #5b21b6;
}
a:visited {
    color: #6d28d9;
}

/* 侧边栏链接 */
div.sphinxsidebar a {
    color: #7c3aed;
    border-bottom-color: #ddd6fe;
}
div.sphinxsidebar a:hover {
    border-bottom-color: #7c3aed;
}

/* 侧边栏标题 */
div.sphinxsidebar h3 {
    color: #5b21b6;
    font-family: Georgia, serif;
}

/* 代码块链接 */
div.body a code {
    color: #7c3aed;
}

/* 提示框 - note 使用品牌色 */
div.note {
    background-color: #f5f3ff;
    border: 1px solid #c4b5fd;
    border-left: 4px solid #7c3aed;
}

/* 警告框 */
div.warning {
    background-color: #fffbeb;
    border: 1px solid #fcd34d;
    border-left: 4px solid #f59e0b;
}

/* 版本添加/变更标记 */
.versionadded {
    background-color: #ecfdf5;
    border-left: 4px solid #10b981;
}
.versionchanged {
    background-color: #eff6ff;
    border-left: 4px solid #3b82f6;
}
.deprecated {
    background-color: #fef2f2;
    border-left: 4px solid #ef4444;
}
```

配合 `conf.py` 中的颜色选项：

```python
html_theme_options = {
    'link': '#7c3aed',
    'link_hover': '#5b21b6',
    'code_bg': '#f5f3ff',
    'note_bg': '#f5f3ff',
    'note_border': '#c4b5fd',
    'sidebar_link': '#7c3aed',
    'sidebar_link_underscore': '#ddd6fe',
}
```

## 案例二：自定义字体

使用系统字体栈或 Web 字体替换默认 Georgia/Consolas。

### 方案 A：现代系统字体栈

```css
/* _static/custom.css — 系统字体 */

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, "Noto Sans SC", "PingFang SC",
                 "Microsoft YaHei", sans-serif;
    font-size: 16px;
    line-height: 1.75;
}

h1, h2, h3, h4, h5, h6 {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, "Noto Sans SC", "PingFang SC",
                 sans-serif;
    font-weight: 600;
    color: #1a1a2e;
}

code, pre, kbd, samp {
    font-family: "JetBrains Mono", "Fira Code", "Cascadia Code",
                 Consolas, "Courier New", monospace;
    font-size: 0.9em;
}

/* 代码块优化 */
pre {
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    padding: 16px 20px;
    line-height: 1.6;
}

/* 行内代码 */
code {
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.9em;
}
```

### 方案 B：引入 Google Fonts

在 `conf.py` 中添加额外的 CSS 链接：

```python
# conf.py
html_css_files = [
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap',
]
```

```css
/* _static/custom.css — Google Fonts */

body {
    font-family: 'Inter', -apple-system, sans-serif;
}

code, pre {
    font-family: 'JetBrains Mono', Consolas, monospace;
}
```

## 案例三：固定宽度内容区

Alabaster 默认内容宽度为 940px，可通过 CSS 调整。

```css
/* _static/custom.css — 宽屏布局 */

div.document {
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;
}

div.bodywrapper {
    margin: 0 0 0 300px;  /* 侧边栏宽度调整 */
}

div.sphinxsidebar {
    width: 300px;          /* 侧边栏宽度 */
}

div.body {
    min-width: auto;
    max-width: 1000px;    /* 正文最大阅读宽度 */
    padding: 0 40px;
}

/* 适配超宽屏幕 */
@media screen and (min-width: 1600px) {
    div.document {
        max-width: 1600px;
    }
    div.body {
        max-width: 1200px;
    }
}
```

## 案例四：自动深色模式

使用 CSS `prefers-color-scheme` 媒体查询实现自动深色模式。

```css
/* _static/custom.css — 自动深色模式 */

@media (prefers-color-scheme: dark) {
    /* 基础背景与文字 */
    body {
        background-color: #1a1a2e !important;
        color: #e0e0e0 !important;
    }

    div.document {
        background-color: #1a1a2e !important;
    }

    div.body {
        background-color: #16213e !important;
        color: #e0e0e0 !important;
    }

    div.bodywrapper {
        background-color: #16213e !important;
    }

    /* 侧边栏 */
    div.sphinxsidebar {
        background-color: #0f3460 !important;
        color: #c0c0c0 !important;
    }

    div.sphinxsidebar h3,
    div.sphinxsidebar h4 {
        color: #e94560 !important;
    }

    div.sphinxsidebar a {
        color: #53a8b6 !important;
        border-bottom-color: #53a8b640 !important;
    }

    /* 链接 */
    a {
        color: #53a8b6 !important;
    }
    a:hover {
        color: #7fdbda !important;
    }
    a:visited {
        color: #9b59b6 !important;
    }

    /* 标题 */
    h1, h2, h3, h4, h5, h6 {
        color: #e94560 !important;
    }

    /* 代码块 */
    pre {
        background-color: #0f0f23 !important;
        color: #e0e0e0 !important;
        border: 1px solid #2d2d44 !important;
    }

    code {
        background-color: #2d2d44 !important;
        color: #f8c555 !important;
    }

    /* 水平线 */
    hr {
        border-color: #2d2d44 !important;
    }

    /* 表格 */
    table.docutils {
        border-color: #2d2d44 !important;
    }
    table.docutils th,
    table.docutils td {
        background-color: #16213e !important;
        border-color: #2d2d44 !important;
        color: #e0e0e0 !important;
    }
    table.docutils th {
        background-color: #0f3460 !important;
    }

    /* 提示框 */
    div.note {
        background-color: #1a3a5c !important;
        border-color: #2980b9 !important;
        color: #e0e0e0 !important;
    }

    div.warning {
        background-color: #3d2e0a !important;
        border-color: #f39c12 !important;
        color: #e0e0e0 !important;
    }

    /* 页脚 */
    div.footer {
        background-color: #0f3460 !important;
        color: #888 !important;
        border-top: 1px solid #2d2d44 !important;
    }

    /* 搜索框 */
    div.sphinxsidebar input[type="text"] {
        background-color: #0f0f23 !important;
        color: #e0e0e0 !important;
        border: 1px solid #2d2d44 !important;
    }
}
```

## 案例五：自定义 Logo 区域样式

```css
/* _static/custom.css — Logo 区域美化 */

p.logo {
    margin-bottom: 10px;
    text-align: center;
}

p.logo img.logo {
    max-width: 160px;
    height: auto;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h1.logo a {
    font-size: 1.6em;
    font-weight: 700;
    background: linear-gradient(135deg, #7c3aed, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-decoration: none;
    border-bottom: none !important;
}

p.blurb {
    font-size: 0.9em;
    color: #666;
    font-style: italic;
    text-align: center;
    margin-bottom: 15px;
}
```

## 案例六：隐藏不需要的元素

```css
/* _static/custom.css — 精简界面 */

/* 隐藏页脚 "Page source" 链接 */
div.footer a[href*="_sources"] {
    display: none;
}

/* 隐藏侧边栏 "Navigation" 标题（保留导航树） */
div.sphinxsidebar h3:first-of-type {
    display: none;
}

/* 隐藏侧边栏搜索框（如果不需要搜索） */
/* div.sphinxsidebar form { display: none; } */

/* 移动端隐藏 GitHub 角标（避免遮挡） */
@media screen and (max-width: 768px) {
    a.github {
        display: none !important;
    }
}
```

## 调试技巧

使用浏览器开发者工具（F12）定位元素和选择器：

1. 右键点击要修改的元素 → "检查"
2. 在 Elements 面板中查看元素的 class 和 CSS 规则
3. 在 Styles 面板中实时编辑 CSS 预览效果
4. 将满意的规则复制到 `custom.css`

### Alabaster 常用 CSS 类名

| 选择器 | 对应元素 |
|--------|---------|
| `div.document` | 文档主容器 |
| `div.bodywrapper` | 正文包装器 |
| `div.body` | 正文内容区 |
| `div.sphinxsidebar` | 左侧边栏 |
| `div.sphinxsidebarwrapper` | 边栏内容包装器 |
| `div.footer` | 页脚 |
| `div.related` | 上下页导航栏 |
| `pre` | 代码块 |
| `code` | 行内代码 |
| `div.note` / `div.warning` / `div.tip` | 提示框 |
| `a.github` | GitHub 角标 |
| `p.logo` / `p.blurb` | Logo 和描述区 |

## 相关概念

- [高级定制开发](/concepts/06-customization-advanced.md)：custom.css 机制详解
- [主题配置选项体系](/concepts/04-theme-options.md)：可通过配置选项调整的样式
- [主题选项定制示例](custom-theme-options.md)：html_theme_options 配置
