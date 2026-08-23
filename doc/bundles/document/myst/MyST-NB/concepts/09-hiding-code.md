---
type: Concept
title: 代码隐藏与输出控制
description: remove-input/output/cell 标签、scroll_outputs、代码折叠（Hide Code Cell）、prompt 自定义、行号
tags: [myst-nb, hide, remove, scroll, code-cell, toggle]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

## 代码隐藏与输出控制

MyST-NB 提供细粒度的代码和输出控制能力，可以隐藏/移除代码源码、输出、整个 cell，或添加可折叠的代码块。

## Cell 标签控制（推荐）

最简单的方式是使用 cell tags，在代码 cell 上添加标签：

| 标签 | 效果 |
|------|------|
| `remove-cell` | 完全移除该 cell（源码和输出都不渲染） |
| `remove-input` | 移除源码（只显示输出） |
| `remove-output` | 移除输出（只显示源码） |
| `remove-stderr` | 仅移除 stderr 输出 |
| `hide-input` | 折叠源码（有展开/折叠按钮） |
| `hide-output` | 折叠输出 |

文本格式示例：
````markdown
```{code-cell}
:tags: [remove-input]

# 源码会被移除，只显示输出
print("只显示输出")
```
````

.ipynb 格式：在 cell metadata 的 tags 数组中添加标签。

## 配置项控制

### 全局设置

```python
nb_remove_code_source = False   # 全局移除所有 code cell 源码
nb_remove_code_outputs = False  # 全局移除所有 code cell 输出
nb_scroll_outputs = False       # 全局启用输出滚动
nb_number_source_lines = False  # 全局显示代码行号
```

### 文件级设置（frontmatter）

```markdown
---
file_format: mystnb
mystnb:
  remove_code_source: false
  remove_code_outputs: false
  scroll_outputs: true
  number_source_lines: true
---
```

### Cell 级设置

````markdown
```{code-cell}
---
mystnb:
  remove_code_source: true
  scroll_outputs: true
  number_source_lines: true
---
print("源码被移除，输出可滚动")
```
````

## 代码折叠（Hide Code Cell）

使用 `hide-input` 标签创建可折叠的代码块，渲染为带「显示/隐藏代码」按钮的折叠区域：

````markdown
```{code-cell}
:tags: [hide-input]

import matplotlib.pyplot as plt
plt.plot([1,2,3], [4,5,6])
plt.show()
```
````

这会渲染一个可点击展开的代码块，默认折叠，读者可按需展开查看源码。

### 折叠提示自定义

```python
nb_code_prompt_show = "Show code cell {type}"   # {type} 替换为 content/source/outputs
nb_code_prompt_hide = "Hide code cell {type}"
```

文件/Cell 级别也可自定义：
````markdown
```{code-cell}
---
mystnb:
  code_prompt_show: "点击查看实现"
  code_prompt_hide: "隐藏实现"
tags: [hide-input]
---
# 自定义折叠提示
```
````

## 输出滚动

当代码输出很长（如大量文本输出）时，`scroll_outputs` 选项会给输出区域添加滚动条：

```python
nb_scroll_outputs = True  # 全局
```

或 cell 级别：
````markdown
```{code-cell}
---
mystnb:
  scroll_outputs: true
---
for i in range(1000):
    print(f"Line {i}")
```
````

## stderr 控制

通过 `output_stderr` 控制 stderr 输出的去留：

| 值 | 行为 |
|----|------|
| `show` | 正常显示（默认） |
| `remove` | 移除不警告 |
| `remove-warn` | 移除并警告 |
| `warn` | 显示并警告 |
| `error` | 作为错误 |
| `severe` | 严重错误 |

Cell 级别：
````markdown
```{code-cell}
---
mystnb:
  output_stderr: "remove"
---
import warnings
warnings.warn("这条警告会被移除")
```
````

## 代码行号

启用行号显示：

```python
nb_number_source_lines = True
```

Cell 级别：
````markdown
```{code-cell}
---
mystnb:
  number_source_lines: true
---
print("这段代码会显示行号")
```
````

## 流合并

`merge_streams` 将同一 cell 的多个 stdout 输出合并为一个块，stderr 同理：

```python
nb_merge_streams = True
```

适用于 Python 中多次 print 导致输出分段的情况。

## 相关概念

- [渲染与 MIME 类型](06-render-and-mime.md)
- [配置系统](04-config-system.md)
- [MyST Notebook 文件格式](02-notebook-format.md)
- [代码隐藏实战示例](/examples/04-hiding-code.md)
