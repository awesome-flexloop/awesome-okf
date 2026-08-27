---
type: reference
title: Plotly 图对象模型
description: 深入解析 plotly.py 中图对象（graph objects）的包结构、类层级、基类体系、属性访问机制与代码生成流程
tags:
  - plotly
  - graph-objects
  - 数据模型
  - 类层级
  - 动态属性
generated:
  by: reference_agent/trae-glm
  at: 2026-08-22T15:00:00Z
verified:
  by: "process:seven-concepts-v"
  at: 2026-08-22T15:30:00Z
status: stable
stale_after: 2027-12-31
sources:
  - basedatatypes.py (BaseFigure, BasePlotlyType, BaseTraceType, BaseLayoutType)
  - graph_objs/_figure.py (Figure)
  - graph_objs/_layout.py (Layout)
  - graph_objs/_scatter.py (Scatter 等 Trace 类)
  - graph_objects/__init__.py (别名包)
---

# Plotly 图对象模型

Plotly.py 的核心数据模型建立在一套分层的图对象（Graph Objects）体系之上。所有图表组件——从顶层的 Figure 到单个 Trace 的标记样式——都由这套对象树构成，每个节点对应 plotly.js 规范中的一个 JSON 对象。

## 包结构

plotly.py 维护两套图对象包：

- **`plotly.graph_objs`**（旧命名，无下划线）：实际存放所有自动生成的图对象类
- **`plotly.graph_objects`**（新命名，带下划线）：PEP8 风格别名包，通过 `relative_import` 惰性重导出 `graph_objs` 中的全部类与子模块

推荐使用 `import plotly.graph_objects as go`。

`graph_objs/` 目录结构：

```
graph_objs/
├── __init__.py          # 重导出所有 Trace/Layout/Figure 类及子模块
├── graph_objs.py        # from plotly.graph_objs import * 的兼容入口
├── _figure.py           # Figure 类（继承 BaseFigure）
├── _figurewidget.py     # FigureWidget 类（Jupyter 交互控件）
├── _frame.py            # Frame 类（动画帧）
├── _layout.py           # Layout 类（继承 BaseLayoutType）
├── _deprecations.py     # 已废弃别名：Data, Trace, Annotations 等
├── _scatter.py          # Scatter 类（自动生成）
├── _bar.py              # Bar 类
├── _box.py / _violin.py / _histogram.py / ...  # 每种图表类型一个文件
├── scatter/             # Scatter 的子属性目录
│   ├── __init__.py
│   ├── _marker.py       # scatter.Marker 子对象
│   ├── _line.py         # scatter.Line 子对象
│   ├── _error_x.py      # scatter.ErrorX
│   ├── _hoverlabel.py   # scatter.Hoverlabel
│   └── marker/          # 更深层级：marker.colorbar, marker.line 等
│       ├── __init__.py
│       ├── _colorbar.py
│       └── _line.py
├── layout/              # Layout 的子属性目录
│   ├── __init__.py
│   ├── _xaxis.py / _yaxis.py / _scene.py / _geo.py / ...
│   └── xaxis/ / scene/ / legend/ / ...  # 进一步嵌套
└── bar/ / box/ / pie/ / heatmap/ / ...  # 每种 Trace 的子属性目录
```

## 核心类层级

所有图对象类最终继承自 basedatatypes.py 中定义的基类：

```
BaseFigure (L401)
├── Figure (graph_objs/_figure.py)
└── FigureWidget (graph_objs/_figurewidget.py, 继承 ipywidgets.DOMWidget)

BasePlotlyType (L4312)                # 所有 trace/layout/frame 层级对象的基类
├── BaseLayoutHierarchyType           # Layout 及其子对象的中间基类
│   └── BaseLayoutType (L5755)        # Layout 类的直接基类
│       └── Layout (graph_objs/_layout.py)
└── BaseTraceHierarchyType (L5996)    # Trace 层级对象的中间基类
    └── BaseTraceType (L6010)         # 所有 Trace 类型的直接基类
        ├── Scatter (_scatter.py)
        ├── Bar (_bar.py)
        ├── Box (_box.py)
        ├── Heatmap (_heatmap.py)
        ├── Pie (_pie.py)
        ├── Surface (_surface.py)
        ├── Histogram (_histogram.py)
        └── ... (40+ 种 Trace 类型)
```

### BaseFigure（顶层容器）

BaseFigure 是 Figure 和 FigureWidget 的基类，管理三大核心组件：

- **`_data_objs`**：Trace 对象元组（通过 `_data_validator.validate_coerce()` 从输入数据构造）
- **`layout`**：Layout 对象实例
- **`frames`**：Frame 对象列表（用于动画）

关键方法：

| 方法 | 作用 |
|------|------|
| `__init__(data, layout, frames, skip_invalid)` | 构造 Figure，支持 Trace 列表、dict 或 Figure 对象作为输入 |
| `show(*args, **kwargs)` | 委托给 `plotly.io.show()` 渲染图表 |
| `to_json(*args, **kwargs)` | 委托给 `plotly.io.to_json()` 序列化为 JSON |
| `to_html(*args, **kwargs)` | 委托给 `plotly.io.to_html()` 生成 HTML |
| `to_plotly_json()` | 返回可直接序列化的 dict 结构 |
| `update(dict1, overwrite, **kwargs)` | 递归更新 Figure 属性 |
| `update_traces(patch, selector, row, col, ...)` | 按选择器批量更新 Trace |
| `add_trace(trace, row, col, secondary_y)` | 添加单个 Trace 到指定子图位置 |
| `add_traces(data, rows, cols, secondary_ys)` | 批量添加 Trace |
| `__getitem__(prop)` / `__setitem__(prop, value)` | 支持 `fig['layout']['title']` 和路径语法 `fig['layout.title']` |

### BasePlotlyType（属性节点基类）

BasePlotlyType 是 trace/layout 层级所有对象的基类，核心机制：

- **`_valid_props`**：该对象支持的合法属性名集合（由代码生成器填充）
- **`_compound_props`**：子对象字典（复合属性，如 `marker`、`line`、`hoverlabel`）
- **`_compound_array_props`**：子对象列表字典（如 `annotations`、`shapes`）
- **`_orphan_props`**：无父对象时的临时属性存储
- **`_parent`**：父对象引用（构成对象树）
- **`_change_callbacks`**：属性变更回调注册表（FigureWidget 交互用）

属性访问通过魔法方法实现：

- `__setattr__(prop, value)`（L4974）：公共属性经 `_valid_props` 校验后设置，下划线属性和已知属性直接通过 `super().__setattr__`
- `__getitem__` / `__setitem__`（L4732/L4870）：支持点分路径语法 `trace['marker.color']` 等价于 `trace.marker.color`
- `_process_kwargs(**kwargs)`：构造时将下划线命名参数（如 `marker_color=red`）转换为嵌套路径

### BaseTraceType（Trace 基类）

BaseTraceType 为所有图表系列类型的基类，额外提供：

- **事件回调系统**：`on_hover()`、`on_unhover()`、`on_click()`、`on_selection()`、`on_deselect()` 注册回调函数
- **`uid` 属性**：每个 Trace 的唯一标识符
- **`_trace_ind`**：Trace 在 Figure.data 中的索引位置

### BaseLayoutType（Layout 基类）

BaseLayoutType 管理布局配置，支持动态子图属性：

- **`_subplotid_prop_names`**：可编号子图属性名列表（`xaxis`, `yaxis`, `scene`, `geo`, `polar`, `mapbox`, `map`, `ternary`, `smith`, `coloraxis`, `legend`）
- **`_subplotid_prop_re`**：正则匹配如 `xaxis2`、`scene3` 的动态属性
- **`__getattr__` / `__setattr__` / `__getitem__` / `__setitem__`**（L5922-5984）：拦截对子图编号属性的访问，动态创建子图对象

## Figure → Data → Layout → Trace 层级

一个典型的 Figure 对象树结构：

```
Figure
├── data (trace 列表)
│   ├── Scatter
│   │   ├── x, y, mode, name, ... (基础属性)
│   │   ├── marker (scatter.Marker)
│   │   │   ├── color, size, opacity, ...
│   │   │   ├── line (scatter.marker.Line)
│   │   │   │   ├── color, width
│   │   │   │   └── colorbar (scatter.marker.line.ColorBar)
│   │   │   └── colorbar (scatter.marker.ColorBar)
│   │   ├── line (scatter.Line)
│   │   │   ├── color, width, dash, shape
│   │   │   └── ...
│   │   └── hoverlabel (scatter.Hoverlabel)
│   ├── Bar
│   │   ├── x, y, ...
│   │   └── marker (bar.Marker)
│   └── ...
├── layout (Layout)
│   ├── title, width, height, template, ...
│   ├── xaxis, xaxis2, xaxis3, ... (动态子图轴)
│   ├── yaxis, yaxis2, ...
│   ├── scene, scene2, ... (3D 场景)
│   ├── legend, annotations[], shapes[], updatemenus[], sliders[]
│   ├── margin (layout.Margin)
│   ├── font (layout.Font)
│   └── ...
└── frames (Frame 列表，动画帧)
    ├── Frame(data=[...], layout=...)
    └── ...
```

## 动态属性访问（魔术方法）

Plotly.py 提供三种属性访问方式，底层共享同一套存储：

```python
import plotly.graph_objects as go

fig = go.Figure(data=go.Scatter(x=[1,2], y=[3,4]))

# 方式1：点号属性访问
fig.layout.title = "My Chart"
fig.data[0].marker.color = "red"

# 方式2：字典键访问
fig["layout"]["title"] = "My Chart"
fig["data"][0]["marker"]["color"] = "red"

# 方式3：点分路径（下划线魔法）
fig.update_layout(title_font_size=14)       # title.font.size
fig.data[0].update(marker_color="blue")     # marker.color
```

路径解析由 _str_to_dict_path_full() 完成，将 `foo.bar[0].baz` 拆分为 `("foo", "bar", 0, "baz")` 的元组路径。

特殊保护属性（含下划线的真实属性名如 `error_x`、`paper_bgcolor`）通过 `_valid_underscore_properties` 映射为连字符形式 `error-x`，避免被错误拆分。

## 代码自动生成机制

所有 `_*.py` Trace 类文件（`_scatter.py`、`_bar.py` 等）和子属性文件均由代码生成器自动生成，文件头部标注：

```
#                   --- THIS FILE IS AUTO-GENERATED ---
# Modifications will be overwitten the next time code generation run.
```

每个自动生成的 Trace 类：

1. 继承对应基类（如 `BaseTraceType`）
2. 定义 `_parent_path_str`（父路径字符串）
3. 定义 `_path_str`（当前对象的 plotly.js 路径名，如 `"scatter"`）
4. 定义 `_valid_props`（该类型支持的所有属性名集合）
5. 提供 `__init__(self, **kwargs)` 方法，调用基类构造并处理复合属性

子属性模块（如 `scatter/_marker.py`）中的类同样是自动生成的，继承自 `BaseTraceHierarchyType`。

## 验证器体系（ValidatorCache）

属性校验通过 `plotly.validator_cache.ValidatorCache` 实现：

- 每个对象类型的每个属性都有对应的 Validator（如 `DataValidator`、`LayoutValidator`、`ColorValidator`、`SubplotidValidator` 等）
- `_get_validator(prop)` 方法按需从缓存获取 validator
- `validate_coerce()` 方法将用户输入（dict、列表、原始值）转换为强类型图对象
- `skip_invalid=True` 可静默跳过无效属性（默认 False 则抛 ValueError）

## 序列化为 JSON

图对象通过 `to_plotly_json()` 方法递归转换为可 JSON 序列化的 dict：

- 每个对象将 `_props`、`_compound_props`、`_compound_array_props` 合并为纯 dict
- numpy 数组等特殊类型在序列化时被转换为列表
- `to_json()` 通过 `plotly.io._json` 模块处理，支持 `orjson` 加速引擎
- `to_html()` 生成包含 plotly.js CDN 引用和 JSON 数据的独立 HTML 页面

## 相关概念

- [Figure 数据模型](../concepts/01-figure-model.md)
- [Plotly.py 简介](../concepts/00-introduction.md)
- [渲染与 IO](../concepts/03-rendering-io.md)
- [Plotly Express 高级 API](../concepts/02-plotly-express.md)
