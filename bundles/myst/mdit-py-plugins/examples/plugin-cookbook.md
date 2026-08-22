---
type: Example
title: 插件配方集
description: 常见插件开发模式的可复用代码片段
tags:
- mdit-py-plugins
- example
- cookbook
- snippets
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

# 插件配方集

## 块级插件：检查起始标记

```python
start = state.bMarks[startLine] + state.tShift[startLine]
maximum = state.eMarks[startLine]
if state.src[start:start+3] != "!!!":
    return False
```

## 块级插件：跳过空行找结束

```python
nextLine = startLine + 1
while nextLine < endLine:
    if state.sCount[nextLine] < state.blkIndent and state.src[state.bMarks[nextLine]:state.eMarks[nextLine]].strip():
        break
    nextLine += 1
```

## 行内插件：检查转义

```python
def is_escaped(state, pos):
    backslashes = 0
    p = pos - 1
    while p >= 0 and state.src[p] == "\\":
        backslashes += 1; p -= 1
    return backslashes % 2 == 1
```

## 行内插件：添加终止字符

```python
md.inline.add_terminator_char("=")  # 在插件注册前添加
md.inline.ruler.after("emphasis", "my_rule", my_rule_fn)
```

## Core插件：遍历所有text Token统计词数

```python
def count_words(state):
    words = 0
    for tok in state.tokens:
        if tok.type == "text":
            words += len(tok.content.split())
        if tok.children:
            for child in tok.children:
                if child.type == "text":
                    words += len(child.content.split())
    state.env["wordcount"] = words
```

## 输出Token：开-内容-闭模式

```python
# 块级
token = state.push("my_open", "div", 1)
token.attrSet("class", "my-class")
token.map = [startLine, nextLine]
# ...递归解析或inline占位...
token = state.push("inline", "", 0)
token.content = content
token.children = []
state.push("my_close", "div", -1)

# 行内
state.pushPending()
state.push("my_open", "span", 1)
t = state.push("text", "", 0)
t.content = content
state.push("my_close", "span", -1)
```

## 递归解析块内容

```python
old_indent = state.blkIndent
state.blkIndent += 4
state.parentType = "my_type"
state.md.block.tokenize(state, startLine + 1, nextLine)
state.blkIndent = old_indent
```

## 自定义渲染：修改已有Token渲染

```python
def render_link_open(tokens, idx, options, env, renderer):
    tokens[idx].attrSet("target", "_blank")
    tokens[idx].attrSet("rel", "noopener")
    return renderer.renderToken(tokens, idx, options)

md.add_render_rule("link_open", render_link_open)
```

## 渲染规则签名

```python
def render_fn(self_renderer, tokens, idx, options, env):
    token = tokens[idx]
    # 自闭合Token
    return f'<tag class="{token.attrGet("class", "")}">{token.content}</tag>'
    # 开标签
    # return f'<tag>'
    # 闭标签
    # return '</tag>'
```

## 闭包工厂传参

```python
def make_rule(config_value):
    def rule(state, silent):
        # 闭包访问 config_value
        if not config_value:
            return False
        # ...
        return True
    return rule

def my_plugin(md, option=True):
    md.inline.ruler.after("text", "my_rule", make_rule(option))
```

## env存储数据

```python
# 在规则中
data = state.env.setdefault("my_plugin", {})
data["key"] = value

# 在渲染后
env = {}
md.render(text, env)
result = env["my_plugin"]
```
