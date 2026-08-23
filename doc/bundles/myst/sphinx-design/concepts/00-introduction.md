---
type: Concept
title: sphinx-design 简介
description: sphinx-design 的定位、核心特性、技术栈与适用场景
tags:
- sphinx
- extension
- design
- overview
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- pyproject.toml
- sphinx_design/__init__.py
---

# sphinx-design 简介

## 什么是 sphinx-design？

sphinx-design 是一个为 Sphinx 文档生成器设计的扩展，用于在 reStructuredText（rST）和 MyST Markdown 文档中创建美观、响应式的 Web 组件。它将 Bootstrap 设计系统的核心布局和组件能力移植到 Sphinx 生态中，让文档作者无需编写 HTML/CSS 即可使用卡片、网格、标签页、下拉折叠、徽章、按钮、图标等现代 Web UI 组件。

- **项目全称**：sphinx_design（Python 包名，下划线）
- **Sphinx 扩展名**：`sphinx_design`（在 `conf.py` 的 `extensions` 中添加）
- **作者**：Chris Sewell（Executable Books 社区）
- **许可证**：MIT
- **Python 要求**：>=3.11
- **运行时依赖**：仅 `sphinx>=7.2,<10`（零其他第三方 Python 依赖）

## 核心特性

### 1. 自包含设计系统

sphinx-design 自带完整的预编译 CSS（`sphinx-design.min.css`），所有组件使用 `sd-` 前缀的类名（如 `sd-card`、`sd-row`、`sd-btn-primary`），不会与任何 Sphinx 主题的 CSS 冲突。通过 `sd-sphinx-override` 类重置主题样式的干扰，实现真正的主题无关性。

### 2. 12 列响应式网格

基于 Bootstrap 的 12 列网格系统，支持 4 个响应式断点（xs/sm/md/lg），可定义每行列数、列跨度、间距（gutter）、flex 方向和对齐方式。

### 3. 丰富的组件库

| 组件类别 | 组件名 | 用途 |
|---|---|---|
| 布局 | grid / grid-item / grid-item-card / div | 响应式网格与通用容器 |
| 内容 | card / card-carousel | 卡片与横向滚动卡片组 |
| 交互 | dropdown | 原生 HTML5 `<details>` 折叠容器 |
| 交互 | tab-set / tab-item / tab-set-code | CSS 驱动标签页，JS 同步与持久化 |
| 行内 | bdg / bdg-link / bdg-ref | 徽章（纯色/轮廓/外链/内链） |
| 行内 | button-link / button-ref | 按钮（外部链接/内部引用） |
| 图标 | octicon / fontawesome / material-* | 三类内嵌图标系统 |
| 信息 | article-info | 文章元信息栏（头像/作者/日期/阅读时间） |

### 4. 两阶段渲染架构

- **第一阶段**（指令解析）：生成语义化的通用 AST（抽象语法树），确保 LaTeX/PDF/man 等非 HTML 格式有降级渲染
- **第二阶段**（Post-Transform）：仅在 HTML 构建时执行，将通用 AST 转换为 HTML 专用结构（如 `<details>/<summary>`、radio input + label），注入交互属性

### 5. 零 JS 折叠 + 轻量 JS 同步

dropdown 组件使用 HTML5 原生 `<details>/<summary>` 标签实现折叠，完全不需要 JavaScript；tab 组件使用 CSS `:checked` 伪类 + radio input 实现切换，仅同步和 localStorage 持久化需要少量 JS（`design-tabs.js`，约 227 行）。

### 6. 配置式自定义指令

通过 `sd_custom_directives` 配置，可以在 `conf.py` 中声明新指令继承内置指令并预设参数/选项，无需编写 Python 代码。

## 技术栈

- **CSS 框架**：自定义 Bootstrap 子集（预编译为 min.css，`sd-` 前缀命名空间）
- **JavaScript**：原生 ES6+（无框架依赖），约 227 行实现 tab 同步
- **图标**：GitHub Octicon（SVG 内嵌）、Material Design Icons（SVG 内嵌）、FontAwesome（CSS class，可选 CDN）
- **Sphinx API**：Directives、Roles、PostTransforms、自定义 Nodes、config values、event hooks

## 适用场景

1. **技术文档美化**：为 API 文档、教程、指南添加卡片式导航、标签页代码示例、折叠的注意事项
2. **文档网站搭建**：配合 Jupyter Book、sphinx-book-theme 创建类似 Material Design 风格的文档站
3. **多语言代码示例**：使用 `tab-set-code` 自动为不同语言的代码块创建标签页
4. **文章元信息**：使用 `article-info` 在文档顶部展示作者、日期、阅读时间
5. **快速原型**：通过网格+卡片快速构建文档首页的功能导航区

## 与其他方案的对比

| 特性 | sphinx-design | sphinx-panels（前身） | 手写 HTML |
|---|---|---|---|
| 运行时依赖 | 仅 sphinx | sphinx + 多个 | 无 |
| CSS 命名空间 | `sd-` 前缀，无冲突 | `card-` 前缀，可能冲突 | 自由 |
| 非 HTML 输出 | ✅ 降级渲染 | ⚠️ 部分支持 | ❌ 直接输出 HTML |
| 响应式网格 | ✅ 4 断点 | ✅ 基本支持 | 需自己写 |
| 图标系统 | ✅ 3 套内置 | ❌ 无 | 需自己引入 |
| Tab 同步 | ✅ localStorage + URL | ❌ 无 | 需自己写 JS |
| 配置式扩展 | ✅ custom_directives | ❌ 无 | 需写代码 |

## 相关概念

- [快速上手](/concepts/01-getting-started.md) — 安装与最小配置
- [扩展架构](/concepts/02-extension-architecture.md) — 两阶段渲染与组件注册机制
- [设计系统与CSS类](/concepts/03-design-system.md) — `sd-` 前缀CSS体系详解
