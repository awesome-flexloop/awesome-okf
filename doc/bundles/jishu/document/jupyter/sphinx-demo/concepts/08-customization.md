---
type: Concept
title: 样式定制与主题扩展
description: 自定义 CSS 美化 TryExamples 按钮、PyData 主题图标链接、自定义 JavaScript 功能扩展
tags: [css, styling, customization, theme, pydata, icons]
difficulty: intermediate
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: customization
    resource: /references/conf-py-source.md
    title: _static/ 目录静态资源
---

## 自定义 CSS

所有自定义 CSS 文件放置在 `_static/` 目录中，通过 `html_css_files` 加载：

```python
html_static_path = ["_static"]
html_css_files = ["button_styling.css"]
```

### TryExamples 按钮美化

demo 的 `button_styling.css` 为 TryExamples 按钮添加了光泽悬停动画和圆角效果：

```css
.try_examples_button {
    color: white;
    background-color: #f37726;  /* Jupyter 品牌橙色 */
    padding: 10px 20px;
    border-radius: 8px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease;
}

/* 光泽扫过动画 */
.try_examples_button::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        120deg,
        transparent,
        rgba(255, 255, 255, 0.3),
        transparent
    );
    transition: none;
}

.try_examples_button:hover::before {
    animation: shine 0.5s ease forwards;
}

.try_examples_button:hover {
    transform: scale(1.05);
}
```

关键 CSS 选择器：

| 选择器 | 目标元素 |
|--------|---------|
| `.try_examples_button` | TryExamples 按钮 |
| `.try_examples_button_container` | 按钮容器 div |
| `.try_examples_iframe_container` | iframe 容器 |
| `.try_examples_iframe` | 嵌入的 JupyterLite iframe |

## 自定义 JavaScript

通过 `html_js_files` 加载自定义 JS：

```python
html_js_files = ["pypi.js"]
```

demo 的 `pypi.js` 在导航栏添加 PyPI 图标链接。自定义 JS 文件放在 `_static/` 目录中。

### 常用自定义场景

- 添加导航栏外部链接图标（如 PyPI、Conda Forge）
- 自定义 TryExamples 按钮行为
- 添加页面访问统计
- 实现自定义搜索功能

## PyData 主题配置

demo 使用 PyData Sphinx Theme，提供丰富的主题选项：

### 图标链接

```python
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/jupyterlite/sphinx-demo",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/jupyterlite-sphinx",
            "icon": "fa-custom fa-pypi",  # 自定义图标
        },
    ],
}
```

内置图标使用 Font Awesome 类名（`fa-brands fa-github`）。自定义图标需要在 `_static/` 中提供 SVG 文件（如 `jupyter.svg`），并通过 CSS 注册。

### 版本切换器

demo 的双内核切换通过 PyData 主题的版本切换器实现：

```python
html_theme_options = {
    "switcher": {
        "json_url": "_static/switcher.json",  # 部署时使用根路径
        "version_match": "pyodide",  # 或 "xeus"
    },
    "navbar_end": ["theme-switcher", "version-switcher", "navbar-icon-links"],
}
```

`switcher.json` 定义在项目根目录：

```json
[
    {
        "name": "Pyodide kernel",
        "version": "pyodide",
        "url": "pyodide/"
    },
    {
        "name": "Xeus kernel",
        "version": "xeus",
        "url": "xeus/"
    }
]
```

切换器的工作原理是页面跳转——点击不同版本跳转到不同 URL 路径，而非单页应用内切换。

### 侧边栏配置

```python
html_theme_options = {
    "secondary_sidebar_items": {
        "**": ["page-toc", "sourcelink", "edit-this-page"],
        "index": ["page-toc"],  # 首页只显示目录
    },
}
```

`"**"` 匹配所有页面，`"index"` 单独配置首页。

### 编辑按钮

```python
html_theme_options = {
    "use_edit_page_button": True,
}
```

配合 `html_context` 中的 GitHub 配置，生成"在 GitHub 上编辑此页"链接。

## 自定义图标

demo 包含一个自定义图标 `jupyter.svg`，通过 CSS 定义 Font Awesome 自定义类：

在 PyData 主题中，自定义 SVG 图标需要放置在 `_static/` 目录，并在 CSS 中通过 `--fa-custom-icon-*` 变量注册。更简单的方式是直接使用内联 SVG 或图片链接。

## 相关内容

- [03-sphinx-conf](03-sphinx-conf.md)
- [06-try-examples](06-try-examples.md)
- [09-ci-deployment](09-ci-deployment.md)
