---
type: Example
title: 自定义渲染示例
description: 使用 add_render_rule 自定义标题ID、链接新窗口、代码高亮、图片懒加载
tags:
- markdown-it-py
- example
- render
- custom
- add_render_rule
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

# 自定义渲染示例

## 为标题添加自动 ID

```python
from markdown_it import MarkdownIt
import re

def slugify(text):
    return re.sub(r'[^\w\u4e00-\u9fff\- ]', '', text.lower()).strip().replace(' ', '-')

def render_heading_open(tokens, idx, options, env, renderer):
    token = tokens[idx]
    level = token.tag[1]  # "h1" → "1"
    # 获取下一个inline token的文本内容作为slug
    inline_token = tokens[idx + 1]
    text = ""
    if inline_token.children:
        for child in inline_token.children:
            if child.type == "text":
                text += child.content
    slug = slugify(text) or f"section-{idx}"
    return f'<h{level} id="{slug}">'

md = MarkdownIt()
md.add_render_rule("heading_open", render_heading_open)
html = md.render("# Hello World")
print(html)
# <h1 id="hello-world">Hello World</h1>
```

## 外链在新窗口打开

```python
from markdown_it import MarkdownIt
from urllib.parse import urlparse

def render_link_open(tokens, idx, options, env, renderer):
    token = tokens[idx]
    href = token.attrGet("href") or ""
    parsed = urlparse(href)
    # 外链添加 target="_blank"
    if parsed.scheme in ("http", "https") and parsed.netloc:
        token.attrSet("target", "_blank")
        token.attrSet("rel", "noopener noreferrer")
    return renderer.renderToken(tokens, idx, options)

md = MarkdownIt()
md.add_render_rule("link_open", render_link_open)
html = md.render("[external](https://example.com) and ``[internal](/page)``")
# external 链接有 target="_blank"，internal 没有
```

## 自定义代码块（带复制按钮）

```python
from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml

def render_fence(tokens, idx, options, env, renderer):
    token = tokens[idx]
    lang = token.info.strip() if token.info else ""
    code = escapeHtml(token.content)
    lang_class = f'language-{lang}' if lang else ""
    return (
        f'<div class="code-block">'
        f'<div class="code-header">{lang or "code"}'
        f'<button class="copy-btn" onclick="copyCode(this)">Copy</button>'
        f'</div>'
        f'<pre><code class="{lang_class}">{code}</code></pre>'
        f'</div>'
    )

md = MarkdownIt()
md.add_render_rule("fence", render_fence)
html = md.render("```python\nprint('hello')\n```")
```

## 图片懒加载

```python
def render_image(tokens, idx, options, env, renderer):
    token = tokens[idx]
    token.attrSet("loading", "lazy")
    token.attrSet("decoding", "async")
    return renderer.renderToken(tokens, idx, options)

md = MarkdownIt()
md.add_render_rule("image", render_image)
html = md.render("!``[alt](image.png)``")
# <img src="image.png" alt="alt" loading="lazy" decoding="async" />
```

## 集成 Pygments 代码高亮

```python
from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml

def highlight_code(code, lang, attrs):
    try:
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name
        from pygments.formatters import HtmlFormatter
        if not lang:
            return f'<pre><code>{escapeHtml(code)}</code></pre>'
        lexer = get_lexer_by_name(lang, stripall=False)
        formatter = HtmlFormatter(cssclass="highlight")
        return highlight(code, lexer, formatter)
    except (ImportError, ValueError):
        return f'<pre><code class="language-{lang}">{escapeHtml(code)}</code></pre>'

md = MarkdownIt("commonmark", {"highlight": highlight_code})
html = md.render("```python\nprint('hello')\n```")
```

## 组合多个自定义渲染

```python
md = (MarkdownIt("gfm-like")
      .add_render_rule("heading_open", render_heading_open)
      .add_render_rule("link_open", render_link_open)
      .add_render_rule("image", render_image))
```
