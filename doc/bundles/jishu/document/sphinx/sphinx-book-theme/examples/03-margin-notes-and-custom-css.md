---
type: Example
title: "边注、margin 与自定义 CSS"
description: "一页完整的 MyST 源文件：编号边注、无编号 margin note、块级 margin、图注出边、全宽提示框，以及配套的品牌 CSS"
tags: [sphinx, theme, example, sidenote, margin, css, myst]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-content-blocks
    resource: https://sphinx-book-theme.readthedocs.io/en/latest/content/content-blocks.html
    title: Special content blocks
  - id: sbt-transform
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme/src/sphinx_book_theme/_transforms.py
    title: HandleFootnoteTransform
---

# 边注、margin 与自定义 CSS

目标：在同一页里演示五种"出边"表达，并给出可维护的品牌样式。

## 1. 启用边注

```python
html_theme_options = {
    "use_sidenotes": True,
}
```

开启后，页面里的**所有脚注**都会变成边注或 margin note。

## 2. 完整页面源文件

把下面内容保存为 `docs/part-1/layout.md`，并加入 `toctree`。

````md
# 排版实验

## 编号边注

这是一句正文，带一个编号边注[^note1]。桌面端它会出现在右侧留白，
窄屏时点击编号展开。

[^note1]: 这是边注内容。它应该是**行内**内容，不能放代码块或列表。

## 无编号 margin note

这是一句正文，带一个无编号旁注[^note2]。

[^note2]: {-} 这是 margin note。开头的 `{-}` 会被移除，编号也不显示。

## 块级 margin

下面的 margin 块可以放代码、图片、提示框：

```{margin} **实现提示**
margin 块本质是 docutils 的 `Sidebar`，加了一个 `margin` class。
```

正文继续。注意 margin 块不要嵌套在提示框里。

## 图注出边

```{figure} ../images/architecture.png
---
width: 70%
figclass: margin-caption
alt: 架构图
name: fig-architecture
---
图注会出现在右侧留白，图片仍在正文。
```

引用这张图：{ref}`fig-architecture`。

## 整张图出边

```{figure} ../images/logo.png
---
width: 50%
figclass: margin
alt: logo
---
整张图进入右侧留白。
```

## 全宽提示框

```{note}
:class: full-width
这条提示会向右扩展，占据右侧留白，适合放重要结论。
```

## 全宽公式

```{math}
:class: full-width
:label: eq-example

\int_0^\infty \frac{x^3}{e^x - 1}\,dx = \frac{\pi^4}{15}
```

引用公式：{eq}`eq-example`。
````

## 3. 品牌 CSS

`docs/_static/custom.css`：

```css
/* 主色与链接色 */
:root {
    --pst-color-primary: #0b5fff;
    --pst-color-link: #0b5fff;
    --pst-color-link-hover: #0846bd;
}

/* 标题字重与字距 */
h1, h2, h3 {
    font-weight: 650;
    letter-spacing: 0.01em;
}

/* 边注文字稍小、颜色稍淡 */
.sidenote,
.marginnote {
    font-size: 0.85rem;
    line-height: 1.55;
    color: #4a5568;
}

/* margin 块加左侧强调线 */
.margin {
    border-left: 3px solid var(--pst-color-primary);
    padding-left: 0.75rem;
}

/* 全宽内容加浅背景 */
.full-width {
    background: #f7f9fc;
    padding: 1rem 1.25rem;
    border-radius: 6px;
}

/* 下载按钮用稳定 label class */
.btn-download-buttons {
    border: 1px solid var(--pst-color-primary);
}

/* 打印时边注回到正文，去掉强调线避免干扰 */
@media print {
    .margin {
        border-left: none;
        padding-left: 0;
    }
}
```

## 4. 配置

```python
html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

html_theme_options = {
    "use_sidenotes": True,
    "show_toc_level": 2,
}
```

## 5. 效果检查

| 元素 | 桌面端 | 窄屏 |
|------|--------|------|
| 编号边注 | 右侧留白，带编号 | 点击编号展开 |
| margin note | 右侧留白，无编号 | 点击符号展开 |
| `{margin}` 块 | 右侧留白，可带标题 | 回到正文流 |
| `margin-caption` | 图在正文，图注在右 | 图注回到图下 |
| `margin` 图 | 整图在右 | 图回到正文 |
| `full-width` | 向右扩展 | 回到普通宽度 |

## 6. 排错

### 边注没有出现

- `use_sidenotes` 是否为 `True`（不是字符串 `"True"` 也可能被 `as_bool` 正确识别，但 YAML/JSON 配置里建议用布尔值）。
- 脚注是否真的被引用；未被引用的脚注不会转换。
- 是否在非 HTML builder 下构建；变换只对 `html` 格式生效。

### 边注内容和正文重复

检查是否同时保留了页尾脚注定义。变换会删除原脚注节点；如果你自定义了模板或扩展重复渲染，可能出现两份。

### margin 块与提示框重叠

把 `{margin}` 从提示框里移出来，放到提示框前后。docutils 的 Sidebar 在嵌套容器中定位不稳定。

### 全宽内容在移动端溢出

给全宽元素加 `max-width: 100%`，并检查内部是否有固定宽度图片或表格。

## 7. 设计检查清单

- 每个边注都能独立读懂，不依赖正文的上一句。
- 一屏内不超过 2 个边注。
- margin 块没有承载主线论证。
- 全宽元素在 1280px、768px、375px 三个宽度下都不溢出。
- 打印预览中边注顺序正确。

## 相关概念

- [边注、margin 与全宽内容](../concepts/06-sidenotes-margin.md)
- [定制、子主题与主题开发](../concepts/08-customization-and-development.md)
- [从零搭建书籍站点](01-basic-book-site.md)
