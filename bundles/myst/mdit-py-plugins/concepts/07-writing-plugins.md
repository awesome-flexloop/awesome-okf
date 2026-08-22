---
type: Concept
title: 编写自定义插件
description: 从零开始编写markdown-it-py插件的完整指南，涵盖块级/行内/核心规则、闭包工厂、Token操作、渲染规则
tags:
- mdit-py-plugins
- plugin
- custom
- development
- guide
difficulty: 高级
estimated_time: 25分钟
prerequisites:
- 01-plugin-basics
- 03-block-plugins
- 04-inline-plugins
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

# 编写自定义插件

## 最简插件

```python
from markdown_it import MarkdownIt

def hello_plugin(md: MarkdownIt) -> None:
    """将 :(hello): 替换为 <span class="emoji">👋</span>"""
    
    def hello_rule(state, silent: bool) -> bool:
        if state.src[state.pos:state.pos+9] != ":(hello):":
            return False
        if silent:
            return True
        state.pushPending()
        token = state.push("emoji_hello", "", 0)
        token.content = "👋"
        state.pos += 9
        return True
    
    def render_emoji(tokens, idx, options, env, renderer):
        return '<span class="emoji">👋</span>'
    
    md.inline.add_terminator_char(":")
    md.inline.ruler.after("text", "hello_emoji", hello_rule)
    md.add_render_rule("emoji_hello", render_emoji)

md = MarkdownIt().use(hello_plugin)
print(md.render("Hello :(hello): World"))
# <p>Hello <span class="emoji">👋</span> World</p>
```

## 块级插件模板

```python
from markdown_it import MarkdownIt
from markdown_it.rules_block import StateBlock
from mdit_py_plugins.utils import is_code_block

def my_block_plugin(md: MarkdownIt, marker: str = "!!!") -> None:
    min_markers = len(marker)
    
    def block_rule(state: StateBlock, startLine: int, endLine: int, silent: bool) -> bool:
        if is_code_block(state, startLine):
            return False
        
        start = state.bMarks[startLine] + state.tShift[startLine]
        maximum = state.eMarks[startLine]
        
        # 检查起始标记
        if state.src[start:start+min_markers] != marker:
            return False
        
        # 计算标记长度
        pos = start
        while pos < maximum and state.src[pos] == marker[0]:
            pos += 1
        marker_len = pos - start
        if marker_len < min_markers:
            return False
        
        # silent模式只验证
        if silent:
            return True
        
        # 解析参数
        params = state.src[pos:maximum].strip()
        
        # 查找结束标记
        nextLine = startLine + 1
        haveEndMarker = False
        while nextLine < endLine:
            pos_n = state.bMarks[nextLine] + state.tShift[nextLine]
            max_n = state.eMarks[nextLine]
            line = state.src[pos_n:max_n].strip()
            if line.startswith(marker) and len(line) >= marker_len:
                # 检查结束标记长度≥起始标记
                haveEndMarker = True
                break
            if state.sCount[nextLine] < state.blkIndent:
                break  # 缩进减少，终止
            nextLine += 1
        
        state.line = nextLine + (1 if haveEndMarker else 0)
        
        # 输出Token
        token = state.push("my_block_open", "div", 1)
        token.markup = marker
        token.attrSet("class", "my-block")
        token.map = [startLine, state.line]
        if params:
            token.info = params
        
        # 递归解析内容
        old_blkIndent = state.blkIndent
        state.blkIndent += 4
        state.md.block.tokenize(state, startLine + 1, nextLine)
        state.blkIndent = old_blkIndent
        
        token = state.push("my_block_close", "div", -1)
        return True
    
    md.block.ruler.before("paragraph", "my_block", block_rule,
                          {"alt": ["paragraph", "reference", "blockquote"]})
    
    # 渲染
    def render_open(tokens, idx, options, env, renderer):
        cls = tokens[idx].attrGet("class")
        return f'<div class="{cls}">'
    md.add_render_rule("my_block_open", render_open)
    md.add_render_rule("my_block_close", lambda t,i,o,e,r: "</div>\n")
```

## 行内插件模板（可配置）

```python
from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline

def make_citation_rule(allow_digits: bool = True):
    """闭包工厂：@[citekey] 引用语法"""
    def citation_rule(state: StateInline, silent: bool) -> bool:
        if state.src[state.pos:state.pos+2] != "@[":
            return False
        
        pos = state.pos + 2
        max_pos = state.posMax
        
        # 找到闭合 ]
        while pos < max_pos:
            if state.src[pos] == "]" and not _is_escaped(state, pos):
                break
            pos += 1
        else:
            return False  # 未找到闭合
        
        key = state.src[state.pos+2:pos]
        if not key:
            return False
        
        # 数字检查
        if not allow_digits and key[0].isdigit():
            return False
        
        if silent:
            return True
        
        state.pushPending()
        token = state.push("citation", "", 0)
        token.content = key
        token.meta = {"key": key}
        state.pos = pos + 1
        return True
    
    return citation_rule

def _is_escaped(state, pos):
    """检查位置是否被反斜杠转义"""
    backslashes = 0
    p = pos - 1
    while p >= 0 and state.src[p] == "\\":
        backslashes += 1
        p -= 1
    return backslashes % 2 == 1

def citation_plugin(md: MarkdownIt, allow_digits: bool = True):
    md.inline.add_terminator_char("@")
    md.inline.ruler.after("link", "citation", make_citation_rule(allow_digits))
    md.add_render_rule("citation", lambda t,i,o,e,r:
        f'<cite class="citation" data-key="{t[i].content}">@{t[i].content}</cite>')
```

## Core后处理插件模板

```python
from markdown_it import MarkdownIt
from markdown_it.rules_core import StateCore
import re

def heading_anchor_plugin(md: MarkdownIt, slug_func=None):
    """为所有heading_open添加id属性"""
    if slug_func is None:
        slug_func = lambda s: re.sub(r'[^\w\- ]', '', s.lower()).strip().replace(' ', '-')
    
    def add_anchors(state: StateCore) -> None:
        slug_count = {}
        tokens = state.tokens
        i = 0
        while i < len(tokens):
            if tokens[i].type == "heading_open":
                # 获取下一个inline token的文本
                j = i + 1
                text = ""
                while j < len(tokens) and tokens[j].type != "heading_close":
                    if tokens[j].type == "inline" and tokens[j].children:
                        for child in tokens[j].children:
                            if child.type == "text":
                                text += child.content
                    j += 1
                
                slug = slug_func(text)
                if slug in slug_count:
                    slug_count[slug] += 1
                    slug = f"{slug}-{slug_count[slug]}"
                else:
                    slug_count[slug] = 0
                
                if slug:
                    tokens[i].attrSet("id", slug)
            i += 1
    
    md.core.ruler.after("inline", "heading_anchors", add_anchors)
```

## 最佳实践

1. **始终检查is_code_block**：块级规则开头调用
2. **处理silent模式**：返回True/False，不输出Token
3. **使用闭包工厂**：传递配置参数给规则函数
4. **注册终止字符**：行内插件的起始字符需要add_terminator_char
5. **先pushPending再push**：行内规则输出Token前刷新文本缓冲区
6. **使用env传递数据**：插件间通信和输出元数据
7. **选择合适的注册位置**：before谁/after谁/push到末尾
8. **递归解析子内容**：块级插件用state.md.block.tokenize()
9. **处理转义**：检查`\`前缀
10. **添加alt列表**：告诉其他规则哪些可以终止当前块
