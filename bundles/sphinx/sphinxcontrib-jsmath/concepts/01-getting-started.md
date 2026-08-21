---
type: Concept
title: 5分钟快速上手
description: 安装 sphinxcontrib-jsmath、配置 conf.py、编写数学公式并构建 HTML 文档
tags: [sphinxcontrib-jsmath, getting-started, installation, configuration, sphinx]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jsmath-source
    resource: /references/jsmath-source.md
    title: sphinxcontrib-jsmath 源码信源登记
---

# 5分钟快速上手

## 安装

从 PyPI 安装 sphinxcontrib-jsmath：

```bash
pip install sphinxcontrib-jsmath
```

> **注意**：sphinxcontrib-jsmath 本身不依赖 Sphinx（避免循环依赖），但实际使用时需要已安装 Sphinx >= 5.0。安装 Sphinx 完整环境：`pip install sphinxcontrib-jsmath sphinx`。

你还需要获取 jsMath 的 JavaScript 文件和字体。jsMath 可以从 [jsMath 官网](http://www.math.union.edu/~dpvc/jsmath/) 下载，解压后将 `jsMath.js` 及相关字体文件放到你的文档静态资源目录中。

## 最小配置

在 Sphinx 项目的 `conf.py` 中添加扩展并配置 jsMath 路径：

```python
# conf.py
extensions = ['sphinxcontrib.jsmath']

# jsMath 脚本的路径（相对于 HTML 输出根目录，或绝对 URL）
jsmath_path = '/path/to/jsmath.js'
```

`jsmath_path` 是**唯一必须配置**的选项。它指向 jsMath 的 JavaScript 文件，可以是：

- 相对于 HTML 输出根目录的路径：如 `'_static/jsMath/easy/load.js'`
- 绝对 URL：如 `'https://example.com/jsmath.js'`
- CDN 地址（如果有托管）

> ⚠️ **重要**：如果未设置 `jsmath_path`（保持默认空字符串），构建时会抛出 `ExtensionError`，提示 "jsmath_path config value must be set for the jsmath extension to work"。

## 放置 jsMath 文件

将下载的 jsMath 文件放到 Sphinx 项目的 `_static/` 目录下，例如：

```
your-docs/
├── _static/
│   └── jsMath/
│       ├── easy/
│       │   └── load.js        # jsmath_path 指向此文件
│       ├── plugins/
│       └── fonts/
│           └── ...            # TeX 字体文件
├── conf.py
└── index.rst
```

然后在 `conf.py` 中配置：

```python
html_static_path = ['_static']
jsmath_path = '_static/jsMath/easy/load.js'
```

## 编写数学公式

配置完成后，就可以在 reStructuredText 文档中使用标准的数学标记了：

### 行内公式

使用 `` :math:`...` `` 角色插入行内公式：

```rst
质能方程 :math:`E = mc^2` 是爱因斯坦的著名公式。
```

### 块级公式

使用 `.. math::` 指令插入块级公式：

```rst
.. math::

   E = mc^2
```

### 带标签的公式（可引用）

使用 `:label:` 选项给公式添加标签，以便在文档中交叉引用：

```rst
.. math::
   :label: pythagorean

   a^2 + b^2 = c^2

根据勾股定理 :eq:`pythagorean`，直角三角形两直角边的平方和等于斜边的平方。
使用 :math:numref:`pythagorean` 可以生成带编号的引用。
```

### 多行长公式（split 环境）

对于多行对齐的公式，使用 `\\` 分隔行、`&` 标记对齐位置。jsmath 扩展会自动检测 `&` 或 `\\` 并包裹 `\begin{split}...\end{split}`：

```rst
.. math::

   (a + b)^2 &= (a + b)(a + b) \\
             &= a^2 + 2ab + b^2
```

## 构建 HTML

```bash
sphinx-build -b html . _build/html
```

构建成功后，打开 `_build/html/index.html`，数学公式应该由 jsMath 渲染为美观的数学排版。

## 验证安装

构建完成后，可以检查 HTML 源码确认扩展工作正常：

1. 页面 `<head>` 中应包含 `<script src="/path/to/jsmath.js"></script>`
2. 数学公式应被包裹在 `<span class="math notranslate nohighlight">` 或 `<div class="math notranslate nohighlight">` 中
3. 带标签的公式应有 `id="equation-<label>"` 属性和 `eqno` 编号

## 常见配置选项

sphinxcontrib-jsmath 本身只提供一个配置项 `jsmath_path`。其他数学相关的配置项由 Sphinx 核心提供：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `jsmath_path` | `''` | jsMath 脚本路径（**必须设置**） |
| `math_number_all` | `False` | 是否为所有块级公式编号（默认仅带标签的编号） |
| `math_eqref_format` | `None` | 公式引用格式，如 `'Eq. {number}'` |
| `numfig` | `False` | 是否启用数字编号（影响公式编号格式） |
| `math_numfig` | `True` | 公式编号是否使用 `章号.序号` 格式（需 `numfig=True`） |

## 相关概念

- [sphinxcontrib-jsmath 简介](/concepts/00-introduction.md)
- [扩展注册与 setup 函数](/concepts/02-setup-and-registration.md)
- [基础使用示例](/examples/basic-usage.md)
- [常见问题排查](/examples/troubleshooting.md)
