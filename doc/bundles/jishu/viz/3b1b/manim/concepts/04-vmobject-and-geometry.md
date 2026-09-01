---
type: Concept
title: VMobject 与几何图形
description: VMobject 继承 Mobject，以贝塞尔路径存储矢量数据，扩展 data_dtype 和 uniform_dtype 支持描边填充，是 Circle/Square/Line/Arrow 等几何类的基类。
tags: [manimgl, vmobject, vectorized-mobject, bezier, geometry, stroke, fill, arrow]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: ManimGL 源码事实采集
---

# VMobject 与几何图形

VMobject（Vectorized Mobject，矢量数学对象）是 ManimGL 中所有矢量图形的基类，定义在 `manimlib/mobject/types/vectorized_mobject.py` 第64行，继承自 Mobject（F-068）。VMobject 在 Mobject 的基础上扩展了贝塞尔（Bézier）路径数据结构、描边（stroke）与填充（fill）渲染属性，是 Circle、Square、Line、Arrow、多边形、曲线等几乎所有二维几何图形的共同父类。TipableVMobject 进一步提供箭头尖端机制，让 Arc 和 Line 等路径类对象可以方便地添加箭头。

## VMobject 与 Mobject 的关系

VMobject 继承自 Mobject，复用了 Mobject 的所有核心机制：data 数组、uniforms 缓冲、submobjects 树形结构、family 概念、animate/always/f_always 语法糖、几何变换方法（shift/scale/rotate）等。VMobject 的扩展主要体现在三个方面：

1. **渲染类替换**：`drawing_class = VDrawing`（F-069），使用矢量图形专用的 Drawing 子类，处理贝塞尔路径的 GPU 渲染
2. **数据结构扩展**：`data_dtype` 增加描边相关的逐顶点字段，`uniform_dtype` 增加填充、渐变、抗锯齿等逐对象参数
3. **初始化参数扩展**：新增 fill_color、stroke_color、stroke_width 等矢量图形特有的配置参数
4. **结构键标记**：`structural_data_keys = ['subpath_range']`（F-070），标记子路径范围字段为结构数据，参与数据对齐和插值

这种继承设计遵循"开闭原则"——Mobject 提供通用数学对象和 GPU 渲染原语的基础，VMobject 在此之上增量式扩展矢量图形能力，而非从零重写。

## 贝塞尔路径数据

VMobject 的几何形状由贝塞尔曲线组成，每个 VMobject 包含一条或多条子路径（subpath），每条子路径由一段或多段三次贝塞尔曲线（Cubic Bézier）连接而成。贝塞尔曲线的控制点存储在 `data['point']` 数组中，这是 Mobject 已有的 point 字段的复用——VMobject 没有新增几何位置字段，而是约定 point 数组中每 4 个连续顶点构成一段三次贝塞尔曲线（起点 + 两个控制点 + 终点）。

### subpath_range：子路径标记

为了区分多条子路径，VMobject 在 `data_dtype` 中新增了 `subpath_range` 字段（F-071）：

```python
VMobject.data_dtype = [
    ('point', np.float32, (3,)),         # 继承自 Mobject：顶点位置
    ('stroke_rgba', np.float32, (4,)),   # 描边颜色（逐顶点）
    ('stroke_width', np.float32, (1,)),  # 描边宽度（逐顶点）
    ('subpath_range', np.float32, (2,))  # 新增：子路径起止索引
]
```

`structural_data_keys = ['subpath_range']`（F-070）将 subpath_range 标记为结构数据，这意味着在 Transform 插值时，subpath_range 会被当作数据结构标记而非普通顶点属性处理，保证子路径边界在动画中正确对齐。

### 点的组织约定

VMobject 的 point 数组按以下约定组织：
- 每 4 个连续点构成一段三次贝塞尔曲线（P0 起点、P1 控制点、P2 控制点、P3 终点）
- 一段贝塞尔的终点（P3）是下一段贝塞尔的起点（P0），通过点的复用来保证连续性
- 每条子路径由多段连接的贝塞尔曲线组成
- `subpath_range` 标记每条子路径在 point 数组中的起止范围

这种基于顶点数组的贝塞尔路径表示让 Transform 插值可以直接在点级别工作——两个 VMobject 之间的变换动画本质上是起点数组到终点数组的逐点插值，这是 ManimGL 形变动画流畅自然的数据基础（洞察 I-02）。

## 描边与填充：data_dtype 扩展

VMobject 的 `data_dtype` 在 Mobject 基础上增加了两个描边相关字段（F-071）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `stroke_rgba` | `(4,) float32` | 逐顶点描边颜色，允许描边颜色沿路径渐变 |
| `stroke_width` | `(1,) float32` | 逐顶点描边宽度，允许粗细变化 |
| `subpath_range` | `(2,) float32` | 子路径范围标记（结构数据） |

注意 VMobject 仍然保留了 Mobject 的 `rgba` 字段。在 VMobject 的渲染语义中：
- `data['rgba']`（继承自 Mobject）通常用作填充颜色的逐顶点数据
- `data['stroke_rgba']` 专门用于描边颜色
- 填充和描边可以有不同的颜色，甚至各自独立渐变

逐顶点存储颜色和宽度意味着描边和填充都可以实现沿路径变化的效果——例如一条线段从红色渐变到蓝色、从粗变细。

## 着色器参数：uniform_dtype 扩展

VMobject 的 `uniform_dtype` 在 COMMON_UNIFORMS 基础上增加了多个矢量图形渲染专用的 uniform 参数（F-072）：

| uniform 字段 | 维度 | 说明 |
|--------------|------|------|
| `anti_alias_width` | 1 | 抗锯齿宽度，控制描边边缘的平滑程度 |
| `joint_roundness` | 1 | 线连接点圆度，控制折线拐角是尖锐还是圆润 |
| `flat_stroke` | 1 | 平面描边开关，禁用视角相关的粗细变化 |
| `stroke_width_in_scene_units` | 1 | 描边宽度是否使用场景单位（而非像素） |
| `unit_normal` | 3 | 单位法向量（用于3D场景的光照计算） |
| `fill_rgba` | 4 | 填充颜色（逐对象，与逐顶点 fill_rgba 配合） |
| `fill_rgba_end` | 4 | 渐变终点填充颜色 |
| `gradient_start` | 3 | 渐变起点位置 |
| `gradient_end` | 3 | 渐变终点位置 |
| `fill_border_width` | 1 | 填充边界宽度 |

这些 uniform 参数对整个 VMobject 的所有顶点生效，控制描边和填充的全局渲染效果。`anti_alias_width` 默认 1.5（F-073），提供了合适的抗锯齿效果。`fill_rgba` 和 `fill_rgba_end` 配合 `gradient_start`/`gradient_end` 可以实现线性渐变填充。

## VMobject 初始化参数

VMobject `__init__` 方法接收以下参数（F-073）：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `color` | | 主颜色（同时影响填充和描边） |
| `fill_color` | | 填充颜色，默认继承 color |
| `fill_opacity` | `0.0` | 填充不透明度，默认为 0（不填充） |
| `stroke_color` | | 描边颜色，默认继承 color |
| `stroke_opacity` | `1.0` | 描边不透明度，默认 1（完全不透明） |
| `stroke_width` | `DEFAULT_STROKE_WIDTH` | 描边宽度 |
| `stroke_behind` | `False` | 描边是否在填充后面渲染 |
| `background_image_file` | | 背景图片文件路径 |
| `long_lines` | `False` | 是否优化长线段渲染 |
| `joint_roundness` | `0.0` | 连接点圆度 |
| `flat_stroke` | `False` | 平面描边 |
| `stroke_width_in_scene_units` | `False` | 描边宽度使用场景单位 |
| `use_simple_quadratic_approx` | `False` | 使用简单二次逼近 |
| `anti_alias_width` | `1.5` | 抗锯齿宽度 |
| `fill_border_width` | `0.0` | 填充边界宽度 |

注意 `fill_opacity` 默认为 `0.0`——这意味着新创建的 VMobject 默认只有描边，没有填充。如果需要填充形状内部，必须显式设置 `fill_opacity > 0` 或调用 `set_fill()` 方法。这与许多图形库"默认填充白色"的行为不同，是 ManimGL 常见的初学者陷阱之一。

### 常用颜色设置方法

VMobject 提供了便捷的颜色设置方法：

```python
# 同时设置填充和描边
circle.set_color(BLUE)

# 只设置填充
circle.set_fill(BLUE, opacity=0.5)

# 只设置描边
circle.set_stroke(BLUE_E, width=4, opacity=1.0)

# 设置透明度
circle.set_opacity(0.8)
```

## 几何常量

`manimlib/mobject/geometry.py` 第38-42行定义了几何图形使用的尺寸常量（F-074）：

| 常量 | 值 | 说明 |
|------|-----|------|
| `DEFAULT_DOT_RADIUS` | `0.08` | 默认点（Dot）半径 |
| `DEFAULT_SMALL_DOT_RADIUS` | `0.04` | 默认小点半径 |
| `DEFAULT_DASH_LENGTH` | `0.05` | 默认虚线线段长度 |
| `DEFAULT_ARROW_TIP_LENGTH` | `0.35` | 默认箭头尖端长度 |
| `DEFAULT_ARROW_TIP_WIDTH` | `0.35` | 默认箭头尖端宽度 |

这些常量是几何图形构造函数中对应参数的默认值，保证了整个库中图形尺寸的一致性。

## TipableVMobject：可加箭头的矢量对象

TipableVMobject 定义在 `manimlib/mobject/geometry.py` 第46行，继承自 VMobject（F-075），为 Arc（弧）和 Line（直线）等路径类对象提供箭头尖端的共享功能。不是所有 VMobject 都需要加箭头（例如填充的圆形不需要），因此箭头机制通过中间类 TipableVMobject 提供，而非直接放在 VMobject 中。

### tip_config：箭头默认配置

TipableVMobject 定义了 `tip_config` 类字典，存储箭头尖端的默认配置（F-076）：

```python
tip_config = {
    "fill_opacity": 1.0,
    "stroke_width": 0.0,
    "tip_style": 0.0
}
```

`tip_style` 控制箭头形状（F-076）：
- `0.0`：三角形箭头（默认）
- `1.0`：内平滑箭头
- `2.0`：点状箭头

`fill_opacity=1.0` 和 `stroke_width=0.0` 表示箭头默认完全填充且无描边，呈现为实心三角形。

### add_tip() 方法

`add_tip(at_start=False, **kwargs)` 方法（F-077）是添加箭头的核心接口，执行以下步骤：

```
add_tip(at_start=False, **kwargs)
  → create_tip()           # 创建 ArrowTip 实例
  → reset_endpoints_based_on_tip()  # 根据箭头大小调整路径端点，避免箭头重叠在路径上
  → asign_tip_attr()       # 将 tip 赋值给 self.tip 或 self.start_tip
  → tip.set_color()        # 设置箭头颜色与主对象一致
  → self.add(tip)          # 将箭头作为子对象加入 submobjects
```

`at_start=False`（默认）在路径终点加箭头，`at_start=True` 在路径起点加箭头。一个对象可以同时添加起点箭头和终点箭头（双向箭头）。

箭头作为 submobject 加入 TipableVMobject 后，会随主对象一起移动、旋转、缩放、变色和参与动画——对 Line 调用 `set_color(RED)` 也会改变箭头颜色，`line.animate.shift(RIGHT)` 会让箭头一起移动。这种"箭头是子对象"的设计充分利用了 Mobject 的 family 机制，无需额外代码就实现了箭头与路径的联动。

## 常用几何类

基于 VMobject 和 TipableVMobject，geometry.py 提供了多种常用几何图形类。根据 F-074 ~ F-077 以及模块导入列表（F-006），以下是 ManimGL 提供的主要几何图形类：

### 基础形状类

这些类继承自 VMobject，是预定义好形状的闭合路径：

| 类名 | 说明 |
|------|------|
| `Circle` | 圆形，参数含 radius（半径）、color 等 |
| `Ellipse` | 椭圆，参数含 width、height |
| `Square` | 正方形，参数含 side_length（边长） |
| `Rectangle` | 矩形，参数含 width、height |
| `RegularPolygon` | 正多边形，参数含 n（边数） |
| `Triangle` | 三角形（正三角形的别名/特例） |
| `Polygon` | 任意多边形，参数为顶点列表 |
| `Dot` | 实心圆点，默认半径 `DEFAULT_DOT_RADIUS`（0.08） |
| `SmallDot` | 小实心圆点，默认半径 `DEFAULT_SMALL_DOT_RADIUS`（0.04） |
| `Annulus` | 环形（圆环） |

### 线条与弧类（继承 TipableVMobject）

这些类继承自 TipableVMobject，支持 `add_tip()` 添加箭头：

| 类名 | 说明 |
|------|------|
| `Line` | 直线段，参数含 start、end 两点 |
| `DashedLine` | 虚线，线段由 `DEFAULT_DASH_LENGTH` 控制 |
| `Arc` | 圆弧，参数含 start_angle、angle、radius |
| `ArcBetweenPoints` | 两点间的弧 |
| `CurvedArrow` | 弧形箭头（Arc + tip） |
| `TangentLine` | 切线 |

### 箭头类

箭头类在 Line/TipableVMobject 基础上预置了箭头尖端：

| 类名 | 说明 |
|------|------|
| `Arrow` | 直箭头，默认在终点添加三角形 tip，tip 长度 `DEFAULT_ARROW_TIP_LENGTH`（0.35） |
| `ArrowTip` | 箭头尖端形状（三角形），供 add_tip() 内部使用 |
| `Vector` | 从原点出发的箭头 |
| `DoubleArrow` | 双向箭头（起点和终点都有 tip） |

### 箭头使用示例

```python
from manimlib import *

# 创建直线并在终点添加箭头
line = Line(LEFT, RIGHT)
line.add_tip()  # 默认在终点加三角形箭头

# 创建双向箭头（起点和终点都加箭头）
line.add_tip(at_start=True)

# 创建预置箭头
arrow = Arrow(LEFT * 3, RIGHT * 3, color=BLUE)

# 弧形箭头
curved = CurvedArrow(LEFT * 2, RIGHT * 2, angle=TAU / 4)
```

## 几何图形使用示例

以下是常见几何图形的创建和配置示例：

```python
from manimlib import *

class GeometryExample(Scene):
    def construct(self):
        # 圆形：蓝色描边，半透明填充
        circle = Circle()
        circle.set_stroke(BLUE_E, width=4)
        circle.set_fill(BLUE, opacity=0.5)
        
        # 正方形：红色，无填充，较粗描边
        square = Square()
        square.set_stroke(RED, width=3)
        square.next_to(circle, RIGHT, buff=1)
        
        # 直线带箭头
        arrow = Arrow(LEFT, RIGHT * 3)
        arrow.set_color(YELLOW)
        arrow.next_to(circle, DOWN, buff=1)
        
        # 实心点
        dot = Dot(point=UP * 2, color=GREEN)
        
        # 添加到场景
        self.add(circle, square, arrow, dot)
        self.wait()
```

注意事项：
1. 默认 `fill_opacity=0`，不设置填充时形状是中空的——需要填充必须显式设置 `set_fill()` 或 `fill_opacity`
2. 几何对象创建后默认在原点，需要用 `move_to()`、`next_to()`、`to_edge()` 等方法定位
3. 颜色参数接受颜色常量（如 `BLUE`、`RED_C`）或十六进制字符串
4. `shift()`/`scale()`/`rotate()` 等变换方法对所有 VMobject 子类都生效
5. `animate` 语法糖同样适用于几何图形，`circle.animate.set_fill(RED)` 可以制作颜色渐变动画

## 相关概念

- [03 Mobject：数学对象基类](03-mobject-fundamentals.md)
- [05 动画基础](05-animation-basics.md)
- [06 Transform 深度解析](06-transform-deep-dive.md)
- [08 常量系统与颜色体系](08-constants-and-colors.md)
