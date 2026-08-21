---
type: Example
title: 公式编号与引用
description: 配置公式自动编号、使用 numfig 章节编号、eq/numref 交叉引用、自定义编号格式
tags: [sphinxcontrib-jsmath, example, equation-numbering, numfig, cross-reference, labeling]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jsmath-source
    resource: /references/jsmath-source.md
    title: sphinxcontrib-jsmath 源码信源登记
---

# 公式编号与引用

本示例演示 sphinxcontrib-jsmath 中公式编号的各种配置方式，包括自动编号、章节编号、交叉引用和自定义格式。

## 基础编号方式

### 仅带标签的公式编号（默认）

默认情况下，只有带 `:label:` 选项的公式才会被编号：

```rst
.. math::
   :label: einstein

   E = mc^2

这个公式编号为 :eq:`einstein`。

.. math::

   这个公式没有标签，不会被编号。
```

输出中，带标签的公式会显示编号 `(1)`，无标签的公式无编号。

### 所有公式自动编号

设置 `math_number_all = True` 为所有块级公式自动编号：

```python
# conf.py
math_number_all = True
```

```rst
.. math::

   这个公式即使没有标签也会被编号。

.. math::
   :label: labeled-eq

   带标签的公式同样编号，且可被引用。
```

> **注意**：`math_number_all` 是 Sphinx 核心配置，不是 jsmath 扩展特有的。

## 章节编号格式（numfig）

默认编号是连续的 `(1), (2), (3)...`。启用 `numfig` 后，编号变为"章号.序号"格式 `(1.1), (1.2), (2.1)...`。

### 配置 numfig

```python
# conf.py
numfig = True
math_numfig = True  # 数学公式使用 numfig 编号格式（默认 True）
```

### numfig 效果

假设文档结构如下：

```rst
第一章（index.rst）
==================

.. math::
   :label: eq-ch1-a

   E = mc^2

.. math::
   :label: eq-ch1-b

   a^2 + b^2 = c^2

第二章（chapter2.rst）
=====================

.. math::
   :label: eq-ch2-a

   \\nabla \\cdot \\mathbf{E} = \\frac{\\rho}{\\epsilon_0}
```

编号结果：
- 第一章公式：`(1.1)`、`(1.2)`
- 第二章公式：`(2.1)`

这对应测试用例 `test_numfig_enabled` 验证的行为：

```python
assert '<span class="eqno">(1.1)...' in content  # 第一个公式
assert '<span class="eqno">(1.2)...' in content  # 第二个公式
```

### 禁用数学公式的 numfig 格式

如果希望在 `numfig=True` 的情况下数学公式仍使用连续编号：

```python
# conf.py
numfig = True
math_numfig = False  # 数学公式不使用章节编号
```

此时即使启用了 numfig，公式编号仍然是 `(1), (2), (3)...` 连续格式。

## 交叉引用方式

### :eq: 角色——引用公式编号

```rst
根据 :eq:`pythagorean`，直角三角形满足...
```

输出：`根据 (1)，直角三角形满足...`（或 numfig 模式下 `根据 (1.1)`）。

### :math:numref: 角色——带"公式"前缀的引用

```rst
如 :math:numref:`pythagorean` 所示...
```

`:math:numref:` 是数学域的 numref 角色，它根据 `math_eqref_format` 配置格式化输出。

### 自定义引用格式

通过 `math_eqref_format` 自定义公式引用的显示格式：

```python
# conf.py
math_eqref_format = '式 ({number})'
```

```rst
如 :eq:`einstein` 所示...
```

输出：`如 式 (1) 所示...`

`{number}` 占位符会被替换为实际编号。

## 完整示例项目

### conf.py 配置

```python
extensions = ['sphinxcontrib.jsmath']
jsmath_path = '_static/jsMath/easy/load.js'
html_static_path = ['_static']

# 编号配置
numfig = True
math_numfig = True
math_eqref_format = 'Eq.{number}'
```

### 文档源文件

```rst
经典力学公式
============

牛顿第二定律：

.. math::
   :label: newton-second

   \\mathbf{F} = m\\mathbf{a}

动能公式：

.. math::
   :label: kinetic-energy

   E_k = \\frac{1}{2}mv^2

如 :eq:`newton-second` 所示，力等于质量乘以加速度。
动能由 :math:numref:`kinetic-energy` 给出。

电磁学公式
==========

麦克斯韦方程组——高斯定律：

.. math::
   :label: gauss-law

   \\nabla \\cdot \\mathbf{E} = \\frac{\\rho}{\\epsilon_0}
```

### 预期输出

| 公式 | 编号（numfig模式） | 引用输出 |
|------|-------------------|---------|
| newton-second | (1.1) | `Eq.1.1` |
| kinetic-energy | (1.2) | `Eq.1.2` |
| gauss-law | (2.1) | `Eq.2.1` |

## HTML 输出结构详解

### 有编号的公式

```html
<span class="eqno">(1.1)<a class="headerlink" href="#equation-newton-second"
      title="Permalink to this equation">¶</a></span>
<div class="math notranslate nohighlight" id="equation-newton-second">
\mathbf{F} = m\mathbf{a}</div>
```

关键元素：
- `<span class="eqno">` 包裹编号和永久链接
- `(1.1)` 是公式编号文本
- `<a class="headerlink">` 是 ¶ 永久链接
- `<div id="equation-newton-second">` 提供锚点目标
- `id` 格式为 `equation-<label>`，其中 label 是 `:label:` 选项的值

### 无编号的公式

```html
<div class="math notranslate nohighlight">
公式内容</div>
```

无 `eqno` span，无 `id` 属性。

### 交叉引用链接

```html
<a class="reference internal" href="#equation-newton-second">Eq.1.1</a>
```

链接 `href` 指向公式的 `id` 锚点。

## 编号获取机制

公式编号由 Sphinx 的 `get_node_equation_number` 工具函数生成：

```python
from sphinx.util.math import get_node_equation_number

number = get_node_equation_number(self, node)
```

这个函数：
1. 从 MathDomain 获取公式的序号
2. 如果 `numfig=True` 且 `math_numfig=True`，格式化为"章号.序号"
3. 否则使用简单的连续数字
4. 应用 `math_eqref_format` 格式化（如果已配置）

sphinxcontrib-jsmath 在 `html_visit_displaymath` 中调用此函数获取编号字符串，然后包裹在 `<span class="eqno">` 中输出。

## 相关概念

- [数学节点访问者](/concepts/03-math-node-visitors.md)
- [智能JS加载机制](/concepts/04-smart-js-loading.md)
- [基础使用示例](/examples/basic-usage.md)
- [常见问题排查](/examples/troubleshooting.md)
