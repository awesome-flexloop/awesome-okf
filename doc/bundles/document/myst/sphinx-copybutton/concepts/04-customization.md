---
type: Concept
title: 自定义样式与图标
description: 如何自定义 sphinx-copybutton 的外观——CSS 样式覆盖、自定义 SVG 图标、选择器定制、本地化支持
tags: [sphinx, sphinx-extension, copybutton, customization, css, svg, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: copybutton-source
    resource: /references/copybutton-source.md
    title: sphinx-copybutton 源码路径映射
---

# 自定义样式与图标

sphinx-copybutton 提供了多种定制方式：CSS 样式覆盖、自定义 SVG 图标、调整目标选择器、添加自定义 CSS 类等。本文档详细介绍各定制选项。

## CSS 样式定制

### 默认样式结构

复制按钮的 CSS 定义在 `copybutton.css` 中，核心选择器：

```css
button.copybtn {
    position: absolute;
    top: .3em;
    right: .3em;
    width: 1.7em;
    height: 1.7em;
    opacity: 0;           /* 默认隐藏 */
    border: #1b1f2426 1px solid;
    background-color: #f6f8fa;
    color: #57606a;
    border-radius: 0.4em;
    /* ... */
}

div.highlight {
    position: relative;   /* 按钮定位参照 */
}

/* 悬停显示 */
.highlight:hover button.copybtn, button.copybtn.success {
    opacity: 1;
}

/* 成功状态 */
button.copybtn.success {
    border-color: #22863a;
    color: #22863a;
}
```

### 覆盖默认样式

在 Sphinx 的 `_static` 目录下创建自定义 CSS 文件（如 `custom.css`），然后在 `conf.py` 中添加：

```python
def setup(app):
    app.add_css_file("custom.css")
```

或者如果已有 `html_css_files` 配置：

```python
html_css_files = ["custom.css"]
```

### 常见样式定制示例

**让按钮始终可见（不只是悬停时）：**

```css
button.copybtn {
    opacity: 1;
}
```

**调整按钮位置：**

```css
button.copybtn {
    top: 0.5em;
    right: 0.5em;
}
```

**修改按钮颜色：**

```css
button.copybtn {
    background-color: #your-color;
    color: #your-text-color;
    border-color: #your-border-color;
}

button.copybtn.success {
    border-color: #your-success-color;
    color: #your-success-color;
}
```

**调整按钮大小：**

```css
button.copybtn {
    width: 2em;
    height: 2em;
}
button.copybtn svg {
    width: 1.8em;
    height: 1.8em;
}
```

**修改 tooltip 样式：**

```css
.o-tooltip--left:after {
    background: #333;
    font-size: 0.75em;
    padding: 0.3em 0.5em;
    border-radius: 4px;
}
```

## 自定义 SVG 图标

sphinx-copybutton 支持两种方式自定义复制按钮图标。

### 方式一：copybutton_image_svg（推荐）

通过 `copybutton_image_svg` 配置项直接传入 SVG 字符串：

```python
# conf.py
copybutton_image_svg = """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
</svg>
"""
```

或者从文件读取：

```python
from pathlib import Path
copybutton_image_svg = Path("_static/my-copy-icon.svg").read_text()
```

### 方式二：copybutton_image_path（已废弃）

旧版本使用 `copybutton_image_path` 指定 SVG 文件路径，此配置已废弃，会发出 warning。建议迁移到 `copybutton_image_svg`。

### 默认图标说明

- **复制图标**：Tabler Icons 的 copy 图标（双矩形），黑色描边
- **成功图标**：Tabler Icons 的 check 图标（对勾），绿色 `#22863a`
- 成功图标不可通过配置修改，需要通过 CSS 或 JS 自定义

## 选择器定制

### copybutton_selector

默认选择器是 `"div.highlight pre"`，匹配 Sphinx 标准代码块结构。如果你的主题使用不同的 HTML 结构，可以修改此选择器：

```python
# 示例：适配某些主题使用的不同类名
copybutton_selector = "div.highlight > pre, div.my-custom-code pre"
```

### copybutton_exclude

默认值 `".linenos"` 排除 Pygments 生成的行号单元格。如果需要排除其他元素，可以扩展选择器：

```python
# 排除行号和某些自定义装饰元素
copybutton_exclude = ".linenos, .code-decoration, .line-anchor"
```

## 本地化支持

sphinx-copybutton 内置 7 种语言的界面文本：

| 语言代码 | 语言 | 复制 | 复制成功 | 复制失败 |
|---------|------|------|---------|---------|
| `en` | English | Copy | Copied! | Failed to copy |
| `zh-CN` | 简体中文 | 复制 | 复制成功! | 复制失败 |
| `es` | Español | Copiar | ¡Copiado! | Error al copiar |
| `de` | Deutsch | Kopieren | Kopiert! | Fehler beim Kopieren |
| `fr` | Français | Copier | Copié ! | Échec de la copie |
| `ru` | Русский | Скопировать | Скопировано! | Не удалось скопировать |
| `it` | Italiano | Copiare | Copiato! | Errore durante la copia |

语言通过 `html_document_lang` 或页面 `<html lang="...">` 属性自动检测。在 `conf.py` 中设置：

```python
language = 'zh_CN'  # Sphinx 会设置 <html lang="zh-CN">
```

注意：中文使用 `zh-CN`（带连字符），这是 Sphinx 的约定。JS 中检测的也是 `document.documentElement.lang`，即 `zh-CN`。

## 打印样式

默认情况下，打印页面时复制按钮会隐藏（`@media print { display: none }`）。如果你需要在打印时显示按钮（不推荐），可以覆盖：

```css
@media print {
    button.copybtn {
        display: flex !important;
    }
}
```

## 完整定制示例 conf.py

```python
# conf.py
project = 'My Project'
copyright = '2024, Your Name'
author = 'Your Name'
release = '1.0.0'

extensions = [
    'sphinx_copybutton',
]

# 复制按钮配置
copybutton_prompt_text = "$ "
copybutton_remove_prompts = True
copybutton_only_copy_prompt_lines = True

# 自定义图标
from pathlib import Path
# copybutton_image_svg = Path("_static/copy-icon.svg").read_text()

# 自定义选择器
# copybutton_selector = "div.highlight pre"
# copybutton_exclude = ".linenos"

# 静态文件
html_static_path = ['_static']
html_css_files = ['custom.css']
```

## 相关概念

- [扩展架构与注册机制](02-extension-architecture.md)
- [文本处理与提示符剥离](03-text-processing.md)
- [基础配置示例](../examples/basic-setup.md)
