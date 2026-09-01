---
type: Example
title: 数据可视化实战
description: 在 JupyterLite 中使用 Matplotlib、Altair、Plotly 三大可视化库进行数据绘图，涵盖基础图表和交互式可视化
tags: [visualization, matplotlib, altair, plotly, charts, data-viz]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: notebook-catalog
    resource: /references/notebook-catalog.md
    title: 笔记本目录信源
---

## 概述

本文档演示 JupyterLite 中三大 Python 可视化库的使用：Matplotlib（基础绘图）、Altair（声明式统计图表）、Plotly（交互式图表）。选择 **Python (Pyodide)** 内核。

## Matplotlib 基础绘图

numpy 和 matplotlib 在 Pyodide 内核中已预装，无需 %pip install：

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 10, 1000)
plt.plot(x, np.sin(x))
plt.show()
```

### Matplotlib 交互式后端

安装 ipympl 启用交互式绘图（支持缩放、平移）：

```python
%pip install -q ipympl
```

```python
%matplotlib widget

x = np.linspace(0, 10, 1000)
plt.plot(x, np.sin(x))
```

使用 `%matplotlib inline` 切回静态图片模式。

## Altair 声明式可视化

Altair 基于 Vega-Lite，采用声明式语法描述图表：

```python
%pip install -q altair
import altair as alt
import pandas as pd
```

### 条形图

```python
source = pd.DataFrame({
    'a': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
    'b': [28, 55, 43, 91, 81, 53, 19, 87, 52]
})

alt.Chart(source).mark_bar().encode(
    x='a',
    y='b'
)
```

### 热力图

```python
import numpy as np

x, y = np.meshgrid(range(-5, 5), range(-5, 5))
z = x ** 2 + y ** 2

source = pd.DataFrame({'x': x.ravel(), 'y': y.ravel(), 'z': z.ravel()})

alt.Chart(source).mark_rect().encode(
    x='x:O',
    y='y:O',
    color='z:Q'
)
```

### 交互式选择（Brush Selection）

```python
%pip install -q vega_datasets
from vega_datasets import data

source = data.seattle_weather()
brush = alt.selection(type='interval', encodings=['x'])

bars = alt.Chart().mark_bar().encode(
    x='month(date):O',
    y='mean(precipitation):Q',
    opacity=alt.condition(brush, alt.OpacityValue(1), alt.OpacityValue(0.7)),
).add_selection(brush)

line = alt.Chart().mark_rule(color='firebrick').encode(
    y='mean(precipitation):Q',
    size=alt.SizeValue(3)
).transform_filter(brush)

alt.layer(bars, line, data=source)
```

拖拽选择图表区域可查看选中范围的平均值。

### 地理可视化

```python
airports = data.airports.url
states = alt.topo_feature(data.us_10m.url, feature='states')

# 美国州背景
background = alt.Chart(states).mark_geoshape(
    fill='lightgray', stroke='white'
).properties(width=500, height=300).project('albersUsa')

# 机场位置
points = alt.Chart(airports).transform_aggregate(
    latitude='mean(latitude)',
    longitude='mean(longitude)',
    count='count()',
    groupby=['state']
).mark_circle().encode(
    longitude='longitude:Q',
    latitude='latitude:Q',
    size=alt.Size('count:Q', title='Number of Airports'),
    color=alt.value('steelblue'),
    tooltip=['state:N','count:Q']
).properties(title='Number of airports in US')

background + points
```

## Plotly 交互式图表

Plotly 提供丰富的交互式图表类型：

```python
%pip install -q nbformat plotly
import plotly.graph_objects as go
```

### 基础图形

```python
fig = go.Figure()
fig.add_trace(go.Scatter(y=[2, 1, 4, 3], name='Line'))
fig.add_trace(go.Bar(y=[1, 4, 3, 2], name='Bar'))
fig.update_layout(title='Hello Figure')
fig.show()
```

图表支持悬停查看数据点、缩放、下载 PNG 等交互。

### DataFrame 表格

结合 fetch 从网络加载数据：

```python
import pandas as pd
from js import fetch

URL = "https://raw.githubusercontent.com/plotly/datasets/master/2014_usa_states.csv"
res = await fetch(URL)
text = await res.text()

with open('data.csv', 'w') as f:
    f.write(text)

df = pd.read_csv('data.csv')

fig = go.Figure(data=[go.Table(
    header=dict(values=list(df.columns), fill_color='paleturquoise', align='left'),
    cells=dict(values=[df.Rank, df.State, df.Postal, df.Population],
               fill_color='lavender', align='left'))
])
fig.show()
```

### 矢量场图（Quiver Plot）

```python
import plotly.figure_factory as ff
import numpy as np

x, y = np.meshgrid(np.arange(-2, 2, .2), np.arange(-2, 2, .25))
z = x * np.exp(-x**2 - y**2)
v, u = np.gradient(z, .2, .2)

fig = ff.create_quiver(x, y, u, v, scale=.25, arrow_scale=.4,
                       name='quiver', line_width=1)
fig.add_trace(go.Scatter(x=[-.7, .75], y=[0, 0],
                         mode='markers', marker_size=12, name='points'))
fig.show()
```

## 绘图库选择建议

| 场景 | 推荐库 | 理由 |
|------|--------|------|
| 快速静态图表 | Matplotlib | 预装、简单直接、生态成熟 |
| 统计可视化 | Altair | 声明式语法简洁、交互选择强大 |
| 复杂交互式图表 | Plotly | 图表类型丰富、3D 支持、交互完善 |
| 高性能大数据 | bqplot | Jupyter 原生、基于 d3.js、响应式 |
| 地图可视化 | ipyleaflet/folium | 专业地图库，见地图示例 |

## 相关概念

- [Pyodide 生态库与 %pip 安装](../concepts/05-pyodide-libraries.md)
- [三大内核生态对比](../concepts/03-kernel-ecosystem.md)
- [Python 内核基础使用](02-python-basics.md)
- [交互式控件实战](04-interactive-widgets.md)
- [交互式地图实战](05-interactive-maps.md)
