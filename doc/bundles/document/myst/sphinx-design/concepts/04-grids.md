---
type: Concept
title: 网格布局系统
description: grid/grid-item/grid-item-card 指令的用法、响应式参数、间距与对齐
tags:
- sphinx
- design
- grid
- layout
- responsive
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- sphinx_design/grids.py
---

# 网格布局系统

网格系统是 sphinx-design 布局的基础，基于 Bootstrap 的 12 列 flexbox 网格实现，支持 4 个响应式断点。

## 基本概念

sphinx-design 的网格由三个核心指令构成：

- **`grid`**：网格容器，创建行（row），接受列数参数控制每行子项数量
- **`grid-item`**：网格列，放置在 grid 内部，可控制占位列数、方向、对齐等
- **`grid-item-card`**：带卡片的网格列，是 grid-item + card 的组合，是最常用的布局组件

### 12 列体系

网格基于 12 列布局：一个 grid-item 可以占 1-12 列。例如每行 2 列时每个 item 默认占 6 列（12÷2=50%）。

## grid 指令

### 语法

```rst
.. grid:: [列数]
   :gutter: 间距
   :margin: 外边距
   :padding: 内边距
   :outline: (flag) 显示边框
   :reverse: (flag) 反向排列
   :class-container: 容器额外CSS类
   :class-row: 行额外CSS类

   .. grid-item::
      内容
```

### 参数

**列数**（可选位置参数）：
- 单个值（1-12 或 auto）：所有断点使用相同列数
- 四个值（用空格分隔）：按 xs sm md lg 顺序设置，如 `1 2 3 4` 表示 xs 每行1列、sm 每行2列、md 每行3列、lg 每行4列
- 省略时不自动设置行宽，由 grid-item 的 columns 选项手动控制

### 选项详解

| 选项 | 值格式 | 默认值 | 说明 |
|---|---|---|---|
| `gutter` | 1-4个值 0-5 | 无 | 列间距（水平+垂直） |
| `margin` | 1或4个值 0-5/auto | sd-mb-4 | 外边距 |
| `padding` | 1或4个值 0-5 | 无 | 内边距 |
| `outline` | flag | 无 | 添加 1px 边框 |
| `reverse` | flag | 无 | flex-direction: row-reverse |
| `class-container` | CSS类列表 | 无 | 容器额外类 |
| `class-row` | CSS类列表 | 无 | 行额外类 |

## grid-item 指令

### 语法

```rst
.. grid-item::
   :columns: 占位列数
   :margin: 外边距
   :padding: 内边距
   :child-direction: column|row
   :child-align: start|end|center|justify|spaced
   :outline: (flag) 显示边框
   :class: 额外CSS类

   内容
```

### 选项详解

| 选项 | 值格式 | 默认值 | 说明 |
|---|---|---|---|
| `columns` | 1-4个值 1-12/auto | 自适应 | 占位列数 |
| `margin` | 1或4个值 0-5/auto | 无 | 外边距 |
| `padding` | 1或4个值 0-5 | 无 | 内边距 |
| `child-direction` | column/row | column | 子元素排列方向 |
| `child-align` | start/end/center/justify/spaced | 无 | 主轴对齐方式 |
| `outline` | flag | 无 | 边框 |
| `class` | CSS类列表 | 无 | 额外CSS类 |

**columns 参数格式**：
- 单个值：所有断点相同列数
- 四个值（xs sm md lg）：响应式列数，如 `6 6 4 3` 表示 xs/sm 占6列(50%)、md 占4列(33%)、lg 占3列(25%)
- `auto`：宽度自适应内容

## grid-item-card 指令

这是最常用的组件，组合了 grid-item 的布局能力和 card 的内容展示能力。

### 语法

```rst
.. grid-item-card:: [卡片标题]
   :columns: 占位列数
   :width: auto|25%|50%|75%|100%
   :text-align: left|right|center|justify
   :img-top: 顶部图片URL
   :img-bottom: 底部图片URL
   :img-background: 背景图片URL
   :img-alt: 图片alt文本
   :link: 链接目标
   :link-type: url|any|ref|doc
   :link-alt: 链接alt文本
   :shadow: none|sm|md|lg
   :class-item: grid-item额外类
   :class-card: card额外类
   :class-body: body额外类
   :class-title: title额外类
   :class-header: header额外类
   :class-footer: footer额外类
   :class-img-top: 顶部图片额外类
   :class-img-bottom: 底部图片额外类

   卡片正文内容
```

默认 width 为 "100%"（占满 grid-item 宽度），margin 为空（由 grid 的 gutter 控制间距）。

## 使用示例

### 简单两列网格

```rst
.. grid:: 2

   .. grid-item-card:: 功能一

      功能描述文字。

   .. grid-item-card:: 功能二

      功能描述文字。
```

### 响应式三列（手机1列→平板2列→桌面3列）

```rst
.. grid:: 1 2 2 3
   :gutter: 2

   .. grid-item-card:: 项目 A

      A 的说明。

   .. grid-item-card:: 项目 B

      B 的说明。

   .. grid-item-card:: 项目 C

      C 的说明。
```

### 手动控制列宽

```rst
.. grid::
   :gutter: 3

   .. grid-item::
      :columns: 8

      主要内容区域（占8列，约67%宽度）。

   .. grid-item::
      :columns: 4
      :child-align: center

      侧边栏（占4列，约33%宽度），内容居中对齐。
```

### 带边框和间距

```rst
.. grid:: 2
   :outline:
   :padding: 3
   :gutter: 2

   .. grid-item::
      :outline:
      :padding: 2

      带边框和内边距的列。

   .. grid-item::
      :outline:
      :padding: 2

      另一列。
```

### MyST Markdown 语法

````markdown
```{grid} 2
:gutter: 2

```{grid-item-card} 卡片 1
内容一
```

```{grid-item-card} 卡片 2
内容二
```
```
````

## 子元素验证

grid 指令会验证直接子元素是否为 grid-item（通过 `is_component(item, "grid-item")` 检查），如果发现非 grid-item 且非可忽略节点（注释、系统消息），会发出警告：

> "All children of a 'grid-row' should be 'grid-item' [design.grid]"

但不会中断构建，无效子节点仍会被输出。同样，grid-item 如果不在 grid-row 内也会发出警告。

## div 指令

除了网格系统，sphinx-design 还提供了 `div` 指令用于创建不带 `container` 类的通用 `<div>` 容器：

```rst
.. div:: custom-class another-class
   :style: color: red; font-size: 1.2em;
   :name: my-div

   内容
```

这在需要自定义容器样式时非常有用，比原生 `container` 指令更安全（不会引入 Bootstrap 的 `.container` 固定宽度样式）。

## 相关概念

- [设计系统与CSS类名体系](03-design-system.md) — 间距、响应式、flex 类名详解
- [卡片组件](05-cards.md) — 卡片选项和分隔语法详解
- [sphinx-design 简介](00-introduction.md) — 项目概览
