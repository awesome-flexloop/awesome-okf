---
type: Concept
title: mdit-py-plugins 简介
description: mdit-py-plugins 是 markdown-it-py 的官方插件集合，提供脚注、数学公式、定义列表、任务列表、GFM扩展等22个插件
tags:
- mdit-py-plugins
- markdown-it-py
- plugins
- markdown
- extension
difficulty: 入门
estimated_time: 10分钟
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: mdit-py-plugins-source
  resource: /references/plugin-source-mapping.md
  title: mdit-py-plugins 源码路径映射
---

# mdit-py-plugins 简介

## 它是什么

mdit-py-plugins 是 [markdown-it-py](https://github.com/executablebooks/markdown-it-py) 的官方插件集合，版本 0.7.0，MIT 许可证。它提供了22个常用的 Markdown 语法扩展插件，包括脚注、数学公式、定义列表、任务列表、GFM自动链接、前置元数据等，被 [MyST-Parser](https://github.com/executablebooks/MyST-Parser) 广泛使用。

```python
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.dolarmath import dollarmath_plugin

md = MarkdownIt().use(footnote_plugin).use(dollarmath_plugin)
html = md.render("Here is a note[^1] and $x^2$ math.\n\n[^1]: Footnote content.")
```

## 安装

```bash
pip install mdit-py-plugins
```

唯一的运行时依赖是 markdown-it-py（>=2.0.0, <5.0.0）。

## 插件分类

### 块级语法插件

| 插件 | 语法 | 说明 |
|------|------|------|
| front_matter | `---\nYAML\n---` | 文档起始的YAML元数据 |
| colon_fence | `:::name\ncontent\n:::` | 冒号围栏代码块（替代反引号） |
| amsmath | `\begin{gather}...\end{gather}` | AMS数学环境 |
| container | `:::warning\ncontent\n:::` | 自定义容器div |
| deflist | `Term\n: Definition` | 定义列表（Pandoc风格） |
| fieldlist | `:name: value` | reST风格字段列表 |
| admon | `!!! note "Title"` | 告警/提示块 |
| section_ref | - | 章节引用 |
| myst_blocks | ` ```{directive} ` | MyST指令块 |

### 行内语法插件

| 插件 | 语法 | 说明 |
|------|------|------|
| dollarmath(inline) | `$x^2$` | 行内数学公式 |
| subscript | `~H~2~O` | 下标（`<sub>`） |
| superscript | `^super^script` | 上标（`<sup>`） |
| myst_role | `` {role}`text` `` | MyST角色语法 |
| gfm_autolink | `https://example.com` | GFM自动链接（不用`<>`包裹） |
| attrs(inline) | `text{.class}` | 行内属性 |
| texmath(inline) | `\(x^2\)` | TeX行内公式 |

### 核心后处理插件

| 插件 | 功能 |
|------|------|
| footnote | 脚注（block+inline+core三链协作） |
| tasklists | 任务列表复选框（`- [x] done`） |
| wordcount | 字数统计 |
| anchors | 标题锚点 |
| substitution | 文本替换 |

### 组合插件

| 插件 | 功能 |
|------|------|
| gfm | GFM风格组合（表格+删除线+任务列表+自动链接+脚注） |

## 生态位置

```
MyST-Parser
    ↓
mdit-py-plugins（本项目）→ markdown-it-py → mdurl
```

- **上层**：MyST-Parser 使用 mdit-py-plugins 的多个插件（dollarmath、footnote、attrs、myst_role、myst_blocks 等）
- **下层**：基于 markdown-it-py 的插件 API（Ruler + add_render_rule + env）

## 与JS markdown-it插件的关系

多个插件移植自 JS markdown-it 生态：
- footnote ← markdown-it-footnote
- container ← markdown-it-container
- deflist ← markdown-it-deflist
- front_matter ← markdown-it-front-matter
- sub ← markdown-it-sub
- tasklists ← markdown-it-task-lists

## 下一步

- [插件基础](01-plugin-basics.md) — 理解插件工作原理
- [使用插件](02-using-plugins.md) — 快速上手常用插件
