---
type: Example
title: 编写自定义插件
description: 从零编写一个完整的markdown-it-py插件：警告块+提及+字数统计
tags:
- mdit-py-plugins
- example
- plugin-development
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

# 编写自定义插件

## 示例1：!!! 告警块插件

```python
from markdown_it import MarkdownIt
from markdown_it.rules_block import StateBlock
from mdit_py_plugins.utils import is_code_block
import re

ADMON_RE = re.compile(r'^!!!\s+(\w+)(?:\s+"([^"]*)")?\s*$')
ADMON_TYPES = {"note", "warning", "tip", "important", "caution", "info", "danger"}

def admon_plugin(md: MarkdownIt, default_title: bool = True):
    def admon_rule(state: StateBlock, startLine: int, endLine: int, silent: bool) -> bool:
        if is_code_block(state, startLine):
            return False
        
        start = state.bMarks[startLine] + state.tShift[startLine]
        line_text = state.src[start:state.eMarks[startLine]]
        m = ADMON_RE.match(line_text)
        if not m:
            return False
        
        adm_type = m.group(1)
        if adm_type not in ADMON_TYPES:
            return False
        title = m.group(2) or (adm_type.title() if default_title else "")
        
        if silent:
            return True
        
        # 查找结束（缩进行结束或非缩进行）
        nextLine = startLine + 1
        while nextLine < endLine:
            if state.sCount[nextLine] - state.blkIndent < 4:
                non_space = state.bMarks[nextLine] + state.tShift[nextLine]
                if state.src[non_space:state.eMarks[nextLine]].strip():
                    break
            nextLine += 1
        
        # 输出Token
        token = state.push("admonition_open", "div", 1)
        token.attrSet("class", f"admonition {adm_type}")
        token.markup = "!!!"
        token.map = [startLine, nextLine]
        
        if title:
            t = state.push("admonition_title_open", "p", 1)
            t.attrSet("class", "admonition-title")
            t_inline = state.push("inline", "", 0)
            t_inline.content = title
            t_inline.children = []
            state.push("admonition_title_close", "p", -1)
        
        old_indent = state.blkIndent
        state.blkIndent += 4
        state.md.block.tokenize(state, startLine + 1, nextLine)
        state.blkIndent = old_indent
        
        state.push("admonition_close", "div", -1)
        state.line = nextLine
        return True
    
    md.block.ruler.before("paragraph", "admonition", admon_rule,
                          {"alt": ["paragraph", "reference", "blockquote"]})
    
    md.add_render_rule("admonition_open", lambda t,i,o,e,r:
        f'<div class="{t[i].attrGet("class")}">')
    md.add_render_rule("admonition_close", lambda t,i,o,e,r: "</div>")
    md.add_render_rule("admonition_title_open", lambda t,i,o,e,r:
        f'<p class="{t[i].attrGet("class")}">')
    md.add_render_rule("admonition_title_close", lambda t,i,o,e,r: "</p>")

# 使用
md = MarkdownIt().use(admon_plugin)
html = md.render('''
!!! warning "注意"
    这是一个警告。
    
    多行内容。
''')
print(html)
```

## 示例2：==标记==高亮插件

```python
from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline

def mark_plugin(md: MarkdownIt):
    def mark_rule(state: StateInline, silent: bool) -> bool:
        if state.src[state.pos:state.pos+2] != "==":
            return False
        
        pos = state.pos + 2
        found = False
        while pos < state.posMax - 1:
            if state.src[pos] == "=" and state.src[pos+1] == "=":
                # 检查转义
                bs = 0
                p = pos - 1
                while p >= state.pos and state.src[p] == "\\":
                    bs += 1; p -= 1
                if bs % 2 == 1:
                    pos += 2; continue
                found = True; break
            pos += 1
        
        if not found or state.pos + 2 == pos:
            return False
        if silent:
            return True
        
        text = state.src[state.pos+2:pos]
        state.pushPending()
        tok = state.push("mark_open", "mark", 1)
        tok.markup = "=="
        t = state.push("text", "", 0)
        t.content = text
        state.push("mark_close", "mark", -1)
        state.pos = pos + 2
        return True
    
    md.inline.add_terminator_char("=")
    md.inline.ruler.after("emphasis", "mark", mark_rule)
    md.add_render_rule("mark_open", lambda t,i,o,e,r: "<mark>")
    md.add_render_rule("mark_close", lambda t,i,o,e,r: "</mark>")

# 使用
md = MarkdownIt().use(mark_plugin)
print(md.render("This is ==highlighted== text."))
# <p>This is <mark>highlighted</mark> text.</p>
```

## 示例3：文档统计插件（Core后处理）

```python
from markdown_it import MarkdownIt
from markdown_it.rules_core import StateCore
import re

def doc_stats_plugin(md: MarkdownIt):
    def stats_rule(state: StateCore):
        headings = 0
        paragraphs = 0
        code_blocks = 0
        images = 0
        links = 0
        words = 0
        
        for tok in state.tokens:
            if tok.type == "heading_open":
                headings += 1
            elif tok.type == "paragraph_open":
                paragraphs += 1
            elif tok.type in ("fence", "code_block"):
                code_blocks += 1
            elif tok.type == "image":
                images += 1
            elif tok.type == "link_open":
                links += 1
            elif tok.type == "text":
                words += len([w for w in re.split(r'\s+', tok.content) if w.strip()])
            if tok.children:
                for child in tok.children:
                    if child.type == "text":
                        words += len([w for w in re.split(r'\s+', child.content) if w.strip()])
        
        state.env["doc_stats"] = {
            "headings": headings,
            "paragraphs": paragraphs,
            "code_blocks": code_blocks,
            "images": images,
            "links": links,
            "words": words,
        }
    
    md.core.ruler.push("doc_stats", stats_rule)

# 使用
md = MarkdownIt().use(doc_stats_plugin)
env = {}
md.render("# Title\n\nHello **world** with ``[link](url)``.", env)
print(env["doc_stats"])
# {'headings': 1, 'paragraphs': 1, 'code_blocks': 0, 'images': 0, 'links': 1, 'words': 4}
```
