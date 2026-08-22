---
type: concept
title: "图片与图表"
description: "image指令和figure指令的用法、选项、子图、Notebook单元格嵌入和iframe嵌入"
tags: [myst-syntax, figure, image, subfigures, iframe, multimedia]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/figure.ts"
    facts: [F-S018]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/image.ts"
    facts: [F-S019]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/iframe.ts"
    facts: [F-S035]
---

# 图片与图表

MyST 提供 `image`（独立图片）和 `figure`（带标题的图表容器）两个图片相关指令。

## Image 指令

`image` 指令用于插入独立图片，不带标题和编号：

```markdown
:::{image} images/photo.png
:width: 300px
:alt: 一张照片
:align: center
:::
```

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | String | ✅ | 图片文件路径（相对路径或URL） |

### 选项

| 选项 | 别名 | 类型 | 说明 |
|------|------|------|------|
| `:width:` | `w` | String | CSS 宽度（50%、300px 等） |
| `:height:` | `h` | String | CSS 高度（4em、300px 等） |
| `:alt:` | - | String | 替代文本（无障碍访问必需） |
| `:align:` | - | String | 对齐方式：left/center/right（默认 center） |
| `:title:` | - | String | 鼠标悬停时显示的标题文本 |
| `:class:` | - | String | CSS 类名 |
| `:label:` | `name` | String | 交叉引用标签 |

如果未提供 `:alt:`，会从指令体文本中自动提取（使用 toText）。

## Figure 指令

`figure` 指令创建带标题和编号的图表容器，这是技术写作中的推荐方式：

````markdown
:::{figure} images/diagram.png
:width: 80%
:alt: 系统架构图
:label: fig-architecture

这是图的**标题**，可以包含 Markdown 格式。
:::
````

Figure 会被自动编号（Figure 1、Figure 2...），可以通过 `{ref}`fig-architecture`` 交叉引用。

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| url/cell-id | String | 图片路径或 Notebook 单元格 ID（`#cell-id` 格式） |

### 选项

| 选项 | 别名 | 类型 | 说明 |
|------|------|------|------|
| `:width:` | `w`/`figwidth` | String | CSS 宽度 |
| `:height:` | `h` | String | CSS 高度 |
| `:alt:` | - | String | 替代文本 |
| `:align:` | - | String | left/center/right |
| `:class:` | `figclass` | String | CSS 类名。`full-width` 在 LaTeX 中跨双栏 |
| `:remove-input:` | - | Boolean | 嵌入 Notebook 单元格时移除输入代码 |
| `:remove-output:` | - | Boolean | 嵌入 Notebook 单元格时移除输出 |
| `:placeholder:` | - | String | Notebook 单元格的静态占位图（PDF 导出时使用） |
| `:no-subfigures:` | `no-subfig`/`no-subfigure` | Boolean | 禁止隐式子图创建 |
| `:kind:` | - | String | 自定义图表类型（影响编号序列） |
| `:label:` | `name` | String | 交叉引用标签 |

### 自定义图类型

`:kind:` 选项可以改变图表的编号序列：

```markdown
:::{figure} diagram.png
:kind: example
:label: ex-setup

设置示例图。
:::
```

这将产生 "Example 1" 而非 "Figure 1"，并有独立的编号计数。

### 引用 Notebook 输出

Figure 可以引用 Jupyter Notebook 单元格的输出：

````markdown
:::{figure} #my-plot-cell
:width: 100%

由 Notebook 生成的图表。
:::
````

参数以 `#` 开头表示单元格 ID。可以配合 `:remove-input:` 只显示输出：

````markdown
:::{figure} #my-plot-cell
:remove-input: true

代码生成的图表。
:::
````

### 子图（Subfigures）

当 figure 指令不带参数（无图片路径），且 body 中包含多个图片时，这些图片自动成为子图：

````markdown
:::{figure}
:label: fig-comparison

对比结果

:::{image} result-a.png
:::

:::{image} result-b.png
:::
:::
````

设置 `:no-subfigures:` 可以禁止这种自动行为。

### Figure 输出结构

```
container(kind:'figure')
  ├── image(url, alt, width, height, align)       [来自参数]
  ├── image(placeholder:true, url)                [可选占位图]
  └── body内容（caption、子图等）
```

有 caption 时，figure 参与自动编号。

## Iframe 指令

`iframe` 指令嵌入外部网页内容：

```markdown
:::{iframe} https://example.com
:width: 100%
:title: 外部示例页面
:::
```

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| src | String | ✅ | iframe 的 URL |

### 选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `:width:` | String | CSS 宽度 |
| `:align:` | String | left/center/right |
| `:title:` | String | iframe 标题（无障碍访问） |
| `:placeholder:` | String | 静态导出时的占位图片 |

### 带标题的 Iframe

如果提供了 body，iframe 被包裹在 figure 容器中，body 作为标题：

````markdown
:::{iframe} https://example.com
:width: 100%

嵌入的外部页面示例。
:::
````

### 静态导出占位

PDF/LaTeX 等静态导出中 iframe 无法渲染，使用 `:placeholder:` 提供替代图片：

```markdown
:::{iframe} https://example.com
:placeholder: images/screenshot.png
:width: 100%

外部页面截图。
:::
```

## 图片路径说明

- 相对路径相对于当前 Markdown 文件
- 支持本地文件路径和 HTTP(S) URL
- 支持的格式：PNG、JPG/JPEG、SVG、GIF、WebP 等
- 大于阈值（默认 1.5MB）的图片在构建时自动转换为 WebP

## 相关概念

- [指令与角色基础](00-directive-role-basics.md)
- [表格](04-tables.md)
- [包含与嵌入](07-include-embed.md) — embed 指令可以嵌入其他已标签的图表
