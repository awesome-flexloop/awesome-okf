---
type: Example
title: 使用插件
description: 加载和组合mdit-py-plugins常用插件的完整示例
tags:
- mdit-py-plugins
- example
- usage
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

# 使用插件

## 数学文档配置

适合技术文档/学术写作：

```python
from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.amsmath import amsmath_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.front_matter import front_matter_plugin

md = (MarkdownIt("commonmark", {"html": False})
      .use(front_matter_plugin)
      .use(dollarmath_plugin, allow_labels=True)
      .use(amsmath_plugin)
      .use(footnote_plugin))

html = md.render("""---
title: Math Notes
---

# Quadratic Equation

The solution to $ax^2 + bx + c = 0$ is:

$$x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$$ (quadratic)

See [^1] for details.

[^1]: Quadratic formula derivation.
""")
```

## GitHub 风格配置

```python
from markdown_it import MarkdownIt
from mdit_py_plugins.gfm import gfm_plugin
from mdit_py_plugins.container import container_plugin

md = MarkdownIt().use(gfm_plugin, dollarmath=False)
md.use(container_plugin, "note")
md.use(container_plugin, "warning")

html = md.render("""
# Project Todo

- [x] Setup project
- [ ] Write docs
- [ ] Deploy

| Feature | Status |
|---------|--------|
| Auth    | ✅     |
| API     | 🚧     |

https://example.com

:::note
This is a note.
:::

See [^1] for more.

[^1]: Reference.
""")
```

## MyST 风格配置

```python
from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.attrs import attrs_plugin, attrs_block_plugin
from mdit_py_plugins.myst_role import myst_role_plugin
from mdit_py_plugins.myst_blocks import myst_blocks_plugin
from mdit_py_plugins.colon_fence import colon_fence_plugin
from mdit_py_plugins.field_list import fieldlist_plugin
from mdit_py_plugins.substitution import substitution_plugin  # if available

md = (MarkdownIt("commonmark")
      .use(dollarmath_plugin)
      .use(footnote_plugin)
      .use(attrs_plugin)
      .use(attrs_block_plugin)
      .use(myst_role_plugin)
      .use(colon_fence_plugin)
      .use(fieldlist_plugin))
```

## 博客配置

```python
from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from mdit_py_plugins.subscript import sub_plugin
from mdit_py_plugins.superscript import superscript_plugin
from mdit_py_plugins.wordcount import wordcount_plugin
from mdit_py_plugins.front_matter import front_matter_plugin

md = (MarkdownIt("commonmark", {"html": False})
      .use(front_matter_plugin)
      .use(anchors_plugin)
      .use(tasklists_plugin, enabled=False)
      .use(sub_plugin)
      .use(superscript_plugin)
      .use(wordcount_plugin, per_minute=200))

env = {}
html = md.render("# Hello World\n\nH~2~O is water. 2^10^=1024.", env)
print("Words:", env.get("wordcount", {}).get("words"))
```

## 自定义渲染数学公式（配合KaTeX）

```python
from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin

def render_math(content, options):
    """使用KaTeX渲染（需要pip install katex）"""
    try:
        import katex
        return katex.render(content, display_mode=options.get("display_mode", False))
    except ImportError:
        from markdown_it.common.utils import escapeHtml
        return escapeHtml(content)

md = MarkdownIt().use(dollarmath_plugin, renderer=render_math)
```
