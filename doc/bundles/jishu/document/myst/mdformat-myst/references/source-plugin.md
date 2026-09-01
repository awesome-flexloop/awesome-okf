---
type: Reference
title: mdformat-myst 插件核心实现
description: plugin.py 实现 update_mdit 入口、RENDERERS 和 POSTPROCESSORS 映射。
tags: [source-code, myst, markdown, mdformat, plugin]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:55:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-plugin
    resource: /spec/facts.md
    title: mdformat-myst 事实清单
---

## 模块概览

`mdformat_myst/plugin.py` 是插件的核心实现文件（158行），包含：

## 公共接口

### `update_mdit(mdit: MarkdownIt) -> None`

mdformat 插件标准入口函数，负责配置 markdown-it 解析器。执行以下操作：

1. 启用 mdformat 内置扩展：tables、front_matters、footnote
2. 启用 mdit-py-plugins 扩展：myst_role_plugin、myst_block_plugin、dollarmath_plugin
3. 覆盖 fence 和 code_block 的 HTML 渲染规则

### `RENDERERS: dict[str, Callable]`

Token 类型到渲染函数的映射字典，包含 9 个渲染器。

### `POSTPROCESSORS: dict[str, Callable]`

后处理器映射，包含 paragraph 和 text 两个后处理器。

## 渲染函数清单

| 函数 | 处理 Token 类型 | 输出格式 |
|------|----------------|---------|
| `_role_renderer` | myst_role | `{name}`content`` |
| `_comment_renderer` | myst_line_comment | `%content` |
| `_blockbreak_renderer` | myst_block_break | `+++` 或 `+++ content` |
| `_target_renderer` | myst_target | `(content)=` |
| `_math_inline_renderer` | math_inline | `$content$` |
| `_math_block_renderer` | math_block | `$$content$$` |
| `_math_block_label_renderer` | math_block_label | `$$content$$ (label)` |
| `_math_block_safe_blockquote_renderer` | blockquote | 数学块安全引用 |
| `fence` | fence | 代码/指令围栏 |

## 转义后处理器

| 函数 | 处理场景 | 转义内容 |
|------|---------|---------|
| `_escape_paragraph` | 段落级别 | `+++`、`%`行首、`(target)=`模式 |
| `_escape_text` | 文本级别 | `{role}`名称、`$`符号 |

## 源码位置

- 文件路径：`mdformat_myst/plugin.py`
- 代码行数：158行

## 相关概念

- [插件架构](../concepts/01-plugin-architecture.md)
- [MyST 语法支持](../concepts/02-myst-syntax-support.md)
- [转义机制与后处理器](../concepts/04-escaping-and-postprocessors.md)
