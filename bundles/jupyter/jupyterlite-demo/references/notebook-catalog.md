---
type: Reference
title: JupyterLite Demo 笔记本目录信源
description: Demo 仓库中所有示例笔记本的完整目录、内容描述、依赖包和演示技能点登记
tags: [notebooks, catalog, examples, pyodide, kernels, p5, javascript]
source_type: content-directory
source_path: content/
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: content
    resource: https://github.com/jupyterlite/demo/tree/main/content
    title: content/ directory
---

## 根级笔记本（3个，对应三种内核）

| 笔记本 | 内核 | 单元格数 | 核心内容 | 关键 API/特性 |
|--------|------|----------|----------|---------------|
| python.ipynb | Pyodide (Python) | 62 | Pyodide 内核完整功能演示 | pyodide_kernel、IPython.display、%pip、%cd、%writefile、js.fetch、await input、_repr_html_、update_display、clear_output |
| javascript.ipynb | JavaScript | 9 | JS 内核基础演示 | console.log、console.error、setTimeout、Markdown 数学公式 |
| p5.ipynb | p5.js | 14 | p5.js 创意编程最小示例 | setup()、draw()、createCanvas、%show magic、实时变量更新 |

## Pyodide 内核示例（8个）

| 笔记本 | 预装/按需 | 核心内容 | 关键库 |
|--------|-----------|----------|--------|
| altair.ipynb | %pip install altair, vega_datasets | Altair 声明式可视化 | altair.Chart、mark_bar/mark_rect、topo_feature、brush selection |
| matplotlib.ipynb | 预装(numpy) + %pip install ipympl | Matplotlib 基础绘图 + widget 后端 | matplotlib.pyplot、%matplotlib widget、plt.plot、plt.show |
| plotly.ipynb | %pip install nbformat plotly | Plotly 交互式图表 | plotly.graph_objects、go.Figure、go.Table、ff.create_quiver、js.fetch 下载数据 |
| folium.ipynb | %pip install folium | Leaflet.js 地图 | folium.Map、location/zoom_start |
| ipycanvas.ipynb | %pip install ipycanvas | 康威生命游戏动画 | ipycanvas.RoughCanvas、hold_canvas、asyncio.sleep、numpy 向量化运算 |
| ipyleaflet.ipynb | %pip install bqplot ipyleaflet | 交互式地图+图表联动 | ipyleaflet.Map/GeoJSON/WidgetControl、bqplot.Lines/Figure/Axis、ipywidgets.Dropdown |
| interactive-widgets.ipynb | %pip install ipywidgets, bqplot | ipywidgets 控件 + bqplot 图表 | IntSlider、IntText、link()、bqplot.Lines/Bars、animation_duration |
| renderers.ipynb | 无需安装 | JupyterLab MIME 渲染器 | application/vnd.fasta.fasta、application/geo+json、display(raw=True) |

## Pyodide/pyb2d 物理引擎示例（8个）

| 笔记本 | 类别 | 内容描述 |
|--------|------|----------|
| 0_tutorial.ipynb | 入门 | Box2D 物理引擎基础教程 |
| color_mixing.ipynb | 模拟 | 颜色混合模拟 |
| gauss_machine.ipynb | 模拟 | 高斯机/统计演示 |
| newtons_cradle.ipynb | 模拟 | 牛顿摆物理模拟 |
| games/angry_shapes.ipynb | 游戏 | 愤怒的小鸟类弹射游戏 |
| games/billiard.ipynb | 游戏 | 台球碰撞模拟 |
| games/goo.ipynb | 游戏 | 粘粘世界类软物体游戏 |
| games/rocket.ipynb | 游戏 | 火箭发射模拟 |

## 数据文件（5个）

| 文件 | 格式 | 用途 |
|------|------|------|
| Museums_in_DC.geojson | GeoJSON | 华盛顿特区博物馆地理位置数据 |
| bar.vl.json | Vega-Lite JSON | Vega-Lite 条形图规范示例 |
| fasta-example.fasta | FASTA | 蛋白质/DNA 序列示例数据 |
| iris.csv | CSV | 鸢尾花经典数据集 |
| matplotlib.png | PNG | Matplotlib 输出示例图片 |

## 笔记本执行模式

- 所有 Pyodide 笔记本第一个代码单元均为 `%pip install -q <packages>` 安装依赖
- 支持 top-level await（如 `await fetch(URL)`、`await input()`、`await asyncio.sleep()`）
- 支持通过 `from js import fetch` 直接调用浏览器 Fetch API
- 支持 `display(bundle, raw=True)` 输出自定义 MIME 类型数据
- p5 内核通过 `%show` magic 命令渲染画布
