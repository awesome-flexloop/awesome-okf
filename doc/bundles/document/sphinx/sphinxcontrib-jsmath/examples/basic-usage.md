---
type: Example
title: 基础使用示例
description: 从零配置 sphinxcontrib-jsmath 项目、编写各类数学公式、构建并验证 HTML 输出
tags: [sphinxcontrib-jsmath, example, basic, setup, math-formulas]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jsmath-source
    resource: /references/jsmath-source.md
    title: sphinxcontrib-jsmath 源码信源登记
---

# 基础使用示例

本示例演示如何从零开始配置一个使用 sphinxcontrib-jsmath 渲染数学公式的 Sphinx 项目。

## 前置条件

- Python >= 3.9
- Sphinx >= 5.0
- sphinxcontrib-jsmath 扩展
- jsMath JavaScript 文件和字体

## 步骤1：创建 Sphinx 项目

```bash
# 创建项目目录
mkdir my-math-docs && cd my-math-docs

# 使用 sphinx-quickstart 初始化（或手动创建）
sphinx-quickstart --sep -p "Math Docs" -a "Author" -r "1.0" -l en
```

## 步骤2：安装扩展

```bash
pip install sphinxcontrib-jsmath
```

## 步骤3：下载 jsMath

从 [jsMath 官网](http://www.math.union.edu/~dpvc/jsmath/) 下载 jsMath 压缩包，解压到 `_static/jsMath/` 目录：

```
my-math-docs/
├── _static/
│   └── jsMath/
│       ├── easy/
│       │   └── load.js       # jsMath 加载器
│       ├── plugins/
│       ├── fonts/
│       │   ├── cmsy10/
│       │   ├── cmr10/
│       │   └── ...           # TeX 字体文件
│       └── jsmath.js         # jsMath 核心
├── source/
│   ├── conf.py
│   └── index.rst
└── Makefile
```

> **提示**：jsMath 的 `easy/load.js` 是最简单的自动加载方式，它会自动加载必要的插件和字体。

## 步骤4：配置 conf.py

编辑 `source/conf.py`，添加扩展和 jsMath 路径配置：

```python
# source/conf.py

# 添加扩展
extensions = [
    'sphinxcontrib.jsmath',
]

# jsMath 脚本路径（相对于 HTML 输出根目录）
jsmath_path = '_static/jsMath/easy/load.js'

# 静态文件路径
html_static_path = ['_static']

# （可选）为所有公式启用编号
# math_number_all = True

# （可选）公式引用格式
# math_eqref_format = '式 ({number})'
```

## 步骤5：编写包含数学公式的文档

创建 `source/math.rst`：

```rst
数学公式示例
============

行内公式
--------

勾股定理表明，直角三角形斜边的平方等于两直角边平方之和：
:math:`a^2 + b^2 = c^2`。

著名的欧拉恒等式 :math:`e^{i\pi} + 1 = 0` 被称为"最美的数学公式"。

质能方程 :math:`E = mc^2` 揭示了质量与能量的等价关系。

块级公式
--------

一元二次方程的求根公式：

.. math::

   x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}

高斯积分：

.. math::

   \\int_{-\\infty}^{\\infty} e^{-x^2} \\, dx = \\sqrt{\\pi}

带标签的公式
------------

勾股定理（可引用）：

.. math::
   :label: pythagorean

   a^2 + b^2 = c^2

如式 :eq:`pythagorean` 所示，直角三角形三边满足这一关系。

多行对齐公式
------------

二项式展开：

.. math::

   (a + b)^2 &= a^2 + 2ab + b^2 \\\\
   (a + b)^3 &= a^3 + 3a^2b + 3ab^2 + b^3 \\\\
   (a + b)^4 &= a^4 + 4a^3b + 6a^2b^2 + 4ab^3 + b^4
```

更新 `source/index.rst` 包含 math 文档：

```rst
欢迎来到 Math Docs
==================

.. toctree::
   :maxdepth: 2

   math
```

## 步骤6：构建 HTML

```bash
sphinx-build -b html source build/html
```

## 步骤7：验证输出

打开 `build/html/math.html`，检查以下内容：

### 检查1：JS 文件是否加载

查看 HTML 源码（右键 → 查看页面源码），确认 `<head>` 中包含：

```html
<script src="_static/jsMath/easy/load.js"></script>
```

### 检查2：行内公式结构

行内公式应被渲染为：

```html
<span class="math notranslate nohighlight">a^2 + b^2 = c^2</span>
```

### 检查3：带标签的公式结构

带标签的块公式应包含编号和永久链接：

```html
<span class="eqno">(1)<a class="headerlink" href="#equation-pythagorean" title="Permalink to this equation">¶</a></span>
<div class="math notranslate nohighlight" id="equation-pythagorean">
a^2 + b^2 = c^2</div>
```

### 检查4：多行公式 split 环境

包含 `&` 或 `\\` 的公式应被 `\begin{split}...\end{split}` 包裹：

```html
<div class="math notranslate nohighlight">
\begin{split}(a + b)^2 &amp;= a^2 + 2ab + b^2 \\
   ...\end{split}</div>
```

> 注意：HTML 中 `&` 被编码为 `&amp;`，jsMath 会在解析时正确处理。

### 检查5：公式交叉引用

`:eq:\`pythagorean\`` 应生成指向公式的链接：

```html
<a class="reference internal" href="#equation-pythagorean">(1)</a>
```

## 常见问题

### Q: 构建报错 "jsmath_path config value must be set"

确保在 `conf.py` 中设置了 `jsmath_path`，且值不为空字符串。

### Q: 页面显示原始 LaTeX 代码而非渲染后的公式

检查：
1. `jsmath_path` 路径是否正确（在浏览器开发者工具的 Network 面板中确认 load.js 返回 200）
2. jsMath 字体文件是否正确放置
3. 浏览器 JavaScript 是否启用

### Q: 无公式页面没有加载 jsmath.js

这是正常行为！sphinxcontrib-jsmath 智能检测公式存在性，无公式的页面不加载 JS 文件。

## 相关概念

- [5分钟快速上手](../concepts/01-getting-started.md)
- [数学节点访问者](../concepts/03-math-node-visitors.md)
- [公式编号与引用示例](equation-numbering.md)
- [常见问题排查](troubleshooting.md)
