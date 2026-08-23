---
type: "concept"
title: "内置扩展完整参考"
description: "Sphinx 19个内置扩展全览——autodoc/autosummary/napoleon/intersphinx/doctest/todo/viewcode/graphviz等扩展的功能、配置与使用场景"
tags: [extensions, builtin, autodoc, sphinx-ext, reference]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T10:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T10:50:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: official-exts
    resource: /references/official-docs.md
    title: "Sphinx 官方文档 Built-in extensions"
---

# 内置扩展完整参考

Sphinx 内置了 **19 个官方扩展**（`sphinx.ext.*`），覆盖自动API文档生成、跨项目引用、代码测试、图表、TODO管理等常用场景。本章提供所有内置扩展的功能速查、启用方法和核心配置。

## 启用扩展

在 `conf.py` 的 `extensions` 列表中添加扩展模块名即可启用：

```python
# conf.py
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    # ... 更多扩展
]
```

## 扩展全览

### 1. autodoc — 自动API文档生成

**模块**：`sphinx.ext.autodoc`

从 Python docstring 自动提取文档，生成API参考。是使用最广泛的扩展。

```python
extensions = ['sphinx.ext.autodoc']
autoclass_content = 'both'  # 'class'|'init'|'both'
autodoc_member_order = 'bysource'  # 'alphabetical'|'groupwise'|'bysource'
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}
```

**核心指令**：
- `.. automodule::` — 自动记录模块
- `.. autoclass::` — 自动记录类
- `.. autofunction::` — 自动记录函数
- `.. automethod::` — 自动记录方法

→ 详见 [Autodoc自动文档](12-autodoc.md)

### 2. autosummary — API摘要页生成

**模块**：`sphinx.ext.autosummary`

自动生成API摘要表和存根（stub）页面，与autodoc配合使用。

```python
extensions = ['sphinx.ext.autosummary']
autosummary_generate = True  # 自动生成存根文件
```

```rst
.. autosummary::
   :toctree: generated

   mymodule.MyClass
   mymodule.my_function
```

### 3. napoleon — NumPy/Google风格docstring支持

**模块**：`sphinx.ext.napoleon`

支持解析 NumPy 风格和 Google 风格的 docstring（Sphinx默认只识别reST风格）。

```python
extensions = ['sphinx.ext.napoleon']
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
```

### 4. intersphinx — 跨项目引用

**模块**：`sphinx.ext.intersphinx`

链接到其他Sphinx项目的文档（Python标准库、Django、Flask等）。

```python
extensions = ['sphinx.ext.intersphinx']
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master', None),
}
```

→ 详见 [Intersphinx跨项目引用](14-intersphinx.md)

### 5. doctest — 文档中的可执行测试

**模块**：`sphinx.ext.doctest`

在文档中嵌入可执行的Python测试代码，运行 `make doctest` 验证。

```rst
.. doctest::

   >>> print("Hello")
   Hello
```

```python
extensions = ['sphinx.ext.doctest']
doctest_global_setup = "from mypackage import *"
doctest_test_doctest_blocks = 'default'
```

### 6. todo — TODO项管理

**模块**：`sphinx.ext.todo`

在文档中插入TODO项，并汇总到专门页面。

```rst
.. todo:: 补充API使用示例
```

```python
extensions = ['sphinx.ext.todo']
todo_include_todos = True  # 设为False可在正式发布时隐藏
```

### 7. viewcode — 链接到源代码

**模块**：`sphinx.ext.viewcode`

为每个API条目添加指向源代码的链接，自动生成源码HTML页面。

```python
extensions = ['sphinx.ext.viewcode']
viewcode_line_numbers = True
```

### 8. graphviz — Graphviz图表

**模块**：`sphinx.ext.graphviz`

嵌入 Graphviz 图表（流程图、类图、依赖图等）。需要安装 [Graphviz](https://graphviz.org/)。

```rst
.. graphviz::

   digraph G {
       A -> B;
       B -> C;
   }
```

```python
extensions = ['sphinx.ext.graphviz']
graphviz_output_format = 'svg'
```

### 9. inheritance_diagram — 继承关系图

**模块**：`sphinx.ext.inheritance_diagram`

基于Graphviz自动生成类的继承关系图。

```rst
.. inheritance-diagram:: mymodule.MyClass
   :parts: 1
```

```python
extensions = ['sphinx.ext.inheritance_diagram']
```

### 10. apidoc — API文档骨架生成

**模块**：`sphinx.ext.apidoc`

命令行工具，从Python包自动生成autodoc页面骨架。

```bash
sphinx-apidoc -o docs/api/ mypackage/
```

生成模块对应的 `.rst` 文件，包含 `automodule` 指令。

### 11. autosectionlabel — 自动章节标签

**模块**：`sphinx.ext.autosectionlabel`

自动为每个章节标题生成可引用标签，无需手动写 `.. _label:`。

```python
extensions = ['sphinx.ext.autosectionlabel']
autosectionlabel_prefix_document = True  # 推荐：加文档名前缀避免冲突
```

启用后可以直接用章节标题引用：`:ref:`文档名:章节名``。

### 12. coverage — 文档覆盖率统计

**模块**：`sphinx.ext.coverage`

统计哪些Python模块/函数/类缺少docstring文档。

```python
extensions = ['sphinx.ext.coverage']
coverage_ignore_modules = []
coverage_ignore_functions = ['test_']
```

运行 `make coverage` 生成覆盖率报告。

### 13. duration — 构建时长统计

**模块**：`sphinx.ext.duration`

在构建结束后报告各文件的处理时长，用于性能优化。

```python
extensions = ['sphinx.ext.duration']
```

### 14. extlinks — 外部链接快捷方式

**模块**：`sphinx.ext.extlinks`

定义常用外部链接的快捷角色，减少重复输入。

```python
extensions = ['sphinx.ext.extlinks']
extlinks = {
    'pypi': ('https://pypi.org/project/%s/', 'PyPI:%s'),
    'issue': ('https://github.com/user/repo/issues/%s', 'issue #%s'),
    'wiki': ('https://en.wikipedia.org/wiki/%s', 'Wikipedia:%s'),
}
```

使用：`:pypi:\`sphinx\`` → PyPI:sphinx

### 15. githubpages — GitHub Pages适配

**模块**：`sphinx.ext.githubpages`

为GitHub Pages发布生成必要的辅助文件（`.nojekyll`、`CNAME`）。

```python
extensions = ['sphinx.ext.githubpages']
```

### 16. ifconfig — 条件内容

**模块**：`sphinx.ext.ifconfig`

根据配置条件包含/排除文档内容。

```python
extensions = ['sphinx.ext.ifconfig']
```

```rst
.. ifconfig:: release == 'dev'

   这段内容只在开发版本文档中显示。
```

### 17. imgconverter — 图片格式转换

**模块**：`sphinx.ext.imgconverter`

使用ImageMagick自动转换图片格式（如将SVG转为PNG供LaTeX/PDF使用）。需要安装ImageMagick。

```python
extensions = ['sphinx.ext.imgconverter']
image_converter = 'convert'  # ImageMagick命令路径
```

### 18. linkcode — 外部源码链接

**模块**：`sphinx.ext.linkcode`

与viewcode类似，但链接到外部源码托管站点（GitHub/GitLab）而非生成本地页面。更轻量，但需要配置URL解析函数。

```python
extensions = ['sphinx.ext.linkcode']

def linkcode_resolve(domain, info):
    if domain != 'py':
        return None
    # 返回GitHub上的源码URL
    return f"https://github.com/user/repo/blob/main/{info['module'].replace('.', '/')}.py"
```

### 19. math — 数学公式支持

**模块**：`sphinx.ext.mathjax`（HTML数学公式渲染）

默认情况下数学支持已内置。通过MathJax（HTML）或LaTeX（PDF）渲染数学公式。

```rst
行内: :math:`E = mc^2`

.. math::

   \int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
```

```python
mathjax_path = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'
mathjax3_config = {'tex': {'inlineMath': [['$', '$']]}}
```

> 📋 Sphinx 9.x 默认使用 MathJax 3 进行数学公式渲染。

## 扩展选择建议

### 大多数项目需要的扩展

```python
extensions = [
    'sphinx.ext.autodoc',        # API文档
    'sphinx.ext.autosummary',    # API摘要
    'sphinx.ext.napoleon',       # Google/NumPy docstring
    'sphinx.ext.intersphinx',    # 跨项目引用
    'sphinx.ext.viewcode',       # 源码链接
    'sphinx.ext.todo',           # TODO项
]
```

### 推荐添加的扩展

```python
extensions += [
    'sphinx.ext.autosectionlabel',  # 自动章节标签
    'sphinx.ext.duration',          # 构建时长
    'sphinx.ext.extlinks',          # 外部链接快捷方式
    'sphinx.ext.githubpages',       # GitHub Pages（如果部署到GP）
]
```

### 按场景选择

| 场景 | 需要的扩展 |
|------|-----------|
| Python库文档 | autodoc + napoleon + autosummary + viewcode/linkcode + intersphinx |
| 教程/指南 | autosectionlabel + todo + math |
| C/C++项目 | 默认C/C++域（无需额外扩展）+ breathe（Doxygen桥接，第三方） |
| 博客/网站 | extlinks + sitemap（第三方）+ opengraph（第三方） |

## 第三方扩展生态

Sphinx拥有丰富的第三方扩展生态，以下是一些流行的第三方扩展：

| 扩展名 | 功能 | 安装 |
|--------|------|------|
| **MyST-Parser** | Markdown/MyST支持 | `pip install myst-parser` |
| **Furo** | 现代化HTML主题 | `pip install furo` |
| **sphinxcontrib-mermaid** | Mermaid图表 | `pip install sphinxcontrib-mermaid` |
| **sphinx-copybutton** | 代码块复制按钮 | `pip install sphinx-copybutton` |
| **sphinx-tabs** | 标签页组件 | `pip install sphinx-tabs` |
| **sphinx-panels** | 卡片/面板布局 | `pip install sphinx-panels` |
| **sphinx-autobuild** | 自动重新构建（开发时） | `pip install sphinx-autobuild` |
| **nbsphinx** | Jupyter Notebook支持 | `pip install nbsphinx` |
| **breathe** | Doxygen → Sphinx桥接 | `pip install breathe` |
| **sphinx-multiversion** | 多版本文档 | `pip install sphinx-multiversion` |
| **sphinxext-opengraph** | OG标签（SEO） | `pip install sphinxext-opengraph` |
| **sphinxcontrib-spelling** | 拼写检查 | `pip install sphinxcontrib-spelling` |

查找更多第三方扩展：
- [sphinx-contrib](https://github.com/sphinx-contrib/) 组织
- [awesome-sphinxdoc](https://github.com/yoloseem/awesome-sphinxdoc) 精选列表
- [PyPI Framework::Sphinx::Extension](https://pypi.org/search/?c=Framework+%3A%3A+Sphinx+%3A%3A+Extension) 分类

## 相关概念

- [Autodoc自动文档](12-autodoc.md)
- [Intersphinx跨项目引用](14-intersphinx.md)
- [扩展开发详解](15-extension-development.md)
- [主题系统](13-theme-system.md)
- [配置系统](04-config-system.md)
