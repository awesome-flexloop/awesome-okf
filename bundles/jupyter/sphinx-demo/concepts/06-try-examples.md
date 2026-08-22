---
type: Concept
title: TryExamples 交互示例系统
description: TryExamples 功能的工作原理、三级控制粒度、按钮定制和使用注意事项
tags: [try-examples, interactivity, docstring, autodoc, button]
difficulty: intermediate
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: try-examples
    resource: /references/conf-py-source.md
    title: TryExamples 配置与示例代码
---

## 什么是 TryExamples

TryExamples 是 jupyterlite-sphinx 提供的一项核心功能：它在文档的代码示例旁边自动添加"Try it online"按钮，读者点击后弹出嵌入式 JupyterLite REPL，可以直接在浏览器中修改和运行示例代码。

```
┌─────────────────────────────────────┐
│  fibonacci_sequence(n)              │
│  ─────────────────────              │
│  Generates the Fibonacci sequence  │
│  up to the nth term.                │
│                                     │
│  Examples                           │
│  >>> fibonacci_sequence(10)         │
│  [0, 1, 1, 2, 3, 5, 8, 13, 21, 34] │
│                                     │
│  ┌─────────────────────────────┐    │
│  │     🚀 Try it online!       │    │  ← TryExamples 按钮
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

点击按钮后，代码示例在嵌入式 JupyterLite iframe 中打开，用户可以直接编辑和运行。

## 工作原理

当 `global_enable_try_examples=True` 时：

1. Sphinx 构建过程中，`jupyterlite-sphinx` 的 `insert_try_examples_directive()` 函数在 autodoc 处理 docstring 后运行
2. 它扫描文档中的 `doctest` 代码块（`>>>` 格式的示例）
3. 对每个包含示例的代码块，自动在其后插入一个"Try it online"按钮
4. 按钮点击时，前端 JS 将代码示例注入到一个隐藏的 JupyterLite REPL iframe 中执行

TryExamples 按钮对应的指令是 `.. try_examples::`，但在全局模式下不需要手动添加。

## 三级控制粒度

TryExamples 提供从粗到细的三级控制：

### Level 1：全局开关（conf.py）

```python
global_enable_try_examples = True  # 全局开启
```

设置为 `False` 则关闭全局自动插入，只有手动添加 `.. try_examples::` 指令的位置才会显示按钮。

### Level 2：页面级排除（try_examples.json）

```json
{
  "ignore_patterns": ["disabled_examples\\/demo.html"]
}
```

`ignore_patterns` 是正则表达式数组，匹配的页面（相对于站点根的 URL 路径）不会显示任何 TryExamples 按钮。多个模式之间是"或"关系——只要匹配任一模式，该页面就不显示按钮。

```json
{
  "ignore_patterns": [
    "disabled_examples\\/demo.html",
    "api\\/internal\\/",
    ".*\\-draft\\.html"
  ]
}
```

> **注意**：正则中 `/` 需要转义为 `\\/`，`.` 需要转义为 `\\.`。

### Level 3：函数级禁用（docstring 注释）

在 docstring 的 Examples 节中添加 `.. disable_try_examples` 注释：

```python
def image_processing(image_path):
    """
    Apply filters to an image.

    Examples
    --------
    .. disable_try_examples

    >>> from PIL import Image
    >>> img = Image.open("example.jpg")  # 需要本地文件
    >>> processed = image_processing("example.jpg")
    """
```

> **重要**：`.. disable_try_examples` 不是 RST 指令（不需要 `::`），而是一个特殊注释标记。它不会在渲染后的文档中可见，仅被 jupyterlite-sphinx 内部检测到后跳过该函数的 TryExamples 按钮插入。

详细说明见 [10-disabling-examples](/concepts/10-disabling-examples.md)。

## 按钮外观定制

### 全局按钮文本

```python
try_examples_global_button_text = "在线运行此示例"
```

### 全局警告文本

```python
try_examples_global_warning_text = (
    "⚠️ 交互式示例是实验性功能，可能与原生 Jupyter 体验不同。"
)
```

### CSS 样式自定义

demo 通过 `_static/button_styling.css` 自定义按钮样式，添加了光泽悬停动画和圆角效果。你可以通过 CSS 选择器 `.try_examples_button` 来定制按钮外观：

```css
.try_examples_button {
    background-color: #f37726;  /* Jupyter 橙色 */
    color: white;
    border-radius: 8px;
    padding: 8px 16px;
    border: none;
    cursor: pointer;
}

.try_examples_button:hover {
    background-color: #e66a1b;
}
```

## iframe 高度控制

通过 try_examples.json 设置全局最小高度：

```json
{
  "global_min_height": "400px"
}
```

支持所有 CSS 长度单位：`px`、`vh`、`em`、`rem` 等。建议使用 `px` 以确保跨设备一致性。

## 预导入代码

可以通过 `try_examples_preamble` 在每个示例前自动插入预导入代码：

```python
try_examples_preamble = """
import numpy as np
import matplotlib.pyplot as plt
"""
```

这样用户在 TryExamples REPL 中无需手动导入 numpy 和 matplotlib。

## 使用注意事项

1. **不要依赖本地文件**：TryExamples 在浏览器中运行，无法访问用户本地文件系统。涉及文件 I/O 的示例应禁用 TryExamples。
2. **长耗时计算慎用**：浏览器中 WASM 执行速度比原生 Python 慢，长耗时计算会导致页面卡顿。
3. **piplite 异步安装**：如果示例需要额外包，使用 `await piplite.install("package-name")`，这是异步操作，需要用 `await`。
4. **MathJax 支持**：TryExamples 中的 docstring 支持 LaTeX 数学公式（如 `$\\theta'' + \\frac{g}{L}\\sin\\theta = 0$`），Sphinx 会通过 MathJax 渲染。

## 相关内容

- [03-sphinx-conf](/concepts/03-sphinx-conf.md)
- [05-config-files](/concepts/05-config-files.md)
- [10-disabling-examples](/concepts/10-disabling-examples.md)
- [08-customization](/concepts/08-customization.md)
