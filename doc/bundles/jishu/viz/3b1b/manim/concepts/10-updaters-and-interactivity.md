---
type: Concept
title: 更新器与交互式动画
description: Updater（更新器）是 ManimGL 实现每帧动态行为的核心机制，通过 always/f_always 构建器、鼠标交互、撤销重做与 iPython 断点，支持响应式动画与交互式探索。
tags: [manimgl, updater, interactivity, always, f_always, mouse-interaction, undo-redo, embed, ipython]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: ManimGL 源码事实采集
  - id: source-code
    resource: /references/manimgl-source-code.md
    title: ManimGL 源码登记
---

# 更新器与交互式动画

Updater（更新器）是 ManimGL 实现**每帧动态行为**的核心机制。与 Animation 的声明式"开始→插值→结束"生命周期不同，更新器在每一帧渲染前被调用，允许对象持续响应状态变化——追踪位置、跟随鼠标、实时更新外观。结合 Scene 的鼠标状态、撤销重做栈和 iPython 断点，ManimGL 不仅能渲染预定义动画，还支持实时交互式探索，是 3Blue1Brown 视频制作中调试和演示的重要工具。

## 更新器概念

更新器本质是**每帧调用的函数**，附加在 Mobject 上，在 Scene 的帧更新阶段执行。Scene 在 `update_frame(dt)` 中按三步更新（F-053）：`increment_time(dt)` 递增时间 → `update_mobjects(dt)` 遍历所有 mobject 调用 `mobject.update(dt, frame_rate=self.camera.fps)`（F-055）→ `draw_frame(dt, force_draw)` 绘制。更新器就在 `update_mobjects` 阶段执行。

Mobject 初始化时通过 `init_updaters()` 初始化更新器状态（F-060）。每个 mobject 维护一个更新器列表，`update(dt)` 调用时列表中的函数按顺序执行，接收 mobject 自身和时间增量 `dt`。

更新器与动画的核心区别：
- **Animation**：有明确起止，状态从 starting_mobject 插值到目标，时间由 run_time 和 rate_func 控制
- **Updater**：持续运行直到移除，每帧重新计算状态，适合持续跟踪、响应式行为

两者并非互斥——Animation 的 `suspend_mobject_updating` 参数（F-100）可在动画期间暂停更新器，避免冲突。

## add_updater 与更新器管理

Mobject 提供 `add_updater(func)` 附加更新函数，函数接收 mobject 为第一个参数，可选接收 `dt`。通过 `remove_updater(func)` 移除，`clear_updaters()` 清除所有更新器。

```python
circle = Circle()

def rotate_updater(mob, dt):
    mob.rotate(0.5 * dt)

circle.add_updater(rotate_updater)
self.add(circle)
self.wait(5)
circle.remove_updater(rotate_updater)
```

更新器可访问闭包变量和 Scene 状态（如 `self.mouse_point`），执行顺序与添加顺序一致。

## always 构建器：每帧方法调用

`always` 属性是语法糖（F-064），返回 `_UpdaterBuilder(self)`，支持 `mobject.always.method(*args, **kwargs)` 链式调用——每一帧对 mobject 调用指定方法。

```python
circle = Circle()
square = Square()
square.always.move_to(circle)

self.add(circle, square)
self.play(circle.animate.shift(RIGHT * 3))
self.wait()
```

这等价于手动编写：
```python
def follow(mob):
    mob.move_to(circle)
square.add_updater(follow)
```

`always` 支持所有 Mobject 方法，常用场景包括对象始终朝向某点、跟随其他对象移动、ValueTracker 驱动数值变化。

## f_always：函数式更新器构建器

`f_always` 是更灵活的函数式构建器（F-065），返回 `_FunctionalUpdaterBuilder(self)`。与 `always` 传固定参数不同，`f_always` 的参数是**函数**——每帧调用函数获取当前参数值，实现动态响应。

```python
tracker = ValueTracker(0)
circle = Circle()
circle.f_always.set_x(lambda: tracker.get_value() * 3)

self.play(tracker.animate.set_value(2), run_time=3)
```

`f_always` 常配合 `ValueTracker` 使用——ValueTracker 是只存储数值、不渲染可见内容的特殊 Mobject，通过它可以将多个对象的属性绑定到同一个动态值上。`always` 和 `f_always` 体现了 ManimGL 声明式动画哲学（洞察 I-02），让"持续行为"的描述接近自然语言。

## 鼠标交互状态

Scene 维护鼠标交互核心状态（F-049）：`self.mouse_point` 和 `self.mouse_drag_point`，均为 `Point` 实例，分别追踪鼠标当前位置和拖拽位置，在交互循环中持续更新。

`self.mouse_point` 保存鼠标在场景坐标系中的位置，更新器可直接读取实现跟随：

```python
dot = Dot(color=RED)
dot.always.move_to(self.mouse_point)
self.add(dot)
```

`self.mouse_drag_point` 追踪拖拽位置。当 `drag_to_pan` 为 True（默认值，F-044）时，拖拽鼠标平移相机（移动 `self.frame`）。F-049 仅客观描述这两个交互状态存在，完整的点击检测、拖拽绑定由 `InteractiveScene` 提供，将在 videos 知识包详解。

## 撤销重做栈

Scene 内置撤销重做机制（F-048）：`self.undo_stack` 和 `self.redo_stack` 保存场景状态快照。`max_num_saved_states`（默认 50，F-044）控制栈最大容量。

通过 `self.undo()` 撤销上一步，`self.redo()` 重做被撤销的操作，这两个方法在交互模式中绑定到键盘快捷键（通常 Ctrl+Z/Ctrl+Y）：

```python
self.play(FadeIn(circle))
self.play(Transform(circle, square))
self.undo()
self.redo()
```

撤销栈使交互模式成为可反复调整、回溯的编辑环境，是 3Blue1Brown 实时调试场景布局的重要工具。

## interact 交互循环

Scene 的 `run()` 方法在 `construct()` 执行后调用 `interact()`（F-050、F-052）。`interact()` 在窗口存在时进入持续循环，不断调用 `update_frame(1 / self.camera.fps)` 直到窗口关闭：

```python
def interact(self):
    if self.window is None:
        return
    self.hold_on_wait = self.presenter_mode
    while not self.window.is_closing:
        self.update_frame(1 / self.camera.fps)
```

交互循环中，更新器持续运行，鼠标位置实时更新，键盘事件被处理（含撤销重做），相机可通过鼠标拖拽平移、滚轮缩放（由 `pan_sensitivity` 和 `scroll_sensitivity` 控制，F-044），`self.quit_interaction` 标志（F-049）设为 True 时退出循环。`presenter_mode`（F-045）是构造参数，影响交互等待行为。

## embed() 断点与 iPython 集成

CLI 参数 `-e/--embed` 接受行号（F-022），在指定行插入 iPython 断点。代码中也可直接调用 `self.embed()` 启动交互式会话：

```python
class ExampleScene(Scene):
    def construct(self):
        circle = Circle()
        self.play(FadeIn(circle))
        self.embed()
        self.play(circle.animate.shift(RIGHT))
```

执行到 `self.embed()` 时场景暂停，弹出 iPython shell，你可以访问 `self`、检查修改 mobject 状态、手动调用 `self.play()`/`self.add()`、查看 `self.mobjects`、测试动画代码，输入 `exit` 继续执行。embed 断点是 ManimGL 最强大的调试工具，让你在 REPL 中实时探索场景，无需反复重跑脚本。

## InteractiveScene 简介

`InteractiveScene` 是 Scene 的子类，通过通配导入自动可用（F-007），提供更高级的交互能力：可拖拽 mobject、按键回调绑定、鼠标点击事件处理。由于该类在 videos/ 项目中大量使用，详细 API 将在 videos 知识包中讲解。基础场景使用 Scene 结合更新器、`mouse_point` 和 `embed()` 已足够。

## 实用示例

### 跟随鼠标的圆点

```python
class MouseFollower(Scene):
    def construct(self):
        dot = Dot(color=RED, radius=0.15)
        dot.always.move_to(self.mouse_point)
        self.add(dot)
```

### 追踪移动目标的箭头

```python
class ObjectTracker(Scene):
    def construct(self):
        target = Dot(color=BLUE)
        arrow = Arrow(ORIGIN, RIGHT, color=YELLOW, buff=0.1)

        def update_arrow(mob):
            mob.put_start_and_end_on(ORIGIN, target.get_center())

        arrow.add_updater(update_arrow)
        self.add(target, arrow)
        self.play(target.animate.shift(RIGHT * 3), run_time=2)
```

这两个示例展示了更新器核心模式：对象状态由其他状态（鼠标位置、目标位置）实时驱动，你只需描述"A 始终跟随 B"，无需手动处理每帧更新逻辑。

## 相关概念

- [03 Mobject：数学对象基类](03-mobject-fundamentals.md)
- [05 动画基础](05-animation-basics.md)
- [06 Transform 深度解析](06-transform-deep-dive.md)
- [07 相机与视角控制](07-camera-and-frame.md)
- [02 配置系统与 CLI 参数](02-configuration.md)
- [ManimGL 源码登记](../references/manimgl-source-code.md)
