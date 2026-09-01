---
type: Example
title: Pyodide Python 内核基础使用
description: 在 JupyterLite 中使用 Pyodide 内核进行 Python 编程，涵盖变量、函数、display、magics、网络请求等基础操作
tags: [python, pyodide, basics, display, magics, input, fetch]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: notebook-catalog
    resource: /references/notebook-catalog.md
    title: 笔记本目录信源
---

## 概述

本文档基于 python.ipynb 示例笔记本，演示 JupyterLite Pyodide 内核的基础使用方法。选择 **Python (Pyodide)** 内核即可开始。

## 查看内核版本

```python
import pyodide_kernel
pyodide_kernel.__version__
```

## 基础代码执行

Pyodide 内核支持标准 Python 语法：

```python
# 变量赋值
a = 3
a  # 输出: 3

# 函数定义
b = 89
def sq(x):
    return x * x

sq(b)  # 输出: 7921
```

## 输出与错误处理

### 标准输出和错误流

```python
import sys

# 标准输出
print("Hello from JupyterLite!")

# 标准错误
print("Error message", file=sys.stderr)
```

### 异常处理

Pyodide 内核会正常显示 Python 异常：

```python
def dummy_function():
    import missing_module  # 这个模块不存在

dummy_function()  # 将显示 ModuleNotFoundError
```

## 代码补全与内省

### Tab 补全

在代码单元格中输入部分代码后按 `Tab` 键可查看可用属性和方法：

```python
from sys import
# 将光标放在 from sys import 后面，按 Tab 查看 sys 模块的所有可导入项
```

### 问号内省

使用 `?` 查看对象的文档字符串：

```python
?print
```

### Shift+Tab 提示

在函数调用的括号内按 `Shift+Tab`，显示函数签名和参数说明：

```python
print(
# 将光标放在括号内，按 Shift+Tab
```

## 用户输入

Pyodide 支持 `input()` 函数，但需要使用 `await`：

```python
name = await input('Enter your name: ')
'Hello, ' + name
```

执行后会出现输入框，输入文本后单元格输出问候语。

## 富媒体显示

使用 `IPython.display` 模块输出富媒体内容：

### HTML

```python
from IPython.display import HTML

s = '<h1 style="color:steelblue">HTML Title</h1>'
display(HTML(s))
```

### Markdown

```python
from IPython.display import Markdown

Markdown('''
# Title

**in bold**

~~Strikethrough~~
''')
```

### Pandas DataFrame

```python
import pandas as pd
import numpy as np
from string import ascii_uppercase as letters

df = pd.DataFrame(
    np.random.randint(0, 100, size=(100, len(letters))),
    columns=list(letters)
)
df  # DataFrame 自动以表格形式渲染
```

### 数学公式

```python
from IPython.display import Math, Latex

Math(r'F(k) = \int_{-\infty}^{\infty} f(x) e^{2\pi i k} dx')

Latex(r"""\begin{eqnarray}
\nabla \times \vec{\mathbf{B}} -\, \frac1c\, \frac{\partial\vec{\mathbf{E}}}{\partial t} & = \frac{4\pi}{c}\vec{\mathbf{j}}
\end{eqnarray}""")
```

### JSON

```python
from IPython.display import JSON

JSON(['foo', {'bar': ('baz', None, 1.0, 2)}], expanded=True)
```

### GeoJSON

```python
from IPython.display import GeoJSON

GeoJSON(
  data={
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [11.8, -45.04]}
  },
  url_template="http://s3-eu-west-1.amazonaws.com/whereonmars.cartodb.net/{basemap_id}/{z}/{x}/{y}.png",
  layer_options={"basemap_id": "celestia_mars-shaded-16k_global"}
)
```

## 动态显示更新

### update_display（动态更新输出）

```python
from IPython.display import display, update_display

class Square:
    color = 'PeachPuff'
    def _repr_html_(self):
        return f'<div style="background:{self.color};width:200px;height:100px;border-radius:10px"></div>'

square = Square()
display(square, display_id='my-square')
```

在后续单元格中更新：

```python
square.color = 'OliveDrab'
update_display(square, display_id='my-square')
```

### clear_output（清除输出）

```python
from IPython.display import clear_output
from asyncio import sleep

print("hello")
await sleep(2)
clear_output(wait=True)  # wait=True 防止闪烁
print("goodbye")
```

### ProgressBar

```python
from IPython.display import ProgressBar

for i in ProgressBar(10):
    await sleep(0.1)
```

## 网络请求

使用 `from js import fetch` 调用浏览器 Fetch API：

```python
import json
from js import fetch

res = await fetch('https://httpbin.org/get')
text = await res.text()
obj = json.loads(text)
JSON(obj)
```

## IPython Magics

### %cd 和 %pwd（目录导航）

```python
import os
os.listdir()  # 列出当前目录

%cd /home     # 切换目录
%pwd          # 查看当前目录
```

### %%writefile（写文件）

```python
%%writefile test.txt

This will create a new file.
With the text that you see here.
```

### %history（查看执行历史）

```python
%history
```

### %%timeit（性能测试）

```python
import time

%%timeit
time.sleep(0.1)
```

## 符号计算（SymPy）

```python
from sympy import Integral, sqrt, symbols, init_printing
init_printing()

x = symbols('x')
Integral(sqrt(1 / x), x)
```

## 自定义 _repr_html_

类实现 `_repr_html_` 方法即可自定义 HTML 渲染：

```python
class ColorBox:
    def __init__(self, color, size=100):
        self.color = color
        self.size = size
    def _repr_html_(self):
        return f'<div style="background:{self.color};width:{self.size}px;height:{self.size}px"></div>'

ColorBox('coral', 150)
```

## 相关概念

- [三大内核生态对比](../concepts/03-kernel-ecosystem.md)
- [Pyodide 生态库与 %pip 安装](../concepts/05-pyodide-libraries.md)
- [内容目录与数据文件组织](../concepts/04-content-and-data.md)
- [数据可视化实战](03-data-visualization.md)
- [交互式控件实战](04-interactive-widgets.md)
