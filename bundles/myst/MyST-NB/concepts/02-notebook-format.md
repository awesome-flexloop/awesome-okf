---
type: Concept
title: MyST Notebook 文件格式
description: .ipynb 标准格式和 .md 文本格式（mystnb）的编写方式，code-cell/raw-cell/markdown-cell 语法
tags: [myst-nb, notebook, format, code-cell, ipynb, mystnb]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
  - id: notebook-cheatsheet
    resource: /references/notebook-cheatsheet.md
    title: MyST Notebook 语法速查
---

## MyST Notebook 文件格式

MyST-NB 支持两种 Notebook 源文件格式：**标准 Jupyter Notebook**（`.ipynb`）和 **MyST 文本格式 Notebook**（`.md`，通过 frontmatter 标识）。

## 格式一：标准 Jupyter Notebook（.ipynb）

标准 `.ipynb` 文件是 JSON 格式，可以直接由 Jupyter Notebook/Lab 创建和编辑。MyST-NB 直接读取和执行 `.ipynb` 文件，无需转换。

```json
{
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": ["# Hello Notebook\n", "\n", "这是 Markdown cell。"]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": ["print('Hello')"],
      "outputs": [],
      "execution_count": null
    }
  ],
  "metadata": {
    "kernelspec": {
      "display_name": "Python 3",
      "language": "python",
      "name": "python3"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 5
}
```

`.ipynb` 文件会被 MyST-NB 自动识别和处理，无需特殊配置。

## 格式二：MyST 文本格式 Notebook（.md）

MyST 文本格式允许在 Markdown 文件中编写 Notebook，使用特殊的指令围栏标记代码 cell。文件必须以包含 `file_format: mystnb` 的 YAML frontmatter 开头。

### 文件标识

```markdown
---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
---
```

或者使用 jupytext 格式标识：

```markdown
---
jupytext:
  text_representation:
    format_name: myst
kernelspec:
  name: python3
---
```

> 如果 `.md` 文件不包含上述 frontmatter 标识，将被 MyST-Parser 作为普通 MyST Markdown 文档处理，不会执行任何代码。

### Markdown Cell

普通 Markdown 内容即为 Markdown cell。多个 Markdown cell 之间用 `+++` 分隔：

```markdown
# 第一个 Markdown Cell

普通的 MyST Markdown 内容，可以使用所有 MyST 语法（指令、角色、交叉引用等）。

+++

## 第二个 Markdown Cell

`+++` 是 cell 分隔符，分隔前后的内容为不同的 Markdown cell。
```

### 带元数据的 Markdown Cell

`+++` 后可跟 JSON 对象作为 cell metadata：

```markdown
普通内容。

+++ {"tags": ["remove-cell"]}

这个 Markdown cell 在渲染时会被移除。
```

### Code Cell

使用 `{code-cell}` 指令围栏标记代码 cell：

````markdown
```{code-cell}
print("Hello from code cell!")
```
````

指定 kernel/language（可选，默认使用 kernelspec.name）：

````markdown
```{code-cell} python3
import numpy as np
arr = np.array([1, 2, 3])
print(arr.mean())
```
````

带选项的 code-cell：

````markdown
```{code-cell}
---
mystnb:
  remove_code_source: true
tags: [hide-output]
---

print("这段代码会被隐藏，只显示输出")
```
````

从外部文件加载代码：

````markdown
```{code-cell}
:load: helpers/setup.py
```
````

### Raw Cell

使用 `{raw-cell}` 指令围栏标记 raw cell：

````markdown
```{raw-cell} latex
\begin{equation}
E = mc^2
\end{equation}
```
````

Raw cell 的内容会直接传递给输出格式（不经过 Markdown 解析）。

### Cell 标签（Tags）

Code cell 和 Markdown cell 都支持 tags，通过 `:tags:` 选项或 metadata 设置：

````markdown
```{code-cell}
:tags: [remove-input, remove-stderr]

print("这段代码的源码会被隐藏，stderr 也会被移除")
```
````

| 标签 | 作用 |
|------|------|
| `remove-cell` / `remove_cell` | 完全移除该 cell（源码和输出都不渲染） |
| `remove-input` / `remove_input` | 只移除源码，保留输出 |
| `remove-output` / `remove_output` | 只移除输出，保留源码 |
| `remove-stderr` | 仅移除 stderr 输出 |
| `skip-execution` | 跳过此 cell 的执行 |
| `raises-exception` | 标记此 cell 预期会抛异常（不视为错误） |

## 读取层工作原理

MyST-NB 的读取层（`core/read.py`）负责将输入文件转换为 `NotebookNode` 对象：

1. 根据文件后缀选择 Reader（.ipynb → 标准 nbformat 读取；.md → 检测 frontmatter 后按 mystnb 格式解析）
2. 支持自定义格式：通过 `nb_custom_formats` 配置注册额外的文件后缀和读取函数
3. `read_myst_markdown_notebook()` 函数将文本格式解析为 NotebookNode：
   - 用 markdown-it 解析到 block 级别
   - 遇到 `{code-cell}` 围栏 → 创建 code cell
   - 遇到 `{raw-cell}` 围栏 → 创建 raw cell
   - 遇到 `+++` 分隔符 → 分割 markdown cell
   - 收集 frontmatter 作为 notebook metadata

## 格式选择建议

| 场景 | 推荐格式 |
|------|---------|
| 数据科学家已在 Jupyter 中工作 | `.ipynb` |
| 文档作者偏好纯文本/Git 友好 | `.md`（mystnb 格式） |
| 需要版本控制 diff 清晰 | `.md`（mystnb 格式） |
| 需要 ipywidgets 交互 | `.ipynb`（更成熟的 widget 支持） |
| 混合 Markdown 文档和少量代码 | `.md`（普通 MyST + {code-cell}） |

## 相关概念

- [快速开始](01-getting-started.md)
- [四阶段处理管线](03-processing-pipeline.md)
- [配置系统](04-config-system.md)
- [Glue 变量粘贴](07-glue.md)
- [MyST Notebook 语法速查](/references/notebook-cheatsheet.md)
