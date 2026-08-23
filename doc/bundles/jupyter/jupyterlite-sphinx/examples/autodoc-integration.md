---
type: Example
title: 与 sphinx.ext.autodoc 集成
description: 配置 global_enable_try_examples 为所有 autodoc 文档的 Examples 段自动添加交互按钮
tags: [example, autodoc, numpydoc, napoleon, automation]
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

本示例演示如何将 jupyterlite-sphinx 的 TryExamples 功能与 `sphinx.ext.autodoc` 自动文档生成集成。启用 `global_enable_try_examples` 配置后，所有通过 autodoc 从 Python 代码 docstring（文档字符串）中提取的 Examples（示例）段落都会自动被包裹在 `.. try_examples::` 指令中，读者无需手动添加指令即可在 JupyterLite 中交互运行文档中的代码示例。此功能需要配合 numpydoc 或 sphinx.ext.napoleon 扩展来正确识别 docstring 的 Examples 段落。

## 项目结构

```
my-docs/
├── conf.py
├── index.rst
├── mypackage/                # 你的 Python 包
│   ├── __init__.py
│   └── utils.py              # 包含带 Examples 段的 docstring
├── try_examples.json         # 运行时配置文件（可选）
└── _build/
```

## Python 源码准备

首先确保你的 Python 代码中使用了标准 docstring 格式，并在 Examples 段中编写了 doctest 风格的示例代码。以下是两种主流格式的示例。

### NumPy 风格 docstring

```python
# mypackage/utils.py

def add(a, b):
    """Add two numbers together.

    Parameters
    ----------
    a : int or float
        The first number.
    b : int or float
        The second number.

    Returns
    -------
    int or float
        The sum of a and b.

    Examples
    --------
    >>> add(2, 3)
    5
    >>> add(1.5, 2.5)
    4.0
    >>> add(-1, 1)
    0
    """
    return a + b


def fibonacci(n):
    """Generate the first n Fibonacci numbers.

    Parameters
    ----------
    n : int
        Number of Fibonacci numbers to generate.

    Returns
    -------
    list
        A list containing the first n Fibonacci numbers.

    Examples
    --------
    >>> fibonacci(1)
    [0]
    >>> fibonacci(10)
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    """
    if n <= 0:
        return []
    result = [0]
    if n == 1:
        return result
    result.append(1)
    for i in range(2, n):
        result.append(result[-1] + result[-2])
    return result
```

### Google 风格 docstring（配合 sphinx.ext.napoleon）

```python
# mypackage/utils.py

def multiply(a, b):
    """Multiply two numbers.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The product of a and b.

    Examples:
        >>> multiply(4, 5)
        20
        >>> multiply(3.14, 2)
        6.28
    """
    return a * b
```

## conf.py 完整配置

启用全局 TryExamples 需要在 conf.py 中进行以下配置：

```python
# conf.py

import os
import sys

# 将你的包路径添加到 Python 路径，使 autodoc 能找到模块
sys.path.insert(0, os.path.abspath('.'))

project = 'Autodoc Integration Demo'
copyright = '2026, Your Name'
author = 'Your Name'
release = '0.1'

extensions = [
    'sphinx.ext.autodoc',       # 自动从 docstring 生成文档
    'sphinx.ext.napoleon',      # 支持 Google/NumPy 风格 docstring（二选一）
    # 'numpydoc',               # 或者使用 numpydoc 扩展
    'jupyterlite_sphinx',       # jupyterlite-sphinx 扩展
]

html_theme = 'alabaster'

# ========== TryExamples 全局配置 ==========

# 核心开关：为所有 autodoc 生成的 Examples 段自动添加交互按钮
global_enable_try_examples = True

# 全局按钮文本（所有 Examples 段共享，可被单独指令覆盖）
try_examples_global_button_text = "在 JupyterLite 中运行此示例"

# 全局警告文本（在每个生成的 Notebook 顶部显示）
try_examples_global_warning_text = (
    "⚠️ 此示例在浏览器中通过 JupyterLite (Pyodide/WASM) 执行，"
    "部分依赖 C 扩展的包可能不可用。"
)

# 全局主题 CSS 类（自定义样式）
try_examples_global_theme = ""  # 留空使用默认样式，或设置自定义类名

# 全局预导代码（preamble）：在每个 Notebook 的警告单元格之后插入一段代码
# 常用于统一导入、设置 matplotlib 后端等
try_examples_preamble = """
import numpy as np
import matplotlib.pyplot as plt
"""

# ========== 其他 jupyterlite-sphinx 配置 ==========

# REPL 相关配置（TryExamples 底层使用 notebooklite/tree 视图）
jupyterlite_silence = True  # 静默 JupyterLite 构建输出
jupyterlite_bind_ipynb_suffix = True  # 绑定 .ipynb 后缀
```

### 关键配置项说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `global_enable_try_examples` | `bool` | `False` | **核心开关**。设为 `True` 时，autodoc 处理 docstring 的 Examples 段会自动插入 `.. try_examples::` 指令 |
| `try_examples_global_button_text` | `str` 或 `None` | `None`（使用 "Try it with JupyterLite!"） | 所有自动生成按钮的默认文本 |
| `try_examples_global_warning_text` | `str` 或 `None` | `None` | 所有自动生成 Notebook 顶部的警告文本 |
| `try_examples_global_theme` | `str` 或 `None` | `None`（空字符串） | 所有 TryExamples 容器的 CSS 类名 |
| `try_examples_preamble` | `str` 或 `None` | `None` | 每个生成的 Notebook 中，在警告单元格之后插入的代码单元格内容 |

## 工作机制

当 `global_enable_try_examples = True` 时，`conditional_process_examples()` 函数（源码第1007-1010行）会连接两个 Sphinx 事件：

1. **`source-read` 事件**：连接 `_process_docstring_examples()`，处理 `.py` 源文件中嵌入的文档
2. **`autodoc-process-docstring` 事件**：连接 `_process_autodoc_docstrings()`，处理 autodoc 提取的 docstring

在 `autodoc-process-docstring` 回调中，`insert_try_examples_directive()` 函数执行以下操作：

1. **查找 Examples 段**：使用正则表达式匹配 `.. rubric:: Examples`（numpydoc 生成）或 `.. admonition:: Examples`（sphinx.ext.napoleon 生成）
2. **检查禁用标记**：如果 Examples 段的第一行内容是 `.. disable_try_examples`，则跳过该段
3. **检查已有指令**：如果 Examples 段已包含 `.. try_examples::` 指令，则不重复插入
4. **查找段结束位置**：通过匹配下一个段落标题（如 Notes、References、Parameters、Returns 等）确定 Examples 段的边界
5. **插入指令**：在 Examples 段内容前插入 `.. try_examples::` 指令，并将段内所有内容缩进4个空格，使其成为指令的内容

## RST 文档：使用 automodule/autofunction

在 RST 文件中使用标准的 autodoc 指令即可，无需手动添加 `.. try_examples::`：

```rst
API 文档
========

.. automodule:: mypackage.utils
   :members:
   :undoc-members:
   :show-inheritance:
```

构建后，每个函数的 Examples 段会自动带有交互按钮，效果与手动添加 `.. try_examples::` 指令完全一致。

## 禁用特定 Examples 段

有时你可能不希望某个 Examples 段被转换为交互式 Notebook（例如依赖无法在浏览器中运行的 C 扩展包）。在 docstring 的 Examples 段开头添加 `.. disable_try_examples` 注释即可禁用：

```python
def c_extension_function(data):
    """Process data using a C extension.

    Examples
    --------
    .. disable_try_examples

    >>> import c_extension_package  # This won't work in JupyterLite
    >>> result = c_extension_package.process(data)
    """
    pass
```

`insert_try_examples_directive()` 函数在检测到 `.. disable_try_examples` 注释后，会直接返回原始 docstring 行，不插入 try_examples 指令。该 Examples 段将以普通文本形式显示，不带交互按钮。

## try_examples.json 运行时配置

jupyterlite-sphinx 支持一个名为 `try_examples.json` 的运行时配置文件，放置在 Sphinx 源目录（与 conf.py 同级）中。该文件在构建时被复制到 HTML 输出目录，前端 JavaScript 在页面加载时读取它，允许在**不重新构建文档**的情况下调整 TryExamples 的行为。

### 配置文件示例

```json
{
    "global_min_height": "500px",
    "ignore_patterns": [
        ".*deprecated.*",
        ".*internal.*"
    ]
}
```

### 配置项说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `global_min_height` | `string` | 所有 TryExamples iframe 的最小高度（CSS 长度值），覆盖构建时设置的高度 |
| `ignore_patterns` | `array of string` | 正则表达式模式数组，匹配到这些模式的 TryExamples 容器将被隐藏/禁用按钮 |

`try_examples.json` 的加载由 `jupyterlite_sphinx.js` 中的 `loadTryExamplesConfig()` 函数处理，在 `DOMContentLoaded` 事件触发时通过相对路径（自动计算从当前页面到文档根的相对路径）加载。这意味着你可以在部署后修改此 JSON 文件来调整交互行为，无需重新运行 `sphinx-build`。

## 构建与查看

```bash
sphinx-build -b html . _build/html
```

构建完成后，使用 HTTP 服务器查看：

```bash
cd _build/html
python -m http.server 8000
```

访问 `http://localhost:8000`，你会看到每个 autodoc 生成的函数/类文档的 Examples 段都带有一个"在 JupyterLite 中运行此示例"按钮。点击按钮后，doctest 代码被转换为 Notebook 单元格，读者可以在 JupyterLite 中直接运行和修改代码。

## 注意事项

1. **必须使用 numpydoc 或 napoleon**：`global_enable_try_examples` 通过匹配 numpydoc/napoleon 生成的 `.. rubric:: Examples` 或 `.. admonition:: Examples` 标记来定位 Examples 段。纯 RST 手写的文档（不通过这两个扩展处理）不会被自动转换
2. **doctest 格式要求**：Examples 段中的代码必须遵循 doctest 格式（`>>>` 前缀代码行，`...` 续行，空行分隔代码块，后续行为输出），否则解析可能出错
3. **内核兼容性**：JupyterLite 使用 Pyodide（WebAssembly Python），不支持依赖 C/Fortran 扩展的包（如部分版本的 pandas、scipy 等），对于这类代码示例应使用 `.. disable_try_examples` 禁用
4. **preamble 代码**：`try_examples_preamble` 中的代码会插入到每个自动生成的 Notebook 中，适合放置全局导入语句。注意这段代码会在所有 Notebook 中执行，避免放置耗时过长的操作

## 相关概念

- [TryExamples 指令详解](/concepts/08-try-examples-directive.md)
- [_try_examples 模块源码](/references/try-examples-source.md)
- [TryExamples 基础用法](/examples/try-examples-basic.md)
- [配置参考](/references/config-reference.md)
- [核心模块源码](/references/main-source.md)
- [指令系统总览](/concepts/03-directive-overview.md)
