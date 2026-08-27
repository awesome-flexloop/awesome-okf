---
type: Example
title: 嵌入带预填代码的 REPL
description: 使用 replite 指令嵌入预填代码的交互式 REPL 控制台，自定义 REPL 行为
tags: [example, replite, repl, code-execution]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-02-22
sources:
  - id: main
    resource: /references/main-source.md
    title: 核心模块源码
  - id: config
    resource: /references/config-reference.md
    title: 配置参考
---

本示例展示如何使用 `.. replite::` 指令在文档中嵌入一个预填代码的交互式 REPL（Read-Eval-Print Loop，读取-求值-输出循环）控制台。与嵌入完整 JupyterLab 或 Notebook 不同，REPL 模式提供一个轻量级的交互式代码执行环境，读者可以直接修改和运行预填代码，特别适合展示简短的代码示例、API 用法演示和数学计算。

## 项目结构

```
my-docs/
├── conf.py
├── index.rst
└── _build/
```

## conf.py 配置

```python
# conf.py

project = 'REPL Embed Demo'
copyright = '2026, Your Name'
author = 'Your Name'
release = '0.1'

extensions = [
    'jupyterlite_sphinx',
]

html_theme = 'alabaster'

# REPL 全局配置（可选，可被指令选项覆盖）
replite_auto_execute = True           # 自动执行预填代码
replite_clear_cells_on_execute = False  # 执行后是否清空单元格
replite_clear_code_content_on_execute = False  # 执行后是否清空代码内容
replite_hide_code_input = False       # 是否隐藏代码输入区域
replite_show_banner = True            # 是否显示顶部横幅
replite_prompt_cell_position = "bottom"  # 输入提示单元格位置：top/bottom/left/right
```

这些全局配置在 `setup()` 函数中通过 `app.add_config_value()` 注册，每个选项都可以被指令级别的同名选项覆盖。

## 基础 REPL 嵌入

在 RST 文件中使用 `.. replite::` 指令，指令内容（缩进的代码块）即为预填到 REPL 中的 Python 代码：

```rst
REPL 示例
=========

试试下面的 Python 代码：

.. replite::
   :width: 100%
   :height: 400px
   :prompt: 运行代码

   print("Hello, JupyterLite!")
   for i in range(5):
       print(f"Count: {i}")
```

指令内容中的代码行会被收集，空行会被保留（转换为空字符串），然后通过 URL 查询参数 `code=` 传递给 REPL 应用。REPL 对应的 JupyterLite 应用路径为 `repl/`。

## 指定内核（kernel）

使用 `:kernel:` 选项可以指定 REPL 使用的 Jupyter 内核。默认使用 Pyodide（基于 WebAssembly 的 Python 内核），也可以指定 xeus-python 等其他内核：

```rst
使用 xeus-python 内核的 REPL：

.. replite::
   :width: 100%
   :height: 500px
   :kernel: xpython
   :prompt: 启动 xeus-python REPL

   import numpy as np
   x = np.linspace(0, 2 * np.pi, 100)
   print(f"Created array with {len(x)} points")
   print(f"sin(π/2) = {np.sin(np.pi/2):.4f}")
```

`:kernel: xpython` 对应 xeus-python 内核。确保你的 JupyterLite 构建中已安装对应内核；默认的 Pyodide 内核无需额外配置。

## 控制自动执行

默认情况下，REPL 加载后会自动执行预填代码（`replite_auto_execute = True`）。使用 `:execute: False` 可以禁用自动执行，让读者手动点击运行按钮：

```rst
.. replite::
   :width: 100%
   :height: 400px
   :execute: False
   :prompt: 点击运行

   # 这段代码不会自动执行，需要手动点击运行按钮
   result = sum(range(1, 101))
   print(f"1 到 100 的和为: {result}")
```

`:execute:` 接受 `True` 或 `False` 字符串值，会被转换为 URL 参数 `execute=1` 或 `execute=0`。

## matplotlib 绘图示例

REPL 支持 matplotlib 绘图，图形输出会显示在 REPL 输出区域：

```rst
matplotlib 绘图示例：

.. replite::
   :width: 100%
   :height: 600px
   :prompt: 运行绘图代码
   :execute: False

   %matplotlib inline
   import matplotlib.pyplot as plt
   import numpy as np

   x = np.linspace(0, 2 * np.pi, 200)
   y = np.sin(x)

   fig, ax = plt.subplots(figsize=(8, 4))
   ax.plot(x, y, 'b-', linewidth=2, label='sin(x)')
   ax.plot(x, np.cos(x), 'r--', linewidth=2, label='cos(x)')
   ax.set_xlabel('x')
   ax.set_ylabel('y')
   ax.set_title('Sine and Cosine Functions')
   ax.legend()
   ax.grid(True, alpha=0.3)
   plt.show()
```

注意 `%matplotlib inline` 魔术命令，它确保图形以内联方式显示在输出中。

## 调整输入单元格位置

使用 `:prompt_cell_position:` 选项可以调整代码输入区域在 REPL 界面中的位置：

```rst
输入框位于顶部：

.. replite::
   :width: 100%
   :height: 400px
   :prompt_cell_position: top

   x = 42
   print(f"The answer is {x}")
```

有效值为 `top`、`bottom`（默认）、`left`、`right`。此选项对应 URL 参数 `promptCellPosition`。

## 在新标签页中打开 REPL

与 `jupyterlite` 指令类似，`replite` 也支持 `:new_tab:` 选项，在新标签页中打开 REPL：

```rst
.. replite::
   :width: 100%
   :height: 400px
   :new_tab: True
   :new_tab_button_text: 在新标签页中打开 REPL
   :kernel: xpython
   :execute: False

   # 这是一个在新标签页中打开的 REPL 示例
   import sys
   print(f"Python version: {sys.version}")
```

当 `:new_tab: True` 时，代码内容会被序列化到 URL 参数中，新标签页的 REPL 会自动加载这些预填代码。`:new_tab_button_text:` 自定义按钮文本，未指定时使用全局配置 `replite_new_tab_button_text`（默认为 "Open in a REPL"）。

## 其他 REPL 选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `:width:` | CSS 长度 | `100%` | iframe 宽度 |
| `:height:` | CSS 长度 | `100%` | iframe 高度 |
| `:kernel:` | 字符串 | 默认内核 | 指定 Jupyter 内核名称 |
| `:execute:` | `True`/`False` | 全局配置值 | 是否自动执行预填代码 |
| `:clear_cells_on_execute:` | `True`/`False` | `False` | 执行时是否清空已有输出单元格 |
| `:clear_code_content_on_execute:` | `True`/`False` | `False` | 执行时是否清空代码输入内容 |
| `:hide_code_input:` | `True`/`False` | `False` | 是否隐藏代码输入区域 |
| `:show_banner:` | `True`/`False` | `True` | 是否显示顶部横幅 |
| `:prompt_cell_position:` | `top`/`bottom`/`left`/`right` | `bottom` | 输入提示单元格位置 |
| `:prompt:` | 字符串 | 无 | 懒加载按钮文本 |
| `:prompt_color:` | CSS 颜色 | `#f7dc1e` | 按钮背景色 |
| `:new_tab:` | `True`/`False` | `False` | 是否在新标签页打开 |
| `:new_tab_button_text:` | 字符串 | 全局配置 | 新标签页按钮文本 |
| `:theme:` | 字符串 | JupyterLite 默认 | JupyterLab 主题名称 |
| `:toolbar:` | 字符串 | 默认 | 工具栏配置 |

布尔类型选项（`execute`、`clear_cells_on_execute` 等）接受 `True`/`False`（不区分大小写），内部转换为 `1`/`0` 作为 URL 参数值。

## 完整 index.rst 示例

```rst
REPL 嵌入演示
============

基础 REPL：

.. replite::
   :width: 100%
   :height: 300px
   :prompt: 运行基础示例

   print("Hello from REPL!")

禁用自动执行：

.. replite::
   :width: 100%
   :height: 300px
   :execute: False
   :prompt: 手动运行

   # 手动点击运行按钮执行
   print("手动执行的代码")

新标签页打开：

.. replite::
   :new_tab: True
   :new_tab_button_text: 在新标签页中尝试

   print("在新标签页中打开的 REPL")
```

## 相关概念

- [replite 指令详解](../concepts/06-replite-directive.md)
- [指令系统总览](../concepts/03-directive-overview.md)
- [配置参考](../references/config-reference.md)
- [核心模块源码](../references/main-source.md)
- [TryExamples 指令](../concepts/08-try-examples-directive.md)
