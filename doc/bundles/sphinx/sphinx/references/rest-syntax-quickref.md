---
type: "reference"
title: "reStructuredText 语法速查"
description: "reStructuredText（reST）常用语法速查表——段落、行内标记、列表、代码块、表格、链接、指令、角色等"
tags: [rest, syntax, reference, markup]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T10:30:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: "rst-primer", resource: "https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html", title: "Sphinx reStructuredText Primer" }
  - { id: "rst-ref", resource: "https://docutils.sourceforge.io/rst.html", title: "reStructuredText User Documentation" }
---

# reStructuredText 语法速查

本文档基于 Sphinx 官方 reST Primer 整理，提供常用 reST 语法的速查参考。

## 段落与换行

- 段落由空行分隔，同一段落的行必须左对齐到相同缩进级别
- 缩进在 reST 中与 Python 一样有意义
- 行块（保留换行）使用 `|` 前缀：
  ```rst
  | 这些行会
  | 精确按照
  | 源文件中的方式换行
  ```

## 行内标记

| 语法 | 效果 | 说明 |
|------|------|------|
| `*斜体*` | *斜体* | 强调 |
| `**粗体**` | **粗体** | 强强调 |
| `` ``代码`` `` | `代码` | 行内代码 |

注意事项：
- 行内标记**不可嵌套**
- 内容不能以空白开头或结尾（`* text*` 是错误的）
- 必须被非单词字符包围（可用反斜杠转义空格解决：`this\ *is*\ one\ word`）

## 列表

### 无序列表

```rst
* 项目一
* 项目二（跨行
  需要缩进）
```

### 有序列表

```rst
1. 第一项
2. 第二项

#. 自动编号项一
#. 自动编号项二
```

### 定义列表

```rst
术语（最多一行文本）
   术语的定义，必须缩进

   可以包含多个段落

下一个术语
   描述
```

### 嵌套列表

嵌套列表必须与父列表项之间用空行分隔：

```rst
* 父列表项一

  * 嵌套列表项一
  * 嵌套列表项二

* 父列表项二
```

## 代码块

### 字面块（使用 `::`）

```rst
这是普通段落，下一段是代码示例::

   这里是代码
   缩进的内容不会被处理
```

### 代码块指令（推荐）

```rst
.. code-block:: python

   def hello():
       print("Hello, Sphinx!")
```

支持语言高亮：python, javascript, c, cpp, java, ruby, bash, rst, yaml, json 等。

### 行内代码

```rst
使用 ``sphinx-build`` 命令构建文档。
```

## 链接

### 外部链接

```rst
`链接文本 <https://example.com>`_

`Sphinx <https://www.sphinx-doc.org/>`_ 是优秀的文档工具。
```

### 内部引用标签

```rst
.. _my-label:

某个章节标题
------------

参见 :ref:`my-label` 获取更多信息。
```

### 自动标题链接

```rst
参见 `某个章节标题`_ （直接引用标题文本，但不跨文件工作）
```

## 表格

### 网格表格

```rst
+------------+------------+-----------+
| 表头1      | 表头2      | 表头3     |
+============+============+===========+
| 单元格     | 单元格     | 单元格    |
+------------+------------+-----------+
```

### 简单表格

```rst
=====  =====  =======
A      B      A and B
=====  =====  =======
False  False  False
True   False  False
False  True   False
True   True   True
=====  =====  =======
```

### CSV表格

```rst
.. csv-table:: 表格标题
   :header: "姓名", "年龄", "城市"
   :widths: 20, 10, 20

   "张三", 28, "北京"
   "李四", 32, "上海"
```

## 图片

```rst
.. image:: /_static/logo.png
   :width: 200px
   :alt: Logo图片
   :align: center
```

## 标题层级

Sphinx 推荐的标题层级（下划线/上划线符号）：

```rst
=========
一级标题（#或=，带overline）
=========

二级标题（=）
==========

三级标题（-）
----------

四级标题（^）
^^^^^^^^^^

五级标题（"）
""""""""""
```

实际上 reST 不强制特定符号，只要同一层级使用一致的符号即可。

## 注释

```rst
.. 这是一条注释，不会出现在输出中

..
   多行注释
   第二行
   第三行
```

## 指令（Directives）

指令是 reST 的扩展机制，格式为 `.. 指令名:: 参数`：

### 警告/提示框

```rst
.. note::

   这是一条提示信息。

.. warning::

   这是一条警告信息。

.. important:: 标题可以写在同一行

   重要提示内容。

.. seealso::

   参见 :doc:`其他文档`
```

### 文档树（toctree）

```rst
.. toctree::
   :maxdepth: 2
   :caption: 目录

   intro
   usage/index
   api/index
```

### 版本标记

```rst
.. versionadded:: 2.0
   新增了某个功能。

.. versionchanged:: 3.0
   修改了某个行为。

.. deprecated:: 4.0
   此功能已废弃，请使用新API替代。
```

### 数学公式

```rst
.. math::

   E = mc^2

行内数学: :math:`a^2 + b^2 = c^2`
```

### 脚注

```rst
这是正文 [#f1]_ ，带有脚注。

.. rubric:: 脚注

.. [#f1] 脚注内容。
```

### 文献引用

```rst
本文参考了 [Knuth1984]_ 的研究。

.. rubric:: 参考文献

.. [Knuth1984] Donald E. Knuth, "Literate Programming", 1984.
```

## 角色（Roles）

角色用于行内标记，格式为 `:角色名:`内容``：

```rst
:py:func:`print`          — Python函数引用
:py:class:`list`          — Python类引用
:py:mod:`os.path`         — Python模块引用
:ref:`my-label`           — 交叉引用标签
:doc:`/other-doc`         — 引用其他文档
:download:`/files/data.csv` — 下载链接
:term:`Sphinx`            — 术语表引用
:command:`sphinx-build`   — 命令名
:file:`conf.py`           — 文件名
:kbd:`Ctrl+C`             — 键盘按键
:mail:`dev@example.com`   — 邮件地址
```

## 替换与宏

```rst
在 conf.py 的 rst_epilog 中定义全局替换：

.. |python| replace:: Python
.. |sphinx-version| replace:: 9.1.1

然后在正文中使用：支持 |python| |sphinx-version|。
```

## 字段列表

常用于信息元数据（如Python文档的参数说明）：

```rst
:param name: 参数说明
:type name: str
:returns: 返回值说明
:rtype: int
:raises ValueError: 异常说明
```
