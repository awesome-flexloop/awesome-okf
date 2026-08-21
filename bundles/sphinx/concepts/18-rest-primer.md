---
type: "concept"
title: "reStructuredText 基础语法"
description: "Sphinx 默认标记语言 reStructuredText（reST）的核心语法入门——段落、行内标记、列表、代码块、表格、链接、指令、角色等"
tags: [rest, markup, syntax, writing, basics]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T10:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T10:30:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: rst-primer
    resource: /references/rest-syntax-quickref.md
    title: "reStructuredText 语法速查"
  - id: official-rst
    resource: /references/official-docs.md
    title: "Sphinx 官方文档 reST Primer"
---

# reStructuredText 基础语法

**reStructuredText**（简称 reST）是 Sphinx 默认的纯文本标记语言。它由 Python Docutils 项目开发，设计理念是"简单、不显眼"——即使不渲染，reST 源文件也具有良好的可读性。本章介绍编写 Sphinx 文档所需的核心 reST 语法。

## 段落

段落是 reST 文档最基本的块。段落由**一个或多个空行**分隔，同一段落的所有行必须左对齐到相同缩进级别（与 Python 类似，缩进在 reST 中具有语义意义）：

```rst
这是第一个段落。它可以包含多行文本，
只要保持相同的缩进级别即可。

这是第二个段落。两个段落之间用空行分隔。
```

### 行块（保留换行）

如果需要精确控制换行（如诗歌、地址），使用 `|` 前缀：

```rst
| 这些行会
| 精确按照
| 源文件中的方式换行显示
```

### 引用块

引用块通过比周围段落更深的缩进创建：

```rst
这是普通段落。

   这是引用块。
   它通常以缩进呈现。
```

## 行内标记

reST 的行内标记非常简洁：

| 语法 | 效果 | 说明 |
|------|------|------|
| `*文本*` | *斜体* | 强调（emphasis） |
| `**文本**` | **粗体** | 强强调（strong emphasis） |
| `` ``代码`` `` | `代码` | 行内代码（literal） |

使用规则和注意事项：

1. **不可嵌套**——行内标记之间不能互相嵌套
2. **不能以空白开头或结尾**——`* 文本*` 是错误写法
3. **必须被非单词字符包围**——如果需要嵌入单词中间，使用反斜杠转义空格：`one\ *word*\ here`
4. **星号和反引号需要转义**——在正文中出现 `*` 或 `` ` `` 可能被误解析为标记，使用 `\*` 和 `` \` `` 转义

## 列表

### 无序列表

使用 `*`、`+` 或 `-` 作为项目符号：

```rst
* 项目一
* 项目二，可以写多行
  第二行需要缩进
* 项目三
```

### 有序列表

使用数字加 `.` 或 `#.` 自动编号：

```rst
1. 第一项
2. 第二项

#. 自动编号项一
#. 自动编号项二
```

### 定义列表

定义列表用于术语-解释对，术语独占一行，定义缩进：

```rst
Sphinx
   Python生态最主流的文档生成器。

reStructuredText
   Sphinx默认的标记语言，简称reST。
```

术语不能超过一行文本。

### 嵌套列表

嵌套列表必须与父列表项之间用**空行**分隔：

```rst
* 父项一

  * 子项一
  * 子项二

* 父项二
```

## 代码块

### 字面块（`::` 标记）

在段落末尾使用 `::`，下一个缩进块即被视为代码：

```rst
安装Sphinx的命令如下::

   pip install sphinx
```

段落末尾的 `::` 会被渲染为一个冒号；如果 `::` 前面是空白行，则完全隐藏。

### code-block 指令（推荐）

使用 `code-block` 指令可以指定语言，获得语法高亮：

```rst
.. code-block:: python

   def hello(name: str) -> str:
       """一个简单的问候函数。"""
       return f"Hello, {name}!"

   print(hello("Sphinx"))
```

支持语言包括：`python`、`javascript`、`c`、`cpp`、`java`、`ruby`、`bash`、`rst`、`yaml`、`json`、`sql`、`html`、`css` 等。还支持 `.. code-block:: none` 表示无高亮。

### doctest 块

交互式 Python 会话可以直接用 `>>>` 标记：

```rst
>>> print("Hello, Sphinx!")
Hello, Sphinx!
>>> 1 + 2
3
```

## 标题

标题通过在文本下方（或上下方）加下划线/上划线创建。reST 不强制特定符号，但同一层级必须一致。Sphinx 推荐约定：

```rst
=================
一级标题（H1）
=================

二级标题（H2）
==============

三级标题（H3）
--------------

四级标题（H4）
~~~~~~~~~~~~~~

五级标题（H5）
^^^^^^^^^^^^^^
```

常用符号：`=`、`-`、`~`、`^`、`"`、`'`、`+`、`*`、`#`。符号行长度必须至少与标题文本等长。

> 💡 在 Sphinx 中，文档的标题（第一个出现的标题）通常由文档文件名和 toctree 控制，不需要手动写 H1。每个 `.rst` 文件通常以 H2 开始。

## 链接

### 外部链接

使用反引号+尖括号语法：

```rst
访问 `Sphinx官方网站 <https://www.sphinx-doc.org/>`_ 获取更多信息。
```

也可以分开定义链接目标：

```rst
访问 Sphinx_ 官方网站。

.. _Sphinx: https://www.sphinx-doc.org/
```

### 交叉引用标签

使用 `.. _标签名:` 定义标签，`:ref:` 角色引用：

```rst
.. _my-installation-section:

安装指南
--------

更多安装说明请参见 :ref:`my-installation-section`。
```

`:ref:` 自动生成链接文本（章节标题）。也可以自定义链接文本：`:ref:`自定义文本<my-installation-section>``。

### 文档引用

使用 `:doc:` 角色直接引用其他文档：

```rst
参见 :doc:`/tutorial/first-steps` 获取入门教程。
```

## 表格

### 网格表格（最灵活）

```rst
+------------------------+------------+----------+
| 功能                   | 支持格式   | 备注     |
+========================+============+==========+
| HTML输出               | ✅         | 主要格式 |
+------------------------+------------+----------+
| PDF/LaTeX输出          | ✅         | 需LaTeX  |
+------------------------+------------+----------+
| EPUB电子书             | ✅         |          |
+------------------------+------------+----------+
```

`=` 分隔表头和表体，`-` 分隔普通行。

### 简单表格（适合纯数据）

```rst
=====  =====  =======
输入1  输入2  输出
=====  =====  =======
False  False  False
True   False  True
False  True   True
True   True   True
=====  =====  =======
```

### CSV 表格

```rst
.. csv-table:: Python版本要求
   :header: "Python", "Sphinx", "状态"
   :widths: 15, 15, 20

   "3.12+", "9.x", "✅ 支持"
   "3.10-3.11", "7.x-8.x", "⚠️ 旧版支持"
```

### 列表表格

最适合包含复杂内容的表格：

```rst
.. list-table:: 标题
   :header-rows: 1
   :widths: 20 40 40

   * - 扩展名
     - 功能
     - 用途
   * - autodoc
     - 从docstring生成文档
     - API文档自动生成
   * - intersphinx
     - 跨项目引用
     - 链接Python标准库文档
```

## 图片与图

### 图片

```rst
.. image:: /_static/logo.png
   :width: 300px
   :height: 100px
   :scale: 50%
   :alt: 项目Logo
   :align: center
```

### 图（带标题的图片）

```rst
.. figure:: /_static/architecture.png
   :width: 600px
   :alt: 架构图

   Sphinx 架构图，展示了核心组件之间的关系。
```

图可以被 `:ref:` 交叉引用（自动编号）。

## 指令（Directives）

指令是 reST 的扩展机制，以 `.. 指令名::` 开头，是 Sphinx 最强大的功能之一。

### 提示/警告框

```rst
.. note::

   这是一条备注信息，用于提供额外说明。

.. warning::

   这是警告信息，表示需要特别注意的事项。

.. important::

   这是重要信息。

.. tip::

   这是小技巧/建议。

.. seealso::

   参见 :doc:`/concepts/03-application-class` 了解更多细节。

.. deprecated:: 9.0
   此方法已废弃，请使用 ``new_method()`` 替代。
```

### 目录树（toctree）

toctree 是 Sphinx 组织文档层级结构的核心指令：

```rst
.. toctree::
   :maxdepth: 2
   :caption: 目录
   :numbered:

   intro
   usage/index
   api/index
```

常用选项：
- `:maxdepth: N` — 目录展开深度
- `:caption: 文本` — 侧边栏标题
- `:numbered:` — 自动章节编号
- `:hidden:` — 隐藏但仍可被引用
- `:glob:` — 使用通配符匹配文件

### 版本标记

```rst
.. versionadded:: 7.0
   新增了 ``Sphinx.add_config_value()`` 的 ``types`` 参数。

.. versionchanged:: 8.0
   默认主题从 classic 改为 alabaster。

.. deprecated:: 9.0
   ``app.add_stylesheet()`` 已废弃，请使用 ``app.add_css_file()``。
```

### 数学公式

```rst
行内公式：:math:`E = mc^2`

.. math::

   \sum_{i=1}^{n} i = \frac{n(n+1)}{2}
```

需要启用 `sphinx.ext.mathjax` 扩展（默认启用）。

### 代码段显示选项

```rst
.. code-block:: python
   :linenos:
   :emphasize-lines: 2,4
   :caption: 示例代码

   def greet(name):        # 第1行
       print(f"Hello!")    # 第2行（高亮）
       return name         # 第3行
       # 第4行（高亮）
```

## 角色（Roles）

角色用于行内语义标记，格式为 `:角色名:`内容``。Sphinx 内置了大量有用的角色：

### 通用角色

| 角色 | 用途 | 示例 |
|------|------|------|
| `:abbr:` | 缩写（title显示全称） | `:abbr:`LSP (Language Server Protocol)`` |
| `:command:` | 命令行命令 | `:command:`sphinx-build`` |
| `:dfn:` | 术语定义 | `:dfn:`Sphinx`` |
| `:file:` | 文件路径 | `:file:`conf.py`` |
| `:guilabel:` | GUI标签 | `:guilabel:`OK``` |
| `:kbd:` | 键盘按键 | `:kbd:`Ctrl+C`` |
| `:mailheader:` | 邮件头 | `:mailheader:`Content-Type`` |
| `:makevar:` | Make变量 | `:makevar:`SPHINXBUILD`` |
| `:manpage:` | man手册页 | `:manpage:`ls(1)`` |
| `:menuselection:` | 菜单选择 | `:menuselection:`File --> Save`` |
| `:mimetype:` | MIME类型 | `:mimetype:`text/html`` |
| `:newsgroup:` | 新闻组 | `:newsgroup:`comp.lang.python`` |
| `:program:` | 可执行程序名 | `:program:`sphinx-build`` |
| `:regexp:` | 正则表达式 | `:regexp:`^[a-z]+$`` |
| `:samp:` | 带变量的字面量 | `:samp:`pip install {package}`` |

### Sphinx 特有角色

| 角色 | 用途 |
|------|------|
| `:ref:` | 交叉引用标签 |
| `:doc:` | 引用其他文档 |
| `:download:` | 下载文件链接 |
| `:numref:` | 带编号引用（图/表/代码块） |
| `:term:` | 引用术语表 |
| `:envvar:` | 环境变量 |
| `:token:` | 语法标记 |
| `:pep:` | Python PEP引用 |
| `:rfc:` | RFC引用 |

### Python域角色

| 角色 | 用途 | 示例 |
|------|------|------|
| `:py:mod:` | 模块 | `:py:mod:`os.path`` |
| `:py:func:` | 函数 | `:py:func:`print`` |
| `:py:class:` | 类 | `:py:class:`list`` |
| `:py:meth:` | 方法 | `:py:meth:`str.join`` |
| `:py:attr:` | 属性 | `:py:attr:`datetime.date.year`` |
| `:py:data:` | 模块级数据 | `:py:data:`sys.version`` |
| `:py:const:` | 常量 | `:py:const:`math.pi`` |
| `:py:exc:` | 异常 | `:py:exc:`ValueError`` |
| `:py:obj:` | 任意Python对象 | `:py:obj:`some.object`` |

### 引用修饰符

- `~` 前缀：缩短链接文本为最后一部分。`:py:meth:`~queue.Queue.get`` 显示为 `get()`
- `!` 前缀：只显示文本不生成链接。`:py:func:`!removed_func`` 防止不存在的引用报错

## 注释

```rst
.. 这是一条注释，不会出现在渲染输出中。

..
   这是多行注释。
   第二行。
   第三行。
```

## 替换

替换类似于宏，可以在全文中复用：

```rst
我使用 |sphinx-version| 版本。

.. |sphinx-version| replace:: 9.1.1
```

在 `conf.py` 中使用 `rst_prolog` 或 `rst_epilog` 定义全局替换：

```python
rst_epilog = """
.. |python| replace:: Python
.. |sphinx| replace:: Sphinx
"""
```

## 脚注与引用

```rst
Sphinx最初为Python官方文档创建 [#f1]_ 。

.. rubric:: 脚注

.. [#f1] Georg Brandl于2008年创建了Sphinx。
```

文献引用：

```rst
Knuth的文学编程 [Knuth1984]_ 影响了文档工具的设计。

.. [Knuth1984] Donald E. Knuth, "Literate Programming", 1984.
```

## 快速检查清单

编写 reST 文档时的常见注意事项：

- [ ] 段落之间用空行分隔
- [ ] 代码块正确缩进（相对于指令至少3空格或与指令内容对齐）
- [ ] 列表嵌套前后有空行
- [ ] 行内标记没有嵌套、没有前后空白
- [ ] 指令末尾的 `::` 后面有空行
- [ ] 交叉引用标签名全局唯一
- [ ] 标题下划线长度 ≥ 标题文本长度
- [ ] toctree 中引用的文件路径正确（相对路径，不含 `.rst` 后缀）

## 相关概念

- [Markdown/MyST 支持](19-markdown-and-myst.md)
- [交叉引用完全指南](20-cross-references-guide.md)
- [5分钟快速上手](01-getting-started.md)
- [Domain领域系统](09-domain-system.md)
