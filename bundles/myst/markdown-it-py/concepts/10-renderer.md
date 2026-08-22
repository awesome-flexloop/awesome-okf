---
type: Concept
title: 渲染器详解
description: RendererHTML 将 Token 流渲染为 HTML，支持自定义渲染规则覆盖默认行为
tags:
- markdown-it-py
- renderer
- html
- renderToken
- custom-rule
difficulty: 核心
estimated_time: 20分钟
prerequisites:
- 03-token-stream
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

# 渲染器详解

RendererHTML 负责将 Token 流转换为 HTML 字符串。它基于 Token 类型查找渲染规则，规则函数输出 HTML 片段，最终拼接为完整文档。

## render() 方法

```python
def render(self, tokens, options, env):
    result = ""
    for i, token in enumerate(tokens):
        if token.type in self.rules:
            result += self.rules``[token.type](tokens, i, options, env, self)``
        else:
            result += self.renderToken(tokens, i, options)
    return result
```

逻辑非常简单：
1. 遍历 tokens 列表
2. 如果 token.type 在 `self.rules` 字典中有对应的渲染函数，调用该函数
3. 否则调用默认的 `renderToken()`
4. 拼接所有输出

## renderToken()——默认渲染

renderToken 处理开标签、闭标签和自闭合标签的默认 HTML 输出：

**开标签（nesting=1）**：输出 `<tag attr1="val1" attr2="val2">`
- 遍历 token.attrs 输出属性
- 自闭合标记（如 `<br/>` vs `<br>`）根据 xhtmlOut 选项决定

**闭标签（nesting=-1）**：输出 `</tag>`

**自闭合（nesting=0）**：输出 `<tag attr1="val1" />` 或 `<tag attr1="val1">`
- 如果 token 有 content，输出在开标签和闭标签之间：`<tag>content</tag>`

## renderInline()——行内容器渲染

对于 `inline` 类型的 Token，Renderer 递归渲染其 children：

```python
def renderInline(self, tokens, idx, options, env):
    return self.render(tokens[idx].children, options, env)
```

## renderInlineAsText()——纯文本输出

递归提取所有 Token 的文本内容（忽略标签），用于生成 alt 文本等场景：

```python
def renderInlineAsText(self, tokens):
    result = ""
    for token in tokens:
        if token.type == "text":
            result += token.content
        elif token.children:
            result += self.renderInlineAsText(token.children)
    return result
```

image 渲染规则使用它来生成 alt 属性文本。

## 内置渲染规则

Renderer.rules 字典预注册了以下特殊渲染规则（不需要默认renderToken处理的）：

| 规则名 | 输出 |
|--------|------|
| `code_block` | `<pre><code class="...">` 包裹的代码，支持 highlight 选项 |
| `fence` | 围栏代码块渲染，支持语言class和highlight |
| `image` | `<img src="..." alt="..." title="..." />`（自闭合） |
| `hardbreak` | `<br>` 或 `<br/>`（取决于 xhtmlOut） |
| `softbreak` | `"\n"` 或 `"<br>"`（取决于 breaks 选项） |
| `text` | HTML 转义后的文本内容 |
| `html_block` | 原始 HTML（不转义） |
| `html_inline` | 原始 HTML（不转义） |
| `inline` | 递归渲染 children |

其他所有 Token 类型使用默认 renderToken() 渲染。

## 代码高亮

`fence` 和 `code_block` 渲染规则检查 `options["highlight"]` 函数：

```python
highlight_fn = options.get("highlight")
if highlight_fn:
    highlighted = highlight_fn(token.content, token.info, token.attrs)
    if highlighted.startswith("<pre"):
        return highlighted
    return f"<pre><code>{highlighted}</code></pre>"
```

highlight 函数签名：`(content, lang, attrs) -> str`
- 返回完整 HTML（以 `<pre` 开头）：直接使用
- 返回代码片段：包装在 `<pre><code>` 中
- 返回空字符串：使用默认转义渲染

## 自定义渲染规则

通过 `add_render_rule(name, function, fmt="html")` 添加或覆盖渲染规则：

```python
from markdown_it import MarkdownIt

def render_heading_open(tokens, idx, options, env, renderer):
    token = tokens[idx]
    level = token.tag[1]  # "h1" → "1"
    slug = f"section-{idx}"
    return f'<h{level} id="{slug}">'

md = MarkdownIt()
md.add_render_rule("heading_open", render_heading_open)
```

渲染函数的签名是 `(tokens, idx, options, env, renderer) -> str`：
- `tokens`：当前 Token 列表
- `idx`：当前 Token 的索引
- `options`：解析器选项字典
- `env`：环境对象
- `renderer`：Renderer 实例（可调用其他渲染方法）

### 常见自定义渲染示例

**添加链接的 target="_blank"**：
```python
def render_link_open(tokens, idx, options, env, renderer):
    tokens[idx].attrSet("target", "_blank")
    tokens[idx].attrSet("rel", "noopener")
    return renderer.renderToken(tokens, idx, options)

md.add_render_rule("link_open", render_link_open)
```

**自定义代码块（复制按钮等）**：
```python
def render_fence(tokens, idx, options, env, renderer):
    token = tokens[idx]
    lang = token.info.strip() or "text"
    code = escapeHtml(token.content)
    return (f'<div class="code-block" data-lang="{lang}">'
            f'<button class="copy-btn">Copy</button>'
            f'<pre><code class="language-{lang}">{code}</code></pre>'
            f'</div>')
```

**修改图片渲染（懒加载）**：
```python
def render_image(tokens, idx, options, env, renderer):
    token = tokens[idx]
    token.attrSet("loading", "lazy")
    return renderer.renderToken(tokens, idx, options)
```

## 属性渲染细节

renderToken 输出属性时，将 attrs 字典中的值进行 HTML 转义：
- `"` → `&quot;`
- `&` → `&amp;`
- `<` → `&lt;`
- `>` → `&gt;`

class 属性可以通过 `attrJoin()` 多次追加，自动用空格拼接。

## 自定义 Renderer 类

MarkdownIt 构造函数接受 `renderer_cls` 参数，可以传入自定义渲染器类：

```python
from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML

class MyRenderer(RendererHTML):
    def __init__(self, parser=None):
        super().__init__(parser)
        # 自定义规则
        self.rules["paragraph_open"] = self._paragraph_open
    
    def _paragraph_open(self, tokens, idx, options, env):
        return '<p class="my-para">'

md = MarkdownIt(renderer_cls=MyRenderer)
```

## 渲染流程总结

```
Token 流
    ↓
render() 遍历
    ↓
token.type 在 rules 中？
    ├── 是 → rules``[type](tokens, idx, options, env, renderer)``
    │         ├── 内置规则（code_block/fence/image/hardbreak等）
    │         └── 自定义规则（add_render_rule 添加）
    └── 否 → renderToken()
              ├── nesting=1 → <tag attrs>
              ├── nesting=-1 → </tag>
              └── nesting=0 → <tag attrs>content</tag> 或 <tag attrs />
    ↓
拼接为 HTML 字符串
```

## 下一步

- [插件系统](12-plugin-system.md)：添加自定义语法和渲染
- [基础解析示例](/examples/basic-usage.md)
- [自定义渲染示例](/examples/custom-rendering.md)
