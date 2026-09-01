---
type: Reference
title: mdformat-footnote 插件核心实现
description: plugin.py 实现 update_mdit、CLI 参数添加和脚注渲染器。
tags: [source-code, footnote, markdown, mdformat, plugin]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:55:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-plugin
    resource: /spec/facts.md
    title: mdformat-footnote 事实清单
---

## 模块概览

`mdformat_footnote/plugin.py` 是插件核心实现（94行），包含渲染器定义和插件入口。

## 公共接口

### `update_mdit(mdit: MarkdownIt) -> None`

配置 markdown-it 解析器：
1. 调用 `mdit.use(footnote_plugin)` 启用 mdit-py-plugins 的脚注插件
2. 调用 `mdit.disable("footnote_inline")` 禁用内联脚注
3. 在 `footnote_tail` 规则前插入 `reorder_footnotes` 规则，执行脚注重排序和孤立脚注处理

### `add_cli_argument_group(group: argparse._ArgumentGroup) -> None`

添加 `--keep-footnote-orphans` CLI 参数，控制是否保留未引用的脚注定义。默认行为是移除孤立脚注。

### `RENDERERS: Mapping[str, Render]`

Token 渲染器映射：

| Token 类型 | 渲染函数 | 输出格式 |
|-----------|---------|---------|
| `footnote_ref` | `_footnote_ref_renderer` | `[^label]` |
| `footnote` | `_footnote_renderer` | `[^label]:` + 缩进内容 |
| `footnote_block` | `_render_children` | 子节点双换行连接 |

## 渲染函数详解

### `_footnote_renderer(node, context) -> str`

脚注定义的渲染逻辑：
1. 首行输出 `[^label]:`，后跟首段首行（使用与label等长+1的缩进上下文）
2. 首段其余行使用4空格缩进
3. 后续子元素（非footnote_anchor）使用4空格缩进，双换行分隔
4. 首段不存在时，所有内容4空格缩进

## 源码位置

- 文件路径：`mdformat_footnote/plugin.py`
- 代码行数：94行

## 相关概念

- [脚注渲染格式与缩进规则](../concepts/02-footnote-rendering.md)
- [插件配置与 CLI 选项](../concepts/01-plugin-configuration.md)
