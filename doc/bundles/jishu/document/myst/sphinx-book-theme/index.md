---
type: bundle
title: sphinx-book-theme 知识包
description: sphinx-book-theme 中文 Wiki 教程——基于 pydata-sphinx-theme 的科学书籍式 Sphinx 主题，支持交互式计算按钮、边注/旁注、下载/全屏等功能
okf_version: '0.2'
tags:
- sphinx-book-theme
- sphinx
- theme
- pydata-sphinx-theme
- jupyter-book
- documentation
- executable-books
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- "https://github.com/executablebooks/sphinx-book-theme"
- "https://sphinx-book-theme.readthedocs.io/"
- pyproject.toml
- src/sphinx_book_theme/
---

# sphinx-book-theme 知识包

sphinx-book-theme 是 Executable Books 团队开发的 Sphinx 主题，专为科学解释文档和书籍式文档设计。它在 pydata-sphinx-theme（PST）基础上提供了干净的三栏书籍布局、交互式计算启动按钮（Binder/Colab/JupyterHub/Thebe）、边注/旁注、下载/全屏等功能，是 Jupyter Book 的默认主题。

## 知识地图

```
入门 → 架构 → 配置 → 功能 → 定制
│       │       │      │      │
│       │       │      │      └── 样式与扩展适配
│       │       │      │      └── 模板与布局定制
│       │       │      └── 交互功能（全屏/Thebe/打印）
│       │       │      └── 边注与Margin指令
│       │       └── 头部按钮系统（下载/启动/源码）
│       │       └── 配置系统详解
│       └── PST继承机制与事件体系
│       └── 主题架构
└── 安装与基础配置
└── 主题概述
```

## 推荐学习路径

### 🟢 初学者：构建第一本书

1. [主题概述](concepts/00-introduction.md) → 了解定位和特性
2. [安装与基础配置](concepts/01-getting-started.md) → 安装、启用、验证
3. [基础书籍配置示例](examples/basic-book-setup.md) → 复制配置快速开始
4. [配置系统详解](concepts/03-configuration.md) → 按需调整配置项

### 🟡 进阶用户：添加交互功能

5. [头部按钮系统](concepts/04-header-buttons.md) → 理解按钮机制
6. [Margin指令与边注旁注](concepts/05-margin-sidenotes.md) → 丰富文档排版
7. [交互功能详解](concepts/06-interactive-features.md) → 全屏/TOC/Thebe
8. [交互式计算书籍示例](examples/interactive-book.md) → 配置Binder/Colab/Thebe

### 🔴 高级用户：深度定制

9. [主题架构与PST继承](concepts/02-theme-architecture.md) → 理解继承链和事件系统
10. [布局与模板定制](concepts/07-layout-and-templates.md) → 覆盖模板和组件
11. [样式定制与扩展适配](concepts/08-customization.md) → SCSS/暗色模式/打印
12. [国际化与高级主题](concepts/09-internationalization.md) → 子主题/翻译/缓存

## 核心洞察

### 1. 薄定制层模式

SBT 并非从零构建的主题，而是在 PST 上做"配置覆盖+组件增量+交互增强"的薄定制层。PST 提供三栏布局骨架和 Bootstrap 5 体系，SBT 专注于书籍特有的功能组合。

### 2. 事件优先级编排

头部按钮通过三阶段事件流水线注入：准备（prep）→ 平台按钮（launch/source）→ 通用按钮（download/fullscreen），priority=501 确保在 PST 设置完编辑URL之后运行。

### 3. AST级别的内容迁移

边注功能通过 Post-Transform 在AST层将脚注从文档末尾迁移到引用旁，配合 `<label> + <input type="checkbox">` 纯CSS交互实现移动端展开。

### 4. 双初始化困境

Sphinx主题与扩展初始化时机不同，SBT通过 setup() 立即调用 + config-inited 事件监听双重调用解决配置覆盖问题。

## 核心数据速查

| 属性 | 值 |
|------|-----|
| 版本 | 1.5.0.dev |
| Python要求 | >= 3.11 |
| Sphinx要求 | >= 8.2 |
| PST依赖 | pydata-sphinx-theme == 0.20.0 |
| 许可证 | BSD-3-Clause |
| 构建系统 | sphinx-theme-builder (Node.js 20.9.0) |
| 自定义指令 | `margin` |
| 自定义节点 | `SideNoteNode` |
| Post-Transform | `HandleFootnoteTransform`（priority=1） |
| 消息目录名 | `booktheme` |

## 文档结构

- [概念文档（10篇）](concepts/index.md) — 系统性介绍各功能模块
- [示例文档（2篇）](examples/index.md) — 可直接使用的配置示例
- [参考文档（1篇）](references/index.md) — 配置速查、API参考
- [R阶段事实采集](spec/facts.md) — 192条零推断源码事实
- [I阶段洞察提炼](spec/insights.md) — 4个核心洞察与知识地图

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
