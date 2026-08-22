---
type: Reference
title: MyST Notebook 语法速查
description: MyST 文本格式 Notebook（mystnb）的语法速查——code-cell、raw-cell、cell metadata、glue、eval 语法
tags: [myst-nb, notebook, syntax, cheatsheet, code-cell]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

# MyST Notebook 语法速查

## 文件标识

MyST 文本格式 Notebook 必须以 YAML frontmatter 开头，包含文件格式标识：

```markdown
---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
---
```

或使用 jupytext 格式：

```markdown
---
jupytext:
  text_representation:
    format_name: myst
kernelspec:
  name: python3
---
```

## 代码 Cell

使用 `{code-cell}` 指令围栏：

````markdown
```{code-cell}
print("Hello, World!")
```
````

### 指定语言/kernel

````markdown
```{code-cell} python3
:tags: [hide-input]

import numpy as np
x = np.array([1, 2, 3])
```
````

### Cell 选项

````markdown
```{code-cell}
:tags: [remove-input, remove-output]
:load: code/helper.py

print("This code is loaded from helper.py")
```
````

| 选项 | 说明 |
|------|------|
| `:load: path` | 从外部文件加载代码内容 |
| `:tags: [tag1,tag2]` | Cell 标签 |

### Cell 标签

| 标签 | 说明 |
|------|------|
| `remove-cell` / `remove_cell` | 移除整个 cell |
| `remove-input` / `remove_input` | 移除输入（源码） |
| `remove-output` / `remove_output` | 移除输出 |
| `remove-stderr` | 仅移除 stderr |
| `skip-execution` | 跳过此 cell 执行 |
| `raises-exception` | 标记 cell 预期会抛异常 |

## Markdown Cell

普通 Markdown 内容即为 Markdown Cell。使用 `+++` 分隔多个 Markdown Cell：

```markdown
# 第一个 Markdown Cell

这是普通 Markdown 内容。

+++

# 第二个 Markdown Cell

`+++` 后面的内容是新的 Markdown Cell。
```

### 带元数据的 Markdown Cell

`+++` 后可跟 JSON 元数据：

```markdown
一些内容。

+++ {"tags": ["remove-cell"]}

这个 Markdown Cell 会被移除。
```

## Raw Cell

使用 `{raw-cell}` 指令围栏：

````markdown
```{raw-cell} markdown
This is raw **markdown** passed directly to output.
```
````

## Glue 语法

### 在代码中粘贴变量

```python
from myst_nb import glue
import pandas as pd

df = pd.DataFrame({"a": [1,2,3], "b": [4,5,6]})
glue("my_dataframe", df)
glue("my_figure", fig, display=False)  # display=False 不立即显示
```

### 在文档中引用

| 语法 | 说明 |
|------|------|
| `{glue}`key`` | 自动选择 MIME 类型粘贴 |
| `{glue:text}`key`` | 粘贴纯文本 |
| `{glue:md}`key`` | 粘贴 Markdown |
| `{glue:figure}`key`` | 以 figure 形式粘贴图片 |
| `{glue:math}`key`` | 粘贴数学公式 |

### glue 指令（块级）

````markdown
```{glue:figure} my_figure
:name: fig-my-plot

这是图片的标题。
```
````

## Eval 语法

### 内联求值

```markdown
数据集中共有 {eval}`len(df)` 条记录。
平均值为 {eval}`x.mean()`。
```

### 块级求值

````markdown
```{eval}
x.describe()
```
````

## nb-download 角色

```markdown
下载 {nb-download}`执行后的 notebook <notebook1.ipynb>`。
```

## Cell 级配置（mystnb metadata）

在 code-cell 的选项中设置 mystnb 元数据：

````markdown
```{code-cell}
---
mystnb:
  remove_code_source: true
  scroll_outputs: true
  output_stderr: remove
  number_source_lines: true
  image:
    width: 500px
  figure:
    caption: "自动生成的图"
---

import matplotlib.pyplot as plt
plt.plot([1,2,3])
plt.show()
```
````

### 常用 cell 级配置

| 配置键 | 类型 | 说明 |
|--------|------|------|
| `remove_code_source` | bool | 移除源码 |
| `remove_code_outputs` | bool | 移除输出 |
| `scroll_outputs` | bool | 滚动输出 |
| `number_source_lines` | bool | 行号 |
| `output_stderr` | str | stderr 处理：show/remove/remove-warn/warn/error/severe |
| `merge_streams` | bool | 合并 stdout/stderr |
| `text_lexer` | str | 文本 lexer |
| `error_lexer` | str | 错误 lexer |
| `image` | dict | 图片选项（width/height/alt/class/align/scale） |
| `figure` | dict | figure 选项（classes/name/caption/caption_before） |
| `markdown_format` | str | Markdown 格式：commonmark/gfm/myst |

## 文件级配置（frontmatter）

```markdown
---
file_format: mystnb
kernelspec:
  name: python3
mystnb:
  execution_mode: cache
  execution_timeout: 60
  remove_code_source: false
---
```

## 执行模式

| 模式 | 说明 |
|------|------|
| `off` | 不执行，使用现有输出 |
| `auto` | 有缺失输出时执行（默认） |
| `force` | 强制重新执行 |
| `cache` | 使用 jupyter-cache 缓存执行 |
| `inline` | 内联模式（eval 用） |
