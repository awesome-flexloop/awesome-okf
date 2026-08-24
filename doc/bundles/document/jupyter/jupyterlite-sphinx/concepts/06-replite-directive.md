---
type: Concept
title: replite 指令——嵌入交互式 REPL
description: "使用 .. replite:: 指令嵌入交互式 REPL 控制台，支持预填代码和丰富的 REPL 行为配置"
tags: [directive, replite, repl, console, interactive]
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

`replite` 指令用于在 Sphinx 文档中嵌入交互式 REPL（Read-Eval-Print Loop，读取-求值-输出循环）控制台。REPL 是类似 IPython 的交互式命令行环境，读者可以逐行输入代码、即时看到执行结果。与 `jupyterlite` 和 `notebooklite` 嵌入完整 Notebook 不同，`replite` 更加轻量，适合展示短小的代码片段、快速验证 API 用法或作为文档中的可交互示例。

## 类继承关系

`replite` 指令的类继承结构与其他指令不同，`RepliteDirective` 直接继承自 Sphinx 的 `SphinxDirective`，**不继承 `_LiteDirective`**：

```
SphinxDirective
  └─ RepliteDirective （replite 指令实现类，has_content=True）
```

这种独立继承是因为 REPL 的工作方式与 Notebook 嵌入有本质区别：REPL 不引用外部 Notebook 文件，而是将指令内容（content）中的代码直接预填到控制台中。

对应的渲染节点类：

- **iframe_cls** = `RepliteIframe`，继承自 `_LiteIframe`，`lite_app` 属性为 `"repl/"`，`notebooks_path` 为空字符串
- **newtab_cls** = `RepliteTab`，**不继承 `_InTab`**，有独立的 URL 处理逻辑

## 基本用法

`replite` 指令通过 `has_content=True` 支持在指令体内编写预填代码：

```rst
.. replite::
   :width: 100%
   :height: 300px
   :prompt: 点击运行代码

   import math

   x = 16
   print(f"Square root of {x} is {math.sqrt(x)}")
```

渲染后，读者点击按钮（或 iframe 直接加载）会看到一个 REPL 控制台，其中预填了指令体内的代码。根据 `:execute:` 选项设置，代码可能在加载时自动执行。

指令内容中的每一行代码会被逐行处理：**空行保留为空字符串**，非空行作为代码行。所有代码行拼接后通过 URL 的 `code` 查询参数传递给 REPL 应用。

## REPL 特有选项

`replite` 除了支持通用选项（width/height/prompt/prompt_color/search_params/new_tab/new_tab_button_text/theme）外，还有一组特有的选项来控制 REPL 行为：

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `:kernel:` | 字符串 | `"python"`（Pyodide） | 指定 REPL 使用的内核名称 |
| `:execute:` | bool | `True`（受全局配置影响） | 加载时是否自动执行预填代码 |
| `:clear_cells_on_execute:` | bool | `False` | 执行新单元格时是否清除之前的单元格输出 |
| `:clear_code_content_on_execute:` | bool | `False` | 执行后是否清空提示单元格（prompt cell）的代码内容 |
| `:hide_code_input:` | bool | `False` | 是否隐藏代码输入区域（仅显示输出结果） |
| `:prompt_cell_position:` | 字符串 | `"bottom"` | 输入提示单元格位置，可选值：`bottom`/`top`/`left`/`right` |
| `:show_banner:` | bool | `True` | 是否显示内核启动 banner 信息 |
| `:toolbar:` | 字符串 | 无 | 控制工具栏显示 |
| `:showbanner:` | bool | 无 | `:show_banner:` 的别名（驼峰转换兼容） |

### prompt_cell_position 验证

`:prompt_cell_position:` 选项在源码中有严格的验证逻辑，只接受四个合法值：`bottom`、`top`、`left`、`right`。传入其他值会导致指令渲染错误。

### 内核选择

`:kernel:` 选项用于指定 REPL 使用的 Jupyter 内核。JupyterLite 环境中常见的内核包括：

- `python`：基于 Pyodide（CPython 编译为 WebAssembly），默认内核
- `xpython`：基于 xeus-python，另一个 Python 内核实现

未来可能支持更多语言内核（如 JavaScript、Lua 等），具体取决于 JupyterLite 部署中安装的内核。

## URL 参数映射机制

REPL 特有的选项在转换为 URL 查询参数时，会进行**蛇形命名到驼峰命名（camelCase）的自动转换**。`_build_options()` 函数负责处理这一转换：

| 指令选项 | URL 参数名 |
|---------|-----------|
| `execute` | `execute` |
| `clear_cells_on_execute` | `clearCellsOnExecute` |
| `clear_code_content_on_execute` | `clearCodeContentOnExecute` |
| `hide_code_input` | `hideCodeInput` |
| `show_banner` / `showbanner` | `showBanner` |
| `prompt_cell_position` | `promptCellPosition` |

布尔值在 URL 参数中转换为字符串 `"0"`（False）或 `"1"`（True）。

例如，以下指令：

```rst
.. replite::
   :execute: True
   :clear_cells_on_execute: False
   :hide_code_input: False
   :prompt_cell_position: bottom

   print("Hello, JupyterLite!")
```

生成的 URL 大致为：

```
{prefix}/repl/index.html?code=print%28%22Hello%2C%20JupyterLite%21%22%29&execute=1&clearCellsOnExecute=0&hideCodeInput=0&promptCellPosition=bottom
```

指令体内的代码行（包括空行保留的空串）使用换行符 `\n` 拼接后，经过 URL 编码作为 `code` 参数值。

## RepliteTab 的独立 URL 处理

`RepliteTab` 类不继承 `_InTab` 基类，而是有完全独立的实现（第 260-335 行）。它在处理新标签页 URL 时有自己的逻辑，包括独立处理代码内容的 URL 编码和 REPL 特有参数的拼接。

## 全局 REPL 行为配置

在 `conf.py` 中可以通过以下配置项设置 REPL 的全局默认行为，所有 `replite` 指令都会继承这些默认值（指令级别选项会覆盖全局配置）：

| 全局配置项 | 默认值 | 对应指令选项 |
|-----------|--------|-------------|
| `replite_auto_execute` | `True` | `:execute:` |
| `replite_clear_cells_on_execute` | `False` | `:clear_cells_on_execute:` |
| `replite_clear_code_content_on_execute` | `False` | `:clear_code_content_on_execute:` |
| `replite_hide_code_input` | `False` | `:hide_code_input:` |
| `replite_prompt_cell_position` | `"bottom"` | `:prompt_cell_position:` |
| `replite_show_banner` | `True` | `:show_banner:` |
| `replite_new_tab_button_text` | `"Open in a REPL"` | `:new_tab_button_text:` |

示例配置：

```python
# conf.py
replite_auto_execute = False
replite_prompt_cell_position = "top"
replite_show_banner = False
```

## 使用场景与示例

### 简单算术演示

```rst
.. replite::
   :height: 200px

   >>> 2 + 2
   4
   >>> sum(range(100))
   4950
```

注意：REPL 中的代码不需要 `>>>` 前缀——与 `try_examples` 不同，`replite` 的内容是直接作为代码执行的，不是 doctest 格式。

### 数据处理示例

```rst
.. replite::
   :width: 100%
   :height: 400px
   :kernel: python
   :execute: True

   import statistics

   data = [23, 45, 67, 12, 89, 34, 56, 78]
   print(f"数据: {data}")
   print(f"均值: {statistics.mean(data):.2f}")
   print(f"中位数: {statistics.median(data)}")
   print(f"标准差: {statistics.stdev(data):.2f}")
```

### 新标签页模式

```rst
.. replite::
   :new_tab: True
   :new_tab_button_text: 打开 REPL 控制台

   import sys
   print(f"Python 版本: {sys.version}")
```

## 相关概念

- [指令系统总览](/concepts/03-directive-overview.md)
- [jupyterlite 指令——嵌入 JupyterLab](/concepts/04-jupyterlite-directive.md)
- [notebooklite 指令——嵌入经典 Notebook](/concepts/05-notebooklite-directive.md)
- [try_examples 指令——交互式文档示例](/concepts/08-try-examples-directive.md)
- [配置参考](/concepts/09-configuration.md)
- [核心模块源码](/references/main-source.md)
- [配置项完整速查表](/references/config-reference.md)
