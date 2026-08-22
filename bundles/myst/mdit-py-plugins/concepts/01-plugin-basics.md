---
type: Concept
title: 插件基础
description: mdit-py-plugins 的工作原理——use()加载、三种规则类型、闭包工厂模式、env数据通道
tags:
- mdit-py-plugins
- plugin
- basics
- ruler
- closure
- env
difficulty: 入门
estimated_time: 20分钟
prerequisites:
- 00-introduction
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: mdit-py-plugins-source
  resource: /references/plugin-source-mapping.md
  title: mdit-py-plugins 源码路径映射
---

# 插件基础

## 插件就是函数

mdit-py-plugins 的核心设计极其简单：**插件就是一个接收 MarkdownIt 实例的函数**。

```python
def my_plugin(md: MarkdownIt) -> None:
    """我的插件：添加一条行内规则和一个渲染规则"""
    md.inline.ruler.after("text", "my_rule", my_rule_fn)
    md.add_render_rule("my_token", render_my_token)

md = MarkdownIt().use(my_plugin)
```

`md.use(plugin_func, *args, **kwargs)` 本质就是调用 `plugin_func(md, *args, **kwargs)`，没有额外抽象层。

## 三种规则注册位置

插件根据功能需要，在三条规则链的 Ruler 上注册规则：

### 1. Block 规则（块级语法）

操作 StateBlock，按行解析：

```python
md.block.ruler.before("fence", "my_block", my_block_rule, {"alt": ["paragraph"]})
# 或
md.block.ruler.after("paragraph", "my_block", my_block_rule)
# 或
md.block.ruler.push("my_block", my_block_rule)
```

Block 规则签名：`(state: StateBlock, startLine: int, endLine: int, silent: bool) -> bool`

适用场景：围栏替代（colon_fence）、容器（container）、定义列表（deflist）、YAML前置（front_matter）、数学块（amsmath/dollarmath block）

### 2. Inline 规则（行内语法）

操作 StateInline，按字符解析：

```python
md.inline.ruler.before("escape", "math_inline", math_rule)
md.inline.ruler.after("emphasis", "sub", sub_rule)
```

Inline 规则签名：`(state: StateInline, silent: bool) -> bool`

适用场景：数学公式（dollarmath inline）、下标/上标（sub/superscript）、角色（myst_role）

### 3. Core 规则（后处理）

操作 StateCore，处理完整 Token 流：

```python
md.core.ruler.after("inline", "footnote_tail", tail_fn)
md.core.ruler.push("wordcount", wc_fn)
```

Core 规则签名：`(state: StateCore) -> None`

适用场景：脚注收集（footnote_tail）、任务列表（tasklists）、字数统计（wordcount）

### 注册位置选择原则

| before/after谁？ | 原因 |
|-----------------|------|
| block规则 before "fence" | 替代围栏语法先于fence匹配 |
| block规则 before "paragraph" | 新块语法先于段落兜底 |
| inline规则 before "escape" | 特殊标记先于转义处理（如$数学） |
| inline规则 after "emphasis" | 新标记在强调之后处理 |
| core规则 after "inline" | 行内解析完成后做后处理 |

## 闭包工厂模式

规则函数的签名是固定的，无法直接传参。可配置插件使用**闭包工厂模式**：外层函数接收配置，返回一个闭包作为规则函数。

```python
def make_inline_rule(allow_space: bool = True):
    """工厂函数：接收配置，返回规则函数"""
    def _inline_rule(state: StateInline, silent: bool) -> bool:
        # 闭包访问 allow_space
        if not allow_space and isWhiteSpace(ord(state.src[state.pos + 1])):
            return False
        # ...解析逻辑...
        return True
    return _inline_rule

# 插件使用工厂
def my_plugin(md: MarkdownIt, allow_space: bool = True):
    md.inline.ruler.before(
        "escape", "my_rule",
        make_inline_rule(allow_space)  # 传入配置，返回闭包
    )
```

dollarmath、footnote、container、tasklists、wordcount 等所有可配置插件都使用这个模式。

## 添加终止字符

行内插件需要解析特殊起始字符时，必须通过 `add_terminator_char()` 注册，否则解析器不会在该字符处停下：

```python
def my_plugin(md):
    md.inline.add_terminator_char("@")  # 让解析器在@处停下
    md.inline.ruler.after("text", "mention", mention_rule)
```

## 渲染规则注册

通过 `add_render_rule(name, function)` 为新 Token 类型添加渲染：

```python
def render_my_token(tokens, idx, options, env, renderer):
    token = tokens[idx]
    return f'<span class="my">{token.content}</span>'

md.add_render_rule("my_token", render_my_token)
```

也可以覆盖已有 Token 类型的渲染（如自定义link_open）。

## env 数据通道

`env` 字典是插件间通信和数据收集的通道：

```python
def my_plugin(md):
    def my_core_rule(state):
        # 从env读取数据
        data = state.env.get("my_plugin_data", {})
        # 向env写入数据
        state.env["my_plugin_data"] = {"count": 42}
    
    md.core.ruler.push("my_rule", my_core_rule)

# 使用时
env = {}
html = md.render(text, env)
print(env["my_plugin_data"])  # {"count": 42}
```

约定：使用插件名作为env键名前缀（如"footnotes"、"wordcount"），避免冲突。

footnote 用 `env["footnotes"]["refs"]` 和 `env["footnotes"]["list"]`，wordcount 用 `env["wordcount"]["words"]`。

## 代码块保护

所有块级插件在规则开头都调用 `is_code_block(state, startLine)` 检查，避免在代码块内触发：

```python
from mdit_py_plugins.utils import is_code_block

def my_block_rule(state, startLine, endLine, silent):
    if is_code_block(state, startLine):
        return False
    # ...解析逻辑...
```

这确保了围栏代码块和缩进代码块内的特殊标记不会被误解析。

## 多文件插件结构

复杂插件采用目录结构：

```
my_plugin/
├── __init__.py   # from .index import my_plugin; __all__ = ("my_plugin",)
└── index.py      # 完整实现
```

简单插件可用单文件（如 colon_fence.py）。

## 下一步

- [使用插件](02-using-plugins.md) — 常用插件快速上手
- [块级插件详解](03-block-plugins.md)
- [编写插件](07-writing-plugins.md)
