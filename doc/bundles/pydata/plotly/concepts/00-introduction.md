---
type: concept
title: Plotly.py 简介
description: Plotly.py 是基于 plotly.js 的 Python 交互式可视化库，提供声明式 API、Plotly Express 高级接口、FigureWidget 交互控件及 Dash 集成能力
tags:
  - plotly
  - 入门
  - 可视化
  - plotly-express
  - figurewidget
  - dash
generated:
  by: reference_agent/trae-glm
  at: 2026-08-22T15:00:00Z
verified:
  by: "process:seven-concepts-v"
  at: 2026-08-22T15:30:00Z
status: stable
stale_after: 2027-12-31
sources:
  - plotly/__init__.py
  - plotly/express/__init__.py
  - plotly/graph_objects/__init__.py
---

# Plotly.py 简介

Plotly.py 是一个开源的 Python 交互式可视化库，以 MIT 许可证发布。它是 Plotly 生态系统的 Python 前端，底层基于 JavaScript 图表库 plotly.js 进行渲染，支持超过 40 种图表类型，涵盖科学计算、金融、地理、统计、3D 等领域。

## 核心特性

### 声明式 API

Plotly.py 采用声明式（Declarative）编程模型：用户描述"图表应该是什么样子"，而非"如何一步步绘制图表"。一个完整的图表由 `Figure` 对象表示，包含 `data`（数据轨迹）和 `layout`（布局配置）两大部分：

```python
import plotly.graph_objects as go

fig = go.Figure(
    data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6], mode="lines+markers")],
    layout=go.Layout(title="我的第一张图表")
)
fig.show()
```

### 基于 plotly.js 渲染

所有图表最终被序列化为 JSON 结构，传递给前端的 plotly.js 库进行渲染。这意味着：

- 生成的图表天然支持**交互操作**：缩放、平移、悬停提示、图例切换、下载 PNG 等
- 同一 Figure 对象可在多种环境中渲染：Jupyter Notebook、浏览器、HTML 文件、静态图片
- 图表输出为自包含的 HTML 文件，无需额外服务器即可查看

### Plotly Express 高级 API

`plotly.express`（通常缩写为 `px`）是 Plotly.py 提供的高级封装，用一行代码即可创建复杂图表：

```python
import plotly.express as px

df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species",
                 marginal_x="histogram", marginal_y="box")
fig.show()
```

Plotly Express 自动处理：
- DataFrame 列到图形属性的映射
- 颜色/符号/大小的图例生成
- Facet 分面图布局
- Marginal 分布图
- 动画帧生成
- 坐标轴标签和标题设置

### FigureWidget 交互控件

`plotly.graph_objects.FigureWidget` 是基于 ipywidgets 的交互式 Figure 子类，可在 Jupyter Notebook/Lab 中实现：

- 实时属性修改：Python 端修改属性即时反映到前端
- 事件回调：悬停、点击、选择、框选等用户交互可触发 Python 回调函数
- 与其他 ipywidgets 控件联动（滑块、下拉菜单等）

```python
import plotly.graph_objects as go

fig = go.FigureWidget(data=[go.Scatter(x=[1,2], y=[3,4])])

def handle_click(trace, points, state):
    print(f"点击了点: {points.point_inds}")

fig.data[0].on_click(handle_click)
fig  # 在 Jupyter 中显示
```

### 与 Dash 集成

Plotly.py 是 [Dash](https://dash.plotly.com/) 框架的图表渲染后端。Dash 是 Plotly 公司推出的 Python Web 应用框架，专门用于构建数据可视化仪表板，无需编写 JavaScript：

- `dcc.Graph` 组件直接接受 Plotly Figure 对象
- Figure 的属性可以通过回调函数（callback）与其他 Dash 组件联动
- 支持在 Dash 应用中实现复杂的交互过滤、钻取和实时更新

## 版本与安装

- 版本号通过 `importlib.metadata.version("plotly")` 动态获取
- 安装：`pip install plotly`
- 完整功能安装（含 Plotly Express 依赖）：`pip install "plotly[express]"`
- Jupyter Lab 支持需要安装 `jupyterlab>=3`（Plotly 6.x 要求）

## 双接口层次

Plotly.py 提供两个层次的 API：

| 层次 | 模块 | 特点 | 适用场景 |
|------|------|------|----------|
| 高级 | `plotly.express` (px) | 一行代码出图，自动布局 | 快速探索、数据分析 |
| 低级 | `plotly.graph_objects` (go) | 完全控制每个属性 | 精细定制、复杂图表 |

两者可以混合使用——通常用 Plotly Express 创建基础图表，再用 graph_objects 方法精细调整。

## 生态模块

| 模块 | 功能 |
|------|------|
| `plotly.graph_objects` / `plotly.graph_objs` | 图对象层级（Trace、Layout、Figure） |
| `plotly.express` | 高级快速绘图 API |
| `plotly.io` | 渲染器框架、JSON/HTML/图片 IO、模板系统 |
| `plotly.figure_factory` | 特殊图表工厂（等高线、甘特图、树状图等） |
| `plotly.colors` | 颜色比例尺与颜色转换工具 |
| `plotly.subplots` | 子图创建工具（make_subplots） |
| `plotly.data` | 内置示例数据集 |

## 相关概念

- [Figure 数据模型](01-figure-model.md)
- [Plotly Express](02-plotly-express.md)
- [渲染与 IO](03-rendering-io.md)
- [图对象模型](../references/graph-obj-model.md)
