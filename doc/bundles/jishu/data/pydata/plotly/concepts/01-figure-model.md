---
type: concept
title: Figure 数据模型
description: 解析 Plotly Figure 的三层结构（data/layout/frames）、graph_objects 对象层级、魔术方法动态属性访问以及 JSON 序列化机制
tags:
  - plotly
  - figure
  - data-model
  - graph-objects
  - json
  - 魔术方法
generated:
  by: reference_agent/trae-glm
  at: 2026-08-22T15:00:00Z
verified:
  by: "process:seven-concepts-v"
  at: 2026-08-22T15:30:00Z
status: stable
stale_after: 2027-12-31
sources:
  - basedatatypes.py (BaseFigure L401, BasePlotlyType L4312)
  - graph_objs/_figure.py (Figure)
  - graph_objs/_layout.py (Layout)
---

# Figure 数据模型

Plotly 的所有图表都由一个 `Figure` 对象表示。理解 Figure 的数据模型是掌握 Plotly.py 的关键——无论是用 Plotly Express 快速绘图，还是用 graph_objects 精细定制，最终操作的都是同一个 Figure 结构。

## Figure 顶层容器

Figure 继承自 BaseFigure，构造函数签名为：

```python
Figure(data=None, layout=None, frames=None, skip_invalid=False, **kwargs)
```

Figure 由三大组件构成：

```
Figure
├── data    → Trace 对象元组（数据系列）
├── layout  → Layout 对象（全局布局配置）
└── frames  → Frame 对象列表（动画帧，可选）
```

构造时支持多种输入形式：

```python
import plotly.graph_objects as go

# 1. 空 Figure
fig = go.Figure()

# 2. 传入 Trace 对象列表
fig = go.Figure(data=[go.Scatter(x=[1,2], y=[3,4]), go.Bar(x=[1,2], y=[5,6])])

# 3. 传入 dict（自动转换）
fig = go.Figure(data=[{"type": "scatter", "x": [1,2], "y": [3,4]}])

# 4. 单个 Trace
fig = go.Figure(data=go.Scatter(x=[1,2], y=[3,4]))

# 5. 完整 dict 结构（含 data/layout/frames 键）
fig = go.Figure({
    "data": [{"type": "scatter", "x": [1,2], "y": [3,4]}],
    "layout": {"title": "标题"}
})

# 6. 从已有 Figure 复制
fig2 = go.Figure(fig)
```

## data：Traces 列表

`data` 是一个 Trace 对象元组，每个 Trace 代表一个数据系列（一条线、一组柱子、一个饼图扇区集合等）。

Trace 类型由 `type` 属性决定，Plotly 支持 40+ 种 Trace 类型：

| 类别 | Trace 类型 | 类名 |
|------|-----------|------|
| 基本散点/折线 | `scatter` | `go.Scatter` |
| WebGL 散点/折线 | `scattergl` | `go.Scattergl` |
| 柱状图 | `bar` | `go.Bar` |
| 饼图 | `pie` | `go.Pie` |
| 热力图 | `heatmap` | `go.Heatmap` |
| 直方图 | `histogram` | `go.Histogram` |
| 箱线图 | `box` | `go.Box` |
| 小提琴图 | `violin` | `go.Violin` |
| 3D 散点 | `scatter3d` | `go.Scatter3d` |
| 3D 曲面 | `surface` | `go.Surface` |
| 3D 网格 | `mesh3d` | `go.Mesh3d` |
| 地图散点 | `scattergeo` / `scattermapbox` | `go.Scattergeo` / `go.Scattermapbox` |
| 等值面 | `isosurface` | `go.Isosurface` |
| 桑基图 | `sankey` | `go.Sankey` |
| 太阳burst | `sunburst` | `go.Sunburst` |
| 树图 | `treemap` | `go.Treemap` |
| K线图 | `candlestick` / `ohlc` | `go.Candlestick` / `go.Ohlc` |
| 漏斗图 | `funnel` / `funnelarea` | `go.Funnel` / `go.Funnelarea` |
| ... | ... | ... |

操作 data 中的 Trace：

```python
fig = go.Figure(data=[go.Scatter(x=[1,2], y=[3,4], name="线1")])

# 添加 Trace
fig.add_trace(go.Bar(x=[1,2], y=[5,6], name="柱1"))
fig.add_traces([go.Scatter(x=[1,2], y=[7,8], name="线2")])

# 访问 Trace
print(fig.data[0].name)  # "线1"

# 批量更新 Trace
fig.update_traces(marker_color="red", selector=dict(type="bar"))

# 选择更新
fig.update_traces(line_dash="dash", selector=dict(name="线2"))
```

## layout：布局配置

`layout` 是一个 Layout 对象，控制图表的全局外观：

```python
fig.layout.title = "销售趋势"
fig.layout.width = 800
fig.layout.height = 500
fig.layout.template = "plotly_dark"
fig.layout.showlegend = True
```

Layout 的主要属性分类：

| 分类 | 属性示例 | 说明 |
|------|----------|------|
| 标题 | `title` | 图表标题（支持 text/font/subtitle） |
| 尺寸 | `width`, `height`, `autosize`, `margin` | 画布大小与边距 |
| 坐标轴 | `xaxis`, `yaxis`, `xaxis2`, `yaxis2`, ... | 笛卡尔坐标轴（动态编号） |
| 3D场景 | `scene`, `scene2`, ... | 3D 相机、坐标轴配置 |
| 地图 | `geo`, `mapbox`, `map`, ... | 地理/地图投影与图层 |
| 极坐标 | `polar`, `polar2`, ... | 极坐标子图 |
| 图例 | `legend`, `legend2`, ... | 图例位置与样式 |
| 颜色 | `coloraxis`, `colorscale`, `colorway` | 颜色轴与配色方案 |
| 字体 | `font` | 全局字体设置 |
| 标注 | `annotations[]` | 文字/箭头标注列表 |
| 形状 | `shapes[]` | 矩形、线条、圆形等几何形状 |
| 交互控件 | `updatemenus[]`, `sliders[]` | 下拉菜单、滑块 |
| 模式栏 | `modebar` | 工具栏按钮配置 |
| 悬停 | `hoverlabel`, `hovermode` | 悬停提示样式与模式 |
| 模板 | `template` | 图表主题模板 |
| 动画过渡 | `transition` | 帧切换动画配置 |

### 动态子图轴

Layout 最强大的特性之一是动态子图属性。通过 `make_subplots()` 创建子图后，Layout 自动生成编号属性：

```python
from plotly.subplots import make_subplots

fig = make_subplots(rows=2, cols=2)
# 自动创建 xaxis, xaxis2, xaxis3, xaxis4, yaxis, yaxis2, ...

fig.update_xaxes(title_text="X轴", row=1, col=1)  # 更新 xaxis
fig.update_xaxes(title_text="X轴2", row=1, col=2)  # 更新 xaxis2
```

子图编号属性由 `_subplotid_prop_re` 正则匹配，支持：`xaxis`, `yaxis`, `scene`, `geo`, `polar`, `map`, `mapbox`, `ternary`, `smith`, `coloraxis`, `legend`。

## graph_objects 层级结构

Trace 和 Layout 内部的属性并非扁平字典，而是按照 plotly.js 规范组织为嵌套对象树。以 Scatter 为例：

```
Scatter
├── 基础属性: x, y, mode, name, text, opacity, visible, ...
├── marker (scatter/marker/_marker.py → Marker)
│   ├── color, size, opacity, symbol, ...
│   ├── line (scatter/marker/_line.py → Line)
│   │   ├── color, width
│   │   └── ...
│   ├── colorbar (scatter/marker/_colorbar.py → ColorBar)
│   │   ├── title, tickvals, ticktext, ...
│   │   └── title.font
│   └── pattern (scatter/marker/_pattern.py → Pattern)
├── line (scatter/_line.py → Line)
│   ├── color, width, dash, shape, smoothing, ...
│   └── ...
├── error_x (scatter/_error_x.py → ErrorX)
├── error_y (scatter/_error_y.py → ErrorY)
├── hoverlabel (scatter/_hoverlabel.py → Hoverlabel)
├── selected / unselected
└── fillgradient / fillpattern
```

每个嵌套对象都对应 `graph_objs/scatter/` 子目录中的一个自动生成类文件。

## 魔术方法：动态属性访问

Plotly.py 通过 Python 魔法方法提供了灵活的属性访问方式。BasePlotlyType 和 BaseFigure 重写了以下方法：

### `__getitem__` / `__setitem__`（字典式访问）

支持两种字典访问语法：

```python
# 嵌套字典访问
fig["layout"]["title"] = "标题"
print(fig["data"][0]["marker"]["color"])

# 点分路径字符串（一句到位）
fig["layout.title"] = "标题"
fig["data"][0]["marker.color"] = "red"
```

路径解析由 `_str_to_dict_path_full()` 实现，支持：
- 点号分隔：`layout.title.font.size`
- 数组索引：`data[0].x`
- 混合使用：`layout.xaxis.title.font.size`

### `__setattr__`（属性式访问）

点号访问同样支持嵌套，但需要通过中间对象：

```python
fig.layout.title = "标题"           # ✅ 直接设置简单属性
fig.data[0].marker.color = "red"    # ✅ 通过中间对象链
# fig.layout.title.font.size = 14   # ❌ 如果 title 不存在会报错，需要先创建
```

`__setattr__`（L4974）的逻辑：
- 下划线开头（`_`）的属性 → 直接设置（内部属性）
- 已存在于实例或类中的属性 → 直接设置
- 在 `_valid_props` 中的合法属性 → 设置为图属性
- 其他 → 调用 `_raise_on_invalid_property_error()` 报错

### 下划线魔法参数（构造时）

构造函数和 `update_*` 方法支持下划线分隔的"扁平"参数，自动映射到嵌套路径：

```python
# 这些写法等价：
fig.update_traces(marker_color="red", marker_line_color="white", marker_line_width=2)

# 等价于：
fig.update_traces(marker=dict(color="red", line=dict(color="white", width=2)))
```

特殊含下划线的真实属性名（如 `error_x`、`paper_bgcolor`、`plot_bgcolor`、`error_y`、`error_z`）通过 `_valid_underscore_properties` 映射保护，不会被错误拆分。

### `__getattr__`（Layout 动态子图）

Layout 的 `__getattr__`（L5922）拦截对动态子图属性的访问：

```python
# 即使之前没有 xaxis2，也能正确访问（make_subplots 后自动创建）
fig.layout.xaxis2.title.text = "第二个X轴"
```

`_strip_subplot_suffix_of_1()` 方法将 `xaxis` 视为 `xaxis1` 的别名，方便统一处理。

## update 方法族

Figure 提供链式 update 方法用于声明式修改：

```python
# 更新 Figure 顶层属性
fig.update(layout_title_text="标题", layout_width=800)
fig.update_layout(title_text="标题", width=800)  # 便捷方法

# 更新所有 Trace
fig.update_traces(marker_size=10)

# 更新坐标轴
fig.update_xaxes(title_font_size=12)
fig.update_yaxes(title_font_size=12)

# 链式调用
(fig
 .update_layout(title="标题")
 .update_traces(marker_color="blue")
 .update_xaxes(gridcolor="gray"))
```

`update_layout`、`update_traces`、`update_xaxes`、`update_yaxes` 等便捷方法在 BaseFigure 中通过方法动态生成或显式定义，本质都是调用底层的 `update` 机制。

## JSON 序列化

Figure 对象的完整序列化流程：

### `to_plotly_json()`

返回一个纯 Python dict，可以直接 `json.dumps()`：

```python
fig = go.Figure(data=[go.Scatter(x=[1,2], y=[3,4])])
fig_dict = fig.to_plotly_json()
# {'data': [{'type': 'scatter', 'x': [1,2], 'y': [3,4], ...}], 'layout': {}}
```

内部递归调用每个 BasePlotlyType 子类的 `to_plotly_json()`（L5652），将 `_props`、`_compound_props`、`_compound_array_props` 合并为嵌套 dict，自动处理 numpy 数组转列表。

### `to_json()`

委托给 `plotly.io.to_json()`，返回 JSON 字符串：

```python
json_str = fig.to_json(pretty=True)  # 格式化输出
json_str = fig.to_json(remove_uids=True)  # 移除 uid（默认 True）
# engine 参数可选 "json"（标准库）或 "orjson"（高速）
```

### `to_html()`

委托给 `plotly.io.to_html()`，生成自包含 HTML 页面：

```python
html_str = fig.to_html(include_plotlyjs="cdn", full_html=True)
# include_plotlyjs: "cdn" | "inline" | "directory" | False
# full_html: True 返回完整 HTML 文档，False 返回 <div> 片段
```

### 与 Plotly.js 的对应

Figure 的 JSON 结构与 [plotly.js Figure schema](https://plotly.com/javascript/reference/) 完全对应：

```json
{
  "data": [
    {
      "type": "scatter",
      "x": [1, 2, 3],
      "y": [4, 5, 6],
      "marker": {"color": "red"},
      "line": {"width": 2}
    }
  ],
  "layout": {
    "title": {"text": "标题"},
    "xaxis": {"title": {"text": "X"}},
    "yaxis": {"title": {"text": "Y"}}
  },
  "frames": []
}
```

这意味着 Plotly.py 是 plotly.js 的精确 Python 映射——所有 JavaScript 文档中的属性名在 Python 中均可使用。

## 相关概念

- [Plotly.py 简介](00-introduction.md)
- [图对象模型](../references/graph-obj-model.md)
- [Plotly Express](02-plotly-express.md)
- [渲染与 IO](03-rendering-io.md)
- [交互式图表示例](../examples/interactive-charts.md)
