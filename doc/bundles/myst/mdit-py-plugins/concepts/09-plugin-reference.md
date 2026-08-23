---
type: Concept
title: 插件速查表
description: mdit-py-plugins 全部22个插件的函数名、导入路径、语法、参数、Token类型速查
tags:
- mdit-py-plugins
- reference
- quickref
- cheatsheet
difficulty: 高级
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

# 插件速查表

## 导入与使用

```python
from mdit_py_plugins.<module> import <plugin_func>
md = MarkdownIt().use(<plugin_func>, **options)
```

## 速查表

| 插件 | 导入 | 语法 | 类型 | 关键参数 | Token类型 |
|------|------|------|------|---------|----------|
| admon | `mdit_py_plugins.admon` | `!!! type "Title"` | Block | - | admonition_open/close |
| amsmath | `mdit_py_plugins.amsmath` | `\begin{align}...\end{align}` | Block | renderer | amsmath |
| anchors | `mdit_py_plugins.anchors` | （自动为标题加id） | Core | - | (修改heading attrs) |
| attrs | `mdit_py_plugins.attrs` | `{.class #id}` | Inline+Block | allowed | (添加attrs) |
| colon_fence | `mdit_py_plugins.colon_fence` | `:::lang\n:::` | Block | - | colon_fence |
| container | `mdit_py_plugins.container` | `:::name\n:::` | Block | name, marker, validate, render | container_open/close |
| deflist | `mdit_py_plugins.deflist` | `Term\n: Def` | Block | - | dl/dt/dd |
| dollarmath | `mdit_py_plugins.dollarmath` | `$x$` / `$$x$$` | Block+Inline | allow_labels/space/digits/blank_lines, renderer, label_renderer | math_inline, math_inline_double, math_block, math_block_label |
| field_list | `mdit_py_plugins.field_list` | `:name: value` | Block | - | field_list_open/close, fieldlist_name_open/close, fieldlist_body_open/close |
| footnote | `mdit_py_plugins.footnote` | `[^n]` / `[^n]:` | Block+Inline+Core | inline, move_to_end, always_match_refs | footnote_ref, footnote_open/close, footnote_block_open/close, footnote_anchor |
| front_matter | `mdit_py_plugins.front_matter` | `---\nYAML\n---` | Block | - | front_matter |
| gfm | `mdit_py_plugins.gfm` | （组合插件） | 组合 | dollarmath, front_matter, tasklists_editable | （组合多个插件） |
| gfm_autolink | `mdit_py_plugins.gfm_autolink` | `https://...` | Inline | - | link_open/close |
| myst_blocks | `mdit_py_plugins.myst_blocks` | ````{directive}``` | Block | - | myst_block |
| myst_role | `mdit_py_plugins.myst_role` | `` {role}`text` `` | Inline | - | myst_role |
| section_ref | `mdit_py_plugins.section_ref` | - | Block | - | - |
| subscript | `mdit_py_plugins.subscript` | `~sub~` | Inline | - | sub_open/close |
| superscript | `mdit_py_plugins.superscript` | `^sup^` | Inline | - | sup_open/close |
| tasklists | `mdit_py_plugins.tasklists` | `- [x] task` | Core | enabled, label, label_after | html_inline(checkbox) |
| texmath | `mdit_py_plugins.texmath` | `\(x\)` / `\[x\]` | Block+Inline | - | math_inline/block |
| wordcount | `mdit_py_plugins.wordcount` | （自动统计） | Core | per_minute, count_func, store_text | （无新Token） |
| substitution | `mdit_py_plugins.substitution` | {{variable}} | Inline | - | - |
