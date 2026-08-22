---
type: Concept
title: 00 - sphinx-book-theme 主题概述
description: sphinx-book-theme 的定位、核心特性、技术栈与适用场景
tags:
- sphinx-book-theme
- introduction
- overview
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- pyproject.toml
- src/sphinx_book_theme/__init__.py
- src/sphinx_book_theme/theme/sphinx_book_theme/theme.conf
---

# sphinx-book-theme 主题概述

sphinx-book-theme 是 Executable Books 团队开发的一款 Sphinx 主题（theme），专为科学解释文档和书籍式文档设计。它在 pydata-sphinx-theme（PST）基础上进行薄定制，提供了干净的书籍式三栏布局、交互式计算按钮、边注/旁注、下载/全屏等实用功能。

## 核心定位

sphinx-book-theme 不是从零构建的独立主题，而是建立在 pydata-sphinx-theme 之上的**定制层**。PST 提供了完整的三栏布局骨架（顶部导航栏 + 左侧主侧边栏 + 右侧页内目录 + 中央内容区）、Bootstrap 5 组件体系、暗色/亮色模式切换等基础能力。sphinx-book-theme 在此基础上做了三件事：

1. **重新编排组件**：清空 PST 默认的导航栏组件，将关键操作（下载、启动、源码按钮）集中到文章头部右侧
2. **添加书籍特有功能**：边注/旁注、Margin 指令、打印优化
3. **集成交互式计算**：Binder、JupyterHub、Colab、Thebe 等一键启动按钮

## 核心特性

- **三栏书籍式布局**：左侧全局导航、右侧页内目录、中央内容区，窄屏自动折叠
- **交互式启动按钮**：一键在 Binder/JupyterHub/Colab/Deepnote/JupyterLite/Thebe 中打开笔记本
- **源码操作按钮**：链接仓库、查看源码、在线编辑、提交Issue
- **下载按钮**：下载源文件、ipynb笔记本、PDF打印
- **边注/旁注**：将标准脚注自动转换为右侧边距注释，支持有编号旁注和无编号边注
- **Margin 指令**：将任意内容放入右侧边距
- **全屏模式**：一键切换全屏阅读
- **暗色模式**：继承 PST 的暗色/亮色主题切换
- **打印优化**：专用打印样式，自动隐藏导航元素，添加打印目录
- **国际化**：支持多语言翻译
- **第三方扩展适配**：内置对 myst-nb、sphinx-design、sphinx-tabs、sphinx-togglebutton、thebe 等扩展的样式适配

## 技术栈

| 层面 | 技术 |
|------|------|
| 构建 | sphinx-theme-builder（Node.js 20.9.0 + webpack） |
| 主题基础 | pydata-sphinx-theme == 0.20.0 |
| 前端框架 | Bootstrap 5（继承自PST） |
| 样式 | SCSS，按 abstracts/base/components/content/extensions/sections 分层 |
| 图标 | Font Awesome（继承自PST）+ 自定义平台SVG图标 |
| Python依赖 | Sphinx >= 8.2 |
| Python版本 | >= 3.11 |
| 许可证 | BSD-3-Clause |

## 适用场景

sphinx-book-theme 特别适合以下场景：

- **Jupyter Book 书籍**：这是 Jupyter Book 的默认主题，配合 MyST-NB 构建可执行书籍
- **技术文档/教程**：需要边注、代码示例下载、交互执行的教程文档
- **科学计算文档**：需要展示公式、代码、可视化结果的科研文档
- **开源项目文档**：需要链接GitHub仓库、在线编辑功能的项目文档
- **课程材料**：需要Binder/Colab集成，让学生一键运行代码的教学材料

## 与其他主题的关系

```
sphinx-book-theme
    └── 继承 → pydata-sphinx-theme (PST)
                    └── 使用 → Bootstrap 5
```

sphinx-book-theme 在 PST 的基础上添加了书籍特有的功能，但 PST 的所有配置项和组件都可以通过 `html_theme_options` 使用。定制 SBT 时，应同时参考 PST 和 SBT 两份文档。

## 相关概念

- [安装与基础配置](/concepts/01-getting-started.md)
- [主题架构与PST继承](/concepts/02-theme-architecture.md)
- [配置系统详解](/concepts/03-configuration.md)
- [头部按钮系统](/concepts/04-header-buttons.md)
- [Margin指令与边注旁注](/concepts/05-margin-sidenotes.md)
