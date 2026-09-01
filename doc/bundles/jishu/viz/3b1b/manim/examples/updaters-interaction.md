---
type: Example
title: 更新器与交互
description: 掌握 add_updater 基本用法、always/f_always 持续更新、ValueTracker 数值驱动、鼠标位置追踪，实现响应式动画和简单的可交互场景。
tags: [manimgl, updater, interactivity, always, f-always, value-tracker, mouse, add-updater, interactive-scene]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: ManimGL 源码事实采集
  - id: concepts-10
    resource: /concepts/10-updaters-and-interactivity.md
    title: 更新器与交互式动画
  - id: concepts-03
    resource: /concepts/03-mobject-fundamentals.md
    title: Mobject：数学对象基类
  - id: concepts-05
    resource: /concepts/05-animation-basics.md
    title: 动画基础
  - id: source-code
    resource: /references/manimgl-source-code.md
    title: ManimGL 源码登记
---

# 更新器与交互

本示例演示 ManimGL 的 Updater（更新器）机制——每帧调用的函数，让对象持续响应状态变化。与 Animation 的"开始→插值→结束"生命周期不同，更新器持续运行直到移除，适合实现持续旋转、对象跟随、数值驱动动画、鼠标追踪等响应式行为。你将学习 `add_updater` 手动管理、`always`/`f_always` 语法糖、`ValueTracker` 数值驱动，以及通过 `self.mouse_point` 实现鼠标交互。

## 完整代码

```python
from manimlib import *

class UpdatersInteraction(Scene):
    def construct(self):
        # ========== 第一部分：add_updater 基础用法——持续旋转 ==========
        title = Text("更新器演示", font_size=36)
        title.to_edge(UP)
        title.is_fixed_in_frame = True
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=0.8)

        subtitle = Text("1. add_updater 持续旋转", font_size=24, color=YELLOW)
        subtitle.to_corner(UL)
        subtitle.is_fixed_in_frame = True
        self.play(FadeIn(subtitle), run_time=0.5)

        # 创建一个齿轮形状的圆形（用大圆形+小圆形组合模拟）
        gear = VGroup()
        outer = Circle(radius=1.2)
        outer.set_fill(BLUE, opacity=0.5)
        outer.set_stroke(BLUE_E, width=4)
        inner = Circle(radius=0.4)
        inner.set_fill(GREY, opacity=0.8)
        inner.set_stroke(WHITE, width=2)
        teeth = VGroup()
        for i in range(8):
            tooth = Rectangle(width=0.2, height=0.3)
            tooth.set_fill(BLUE_E, opacity=1)
            tooth.set_stroke(width=0)
            angle = i * TAU / 8
            tooth.move_to(outer.get_center() + np.array([np.cos(angle), np.sin(angle), 0]) * 1.2)
            tooth.rotate(angle)
            teeth.add(tooth)
        gear.add(outer, inner, teeth)
        gear.shift(LEFT * 3)

        self.play(FadeIn(gear, scale=0.5), run_time=0.8)

        # 使用 add_updater 让齿轮持续旋转
        def rotate_gear(mob, dt):
            mob.rotate(0.8 * dt)
        gear.add_updater(rotate_gear)

        # 等待 3 秒，期间齿轮持续旋转
        self.wait(3)

        # ========== 第二部分：always 语法糖——对象跟随 ==========
        self.play(
            Transform(subtitle, Text("2. always 对象跟随", font_size=24, color=YELLOW).to_corner(UL)),
            run_time=0.5
        )

        # 创建领导者和跟随者
        leader = Circle(radius=0.4)
        leader.set_fill(RED, opacity=0.8)
        leader.set_stroke(RED_E, width=3)
        leader.shift(RIGHT * 2)

        follower = Circle(radius=0.3)
        follower.set_fill(GREEN, opacity=0.8)
        follower.set_stroke(GREEN_E, width=3)
        follower.shift(RIGHT * 2 + DOWN * 1.5)

        # 添加连接线
        line = Line(leader.get_center(), follower.get_center())
        line.set_stroke(GREY_B, width=2)

        self.play(FadeIn(leader), FadeIn(follower), FadeIn(line), run_time=0.8)

        # follower 始终跟随 leader（保持相对偏移），使用 f_always 动态计算位置
        offset = follower.get_center() - leader.get_center()
        follower.f_always.move_to(lambda: leader.get_center() + offset)

        # 线条始终连接两者
        def update_line(mob):
            mob.put_start_and_end_on(leader.get_center(), follower.get_center())
        line.add_updater(update_line)

        # 移动领导者，跟随者自动跟随
        self.play(leader.animate.shift(UP * 2 + RIGHT * 1), run_time=1.5)
        self.wait(0.5)
        self.play(leader.animate.shift(LEFT * 3 + DOWN * 1), run_time=2)
        self.wait(0.5)
        self.play(leader.animate.shift(RIGHT * 2 + UP * 0.5), run_time=1.5)
        self.wait(1)

        # ========== 第三部分：f_always + ValueTracker 数值驱动 ==========
        self.play(
            Transform(subtitle, Text("3. ValueTracker 数值驱动", font_size=24, color=YELLOW).to_corner(UL)),
            FadeOut(gear),
            FadeOut(leader),
            FadeOut(follower),
            FadeOut(line),
            run_time=0.6
        )

        # 创建 ValueTracker（不可见，只存储数值）
        tracker = ValueTracker(0)

        # 创建一个圆形，其大小、颜色、位置由 tracker 驱动
        dynamic_circle = Circle(radius=0.5)
        dynamic_circle.set_fill(BLUE, opacity=0.7)
        dynamic_circle.set_stroke(BLUE_E, width=3)

        # 创建一个显示数值的文字
        value_label = Text("value = 0.0", font_size=20)
        value_label.next_to(dynamic_circle, DOWN, buff=0.5)

        # 使用自定义 updater 控制圆形的位置、大小和颜色
        def update_circle(mob):
            v = tracker.get_value()
            # X 坐标随值从 -3 到 +7 变化
            mob.move_to(np.array([v * 2 - 3, 0, 0]))
            # 大小随值变化（从 0.5 宽度到 4.5 宽度）
            mob.set_width(0.5 + v * 0.8)
            # 根据值设置颜色（蓝→绿→红渐变）
            if v < 1.5:
                mob.set_fill(BLUE, opacity=0.7)
                mob.set_stroke(BLUE_E, width=3)
            elif v < 3:
                mob.set_fill(GREEN, opacity=0.7)
                mob.set_stroke(GREEN_E, width=3)
            else:
                mob.set_fill(RED, opacity=0.7)
                mob.set_stroke(RED_E, width=3)
        dynamic_circle.add_updater(update_circle)

        # 数值标签也跟随更新
        def update_label(mob):
            mob.become(Text(f"value = {tracker.get_value():.1f}", font_size=20).next_to(dynamic_circle, DOWN, buff=0.5))
        value_label.add_updater(update_label)

        self.add(dynamic_circle, value_label)
        self.play(tracker.animate.set_value(5), run_time=3, rate_func=there_and_back)
        self.wait(0.5)

        # ========== 第四部分：鼠标交互——跟随鼠标的圆点 ==========
        self.play(
            Transform(subtitle, Text("4. 鼠标交互：移动鼠标试试!", font_size=24, color=YELLOW).to_corner(UL)),
            FadeOut(dynamic_circle),
            FadeOut(value_label),
            run_time=0.6
        )

        # 创建跟随鼠标的圆点
        mouse_dot = Dot(radius=0.2, color=RED)
        mouse_dot.always.move_to(self.mouse_point)

        # 创建一个箭头，始终从原点指向鼠标位置
        arrow = Arrow(ORIGIN, RIGHT, color=YELLOW, buff=0.2)
        def update_arrow(mob):
            target = self.mouse_point.get_center()
            if np.linalg.norm(target) > 0.1:
                mob.put_start_and_end_on(ORIGIN, target)
        arrow.add_updater(update_arrow)

        # 创建坐标显示标签
        coord_label = Text("(0.0, 0.0)", font_size=18, color=GREY_B)
        coord_label.to_corner(DL)
        coord_label.is_fixed_in_frame = True
        def update_coord(mob):
            pos = self.mouse_point.get_center()
            mob.become(Text(f"({pos[0]:.1f}, {pos[1]:.1f})", font_size=18, color=GREY_B).to_corner(DL))
        coord_label.add_updater(update_coord)

        hint = Text("移动鼠标观察效果，等待进入下一阶段...", font_size=18, color=GREY_B)
        hint.to_edge(DOWN)
        hint.is_fixed_in_frame = True

        self.add(mouse_dot, arrow, coord_label)
        self.play(FadeIn(hint), run_time=0.5)

        # 等待 5 秒，期间用户可以移动鼠标与场景交互
        self.wait(5)

        # ========== 第五部分：组合演示——追踪动画目标 ==========
        self.play(
            Transform(subtitle, Text("5. 追踪移动目标", font_size=24, color=YELLOW).to_corner(UL)),
            FadeOut(mouse_dot),
            FadeOut(arrow),
            FadeOut(coord_label),
            FadeOut(hint),
            run_time=0.6
        )

        # 创建一个移动的目标
        target = Dot(radius=0.2, color=GOLD)
        target.move_to(LEFT * 5)

        # 创建一个追踪箭头和距离标签
        tracker_arrow = Arrow(ORIGIN, RIGHT, color=PURPLE, buff=0.1)

        dist_label = Text("distance: 0.0", font_size=20, color=WHITE)
        dist_label.is_fixed_in_frame = True
        dist_label.to_corner(DR)

        def update_tracker_arrow(mob):
            mob.put_start_and_end_on(ORIGIN, target.get_center())
        tracker_arrow.add_updater(update_tracker_arrow)

        def update_dist(mob):
            d = np.linalg.norm(target.get_center())
            mob.become(Text(f"distance: {d:.1f}", font_size=20, color=WHITE).to_corner(DR))
        dist_label.add_updater(update_dist)

        self.add(target, tracker_arrow, dist_label)

        # 目标做正弦曲线运动（使用闭包变量追踪时间）
        self.wait(0.5)
        time_var = [0.0]  # 使用列表实现闭包可变变量
        def update_target(mob, dt):
            time_var[0] += dt
            t = time_var[0]
            mob.move_to(np.array([
                (t * 1.5) - 4,
                np.sin(t * 2) * 2,
                0
            ]))
        target.add_updater(update_target)

        self.wait(6)

        # 停止更新器
        target.remove_updater(update_target)
        self.wait(0.5)

        # ========== 结束 ==========
        self.play(
            FadeOut(target),
            FadeOut(tracker_arrow),
            FadeOut(dist_label),
            FadeOut(subtitle),
            run_time=0.8
        )

        end_text = Text("更新器演示完成", font_size=36, color=GREEN)
        self.play(FadeIn(end_text, scale=1.5), run_time=1)
        self.wait(1)
```

## 代码分段解释

### 更新器核心概念

与 Animation 有明确起止不同，Updater（更新器）是**每帧调用的函数**，在 Scene 的帧更新循环 `update_mobjects(dt)` 中执行（F-055），直到被移除。更新器函数接收两个参数：mobject 自身和时间增量 `dt`（距上一帧的秒数），用于帧率无关的计算。

### 第一部分：add_updater 持续旋转

```python
def rotate_gear(mob, dt):
    mob.rotate(0.8 * dt)
gear.add_updater(rotate_gear)
self.wait(3)
```

- `add_updater(func)` 将更新函数附加到 mobject 上（F-03 概念文档）。函数签名为 `func(mob, dt)`，其中 `mob` 是 mobject 自身，`dt` 是距上一帧的时间（秒）。
- `mob.rotate(0.8 * dt)` 每帧旋转 `0.8 * dt` 弧度。乘以 `dt` 保证帧率无关——无论 30fps 还是 60fps，旋转角速度都是 0.8 弧度/秒。
- `self.wait(3)` 等待 3 秒（F-091），期间帧更新循环持续运行，更新器每帧执行，齿轮持续旋转。
- 这是最基础的更新器模式：手动编写函数、手动添加、需要时 `remove_updater(func)` 移除。

### 第二部分：always 语法糖——对象跟随

```python
follower = Circle(...)
offset = follower.get_center() - leader.get_center()
follower.f_always.move_to(lambda: leader.get_center() + offset)
```

- `f_always` 属性返回 `_FunctionalUpdaterBuilder`（F-065），与 `always` 传固定参数不同，`f_always` 的参数是**函数**——每帧调用函数获取当前参数值，再调用目标方法。这里 `move_to` 的参数是 `lambda: leader.get_center() + offset`，每帧重新计算 follower 的目标位置，始终在 leader 旁边保持固定偏移。
- 对于简单的固定参数调用使用 `always`（如 `circle.always.rotate(0.01)`），参数需要动态计算时使用 `f_always`。两者都等价于手动编写 updater，但代码更简洁、更接近声明式风格。

**连接线更新**：

```python
def update_line(mob):
    mob.put_start_and_end_on(leader.get_center(), follower.get_center())
line.add_updater(update_line)
```

使用 `add_updater` 手动更新线条端点。`put_start_and_end_on(start, end)` 是 Line/Arrow 的方法，动态设置起点和终点。每当 leader 或 follower 移动，下一帧线条会自动重新连接两者。

### 第三部分：ValueTracker 数值驱动

```python
tracker = ValueTracker(0)
dynamic_circle = Circle(radius=0.5)
```

`ValueTracker` 是只存储浮点数值、不渲染任何可见内容的特殊 Mobject（概念 10）。它是 ManimGL 中"数值驱动动画"的核心——多个对象的属性可以绑定到同一个 ValueTracker 的值上，实现参数化动画。

```python
def update_circle(mob):
    v = tracker.get_value()
    mob.move_to(np.array([v * 2 - 3, 0, 0]))
    mob.set_width(0.5 + v * 0.8)
    if v < 1.5:
        mob.set_fill(BLUE, opacity=0.7)
    elif v < 3:
        mob.set_fill(GREEN, opacity=0.7)
    else:
        mob.set_fill(RED, opacity=0.7)
dynamic_circle.add_updater(update_circle)
```

使用 `add_updater` 手动编写更新函数，根据 tracker 值同时控制圆形的多个属性：
- X 坐标：`v * 2 - 3`，值从 0 到 5 时 X 从 -3 到 +7
- 宽度：`0.5 + v * 0.8`，值增大时圆形变大
- 颜色：根据值区间切换蓝/绿/红，模拟数值驱动的状态变化

当更新逻辑较复杂（同时修改多个属性、有条件判断），使用 `add_updater` 手动编写函数比 `always`/`f_always` 语法糖更灵活。

```python
self.play(tracker.animate.set_value(5), run_time=3, rate_func=there_and_back)
```

ValueTracker 本身也是 Mobject，支持 `animate` 语法糖（F-063）。通过 `tracker.animate.set_value(5)` 让数值从 0 动画到 5，所有绑定到该 tracker 的 updater 会在动画过程中实时响应，驱动圆形位置、大小、颜色和标签同步变化。`there_and_back` 让数值到 5 后自动回到 0（F-138），实现去而复返的动画效果。

### 第四部分：鼠标交互

```python
mouse_dot = Dot(radius=0.2, color=RED)
mouse_dot.always.move_to(self.mouse_point)
```

Scene 维护 `self.mouse_point` 属性（F-049），是一个 Point 实例，在交互循环中持续更新为鼠标在场景坐标系中的位置。通过 `always.move_to(self.mouse_point)`，圆点每帧移动到鼠标当前位置，实现"鼠标跟随"效果。

```python
arrow = Arrow(ORIGIN, RIGHT, color=YELLOW, buff=0.2)
def update_arrow(mob):
    target = self.mouse_point.get_center()
    if np.linalg.norm(target) > 0.1:
        mob.put_start_and_end_on(ORIGIN, target)
arrow.add_updater(update_arrow)
```

箭头从原点指向鼠标位置，实时展示鼠标相对于原点的方向。`np.linalg.norm(target) > 0.1` 避免鼠标在原点附近时箭头长度为零导致渲染问题。

```python
coord_label = Text("(0.0, 0.0)", font_size=18, color=GREY_B)
coord_label.to_corner(DL)
coord_label.is_fixed_in_frame = True
def update_coord(mob):
    pos = self.mouse_point.get_center()
    mob.become(Text(f"({pos[0]:.1f}, {pos[1]:.1f})", ...).to_corner(DL))
coord_label.add_updater(update_coord)
```

`is_fixed_in_frame = True`（F-058）让坐标标签固定在屏幕左下角，不随任何对象移动。`mob.become(other_mobject)` 是 Mobject 方法，让 mob 变身为另一个 mobject 的状态——这里用于实时更新文字内容。

`self.wait(5)` 等待 5 秒，期间用户可以自由移动鼠标，圆点、箭头、坐标标签实时响应，形成简单的可交互场景。

### 第五部分：追踪移动目标

```python
time_var = [0.0]
def update_target(mob, dt):
    time_var[0] += dt
    t = time_var[0]
    mob.move_to(np.array([
        (t * 1.5) - 4,
        np.sin(t * 2) * 2,
        0
    ]))
target.add_updater(update_target)
```

这个 updater 使用 `dt` 参数驱动时间累积，让目标做正弦曲线运动：
- X 坐标：`(t * 1.5) - 4`——匀速向右移动
- Y 坐标：`np.sin(t * 2) * 2`——正弦上下波动

`time_var = [0.0]` 使用 Python 列表作为闭包中的可变变量（列表是可变对象，内部元素可在闭包函数中修改），每帧累加 `dt` 实现独立的时间轴。追踪箭头和距离标签通过各自的 updater 实时响应目标移动，`distance` 标签显示目标到原点的距离。

```python
target.remove_updater(update_target)
```

`remove_updater(func)` 移除指定的更新函数，目标停止运动（但其他 updater 仍在运行）。`clear_updaters()` 可以移除所有更新器。

## 运行说明

1. 将代码保存为 `updaters_interaction.py`
2. 运行命令：

```bash
manimgl updaters_interaction.py UpdatersInteraction
```

3. 播放到"鼠标交互"部分时，**移动鼠标**可以看到红色圆点跟随鼠标、黄色箭头指向鼠标、左下角实时显示坐标。

渲染为视频文件：

```bash
manimgl updaters_interaction.py UpdatersInteraction -w --hd
```

注意：渲染为视频文件（`-w`）时，鼠标交互部分不会响应真实鼠标（没有窗口交互），鼠标位置保持在原点。鼠标交互效果在实时预览窗口中体验最佳。

交互模式快捷键（动画播放结束后可用）：
- 鼠标拖拽：平移相机
- 鼠标滚轮：缩放
- `i`：在当前位置插入 iPython 断点（`self.embed()`）
- `Ctrl+Z`/`Ctrl+Y`：撤销/重做

## 预期效果

动画按 5 个段落依次播放：

1. **持续旋转**：蓝色"齿轮"（大圆+小圆+8个齿）出现后持续顺时针旋转，3 秒内匀速转动，演示 add_updater 最基础用法。
2. **对象跟随**：红色领导者圆形在画面中移动，绿色跟随者圆形保持固定偏移距离自动跟随，灰色连接线始终连接两者——无论领导者怎么移动，跟随者和线条都实时响应。
3. **ValueTracker 驱动**：圆形的水平位置、大小、颜色随 ValueTracker 数值从 0 到 5 再回到 0（there_and_back）平滑变化：从左向右移动时逐渐变大、颜色从蓝变绿再变红；回程时反向变化。下方数值标签实时显示当前值。
4. **鼠标交互**：提示"移动鼠标试试!"，红色圆点跟随鼠标位置，黄色箭头从原点指向鼠标，左下角显示鼠标坐标。此阶段停留 5 秒供用户交互。
5. **追踪移动目标**：金色目标点沿正弦曲线运动（匀速右移+上下波动），紫色箭头从原点始终指向目标，右下角实时显示目标到原点的距离。6 秒后目标停止，最终显示"更新器演示完成"。

固定在帧上的标题和副标题始终保持在屏幕角落，不受场景内容影响。

## 相关概念

- [10 更新器与交互式动画](../concepts/10-updaters-and-interactivity.md) — add_updater/always/f_always 详解、ValueTracker 用法、鼠标状态 self.mouse_point、embed 断点、interact 交互循环
- [03 Mobject：数学对象基类](../concepts/03-mobject-fundamentals.md) — animate 语法糖、Mobject 方法（shift/scale/rotate/move_to/set_fill/become）、family 机制
- [05 动画基础](../concepts/05-animation-basics.md) — Animation 与 Updater 的区别、play/wait 机制、there_and_back 等 rate_func
- [01 第一个 Scene：Hello World](../concepts/01-hello-world.md) — Scene 生命周期、update_frame/update_mobjects 帧更新循环
