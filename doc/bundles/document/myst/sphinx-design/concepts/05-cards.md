---
type: Concept
title: 卡片组件
description: card/card-carousel 指令的用法、内容分隔语法、图片/链接/阴影选项
tags:
- sphinx
- design
- card
- component
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- sphinx_design/cards.py
---

# 卡片组件

卡片（card）是 sphinx-design 中最常用的内容展示组件，支持标题、头部/正文/底部三段结构、图片、链接跳转、阴影等丰富选项。

## 基本用法

```rst
.. card:: 卡片标题

   卡片正文内容。
```

卡片标题是可选的位置参数，省略则创建无标题卡片：

```rst
.. card::

   只有正文的卡片。
```

## 三段式内容结构

卡片内容通过分隔线分为三段：header（头部）、body（正文）、footer（底部）。

```rst
.. card:: 卡片标题

   头部内容（可选）
   ^^^
   正文内容（必须有）
   +++
   底部内容（可选）
```

- `^^^`（3个或以上脱字符 `^`）：分隔 header 和 body
- `+++`（3个或以上加号 `+`）：分隔 body 和 footer

分隔线必须独占一行。header 和 footer 都是可选的。

### 带头部和底部的卡片

```rst
.. card:: 技术规格

   版本信息
   ^^^
   这是产品的详细描述文字，可以包含多行内容。
   +++
   :bdg-success:`可用`
```

## 选项详解

| 选项 | 值 | 默认 | 说明 |
|---|---|---|---|
| `width` | auto/25%/50%/75%/100% | auto | 卡片宽度 |
| `margin` | 1或4个值 0-5/auto | sd-mb-3 | 外边距 |
| `text-align` | left/right/center/justify | 无 | 文本对齐 |
| `img-top` | URI | 无 | 顶部图片 |
| `img-bottom` | URI | 无 | 底部图片 |
| `img-background` | URI | 无 | 背景图片（内容在覆盖层上） |
| `img-alt` | 文本 | "" | 图片 alt 属性 |
| `link` | URL/引用目标 | 无 | 整卡链接（stretched link） |
| `link-type` | url/any/ref/doc | url | 链接类型 |
| `link-alt` | 文本 | link原始值 | 链接可访问性文本 |
| `shadow` | none/sm/md/lg | sm | 阴影大小 |
| `class-card` | CSS类 | 无 | 卡片容器额外类 |
| `class-header` | CSS类 | 无 | header 额外类 |
| `class-body` | CSS类 | 无 | body 额外类 |
| `class-title` | CSS类 | 无 | 标题额外类 |
| `class-footer` | CSS类 | 无 | footer 额外类 |
| `class-img-top` | CSS类 | 无 | 顶部图片额外类 |
| `class-img-bottom` | CSS类 | 无 | 底部图片额外类 |

## 图片选项

### 顶部图片

```rst
.. card:: 带图片的卡片
   :img-top: _static/top-image.jpg
   :img-alt: 描述图片

   图片下方的正文。
```

顶部图片使用 `sd-card-img-top` CSS 类，位于标题/header/body 之上。

### 底部图片

```rst
.. card:: 底部图片卡片
   :img-bottom: _static/bottom-image.jpg

   正文在图片上方。
```

底部图片使用 `sd-card-img-bottom` CSS 类，位于 footer 之下。

### 背景图片

```rst
.. card:: 背景图片卡片
   :img-background: _static/bg.jpg

   内容显示在半透明覆盖层上。
```

背景图片创建 `sd-card-img` 类的 image 节点和 `sd-card-img-overlay` 覆盖层，所有内容（标题/header/body/footer）都在覆盖层内。

## 卡片链接

设置 `link` 选项后，整个卡片变为可点击的链接：

```rst
.. card:: 点击跳转
   :link: https://example.com
   :shadow: lg

   整卡可点击，hover 时有视觉效果。
```

### 内部引用链接

```rst
.. card:: 跳转到文档内章节
   :link: 安装指南
   :link-type: ref
   :link-alt: 前往安装指南章节

   点击跳转到"安装指南"章节。
```

`link-type` 选项：
- `url`（默认）：外部 URL，空白字符被移除
- `ref`：Sphinx `:ref:` 引用，目标小写化匹配标签
- `doc`：Sphinx `:doc:` 文档引用
- `any`：Sphinx `:any:` 任意引用

链接实现使用 `sd-stretched-link` 类（将链接扩展到整个卡片区域）和 `sd-hide-link-text` 类（视觉隐藏链接文本），同时卡片添加 `sd-card-hover` 类提供 hover 效果。

## 轮播卡片（card-carousel）

`card-carousel` 指令创建横向滚动的卡片行：

```rst
.. card-carousel:: 3

   .. card:: 卡片 1
      内容一

   .. card:: 卡片 2
      内容二

   .. card:: 卡片 3
      内容三

   .. card:: 卡片 4
      内容四
```

- 必填参数：列数（1-12），控制可视区域同时显示的卡片数量
- 选项：`class` 额外 CSS 类
- 子元素应为 `card` 指令，否则发出警告

轮播容器使用 `sd-cards-carousel` 和 `sd-card-cols-{n}` 类。

## 子元素类处理

卡片自动为直接子段落（`nodes.paragraph`）添加 `sd-card-text` 类，确保段落间距和字体样式正确。注意仅处理**直接子元素**，不处理嵌套在 admonition、列表、其他卡片内的段落（避免样式污染嵌套组件）。

## 相关概念

- [网格布局系统](04-grids.md) — grid-item-card 组合用法
- [设计系统与CSS类名体系](03-design-system.md) — 宽度/阴影/间距类名
- [徽章与按钮](07-badges-buttons.md) — 在卡片 footer 中使用徽章
