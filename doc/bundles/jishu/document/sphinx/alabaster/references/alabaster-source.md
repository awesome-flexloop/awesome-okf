---
type: Reference
title: Alabaster 源码路径映射
description: Alabaster 核心源文件路径、职责与关键代码位置索引
tags: [sphinx, theme, source, alabaster]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: alabaster-repo
    resource: https://github.com/sphinx-doc/alabaster
    title: Alabaster GitHub Repository
---

# Alabaster 源码路径映射

本文档为 Alabaster 源码的文件级索引，标注每个核心文件的路径、职责和关键代码行号。源路径相对于 `external/libs/docs/alabaster/`。

## 核心文件清单

| 文件 | 行数 | 职责 | 关键代码 |
|------|------|------|---------|
| `alabaster/__init__.py` | 39 行 | 主题注册入口、事件钩子、路径工具 | `setup()` L30-39、`update_context()` L15-27、`get_path()` L7-12 |
| `alabaster/support.py` | 89 行 | 自定义 Pygments 语法高亮样式 | `class Alabaster(Style)` L19-89 |
| `alabaster/theme.conf` | 132 行 | 主题元信息与 50+ 默认配置选项 | `[theme]` L1-5、`[options]` L7-132 |
| `alabaster/layout.html` | 130 行 | 主页面布局模板（继承 basic/layout.html） | `rellink_markup()` 宏 L17-34、`content` 块 L44-86、`footer` 块 L88-129 |
| `alabaster/about.html` | 59 行 | 侧边栏 Logo/项目名/描述/GitHub 徽章组件 | Logo 渲染 L1-14、GitHub 按钮 L20-27、Travis/CodeCov L29-59 |
| `alabaster/navigation.html` | 10 行 | 侧边栏目录树导航组件 | `toctree()` 调用 L2、`extra_nav_links` L3-9 |
| `alabaster/relations.html` | 21 行 | 侧边栏面包屑+上下页导航组件 | 父子层级嵌套 `<ul>` L4-19 |
| `alabaster/donate.html` | 28 行 | 侧边栏捐赠/支持链接组件 | donate_url L7-13、opencollective L15-21、tidelift L23-27 |

## 静态资源

| 路径 | 说明 |
|------|------|
| `alabaster/static/alabaster.css_t` | Sass 模板样式表（使用 theme.conf 中的变量） |
| `alabaster/static/custom.css` | 用户自定义 CSS 覆盖的约定文件名（自动加载） |
| `alabaster/static/github-banner.svg` | 默认 "Fork me on GitHub" 角标图片 |

## 构建与配置文件

| 文件 | 说明 |
|------|------|
| `pyproject.toml` | 项目元数据、依赖声明、entry point 配置 |
| `LICENSE.rst` | BSD-3-Clause 许可证文本 |
| `README.rst` | 项目简介 |
| `.readthedocs.yml` | Read the Docs 构建配置 |

## 文档文件

| 文件 | 说明 |
|------|------|
| `docs/index.rst` | 文档入口，包含 Features 和项目背景 |
| `docs/installation.rst` | 安装与基础配置指南 |
| `docs/customization.rst` | 完整的主题选项参考（50+ 选项分类说明） |
| `docs/changelog.rst` | 版本变更记录 |
| `docs/conf.py` | 文档构建的 Sphinx 配置（Alabaster 自身使用 Alabaster 主题的示例） |

## setup() 函数源码参考

```python
def setup(app):
    app.require_sphinx("6.2")
    theme_path = os.path.abspath(os.path.dirname(__file__))
    app.add_html_theme("alabaster", theme_path)
    app.connect("html-page-context", update_context)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
```

## entry point 配置参考（pyproject.toml）

```toml
[project.entry-points."sphinx.html_themes"]
alabaster = "alabaster"
```

## 相关概念

- [主题架构四要素](../concepts/02-theme-architecture.md)
- [setup 函数与注册机制](../concepts/03-setup-and-registration.md)
- [主题配置选项体系](../concepts/04-theme-options.md)
- [侧边栏组件化设计](../concepts/05-sidebar-components.md)
