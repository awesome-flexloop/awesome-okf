---
okf_version: "0.2"
type: concept
title: Artist 体系
description: Matplotlib 的核心是 Artist 类层次结构——所有可见元素都是 Artist，从顶层 Figure 容器到 Axes 绑图区域，再到 Line2D/Rectangle/Text/Image 等图元，形成完整的对象树
tags: [matplotlib, artist, figure, axes, primitive, container, setp, getp, event]
generated: { by: reference_agent/trae-glm, at: 2026-08-22T15:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T15:30:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: mpl-artist
    resource: external/libs/python/matplotlib/matplotlib/lib/matplotlib/artist.py
    title: matplotlib.artist 模块
  - id: mpl-figure
    resource: external/libs/python/matplotlib/matplotlib/lib/matplotlib/figure.py
    title: matplotlib.figure 模块
  - id: mpl-axes-base
    resource: external/libs/python/matplotlib/matplotlib/lib/matplotlib/axes/_base.py
    title: matplotlib.axes._base 模块
  - id: artist-hierarchy-ref
    resource: /references/artist-hierarchy.md
    title: Artist 层级体系源码参考
---

# Artist 体系

Artist（艺术家）是 Matplotlib 面向对象绑图架构的核心抽象。**所有在画布上可见的元素都是 Artist 的子类**——从顶层的 Figure（整个图形窗口），到中间的 Axes（绑图区域），到具体的线条、矩形、文本、图像，再到坐标轴和刻度，无一例外。

## 一、Artist 继承层次总览

```
Artist（抽象基类）
├── 容器类（Container Artists）
│   ├── FigureBase
│   │   ├── Figure       — 顶层图形窗口/画布
│   │   └── SubFigure    — 子 Figure（嵌套布局）
│   ├── _AxesBase
│   │   └── Axes         — 绑图区域（包含坐标系统）
│   └── Axis
│       ├── XAxis        — X 坐标轴
│       └── YAxis        — Y 坐标轴
│
└── 图元类（Primitive Artists）
    ├── Line2D           — 折线/数据点标记
    │   └── AxLine       — 无限直线（axhline/axvline/axline）
    ├── Patch            — 2D 几何图形基类
    │   ├── Rectangle    — 矩形（含 Figure/Axes 背景）
    │   ├── Polygon      — 多边形
    │   ├── Ellipse
    │   │   ├── Circle   — 圆形
    │   │   └── Arc      — 圆弧
    │   ├── Arrow        — 基本箭头
    │   ├── FancyArrow   — 装饰箭头
    │   └── FancyArrowPatch — 高级箭头（可弯曲）
    ├── Text             — 文本
    │   └── Annotation   — 带箭头注释文本
    ├── _ImageBase
    │   ├── AxesImage    — Axes 内图像（imshow）
    │   ├── FigureImage  — Figure 级图像
    │   └── BboxImage    — Bbox 绑定图像
    └── Collection       — 批量图元（性能优化）
        ├── PathCollection — 路径集合（散点图）
        ├── LineCollection — 线段集合
        ├── PolyCollection — 多边形集合
        └── QuadMesh       — 网格（pcolormesh）
```

此外还有 `Container` 类（`container.py`），它不继承 Artist 而是继承 `tuple`，用于管理一组相关的 Artist（如 `BarContainer` 管理柱状图的所有矩形条）。

## 二、容器层次详解

### Figure：顶层容器

`Figure` 是整个绑图的顶层容器，对应一个图形窗口或输出文件中的一页。它的核心职责：

- **管理 Axes**：通过 `_axstack`（`_AxesStack` 对象）追踪所有 Axes，并维护"当前活动 Axes"
- **管理子 Figure**：`subfigs` 列表支持嵌套 SubFigure
- **管理全局元素**：suptitle（总标题）、supxlabel/supylabel（总轴标签）、colorbar、legend
- **关联 Canvas**：通过 `FigureCanvasBase` 与后端渲染器连接
- **保存输出**：`savefig()` 方法触发渲染到文件

创建 Figure 的方式：
- `plt.figure()` — pyplot 接口
- `plt.subplots()` — 同时创建 Figure 和 Axes
- 直接 `fig = Figure()` — 纯 OO 方式（需自行关联 canvas）

### Axes：绑图区域

`Axes` 是实际的绑图区域，是用户最常交互的对象。每个 Axes 包含：

- **坐标系统**：`transData`（数据坐标变换）、`transAxes`（归一化坐标变换，0-1）
- **坐标轴**：`xaxis`（XAxis）、`yaxis`（YAxis），管理刻度和标签
- **脊线（Spines）**：`spines` 属性，四个方向的边框线（left/right/top/bottom）
- **数据图元列表**：`lines`、`patches`、`texts`、`images`、`collections` 等
- **绘图方法**：`plot()`、`scatter()`、`bar()`、`hist()`、`imshow()` 等数十种

Axes 的子元素类型化列表：

| 属性 | 类型 | 来源方法 |
|------|------|---------|
| `ax.lines` | list of Line2D | `plot()`, `axhline()`, `axvline()` |
| `ax.patches` | list of Patch | `bar()`, `fill_between()`, `add_patch()` |
| `ax.texts` | list of Text | `text()`, `set_title()`, `set_xlabel()` |
| `ax.images` | list of AxesImage | `imshow()` |
| `ax.collections` | list of Collection | `scatter()`, `contourf()`, `pcolormesh()` |
| `ax.containers` | list of Container | `bar()`, `errorbar()`, `stem()` |

## 三、图元类（Primitive）详解

### Line2D：线条与标记

`Line2D` 是最常用的图元，代表数据点之间的连线和/或数据点标记。核心属性：

- `xdata`, `ydata`：数据点坐标
- `linestyle`/`ls`：线型（`'-'`, `'--'`, `':'`, `'-.'`, `''`（空））
- `linewidth`/`lw`：线宽（点）
- `color`/`c`：颜色（颜色名、RGB、十六进制、C0-C9循环色）
- `marker`：标记样式（`'o'`, `'s'`, `'^'`, `'+'`, `'.'`, `','`, `None`）
- `markersize`/`ms`：标记大小
- `markerfacecolor`/`mfc`：标记填充色
- `markeredgecolor`/`mec`：标记边框色

格式字符串（MATLAB风格）可以快速指定：`'r--o'` 表示红色虚线+圆形标记。

### Patch：几何图形

`Patch` 是所有有填充区域的2D图形基类，核心属性：
- `facecolor`/`fc`：填充色
- `edgecolor`/`ec`：边框色
- `linewidth`/`lw`：边框宽度
- `linestyle`/`ls`：边框线型
- `hatch`：填充图案（`'/'`, `'\\'`, `'|'`, `'-'`, `'+'`, `'x'`, `'o'`, `'O'`, `'.'`, `'*'`）
- `alpha`：透明度（0-1）

常用子类：
- `Rectangle((x,y), w, h)` — 矩形，是 bar 图和 Axes 背景的基础
- `Circle((x,y), r)` — 圆形
- `Polygon(verts)` — 闭合多边形
- `Arc((x,y), w, h, angle)` — 圆弧（无填充）

### Text：文本

`Text` 对象负责所有文字渲染：
- `set_text(s)`：设置文本内容
- `set_fontsize(size)` / `set_size(size)`：字号
- `set_fontfamily(family)`：字体族（serif/sans-serif/monospace等）
- `set_fontweight(weight)`：字重（normal/bold等）
- `set_color(color)`：文字颜色
- `set_rotation(angle)`：旋转角度
- `set_ha(align)` / `set_horizontalalignment(align)`：水平对齐（left/center/right）
- `set_va(align)` / `set_verticalalignment(align)`：垂直对齐（top/center/bottom/baseline）

`Annotation` 是 Text 的子类，额外提供箭头指向功能（`xytext`→`xy`）。

### AxesImage：图像

通过 `imshow()` 创建，将二维数组显示为彩色图像。核心属性：
- `set_cmap(cmap)`：设置色图（colormap）
- `set_norm(norm)`：设置归一化方式
- `set_interpolation(interp)`：插值方法（nearest/bilinear/bicubic等）
- `set_alpha(alpha)`：透明度

## 四、属性系统：setp/getp

Matplotlib 提供了统一的属性访问机制。每个 Artist 都有 getter/setter 方法对。

### 批量设置属性

```python
# 方式1：关键字参数（创建时）
line, = ax.plot(x, y, color='red', linewidth=2, linestyle='--')

# 方式2：set() 方法批量设置
line.set(color='blue', linewidth=3, linestyle=':')

# 方式3：独立 setter
line.set_color('green')
line.set_linewidth(1.5)

# 方式4：plt.setp() 函数
plt.setp(line, color='black', linewidth=2)
```

`set()` 方法由 `Artist.__init_subclass__` 钩子在类定义时自动生成签名，支持所有 setter 属性作为关键字参数。

### 查询属性

```python
# 方式1：独立 getter
color = line.get_color()
lw = line.get_linewidth()

# 方式2：plt.getp() 函数查看所有属性
plt.getp(line)          # 打印所有属性
plt.getp(line, 'color') # 获取特定属性

# 方式3：properties() 方法
props = line.properties()  # 返回属性字典
```

### 属性别名

常用属性有短别名，`set()` 和 setter 方法都接受：

| 完整名 | 别名 |
|--------|------|
| `linewidth` | `lw` |
| `linestyle` | `ls` |
| `color` | `c` |
| `markeredgecolor` | `mec` |
| `markerfacecolor` | `mfc` |
| `markersize` | `ms` |
| `markeredgewidth` | `mew` |
| `facecolor` | `fc` |
| `edgecolor` | `ec` |
| `antialiased` | `aa` |

## 五、zorder：绘制顺序

所有 Artist 都有 `zorder` 属性，决定绘制时的层叠顺序。zorder 值越大越靠上（后绘制）：

| Artist | 默认 zorder |
|--------|------------|
| Figure patch（背景） | 0 |
| Axes patch（背景） | 1 |
| Line2D（线条/标记） | 2 |
| Patch（矩形/多边形） | 1 |
| Text（文本） | 3 |
| Legend（图例） | 5 |

同一 zorder 内按添加顺序绘制（后添加在上）。可以通过 `set_zorder()` 手动调整层叠顺序。

## 六、stale 机制与重绘

每个 Artist 都有 `stale` 属性（布尔值），标记该对象是否需要重绘。当 setter 方法修改属性时，会自动将 `stale` 设为 `True`，并通过 `stale_callback` 级联通知父容器：

1. Primitive 变化 → 通知所属 Axes → 通知所属 Figure
2. Figure 标记 stale 后，canvas 的 `draw_idle()` 会被调度
3. 下次 GUI 事件循环空闲时触发重绘

这种增量标记机制避免了不必要的重绘，提高交互性能。

## 七、事件系统

Matplotlib 支持丰富的事件回调，通过 `FigureCanvasBase.mpl_connect(event_name, callback)` 注册：

| 事件名 | 事件类 | 触发时机 |
|--------|--------|---------|
| `'button_press_event'` | MouseEvent | 鼠标按下 |
| `'button_release_event'` | MouseEvent | 鼠标释放 |
| `'motion_notify_event'` | MouseEvent | 鼠标移动 |
| `'key_press_event'` | KeyEvent | 键盘按下 |
| `'key_release_event'` | KeyEvent | 键盘释放 |
| `'draw_event'` | DrawEvent | 画布重绘 |
| `'resize_event'` | ResizeEvent | 画布大小改变 |
| `'close_event'` | CloseEvent | 窗口关闭 |
| `'pick_event'` | PickEvent | Artist 被点击选中（需设置 picker/pickradius） |
| `'scroll_event'` | MouseEvent | 鼠标滚轮 |
| `'figure_enter_event'` | LocationEvent | 鼠标进入 Figure |
| `'figure_leave_event'` | LocationEvent | 鼠标离开 Figure |
| `'axes_enter_event'` | LocationEvent | 鼠标进入 Axes |
| `'axes_leave_event'` | LocationEvent | 鼠标离开 Axes |

### 事件处理示例

```python
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots()
ax.plot(np.random.rand(10), picker=True, pickradius=5)

def on_pick(event):
    if event.artist.get_label() == '_line0':
        print(f'选中了线条，包含 {len(event.ind)} 个数据点')

fig.canvas.mpl_connect('pick_event', on_pick)
plt.show()
```

### Artist 内部属性回调

除了 GUI 事件，Artist 自身也通过 `add_callback(func)` 支持属性变化回调，当任何属性通过 setter 修改时触发 `'pchanged'` 信号。

## 八、添加/移除 Artist

```python
# 添加 Artist 到 Axes
line = Line2D([0, 1], [0, 1], color='red')
ax.add_line(line)
# 或更通用：
ax.add_artist(line)

# 添加 Artist 到 Figure（Figure 级元素）
fig.add_artist(Line2D([0.5], [0.5], transform=fig.transFigure))

# 移除 Artist
line.remove()  # 从所属容器中移除

# 注意：remove() 后需要调用 ax.relim() + ax.autoscale_view() 更新数据范围
```

## 九、对象树遍历

可以通过 `get_children()` 方法遍历 Artist 对象树：

```python
def print_tree(artist, indent=0):
    """打印 Artist 对象树"""
    name = type(artist).__name__
    print('  ' * indent + name)
    if hasattr(artist, 'get_children'):
        try:
            for child in artist.get_children():
                print_tree(child, indent + 1)
        except Exception:
            pass

print_tree(fig)
```

典型输出结构：
```
Figure
  Rectangle (Figure patch)
  Axes
    Rectangle (Axes patch)
    Line2D
    XAxis
      ...
    YAxis
      ...
    Text (title)
    Text (xlabel)
    Text (ylabel)
  Text (suptitle)
```

## 相关概念

- [后端系统](02-backend-system.md)
- [pyplot 状态机](03-pyplot-state-machine.md)
- [Matplotlib 简介](00-introduction.md)
- [Artist 层级源码参考](../references/artist-hierarchy.md)
- [基础绑图示例](../examples/basic-plotting.md)
