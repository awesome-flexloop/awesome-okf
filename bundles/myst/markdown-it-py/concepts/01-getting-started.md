---
type: Concept
title: 快速开始
description: MarkdownIt 实例化、parse/render/parseInline/renderInline 基本用法、CLI 命令行工具
tags:
- markdown-it-py
- getting-started
- parse
- render
- cli
difficulty: 入门
estimated_time: 15分钟
prerequisites:
- 00-introduction
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

# 快速开始

## 基本工作流

使用 markdown-it-py 只需三步：创建实例 → 解析/渲染 → 获取结果。

### 渲染 HTML（最常用）

```python
from markdown_it import MarkdownIt

md = MarkdownIt()  # 默认使用 commonmark 预设
html = md.render("# Hello\n\nThis is **bold** and *italic*.")
print(html)
```

输出：
```html
<h1>Hello</h1>
<p>This is <strong>bold</strong> and <em>italic</em>.</p>
```

### 仅解析为 Token 列表

```python
from markdown_it import MarkdownIt

md = MarkdownIt()
tokens = md.parse("# Hello\n\nWorld")
for tok in tokens:
    print(f"{tok.type:20s} tag={tok.tag:5s} nesting={tok.nesting} content={tok.content!r}")
```

输出：
```
heading_open         tag=h1    nesting=1 content=''
inline               tag=      nesting=0 content='Hello'
text                 tag=      nesting=0 content='Hello'
heading_close        tag=h1    nesting=-1 content=''
paragraph_open       tag=p     nesting=1 content=''
inline               tag=      nesting=0 content='World'
text                 tag=      nesting=0 content='World'
paragraph_close      tag=p     nesting=-1 content=''
```

注意：`inline` 类型的 token 包含 `children` 字段，其中是行内元素的子 tokens。

### 仅渲染行内内容（不含块级包装）

```python
from markdown_it import MarkdownIt

md = MarkdownIt()
# parseInline 不产生 paragraph 包装
tokens = md.parseInline("Hello **world**")
html = md.renderInline("Hello **world**")
print(html)  # Hello <strong>world</strong>
```

## 选择预设

构造函数的第一个参数选择预设，第二个参数覆盖选项：

```python
from markdown_it import MarkdownIt

# CommonMark 严格模式（默认）
md_commonmark = MarkdownIt("commonmark")

# GFM 风格（表格+删除线+自动链接）
md_gfm = MarkdownIt("gfm-like")

# 最小配置（仅段落+文本）
md_zero = MarkdownIt("zero")

# 全规则启用
md_full = MarkdownIt("js-default")

# 带选项覆盖
md = MarkdownIt("commonmark", {"html": False, "breaks": True})
```

## 启用/禁用规则

创建实例后可以精细控制哪些语法规则生效：

```python
from markdown_it import MarkdownIt

md = MarkdownIt("commonmark")

# 禁用规则
md.disable("emphasis")  # 禁用强调
md.disable(["emphasis", "link"])  # 批量禁用

# 启用规则（规则需已注册到 Ruler 中）
md.enable("strikethrough")

# 查看当前规则状态
print(md.get_active_rules())  # 各链当前启用的规则名列表
print(md.get_all_rules())     # 各链所有已注册规则名
```

## env 环境对象

`parse()` 和 `render()` 接受可选的 `env` 参数，用于在解析过程中收集元数据：

```python
from markdown_it import MarkdownIt

md = MarkdownIt()
env = {}
html = md.render("[Google][1]\n\n[1]: https://google.com", env)
print(env)
# {'references': {'1': {'title': '', 'href': 'https://google.com', 'label': '1'}}}
```

`env` 是一个普通字典，插件可以向其中写入自定义数据。

## 自定义渲染规则

通过 `add_render_rule()` 覆盖特定 token 类型的渲染：

```python
from markdown_it import MarkdownIt
from markdown_it.token import Token
from markdown_it.renderer import RendererHTML

def render_heading_open(self: RendererHTML, tokens, idx, options, env):
    token = tokens[idx]
    level = int(token.tag[1])  # h1→1, h2→2, ...
    return f'<h{level} id="section-{idx}">'

md = MarkdownIt()
md.add_render_rule("heading_open", render_heading_open)
html = md.render("# Title")
print(html)  # <h1 id="section-0">Title</h1>
```

## CLI 命令行工具

安装后可直接使用 `markdown-it` 命令：

```bash
# 渲染文件
markdown-it README.md

# 标准输入
echo "# Hello" | markdown-it -

# 交互模式
markdown-it
```

## 完整示例：从解析到检查Token

```python
from markdown_it import MarkdownIt
from pprint import pprint

md = MarkdownIt("gfm-like")
tokens = md.parse("## Table Example\n\n| a | b |\n|---|---|\n| 1 | 2 |")

for i, tok in enumerate(tokens):
    print(f"[{i:2d}] {tok.type:20s} tag={tok.tag:8s} "
          f"nest={tok.nesting} level={tok.level} "
          f"children={len(tok.children) if tok.children else 0}")
```

## 下一步

- [预设与选项](02-presets-and-options.md)：深入了解各预设的差异和选项配置
- [Token 流模型](03-token-stream.md)：理解解析结果的数据结构
- [解析管线架构](04-parsing-pipeline.md)：了解三链解析流程
