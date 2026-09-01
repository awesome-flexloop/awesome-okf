---
type: Example
title: 基础解析示例
description: MarkdownIt 实例化、解析为HTML、Token 检查、env 元数据、parseInline
tags:
- markdown-it-py
- example
- parse
- render
- tokens
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: markdown-it-py-source
  resource: /references/markdown-it-py-source.md
  title: markdown-it-py 源码路径映射
---

# 基础解析示例

## 最简渲染

```python
from markdown_it import MarkdownIt

md = MarkdownIt()  # 默认 commonmark 预设
html = md.render("# Hello\n\nThis is **bold** text.")
print(html)
```

输出：
```html
<h1>Hello</h1>
<p>This is <strong>bold</strong> text.</p>
```

## GFM 风格渲染

```python
md = MarkdownIt("gfm-like")
html = md.render("""
# GFM Example

| Name | Value |
|------|-------|
| A    | 1     |
| B    | 2     |

~~strikethrough~~ and https://example.com
""")
```

## 解析为 Token 列表并检查

```python
from markdown_it import MarkdownIt

md = MarkdownIt()
tokens = md.parse("## Hello **world**")

for i, tok in enumerate(tokens):
    attrs_str = f" attrs={dict(tok.attrs)}" if tok.attrs else ""
    children_str = f" children={len(tok.children)}" if tok.children else ""
    print(f"[{i:2d}] {tok.type:20s} tag={tok.tag:6s} "
          f"nest={tok.nesting} lvl={tok.level}{attrs_str}{children_str}")
```

输出：
```
[ 0] heading_open         tag=h2     nest=1 lvl=0
[ 1] inline               tag=       nest=0 lvl=1 children=3
[ 2] heading_close        tag=h2     nest=-1 lvl=0
```

检查 inline children：
```python
inline_token = tokens[1]
for child in inline_token.children:
    print(f"  {child.type:20s} content={child.content!r}")
#   text                 content='Hello '
#   strong_open          content=''
#   text                 content='world'
#   strong_close         content=''
```

## 使用 env 收集元数据

```python
md = MarkdownIt()
env = {}
md.render("""
[Google][g]
[Python][py]

[g]: https://google.com "Google"
[py]: https://python.org "Python"
""", env)

# 链接引用
print("References:", env.get("references", {}).keys())
# References: dict_keys(['g', 'py'])
```

## parseInline——仅行内解析

```python
md = MarkdownIt()
tokens = md.parseInline("Hello **world** *em*")
# tokens 是一个只有1个inline Token的列表
inline = tokens[0]
for child in inline.children:
    print(f"{child.type:20s} tag={child.tag:4s} nest={child.nesting} content={child.content!r}")
```

## renderInline——行内容器HTML

```python
html = md.renderInline("Hello **world**")
print(html)  # Hello <strong>world</strong>
# 注意：没有 <p> 包装
```

## 启用/禁用规则

```python
md = MarkdownIt("commonmark")
md.disable("emphasis")
print(md.render("**not bold**"))  # <p>**not bold**</p>

md.enable("table")  # 启用表格（commonmark默认禁用）
```

## 选项设置

```python
md = MarkdownIt("commonmark", {
    "html": False,       # 禁用HTML
    "breaks": True,      # 换行转<br>
    "linkify": True,     # 自动链接
    "typographer": True, # 排版增强
})
print(md.render("Hello\nWorld"))  # <p>Hello<br>World</p>
```
