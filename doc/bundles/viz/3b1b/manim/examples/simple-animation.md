---
type: Example
title: 简单动画实战
description: 掌握 Create/FadeIn/FadeOut/Transform/ReplacementTransform 等常用动画，对比不同 rate_func 缓动效果，学习 animate 语法糖链式调用和 lag_ratio 延迟动画。
tags: [manimgl, animation, fadein, fadeout, transform, rate-func, animate, lag-ratio, smooth, there-and-back]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: ManimGL 源码事实采集
  - id: concepts-05
    resource: /concepts/05-animation-basics.md
    title: 动画基础
  - id: concepts-06
    resource: /concepts/06-transform-deep-dive.md
    title: Transform 深度解析
  - id: concepts-03
    resource: /concepts/03-mobject-fundamentals.md
    title: Mobject：数学对象基类
  - id: rate-functions
    resource: /references/rate-functions-gallery.md
    title: 缓动函数可视化参考
  - id: source-code
    resource: /references/manimgl-source-code.md
    title: ManimGL 源码登记
---

# 简单动画实战

本示例系统演示 ManimGL 的核心动画类型：`ShowCreation`（绘制出现，社区版 manim 中名为 `Create`）、`FadeIn`/`FadeOut`（淡入淡出）、`Transform`/`ReplacementTransform`（形变替换），对比不同 `rate_func`（缓动函数）的视觉效果，展示 `animate` 声明式语法糖的链式调用，以及 `lag_ratio` 创造的依次动画效果。最终效果是一个动画小剧场：图形依次出现、变形、缓动对比、延迟入场、最后消失。

## 完整代码

```python
from manimlib import *

class SimpleAnimation(Scene):
    def construct(self):
        # ========== 第一部分：基础出场动画 ==========
        title = Text("动画基础演示", font_size=36)
        title.to_edge(UP)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1)
        self.wait(0.5)

        # 1. ShowCreation：逐段绘制出现（社区版名为Create）
        circle = Circle()
        circle.set_fill(BLUE, opacity=0.5)
        circle.set_stroke(BLUE_E, width=4)
        circle.shift(LEFT * 4 + UP)
        self.play(ShowCreation(circle), run_time=1.5)

        # 2. FadeIn：淡入出现
        square = Square()
        square.set_fill(RED, opacity=0.5)
        square.set_stroke(RED_E, width=4)
        square.next_to(circle, RIGHT, buff=1.5)
        self.play(FadeIn(square, scale=0.8), run_time=1)

        # 3. FadeOut：淡出消失（先创建三角形再淡出）
        triangle = Triangle()
        triangle.set_fill(GREEN, opacity=0.5)
        triangle.set_stroke(GREEN_E, width=4)
        triangle.next_to(square, RIGHT, buff=1.5)
        self.play(FadeIn(triangle, shift=UP * 0.5), run_time=1)
        self.wait(0.3)
        self.play(FadeOut(triangle, scale=0.5), run_time=0.8)

        # ========== 第二部分：Transform vs ReplacementTransform ==========
        # 将圆形变换为星形（Transform：同一对象变形）
        star = Star(n=5)
        star.set_fill(YELLOW, opacity=0.8)
        star.set_stroke(YELLOW_E, width=3)
        star.move_to(circle.get_center())
        self.play(Transform(circle, star), run_time=1.5)
        self.wait(0.5)

        # ReplacementTransform：对象替换（方形被箭头替换）
        arrow = Arrow(LEFT, RIGHT, color=PURPLE)
        arrow.move_to(square.get_center())
        self.play(ReplacementTransform(square, arrow), run_time=1.5)
        self.wait(0.5)

        # ========== 第三部分：rate_func 缓动函数对比 ==========
        # 清除上方图形
        self.play(
            FadeOut(circle),
            FadeOut(arrow),
            FadeOut(title),
            run_time=0.8
        )

        # 创建演示圆形和标签
        demo = Circle(radius=0.5)
        demo.set_fill(BLUE, opacity=0.8)
        demo.set_stroke(BLUE_E, width=3)
        demo.shift(DOWN)
        self.play(FadeIn(demo), run_time=0.5)

        rate_label = Text("smooth", font_size=28)
        rate_label.to_edge(UP)
        self.play(FadeIn(rate_label), run_time=0.5)

        # 逐个演示不同 rate_func 的上下移动效果
        # 1. smooth：默认缓动，慢入慢出
        self.play(demo.animate.shift(UP * 2), run_time=1.5, rate_func=smooth)
        self.play(demo.animate.shift(DOWN * 2), run_time=1.5, rate_func=smooth)

        # 2. linear：匀速线性
        self.play(Transform(rate_label, Text("linear", font_size=28).to_edge(UP)), run_time=0.5)
        self.play(demo.animate.shift(UP * 2), run_time=1.5, rate_func=linear)
        self.play(demo.animate.shift(DOWN * 2), run_time=1.5, rate_func=linear)

        # 3. there_and_back：去而复返
        self.play(Transform(rate_label, Text("there_and_back", font_size=28).to_edge(UP)), run_time=0.5)
        self.play(demo.animate.shift(UP * 2), run_time=2, rate_func=there_and_back)

        # 4. overshoot：过冲回弹
        self.play(Transform(rate_label, Text("overshoot", font_size=28).to_edge(UP)), run_time=0.5)
        self.play(demo.animate.shift(UP * 2), run_time=1.5, rate_func=overshoot)
        self.play(demo.animate.shift(DOWN * 2), run_time=1.5, rate_func=overshoot)

        self.wait(0.5)
        self.play(FadeOut(demo), FadeOut(rate_label), run_time=0.6)

        # ========== 第四部分：animate 链式调用 ==========
        demo_circle = Circle(radius=1)
        demo_circle.set_fill(BLUE, opacity=0.5)
        demo_circle.set_stroke(BLUE_E, width=4)
        self.play(FadeIn(demo_circle), run_time=0.5)

        # animate 链式调用：同时移动、缩放、旋转、变色
        self.play(
            demo_circle.animate
                .shift(RIGHT * 2)
                .scale(1.5)
                .rotate(PI / 4)
                .set_fill(RED, opacity=0.7)
                .set_stroke(RED_E, width=6),
            run_time=2,
            rate_func=smooth
        )
        self.wait(0.5)

        # 恢复
        self.play(
            demo_circle.animate
                .shift(LEFT * 2)
                .scale(1 / 1.5)
                .rotate(-PI / 4)
                .set_fill(BLUE, opacity=0.5)
                .set_stroke(BLUE_E, width=4),
            run_time=1.5
        )
        self.wait(0.3)

        # ========== 第五部分：lag_ratio 延迟动画 ==========
        self.play(FadeOut(demo_circle), run_time=0.5)

        # 创建 5 个圆点
        dots = VGroup(*[
            Dot(radius=0.15, color=color)
            for color in [BLUE_E, BLUE, GREEN, YELLOW, RED]
        ])
        dots.arrange(RIGHT, buff=0.8)
        dots.shift(UP)
        self.play(FadeIn(dots), run_time=0.5)

        lag_label = Text("lag_ratio = 0.3", font_size=24)
        lag_label.next_to(dots, DOWN, buff=1)
        self.play(FadeIn(lag_label), run_time=0.5)

        # lag_ratio=0.3：依次向上跳动
        self.play(
            LaggedStart(
                *[d.animate.shift(UP * 1.5) for d in dots],
                lag_ratio=0.3,
            ),
            run_time=2,
        )
        self.wait(0.3)

        self.play(
            LaggedStart(
                *[d.animate.shift(DOWN * 1.5) for d in dots],
                lag_ratio=0.3,
            ),
            run_time=2,
        )
        self.wait(0.5)

        # ========== 结束：全部淡出 ==========
        self.play(
            FadeOut(dots),
            FadeOut(lag_label),
            run_time=1
        )
        self.wait(0.5)
```

## 代码分段解释

### 导入与场景定义

```python
from manimlib import *

class SimpleAnimation(Scene):
    def construct(self):
```

通过通配导入获得所有动画类（F-004 中 animation 子包的 13 个模块：`ShowCreation`（社区版为 `Create`）来自 creation，`FadeIn`/`FadeOut` 来自 fading，`Transform`/`ReplacementTransform` 来自 transform，`LaggedStart` 来自 composition）。

### 第一部分：基础出场动画

**FadeIn 标题**：

```python
title = Text("动画基础演示", font_size=36)
title.to_edge(UP)
self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1)
```

- `Text()` 创建文字对象。`to_edge(UP)` 将文字移到屏幕上边缘（F-035 中 TOP 位置）。
- `FadeIn(mobject, ...)` 是淡入动画（fading 模块，F-004），`shift=DOWN * 0.3` 参数让文字在淡入的同时从上方略微下移，增加动感。

**ShowCreation 圆形（社区版为 Create）**：

```python
circle = Circle()
circle.set_fill(BLUE, opacity=0.5)
circle.set_stroke(BLUE_E, width=4)
circle.shift(LEFT * 4 + UP)
self.play(ShowCreation(circle), run_time=1.5)
```

- `ShowCreation()`（社区版 manim 中名为 `Create()`）逐段绘制 VMobject 的贝塞尔路径（creation 模块，F-004），适合轮廓清晰的几何图形。`run_time=1.5` 让绘制过程更慢更明显。
- `shift(LEFT * 4 + UP)` 将圆形定位到屏幕左上区域（F-033 方向向量加法）。

**FadeIn 方形**：

```python
square = Square()
square.set_fill(RED, opacity=0.5)
square.set_stroke(RED_E, width=4)
square.next_to(circle, RIGHT, buff=1.5)
self.play(FadeIn(square, scale=0.8), run_time=1)
```

- `next_to(circle, RIGHT, buff=1.5)` 将方形放在圆形右侧，间隔 1.5 个单位（相对定位方法，F-03 中 Mobject 定位方法）。
- `FadeIn(square, scale=0.8)` 让方形从 80% 大小淡入放大到正常大小，创造"弹出"效果。

**FadeOut 三角形**：

```python
triangle = Triangle()
triangle.set_fill(GREEN, opacity=0.5)
triangle.set_stroke(GREEN_E, width=4)
triangle.next_to(square, RIGHT, buff=1.5)
self.play(FadeIn(triangle, shift=UP * 0.5), run_time=1)
self.wait(0.3)
self.play(FadeOut(triangle, scale=0.5), run_time=0.8)
```

- `FadeOut(mobject, scale=0.5)` 让对象在淡出的同时缩小到 50%，FadeOut 设置 `remover=True`（F-104），动画结束后自动从场景移除三角形。

### 第二部分：Transform vs ReplacementTransform

**Transform（同一对象变形）**：

```python
star = Star(n=5)
star.set_fill(YELLOW, opacity=0.8)
star.set_stroke(YELLOW_E, width=3)
star.move_to(circle.get_center())
self.play(Transform(circle, star), run_time=1.5)
```

- `Transform(mobject, target_mobject)` 将 `circle` 从当前状态插值到 `star` 的状态（F-109）。动画结束后，场景中仍然是原来的 `circle` 对象，但其几何形状、颜色等属性已变成星形。Transform 的 `replace_mobject_with_target_in_scene = False`（F-110），目标对象 `star` 不会被加入场景。
- `move_to(circle.get_center())` 确保星形与圆形位置对齐，变形从原位开始。

**ReplacementTransform（对象替换）**：

```python
arrow = Arrow(LEFT, RIGHT, color=PURPLE)
arrow.move_to(square.get_center())
self.play(ReplacementTransform(square, arrow), run_time=1.5)
```

- `ReplacementTransform` 继承自 Transform，但设置 `replace_mobject_with_target_in_scene = True`（F-118）。动画结束后，原始对象 `square` 被从场景中移除，目标对象 `arrow` 被添加到场景中。
- 这在"A 变成 B，之后 B 作为独立对象继续参与动画"的场景中非常有用。Transform 适合"同一个对象改变外观"，ReplacementTransform 适合"一个对象替换为另一个对象"。

### 第三部分：rate_func 缓动函数对比

```python
demo = Circle(radius=0.5)
demo.set_fill(BLUE, opacity=0.8)
demo.set_stroke(BLUE_E, width=3)
demo.shift(DOWN)
rate_label = Text("smooth", font_size=28)
rate_label.to_edge(UP)
```

创建一个蓝色演示圆形和一个显示当前 rate_func 名称的标签，标签固定在屏幕上方。

**1. smooth（默认，F-133）**：

```python
self.play(demo.animate.shift(UP * 2), run_time=1.5, rate_func=smooth)
self.play(demo.animate.shift(DOWN * 2), run_time=1.5, rate_func=smooth)
```

`smooth` 是默认缓动函数，公式为 `t**3 * (10*s*s + 5*s*t + t*t)`（s=1-t），在 t=0 和 t=1 处一二阶导数均为 0，实现"慢入-慢出"的自然效果——开始缓慢加速，中间匀速，结束缓慢减速，没有生硬的启停感。

**2. linear（F-132）**：

```python
self.play(demo.animate.shift(UP * 2), run_time=1.5, rate_func=linear)
self.play(demo.animate.shift(DOWN * 2), run_time=1.5, rate_func=linear)
```

`linear(t) = t`，完全匀速，无加速度变化。视觉上显得机械、生硬，适合需要精确匀速的场景（如时钟指针、匀速传送带）。

**3. there_and_back（F-138）**：

```python
self.play(demo.animate.shift(UP * 2), run_time=2, rate_func=there_and_back)
```

`there_and_back` 让动画进度从 0→1→0，即对象移动到终点后自动返回起点。前半段用 smooth 缓动上去，后半段用 smooth 缓动回来，适合"弹一下就回来"的强调效果。注意这里只需要一个 play()，对象自动回到原位。

**4. overshoot（F-141）**：

```python
self.play(demo.animate.shift(UP * 2), run_time=1.5, rate_func=overshoot)
self.play(demo.animate.shift(DOWN * 2), run_time=1.5, rate_func=overshoot)
```

`overshoot` 使用贝塞尔曲线 `[0,0,pull_factor,pull_factor,1,1]`（默认 pull_factor=1.5），对象会越过终点再弹回，像弹簧到位一样有活力，适合强调到位、选中反馈等场景。

**标签更新使用 Transform**：

```python
self.play(Transform(rate_label, Text("linear", font_size=28).to_edge(UP)), run_time=0.5)
```

通过 `Transform` 将旧标签平滑变形为新标签文字，保持标签位置不变，只改变文字内容，创造连续切换的视觉效果。

### 第四部分：animate 链式调用

```python
self.play(
    demo_circle.animate
        .shift(RIGHT * 2)
        .scale(1.5)
        .rotate(PI / 4)
        .set_fill(RED, opacity=0.7)
        .set_stroke(RED_E, width=6),
    run_time=2,
    rate_func=smooth
)
```

`animate` 返回 `_AnimationBuilder`（F-063），支持链式调用任意 Mobject 方法。ManimGL 自动记录所有链式调用的方法名和参数，在 play() 时构建目标对象（target）并生成 Transform 动画。这段代码让圆形同时执行：右移 2 单位、放大 1.5 倍、旋转 45 度、填充变红色（更不透明）、描边变深红更粗——所有变化在 2 秒内平滑过渡。

animate 语法糖是 ManimGL 声明式动画的核心（洞察 I-02），相比手动创建 target 对象再调用 Transform，代码更简洁、可读性更强。链式调用的顺序不影响最终结果——animate 只关心终态，不关心方法调用顺序。

### 第五部分：lag_ratio 延迟动画

```python
self.play(
    LaggedStart(
        *[d.animate.shift(UP * 1.5) for d in dots],
        lag_ratio=0.3,
    ),
    run_time=2,
)
```

- `LaggedStart` 是 composition 模块的动画组合器（F-004），接收多个动画并按 `lag_ratio` 依次延迟启动。
- `lag_ratio=0.3` 意味着：当第一个圆点的动画进度达到 30% 时，第二个圆点开始动画；第二个到 30% 时第三个开始，以此类推（F-100 中 lag_ratio 计算方式，F-108 中 get_sub_alpha 方法）。
- 效果是五个圆点像波浪一样依次向上弹起，而非同步跳跃。这是制作文字逐字出现、图形依次入场等群体动画的标准模式。

## 运行说明

1. 将代码保存为 `simple_animation.py`
2. 运行命令：

```bash
manimgl simple_animation.py SimpleAnimation
```

3. 预览窗口会按顺序播放五个部分的动画，总时长约 25 秒。

渲染为 1080p 视频文件：

```bash
manimgl simple_animation.py SimpleAnimation -w --hd
```

## 预期效果

动画按五个段落依次播放：

1. **基础出场**：标题"动画基础演示"从上方淡入下移；蓝色圆形用 1.5 秒逐笔绘制出现；红色方形从 80% 大小放大淡入；绿色三角形从上方淡入下移后缩小淡出消失。
2. **Transform 对比**：蓝色圆形平滑变形为黄色五角星；红色方形被紫色箭头替换（替换后方形消失，箭头留在场景中）。
3. **缓动对比**：清除上方图形后，一个蓝色圆形在屏幕下方上下移动，顶部标签依次显示"smooth"（慢入慢出）、"linear"（匀速机械）、"there_and_back"（去而复返，自动弹回）、"overshoot"（过冲回弹），清晰对比四种缓动函数的运动质感差异。
4. **animate 链式**：蓝色圆形在 2 秒内同时右移、放大、旋转 45°、变红色粗描边，然后再恢复原状，展示多属性同时动画的流畅效果。
5. **lag_ratio 波浪**：五个彩色圆点水平排列，像波浪一样依次向上弹起（lag_ratio=0.3 延迟效果），再依次落下，最后全部淡出。

播放结束后进入交互模式，可拖拽平移、滚轮缩放探索场景。

## 相关概念

- [05 动画基础](../concepts/05-animation-basics.md) — Animation 生命周期、run_time/lag_ratio/rate_func 参数、内置动画类型（ShowCreation/社区版Create、FadeIn/FadeOut/Transform）、self.play() 机制
- [06 Transform 深度解析](../concepts/06-transform-deep-dive.md) — Transform 与 ReplacementTransform 的区别、target_copy 机制、路径插值
- [03 Mobject：数学对象基类](../concepts/03-mobject-fundamentals.md) — animate 声明式语法糖、shift/scale/rotate/set_color 等几何变换方法
- [04 VMobject 与几何图形](../concepts/04-vmobject-and-geometry.md) — VMobject 描边填充、Circle/Square/Triangle/Arrow 几何类
- [缓动函数可视化参考](../references/rate-functions-gallery.md) — 15 种内置 rate_func 的曲线图和效果对比
