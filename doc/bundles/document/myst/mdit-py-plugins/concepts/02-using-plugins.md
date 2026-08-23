---
type: Concept
title: 使用插件
description: mdit-py-plugins 常用插件快速上手指南：dollarmath、footnote、container、tasklists、gfm等
tags:
- mdit-py-plugins
- usage
- dollarmath
- footnote
- container
- tasklists
- gfm
difficulty: 入门
estimated_time: 20分钟
prerequisites:
- 01-plugin-basics
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

# 使用插件

## 数学公式：dollarmath

支持 `$inline$` 和 `$$block$$` 数学公式。

```python
from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin

md = MarkdownIt().use(dollarmath_plugin)
html = md.render("$a^2 + b^2 = c^2$\n\n$$E = mc^2$$")
```

常用选项：
```python
md.use(dollarmath_plugin,
       allow_labels=True,         # 允许 $$eq$$ (label) 公式编号
       allow_space=False,         # $ 前后不允许空格（$ a $ 不匹配）
       allow_digits=False,        # $ 前后不允许数字（避免$100误匹配）
       double_inline=True,        # 行内也允许 $$...$$
       renderer=my_render_fn)     # 自定义渲染函数
```

带标签公式：
```markdown
$$x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$$ (quadratic)
```
渲染为带锚点链接的块。

## 脚注：footnote

支持 `[^label]` 引用和 `[^label]: content` 定义。

```python
from mdit_py_plugins.footnote import footnote_plugin

md = MarkdownIt().use(footnote_plugin)
html = md.render("""
Here is a note[^1] and another[^long].

[^1]: First footnote.
[^long]: A longer footnote.

    With multiple paragraphs.
""")
```

选项：
```python
md.use(footnote_plugin,
       inline=True,              # 启用 ^[inline footnote] 语法
       move_to_end=True,         # 脚注定义移到文档末尾
       always_match_refs=False)  # 引用未定义脚注是否仍渲染
```

行内脚注：`Some text ^[inline footnote content]`

## 自定义容器：container

支持 `:::name\ncontent\n:::` 自定义容器。

```python
from mdit_py_plugins.container import container_plugin

md = MarkdownIt()
md.use(container_plugin, "warning")  # 容器名
md.use(container_plugin, "note")     # 可多次use注册不同容器

html = md.render("""
::: warning
This is a warning!
:::
""")
# 渲染为 <div class="warning">...</div>
```

自定义验证和渲染：
```python
def validate(params, markup):
    return params.strip().startswith("spoiler")

def render_spoiler(tokens, idx, options, env, renderer):
    if tokens[idx].nesting == 1:
        return '<details><summary>Click to expand</summary>'
    return '</details>'

md.use(container_plugin, "spoiler",
       marker=":", validate=validate, render=render_spoiler)
```

## 任务列表：tasklists

将 `- [ ]` 和 `- [x]` 渲染为复选框。

```python
from mdit_py_plugins.tasklists import tasklists_plugin

md = MarkdownIt().use(tasklists_plugin)
html = md.render("""
- [x] Completed task
- [ ] Incomplete task
""")
```

选项：
```python
md.use(tasklists_plugin,
       enabled=False,       # checkbox是否disabled（默认False=禁用交互）
       label=False,         # 是否用<label>包裹
       label_after=False)   # label是否在checkbox后
```

## 冒号围栏：colon_fence

用 `:::` 替代反引号的围栏代码块，适合在代码块内嵌套代码块。

```python
from mdit_py_plugins.colon_fence import colon_fence_plugin

md = MarkdownIt().use(colon_fence_plugin)
html = md.render("""
:::python
def hello():
    print("```fence inside fence```")
:::
""")
```

## 定义列表：deflist

Pandoc 风格定义列表。

```python
from mdit_py_plugins.deflist import deflist_plugin

md = MarkdownIt().use(deflist_plugin)
html = md.render("""
Term 1
: Definition of term 1

Term 2
~ Alternative definition marker
""")
# 渲染为 <dl><dt>Term 1</dt><dd>Definition...</dd></dl>
```

## 下标/上标：sub/superscript

```python
from mdit_py_plugins.subscript import sub_plugin
from mdit_py_plugins.superscript import superscript_plugin

md = MarkdownIt().use(sub_plugin).use(superscript_plugin)
html = md.render("H~2~O and 2^10^ = 1024")
# H<sub>2</sub>O and 2<sup>10</sup> = 1024
```

## 前置元数据：front_matter

解析文档开头的 YAML front matter。

```python
from mdit_py_plugins.front_matter import front_matter_plugin

md = MarkdownIt().use(front_matter_plugin)
env = {}
md.render("""---
title: My Document
author: John
---

# Content
""", env)
# front_matter数据不在HTML中输出，需通过token检查获取
```

注意：front_matter插件解析 `---` 分隔的元数据块，但不解析YAML内容（仅作为原始文本）。需要配合YAML解析库使用。

## GFM 组合：gfm

一键启用 GitHub Flavored Markdown 风格。

```python
from mdit_py_plugins.gfm import gfm_plugin

md = MarkdownIt().use(gfm_plugin)
# 自动启用：table、strikethrough、tasklists、alerts、autolink、footnote
```

选项：
```python
md.use(gfm_plugin,
       dollarmath=True,          # 额外启用数学公式
       front_matter=True,        # 额外启用YAML前置
       tasklists_editable=True)  # 复选框可交互
```

要求 markdown-it-py >= 4.1.0。

## 字数统计：wordcount

统计文档词数和预估阅读时间。

```python
from mdit_py_plugins.wordcount import wordcount_plugin

md = MarkdownIt().use(wordcount_plugin, per_minute=200)
env = {}
md.render("Hello world, this is a test document.", env)
print(env["wordcount"])  # {'words': 7, 'minutes': 0}
```

## AMS数学环境：amsmath

解析 LaTeX AMS 数学环境。

```python
from mdit_py_plugins.amsmath import amsmath_plugin

md = MarkdownIt().use(amsmath_plugin)
html = md.render(r"""
\begin{align}
a &= b + c \\
d &= e + f
\end{align}
""")
```

支持：equation, multline, gather, align, alignat, flalign, matrix, pmatrix, bmatrix, Bmatrix, vmatrix, Vmatrix, eqnarray。

## 组合使用多个插件

```python
md = (MarkdownIt("commonmark", {"html": False})
      .use(dollarmath_plugin, allow_labels=False)
      .use(footnote_plugin)
      .use(tasklists_plugin)
      .use(container_plugin, "note")
      .use(container_plugin, "warning")
      .use(colon_fence_plugin)
      .use(sub_plugin)
      .use(superscript_plugin))
```
