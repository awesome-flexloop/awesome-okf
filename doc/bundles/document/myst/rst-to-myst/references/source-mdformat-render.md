---
type: Reference
title: rst-to-myst mdformat 渲染集成
description: mdformat_render.py 实现 token 到 MyST Markdown 文本的渲染和自定义渲染器。
tags: [source-code, mdformat, render, myst, markdown]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:55:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-mdformat-render
    resource: /spec/facts.md
    title: rst-to-myst 事实清单
---

## 模块概览

`rst_to_myst/mdformat_render.py` 实现 markdown-it tokens 到最终 MyST Markdown 文本的渲染（246行）。

## 自定义渲染器

### `AdditionalRenderers` 类

`RENDERERS` 字典注册四个自定义渲染器：

| Token 类型 | 渲染函数 | 输出 |
|-----------|---------|------|
| `unprocessed` | `_unprocessed_render` | 原样输出内容（不转义） |
| `front_matter_tokens` | `_front_matter_tokens_renderer` | YAML front matter（`---`包裹） |
| `substitution_block`/`substitution_inline` | `_sub_renderer` | `{{ content }}` |
| `directive` | `_directive_render` | MyST 指令围栏 |

### `_directive_render(node, context) -> str`

指令渲染核心逻辑：
1. 特殊处理：`misc.Replace` 输出最后一个子节点、`misc.Date` 输出 `{sub-ref}\`today\``
2. 从 `directive_arg` 子节点渲染参数行，压缩为单行
3. 从 `options_list` 渲染 YAML 选项块（冒号缩进格式）
4. 从 `directive_content` 子节点渲染内容
5. 选择围栏字符：markup 含 `:` 用冒号，info 含反引号/波浪线用 `~`，否则用 `` ` ``
6. 计算围栏长度（最长连续字符数+1，最小3）
7. 输出格式：`{fence_len*fence_char}{{name}}{args}\n{options}{content}{fence_len*fence_char}`

### `_front_matter_tokens_render(node, context) -> str`

递归渲染 front matter 键值对：
- 跟踪 `key_path` 构建嵌套字典
- 无子节点的值设为 `True`
- 使用 `yaml_dump` 序列化为 YAML
- 输出 `---\nYAML\n---` 格式

## 核心函数

### `from_tokens(output, *, consecutive_numbering, warning_stream) -> str`

将 MarkdownItRenderer 输出的 tokens 渲染为文本：

1. 创建 `MDRenderer` 实例
2. 配置 parser_extensions：myst、tables、frontmatter、deflist + AdditionalRenderers
3. 设置 `mdformat: {number: consecutive_numbering}` 选项
4. 调用 `md_renderer.render(tokens, options, env, finalize=False)` — 注意 `finalize=False`
5. 手动输出所有引用定义（不仅是使用过的）：设置 `used_refs = references`，调用 `_write_references`
6. 临时重定向 mdformat 日志到 warning_stream

### `rst_to_myst(text, ...) -> ConvertedOutput`

顶层转换函数：
1. 调用 `to_docutils_ast()` 将 RST 解析为 docutils AST
2. 创建 `MarkdownItRenderer` 实例并调用 `to_tokens()` 生成 tokens
3. 调用 `get_myst_extensions()` 推断所需 MyST 扩展
4. 调用 `from_tokens()` 渲染为 Markdown 文本
5. 返回 `ConvertedOutput(text, tokens, env, warning_stream, extensions)`

### `get_myst_extensions(tokens) -> set[str]`

扫描 tokens 推断所需 MyST 扩展：
- substitution_inline/block → `substitution`
- front_matter_key_open 且 key_path[0] == "substitutions" → `substitution`
- directive_open 且 markup 含 `:` → `colon_fence`
- math_inline/block/block_eqno → `dollarmath`
- dl_open → `deflist`

## 数据类

### `ConvertedOutput(NamedTuple)`

| 字段 | 类型 | 说明 |
|------|------|------|
| `text` | `str` | 输出 MyST Markdown 文本 |
| `tokens` | `list[Token]` | markdown-it token 列表 |
| `env` | `dict[str, Any]` | 渲染环境 |
| `warning_stream` | `IO` | 警告输出流 |
| `extensions` | `set[str]` | 所需 MyST 扩展集合 |

## 源码位置

- 文件路径：`rst_to_myst/mdformat_render.py`
- 代码行数：246行

## 相关概念

- [mdformat 渲染集成与自定义渲染器](../concepts/07-mdformat-integration.md)
- [指令转换机制与 directives.yml 映射](../concepts/05-directive-conversion.md)
