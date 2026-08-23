---
type: concept
title: "代码块"
description: "code/code-block/sourcecode指令和code-cell可执行单元格的语法、选项、行号控制和高亮机制"
tags: [myst-syntax, code, code-block, code-cell, syntax-highlighting, line-numbers]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/code.ts"
    facts: [F-S014, F-S015, F-S016, F-S017]
---

# 代码块

MyST 提供两种代码块指令：`code`（静态代码展示）和 `code-cell`（可执行代码单元格）。

## Code 指令

### 基本语法

````markdown
```{code} python
print("Hello, MyST!")
```
````

`code` 有两个别名：`code-block` 和 `sourcecode`，效果相同：

````markdown
```{code-block} python
:linenos:

def hello():
    print("Hello!")
```
````

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| language | String | 否 | 代码语言（python/typescript/javascript/ts/js 等），用于语法高亮 |

### 选项

| 选项 | 类型 | 别名 | 说明 |
|------|------|------|------|
| `:caption:` | myst | - | 代码标题（解析为 MyST），有标题时代码块包裹在带编号的容器中 |
| `:linenos:` | Boolean | - | 显示行号 |
| `:lineno-start:` | Number | - | 行号起始值，自动启用行号 |
| `:number-lines:` | Number | - | 行号起始值（替代方案），>1 时生效 |
| `:lineno-match:` | Boolean | - | 行号匹配源文件（与 include 配合使用） |
| `:emphasize-lines:` | String | - | 高亮行，支持范围如 "3,5,7-9" |
| `:filename:` | String | - | 显示文件名标签 |
| `:class:` | String | - | CSS 类名 |
| `:label:` | String | name | 交叉引用标签 |

### 行号控制

- `:linenos:`：从 1 开始显示行号
- `:lineno-start: 10`：从第 10 行开始编号（自动启用行号）
- `:number-lines: 5`：从第 5 行开始编号
- `:lineno-match:`：匹配源文件行号（与 include 指令配合，显示被包含文件的原始行号）

注意：同时使用 `:lineno-start:` 和 `:number-lines:` 会产生警告。

### 高亮行

`:emphasize-lines:` 支持逗号分隔的行号和范围：

````markdown
```{code} python
:emphasize-lines: 2,4-6

def example():
    x = 1          # 第2行高亮
    y = 2
    z = 3          # 第4行高亮
    if x == 1:     # 第5行高亮
        return z   # 第6行高亮
```
````

无效的行号格式（如 "a-b"、"5-3" 反向范围）会产生警告。

### 文件名标签

````markdown
```{code} python
:filename: hello.py

print("Hello!")
```
````

### 带标题的代码块

当设置 `:caption:` 时，代码块自动包裹在 `container(kind:'code')` 中，标题显示为 caption，并参与编号：

````markdown
```{code} python
:caption: 一个简单的Python函数
:label: code-hello

def hello():
    print("Hello, MyST!")
```
````

可以通过 `{ref}`code-hello`` 引用此代码块。

## Code-Cell 指令

`code-cell` 用于可执行 Jupyter Notebook 单元格：

````markdown
```{code-cell} python
:tags: [remove-input, hide-cell]

import numpy as np
x = np.linspace(0, 10, 100)
```
````

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| language | String | 执行和显示的语言，默认为 Notebook 或文件的语言 |

### 特有选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `:tags:` | String | 逗号分隔或 YAML 数组的标签列表 |

Tags 支持三种格式：
1. 逗号分隔：`:tags: remove-input, hide-cell`
2. 空格分隔：`:tags: remove-input hide-cell`
3. YAML 数组：`:tags: [remove-input, hide-cell]`

常用标签：
- `remove-input`：隐藏输入代码，只显示输出
- `remove-output`：隐藏输出
- `hide-cell`：折叠单元格
- `hide-input`：折叠输入
- `hide-output`：折叠输出

### Code-Cell 输出结构

code-cell 生成的 MDAST 结构：

```
block(kind: NotebookCell.code)
  ├── code(lang, executable:true, value, emphasizeLines, showLineNumbers, ...)
  └── outputs(id: nanoid(), children: [])
```

outputs 节点是执行结果的占位符，执行后会被填充。有 caption 时，caption 信息存入 block.data.caption，由后续 transform 转换为 figure。

## 标准 Markdown 代码块

除了指令形式，标准 Markdown 围栏代码块也支持：

````markdown
```python
print("Hello!")
```
````

这种方式不支持选项和标题，适合简单代码展示。需要选项时使用 `{code}` 指令。

## 相关概念

- [指令与角色基础](00-directive-role-basics.md)
- [包含与嵌入](07-include-embed.md) — literalinclude 自动以代码块形式展示文件内容
