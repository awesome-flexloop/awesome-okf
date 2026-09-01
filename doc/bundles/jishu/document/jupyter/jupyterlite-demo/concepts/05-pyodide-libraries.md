---
type: Concept
title: Pyodide 生态库与 %pip 安装机制
description: JupyterLite 中 %pip install 的工作原理、预装包 vs 按需安装策略、支持的库类型，以及常见数据可视化和交互库的使用模式
tags: [pyodide, pip-install, micropip, libraries, visualization, widgets, wasm-packages]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: requirements
    resource: /references/requirements-source.md
    title: 依赖配置信源
  - id: notebook-catalog
    resource: /references/notebook-catalog.md
    title: 笔记本目录信源
---

## %pip install 的工作原理

JupyterLite 的 Pyodide 内核支持在笔记本中使用 `%pip install` 命令安装第三方 Python 包，但这与传统 Jupyter 中的 pip install 有本质区别。

### 底层机制

`%pip install` 实际上调用的是 Pyodide 的 [micropip](https://pyodide.org/en/stable/usage/loading-packages.html) 工具，而非传统的 pip：

1. 当执行 `%pip install altair` 时，内核将命令转发给 micropip
2. micropip 从 PyPI 下载纯 Python wheel（`*-py3-none-any.whl`）
3. 包被安装到浏览器的虚拟文件系统（Emscripten MEMFS/IDBFS）
4. 安装的包仅在当前浏览器会话中可用
5. 刷新页面后，已安装的包可能需要重新安装（除非配置了持久化）

### 关键限制

| 限制 | 说明 | 解决方案 |
|------|------|----------|
| 仅纯 Python wheel | 包含 C 扩展的包（`.so`/`.dll`）无法直接安装 | 使用 Pyodide 预编译包（如 numpy、pandas） |
| 网络下载 | 每次新会话需要重新下载包 | 常用包在 requirements.txt 中预装 |
| 包大小 | 大型包下载耗时 | 考虑使用更轻量的替代库 |
| CORS 限制 | 从某些 PyPI 镜像下载可能被 CORS 阻止 | 使用支持 CORS 的 CDN 或 PyPI 官方 |

## 预装 vs 按需安装策略

Demo 展示了两种包管理策略的组合使用：

### 预装包（requirements.txt）

预装包在构建时打入站点，用户打开站点即可使用，无需等待下载：

| 类别 | 预装包 | 预装理由 |
|------|--------|----------|
| 核心框架 | jupyterlite-core, jupyterlab, notebook | 站点必须 |
| 内核 | pyodide-kernel, javascript-kernel, p5-kernel | 内核必须 |
| 控件基础 | ipywidgets, ipyevents | 交互控件基础依赖 |
| 渲染扩展 | jupyterlab-fasta, jupyterlab-geojson | 文件渲染 |
| 主题 | jupyterlab-night, jupyterlab_miami_nights | UI 增强 |
| 常用控件 | ipympl, ipycanvas, ipyleaflet | 交互演示需要 |
| 绘图 | plotly, bqplot | 可视化核心库 |

预装包的特点：
- 包含 JupyterLab 扩展（前端 JS/CSS 资源），必须在构建时安装
- 包的前端资源被构建工具自动打包到静态站点
- 增加站点体积，但减少用户等待时间

### 按需安装（%pip install）

用户在笔记本中通过 `%pip install -q <package>` 安装的包：

| 类别 | 按需安装包 | 按需理由 |
|------|-----------|----------|
| 统计可视化 | altair, vega_datasets | 非所有用户需要 |
| 地图 | folium | 大型依赖链，按需加载 |
| 数据格式化 | nbformat | plotly 的依赖，按需安装 |

这些包通常是**纯 Python** 包，不包含 JupyterLab 前端扩展，可以在浏览器端通过 micropip 安装。

### Demo 笔记本中的安装模式

几乎所有 Pyodide 示例笔记本的第一个代码单元都是安装命令：

```python
# altair.ipynb
%pip install -q altair

# plotly.ipynb
%pip install -q nbformat plotly

# folium.ipynb
%pip install -q folium

# ipycanvas.ipynb
%pip install -q ipycanvas
```

`-q`（quiet）标志抑制安装输出，保持笔记本整洁。

## 数据可视化库使用模式

Demo 展示了三类主流 Python 可视化库在 JupyterLite 中的使用：

### Matplotlib（基础绘图）

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 10, 1000)
plt.plot(x, np.sin(x))
plt.show()
```

支持交互式后端：
```python
%pip install -q ipympl
%matplotlib widget
# 之后绘制的图表支持缩放、平移
```

### Altair（声明式统计可视化）

```python
%pip install -q altair
import altair as alt
import pandas as pd

source = pd.DataFrame({'a': ['A','B','C'], 'b': [28, 55, 43]})
alt.Chart(source).mark_bar().encode(x='a', y='b')
```

支持交互式选择（brush selection）、地理可视化（topo_feature）等高级功能。

### Plotly（交互式图表）

```python
%pip install -q nbformat plotly
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(y=[2, 1, 4, 3]))
fig.add_trace(go.Bar(y=[1, 4, 3, 2]))
fig.show()
```

支持表格、矢量场（quiver）、3D 图表等丰富类型。

## 交互式控件库使用模式

### ipywidgets（基础控件）

```python
%pip install -q ipywidgets
from ipywidgets import IntSlider, IntText, link

slider = IntSlider()
slider  # 显示滑块
slider.value  # 读取值

text = IntText()
link((slider, 'value'), (text, 'value'))  # 双向绑定
```

### bqplot（交互式图表）

```python
from bqplot import *
import numpy as np

x = list(range(100))
y = np.cumsum(np.random.randn(100)) + 100
lines = Lines(x=x, y=y, scales={'x': LinearScale(), 'y': LinearScale()})
Figure(marks=[lines], axes=[Axis(scale=LinearScale()), Axis(scale=LinearScale(), orientation='vertical')])
```

支持动画更新（`animation_duration=1000`）和动态数据绑定。

### ipyleaflet（交互式地图）

```python
%pip install -q bqplot ipyleaflet
from ipyleaflet import Map, GeoJSON, WidgetControl

m = Map(zoom=3)
geo = GeoJSON(data=countries, hover_style={'fillColor': '#1f77b4'})
m.add_layer(geo)
m  # 显示地图
```

支持通过 `WidgetControl` 将 ipywidgets 控件嵌入地图。

### ipycanvas（Canvas 绘图）

```python
%pip install -q ipycanvas
from ipycanvas import RoughCanvas, hold_canvas

canvas = RoughCanvas(width=400, height=400)
with hold_canvas(canvas):
    canvas.fill_style = 'blue'
    canvas.fill_rect(0, 0, 100, 100)
canvas
```

支持 RoughCanvas（手绘风格）、动画循环（配合 asyncio.sleep）。

## 网络请求模式

Pyodide 内核中，可以通过 `from js import fetch` 直接使用浏览器 Fetch API 获取网络资源：

```python
from js import fetch
import json
import pandas as pd
from io import StringIO

# 获取 JSON 数据
res = await fetch('https://api.example.com/data')
data = json.loads(await res.text())

# 获取 CSV 数据
res = await fetch('https://example.com/data.csv')
df = pd.read_csv(StringIO(await res.text()))

# 下载文件到虚拟文件系统
res = await fetch('https://example.com/file.csv')
with open('local_file.csv', 'w') as f:
    f.write(await res.text())
```

## 动态显示更新

Pyodide 支持 `display_id` + `update_display` 实现单元格输出的动态更新：

```python
from IPython.display import display, update_display

class Square:
    def _repr_html_(self):
        return f'<div style="background:{self.color};width:200px;height:100px"></div>'

square = Square()
square.color = 'PeachPuff'
display(square, display_id='my-square')

# 后续单元格中更新
square.color = 'OliveDrab'
update_display(square, display_id='my-square')
```

## 相关概念

- [三大内核生态对比](03-kernel-ecosystem.md)
- [内容目录与数据文件组织](04-content-and-data.md)
- [站点配置详解](02-site-configuration.md)
- [Python 基础使用示例](../examples/02-python-basics.md)
- [数据可视化实战](../examples/03-data-visualization.md)
- [交互式控件实战](../examples/04-interactive-widgets.md)
