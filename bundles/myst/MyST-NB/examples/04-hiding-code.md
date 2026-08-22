---
type: Example
title: 代码隐藏与输出控制实战
description: 使用 cell tags 和 mystnb metadata 控制代码显示/隐藏、输出滚动、stderr 处理
tags: [myst-nb, hide, remove, scroll, toggle, code-cell]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

## 代码隐藏与输出控制实战

本示例展示如何使用 cell tags 和 mystnb metadata 精细控制代码和输出的显示。

## conf.py 基础配置

```python
extensions = ["myst_nb"]
nb_execution_mode = "cache"

# 全局默认：显示所有代码和输出
nb_remove_code_source = False
nb_remove_code_outputs = False
nb_scroll_outputs = False
nb_output_stderr = "show"
```

## 常用 Cell Tags

### remove-cell：完全移除 cell

````markdown
```{code-cell}
:tags: [remove-cell]

# 这段代码和输出都不会出现在文档中
# 适合放初始化代码、数据加载等读者不需要看到的内容
import os
import sys
sys.path.insert(0, os.path.abspath("../src"))
```
````

### remove-input：只显示输出

````markdown
```{code-cell}
:tags: [remove-input]

# 源码会被移除，只显示图表
import matplotlib.pyplot as plt
plt.plot([1,2,3], [4,5,6])
plt.title("读者只看到图，不需要看到绘图代码")
plt.show()
```
````

### remove-output：只显示源码

````markdown
```{code-cell}
:tags: [remove-output]

# 输出会被移除，只显示代码
print("这条输出不会显示")
```
````

### remove-stderr：只移除 stderr

````markdown
```{code-cell}
:tags: [remove-stderr]

import warnings
warnings.warn("这个警告不会显示")
print("正常输出仍然显示")
```
````

### hide-input：可折叠代码块

````markdown
```{code-cell}
:tags: [hide-input]

# 代码默认折叠，读者可以点击"显示代码"展开
def complex_calculation(x):
    """一个复杂的计算函数"""
    result = 0
    for i in range(1000):
        result += x ** i / (i + 1)
    return result

print(f"Result: {complex_calculation(0.5):.6f}")
```
````

渲染效果：代码区域默认折叠，显示"Show code cell source"按钮，点击展开。

### hide-output：可折叠输出

````markdown
```{code-cell}
:tags: [hide-output]

for i in range(100):
    print(f"Line {i}: some output that can be collapsed")
```
````

### 多个标签组合

````markdown
```{code-cell}
:tags: [hide-input, remove-stderr]

# 代码可折叠，stderr 被移除
import warnings
warnings.warn("警告被移除")
print("代码可折叠展开，正常输出显示")
```
````

## 使用 mystnb metadata 精细控制

### 滚动长输出

````markdown
```{code-cell}
---
mystnb:
  scroll_outputs: true
---
for i in range(500):
    print(f"Long output line {i}")
```
````

渲染效果：输出区域被限制高度并出现滚动条。

### 代码行号

````markdown
```{code-cell}
---
mystnb:
  number_source_lines: true
---
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
```
````

### 自定义折叠提示

```python
# conf.py - 全局自定义
nb_code_prompt_show = "▸ 显示{type}"
nb_code_prompt_hide = "▾ 隐藏{type}"
```

Cell 级别自定义：
````markdown
```{code-cell}
---
mystnb:
  code_prompt_show: "点击查看完整代码"
  code_prompt_hide: "收起代码"
tags: [hide-input]
---
print("自定义折叠提示")
```
````

### stderr 处理

````markdown
```{code-cell}
---
mystnb:
  output_stderr: "remove"
---
import warnings
warnings.warn("stderr 被移除")
```
````

````markdown
```{code-cell}
---
mystnb:
  output_stderr: "warn"
---
# stderr 会显示但带警告标记
```
````

````markdown
```{code-cell}
---
mystnb:
  output_stderr: "error"
---
# stderr 会被当作错误报告
```
````

### 图片选项控制

````markdown
```{code-cell}
---
mystnb:
  image:
    width: 500px
    align: center
    alt: "示例图片"
  figure:
    caption: "带标题和配置的图"
    name: fig-custom
---
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.bar([1,2,3], [4,5,6])
plt.show()
```
````

### 合并输出流

````markdown
```{code-cell}
---
mystnb:
  merge_streams: true
---
import sys
for i in range(5):
    sys.stdout.write(f"out {i} ")
    sys.stderr.write(f"err {i} ")
# merge_streams=true 后 stdout 和 stderr 各自合并为一个块
```
````

## 全局 vs Cell 级配置示例

### 全局移除代码（纯展示文档）

```python
# conf.py - 用于展示型文档（读者只看结果）
nb_remove_code_source = True
nb_remove_code_outputs = False
```

个别 cell 可以覆盖全局设置：
````markdown
```{code-cell}
---
mystnb:
  remove_code_source: false
---
# 这个 cell 的代码会显示（覆盖全局设置）
print("这段代码可见")
```
````

### 教学文档策略

```python
# conf.py - 教学文档
nb_remove_code_source = False   # 默认显示代码
nb_number_source_lines = True   # 显示行号
nb_scroll_outputs = True        # 长输出滚动
nb_output_stderr = "remove-warn" # 移除 stderr 但警告
```

关键代码使用 hide-input，默认折叠：
````markdown
```{code-cell}
:tags: [hide-input]

# 复杂的实现细节，默认折叠
def train_model(epochs=100, lr=0.01):
    # ... 100行训练代码 ...
    pass
model = train_model()
```
````

## 标签与 metadata 选择

| 控制方式 | 优点 | 适用 |
|---------|------|------|
| Cell tags | 简洁、Jupyter 原生 | 简单开关（remove/hide） |
| mystnb metadata | 精细、支持选项值 | 需要参数的控制（宽度/提示文本等） |

## 相关概念

- [代码隐藏与输出控制](/concepts/09-hiding-code.md)
- [渲染与 MIME 类型](/concepts/06-render-and-mime.md)
- [配置系统](/concepts/04-config-system.md)
- [MyST Notebook 语法速查](/references/notebook-cheatsheet.md)
