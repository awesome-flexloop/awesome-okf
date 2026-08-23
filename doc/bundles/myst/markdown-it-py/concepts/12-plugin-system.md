---
type: Concept
title: 插件系统
description: 插件机制极简——use(plugin_func) 就是函数调用，插件通过 Ruler 和 Renderer API 扩展解析器
tags:
- markdown-it-py
- plugin
- extension
- custom-rule
- add_render_rule
difficulty: 高级
estimated_time: 20分钟
prerequisites:
- 05-ruler
- 10-renderer
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

# 插件系统

markdown-it-py 的插件系统非常极简：`use(plugin, *params, **options)` 就是调用 `plugin(md, *params, **options)`，将 MarkdownIt 实例传给插件函数。

## use() 方法

```python
def use(self, plugin, *params, **options):
    plugin(self, *params, **options)
    return self
```

插件接收 md 实例后，可以做任何事：添加规则、添加渲染函数、修改选项等。支持链式调用：

```python
md = (MarkdownIt()
      .use(plugin1)
      .use(plugin2, {"option": "value"})
      .use(plugin3, param1, param2))
```

## 插件开发模式

### 模式1：添加块级规则

```python
def admonition_plugin(md, name="admonition"):
    """支持 !!! note "Title" 语法的告警块插件"""
    
    def admonition_rule(state, startLine, endLine, silent):
        pos = state.bMarks[startLine] + state.tShift[startLine]
        if state.src[pos:pos+3] != "!!!":
            return False
        
        if silent:
            return True
        
        # 解析类型和标题
        pos += 3
        max = state.eMarks[startLine]
        # ...解析 admonition type 和 title...
        
        # 找到结束行
        nextLine = startLine + 1
        while nextLine < endLine:
            pos_next = state.bMarks[nextLine] + state.tShift[nextLine]
            if state.src[pos_next:pos_next+3] == "!!!":
                break
            nextLine += 1
        
        # 输出 Token
        token = state.push("admonition_open", "div", 1)
        token.markup = "!!!"
        token.attrSet("class", f"admonition {adm_type}")
        token.map = [startLine, nextLine]
        
        # 内容作为 inline 处理
        token = state.push("inline", "", 0)
        token.content = state.getLines(startLine+1, nextLine, state.blkIndent, False)
        token.map = [startLine+1, nextLine]
        token.children = []
        
        state.push("admonition_close", "div", -1)
        state.line = nextLine
        return True
    
    md.block.ruler.before("paragraph", "admonition", admonition_rule,
                          {"alt": ["paragraph", "reference", "blockquote"]})
    
    # 添加渲染规则
    def render_admonition_open(tokens, idx, options, env, renderer):
        token = tokens[idx]
        cls = token.attrGet("class")
        return f'<div class="{cls}">'
    
    def render_admonition_close(tokens, idx, options, env, renderer):
        return "</div>"
    
    md.add_render_rule("admonition_open", render_admonition_open)
    md.add_render_rule("admonition_close", render_admonition_close)
```

### 模式2：添加行内规则

```python
def mention_plugin(md):
    """支持 @username 语法的提及插件"""
    
    def mention_rule(state, silent):
        if state.src[state.pos] != "@":
            return False
        
        pos = state.pos + 1
        start = pos
        while pos < state.posMax and (state.src[pos].isalnum() or state.src[pos] == "_"):
            pos += 1
        
        if pos == start:
            return False
        
        if silent:
            return True
        
        username = state.src[start:pos]
        state.pushPending()
        token = state.push("mention", "", 0)
        token.content = username
        token.meta = {"username": username}
        state.pos = pos
        return True
    
    # 添加终止字符（让解析器在@处停下）
    md.inline.add_terminator_char("@")
    md.inline.ruler.after("text", "mention", mention_rule)
    
    # 渲染
    def render_mention(tokens, idx, options, env, renderer):
        user = tokens[idx].content
        return f'<a href="/user/{user}" class="mention">@{user}</a>'
    
    md.add_render_rule("mention", render_mention)
```

### 模式3：仅自定义渲染

```python
def target_blank_plugin(md):
    """所有外链添加 target="_blank\""""
    def render_link_open(tokens, idx, options, env, renderer):
        tokens[idx].attrSet("target", "_blank")
        tokens[idx].attrSet("rel", "noopener noreferrer")
        return renderer.renderToken(tokens, idx, options)
    
    md.add_render_rule("link_open", render_link_open)
```

### 模式4：修改 Token 流（核心规则）

```python
def heading_id_plugin(md):
    """为标题添加自动id属性"""
    def heading_id_rule(state):
        for token in state.tokens:
            if token.type == "heading_open":
                # 找到下一个inline token获取标题文本
                # ...根据内容生成slug并设置id属性...
                pass
    
    md.core.ruler.push("heading_id", heading_id_rule)
```

## 可用的 md 接口

插件通过 md 实例可以访问：

| 属性/方法 | 用途 |
|-----------|------|
| `md.core.ruler` | Core 规则管理 |
| `md.block.ruler` | Block 规则管理 |
| `md.inline.ruler` | Inline 主规则管理 |
| `md.inline.ruler2` | Inline 后置规则管理 |
| `md.add_render_rule(name, fn)` | 添加/覆盖渲染规则 |
| `md.renderer.rules[name]` | 直接访问渲染规则字典 |
| `md.set(options)` | 修改选项 |
| `md.enable(name)`/`md.disable(name)` | 启用/禁用规则 |
| `md.normalizeLink(url)` | URL规范化 |
| `md.validateLink(url)` | URL安全验证 |
| `md.normalizeLinkText(text)` | 链接文本规范化 |
| `md.inline.add_terminator_char(ch)` | 添加行内终止字符 |

## 插件参数传递

```python
def my_plugin(md, prefix="", css_class="custom"):
    # prefix 和 css_class 是可配置参数
    ...

md.use(my_plugin, prefix="note-", css_class="my-note")
```

## 插件生态

配套插件包 [mdit-py-plugins](https://github.com/executablebooks/mdit-py-plugins) 提供了常用扩展：
- 脚注（footnote）
- 定义列表（deflist）
- 任务列表（tasklists）
- 缩写（abbreviation）
- 数学公式（dollarmath/amsmath）
- 容器（container）
- 表情符号（emoji）
- 插入标记（insert/mark）
- 下标/上标（sub/sup）

## 下一步

- [mdit-py-plugins 项目](https://github.com/executablebooks/mdit-py-plugins) 文档
- [简单插件示例](/examples/simple-plugin.md)
