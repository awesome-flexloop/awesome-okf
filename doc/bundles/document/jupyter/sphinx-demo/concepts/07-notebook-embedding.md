---
type: Concept
title: NotebookLite 嵌入与单元格剥离
description: notebooklite 指令的使用方法、strip_tagged_cells 机制、Matplotlib 交互示例嵌入模式
tags: [notebooklite, embedding, jupyter-cells, strip, matplotlib]
difficulty: intermediate
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: notebooklite
    resource: /references/conf-py-source.md
    title: notebooklite 指令与 matplotlib_demo.md 源码
---

## notebooklite 指令

`notebooklite` 指令用于在文档页面中嵌入一个完整的可交互 Jupyter Notebook。与 jupyterlite 指令（嵌入 JupyterLab 环境）不同，notebooklite 直接展示 Notebook 界面，用户无需在 JupyterLab 中打开文件。

### 基本用法

在 MyST Markdown 中：

````markdown
# Matplotlib 交互示例

点击下方按钮在浏览器中运行此 Notebook：

+++ {"tags": ["jupyterlite_sphinx_strip"]}
> 📝 这是一个可交互的 Matplotlib 绘图示例。
> 点击 "Try it online" 按钮在浏览器中运行代码。

```{code-cell} ipython3
:tags: [remove-input]
%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
```

```{notebooklite}
:width: 100%
:new_tab_button_text: "Open in new tab"
```
````

### 指令选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `:width:` | CSS 长度 | iframe 宽度，如 `"100%"`、`"800px"` |
| `:height:` | CSS 长度 | iframe 高度，如 `"600px"` |
| `:new_tab_button_text:` | string | 新标签页打开按钮的文本 |
| `:notebook:` | 路径 | 嵌入外部 .ipynb 文件的路径 |

如果没有指定 `:notebook:`，notebooklite 会从当前 MyST 文档中的 `{code-cell}` 单元格构建 Notebook。

## strip_tagged_cells 机制

当 `strip_tagged_cells=True`（conf.py 中设置），带有 `jupyterlite_sphinx_strip` 标签的单元格会被特殊处理。

### 机制方向：文档中保留 → Notebook 中移除

这是最容易混淆的点：

| 位置 | 带有 strip 标签的单元格 |
|------|----------------------|
| Sphinx 渲染的文档页面 | ✅ **保留**（对读者可见） |
| JupyterLite 中的 Notebook | ❌ **移除**（不出现） |

```
文档页面上看到的：                用户点击按钮后打开的 Notebook：
┌─────────────────────┐          ┌─────────────────────┐
│ 📝 说明文字 (strip)  │ ←可见    │ import matplotlib    │ ←第一条cell
│ import matplotlib   │ ←可见    │ x = np.linspace(...) │
│ x = np.linspace(...)│ ←可见    │ plt.plot(x, y)       │
│ plt.plot(x, y)      │ ←可见    │ plt.show()           │
│ [Try it online]     │          │ [运行结果]            │
└─────────────────────┘          └─────────────────────┘
```

### 为什么需要 strip

strip 机制解决的核心问题是：**文档中的说明性内容不应出现在可执行 Notebook 中**。

典型使用场景：
1. **使用说明**：告诉读者这个 Notebook 是做什么的、如何操作
2. **指令按钮**：notebooklite 指令本身所在的单元格（如 `{notebooklite}` 代码块）
3. **环境配置说明**：如"在 Pyodide 中使用 matplotlib 需要以下设置"的提示文字

这些内容在文档上下文中有意义，但在 Notebook 中只会造成干扰——用户打开 Notebook 是为了运行代码，不是为了阅读说明。

### 在 MyST Notebook 中使用 strip

在 MyST Markdown 中，使用 `+++` 分隔符添加 cell metadata：

````markdown
+++ {"tags": ["jupyterlite_sphinx_strip"]}

> 这个单元格会在文档中显示，但在 Notebook 中被移除。
> 你可以在这里放任何 Markdown 内容。

+++

```{code-cell} ipython3
# 这个单元格在文档和 Notebook 中都会出现
import numpy as np
```
````

在 `.ipynb` 文件中，直接给 cell 添加 tag：

```json
{
  "cell_type": "markdown",
  "metadata": {
    "tags": ["jupyterlite_sphinx_strip"]
  },
  "source": ["说明文字"]
}
```

## code-cell 标签

除了 `jupyterlite_sphinx_strip`，MyST-NB 还支持其他标签控制代码单元格的显示：

| 标签 | 在文档中 | 在 Notebook 中 |
|------|---------|---------------|
| `jupyterlite_sphinx_strip` | 可见 | 移除 |
| `remove-input` | 隐藏输入代码 | 保留 |
| `remove-output` | 保留输入，隐藏输出 | 保留 |
| `hide-input` | 可折叠输入 | 保留 |

demo 中使用 `:tags: [remove-input]` 隐藏 Matplotlib 配置代码（`%matplotlib inline` 和 import），让读者只看到绘图逻辑和结果。

## 嵌入外部 Notebook 文件

使用 `:notebook:` 选项嵌入已有的 `.ipynb` 文件：

````markdown
```{notebooklite}
:notebook: ../custom_contents/arrays_in_numpy.ipynb
:width: 100%
:height: 500px
```
````

外部 Notebook 文件需要通过 `jupyterlite_contents` 配置包含到 JupyterLite 站点中。

## 相关内容

- [03-sphinx-conf](03-sphinx-conf.md)
- [06-try-examples](06-try-examples.md)
- [/examples/04-matplotlib-notebook.md](../examples/04-matplotlib-notebook.md)
