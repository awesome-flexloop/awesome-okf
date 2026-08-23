---
type: Concept
title: 08 - 样式定制与第三方扩展适配
description: SCSS样式架构、CSS自定义方法、暗色模式、打印样式，以及对myst-nb、sphinx-design等第三方扩展的内置样式适配
tags:
- sphinx-book-theme
- scss
- css
- customization
- dark-mode
- print
- extensions
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- src/sphinx_book_theme/assets/styles/
---

# 样式定制与第三方扩展适配

sphinx-book-theme 使用 SCSS 组织样式，在 pydata-sphinx-theme（PST）的 Bootstrap 5 基础上添加书籍式外观和对第三方扩展的适配。

## SCSS 架构

样式入口为 `assets/styles/index.scss`，通过 webpack 编译为 `styles/sphinx-book-theme.css`（F-181）。目录结构按职责分层：

### abstracts/ — 抽象层

| 文件 | 职责 |
|------|------|
| `_variables.scss` | SCSS变量定义（颜色、间距、字体等） |
| `_mixins.scss` | 可复用的SCSS混入 |

### base/ — 基础层

| 文件 | 职责 |
|------|------|
| `_base.scss` | 全局基础样式重置 |
| `_typography.scss` | 排版样式（字体、行高、标题等） |
| `_print.scss` | 打印样式（`@media print`） |

### components/ — 组件层

| 文件 | 职责 |
|------|------|
| `_back-to-top.scss` | 返回顶部按钮 |
| `_icon-links.scss` | 图标链接（导航栏） |
| `_logo.scss` | Logo样式 |
| `_search.scss` | 搜索框样式 |

### content/ — 内容层

| 文件 | 职责 |
|------|------|
| `_admonitions.scss` | 提示框（admonition）样式 |
| `_code.scss` | 代码块样式 |
| `_images.scss` | 图片样式 |
| `_margin.scss` | 边注/旁注/margin内容样式 |
| `_notebooks.scss` | Jupyter笔记本输出样式 |
| `_quotes.scss` | 引用块样式 |

### sections/ — 区域层

| 文件 | 职责 |
|------|------|
| `_announcement.scss` | 公告栏样式 |
| `_article-container.scss` | 文章容器 |
| `_article.scss` | 文章内容区 |
| `_footer-article.scss` | 文章底部页脚 |
| `_footer-content.scss` | 页脚内容区 |
| `_header-article.scss` | 文章头部 |
| `_header-primary.scss` | 顶部导航栏 |
| `_sidebar-primary.scss` | 主侧边栏 |
| `_sidebar-secondary.scss` | 次级侧边栏（TOC） |

### extensions/ — 第三方扩展适配层

| 文件 | 适配的扩展 |
|------|-----------|
| `_comments.scss` | 评论系统（如utterances） |
| `_myst-nb.scss` | MyST-NB（Jupyter笔记本执行） |
| `_sphinx-design.scss` | sphinx-design（卡片/网格/标签页等） |
| `_sphinx-tabs.scss` | sphinx-tabs（标签页） |
| `_sphinx-togglebutton.scss` | sphinx-togglebutton（内容折叠） |
| `_thebe.scss` | Thebe（在线代码执行） |

（F-182-F-185）

## 添加自定义CSS

### 方法1：通过 conf.py 添加CSS文件

最简单的方式是在项目的 `_static/` 目录下创建自定义CSS，然后在 `conf.py` 中添加：

```python
html_static_path = ["_static"]
html_css_files = [
    "css/custom.css",
]
```

### 方法2：覆盖SBT的CSS变量

SBT和PST使用CSS自定义属性（CSS变量），可以通过覆盖变量快速修改配色：

```css
/* _static/css/custom.css */
:root {
  /* 修改主色调 */
  --pst-color-primary: #2a7ae2;
  /* 修改侧边栏背景 */
  --pst-color-sidebar-background: #f8f9fa;
}
```

### 方法3：添加自定义SCSS（需要fork或子主题）

如需深度定制SCSS，需要：
1. Fork sphinx-book-theme 或创建子主题
2. 修改 SCSS 源文件
3. 使用 sphinx-theme-builder 重新编译静态资源

## 边注样式核心机制

`_margin.scss` 是SBT的样式核心之一，配合 `_transforms.py` 和 `nodes.py` 实现边注效果：

1. **宽屏布局**：margin/sidenote 元素通过CSS定位到右侧边距区域
2. **窄屏交互**：利用 `<label> + <input type="checkbox">` 的纯CSS `:checked` 伪类实现展开/收起，无需JavaScript
3. **TOC联动**：JS IntersectionObserver在边注可见时隐藏TOC（详见交互功能章节）

## 暗色模式

暗色模式完全继承自PST，通过 `data-theme="dark"` 属性切换。SBT的SCSS中：
- 颜色使用PST定义的CSS变量（如 `--pst-color-background`、`--pst-color-text`）
- 自定义颜色需要同时定义亮色和暗色变量
- 可通过 `html_theme_options` 配置 `pygments_dark_style` 暗色代码高亮

## 打印样式

`_print.scss` 和 `addNoPrint()` JS函数共同优化打印效果：

1. JS自动为导航元素添加 `.noprint` 类（F-176）
2. CSS通过 `@media print` 隐藏 `.noprint` 元素
3. layout.html 中的 `#jb-print-docs-body` 在打印时显示页面目录
4. `.onlyprint` 类在屏幕显示时隐藏，打印时显示
5. PDF按钮通过 `window.print()` 触发浏览器打印对话框

PDF导出推荐方式：
- 浏览器打印 → 保存为PDF
- 使用 `sphinx-sitemap` 等工具生成完整PDF
- 打印时浏览器自动应用打印样式

## 响应式断点

SBT继承Bootstrap 5的响应式断点体系：

| 断点 | 宽度 | 设备类型 | 侧边栏行为 |
|------|------|---------|-----------|
| xs | <576px | 手机 | 侧边栏隐藏，点击toggle打开modal |
| sm | ≥576px | 大屏手机 | 同上 |
| md | ≥768px | 平板 | 同上 |
| lg | ≥992px | 笔记本/桌面 | 主侧边栏可固定/折叠 |
| xl | ≥1200px | 大屏桌面 | 三栏全部显示 |
| xxl | ≥1400px | 超大屏 | 三栏+更宽边距 |

关键断点是 **992px（lg）**：`fixSidebarToggle()` JS函数在此断点以上拦截PST的modal行为，改为切换侧边栏可见性（F-228-F-238）。

## 第三方扩展适配

SBT内置了对以下扩展的CSS适配，使用这些扩展时无需额外调整样式：

### myst-nb

`_myst-nb.scss` 适配Jupyter笔记本的输出样式：
- 代码单元的输入/输出区域样式
- 笔记本单元格边距
- 执行计数编号样式
- ipywidget输出区域

### sphinx-design

`_sphinx-design.scss` 适配卡片、网格、标签页等组件在SBT三栏布局中的表现：
- 卡片阴影和边距调整
- 网格在内容区的宽度适配
- 标签页与SBT导航的样式协调

### sphinx-tabs

`_sphinx-tabs.scss` 适配sphinx-tabs扩展的标签页样式。

### sphinx-togglebutton

`_sphinx-togglebutton.scss` 适配内容折叠按钮的样式。

### Thebe

`_thebe.scss` 适配Thebe在线代码执行的UI：
- Thebe启动按钮样式
- 代码单元激活状态样式
- Thebe状态栏样式

### Pygments代码高亮

SBT默认使用 `tango` 作为亮色模式的Pygments样式（F-013）。暗色模式推荐使用 `monokai`：

```python
html_theme_options = {
    "pygments_light_style": "tango",
    "pygments_dark_style": "monokai",
}
```

## 全宽内容

SBT支持全宽（full-width）内容，某些元素可以打破内容区宽度限制延伸到边距区域。CSS类 `full-width` 的元素会被TOC隐藏Observer监听（F-171），当全宽内容可见时自动隐藏右侧TOC。

## 相关概念

- [主题架构与PST继承](/concepts/02-theme-architecture.md)
- [布局与模板定制](/concepts/07-layout-and-templates.md)
- [交互功能详解](/concepts/06-interactive-features.md)
- [Margin指令与边注旁注](/concepts/05-margin-sidenotes.md)
