---
type: Reference
title: sphinx-tabs 源码路径映射
description: sphinx-tabs 核心源文件路径、职责与关键代码位置索引
tags: [sphinx, tabs, source, directive, executable-books]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:20:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: tabs-repo
    resource: https://github.com/executablebooks/sphinx-tabs
    title: sphinx-tabs GitHub Repository
---

# sphinx-tabs 源码路径映射

本文档为 sphinx-tabs 源码的文件级索引。源路径相对于 `external/libs/ai/executablebooks/sphinx-tabs/`。

## 核心文件清单

| 文件 | 行数 | 职责 | 关键代码 |
|------|------|------|---------|
| `sphinx_tabs/__init__.py` | 1 行 | 版本号声明 | `__version__ = "3.6.0.dev"` |
| `sphinx_tabs/tabs.py` | 348 行 | 全部指令、节点、事件处理逻辑 | `TabsDirective` L80-131、`TabDirective` L134-211、`CodeTabDirective` L230-278、`setup()` L325-348 |
| `sphinx_tabs/static/tabs.js` | - | 前端标签切换交互 | `changeTabs()` L59-82、键盘导航 L28-52、sessionStorage L20-21 |
| `sphinx_tabs/static/tabs.css` | - | 标签页样式 | `.sphinx-tabs`、`.sphinx-tabs-tab`、`.sphinx-tabs-panel` 样式 |

## 四个指令一览

| 指令 | 类名 | 继承 | 核心功能 |
|------|------|------|---------|
| `.. tabs::` | TabsDirective | SphinxDirective | 标签页容器，管理 tablist 和 ARIA 属性 |
| `.. tab::` | TabDirective | SphinxDirective | 单个标签页面板 |
| `.. group-tab::` | GroupTabDirective | TabDirective | 跨页面同步选中的标签页 |
| `.. code-tab::` | CodeTabDirective | GroupTabDirective | 代码块标签页（自动 lexer 识别+跨页同步） |

## setup() 函数关键逻辑

```python
def setup(app):
    app.add_config_value("sphinx_tabs_valid_builders", [], "")
    app.add_config_value("sphinx_tabs_disable_css_loading", False, "html", [bool])
    app.add_config_value("sphinx_tabs_disable_tab_closing", False, "html", [bool])
    # 注册4个自定义节点
    app.add_node(SphinxTabsContainer, html=(visit, depart))
    app.add_node(SphinxTabsPanel, html=(visit, depart))
    app.add_node(SphinxTabsTab, html=(visit, depart))
    app.add_node(SphinxTabsTablist, html=(visit, depart))
    # 注册4个指令
    app.add_directive("tabs", TabsDirective)
    app.add_directive("tab", TabDirective)
    app.add_directive("group-tab", GroupTabDirective)
    app.add_directive("code-tab", CodeTabDirective)
    # 条件加载静态资源
    app.connect("html-page-context", update_context)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
```

## 相关概念

- [简介](/concepts/00-introduction.md)
- [四个指令详解](/concepts/02-directives.md)
- [分组标签与代码标签](/concepts/03-group-and-code-tabs.md)
