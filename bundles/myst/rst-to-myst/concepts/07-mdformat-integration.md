---
type: Concept
title: mdformat 渲染集成与自定义渲染器
description: rst-to-myst 如何使用 mdformat 引擎渲染 tokens 以及自定义渲染器的实现。
tags: [mdformat, rendering, custom-renderer, extensions, references]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:57:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: src-mdformat-render
    resource: /references/source-mdformat-render.md
    title: rst-to-myst mdformat 渲染集成
---

## 为什么使用 mdformat

markdown-it-py 本身可以将 token 流渲染为 HTML，但 rst-to-myst 需要输出的是 Markdown 文本而非 HTML。mdformat 提供了一个 Markdown 渲染器（MDRenderer），可以将 markdown-it token 流重新渲染为格式化的 Markdown 文本。mdformat-myst 插件确保 MyST 特有语法被正确渲染。

## from_tokens 函数

`from_tokens()` 函数是 token→Markdown 文本的渲染入口：

```python
def from_tokens(output, *, consecutive_numbering=True, warning_stream=None):
    md_renderer = MDRenderer()
    options = {
        "parser_extension": [
            PARSER_EXTENSIONS[name]
            for name in ["myst", "tables", "frontmatter", "deflist"]
        ] + [AdditionalRenderers],
        "mdformat": {"number": consecutive_numbering},
    }
    # ...渲染逻辑...
    return text
```

### 加载的 mdformat 扩展

| 扩展名 | 功能 |
|--------|------|
| `myst` | MyST 语法渲染（角色、指令、注释、目标、数学等） |
| `tables` | 表格语法渲染 |
| `frontmatter` | YAML front matter 渲染 |
| `deflist` | 定义列表（definition list）渲染 |
| `AdditionalRenderers` | rst-to-myst 自定义渲染器 |

### finalize=False 的关键设置

mdformat 默认在 `finalize=True` 时只输出被引用过的引用定义（reference definitions）。但在 RST→MyST 转换中，我们希望保留所有解析出的引用定义（因为 RST 中可能定义了未在当前片段引用的链接目标），因此设置 `finalize=False` 后手动设置 `used_refs` 为所有 references，再调用 `_write_references` 输出全部引用。

```python
text = md_renderer.render(tokens, options, env, finalize=False)
if env["references"]:
    if text:
        text += "\n\n"
    env["used_refs"] = set(env["references"])
    text += md_renderer._write_references(env)
```

## AdditionalRenderers 自定义渲染器

`AdditionalRenderers` 类注册了四个 mdformat 标准不支持的 token 类型的渲染器。

### unprocessed - 未处理文本

```python
def _unprocessed_render(node, context):
    return node.content
```

原样返回内容，不进行任何转义处理。用于需要逐字输出的文本节点（UnprocessedText 类型）。

### front_matter_tokens - YAML Front Matter

```python
def _front_matter_tokens_render(node, context):
    # 递归构建嵌套字典
    # YAML 序列化
    return f"---\n{yaml_text}\n---"
```

将 front_matter_tokens 递归构建为嵌套字典结构，然后使用自定义 YamlDumper 序列化为 YAML 文本，包裹在 `---` 之间。无子节点的值设为 `True`（YAML 布尔值）。

### substitution - 替换

```python
def _sub_renderer(node, context):
    return f"{{{{ {node.content} }}}}"
```

输出 MyST 替换语法 `{{ content }}`。同时处理 substitution_block 和 substitution_inline 两种 token 类型。

### directive - 指令

```python
def _directive_render(node, context):
    # 处理特殊指令（Replace、Date）
    # 渲染参数行、选项块、内容
    # 选择围栏字符和长度
    return f"{fence_str}{{{name}}}{info_str}\n{option_block}{code_block}{fence_str}"
```

这是最复杂的自定义渲染器，处理 MyST 指令的输出。详见[指令转换机制](/concepts/05-directive-conversion.md)。

## MyST 扩展推断

`get_myst_extensions(tokens)` 函数扫描 token 流，根据出现的特殊 token 类型推断需要哪些 MyST 扩展：

| Token 类型 | 所需扩展 |
|-----------|---------|
| `substitution_inline`/`substitution_block` | `substitution` |
| `front_matter_key_open` 且 key_path 以 "substitutions" 开头 | `substitution` |
| `directive_open` 且 markup 含 `:` | `colon_fence` |
| `math_inline`/`math_block`/`math_block_eqno` | `dollarmath` |
| `dl_open`（定义列表） | `deflist` |

这个推断结果通过 `ConvertedOutput.extensions` 返回给用户，提示需要在 MyST 配置中启用哪些扩展。

## 日志重定向

mdformat 有自己的 LOGGER，`from_tokens` 函数临时将其重定向到 warning_stream：

```python
warning_handler = logging.StreamHandler(warning_stream)
warning_handler.setLevel(logging.WARNING)
LOGGER.addHandler(warning_handler)
try:
    # ...渲染...
finally:
    LOGGER.removeHandler(warning_handler)
```

这确保 mdformat 的格式化警告也能被用户看到。

## 输出文本后处理

渲染完成后，如果文本非空，追加一个末尾换行符：
```python
if text:
    text += "\n"
```

这是 POSIX 文本文件的标准约定（末尾换行）。

## 相关概念

- [三阶段转换流水线架构](/concepts/03-conversion-pipeline.md)
- [MarkdownItRenderer 与 AST→Token 遍历](/concepts/06-token-rendering.md)
- [指令转换机制与 directives.yml 映射](/concepts/05-directive-conversion.md)
