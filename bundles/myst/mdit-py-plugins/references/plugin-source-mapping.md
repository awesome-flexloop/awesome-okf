---
type: Reference
title: mdit-py-plugins 插件源码映射
description: mdit-py-plugins 全部22个插件的源码路径、导出函数、规则类型和Token类型索引
tags: [mdit-py-plugins, plugins, source, reference]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: mdit-py-plugins-repo
    resource: https://github.com/executablebooks/mdit-py-plugins
    title: mdit-py-plugins GitHub Repository
---

# mdit-py-plugins 插件源码映射

## 项目元数据

| 属性 | 值 |
|------|-----|
| 名称 | mdit-py-plugins |
| 版本 | 0.7.0 |
| 描述 | Collection of plugins for markdown-it-py |
| 许可证 | MIT |
| Python 要求 | >=3.10 |
| 运行时依赖 | markdown-it-py >=2.0.0,<5.0.0 |
| 构建系统 | flit_core >=3.4,<4 |

## 插件全览

| 插件名 | 导出函数 | 类型 | 源路径 | 注册位置 |
|--------|---------|------|--------|---------|
| admon | `admon_plugin` | Block | `admon/` | block.ruler |
| amsmath | `amsmath_plugin` | Block | `amsmath/__init__.py` | block.ruler (before blockquote) |
| anchors | `anchors_plugin` | Core | `anchors/` | core.ruler |
| attrs | `attrs_plugin`, `attrs_block_plugin` | Inline+Block | `attrs/` | inline.ruler + block.ruler |
| colon_fence | `colon_fence_plugin` | Block | `colon_fence.py` | block.ruler (before fence) |
| container | `container_plugin` | Block | `container/` | block.ruler |
| deflist | `deflist_plugin` | Block | `deflist/` | block.ruler |
| dollarmath | `dollarmath_plugin` | Block+Inline | `dollarmath/` | block.ruler (before fence) + inline.ruler (before escape) |
| field_list | `fieldlist_plugin` | Block | `field_list/` | block.ruler (before paragraph) |
| footnote | `footnote_plugin` | Block+Inline+Core | `footnote/` | block.ruler (before reference) + inline.ruler (after image) + core.ruler (after inline) |
| front_matter | `front_matter_plugin` | Block | `front_matter/` | block.ruler (before table) |
| gfm | `gfm_plugin` | 组合 | `gfm/` | 组合多个插件+enable内置规则 |
| gfm_autolink | `gfm_autolink_plugin` | Inline | `gfm_autolink/` | inline.ruler |
| myst_blocks | （待确认） | Block | `myst_blocks/` | block.ruler |
| myst_role | `myst_role_plugin` | Inline | `myst_role/` | inline.ruler |
| section_ref | `section_ref_plugin` | Block | `section_ref/` | block.ruler |
| subscript | `sub_plugin` | Inline | `subscript/` | inline.ruler (after emphasis) |
| superscript | `superscript_plugin` | Inline | `superscript/` | inline.ruler |
| tasklists | `tasklists_plugin` | Core | `tasklists/` | core.ruler (after inline) |
| texmath | `texmath_plugin` | Block+Inline | `texmath/` | block.ruler + inline.ruler |
| wordcount | `wordcount_plugin` | Core | `wordcount/` | core.ruler (push) |
| substitution | - | Inline | `substitution.py` | inline.ruler |

## 共享工具

| 文件 | 函数 | 作用 |
|------|------|------|
| `utils.py` | `is_code_block(state, line)` | 检查行是否在代码块内（v2/v3兼容） |
| `utils.py` | `UNESCAPE_RE` | 反转义正则（sub/superscript使用） |
| `utils.py` | `WHITESPACE_RE` | 空白检测正则 |
