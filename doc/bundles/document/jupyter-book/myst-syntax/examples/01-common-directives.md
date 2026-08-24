---
type: example
title: "常用指令实战"
description: "admonition/code/figure/table/math等常用指令的完整示例"
tags: [example, directives, admonition, code, figure, table, math]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "mystmd/packages/myst-directives/src/"
  - path: "mystmd/packages/myst-roles/src/"
---

# 常用指令实战

本文档提供 MyST 常用指令的完整可运行示例。

## 提示框（Admonition）

### 基础提示框

```markdown
:::{note}
这是一条备注信息。
:::

:::{tip}
使用 `myst start` 启动热重载开发服务器。
:::

:::{warning}
删除操作不可恢复，请谨慎执行。
:::

:::{danger}
高压危险！请勿在通电时打开机箱。
:::
```

### 自定义标题

```markdown
:::{admonition} 我的自定义标题
:class: tip

这是一个自定义标题、自定义样式的提示框。
:::

:::{note} 注意
这是一个有标题的 note。
:::
```

### 可折叠提示框

```markdown
:::{note} 点击展开答案
:open: false

答案是 42。
:::
```

### 隐藏图标

```markdown
:::{important}
:icon: false

这是一个没有图标的重要提示。
:::
```

### 11 种提示框类型

```markdown
:::{note} 备注 :::
:::{tip} 提示 :::
:::{hint} 暗示 :::
:::{important} 重要 :::
:::{warning} 警告 :::
:::{caution} 小心 :::
:::{attention} 注意 :::
:::{danger} 危险 :::
:::{error} 错误 :::
:::{seealso} 另见 :::
```

## 代码块

### 基础代码块

````markdown
```{code} python
print("Hello, MyST!")
```
````

### 带行号

````markdown
```{code-block} python
:linenos:

def fibonacci(n):
    """计算斐波那契数列"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```
````

### 指定行号起始值

````markdown
```{code} python
:lineno-start: 10

# 这是第10行
def hello():
    print("Hello!")
```
````

### 高亮行

````markdown
```{code} python
:emphasize-lines: 2,4-5

def example():
    x = 1          # 这行高亮
    y = 2
    if x == 1:     # 这行高亮
        return y   # 这行高亮
```
````

### 文件名标签

````markdown
```{code} python
:filename: hello.py

print("Hello, World!")
```
````

### 带标题和标签（可引用）

````markdown
```{code} python
:caption: 斐波那契数列递归实现
:label: code-fibonacci

def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)
```

参见 {ref}`code-fibonacci` 中的斐波那契实现。
````

## 图片与图表

### 基础图片

```markdown
:::{image} images/photo.png
:width: 300px
:alt: 照片描述
:align: center
:::
```

### 带标题和编号的图表

````markdown
:::{figure} images/architecture.png
:width: 90%
:alt: 系统架构图
:label: fig-architecture

**图1**：系统架构概览，展示了三个核心模块的关系。
:::

如 {ref}`fig-architecture` 所示...
````

### 可执行代码单元格

````markdown
```{code-cell} python
:tags: [remove-input]

import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2*np.pi, 100)
plt.plot(x, np.sin(x))
plt.title("Sine Wave")
plt.show()
```
````

## 表格

### Markdown 表格（带标题）

````markdown
:::{table} 常用编程语言对比
:label: tbl-languages

| 语言 | 类型 | 用途 |
|------|------|------|
| Python | 解释型 | 数据科学、Web |
| TypeScript | 编译型 | Web前端 |
| Rust | 编译型 | 系统编程 |
:::
````

### CSV 表格

````markdown
:::{csv-table} 学生成绩
:header-rows: 1
:delim: comma

姓名,科目,分数
张三,数学,95
李四,数学,88
王五,数学,92
:::
````

### 列表表格（复杂内容）

````markdown
:::{list-table} 功能对比表
:header-rows: 1

*   - 功能
    - 免费版
    - 专业版
*   - 基础编辑
    - ✅
    - ✅
*   - 协作编辑
    - ❌
    - ✅
*   - 导出PDF
    - ❌
    - ✅
:::
````

## 数学公式

### 行内公式

```markdown
质能方程 $E=mc^2$ 是爱因斯坦提出的。
圆的面积公式为 {math}`A = \pi r^2`。
```

### 块级公式（带标签可引用）

````markdown
```{math}
:label: eq-quadratic

x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
```

求根公式（{eq}`eq-quadratic`）用于解一元二次方程。
````

### 多行对齐

````markdown
```{math}
\begin{aligned}
\nabla \times \vec{E} &= -\frac{\partial \vec{B}}{\partial t} \\
\nabla \times \vec{B} &= \mu_0\vec{J} + \mu_0\epsilon_0\frac{\partial \vec{E}}{\partial t}
\end{aligned}
```
````

## 下拉折叠面板

```markdown
:::{dropdown} 点击查看详细说明
:open: false

这里是折叠的详细内容，可以包含 **Markdown** 格式的文本、代码块、图片等。

```{code} python
print("嵌套的代码块也可以")
```
:::
```

## Iframe 嵌入

```markdown
:::{iframe} https://example.com
:width: 100%
:title: 示例网站
:placeholder: images/screenshot.png

嵌入的外部网页（PDF导出时显示占位图）
:::
```
