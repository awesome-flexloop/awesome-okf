---
type: bundle
title: sphinx-tabs
description: Executable Books 生态的 Sphinx 标签页组件扩展，提供可切换标签页、多语言代码示例、跨页分组同步和无障碍 WAI-ARIA 支持
tags:
- sphinx
- extension
- tabs
- tabbed-content
- code-tab
- group-tab
- executable-books
- accessibility
- wai-aria
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23T03:40:00Z"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- id: tabs-repo
  resource: "https://github.com/executablebooks/sphinx-tabs"
  title: sphinx-tabs GitHub Repository
okf_version: '0.2'
---

# sphinx-tabs

sphinx-tabs 是 Executable Books 生态中的 Sphinx 标签页（Tabbed Content）组件扩展，支持创建可切换的标签页面板、多语言代码示例（code-tab）、跨页面分组标签同步（group-tab），输出符合 WAI-ARIA 无障碍标准。

## 核心功能

- **基础标签页**：`.. tabs::` + `.. tab::` 指令创建可切换面板
- **代码标签页**：`.. code-tab::` 自动识别 Pygments lexer 并语法高亮
- **分组同步**：`.. group-tab::` 跨页面记忆用户选择（sessionStorage）
- **无障碍设计**：WAI-ARIA Tabs Pattern、键盘左右箭头导航
- **条件资源加载**：仅使用标签页的页面加载 CSS/JS
- **嵌套支持**：标签页内可嵌套标签页

## 文档导航

| 章节 | 链接 |
|------|------|
| 📖 入门 | [概念文档](/concepts/index.md) |
| 💡 示例 | [示例代码](/examples/index.md) |
| 📚 参考 | [源码参考](/references/index.md) |
| 🔬 规格 | [事实清单](/spec/facts.md) · [架构洞察](/spec/insights.md) |

## 快速开始

```bash
pip install sphinx-tabs
```

```python
# conf.py
extensions = ['sphinx_tabs.tabs']
```

```rst
.. tabs::

   .. code-tab:: python

      print("Hello, World!")

   .. code-tab:: javascript

      console.log("Hello, World!");
```

## 更新日志

见 [log.md](/log.md)。
