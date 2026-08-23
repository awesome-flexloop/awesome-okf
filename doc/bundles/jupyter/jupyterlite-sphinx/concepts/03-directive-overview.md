---
type: Concept
title: 指令系统总览
description: jupyterlite-sphinx 提供的五个 RST 指令对比：jupyterlite、notebooklite、replite、voici、try_examples
tags: [directives, overview, comparison]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-02-22
sources:
  - id: main
    resource: /references/main-source.md
    title: 核心模块源码
---

jupyterlite-sphinx 提供了五个 RST 指令（directive）用于在 Sphinx 文档中嵌入 JupyterLite 内容。每个指令对应不同的前端界面和使用场景，并共享一组通用选项。本文对这五个指令进行全面对比，帮助你根据需求选择合适的指令。

## 五个指令对比表

| 指令名 | 嵌入内容 | URL 路径 | 支持 notebook 参数 | 支持 new_tab | 典型用途 |
|--------|---------|---------|:-----------------:|:------------:|---------|
| `jupyterlite` | JupyterLab 界面 | `lab/` | ✅ | ✅ | 嵌入空白 JupyterLab 环境或在 JupyterLab 中打开 Notebook |
| `notebooklite` | 经典 Notebook 界面 | `tree/`（Notebook 路径为 `../notebooks/`） | ✅ | ✅ | 在经典 Jupyter Notebook 界面中打开 Notebook 文件 |
| `replite` | REPL 交互式控制台 | `repl/` | ❌（使用指令内容作为代码） | ✅ | 嵌入短小的交互式代码片段，即时运行 |
| `voici` | Voici 仪表板 | `voici/render/`（指定 notebook）或 `voici/tree`（未指定） | ✅ | ✅ | 嵌入 Voici 渲染的静态交互式仪表板 |
| `try_examples` | doctest 示例转 Notebook | `tree/`（Notebook 路径为 `../notebooks/`） | ❌（使用指令内容生成 Notebook） | ✅（内置"Open In Tab"按钮） | 自动将文档中的 doctest 代码示例转为可运行 Notebook |

> **注意**：`retrolite` 是 `notebooklite` 的别名，两者完全等效，指向同一个指令类 `NotebookLiteDirective`。

## 两种嵌入模式

除 `try_examples` 外，四个指令均支持两种嵌入模式：iframe 嵌入模式和新标签页模式。

### iframe 嵌入模式（默认）

默认情况下，指令渲染为一个 `<iframe>` 元素，将 JupyterLite 界面直接嵌入到文档页面内。读者无需离开文档页面即可与代码交互。iframe 的尺寸通过 `:width:` 和 `:height:` 选项控制。

iframe 嵌入支持**懒加载**：当设置 `:prompt:` 选项时，页面初始加载时不会创建 iframe，而是显示一个可点击按钮。读者点击按钮后，前端 JavaScript（`jupyterlite_sphinx.js` 中的 `window.jupyterliteShowIframe` 函数）才会动态创建 iframe 并加载 JupyterLite 内容。这避免了页面中存在多个 JupyterLite 实例时的性能问题。

### 新标签页模式（`:new_tab: True`）

设置 `:new_tab: True` 选项后，指令不再渲染 iframe，而是渲染一个按钮。读者点击按钮后，JupyterLite 界面会在浏览器的新标签页中打开，提供更完整的使用体验（不受 iframe 尺寸限制）。

每个指令的新标签页按钮有独立的默认文本，可以通过指令选项或全局配置自定义：

| 指令 | 默认按钮文本 | 全局配置项 |
|------|------------|-----------|
| `jupyterlite` | "Open as a notebook" | `jupyterlite_new_tab_button_text` |
| `notebooklite` | "Open as a notebook" | `notebooklite_new_tab_button_text` |
| `voici` | "Open with Voici" | `voici_new_tab_button_text` |
| `replite` | "Open in a REPL" | `replite_new_tab_button_text` |

在指令级别，可以通过 `:new_tab_button_text:` 选项覆盖默认文本。

## 通用选项详解

以下选项在 `jupyterlite`、`notebooklite`、`replite`、`voici` 四个指令上通用（`try_examples` 有自己独立的选项集）：

### 尺寸选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `:width:` | `100%` | iframe 宽度，接受 CSS 长度值（如 `100%`、`800px`） |
| `:height:` | `1000px`（jupyterlite/notebooklite）<br>`100%`（replite） | iframe 高度，接受 CSS 长度值 |

注意 replite 的默认高度是 `100%`（占满容器高度），而 jupyterlite 和 notebooklite 的默认高度是 `1000px`，这是因为 JupyterLab 和经典 Notebook 界面需要足够的垂直空间来显示完整的 IDE 布局，而 REPL 控制台更灵活。

### 懒加载按钮选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `:prompt:` | 无（不显示按钮，直接加载 iframe） | 设置后显示可点击按钮，按钮文本为选项值；点击后才加载 iframe |
| `:prompt_color:` | `#f7dc1e`（黄色） | 按钮背景颜色，接受 CSS 颜色值 |

`:prompt:` 选项是提升页面加载性能的关键。当一个文档页面包含多个 JupyterLite 嵌入时，强烈建议为每个指令设置 `:prompt:` 选项，避免页面加载时同时启动多个 JupyterLite 实例（每个实例都是一个完整的 Jupyter 环境，内存消耗较大）。

按钮默认使用黄色背景（`#f7dc1e`）和 "Try It Live!" 文本（当 `:prompt:` 未指定文本时）。指定 `:prompt:` 后文本会替换为你设置的值。

### 新标签页选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `:new_tab:` | 未设置（默认 iframe 模式） | 设为 `True` 时使用新标签页模式 |
| `:new_tab_button_text:` | 各指令默认值 | 新标签页按钮的显示文本 |

### URL 参数传递选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `:search_params:` | `False` | 控制是否将当前页面的 URL 搜索参数传递到 iframe |

`:search_params:` 选项接受三种值：

- `True`：将当前页面的所有 URL 搜索参数（query string）传递到 iframe 的 JupyterLite URL 中
- `False`（默认）：不传递任何搜索参数
- `["param1", "param2"]`（JSON 数组格式）：只传递指定名称的搜索参数

这个选项的典型用途是将页面的认证 token、语言设置等参数传递给嵌入的 JupyterLite 实例。前端 JavaScript 函数 `window.jupyterliteConcatSearchParams` 负责处理参数的筛选和拼接。

### 主题选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `:theme:` | JupyterLite 默认主题 | 指定 JupyterLite 的主题（如 JupyterLab 明暗主题） |

## 各指令对应的前端界面

每个指令指向 JupyterLite 站点中的不同应用路径，对应不同的前端界面：

### `jupyterlite` → JupyterLab

URL 路径：`lite/lab/`

打开完整的 JupyterLab 界面，包含文件浏览器、代码编辑器、终端、命令面板等功能。这是功能最完整的界面，适合需要完整 Notebook 编辑体验的场景。不指定 notebook 参数时，显示 JupyterLab 的启动页（Launcher），读者可以创建新的 Notebook、Console、Terminal 等。指定 notebook 参数时，在 JupyterLab 中打开该 Notebook 文件。

```rst
.. jupyterlite::
   :prompt: 打开 JupyterLab

.. jupyterlite:: my_notebook.ipynb
   :prompt: 在 JupyterLab 中打开 Notebook
```

### `notebooklite` → 经典 Notebook

URL 路径：`lite/tree/`（文件浏览器），Notebook 文件路径为 `lite/notebooks/`

打开 Jupyter 的经典 Notebook 界面（即 JupyterLab 出现之前的传统单文档界面）。不指定参数时显示文件浏览器视图（tree view），指定 notebook 参数时直接打开该 Notebook。这个界面更简洁，适合只需要阅读和运行单个 Notebook 的场景。

```rst
.. notebooklite:: my_notebook.ipynb
   :prompt: 打开 Notebook
```

`retrolite` 是 `notebooklite` 的别名：

```rst
.. retrolite:: my_notebook.ipynb
   :prompt: 打开 Notebook（使用别名）
```

### `replite` → REPL 控制台

URL 路径：`lite/repl/`

打开 Jupyter REPL（Read-Eval-Print Loop）交互式控制台，类似 IPython 的交互模式。指令内容（content）中的代码会被预加载到 REPL 中，加载时自动执行（可通过 `:execute: False` 关闭）。

replite 支持一组特有的选项来控制 REPL 行为：

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `:kernel:` | `python` | 指定内核名称 |
| `:execute:` | `True`（受全局配置影响） | 加载时是否自动执行代码 |
| `:clear_cells_on_execute:` | `False` | 执行新单元格时是否清除之前的单元格 |
| `:clear_code_content_on_execute:` | `False` | 执行后是否清空提示单元格代码 |
| `:hide_code_input:` | `False` | 是否隐藏输入单元格（仅显示输出） |
| `:prompt_cell_position:` | `bottom` | 提示单元格位置：`bottom`/`top`/`left`/`right` |
| `:show_banner:` | `True` | 是否显示内核 banner |
| `:toolbar:` | 无 | 控制工具栏显示 |
| `:showbanner:` | 无 | showBanner 的别名（URL 参数名转换） |

```rst
.. replite::
   :width: 100%
   :height: 300px
   :prompt: 运行代码

   import math
   x = 16
   print(f"Square root of {x} is {math.sqrt(x)}")
```

### `voici` → Voici 仪表板

URL 路径：`lite/voici/render/<notebook>.html`（指定 notebook）或 `lite/voici/tree`（未指定）

Voici 是基于 JupyterLite 的仪表板渲染工具，可以将 Notebook 转换为静态交互式仪表板（隐藏代码单元格，只保留 Markdown 文本和 widgets 输出）。使用 voici 指令需要单独安装 `voici` 包，否则会抛出 RuntimeError。

```rst
.. voici:: my_dashboard.ipynb
   :width: 100%
   :height: 800px
   :prompt: 查看仪表板
```

不指定 notebook 参数时，显示 Voici 的文件浏览器视图（tree view），读者可以选择要查看的仪表板。

### `try_examples` → 自动生成 Notebook

URL 路径：`lite/tree/`（生成的 Notebook 存放在 `lite/notebooks/` 下）

`try_examples` 是 jupyterlite-sphinx 中最具特色的指令。它不引用外部 Notebook 文件，而是将指令内容中的 doctest 格式代码块自动转换为 Jupyter Notebook，并嵌入到文档中。

try_examples 有自己独立的选项集：

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `:height:` | 自适应 | iframe 高度 |
| `:theme:` | 无 | example_class CSS 类名 |
| `:button_text:` | "Try it with JupyterLite!" | 触发按钮文本 |
| `:example_class:` | 无 | 示例容器的 CSS 类 |
| `:warning_text:` | 无 | 在 Notebook 顶部显示的警告文本 |

try_examples 生成的 HTML 结构比其他指令更复杂，包含三个按钮：
1. **Try it** 按钮：点击后加载 iframe 显示 Notebook
2. **Go Back** 按钮：在 iframe 中返回文档示例视图
3. **Open In Tab** 按钮：在新标签页中打开 Notebook

指令内容中的代码使用 doctest 格式编写：

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

扩展内部的 `examples_to_notebook()` 函数会解析这些 doctest 行，生成对应的 Jupyter Notebook JSON（包含代码单元格和输出单元格），保存为随机 UUID 命名的 `.ipynb` 文件。

此外，try_examples 支持通过 `global_enable_try_examples = True` 配置全局启用——启用后，Sphinx 的 autodoc 扩展在处理 Python docstring 中的 `Examples` 段时，会自动为其注入 `try_examples` 指令，无需手动编写。

## URL 路径与 iframe 构造原理

每个指令在渲染时，会根据自身的 `lite_app` 属性和当前文档相对于 JupyterLite 输出目录（`lite/`）的位置来构造 iframe 的 `src` URL。URL 的基本结构为：

```
{prefix}/{lite_app}{path}?{options}
```

其中：

- `prefix` 是从当前 RST 源文件所在目录到 `lite/` 目录的相对路径（通过 `os.path.relpath` 计算）
- `lite_app` 是各指令对应的应用路径前缀
- `path` 是 Notebook 文件路径（如果指定了 notebook 参数）或代码参数（如果是 replite）
- `options` 是通过 `_build_options()` 函数将指令选项转换的 URL 查询参数（蛇形命名自动转为驼峰命名，如 `clear_cells_on_execute` → `clearCellsOnExecute`，布尔值转为 `0`/`1`）

## 指令继承关系

从源码实现看，五个指令的类继承关系如下：

- `SphinxDirective`（Sphinx 提供的指令基类）
  - `RepliteDirective`：独立实现，处理 REPL 特有的代码内容和 URL 参数
  - `_LiteDirective`：Notebook 嵌入基类，处理文件路径解析、Notebook 复制、jupytext 转换
    - `BaseJupyterViewDirective`：定义 iframe/tab 类属性的中间类
      - `JupyterLiteDirective` → `jupyterlite` 指令
      - `NotebookLiteDirective` → `notebooklite`/`retrolite` 指令
      - `VoiciDirective` → `voici` 指令（额外检查 voici 包是否安装）
  - `TryExamplesDirective`：独立实现，处理 doctest 解析和 Notebook 生成

## 相关概念

- [jupyterlite-sphinx 是什么](/concepts/00-introduction.md)
- [安装与基础配置](/concepts/01-installation.md)
- [快速开始](/concepts/02-quick-start.md)
