---
type: concept
title: "命名网格线响应式布局系统"
description: "基于 CSS Grid 命名网格线的学术文档布局系统，支持边注、全宽图片和多断点响应"
tags: [myst-theme, css-grid, layout, responsive]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "styles/index.js"
    facts: [F-019, F-020]
  - path: "spec/facts.md"
    facts: [F-044]
---

# 命名网格线响应式布局系统

## 设计动机

传统 12 列网格系统难以满足学术出版的排版需求。学术文档经常需要：边注（margin note）、全宽图片、正文区域精确控制、侧边交叉引用栏。myst-theme 选择基于 **CSS Grid 命名网格线（named grid lines）** 构建布局系统，而非传统的列数方案。

## 网格轨道定义

在 `styles/index.js` 的 `themeExtensions.gridTemplateColumns` 中，定义了多套响应式网格模板：

### 基础轨道命名

```
┌─────────┬──────────┬─────────┬──────────┬──────────┬─────────┬──────────┬─────────┐
│ gutter  │  screen  │ gutter  │   page   │   body   │ gutter  │  screen  │ gutter  │
│ -left   │ -inset-  │ -left   │ -inset-  │          │ -right  │ -inset-  │ -right  │
│         │  left    │         │  left    │          │         │  right   │         │
└─────────┴──────────┴─────────┴──────────┴──────────┴─────────┴──────────┴─────────┘
```

命名网格线包括：
- `screen-start` / `screen-end`：全屏宽度边界
- `page-start` / `page-end`：页面内容区（有最大宽度限制）
- `body-start` / `body-end`：正文区域
- `gutter-left-start/end`、`gutter-right-start/end`：边注区域
- `middle`：中线

### 响应式断点模板

| 模板名 | 断点 | 布局特征 |
|--------|------|---------|
| `article-sm` | 小屏 | 单列，body 占满 |
| `article-md` | 中屏 | body + 右侧 gutter |
| `article-lg` | 大屏 | body + 双侧 gutter（边注可见） |
| `article-xl` | 超大屏 | 更宽的 gutter，page-inset 可见 |
| `article-2xl` | 最大屏 | 完整三栏：gutter-left + body + gutter-right |
| `article-left-*` | 各断点 | TOC 在左侧的布局变体 |
| `article-center-*` | 各断点 | 居中内容布局变体 |

## 快捷定位类

`gridColumn` 配置提供了语义化的快捷类，映射到命名网格线：

| 类名 | 跨越范围 | 用途 |
|------|---------|------|
| `col-body` | body-start → body-end | 正文内容（默认） |
| `col-page` | page-start → page-end | 页面宽度元素 |
| `col-screen` | screen-start → screen-end | 全宽元素（突破容器） |
| `col-body-outset` | gutter-left → gutter-right | 正文突出（比 body 宽，比 page 窄） |
| `col-body-inset` | body 内部缩窄 | 引述块、窄内容 |
| `col-gutter-left` | 左侧 gutter | 左边注 |
| `col-gutter-right` | 右侧 gutter | 右边注、交叉引用 |
| `col-middle` | 到中线 | 半宽元素 |

## 使用示例

```tsx
// 正文内容（默认 col-body）
<article className="col-body">
  <p>主要内容...</p>
</article>

// 全宽图片
<figure className="col-screen">
  <img src="wide-diagram.png" alt="全宽图表" />
</figure>

// 右边注
<aside className="col-gutter-right">
  <p>这是一个边注（margin note）</p>
</aside>

// 正文突出（如代码块）
<pre className="col-body-outset">
  <code>...</code>
</pre>
```

## 与内容组件的集成

myst-to-react 的组件根据语义自动选择网格位置：
- `paragraph`、`heading`：默认 `col-body`
- `figure` with `outset`：使用 `col-body-outset` 或 `col-page`
- `iframe`、`mermaid` 全宽图表：使用 `col-screen`
- `crossReference` 侧边栏：使用 `col-gutter-right`
- `proof`、`exercise`：使用 `col-body`

## GridProvider

`GridProvider` React Context 允许组件在运行时感知当前网格布局状态（当前断点、是否有 gutter 等），从而动态决定渲染方式。例如，在小屏上 gutter 不可见时，边注内容会内联显示在正文流中。

## 关键设计决策

1. **命名线而非编号列**：`col-body` 比 `col-span-8` 更具语义，且响应式变化时不需要修改组件
2. **纯 CSS 实现**：网格逻辑完全在 CSS 中，不依赖 JS 测量
3. **渐进增强**：小屏单列，大屏自动获得多栏能力
4. **与 Tailwind 集成**：通过 `themeExtensions` 注册，组件使用标准 Tailwind 类名
