---
type: Example
title: 交互式地图可视化
description: 使用 folium 创建简单交互式地图，使用 ipyleaflet+bqplot 实现地图与图表联动的高级交互
tags: [maps, folium, ipyleaflet, bqplot, geojson, interactive-maps, geospatial]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: notebook-catalog
    resource: /references/notebook-catalog.md
    title: 笔记本目录信源
---

## 概述

本文档演示 JupyterLite 中两种地图可视化方案：folium（轻量简单）和 ipyleaflet（高度交互+控件联动）。选择 **Python (Pyodide)** 内核。

## Folium 简单地图

folium 基于 Leaflet.js，创建地图简单直接：

```python
%pip install -q folium
import folium
```

### 创建基础地图

```python
# 创建地图，指定中心点和缩放级别
m = folium.Map(location=[50.693848, -1.304734], zoom_start=11)
m
```

执行后显示一个可交互的地图，支持缩放、平移。

### 添加标记

```python
m = folium.Map(location=[39.9042, 116.4074], zoom_start=12)  # 北京

# 添加标记
folium.Marker(
    [39.9163, 116.3972],
    popup='<b>天安门</b>',
    tooltip='点击查看'
).add_to(m)

m
```

### 添加 GeoJSON 图层

```python
# 使用本地 GeoJSON 数据（content/data/ 目录下的文件）
import json

# 华盛顿特区博物馆数据（Demo 自带）
with open('data/Museums_in_DC.geojson', 'r') as f:
    dc_museums = json.load(f)

m = folium.Map(location=[38.9072, -77.0369], zoom_start=12)
folium.GeoJson(dc_museums, name="DC Museums").add_to(m)
folium.LayerControl().add_to(m)
m
```

## ipyleaflet 高级交互地图

ipyleaflet 是 Jupyter 原生的交互式地图库，支持与 ipywidgets 和 bqplot 联动：

```python
%pip install -q bqplot ipyleaflet
```

### 导入依赖

```python
import os, json
import numpy as np
import pandas as pd
from datetime import datetime

from js import fetch
from ipywidgets import Dropdown
from bqplot import Lines, Figure, LinearScale, DateScale, Axis
from ipyleaflet import Map, GeoJSON, WidgetControl
```

### 加载地图数据

使用 `js.fetch` 从网络加载 GeoJSON 数据：

```python
# 加载国家边界 GeoJSON
URL = "https://raw.githubusercontent.com/jupyter-widgets/ipyleaflet/master/examples/countries.geo.json"
res = await fetch(URL)
text = await res.text()
countries = json.loads(text)

# 加载各国经济数据
URL = "https://raw.githubusercontent.com/jupyter-widgets/ipyleaflet/master/examples/nations.json"
res = await fetch(URL)
text = await res.text()
data = pd.read_json(text)
```

### 数据预处理

```python
def clean_data(data):
    for column in ['income', 'lifeExpectancy', 'population']:
        data = data.drop(data[data[column].apply(len) <= 4].index)
    return data

def extrap_interp(data):
    data = np.array(data)
    x_range = np.arange(1800, 2009, 1.)
    y_range = np.interp(x_range, data[:, 0], data[:, 1])
    return y_range

def extrap_data(data):
    for column in ['income', 'lifeExpectancy', 'population']:
        data[column] = data[column].apply(extrap_interp)
    return data

data = clean_data(data)
data = extrap_data(data)
```

### 创建 bqplot 图表

```python
date_start = datetime(1800, 12, 31)
date_end = datetime(2009, 12, 31)
date_scale = DateScale(min=date_start, max=date_end)
date_data = pd.date_range(start=date_start, end=date_end, freq='A', normalize=True)

country_name = 'China'
data_name = 'income'

x_data = data[data.name == country_name][data_name].values[0]
x_scale = LinearScale()

lines = Lines(x=date_data, y=x_data, scales={'x': date_scale, 'y': x_scale})
ax_x = Axis(label='Year', scale=date_scale, num_ticks=10, tick_format='%Y')
ax_y = Axis(label=data_name.capitalize(), scale=x_scale, orientation='vertical', side='left')

figure = Figure(axes=[ax_x, ax_y], title=country_name, marks=[lines],
                animation_duration=500,
                layout={'max_height': '250px', 'max_width': '400px'})
```

### 更新函数

```python
def update_figure(country_name, data_name):
    try:
        lines.y = data[data.name == country_name][data_name].values[0]
        ax_y.label = data_name.capitalize()
        figure.title = country_name
    except IndexError:
        pass
```

### 创建地图并添加图层

```python
m = Map(zoom=3)

geo = GeoJSON(
    data=countries,
    style={'fillColor': 'white', 'weight': 0.5},
    hover_style={'fillColor': '#1f77b4'},
    name='Countries'
)
m.add_layer(geo)
```

### 悬停事件绑定

鼠标悬停在国家上时更新图表：

```python
def on_hover(event, feature, **kwargs):
    global country_name
    country_name = feature['properties']['name']
    update_figure(country_name, data_name)

geo.on_hover(on_hover)
```

### 添加图表控件

将 bqplot 图表作为 WidgetControl 嵌入地图：

```python
widget_control1 = WidgetControl(widget=figure, position='bottomright')
m.add_control(widget_control1)
```

### 添加下拉选择器

```python
dropdown = Dropdown(
    options=['income', 'population', 'lifeExpectancy'],
    value=data_name,
    description='Plotting:'
)

def on_click(change):
    global data_name
    data_name = change['new']
    update_figure(country_name, data_name)

dropdown.observe(on_click, 'value')

widget_control2 = WidgetControl(widget=dropdown, position='bottomleft')
m.add_control(widget_control2)

m  # 显示地图
```

鼠标悬停在任意国家上，右下角图表自动更新为该国的收入/人口/预期寿命数据；左下角下拉框可切换数据维度。

## folium vs ipyleaflet 对比

| 特性 | folium | ipyleaflet |
|------|--------|------------|
| 易用性 | ⭐⭐⭐⭐⭐ 一行代码创建地图 | ⭐⭐⭐ 需要更多设置 |
| 交互性 | 基础交互（缩放/弹窗） | 高度交互（事件回调/控件联动） |
| 控件扩展 | 有限 | 丰富（WidgetControl 嵌入任意 widget） |
| 数据更新 | 重新渲染整个地图 | 属性绑定，实时更新 |
| 依赖大小 | 较大（包含完整 Leaflet） | 适中 |
| 适用场景 | 快速创建静态/半交互地图 | 需要控件联动的复杂应用 |

## 相关概念

- [Pyodide 生态库与 %pip 安装](/concepts/05-pyodide-libraries.md)
- [内容目录与数据文件组织](/concepts/04-content-and-data.md)
- [交互式控件实战](/examples/04-interactive-widgets.md)
- [数据可视化实战](/examples/03-data-visualization.md)
- [创意编程与物理模拟](/examples/06-creative-coding.md)
