---
type: Concept
title: try_examples 指令——交互式文档示例
description: 使用 .. try_examples:: 指令将 doctest 格式的代码示例转为可在 JupyterLite 中运行的交互式 Notebook，支持 autodoc 自动注入
tags: [directive, try-examples, doctest, interactive, autodoc]
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
  - id: js
    resource: /references/js-source.md
    title: 前端JS源码
---

`try_examples` 是 jupyterlite-sphinx 中最具特色的指令，它能够将文档中 doctest 格式的代码示例自动转换为可在 JupyterLite 中运行的交互式 Notebook。这意味着文档中传统的静态代码示例（带有 `>>>` 提示符的 Python 交互示例）可以一键变为读者可实际运行、修改和探索的活代码环境，极大地提升了文档的交互性和教学价值。

## 类继承与模块分工

`try_examples` 的实现跨越两个模块：

- **`TryExamplesDirective`**（在 `jupyterlite_sphinx.py` 中，第 824-984 行）：Sphinx 指令类，负责指令解析、HTML 渲染、Notebook 文件写入
- **`examples_to_notebook()`**（在 `_try_examples.py` 中，第 7-124 行）：核心转换函数，负责将 doctest 文本行解析为 Notebook JSON 结构
- **前端 JavaScript**（`jupyterlite_sphinx.js`）：处理按钮交互、iframe 切换、移动端适配和运行时配置加载

`TryExamplesDirective` 直接继承自 `SphinxDirective`，不继承 `_LiteDirective`，因为它不引用外部 Notebook 文件，而是在构建时动态生成 Notebook。

## 基本用法

### 手动编写交互式示例

`try_examples` 指令的内容使用 doctest 格式编写：以 `>>>` 开头的行是输入代码，后续不以 `>>>` 或 `...` 开头的非空行是期望输出，以 `...` 开头的行是多行代码的续行：

```rst
.. try_examples::
   :button_text: 试试看！

   这是一个简单的加法示例：

   >>> 1 + 1
   2
   >>> for i in range(3):
   ...     print(i)
   0
   1
   2
```

构建时，`examples_to_notebook()` 函数会解析这些内容，生成一个包含 Markdown 单元格（说明文本）和代码单元格（含预填输出）的 Jupyter Notebook，保存为随机 UUID 命名的 `.ipynb` 文件到 `_contents/` 目录。

渲染后的 HTML 包含三个按钮（区别于其他指令只有一个按钮）：

1. **Try it** 按钮：初始可见，点击后在 iframe 中加载生成的 Notebook
2. **Go Back** 按钮：iframe 显示后可见，点击后返回文档原始示例视图
3. **Open In Tab** 按钮：在浏览器新标签页中打开 Notebook

### 添加警告文本

通过 `:warning_text:` 选项可以在 Notebook 顶部添加一个警告单元格，提醒读者注意事项：

```rst
.. try_examples::
   :warning_text: 注意：修改代码后需要重新运行单元格才能看到新结果

   >>> x = 10
   >>> print(x * 2)
   20
```

警告文本会作为 Notebook 的第一个 Markdown 单元格显示。

## 指令选项

`try_examples` 拥有独立的选项集，不使用其他指令的通用选项：

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `:height:` | CSS 长度 | 自适应内容高度 | iframe 高度 |
| `:theme:` | 字符串 | 无 | 应用于示例容器的 CSS 类名（`example_class`） |
| `:button_text:` | 字符串 | `"Try it with JupyterLite!"` | "Try it" 按钮的显示文本 |
| `:example_class:` | 字符串 | 无 | 示例外层容器的自定义 CSS 类名 |
| `:warning_text:` | 字符串 | 无 | Notebook 顶部显示的警告/说明文本 |

注意：`:theme:` 选项在 try_examples 中的含义与其他指令不同——它不是 JupyterLite 的界面主题，而是传递给 `example_class` 的 CSS 类名，用于自定义示例区域的外观样式。

## doctest 解析规则

`examples_to_notebook()` 函数逐行解析指令内容，维护四个状态变量：

| 状态变量 | 用途 |
|---------|------|
| `code_lines` | 累积当前代码块的输入代码行 |
| `md_lines` | 累积当前 Markdown 文本行 |
| `output_lines` | 累积当前代码块的输出行 |
| `inside_multiline_code_block` | 标记是否处于多行续行（`...`）中 |

行类型判定规则：

- **`>>>` 开头的行**：新代码行。去除 `>>> ` 前缀加入 `code_lines`；如果之前有待处理的 `output_lines` 或 `md_lines`，先将它们闭合为对应的单元格
- **`...` 开头且 code_lines 非空**：多行续行。去除 `... ` 前缀加入 `code_lines`，标记 `inside_multiline_code_block=True`
- **空行且 code_lines 非空**：代码块结束。调用 `_append_code_cell_and_clear_lines()` 创建代码单元格并附加输出
- **非空非前缀行且 code_lines 非空**：输出行。加入 `output_lines`
- **`.. plot::` 或 `.. only::` 开头**：进入忽略模式，跳过该指令及其缩进行
- **其他行**：Markdown 文本行，加入 `md_lines`

生成的 Notebook 使用 Python 内核，kernelspec metadata 为：

```json
{
  "kernelspec": {"display_name": "Python", "language": "python", "name": "python"},
  "language_info": {"name": "python"}
}
```

Markdown 单元格在写入 Notebook 前会经过四道后处理管线：LaTeX 语法转换、literal block 转换、Sphinx 引用标识符清理、Sphinx 链接转 Markdown 链接。

## 全局预导入代码

通过 `conf.py` 中的 `try_examples_preamble` 配置项，可以设置全局预导入代码。这段代码会作为一个独立的代码单元格插入到每个生成 Notebook 的第二个位置（在 warning 单元格之后，在示例代码单元格之前）：

```python
# conf.py
try_examples_preamble = """
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
"""
```

这样，每个 try_examples 生成的 Notebook 都默认导入了常用的科学计算库，读者无需手动编写 import 语句即可直接使用。

## autodoc 自动注入

`try_examples` 最强大的功能之一是与 Sphinx autodoc 扩展的集成。通过在 `conf.py` 中设置：

```python
global_enable_try_examples = True
```

可以全局启用自动注入。启用后，Sphinx 在处理 Python docstring 中的 `Examples` 段时，会自动为其注入 `try_examples` 指令，无需在 docstring 中手动编写 RST 指令。

自动注入的流程（由 `insert_try_examples_directive()` 函数实现）：

1. 搜索 `.. rubric:: Examples` 或 `.. admonition:: Examples` 标记定位 Examples 段
2. 跳过空行找到首个内容行
3. 检查是否存在 `.. disable_try_examples` 注释——如果存在则跳过该段，不注入
4. 检查是否已有 `.. try_examples::` 指令——避免重复注入
5. 定位节结束位置（下一个节标题）
6. 在内容前插入 `.. try_examples::` 指令和选项，将原内容缩进 4 个空格作为指令内容

这意味着你现有的使用 Google 风格或 NumPy 风格 docstring 的 Python 代码，无需修改即可自动获得交互式示例功能。

### 禁用特定 Examples 段

在 docstring 中使用 `.. disable_try_examples` 注释可以禁用特定 Examples 段的自动注入：

```python
def my_function(x):
    """
    函数说明。

    Examples
    --------
    .. disable_try_examples

    >>> my_function(1)
    1
    """
    pass
```

这适用于包含不适合在 JupyterLite 中运行的代码（如依赖本地文件系统、GPU 或特殊硬件的示例）的 Examples 段。

## 运行时配置（try_examples.json）

`try_examples` 支持一个独特的运行时配置机制：在 Sphinx 源目录根放置 `try_examples.json` 文件，可以在**不重新构建文档**的情况下调整行为。配置文件在前端页面加载时通过 fetch 请求读取。

配置字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `global_min_height` | 字符串（如 `"400px"`） | iframe 的全局最小高度，确保所有 try_examples 实例都有足够的显示空间 |
| `ignore_patterns` | 字符串数组（JS 正则表达式） | 匹配 URL pathname 的正则列表，匹配的页面上所有 try_examples 按钮会被自动隐藏 |

示例配置：

```json
{
  "global_min_height": "500px",
  "ignore_patterns": ["/api/", "/changelog/"]
}
```

`ignore_patterns` 可用于在特定页面（如纯 API 参考页、变更日志页）自动禁用 try_examples 按钮，无需在构建时处理。

## 移动端适配

`jupyterlite_sphinx.js` 中的 `isMobileDevice()` 函数（IIFE 单例）负责检测移动设备：

1. **User-Agent 检测**：使用 14 种移动设备 UA 正则模式匹配（Android、iPhone、iPad、iPod、BlackBerry、IEMobile、Windows Phone、Opera Mini、SamsungBrowser、UC Browser、MiuiBrowser、Mobile、Tablet 等）
2. **屏幕尺寸兜底**：屏幕宽度 ≤480px 或高度 ≤480px

检测到移动设备时，所有 `.try_examples_button` 会被自动隐藏（添加 `hidden` class），因为 JupyterLite 在小屏移动设备上的体验不佳。窗口 `resize` 事件（250ms 防抖）也会触发重新检测。

## 高度自适应

默认情况下，`try_examples` iframe 的高度会匹配原始示例内容的高度（`examples.offsetHeight`），确保 iframe 不会过高或过低。同时，如果设置了 `global_min_height`，iframe 高度不会低于该最小值。在 `tryExamplesShowIframe()` 函数中，最终高度取以下两者的较大值：

- 指定的 `iframeHeight` 参数值
- `max(globalMinHeight, examples.offsetHeight)`

这意味着内容多的示例会自动获得更高的 iframe，而简短的示例不会占用过多页面空间。

## 与其他指令的区别

| 特性 | try_examples | 其他指令 |
|------|-------------|---------|
| 内容来源 | 指令体内 doctest 文本 → 动态生成 Notebook | 引用外部 .ipynb/.md 文件 |
| 按钮数量 | 3个（Try it/Go Back/Open In Tab） | 1个（prompt 按钮或 new_tab 按钮） |
| 选项集 | 独立选项（height/theme/button_text/example_class/warning_text） | 通用选项（width/height/prompt/new_tab等） |
| autodoc 集成 | 支持自动注入 | 不支持 |
| 运行时配置 | 支持 try_examples.json | 不支持 |
| 移动端适配 | 自动隐藏按钮 | 无特殊处理 |

## 相关概念

- [指令系统总览](/concepts/03-directive-overview.md)
- [replite 指令——嵌入交互式 REPL](/concepts/06-replite-directive.md)
- [配置参考](/concepts/09-configuration.md)
- [核心模块源码](/references/main-source.md)
- [_try_examples 模块源码](/references/try-examples-source.md)
- [前端 JS 源码](/references/js-source.md)
