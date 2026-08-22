---
type: Example
title: TryExamples 基础：为代码示例添加交互按钮
description: 使用 try_examples 指令将 doctest 格式的代码示例转为可在 JupyterLite 中运行的 Notebook
tags: [example, try-examples, doctest, interactive]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-02-22
sources:
  - id: main
    resource: /references/main-source.md
    title: 核心模块源码
  - id: try-examples
    resource: /references/try-examples-source.md
    title: _try_examples模块源码
---

本示例演示如何手动使用 `.. try_examples::` 指令，将文档中 doctest（文档测试）格式的代码示例自动转换为可在 JupyterLite 中交互式运行的 Notebook。doctest 是 Python 标准的文档示例格式（`>>>` 开头表示代码行，`...` 表示续行，后续行表示预期输出），TryExamples 能够解析这种格式并生成对应的 Notebook 文件，读者点击按钮即可在浏览器中运行这些代码。

## 项目结构

```
my-docs/
├── conf.py
├── index.rst
└── _build/
```

## conf.py 配置

手动使用 `try_examples` 指令时，最简配置只需添加扩展：

```python
# conf.py

project = 'TryExamples Demo'
copyright = '2026, Your Name'
author = 'Your Name'
release = '0.1'

extensions = [
    'jupyterlite_sphinx',
]

html_theme = 'alabaster'
```

## 基础用法

在 RST 文件中使用 `.. try_examples::` 指令，指令内容为 doctest 格式的代码示例。指令选项包括 `:button_text:`、`:warning_text:`、`:height:` 和 `:example_class:`（主题类名）：

```rst
TryExamples 基础示例
====================

下面是一个简单的加法函数及其 doctest 示例：

.. try_examples::
   :button_text: 在 JupyterLite 中运行
   :warning_text: 注意：这是一个交互式示例，代码将在浏览器中执行。
   :height: 500px

   Add two numbers together.

   >>> x = 2
   >>> y = 3
   >>> x + y
   5

   You can also use loops:

   >>> total = 0
   >>> for i in range(1, 6):
   ...     total += i
   >>> total
   15
```

构建后，这段内容会在文档中以两种视图呈现：

1. **示例视图**（默认显示）：显示原始的 doctest 格式文本，附带一个 "在 JupyterLite 中运行" 按钮
2. **Notebook 视图**（点击按钮后显示）：在 iframe 中嵌入 JupyterLite Notebook，代码已按单元格组织好，读者可以运行、修改和编辑

点击按钮后，示例内容区域会被隐藏，JupyterLite iframe 会显示在下方。Notebook 视图还提供 "Go Back"（返回示例视图）和 "Open In Tab"（在新标签页中打开）按钮。

## doctest 格式规则

`.. try_examples::` 指令内容遵循标准 doctest 格式，由 `examples_to_notebook()` 函数（在 `_try_examples.py` 中）解析。核心解析规则如下：

- **`>>>` 开头的行**：代码行，去掉 `>>> ` 前缀后作为 Python 代码
- **`...` 开头的行**：多行代码的续行（如函数定义、循环体），去掉 `... ` 前缀后追加到当前代码块
- **空行**：表示当前代码块结束
- **其他非空行（在代码块之后）**：视为代码的预期输出文本，存储在单元格的输出中
- **非代码行（在 `>>>` 之前或代码块之间）**：视为 Markdown 文本，转换为 Markdown 单元格
- **`.. plot::` 和 `.. only::` 指令**：其下缩进的内容会被忽略，不会出现在生成的 Notebook 中

### 多行代码示例

```rst
.. try_examples::
   :button_text: 运行示例

   Define a function and call it:

   >>> def greet(name):
   ...     \"\"\"Generate a greeting message.\"\"\"
   ...     return f"Hello, {name}!"
   ...
   >>> greet("World")
   'Hello, World!'
   >>> greet("JupyterLite")
   'Hello, JupyterLite!'
```

注意函数定义和函数体之间的空行——在 doctest 中，空行后的 `...` 续行表示函数体仍在继续。

## 自定义按钮文本和警告

通过 `:button_text:` 和 `:warning_text:` 选项自定义交互按钮和警告信息：

```rst
.. try_examples::
   :button_text: 🚀 交互式运行
   :warning_text: ⚠️ 此示例需要浏览器支持 WebAssembly，首次加载可能需要一些时间。
   :height: 600px

   >>> import math
   >>> math.sqrt(16)
   4.0
   >>> math.factorial(10)
   3628800
```

- `:button_text:`：设置按钮上显示的文本，默认为全局配置 `try_examples_global_button_text` 的值，若未设置全局配置则默认为 "Try it with JupyterLite!"
- `:warning_text:`：在生成的 Notebook 顶部添加一个警告 Markdown 单元格（使用 `alert alert-warning` CSS 类），用于提示读者注意事项。默认为全局配置 `try_examples_global_warning_text` 的值
- `:height:`：设置 iframe 的高度，支持 CSS 单位（如 `500px`），未设置时由 JupyterLite 默认高度决定

## 自定义主题样式

使用 `:example_class:` 选项为整个 TryExamples 容器添加自定义 CSS 类，便于通过 CSS 定制样式：

```rst
.. try_examples::
   :button_text: 运行
   :example_class: dark-theme

   >>> print("Styled example")
   Styled example
```

`:example_class:` 默认值为全局配置 `try_examples_global_theme`（未设置时为空字符串）。你可以通过自定义 CSS 文件为该类设置样式。

## LaTeX 和链接自动转换

TryExamples 解析器自动处理 Sphinx 中的 LaTeX 数学标记和交叉引用链接，将它们转换为 Notebook 中的对应格式：

### LaTeX 数学公式

- **行内公式**：`:math:`x + y = 4`` 自动转换为 `$x + y = 4$`（Notebook 中的 Markdown 数学公式）
- **块级公式**：`.. math::` 指令及其缩进内容自动转换为 `$$ ... $$` 块级数学公式

```rst
.. try_examples::
   :button_text: 运行数学示例

   Inline LaTeX like :math:`x + y = 4` will be rendered correctly.

   Block LaTeX:

   .. math::

       \sum_{i=1}^{n} i = \frac{n(n+1)}{2}

   >>> n = 100
   >>> n * (n + 1) // 2
   5050
```

### Sphinx 链接

Sphinx 风格的链接（`link text <url>`_）自动转换为 Markdown 格式的链接（`[link text](url)`），使链接在 Notebook 的 Markdown 单元格中正常工作。引用标识符（如 `[R4c2dbc17006a-1]_`）会被简化为数字引用。

## 字面量块处理

doctest 内容中的 `::` 字面量块标记会被自动处理：以 `::` 结尾的行会被去掉末尾的 `::`，后续缩进行会被包裹在 Markdown 代码围栏（```）中，确保在 Notebook 中正确显示为代码块。

## 工作原理

当你在文档中使用 `.. try_examples::` 指令时，构建过程中发生以下操作：

1. **内容解析**：`examples_to_notebook()` 函数解析指令内容中的 doctest 格式文本，区分 Markdown 文本、代码块和输出文本
2. **Notebook 生成**：将解析结果转换为 Jupyter Notebook 格式（`.ipynb` JSON），代码行放入代码单元格，文本放入 Markdown 单元格，输出文本放入单元格的 `execute_result` 输出
3. **文件保存**：生成的 Notebook 以 UUID 命名（如 `a1b2c3d4_e5f6_...ipynb`），保存到 `_contents/` 目录
4. **HTML 渲染**：在 HTML 输出中，渲染为包含原始示例内容和交互按钮的容器，以及一个初始隐藏的 iframe 容器
5. **前端交互**：`jupyterlite_sphinx.js` 提供 JavaScript 函数 `tryExamplesShowIframe()` 和 `tryExamplesHideIframe()`，处理按钮点击后的视图切换

## 完整 index.rst 示例

```rst
TryExamples 演示文档
====================

基础计算示例：

.. try_examples::
   :button_text: 尝试运行
   :height: 400px

   Basic arithmetic operations.

   >>> a = 10
   >>> b = 3
   >>> a + b
   13
   >>> a * b
   30
   >>> a / b
   3.3333333333333335

列表推导式示例：

.. try_examples::
   :button_text: 运行列表示例
   :warning_text: 此示例展示列表推导式用法。
   :height: 500px

   List comprehensions in Python.

   >>> squares = [x**2 for x in range(10)]
   >>> squares
   [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

   >>> even_squares = [x**2 for x in range(10) if x % 2 == 0]
   >>> even_squares
   [0, 4, 16, 36, 64]
```

## 相关概念

- [TryExamples 指令详解](/concepts/08-try-examples-directive.md)
- [_try_examples 模块源码](/references/try-examples-source.md)
- [与 autodoc 集成](/examples/autodoc-integration.md)
- [指令系统总览](/concepts/03-directive-overview.md)
- [核心模块源码](/references/main-source.md)
