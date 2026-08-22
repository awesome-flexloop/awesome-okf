---
type: concept
title: 01 - 安装、启用与基础配置
description: sphinx-book-theme 的安装方法、启用步骤、最小配置和常见问题排查
tags:
- sphinx-book-theme
- installation
- getting-started
- configuration
generated: 2026-08-23
status: stable
stale_after: 2027-08-23
sources:
- pyproject.toml
- src/sphinx_book_theme/__init__.py
---

# 安装、启用与基础配置

## 安装

使用 pip 安装 sphinx-book-theme：

```bash
pip install sphinx-book-theme
```

依赖会自动安装，核心依赖包括：
- Sphinx >= 8.2
- pydata-sphinx-theme == 0.20.0

> **注意**：pydata-sphinx-theme 被锁定为 0.20.0 版本，不兼容其他版本。

## 启用主题

在 Sphinx 的 `conf.py` 中设置：

```python
html_theme = "sphinx_book_theme"
```

主题通过入口点（entry point）`sphinx.html_themes` 自动注册，无需手动添加到 `extensions` 列表。但如果你需要使用边注、Margin 指令等**扩展功能**（不仅是主题外观），还需要添加：

```python
extensions = [
    "sphinx_book_theme",
    # ... 其他扩展
]
```

> **为什么要加 extensions？** sphinx-book-theme 既是主题也是扩展。主题功能（布局、样式）通过 `html_theme` 启用，但指令（margin）、Transform（脚注转边注）、事件钩子（按钮注入）等扩展功能需要在 `extensions` 中声明才能激活。如果你的 conf.py 中 `html_theme = "sphinx_book_theme"` 但边注不工作，检查是否添加了 extensions。

## 最小配置

一个最小的 conf.py 配置示例：

```python
project = "My Book"
author = "Author Name"

html_theme = "sphinx_book_theme"
html_theme_options = {
    "repository_url": "https://github.com/username/repo",
    "use_repository_button": True,
    "use_download_button": True,
}
```

## 验证安装

构建文档后，检查以下几点确认主题正常工作：

1. 页面呈现三栏布局（主侧边栏 + 内容区 + 页内目录）
2. 文章头部右侧出现下载按钮组（📥图标）
3. 左上角显示站点标题/Logo
4. 暗色/亮色模式切换按钮可用

如果只看到基本的 Sphinx 页面样式，检查：
- `html_theme` 是否正确拼写为 `"sphinx_book_theme"`（下划线，非连字符）
- 运行 `pip list | grep sphinx-book-theme` 确认包已安装
- 清除构建缓存：`make clean && make html`

## 常见问题

### Q: 导航栏是空的？
SBT 默认清空了 PST 的导航栏组件（navbar_start/center/end/persistent），这是设计行为。导航通过主侧边栏（左侧）实现。如需在导航栏添加内容，通过 `html_theme_options` 配置相应组件。

### Q: 按钮不显示？
按钮通过事件钩子动态注入，需要主题扩展正确加载。确认：
1. `"sphinx_book_theme"` 在 extensions 列表中
2. 按钮对应的配置项设为 True（如 `use_repository_button: True`）
3. 仓库按钮需要配置 `repository_url`

### Q: 边注不工作？
边注功能需要：
1. `"sphinx_book_theme"` 在 extensions 列表中
2. `html_theme_options` 中设置 `"use_sidenotes": True`
3. 使用标准脚注语法（MyST: `[^1]`，rST: `[#1]_`）

### Q: 与 myst-nb 配合使用需要注意什么？
myst-nb 不是 SBT 的核心依赖，但 SBT 内置了对 myst-nb 的样式适配。建议同时安装：

```bash
pip install myst-nb
```

并在 conf.py 添加：

```python
extensions = ["sphinx_book_theme", "myst_nb"]
```

ipynb 笔记本的下载按钮会自动出现（F-066、F-067）。

## 相关概念

- [主题概述](/concepts/00-introduction.md)
- [主题架构与PST继承](/concepts/02-theme-architecture.md)
- [配置系统详解](/concepts/03-configuration.md)
- [头部按钮系统](/concepts/04-header-buttons.md)
- [基础配置示例](/examples/basic-book-setup.md)
