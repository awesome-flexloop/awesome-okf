---
type: concept
title: Plotly Express
description: 详解 plotly.express 高级 API，包括 _chart_types.py 中的图表工厂函数、facet/marginal/animation 参数、长表/宽表数据输入以及 _core.py 核心逻辑
tags:
  - plotly
  - plotly-express
  - px
  - 高级API
  - 数据可视化
  - facet
  - animation
generated:
  by: reference_agent/trae-glm
  at: 2026-08-22T15:00:00Z
verified:
  by: "process:seven-concepts-v"
  at: 2026-08-22T15:30:00Z
status: stable
stale_after: 2027-12-31
sources:
  - express/__init__.py
  - express/_chart_types.py
  - express/_core.py
  - express/_doc.py
  - express/_special_inputs.py
---

# Plotly Express

Plotly Express（简称 `px`）是 Plotly.py 提供的高级绘图接口，以"一行代码出图"为设计目标。它封装了数据映射、图例生成、分面布局、颜色比例尺、动画帧等常见模式，让用户专注于数据本身而非图表配置细节。

## 模块入口

`plotly.express` 模块通过 __init__.py 导出三大类内容：

1. **图表工厂函数**（来自 `_chart_types.py`）：`scatter`, `line`, `bar`, `pie`, `histogram`, `box`, `violin`, `imshow` 等 40+ 函数
2. **核心工具**（来自 `_core.py`）：`set_mapbox_access_token`, `defaults`, `get_trendline_results`, `NO_COLOR`
3. **特殊输入类型**（来自 `_special_inputs.py`）：`IdentityMap`, `Constant`, `Range`
4. **子模块**：`data`（内置数据集）、`colors`（颜色方案）、`trendline_functions`（趋势线算法）

Plotly Express 依赖 numpy（必需）、narwhals（DataFrame 抽象层，支持 pandas/polars 等）。

## 图表工厂函数（_chart_types.py）

_chart_types.py 中定义了所有图表类型的工厂函数。每个函数遵循统一模式：

```python
def scatter(
    data_frame=None, x=None, y=None, color=None, symbol=None, size=None,
    hover_name=None, hover_data=None, custom_data=None, text=None,
    facet_row=None, facet_col=None, facet_col_wrap=0,
    facet_row_spacing=None, facet_col_spacing=None,
    error_x=None, error_x_minus=None, error_y=None, error_y_minus=None,
    animation_frame=None, animation_group=None,
    category_orders=None, labels=None, orientation=None,
    color_discrete_sequence=None, color_discrete_map=None,
    color_continuous_scale=None, range_color=None, color_continuous_midpoint=None,
    symbol_sequence=None, symbol_map=None,
    opacity=None, size_max=None,
    marginal_x=None, marginal_y=None,
    trendline=None, trendline_options=None,
    trendline_color_override=None, trendline_scope="trace",
    log_x=False, log_y=False, range_x=None, range_y=None,
    render_mode="auto", title=None, subtitle=None,
    template=None, width=None, height=None,
) -> go.Figure:
    return make_figure(args=locals(), constructor=go.Scatter)
```

所有工厂函数最终都调用 _core.py 中的 `make_figure()` 函数，传入：

- `args=locals()`：所有调用参数（包括默认值）
- `constructor`：底层 graph_objects Trace 类（如 `go.Scatter`, `go.Bar`, `go.Histogram2dContour`）
- `trace_patch`：（可选）额外的 Trace 属性覆盖

### 完整图表函数列表

**2D 笛卡尔坐标系：**

| 函数 | 底层 Trace | 说明 |
|------|-----------|------|
| `px.scatter()` | `go.Scatter` | 散点图 |
| `px.line()` | `go.Scatter` (mode="lines") | 折线图 |
| `px.area()` | `go.Scatter` (fill="tozeroy") | 面积图 |
| `px.bar()` | `go.Bar` | 柱状图 |
| `px.timeline()` | - | 甘特时间线 |
| `px.bar_polar()` | `go.Barpolar` | 极坐标柱状图 |
| `px.strip()` | `go.Box` (boxpoints) | 散点条图 |
| `px.box()` | `go.Box` | 箱线图 |
| `px.violin()` | `go.Violin` | 小提琴图 |
| `px.histogram()` | `go.Histogram` | 直方图 |
| `px.ecdf()` | - | 经验累积分布图 |
| `px.density_contour()` | `go.Histogram2dContour` | 2D 密度等高线 |
| `px.density_heatmap()` | `go.Histogram2d` | 2D 密度热力图 |
| `px.scatter_matrix()` | `go.Splom` | 散点矩阵 |
| `px.parallel_coordinates()` | `go.Parcoords` | 平行坐标图 |
| `px.parallel_categories()` | `go.Parcats` | 平行类别图 |

**3D 图表：**

| 函数 | 底层 Trace | 说明 |
|------|-----------|------|
| `px.scatter_3d()` | `go.Scatter3d` | 3D 散点图 |
| `px.line_3d()` | `go.Scatter3d` | 3D 折线图 |

**极坐标/三元相图：**

| 函数 | 底层 Trace |
|------|-----------|
| `px.scatter_polar()` | `go.Scatterpolar` |
| `px.line_polar()` | `go.Scatterpolar` |
| `px.scatter_ternary()` | `go.Scatterternary` |
| `px.line_ternary()` | `go.Scatterternary` |

**地图：**

| 函数 | 底层 Trace | 说明 |
|------|-----------|------|
| `px.scatter_geo()` | `go.Scattergeo` | 地理散点 |
| `px.line_geo()` | `go.Scattergeo` | 地理线 |
| `px.scatter_mapbox()` | `go.Scattermapbox` | Mapbox 散点 |
| `px.line_mapbox()` | `go.Scattermapbox` | Mapbox 线 |
| `px.scatter_map()` | `go.Scattermap` | 地图散点 |
| `px.line_map()` | `go.Scattermap` | 地图线 |
| `px.choropleth()` | `go.Choropleth` | 分级填色地图 |
| `px.choropleth_mapbox()` | `go.Choroplethmapbox` | Mapbox 分级填色 |
| `px.choropleth_map()` | `go.Choroplethmap` | 地图分级填色 |
| `px.density_mapbox()` | `go.Densitymapbox` | Mapbox 密度图 |
| `px.density_map()` | `go.Densitymap` | 地图密度图 |

**分面/层级图表：**

| 函数 | 底层 Trace | 说明 |
|------|-----------|------|
| `px.pie()` | `go.Pie` | 饼图 |
| `px.sunburst()` | `go.Sunburst` | 旭日图 |
| `px.treemap()` | `go.Treemap` | 树图 |
| `px.icicle()` | `go.Icicle` | 冰柱图 |
| `px.funnel()` | `go.Funnel` | 漏斗图 |
| `px.funnel_area()` | `go.Funnelarea` | 漏斗面积图 |

**其他：**

| 函数 | 说明 |
|------|------|
| `px.imshow()` | 图像显示（来自 `_imshow.py`） |

## 参数体系

Plotly Express 所有图表函数共享一套丰富的参数体系。

### 数据映射参数

| 参数 | 作用 |
|------|------|
| `data_frame` | DataFrame 对象（pandas/polars/ narwhals 兼容） |
| `x`, `y`, `z` | 坐标轴数据列名或数组 |
| `a`, `b`, `c` | 三元相图坐标 |
| `r`, `theta` | 极坐标 |
| `lat`, `lon` | 地图经纬度 |
| `locations` | 地图位置编码 |
| `names`, `values` | 饼图/漏斗图的名称和值 |
| `parents`, `ids` | 层级图（sunburst/treemap）的父节点和 ID |
| `path` | icicle/treemap 的层级路径 |
| `text` | 数据点标签文本 |
| `hover_name` | 悬停提示标题 |
| `hover_data` | 悬停提示附加数据列（list/dict） |
| `custom_data` | 自定义数据（用于回调） |
| `error_x`, `error_y`, `error_z` | 误差棒 |

### 视觉编码参数

| 参数 | 作用 |
|------|------|
| `color` | 颜色映射（离散→分类颜色，连续→颜色比例尺） |
| `symbol` | 标记符号映射（散点图） |
| `size` | 标记大小映射 |
| `line_dash` | 线型映射（折线图） |
| `pattern_shape` | 填充图案映射（柱状图） |
| `opacity` | 整体透明度 |
| `size_max` | 散点最大尺寸 |
| `color_discrete_sequence` | 离散颜色序列（list） |
| `color_discrete_map` | 离散颜色映射（dict） |
| `color_continuous_scale` | 连续颜色比例尺 |
| `range_color` | 连续颜色范围 |
| `color_continuous_midpoint` | 连续颜色中点（发散色标） |
| `symbol_sequence` / `symbol_map` | 符号序列/映射 |

### Facet 分面参数

| 参数 | 作用 |
|------|------|
| `facet_row` | 按列分面（行方向排列） |
| `facet_col` | 按列分面（列方向排列） |
| `facet_col_wrap` | 分面列数换行阈值 |
| `facet_row_spacing` | 行间距 |
| `facet_col_spacing` | 列间距 |

分面通过 `_subplots.make_subplots()` 创建多子图布局，每个分面值对应一个子图。

### Marginal 边缘分布参数

| 参数 | 作用 |
|------|------|
| `marginal_x` | X 轴边缘分布图类型：`"histogram"`, `"rug"`, `"box"`, `"violin"` |
| `marginal_y` | Y 轴边缘分布图类型 |

边缘分布图通过附加子图实现，主图占据中心区域。

### 动画参数

| 参数 | 作用 |
|------|------|
| `animation_frame` | 动画帧列名（时间维度） |
| `animation_group` | 动画中跨帧追踪对象的标识列 |

设置 `animation_frame` 后，自动创建 `frames` 列表和播放控件（slider + updatemenus）。

### 趋势线参数

| 参数 | 作用 |
|------|------|
| `trendline` | 趋势线类型：`"ols"`（线性回归）、`"lowess"`（局部加权）、`"rolling"`（滚动平均）、`"expanding"`（展开平均）、`"ewm"`（指数加权） |
| `trendline_options` | 趋势线参数（dict） |
| `trendline_color_override` | 趋势线颜色 |
| `trendline_scope` | `"trace"`（每个 trace 一条）或 `"overall"`（全局一条） |

趋势线算法在 `trendline_functions` 字典中注册（_core.py L27）：`ols`, `lowess`, `rolling`, `expanding`, `ewm`。使用 `px.get_trendline_results(fig)` 获取趋势线拟合结果。

### 布局参数

| 参数 | 作用 |
|------|------|
| `title` | 图表标题 |
| `subtitle` | 副标题 |
| `template` | 主题模板名（`"plotly"`, `"plotly_white"`, `"plotly_dark"`, `"ggplot2"`, `"seaborn"` 等） |
| `width` / `height` | 画布尺寸 |
| `log_x` / `log_y` | 对数坐标轴 |
| `range_x` / `range_y` | 坐标范围 |
| `labels` | 轴标签映射（dict：`{"col_name": "显示名"}`） |
| `category_orders` | 分类顺序（dict：`{"col": ["a", "b", "c"]}`） |
| `orientation` | 柱状图方向：`"h"` 水平 / `"v"` 垂直 |

## 长表与宽表数据输入

Plotly Express 同时支持长表（long/tidy format）和宽表（wide format）数据。

### 长表模式（默认）

一列一个变量，一行一个观测值：

```python
import plotly.express as px
df = px.data.iris()  # sepal_length, sepal_width, petal_length, petal_width, species
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")
```

### 宽表模式

`x` 或 `y` 传入列名列表时自动进入宽表模式，每列生成一个 Trace：

```python
df = px.data.gapminder().query("country=='China'")
fig = px.line(df, x="year", y=["gdpPercap", "lifeExp"])
# 自动生成两条线，颜色不同
```

宽表模式文档由 `_wide_mode_xy_append` 注入（_chart_types.py L7-11）。

### 特殊输入类型

_special_inputs.py 提供三种特殊输入包装器：

- **`IdentityMap`**：将列值直接用作视觉属性（不做映射转换）
- **`Constant`**：将常量值应用于所有数据点
- **`Range`**：将值映射到 [0,1] 范围（用于大小等）

### 无 DataFrame 模式

直接传入数组/列表而不传入 `data_frame`：

```python
fig = px.scatter(x=[1,2,3,4], y=[10,11,12,13], color=[0,0,1,1])
```

## _core.py 核心逻辑

_core.py 是 Plotly Express 的核心引擎，主要逻辑包括：

### 属性分类（all_attrables）

Core 模块定义了四种属性映射类别（L32-48）：

```python
direct_attrables = ["x", "y", "z", "a", "b", "c", "r", "theta", "size", ...]
array_attrables = ["dimensions", "custom_data", "hover_data", "path", ...]
group_attrables = ["animation_frame", "facet_row", "facet_col", "line_group"]
renameable_group_attrables = ["color", "symbol", "line_dash", "pattern_shape"]
all_attrables = direct_attrables + array_attrables + group_attrables + renameable_group_attrables
```

### PxDefaults 默认配置

PxDefaults 类（实例为 `px.defaults`）管理全局默认值：

```python
px.defaults.template = "plotly_dark"       # 全局模板
px.defaults.width = 800                     # 全局宽度
px.defaults.height = 500                    # 全局高度
px.defaults.color_continuous_scale = "Viridis"  # 连续色标
px.defaults.color_discrete_sequence = px.colors.qualitative.Set1  # 离散色
px.defaults.reset()  # 重置所有默认值
```

### make_figure() 流程

`make_figure(args, constructor, trace_patch, layout_patch)` 是所有工厂函数的核心入口，执行以下步骤：

1. **参数提取**：从 `args=locals()` 获取所有参数，合并 PxDefaults 全局默认值
2. **数据处理**：通过 narwhals 统一处理不同类型的 DataFrame（pandas/polars/...）
3. **列映射推断**（infer_config）：根据 `color`/`symbol`/`size` 等参数推断映射配置
4. **Trace 构造**：对每个分组（color/symbol/facet/animation_frame 组合）构造一个 Trace 对象
5. **布局配置**：生成 Layout 配置（标题、坐标轴、图例、模板）
6. **子图创建**：如 facet/marginal 存在，调用 `make_subplots()` 创建子图网格
7. **Trace 放置**：通过 `_set_trace_grid_reference()` 将 Trace 放到正确的子图位置
8. **趋势线添加**：如指定 trendline，拟合趋势线并添加为额外 Trace
9. **动画帧构建**：如指定 animation_frame，构建 Frame 列表和播放控件
10. **返回 Figure**：最终返回完整的 `go.Figure` 对象

### 地图 Token

Mapbox 相关图表需要 access token：

```python
px.set_mapbox_access_token("your-token-here")
```

Token 存储在模块级变量 `MAPBOX_TOKEN` 中。

## 与 graph_objects 的关系

Plotly Express 和 graph_objects 不是互斥的——它们协同工作：

1. **px 创建 → go 精细调整**：用 px 创建基础图表，再用 go 方法修改细节
   ```python
   fig = px.scatter(df, x="x", y="y", color="c")
   fig.update_layout(title_font_size=20)
   fig.update_traces(marker_size=12, selector=dict(type="scatter"))
   ```

2. **px 创建 → 添加 go Trace**：用 px 创建后追加自定义 Trace
   ```python
   fig = px.line(df, x="x", y="y")
   fig.add_trace(go.Scatter(x=[0,10], y=[5,5], mode="lines", name="阈值"))
   ```

3. **px 输出是 go.Figure**：所有 px 函数返回 `go.Figure` 实例，可使用全部 Figure 方法

## 内置数据集

`px.data` 模块提供经典示例数据集：

| 数据集 | 内容 |
|--------|------|
| `px.data.iris()` | 鸢尾花数据 |
| `px.data.gapminder()` | 全球 GDP/寿命/人口（1952-2007） |
| `px.data.tips()` | 餐厅小费数据 |
| `px.data.titanic()` | 泰坦尼克乘客数据 |
| `px.data.election()` | 选举数据 |
| `px.data.wind()` | 风向风速数据 |
| `px.data.carshare()` | 共享汽车数据 |
| `px.data.stocks()` | 股票数据 |
| `px.data.medals_wide()` / `medals_long()` | 奖牌数据 |
| `px.data.fig_*()` | 测试图数据 |

## 相关概念

- [Figure 数据模型](01-figure-model.md)
- [Plotly.py 简介](00-introduction.md)
- [渲染与 IO](03-rendering-io.md)
- [图对象模型](../references/graph-obj-model.md)
- [交互式图表示例](../examples/interactive-charts.md)
