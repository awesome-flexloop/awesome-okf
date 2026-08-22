---
type: Example
title: 编写插件
description: "开发简单的行内规则插件（@提及）和块级规则插件（!!!告警块）"
tags:
- markdown-it-py
- example
- plugin
- ruler
- block-rule
- inline-rule
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: markdown-it-py-source
  resource: /references/markdown-it-py-source.md
  title: markdown-it-py 源码路径映射
---

# 编写插件

## 行内插件：@提及

支持 `@username` 语法，渲染为用户链接。

```python
from markdown_it import MarkdownIt
from markdown_it.rules_inline.state_inline import StateInline
from markdown_it.renderer import RendererHTML

def mention_inline(state: StateInline, silent: bool) -> bool:
    """匹配 @username"""
    if state.src[state.pos] != "@":
        return False
    
    pos = state.pos + 1
    start = pos
    max_pos = state.posMax
    
    # 用户名：字母、数字、下划线
    while pos < max_pos:
        ch = state.src[pos]
        if ch.isalnum() or ch == "_":
            pos += 1
        else:
            break
    
    if pos == start:
        return False  # 只有@没有用户名
    
    if silent:
        return True
    
    username = state.src[start:pos]
    
    # flush 累积的文本
    state.pushPending()
    
    # 输出 mention token
    token = state.push("mention", "", 0)
    token.content = username
    token.meta["username"] = username
    
    state.pos = pos
    return True

def render_mention(tokens, idx, options, env, renderer: RendererHTML):
    username = tokens[idx].content
    return (f'<a href="/users/{username}" '
            f'class="mention" '
            f'data-user="{username}">@{username}</a>')

def mention_plugin(md: MarkdownIt):
    md.inline.add_terminator_char("@")  # 让解析器在@处停下
    md.inline.ruler.after("text", "mention", mention_inline)
    md.add_render_rule("mention", render_mention)

# 使用
md = MarkdownIt().use(mention_plugin)
html = md.render("Hello @world and @john_doe!")
print(html)
# <p>Hello <a href="/users/world" class="mention" data-user="world">@world</a>
#  and <a href="/users/john_doe" class="mention" data-user="john_doe">@john_doe</a>!</p>
```

## 块级插件：!!! 告警块

支持 `!!! note "Title"` 语法。

```python
import re
from markdown_it import MarkdownIt
from markdown_it.rules_block.state_block import StateBlock

ADMONITION_START = re.compile(r'^!!!\s+(\w+)(?:\s+"([^"]*)")?\s*$')

def admonition_block(state: StateBlock, startLine: int, endLine: int, silent: bool) -> bool:
    start = state.bMarks[startLine] + state.tShift[startLine]
    line_text = state.src[start:state.eMarks[startLine]]
    
    m = ADMONITION_START.match(line_text)
    if not m:
        return False
    
    if silent:
        return True
    
    adm_type = m.group(1)
    adm_title = m.group(2) or adm_type.title()
    
    # 找到结束行（非缩进行或新的!!!块）
    nextLine = startLine + 1
    while nextLine < endLine:
        pos_next = state.bMarks[nextLine] + state.tShift[nextLine]
        line_next = state.src[pos_next:state.eMarks[nextLine]]
        if line_next.startswith("!!!") or (
            state.sCount[nextLine] - state.blkIndent < 4 and line_next.strip()
        ):
            # 检查是否是新的同级别块
            if not line_next.startswith("    "):
                break
        nextLine += 1
    
    # 输出 open token
    token = state.push("admonition_open", "div", 1)
    token.markup = "!!!"
    token.attrSet("class", f"admonition admonition-{adm_type}")
    token.info = adm_type
    token.map = [startLine, nextLine]
    
    # 标题
    title_token = state.push("admonition_title", "p", 1)
    title_token.attrSet("class", "admonition-title")
    title_token.map = [startLine, startLine + 1]
    
    title_inline = state.push("inline", "", 0)
    title_inline.content = adm_title
    title_inline.map = [startLine, startLine + 1]
    title_inline.children = []
    
    state.push("admonition_title", "p", -1)
    
    # 内容
    content_start = startLine + 1
    content_end = nextLine
    old_blkIndent = state.blkIndent
    state.blkIndent += 4
    state.md.block.tokenize(state, content_start, content_end)
    state.blkIndent = old_blkIndent
    
    # 输出 close token
    state.push("admonition_close", "div", -1)
    
    state.line = nextLine
    return True

def render_admonition_open(tokens, idx, options, env, renderer):
    return f'<div class="{tokens[idx].attrGet("class")}">'

def render_admonition_title_open(tokens, idx, options, env, renderer):
    cls = tokens[idx].attrGet("class")
    return f'<p class="{cls}">'

def admonition_plugin(md: MarkdownIt):
    md.block.ruler.before("paragraph", "admonition", admonition_block,
                          {"alt": ["paragraph", "reference", "blockquote"]})
    md.add_render_rule("admonition_open", render_admonition_open)
    md.add_render_rule("admonition_close", 
                       lambda t,i,o,e,r: "</div>")
    md.add_render_rule("admonition_title", render_admonition_title_open)

# 使用
md = MarkdownIt().use(admonition_plugin)
html = md.render('''
!!! note "Note Title"
    This is a note with **bold** text.
    
    Multiple paragraphs supported.

!!! warning "Warning!"
    Be careful!
''')
```

## 核心规则插件：自动ID

在 Core 链添加后处理规则。

```python
def heading_ids(state):
    """为所有heading_open添加id属性"""
    slug_count = {}
    for i, token in enumerate(state.tokens):
        if token.type == "heading_open" and not token.attrGet("id"):
            # 获取标题文本
            text = ""
            j = i + 1
            while j < len(state.tokens) and state.tokens[j].type != "heading_close":
                if state.tokens[j].type == "inline" and state.tokens[j].children:
                    for child in state.tokens[j].children:
                        if child.type == "text":
                            text += child.content
                j += 1
            
            slug = text.lower().strip().replace(" ", "-")
            slug = "".join(c for c in slug if c.isalnum() or c in "-_")
            if slug in slug_count:
                slug_count[slug] += 1
                slug = f"{slug}-{slug_count[slug]}"
            else:
                slug_count[slug] = 0
            if slug:
                token.attrSet("id", slug)

md = MarkdownIt()
md.core.ruler.push("heading_ids", heading_ids)
```

## 插件带参数

```python
def my_plugin(md, prefix="", css_class="custom"):
    """可配置参数的插件"""
    def render_custom(tokens, idx, options, env, renderer):
        content = tokens[idx].content
        return f'<span class="{css_class}" data-prefix="{prefix}">{content}</span>'
    
    # ...添加规则...
    md.add_render_rule("custom_token", render_custom)

md = MarkdownIt().use(my_plugin, prefix="note-", css_class="note")
```
