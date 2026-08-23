---
type: Concept
title: 设计系统与 CSS 类名体系
description: sphinx-design 的 sd- 前缀 CSS 类命名体系、语义色、间距、响应式断点
tags:
- sphinx
- design
- css
- design-system
- styling
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- sphinx_design/shared.py
- sphinx_design/extension.py
- sphinx_design/static/sphinx-design.min.css
---

# 设计系统与 CSS 类名体系

sphinx-design 实现了一套自包含的 Bootstrap 子集 CSS 框架，所有类名使用 `sd-` 前缀以避免与主题或其他扩展冲突。理解这套命名体系是自定义样式和高级用法的基础。

## 命名空间隔离

- 所有 sphinx-design 的 CSS 类以 `sd-` 开头
- 组件容器额外添加 `sd-sphinx-override` 类，用于重置主题 CSS 的干扰
- 扩展通过覆盖 `nodes.container` 的 HTML visitor，阻止 Sphinx 默认添加 `container` 类（该类在 Bootstrap 中代表固定宽度容器，与 sphinx-design 的流式布局冲突）
- 当 `is_div=True` 时，container 输出 `<div class="docutils">`（无 `container` 类）

## 语义色彩系统

sphinx-design 定义了 11 种语义色，在多个组件中统一使用：

| 色彩名 | 用途 | CSS 类模式 |
|---|---|---|
| `primary` | 主要操作/强调 | `sd-bg-primary`, `sd-text-primary`, `sd-outline-primary` |
| `secondary` | 次要信息 | `sd-bg-secondary`, `sd-text-secondary` |
| `success` | 成功/正向 | `sd-bg-success`, `sd-text-success` |
| `info` | 信息提示 | `sd-bg-info`, `sd-text-info` |
| `warning` | 警告 | `sd-bg-warning`, `sd-text-warning` |
| `danger` | 危险/错误 | `sd-bg-danger`, `sd-text-danger` |
| `light` | 浅色背景 | `sd-bg-light`, `sd-text-light` |
| `muted` | 弱化文本 | `sd-bg-muted`, `sd-text-muted` |
| `dark` | 深色 | `sd-bg-dark`, `sd-text-dark` |
| `white` | 白色 | `sd-bg-white`, `sd-text-white` |
| `black` | 黑色 | `sd-bg-black`, `sd-text-black` |

色彩在不同组件中的表现形式：

- **徽章/按钮填充**：`sd-bg-{color} sd-bg-text-{color}`（背景色+对比色文本）
- **徽章/按钮轮廓**：`sd-outline-{color} sd-text-{color}`（透明背景+彩色边框+文本）
- **dropdown 标题**：`sd-bg-{color} sd-bg-text-{color}`

## 间距系统

间距（margin/padding）使用 0-5 的刻度，对应 Bootstrap 的间距尺度：

### Margin（外边距）

```
sd-m-{n}           — 四个方向（0-5, auto）
sd-mt-{n}          — 上
sd-mb-{n}          — 下
sd-ml-{n}          — 左
sd-mr-{n}          — 右
```

默认卡片外边距为 `sd-mb-3`（底部间距）。

### Padding（内边距）

```
sd-p-{n}           — 四个方向（0-5）
sd-pt-{n}          — 上
sd-pb-{n}          — 下
sd-pl-{n}          — 左
sd-pr-{n}          — 右
```

指令中的 `margin` 和 `padding` 选项接受：
- 单个值：所有方向相同，如 `:margin: 2` → `sd-m-2`
- 四个值：上 右 下 左（顺时针），如 `:padding: 1 2 3 4` → `sd-pt-1 sd-pr-2 sd-pb-3 sd-pl-4`

## 文本工具类

| 类名 | 作用 |
|---|---|
| `sd-text-left` | 文本左对齐 |
| `sd-text-right` | 文本右对齐 |
| `sd-text-center` | 文本居中 |
| `sd-text-justify` | 文本两端对齐 |
| `sd-text-wrap` | 文本允许换行（按钮默认） |
| `sd-font-weight-bold` | 粗体（卡片标题使用） |
| `sd-hide-link-text` | 视觉隐藏链接文本（用于 stretched-link） |

## 阴影系统

| 选项值 | CSS 类 | 效果 |
|---|---|---|
| `none` | 无 | 无阴影 |
| `sm`（默认） | `sd-shadow-sm` | 小阴影 |
| `md` | `sd-shadow-md` | 中阴影 |
| `lg` | `sd-shadow-lg` | 大阴影 |

按钮的 `shadow` flag 选项添加 `sd-shadow-sm`。

## Flex 布局类

| 类名 | 作用 |
|---|---|
| `sd-d-flex-row` | flex 水平排列 |
| `sd-d-flex-column` | flex 垂直排列（grid-item 默认） |
| `sd-align-major-start` | 主轴起点对齐 |
| `sd-align-major-end` | 主轴终点对齐 |
| `sd-align-major-center` | 主轴居中 |
| `sd-align-major-justify` | 主轴两端对齐 |
| `sd-align-major-spaced` | 主轴均匀分布 |
| `sd-align-minor-center` | 交叉轴居中（article-info 使用） |
| `sd-flex-row-reverse` | 水平反向排列（grid reverse 选项） |

## 响应式断点系统

sphinx-design 使用 4 个响应式断点，对应 Bootstrap 的断点体系：

| 断点前缀 | 对应尺寸 | 说明 |
|---|---|---|
| xs | < 576px | 超小屏幕（手机竖屏） |
| sm | ≥ 576px | 小屏幕（手机横屏） |
| md | ≥ 768px | 中等屏幕（平板） |
| lg | ≥ 992px | 大屏幕（桌面） |

响应式类模式：`sd-{property}-{breakpoint}-{value}`

例如：
- `sd-row-cols-2 sd-row-cols-sm-3 sd-row-cols-md-4` — xs 每行2列、sm每行3列、md+每行4列
- `sd-col-6 sd-col-sm-4 sd-col-md-3` — xs占6列(50%)、sm占4列(33%)、md+占3列(25%)
- `sd-g-2 sd-g-md-3` — xs/sm间距2、md/lg间距3

单值会自动复制到所有断点，如 `:gutter: 2` → `sd-g-2`（所有断点间距为2）。

## 网格类

### 容器
- `sd-container-fluid` — 100% 宽度流式容器（grid 默认）

### 行
- `sd-row` — flex 行容器
- `sd-row-cols-{n}` — 每行 n 列（1-12 或 auto）
- `sd-row-cols-{bp}-{n}` — 指定断点每行 n 列
- `sd-g-{n}` — 间距（gutter），0-5
- `sd-g{xy}-{n}` — 水平/垂直间距（gx/gy）

### 列
- `sd-col` — 弹性列
- `sd-col-{n}` — 占 n 列（1-12 或 auto）
- `sd-col-{bp}-{n}` — 指定断点占 n 列
- `sd-col-auto` — 宽度自适应内容

## 组件特定类

### 卡片（card）
- `sd-card` — 卡片容器
- `sd-card-header` / `sd-card-body` / `sd-card-footer` — 头部/正文/底部
- `sd-card-title` — 标题
- `sd-card-text` — 直接子段落文本
- `sd-card-img` / `sd-card-img-top` / `sd-card-img-bottom` — 背景图/顶部图/底部图
- `sd-card-img-overlay` — 图片覆盖层
- `sd-card-hover` — hover 效果（有 link 时自动添加）
- `sd-cards-carousel` — 横向滚动卡片容器
- `sd-card-cols-{n}` — 轮播每行卡片数
- `sd-w-25` / `sd-w-50` / `sd-w-75` / `sd-w-100` / `sd-w-auto` — 宽度

### 按钮（btn）
- `sd-btn` — 按钮基础类
- `sd-btn-{color}` — 填充色按钮
- `sd-btn-outline-{color}` — 轮廓色按钮
- `sd-stretched-link` — 扩展点击区域到父元素（click-parent 选项）
- `sd-d-grid` — 全宽按钮包装器（expand 选项）

### 徽章（badge）
- `sd-badge` — 徽章基础类
- `sd-bg-{color} sd-bg-text-{color}` — 填充徽章
- `sd-outline-{color} sd-text-{color}` — 轮廓徽章

### 折叠（dropdown）
- `sd-dropdown` — details 元素
- `sd-summary-title` — summary 标题区
- `sd-summary-text` — 标题文本
- `sd-summary-icon` — 标题图标
- `sd-summary-state-marker` — chevron 图标
- `sd-summary-content` — 折叠内容区
- `sd-fade-in` / `sd-fade-in-slide-down` — 展开动画

### 标签页（tab）
- `sd-tab-set` — tab 容器
- `sd-tab-item` — tab 面板
- `sd-tab-label` — tab 标签（label 元素）
- `sd-tab-content` — tab 内容面板

### 图标
- `sd-octicon sd-octicon-{name}` — Octicon 图标
- `sd-material-icon sd-material-icon-{name}` — Material 图标

### 其他
- `sd-border-1` — 1px 边框（outline 选项）
- `sd-d-none` — display:none（sd_hide_title 使用）
- `sd-avatar-sm` — 小尺寸头像
- `sd-p-0 sd-m-0` — 零间距重置（article-info 文本段落使用）
- `sd-pr-2` — 右 padding 2（图标与文本间距）

## 自定义样式最佳实践

添加自定义 CSS 文件覆盖默认样式：

```python
# conf.py
html_static_path = ["_static"]
html_css_files = ["custom.css"]
```

```css
/* _static/custom.css */

/* 自定义卡片圆角 */
.sd-card {
    border-radius: 1rem;
}

/* 自定义主色调按钮 */
.sd-btn-primary {
    background-color: #your-color;
    border-color: #your-color;
}

/* 自定义卡片标题 */
.sd-card-title {
    font-size: 1.25rem;
}
```

> **注意**：避免修改 `sd-sphinx-override` 类内的重置属性，这可能导致跨主题兼容性问题。

## 相关概念

- [网格布局系统](/concepts/04-grids.md) — 网格指令与响应式布局详解
- [卡片组件](/concepts/05-cards.md) — 卡片指令详解
- [快速上手](/concepts/01-getting-started.md) — 安装与基本配置
