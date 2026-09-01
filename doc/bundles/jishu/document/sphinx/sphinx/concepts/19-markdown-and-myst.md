---
type: "concept"
title: "Markdown 与 MyST 支持"
description: "在Sphinx中使用Markdown——MyST-Parser安装配置、CommonMark兼容语法、Markdown与reST混排、reST指令/角色在Markdown中的使用"
tags: [markdown, myst, mysta-parser, markup, writing]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T10:35:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T10:35:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: official-markdown
    resource: /references/official-docs.md
    title: "Sphinx 官方文档 Markdown 页面"
  - id: myst-docs
    resource: "https://myst-parser.readthedocs.io/en/latest/"
    title: "MyST-Parser 官方文档"
---

# Markdown 与 MyST 支持

虽然 Sphinx 默认使用 reStructuredText，但通过 **MyST-Parser** 扩展，Sphinx 也可以完整支持 Markdown 编写文档。MyST（Markedly Structured Text）是专为技术文档设计的 Markdown 风味，兼容 CommonMark 标准，同时支持 Sphinx 的所有强大功能（指令、角色、交叉引用等）。

## 为什么用 MyST 而非普通 Markdown？

标准 Markdown（CommonMark）在技术文档场景下功能有限——不支持警告框、交叉引用、自动API文档、目录树等。MyST 在 CommonMark 基础上增加了 Sphinx/reST 生态的能力：

| 特性 | CommonMark | MyST | reST |
|------|:----------:|:----:|:----:|
| 标题/段落/列表/链接 | ✅ | ✅ | ✅ |
| 代码块语法高亮 | ⚠️ 有限 | ✅ | ✅ |
| 表格 | ⚠️ 有限 | ✅ | ✅ |
| 警告/提示框（note/warning） | ❌ | ✅ | ✅ |
| 交叉引用（ref/doc） | ❌ | ✅ | ✅ |
| Sphinx指令（toctree/code-block） | ❌ | ✅ | ✅ |
| Sphinx角色（py:func等） | ❌ | ✅ | ✅ |
| 数学公式 | ❌ | ✅ | ✅ |
| 脚注 | ⚠️ 部分支持 | ✅ | ✅ |
| 与reST文件混排 | — | ✅ | ✅ |

## 安装与配置

### 步骤1：安装 MyST-Parser

```bash
pip install --upgrade myst-parser
```

> 📋 MyST-Parser 要求 Sphinx ≥ 2.1，完全兼容 Sphinx 9.x。

### 步骤2：在 conf.py 中启用

```python
# conf.py
extensions = [
    'myst_parser',  # 添加 MyST-Parser
    # ... 其他扩展
]
```

### 步骤3：配置源文件后缀

如果需要同时支持 `.rst` 和 `.md` 文件，配置 `source_suffix`：

```python
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
```

也可以将 `.txt` 文件解析为 Markdown：

```python
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
    '.txt': 'markdown',
}
```

### 步骤4（可选）：配置 MyST 语法扩展

MyST 支持通过 `myst_enable_extensions` 启用额外语法：

```python
myst_enable_extensions = [
    "amsmath",      # LaTeX 数学公式
    "colon_fence",  # 使用 ::: 代替 ``` 的围栏（支持指令嵌套）
    "deflist",      # 定义列表
    "dollarmath",   # 使用 $...$ 和 $$...$$ 的行内/块级数学
    "fieldlist",    # 字段列表（如参数说明）
    "html_admonition", # HTML风格的警告框
    "html_image",   # HTML风格的图片
    "linkify",      # 自动链接URL
    "replacements", # 文本替换（如 (c) → ©）
    "smartquotes",  # 智能引号
    "strikethrough", # 删除线 ~~text~~
    "substitution", # 替换引用
    "tasklist",     # 任务列表 - [ ] / - [x]
]
```

## MyST Markdown 语法速览

### 标准 CommonMark 语法

MyST 完全兼容标准 Markdown 语法：

```markdown
# 一级标题

## 二级标题

**粗体** *斜体* `行内代码` ~~删除线~~

[链接文本](https://example.com)
![图片描述](/_static/image.png)

- 无序列表项
- 无序列表项

1. 有序列表项
2. 有序列表项

> 引用块

```python
print("代码块")
```
```

### MyST 特有语法

#### 1. 指令（Directives）

MyST 使用围栏代码块语法（```` ``` ```` 或 `:::`）替代 reST 的 `.. directive::` 语法：

**方法一：反引号围栏**（推荐，与Markdown代码块一致）

````markdown
```{note}
这是一条提示信息。
```
````

**方法二：冒号围栏**（适合嵌套场景）

```markdown
:::{warning}
这是警告信息。
:::
```

**带参数的指令**：

````markdown
```{code-block} python
:linenos:
:emphasize-lines: 2

def hello():
    print("Hello!")  # 这行高亮
```
````

**toctree 指令**：

````markdown
```{toctree}
---
maxdepth: 2
caption: 目录
numbered: true
---
intro
usage/index
api/index
```
````

#### 2. 角色（Roles）

MyST 使用 `{role}`text`` 语法替代 reST 的 `:role:`text`` 语法：

```markdown
{func}`print`              {== 相当于reST的:py:func:`print` ==}
{meth}`str.join`           {== 类方法 ==}
{mod}`os.path`             {== 模块 ==}
{ref}`my-label`            {== 交叉引用 ==}
{doc}`/intro`              {== 文档引用 ==}
{download}`/files/data.csv` {== 下载链接 ==}
```

如果角色名称包含冒号（如域角色），使用反引号包裹：

```markdown
{py:func}`print`
{py:class}`list`
{py:meth}`~queue.Queue.get`
```

#### 3. 链接到Sphinx文档

```markdown
{doc}`/tutorial/first-steps`           {== 文档引用 ==}
[参见安装指南](<install.md>)           {== Markdown风格链接到本地md文件 ==}
{ref}`my-reference-label`             {== 引用标签 ==}
```

#### 4. 脚注

```markdown
这是带脚注的文字[^1]。

[^1]: 这是脚注内容。
```

#### 5. 数学公式（需启用 dollarmath 扩展）

```markdown
行内公式：$E = mc^2$

块级公式：
$$
\sum_{i=1}^{n} i = \frac{n(n+1)}{2}
$$
```

#### 6. 任务列表（需启用 tasklist 扩展）

```markdown
- [x] 完成Sphinx安装
- [x] 编写第一个文档
- [ ] 部署到线上
```

#### 7. 定义列表（需启用 deflist 扩展）

```markdown
Sphinx
: Python生态最主流的文档生成器

MyST
: Markedly Structured Text，支持Sphinx功能的Markdown风味
```

#### 8. 自动链接URL（需启用 linkify 扩展）

```markdown
访问 https://www.sphinx-doc.org/ 了解更多。
（URL会自动变成链接，不需要手动写[]()语法）
```

## Markdown 与 reST 混排

MyST-Parser 支持在同一个 Sphinx 项目中同时使用 `.rst` 和 `.md` 文件：

- toctree 中可以混合引用 `.rst` 和 `.md` 文件（不需要写扩展名）
- `.md` 文件可以通过 `{doc}` / `{ref}` 角色引用 `.rst` 文件
- `.rst` 文件可以通过 `:doc:` / `:ref:` 角色引用 `.md` 文件
- 两种格式的文件共享同一个 Sphinx 构建环境、交叉引用、搜索索引

```rst
.. toctree::

   install       # install.rst
   quickstart    # quickstart.md
   api/index     # 可以是rst或md
```

## 从纯 Markdown 迁移到 MyST

如果你已有 MkDocs 或其他工具编写的 Markdown 文档，迁移到 Sphinx+MyST 通常很简单：

1. 安装 `myst-parser` 并在 `extensions` 中启用
2. 配置 `source_suffix` 支持 `.md`
3. 添加 `index.md` 作为入口文件（替代 `index.rst`）
4. 在 `index.md` 中使用 `{toctree}` 指令组织文档
5. 逐步将 reST 特有功能（如交叉引用、警告框）迁移为 MyST 语法

### 常见转换对照

| 功能 | reST 语法 | MyST 语法 |
|------|----------|-----------|
| 提示框 | `.. note::` | ````{note}```` ```` ``````` |
| 代码块 | `.. code-block:: python` | ```` ```python ```` |
| 函数引用 | `:py:func:\`print\`` | `{py:func}\`print\`` |
| 交叉引用 | `:ref:\`label\`` | `{ref}\`label\`` |
| 文档引用 | `:doc:\`/path\`` | `{doc}\`/path\`` |
| 目录树 | `.. toctree::` | ````{toctree}```` ```` ``````` |
| 数学 | `.. math::` | `$$ ... $$` |

## include 功能

在 Markdown 中可以 include 其他文件：

````markdown
```{include} /_static/header.md
```
````

也可以包含 reST 文件（MyST会自动检测格式）：

````markdown
```{include} /legacy/content.rst
```
````

## 配置参考

### 常用 MyST 配置项

```python
# conf.py

# 启用的MyST语法扩展
myst_enable_extensions = [
    "amsmath", "colon_fence", "deflist", "dollarmath",
    "fieldlist", "linkify", "replacements", "smartquotes",
    "strikethrough", "substitution", "tasklist",
]

# 数学公式渲染（MathJax或KaTeX）
myst_update_mathjax = True

# 标题锚点自动生成（slugify方式）
myst_heading_anchors = 3  # 为H1-H3自动生成锚点

# 脚注自动编号
myst_footnote_transition = True

# 链接URL安全方案（允许的scheme）
myst_url_schemes = ("http", "https", "mailto", "ftp")

# 代码块语言别名
myst_code_block_lang_aliases = {}
```

## 相关概念

- [reStructuredText 基础语法](18-rest-primer.md)
- [交叉引用完全指南](20-cross-references-guide.md)
- [5分钟快速上手](01-getting-started.md)
- [Sphinx应用类](03-application-class.md)
