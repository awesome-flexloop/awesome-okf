---
type: Example
title: 交互式控件与图表
description: 使用 ipywidgets 创建交互式滑块、文本框等控件，结合 bqplot 创建响应式交互式图表
tags: [ipywidgets, bqplot, interactive, widgets, sliders, controls]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: notebook-catalog
    resource: /references/notebook-catalog.md
    title: 笔记本目录信源
---

## 概述

本文档演示 JupyterLite 中 ipywidgets 交互式控件和 bqplot 交互式图表的使用。选择 **Python (Pyodide)** 内核。

## ipywidgets 基础控件

首先安装 ipywidgets：

```python
%pip install -q ipywidgets
```

### IntSlider（整数滑块）

```python
from ipywidgets import IntSlider

slider = IntSlider()
slider
```

显示一个滑块控件，可以拖动改变值。

读取和设置滑块值：

```python
slider.value       # 读取当前值
slider.value = 50  # 程序化设置值
```

### IntText（整数文本框）

```python
from ipywidgets import IntText

text = IntText()
text
```

### 控件联动（link）

使用 `link()` 函数将两个控件的值双向绑定：

```python
from ipywidgets import link

# 滑块和文本框双向联动——拖动滑块文本框更新，输入文本滑块更新
link((slider, 'value'), (text, 'value'))
```

现在拖动滑块，文本框的值同步变化；在文本框中输入数字，滑块位置也同步更新。

### 更多控件

ipywidgets 提供丰富的控件类型：

```python
from ipywidgets import (
    IntSlider, FloatSlider, IntRangeSlider,    # 滑块
    IntText, FloatText, Text, Textarea,         # 文本输入
    Checkbox, ToggleButton,                     # 布尔控件
    Dropdown, RadioButtons, Select,             # 选择控件
    ColorPicker, DatePicker,                    # 特殊输入
    HBox, VBox, Accordion, Tabs,                # 布局控件
    Output                                      # 输出区域
)
```

## bqplot 交互式图表

bqplot 是基于 d3.js 的 Jupyter 原生交互式图表库，图表元素可直接绑定 Python 回调。

```python
%pip install -q bqplot
from bqplot import *
import numpy as np
import pandas as pd
```

### 线形图

```python
np.random.seed(0)
n = 100
x = list(range(n))
y = np.cumsum(np.random.randn(n)) + 100.0

sc_x = LinearScale()
sc_y = LinearScale()

lines = Lines(
    x=x, y=y,
    scales={'x': sc_x, 'y': sc_y}
)
ax_x = Axis(scale=sc_x, label='Index')
ax_y = Axis(scale=sc_y, orientation='vertical', label='Value')

Figure(marks=[lines], axes=[ax_x, ax_y], title='Interactive Lines')
```

### 动态更新图表数据

bqplot 的图表属性可以直接赋值修改，图表会实时更新：

```python
# 更改线条颜色
lines.colors = ['green']

# 添加填充
lines.fill = 'bottom'

# 显示数据点标记
lines.marker = 'circle'
```

### 条形图（带动画）

```python
n = 100
x = list(range(n))
y = np.cumsum(np.random.randn(n))

bars = Bars(
    x=x, y=y,
    scales={'x': LinearScale(), 'y': LinearScale()}
)
ax_x = Axis(scale=LinearScale(), label='Index')
ax_y = Axis(scale=LinearScale(), orientation='vertical', label='Bars')

Figure(marks=[bars], axes=[ax_x, ax_y], title='Animated Bars',
       animation_duration=1000)
```

`animation_duration=1000` 设置数据更新时的动画时长（毫秒）。

动态更新条形图数据：

```python
bars.y = np.cumsum(np.random.randn(n))
```

图表会以动画过渡到新数据。

### ipywidgets + bqplot 联动

结合 ipywidgets 控件和 bqplot 图表，创建交互式数据浏览器：

```python
from ipywidgets import FloatSlider, VBox

# 创建一个控制均值的滑块
mean_slider = FloatSlider(value=0.0, min=-3.0, max=3.0, step=0.1, description='Mean:')

# 创建图表
sc_x = LinearScale()
sc_y = LinearScale()
hist = Bars(x=[], y=[], scales={'x': sc_x, 'y': sc_y})
ax_x = Axis(scale=sc_x, label='Value')
ax_y = Axis(scale=sc_y, orientation='vertical', label='Count')
fig = Figure(marks=[hist], axes=[ax_x, ax_y], title='Normal Distribution')

# 定义更新函数
def update_hist(change):
    y = np.random.normal(change['new'], 1.0, 1000)
    counts, edges = np.histogram(y, bins=30)
    hist.x = edges[:-1].tolist()
    hist.y = counts.tolist()

# 绑定滑块事件
mean_slider.observe(update_hist, names='value')

# 初始更新
update_hist({'new': 0.0})

# 显示
VBox([mean_slider, fig])
```

拖动滑块时，直方图实时更新为对应均值的正态分布。

## 控件布局

使用 HBox/VBox 组合控件：

```python
from ipywidgets import HBox, VBox

# 水平排列两个滑块
h_box = HBox([IntSlider(description='A'), IntSlider(description='B')])

# 垂直排列
v_box = VBox([IntSlider(description='X'), IntSlider(description='Y'), h_box])
v_box
```

## 事件处理

使用 `.observe()` 监听控件属性变化：

```python
from ipywidgets import ToggleButton

btn = ToggleButton(description='Click Me')

def on_toggle(change):
    if change['new']:
        print("Button is ON")
    else:
        print("Button is OFF")

btn.observe(on_toggle, names='value')
btn
```

## 相关概念

- [Pyodide 生态库与 %pip 安装](/concepts/05-pyodide-libraries.md)
- [Python 内核基础使用](/examples/02-python-basics.md)
- [数据可视化实战](/examples/03-data-visualization.md)
- [交互式地图实战](/examples/05-interactive-maps.md)
