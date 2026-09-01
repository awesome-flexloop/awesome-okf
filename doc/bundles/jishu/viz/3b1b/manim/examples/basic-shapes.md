---
type: Example
title: 基础图形绘制
description: 学习创建圆形、方形、三角形、线条、箭头等基础几何图形，掌握颜色填充、描边设置和位置排列方法，通过 ShowCreation（社区版为Create）动画逐个显示图形。
tags: [manimgl, shapes, circle, square, triangle, line, arrow, geometry, fill, stroke, arrange]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: ManimGL 源码事实采集
  - id: concepts-03
    resource: /concepts/03-mobject-fundamentals.md
    title: Mobject：数学对象基类
  - id: concepts-04
    resource: /concepts/04-vmobject-and-geometry.md
    title: VMobject 与几何图形
  - id: concepts-08
    resource: /concepts/08-constants-and-colors.md
    title: 常量系统与颜色体系
  - id: source-code
    resource: /references/manimgl-source-code.md
    title: ManimGL 源码登记
---

# 基础图形绘制

本示例演示 ManimGL 中基础几何图形的创建与配置：圆形（Circle）、方形（Square）、三角形（Polygon）、线条（Line）、箭头（Arrow）。你将学会如何设置填充颜色与透明度、描边颜色与宽度，以及使用 `arrange()` 和 `next_to()` 进行水平排列和相对定位。最终效果是五个基础图形从左到右水平排列，通过 `ShowCreation`（社区版 manim 中名为 `Create`）动画逐个绘制出来，形成一个几何图形展示板。

## 完整代码

```python
from manimlib import *

class BasicShapes(Scene):
    def construct(self):
        # 1. 创建圆形
        circle = Circle()
        circle.set_fill(BLUE, opacity=0.5)
        circle.set_stroke(BLUE_E, width=4)

        # 2. 创建方形
        square = Square()
        square.set_fill(RED, opacity=0.5)
        square.set_stroke(RED_E, width=4)

        # 3. 创建三角形（使用 Polygon 定义三个顶点）
        triangle = Polygon(
            UP,
            LEFT + DOWN,
            RIGHT + DOWN,
        )
        triangle.set_fill(GREEN, opacity=0.5)
        triangle.set_stroke(GREEN_E, width=4)

        # 4. 创建线条
        line = Line(LEFT * 0.5, RIGHT * 0.5)
        line.set_stroke(YELLOW, width=6)

        # 5. 创建箭头
        arrow = Arrow(LEFT * 0.5, RIGHT * 0.5)
        arrow.set_color(PURPLE)
        arrow.set_stroke(width=4)

        # 6. 将所有图形放入 VGroup 并水平排列
        shapes = VGroup(circle, square, triangle, line, arrow)
        shapes.arrange(RIGHT, buff=0.8)

        # 7. 使用 ShowCreation 动画逐个显示图形（lag_ratio 创造依次出现效果）
        self.play(
            LaggedStart(
                *[ShowCreation(shape) for shape in shapes],
                lag_ratio=0.2,
            ),
            run_time=3,
        )

        # 8. 等待 2 秒展示最终效果
        self.wait(2)
```

## 代码分段解释

### 1. 导入模块

```python
from manimlib import *
```

ManimGL 入口模块通过通配导入导出所有核心类和常量（F-003~F-009）：`Scene`、`Circle`、`Square`、`Polygon`、`Line`、`Arrow`、`VGroup`、`ShowCreation`（社区版为 `Create`）、`LaggedStart`、`BLUE`、`BLUE_E`、`UP`、`DOWN`、`LEFT`、`RIGHT` 等均可直接使用，无需单独导入子模块。

### 2. 定义 Scene 子类与 construct 方法

```python
class BasicShapes(Scene):
    def construct(self):
```

所有动画必须定义在继承自 `Scene` 的类中（F-043）。`construct()` 是动画逻辑入口（F-051），ManimGL 在 `run()` 流程中自动调用此方法。

### 3. 创建圆形

```python
circle = Circle()
circle.set_fill(BLUE, opacity=0.5)
circle.set_stroke(BLUE_E, width=4)
```

- `Circle()` 创建一个圆形 VMobject 实例，默认半径为 1 个单位，位于原点。圆形继承自 VMobject（F-068），支持描边和填充渲染。
- `set_fill(BLUE, opacity=0.5)` 设置填充颜色为中位蓝 `BLUE`（即 `BLUE_C`，F-039），不透明度 0.5（半透明）。注意 VMobject 默认 `fill_opacity=0.0`（F-073），不设置填充则形状是中空的。
- `set_stroke(BLUE_E, width=4)` 设置描边颜色为最深一级蓝色 `BLUE_E`（F-038），描边宽度 4 像素。

### 4. 创建方形

```python
square = Square()
square.set_fill(RED, opacity=0.5)
square.set_stroke(RED_E, width=4)
```

- `Square()` 创建正方形 VMobject，默认边长 2 个单位（即从 -1 到 +1），位于原点。
- 使用红色系配色：`RED`（中位红，F-039）填充，`RED_E`（深红，F-038）描边，遵循 3B1B 典型配色模式——C 级填充、E 级描边。

### 5. 创建三角形（Polygon）

```python
triangle = Polygon(
    UP,
    LEFT + DOWN,
    RIGHT + DOWN,
)
triangle.set_fill(GREEN, opacity=0.5)
triangle.set_stroke(GREEN_E, width=4)
```

- `Polygon` 接受任意数量的顶点坐标作为参数，依次连接形成闭合多边形（F-006 中 geometry 模块导出）。这里定义了三个顶点：上方 `UP`（即 `[0, 1, 0]`，F-033）、左下方 `LEFT + DOWN`（即 `[-1, -1, 0]`）、右下方 `RIGHT + DOWN`（即 `[1, -1, 0]`），构成一个等腰三角形。方向向量支持加法运算组合。
- 使用绿色系配色：`GREEN`（中位绿）填充，`GREEN_E`（深绿）描边。

### 6. 创建线条

```python
line = Line(LEFT * 0.5, RIGHT * 0.5)
line.set_stroke(YELLOW, width=6)
```

- `Line(start, end)` 创建直线段，继承自 TipableVMobject（F-075）。参数为起点和终点坐标，这里从 `LEFT * 0.5`（即 `[-0.5, 0, 0]`）到 `RIGHT * 0.5`（即 `[0.5, 0, 0]`），长度为 1 个单位。
- 线条只有描边没有填充，因此只调用 `set_stroke()` 设置黄色 `YELLOW`（中位黄，F-039）和较粗的线宽 6。

### 7. 创建箭头

```python
arrow = Arrow(LEFT * 0.5, RIGHT * 0.5)
arrow.set_color(PURPLE)
arrow.set_stroke(width=4)
```

- `Arrow(start, end)` 创建预置三角形尖端的箭头，在 Line 基础上自动添加 ArrowTip（F-077 中 add_tip 机制）。箭头尖端默认长度为 `DEFAULT_ARROW_TIP_LENGTH`（0.35，F-074）。
- `set_color(PURPLE)` 同时设置填充和描边颜色为紫色 `PURPLE`（中位紫，F-039）。箭头尖端是实心填充，箭杆是描边，`set_color()` 统一设置两者。
- `set_stroke(width=4)` 单独设置箭杆描边宽度。

### 8. 分组与水平排列

```python
shapes = VGroup(circle, square, triangle, line, arrow)
shapes.arrange(RIGHT, buff=0.8)
```

- `VGroup(*mobjects)` 将多个 Mobject 组合成一个组（等价于 `circle + square + triangle + line + arrow`，利用 `__add__` 运算符，F-066）。VGroup 本身也是 Mobject，其 submobjects 包含传入的所有对象，对 VGroup 的操作（如移动、动画）会递归应用到整个 family（F-059 中 family 概念）。
- `arrange(RIGHT, buff=0.8)` 将组内子对象沿 `RIGHT` 方向（水平向右）依次排列，相邻对象之间间隔 0.8 个单位。`arrange()` 是 VMobject/VGroup 的布局方法，自动计算每个子对象的位置，避免手动计算坐标。

### 9. 播放 Create 动画（依次出现）

```python
self.play(
    LaggedStart(
        *[Create(shape) for shape in shapes],
        lag_ratio=0.2,
    ),
    run_time=3,
)
```

- `Create(shape)` 是 creation 模块提供的动画（F-004），逐段绘制 VMobject 的贝塞尔路径，从无到有"画"出图形，非常适合几何图形的出场动画。
- `LaggedStart` 是 composition 模块提供的组合动画（F-004），配合 `lag_ratio=0.2` 让五个图形依次开始创建——第一个图形开始绘制后，等动画进度到 20% 时第二个开始，以此类推，创造波浪式依次出现的效果（F-100 中 lag_ratio 参数，F-108 中 get_sub_alpha 计算机制）。
- `run_time=3` 指定总动画时长为 3 秒。

### 10. 等待

```python
self.wait(2)
```

`self.wait(2)` 保持当前画面 2 秒（F-091 中 wait 概念），让观众看清最终排列效果。不带参数时默认等待 1 秒。

## 运行说明

1. 将上述代码保存为 `basic_shapes.py` 文件
2. 在命令行中运行：

```bash
manimgl basic_shapes.py BasicShapes
```

3. ManimGL 将打开实时预览窗口，播放动画。

常用命令行选项：
- 渲染为视频文件：`manimgl basic_shapes.py BasicShapes -w`（F-014）
- 1080p 画质：`manimgl basic_shapes.py BasicShapes -w --hd`（F-016）
- 渲染为 GIF：`manimgl basic_shapes.py BasicShapes -w -i`（F-017）

## 预期效果

运行后你将看到：

1. **黑色背景**上，五个图形从左到右依次被"画"出来——蓝色圆形最先出现，然后红色方形、绿色三角形、黄色线条，最后紫色箭头。每个图形开始绘制时有短暂的重叠延迟，形成流畅的波浪式出场。
2. 五个图形水平等距排列，间距均匀。圆形和方形较大，三角形略高，线条和箭头较细，形成大小对比。
3. 圆形、方形、三角形是半透明填充加深色描边的效果；线条是纯描边；箭头是紫色实心箭头加描边箭杆。
4. 所有图形绘制完成后，画面静止 2 秒，之后进入交互模式（可鼠标拖拽平移、滚轮缩放）。

## 相关概念

- [03 Mobject：数学对象基类](../concepts/03-mobject-fundamentals.md) — Mobject 基类、data/uniforms 双数组、family 树形结构、animate 语法糖
- [04 VMobject 与几何图形](../concepts/04-vmobject-and-geometry.md) — VMobject 描边填充机制、贝塞尔路径、TipableVMobject 箭头机制、常用几何类
- [05 动画基础](../concepts/05-animation-basics.md) — Animation 生命周期、lag_ratio 子对象延迟、ShowCreation（社区版Create）等内置动画
- [08 常量系统与颜色体系](../concepts/08-constants-and-colors.md) — 方向向量（UP/DOWN/LEFT/RIGHT）、五级颜色体系（BLUE/BLUE_E 等）、3B1B 配色方案
