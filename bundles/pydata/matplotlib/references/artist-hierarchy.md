---
type: reference
title: Matplotlib Artist 层级体系源码参考
description: 基于源码追踪 matplotlib Artist 基类、Figure/Axes/Primitive/Container 的完整继承关系与核心方法定义
tags: [matplotlib, artist, figure, axes, hierarchy, source]
generated: { by: reference_agent/trae-glm, at: 2026-08-22T15:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T15:30:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: mpl-artist
    resource: external/libs/python/matplotlib/matplotlib/lib/matplotlib/artist.py
    title: matplotlib.artist 模块 — Artist 基类定义
  - id: mpl-figure
    resource: external/libs/python/matplotlib/matplotlib/lib/matplotlib/figure.py
    title: matplotlib.figure 模块 — Figure/FigureBase/SubFigure
  - id: mpl-axes-base
    resource: external/libs/python/matplotlib/matplotlib/lib/matplotlib/axes/_base.py
    title: matplotlib.axes._base 模块 — _AxesBase 基类
  - id: mpl-axes
    resource: external/libs/python/matplotlib/matplotlib/lib/matplotlib/axes/_axes.py
    title: matplotlib.axes._axes 模块 — Axes 绘图类
---

# Matplotlib Artist 层级体系源码参考

本文档基于 matplotlib 源码逐类追踪 Artist 继承体系，列出每个类的定义位置、核心属性和方法签名。

## 一、Artist 基类（artist.py:111）

**定义位置**：`artist.py` 第 111 行

```python
class Artist:
    """Abstract base class for objects that render into a FigureCanvas."""
    zorder = 0
```

### 核心属性初始化（__init__，第194行起）

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `_stale` | bool | True | 是否需要重绘 |
| `stale_callback` | callable/None | None | 过期回调 |
| `_axes` | Axes/None | None | 所属 Axes |
| `_parent_figure` | Figure/None | None | 所属 Figure |
| `_transform` | Transform/None | None | 坐标变换 |
| `_visible` | bool | True | 是否可见 |
| `_animated` | bool | False | 是否动画模式 |
| `_alpha` | float/None | None | 透明度 |
| `_clippath` | Path/None | None | 裁剪路径 |
| `_clipon` | bool | True | 是否启用裁剪 |
| `_label` | str | '' | 标签文本 |
| `_rasterized` | bool | False | 是否光栅化 |
| `_callbacks` | CallbackRegistry | 新建 | 回调注册表（信号："pchanged"） |

### 核心方法

| 方法 | 行号 | 签名 | 说明 |
|------|------|------|------|
| `draw` | 装饰器模式 | `draw(self, renderer, *args, **kwargs)` | 渲染方法，子类必须重写 |
| `remove` | 236 | `remove(self)` | 从 Figure 中移除该 Artist |
| `set` | 自动生成 | `set(self, **kwargs)` | 批量设置属性（自动生成签名） |
| `get_window_extent` | 338 | `get_window_extent(self, renderer=None)` | 获取显示空间边界框 |
| `get_tightbbox` | 374 | `get_tightbbox(self, renderer=None)` | 获取裁剪后紧边界框 |
| `add_callback` | 405 | `add_callback(self, func)` | 添加属性变化回调 |
| `axes` (property) | 302-315 | getter/setter | 获取/设置所属 Axes |
| `stale` (property) | 317-336 | getter/setter | 获取/设置过期状态（级联传播） |
| `get_figure` | - | `get_figure(self, root=False)` | 获取所属 Figure |

### set() 方法自动生成机制（第120-144行）

`__init_subclass__` 钩子为每个子类自动生成 `set()` 方法，通过 `ArtistInspector(cls).get_setters()` 收集所有 setter 属性，构造签名和文档。被排除的属性包括 `navigate_mode`、`figure`、`3d_properties`。

### 光栅化装饰器

- `_prevent_rasterization(draw)` — 第24行：默认装饰器，防止普通 Artist 继承光栅化状态
- `allow_rasterization(draw)` — 第45行：允许光栅化的装饰器，处理 `_raster_depth` 计数
- `_finalize_rasterization(draw)` — 第88行：Figure 最外层装饰器，确保渲染结束光栅化

## 二、FigureBase 类（figure.py:183）

**定义位置**：`figure.py` 第 183 行

```python
class FigureBase(Artist):
    """Base class for Figure and SubFigure."""
```

### 核心属性

| 属性 | 说明 |
|------|------|
| `_suptitle` | 总标题 Text 对象 |
| `_supxlabel` | 总 X 轴标签 |
| `_supylabel` | 总 Y 轴标签 |
| `_localaxes` | 所有 Axes 列表 |
| `subfigs` | 子图列表 |
| `_children` | 除 SubFigure 和 Axes 外的所有子 Artist |
| `suppressComposite` | 是否抑制合成 |

### 类型化 Artist 列表属性

通过 `_FigureArtistList` 提供类型安全的子元素访问：

| 属性 | 有效类型 |
|------|---------|
| `artists` | 通用 Artist（弃用警告） |
| `images` | FigureImage |
| `legends` | Legend |
| `lines` | Line2D |
| `patches` | Patch |
| `texts` | Text |

### 核心方法

| 方法 | 说明 |
|------|------|
| `add_artist` | 添加 Artist 到 Figure |
| `add_subplot` | 添加子图 Axes |
| `add_axes` | 添加 Axes |
| `subplots` | 批量创建子图 |
| `subfigures` | 创建子 Figure |
| `suptitle` | 设置总标题 |
| `supxlabel` | 设置总 X 标签 |
| `supylabel` | 设置总 Y 标签 |
| `colorbar` | 添加颜色条 |
| `legend` | 添加图例 |
| `_get_draw_artists` | 获取待渲染 Artist 列表（按 zorder 排序） |

## 三、Figure 类（figure.py:2511）

**定义位置**：`figure.py` 第 2511 行

```python
class Figure(FigureBase):
    """The top level Artist, which holds all plot elements."""
```

Figure 是用户创建图形的顶层容器，继承自 FigureBase，包含画布（canvas）关联、保存输出、布局管理等功能。

### 关键特性

- 拥有 `FigureCanvasBase` 实例（通过 `set_canvas` 关联）
- 管理 `_AxesStack`（`_axstack`）追踪当前活动 Axes
- 支持 `savefig` 方法保存到文件（PNG/PDF/SVG/PS/EPS 等）
- 支持 `tight_layout` 和 `constrained_layout` 布局引擎
- `patch` 属性是 `Rectangle`，代表 Figure 背景

## 四、_AxesBase 类（axes/_base.py:558）

**定义位置**：`axes/_base.py` 第 558 行

```python
class _AxesBase(martist.Artist):
    name = "rectilinear"
    _axis_names = ("x", "y")
    _shared_axes = {name: cbook.Grouper() for name in _axis_names}
    _twinned_axes = cbook.Grouper()
```

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `dataLim` | Bbox | 所有数据的边界框 |
| `spines` | Spines | 坐标轴脊线容器（left/right/top/bottom） |
| `transData` | Transform | 数据坐标→显示坐标变换 |
| `transAxes` | Transform | Axes 坐标(0-1)→显示坐标变换 |
| `xaxis` | XAxis | X 轴对象 |
| `yaxis` | YAxis | Y 轴对象 |
| `_position` | Bbox | Axes 在 Figure 中的位置矩形 |

### 初始化参数（__init__，第633行起）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `fig` | 必填 | 所属 Figure |
| `facecolor` | None（rc: axes.facecolor） | 背景色 |
| `frameon` | True | 是否绘制边框 |
| `sharex` | None | 共享 X 轴的 Axes |
| `sharey` | None | 共享 Y 轴的 Axes |
| `label` | '' | Axes 标签 |
| `xscale` | None | X 轴缩放（linear/log/symlog/logit） |
| `yscale` | None | Y 轴缩放 |
| `box_aspect` | None | 框体宽高比 |

## 五、Axes 类（axes/_axes.py:89）

**定义位置**：`axes/_axes.py` 第 89 行

```python
class Axes(_AxesBase):
    """
    The Axes contains most of the figure elements: Axis, Tick, Line2D,
    Text, Polygon, etc., and sets the coordinate system.
    """
```

Axes 是实际绘图区域类，继承自 `_AxesBase`，实现了所有绘图方法：`plot`、`scatter`、`bar`、`hist`、`imshow`、`contour`、`pie`、`fill_between` 等。

### Axes 中的子元素列表

| 属性 | 类型 | 内容 |
|------|------|------|
| `lines` | list[Line2D] | 通过 `plot`/`plot_date` 等添加的线条 |
| `patches` | list[Patch] | 矩形/多边形/圆等几何图形 |
| `texts` | list[Text] | 文本注释 |
| `images` | list[AxesImage] | 通过 `imshow` 添加的图像 |
| `collections` | list[Collection] | 散点/等值线/路径集合 |
| `artists` | list[Artist] | 其他 Artist |
| `containers` | list[Container] | bar/errorbar/stem 等容器 |
| `tables` | list[Table] | 表格对象 |

## 六、Primitive Artist 类型

所有可视化图元都直接继承自 Artist，是可见的渲染元素：

### Line2D（lines.py:265）

```python
class Line2D(Artist):
    """A line - the line can have both a solid linestyle and a marker at each data point."""
```

核心属性：`_xorig`/`_yorig`（原始数据）、`_linestyle`、`_linewidth`、`_color`、`_marker`、`_markersize`、`_markeredgecolor`、`_markerfacecolor`。

### Patch（patches.py:35）

```python
class Patch(artist.Artist):
    """A patch is a 2D artist with a face color and an edge color."""
```

子类包括：
- `Rectangle`（第802行）— 矩形（包括 Figure/Axes 背景 patch）
- `Polygon`（第1209行）— 多边形
- `Circle`（第2044行，通过 `Ellipse` 继承）— 圆形
- `Arc`（第2086行，通过 `Ellipse` 继承）— 圆弧
- `Arrow`（第1395行）— 箭头
- `FancyArrow`（第1478行）— 装饰箭头
- `FancyArrowPatch`（第4257行）— 高级箭头补丁
- `StepPatch`（第1100行，通过 `PathPatch`）— 阶梯形补丁

### Text（text.py:149）

```python
class Text(Artist):
    """Handle storing and rendering of text."""
```

核心属性：`_text`（文本内容）、`_fontproperties`、`_fontsize`、`_color`、`_rotation`、`_horizontalalignment`/`_verticalalignment`。

子类：`Annotation`（第1893行）— 带箭头的注释文本。

### AxesImage（image.py:880）

```python
class AxesImage(_ImageBase):
    """An image attached to an Axes."""
```

图像显示类，支持 colormap 映射、插值、透明度等。同类还有 `FigureImage`（第1381行）和 `BboxImage`（第1447行）。

## 七、Container 类型（container.py）

Container 不直接继承 Artist，而是继承 `tuple`，用于管理一组相关 Artist：

```python
class Container(tuple):
    """Base class for containers."""
```

| Container 类 | 行号 | 包含元素 |
|-------------|------|---------|
| `BarContainer` | 42 | patches（矩形条）+ errorbar/label |
| `ErrorbarContainer` | 119 | lines（数据线/帽线/竖线）+ has_xerr/has_yerr |
| `PieContainer` | 151 | patches（楔形）+ texts + autotexts |
| `StemContainer` | 223 | markerline + stemlines + baseline |

## 八、继承关系树

```
Artist (artist.py:111)
├── FigureBase (figure.py:183)
│   ├── Figure (figure.py:2511)
│   └── SubFigure
├── _AxesBase (axes/_base.py:558)
│   └── Axes (axes/_axes.py:89)
│       └── [PolarAxes, Axes3D, GeoAxes 等投影子类]
├── Axis (axis.py)
│   ├── XAxis
│   └── YAxis
│       └── Tick (内部类)
├── Line2D (lines.py:265)
│   └── AxLine (lines.py:1517)
├── Patch (patches.py:35)
│   ├── Rectangle (patches.py:802)
│   ├── Polygon (patches.py:1209)
│   │   └── FancyArrow (patches.py:1478)
│   ├── Ellipse
│   │   ├── Circle (patches.py:2044)
│   │   └── Arc (patches.py:2086)
│   ├── Arrow (patches.py:1395)
│   ├── FancyArrowPatch (patches.py:4257)
│   ├── PathPatch
│   │   └── StepPatch (patches.py:1100)
│   └── RegularPolygon
│       └── CirclePolygon (patches.py:1652)
├── Text (text.py:149)
│   └── Annotation (text.py:1893)
├── _ImageBase
│   ├── AxesImage (image.py:880)
│   ├── FigureImage (image.py:1381)
│   └── BboxImage (image.py:1447)
├── Collection (collections.py)
│   ├── LineCollection
│   ├── PolyCollection
│   ├── PathCollection
│   ├── QuadMesh
│   └── EventCollection
├── Legend (legend.py)
├── Colorbar (colorbar.py)
├── Table
└── Spine

Container (container.py:5) — 不继承 Artist，tuple 子类
├── BarContainer (42)
├── ErrorbarContainer (119)
├── PieContainer (151)
└── StemContainer (223)
```

## 九、属性系统（setp/getp）

matplotlib 提供了 `matplotlib.artist` 模块中的两个工具函数：

- `setp(obj, *args, **kwargs)` — 设置对象属性，可以接受属性字典或关键字参数
- `getp(obj, *args)` — 获取对象属性值，支持属性名或属性名列表

每个 Artist 子类通过属性 setter 方法（`set_<property>`）暴露可配置项，`ArtistInspector` 类可以内省这些属性列表。setter 命名约定：`set_linewidth`、`set_color`、`set_linestyle` 等，对应的 getter 为 `get_linewidth`、`get_color` 等。

## 十、事件系统

`artist.py` 中的 `_callbacks`（`cbook.CallbackRegistry`）维护 `"pchanged"` 信号的回调列表，当 Artist 属性通过 setter 改变时触发。此外，`backend_bases.py` 定义了完整的 GUI 事件体系：

| 事件类 | 行号 | 触发时机 |
|--------|------|---------|
| `Event` | 1178 | 事件基类 |
| `DrawEvent` | 1206 | 画布重绘 |
| `ResizeEvent` | 1233 | 画布大小改变 |
| `CloseEvent` | 1253 | 画布关闭 |
| `MouseEvent` | 1323 | 鼠标移动/点击/释放 |
| `PickEvent` | 1448 | Artist 被拾取（点击选中） |
| `KeyEvent` | 1497 | 键盘按键 |

所有 GUI 事件通过 `FigureCanvasBase` 的 `mpl_connect` 方法注册回调处理。

## 相关概念

- [Artist 体系](../concepts/01-artist-hierarchy.md)
- [后端系统](../concepts/02-backend-system.md)
- [pyplot 状态机](../concepts/03-pyplot-state-machine.md)
- [基础绑图示例](../examples/basic-plotting.md)
