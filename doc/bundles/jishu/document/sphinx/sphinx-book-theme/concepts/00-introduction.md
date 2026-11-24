---
type: Concept
title: "定位与生态：一本书式的 Sphinx 主题"
description: "sphinx-book-theme 的设计目标、核心特性、与 pydata-sphinx-theme 和 Jupyter Book 的继承/消费关系，以及当前维护状态"
tags: [sphinx, theme, book, executable-books, jupyter-book]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-readme
    resource: https://github.com/executablebooks/sphinx-book-theme/blob/main/README.md
    title: sphinx-book-theme README
  - id: sbt-docs-index
    resource: https://sphinx-book-theme.readthedocs.io/
    title: Sphinx Book Theme documentation
  - id: sbt-local
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme
    title: 本地源码快照（1.5.0.dev）
---

# 定位与生态：一本书式的 Sphinx 主题

## 它解决什么问题

Sphinx 默认主题（如 [alabaster](../../alabaster/index.md)）面向"API 参考手册"：以函数、类、模块为一级对象，页面结构偏工具化。`sphinx-book-theme` 面向另一种文档形态——**单读者的连续叙事**：教程、教材、研究报告、可复现实验记录。它把页面组织成"书"：

- 左侧是全书目录（primary sidebar），持续可见。
- 中间是单列正文，保持适合长文阅读的行宽。
- 右侧是当前页目录（secondary sidebar），滚动时高亮。
- 页眉提供下载、源码、仓库、在线运行等工具箱。
- 正文可以"溢出"到右侧留白，形成 Tufte 风格的边注与 margin 内容。

## 核心特性

| 特性 | 具体表现 | 依赖 |
|------|---------|------|
| Bootstrap 5 视觉体系 | 按钮、下拉、导航、工具提示统一由 Bootstrap 组件实现 | pydata-sphinx-theme 内置 |
| 书籍式弹性布局 | 单列正文 + 双 sidebar；正文可占满、可出边 | 主题自身 SCSS |
| Tufte 风格边注 | 脚注转为编号边注；`{-}` 前缀转为无编号 margin note | `HandleFootnoteTransform` + `SideNoteNode` |
| `{margin}` 指令 | 块级内容放入右侧留白，可带标题 | `Margin(Sidebar)` 指令 |
| Notebook 视觉类 | 单元格输入/输出、隐藏输入、滚动输出、全宽单元格 | MyST-NB 生成的 HTML class |
| 在线交互启动按钮 | Binder、JupyterHub、Colab、Deepnote、JupyterLite、Thebe | `header_buttons/launch.py` |
| 源文件工具箱 | 下载 `.md`/`.ipynb`/打印 PDF、查看源码、建议编辑、开 issue | `header_buttons/source.py` |
| 国际化 | 主题内置文案走 Sphinx message catalog | `booktheme` 翻译目录 |

## 与 pydata-sphinx-theme 的关系

这是理解源码最重要的一条关系：

```text
pydata-sphinx-theme（父主题）
        ▲  inherit = pydata_sphinx_theme
        │
sphinx-book-theme（子主题）
        │  extends "pydata_sphinx_theme/layout.html"
        ▼
最终 HTML
```

- `theme.conf` 第一行就是 `inherit = pydata_sphinx_theme`。
- `layout.html` 只做三件事：没有 navbar 内容时跳过 `<header>`、插入滚动检测像素、插入仅供打印的目录。
- 导航、搜索、主题切换器、页面骨架、Bootstrap 资源都来自父主题。
- 因此排查问题时，先判断某个 class/函数是"本书主题新增"还是"父主题提供"。`ARCHITECTURE.md` 明确建议：不确定时去 pydata-sphinx-theme 源码里搜。

> **版本耦合**：当前源码 `pyproject.toml` 将父主题**精确锁定**为 `pydata-sphinx-theme==0.23.0`，同时要求 `sphinx>=8.2`、Python `>=3.11`。父主题升级需要同步验证本书主题的模板与测试快照。

## 与 Jupyter Book 的关系

`sphinx-book-theme` 是 **Jupyter Book 的默认主题**。两者的分工是：

- Jupyter Book 负责"书籍工程"：目录配置、Notebook 执行、多格式导出、构建 CLI。
- `sphinx-book-theme` 负责"书的样子"：HTML 布局、导航、边注、启动按钮。
- `myst-nb` / `myst-parser` 负责"内容语法"：Markdown 中的指令、角色、代码单元格。

所以本书主题的很多能力（Notebook 样式、Thebe、下载 `.ipynb`）不是主题单独实现的，而是与 MyST-NB 约定好的 HTML 结构与元数据协作。

## 维护状态与版本

| 项目 | 事实 |
|------|------|
| 维护模式 | README 标注 Maintenance Mode：接受缺陷修复，不保证新功能 |
| 源码版本 | `src/sphinx_book_theme/__init__.py` 中 `__version__ = "1.5.0.dev"` |
| 最近正式版 | CHANGELOG 顶部为 `v1.4.0`（2026-07-19） |
| 父主题版本 | `pydata-sphinx-theme==0.23.0` |
| Sphinx 下限 | `sphinx>=8.2` |
| Python 下限 | `>=3.11` |
| 许可证 | BSD-3-Clause |
| 构建后端 | `sphinx-theme-builder >= 0.2.0a7` |

> 版本判断请以 `pyproject.toml` 与 `__init__.py` 为准；CHANGELOG 只记录已发布版本，开发版号可能领先一个版本。

## 何时选它，何时不选

适合：

- 你写的是**连续阅读**的教程、教材、课程讲义、实验报告。
- 你使用 MyST Markdown / Jupyter Notebook，希望代码、输出、交互按钮在同一页。
- 你需要边注、margin、全宽图表等"学术排版"表达。
- 你接受 Bootstrap 5 的视觉语言，不想从零写主题。

不适合：

- 你需要多读者角色、多套文档门户、复杂版本矩阵——pydata-sphinx-theme 或专门的门户主题更合适。
- 你只写 API 参考，不需要叙事型排版——alabaster、Furo 更轻。
- 你依赖频繁的新功能迭代——本项目已进入维护模式。

## 相关概念

- [安装与最小站点](01-getting-started.md)
- [主题骨架与构建链](02-theme-architecture.md)
- [页面分区与导航](03-layout-and-navigation.md)
