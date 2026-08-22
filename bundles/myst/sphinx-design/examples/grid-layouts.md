---
type: example
title: 网格布局示例集
description: grid/grid-item/grid-item-card 的各种用法示例，从简单两列到响应式复杂布局
tags:
- sphinx
- design
- grid
- example
- layout
generated: 2026-08-23
status: stable
stale_after: 2027-08-23
sources:
- sphinx_design/grids.py
---

# 网格布局示例集

## 示例1：简单两列卡片

最常用的布局模式，每行2个卡片：

```rst
.. grid:: 2
   :gutter: 3

   .. grid-item-card:: 🚀 快速开始

      几分钟内上手，零配置即可使用。

   .. grid-item-card:: 📦 组件丰富

      卡片、标签页、折叠、按钮、徽章一应俱全。
```

## 示例2：响应式卡片网格

手机1列→平板2列→桌面3列→大屏4列：

```rst
.. grid:: 1 2 3 4
   :gutter: 2

   .. grid-item-card:: 功能一
      描述一。

   .. grid-item-card:: 功能二
      描述二。

   .. grid-item-card:: 功能三
      描述三。

   .. grid-item-card:: 功能四
      描述四。
```

## 示例3：主内容+侧边栏

手动控制列宽，左8列右4列：

```rst
.. grid::
   :gutter: 3

   .. grid-item::
      :columns: 8

      **主要内容区域**

      这里是文档的主要内容，占约67%宽度。

      可以包含任意内容：段落、列表、代码块等。

   .. grid-item::
      :columns: 4
      :child-direction: column

      .. card:: 目录
         :shadow: sm

         - 章节一
         - 章节二
         - 章节三
```

## 示例4：带边框和内边距的网格

```rst
.. grid:: 3
   :outline:
   :padding: 3
   :gutter: 2

   .. grid-item::
      :outline:
      :padding: 2
      :text-align: center

      带边框的格子1

   .. grid-item::
      :outline:
      :padding: 2
      :text-align: center

      带边框的格子2

   .. grid-item::
      :outline:
      :padding: 2
      :text-align: center

      带边框的格子3
```

## 示例5：功能卡片导航（首页常用）

结合卡片链接和图标：

```rst
.. grid:: 2 3
   :gutter: 3

   .. grid-item-card::
      :link: getting-started
      :link-type: ref
      :text-align: center
      :shadow: md

      📖 入门指南
      ^^^^^^^^^^^
      安装、配置、第一个页面。

   .. grid-item-card::
      :link: api-reference
      :link-type: ref
      :text-align: center
      :shadow: md

      🔧 API 参考
      ^^^^^^^^^^
      完整的指令和配置参考。

   .. grid-item-card::
      :link: examples
      :link-type: ref
      :text-align: center
      :shadow: md

      💡 示例集
      ^^^^^^^^^
      从简单到复杂的使用示例。
```

## 示例6：反向排列和自定义对齐

```rst
.. grid:: 3
   :reverse:
   :gutter: 2

   .. grid-item::
      :child-align: center

      居中对齐内容（反向排列后显示在最右）

   .. grid-item::
      :child-align: start

      顶部对齐

   .. grid-item::
      :child-align: end

      底部对齐
```

## 示例7：MyST Markdown 响应式网格

````markdown
```{grid} 1 2 2 3
:gutter: 3

```{grid-item-card} 标题一
内容一
```

```{grid-item-card} 标题二
内容二
```

```{grid-item-card} 标题三
内容三
```
```
````

## 示例8：使用 div 指令自定义容器

```rst
.. div:: sd-d-flex-row sd-align-major-spaced sd-p-3 sd-border-1

   左侧文字

   :bdg-primary:`标签`

   右侧文字
```
