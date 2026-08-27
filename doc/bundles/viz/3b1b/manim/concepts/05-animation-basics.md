---
type: Concept
title: 动画基础
description: Animation 是 ManimGL 动画系统的基类，定义了 begin→interpolate→finish 生命周期，通过 starting_mobject 状态拷贝、lag_ratio 子对象延迟、rate_func 缓动函数实现流畅插值动画。
tags: [manimgl, animation, interpolation, rate-functions, lag-ratio, play, lifecycle]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: ManimGL 源码事实采集
  - id: rate-functions
    resource: /references/rate-functions-gallery.md
    title: 缓动函数可视化参考
---

# 动画基础

Animation（动画）是 ManimGL 动画系统的基类，定义在 `manimlib/animation/animation.py` 第23行（F-099）。所有具体动画（FadeIn、FadeOut、Transform、Write 等）都继承自 Animation。Animation 采用声明式三层架构设计（洞察 I-02）：底层是状态拷贝与插值内核，中层是时间重映射（rate_func、lag_ratio），上层是 Scene.play() 调用机制。理解 Animation 的生命周期和插值原理，是掌握 Manim 动画的基础。

## Animation 基类与生命周期

每个 Animation 实例都对应一个 mobject 的单次动画过程。Animation 定义了两个默认常量（F-098）：`DEFAULT_ANIMATION_RUN_TIME = 1.0`（默认动画时长 1 秒）和 `DEFAULT_ANIMATION_LAG_RATIO = 0`（默认子对象无延迟）。

### __init__ 参数

Animation `__init__` 方法接收以下核心参数（F-100）：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `mobject` | 必填 | 要动画化的 Mobject 实例 |
| `run_time` | `1.0` | 动画持续时间（秒） |
| `time_span` | `None` | `(start, end)` 元组，指定绝对时间区间 |
| `lag_ratio` | `0` | 子对象延迟比例：0=同步，1=逐次，0~1=滞后重叠 |
| `rate_func` | `smooth` | 缓动函数，控制时间到进度的映射 |
| `name` | `""` | 动画名称，用于调试 |
| `remover` | `False` | 动画结束后是否从场景移除 mobject |
| `final_alpha_value` | `1.0` | 动画结束时的 alpha 值（<1 表示不到终点） |
| `suspend_mobject_updating` | `False` | 动画期间是否暂停 mobject 的 updater |

初始化时通过 `_validate_input_type(mobject)` 检查 mobject 是否为 Mobject 实例，否则抛出 TypeError（F-101）。

### 生命周期三阶段

Animation 有清晰的三阶段生命周期，由 Scene 在 `play()` 过程中依次调用：

```
begin() → interpolate(alpha) 多次调用 → finish() → clean_up_from_scene()
```

#### begin()：动画开始

`begin()` 方法在动画第一帧之前调用，执行以下步骤（F-102）：

1. 处理 `time_span` 参数，计算实际 run_time
2. 调用 `mobject.set_animating_status(True)` 标记对象正在动画
3. 调用 `create_starting_mobject()` 创建起始状态拷贝（见下节）
4. 若 `suspend_mobject_updating` 为 True，暂停 mobject 的 updater
5. 调用 `get_all_families_zipped()` 获取配对的家族列表
6. 调用 `prepare_interpolation()` 做插值前准备
7. 调用 `interpolate(0)` 将对象设置到动画起始状态

```python
# begin() 关键逻辑示意
def begin(self):
    self.mobject.set_animating_status(True)
    self.starting_mobject = self.create_starting_mobject()
    self.families = list(self.get_all_families_zipped())
    self.interpolate(0)
```

#### interpolate(alpha)：插值计算

`interpolate(alpha)` 是动画的核心方法，alpha 是动画进度（0.0 到 1.0），由 Scene 根据当前时间和 rate_func 计算得到（F-107）。该方法内部调用 `interpolate_mobject(alpha)`：

```python
def interpolate_mobject(self, alpha):
    for submob, start in self.families:
        sub_alpha = self.get_sub_alpha(alpha, index, len(self.families))
        self.interpolate_submobject(submob, start, sub_alpha)
```

这里体现了 family 递归插值的关键机制：对 mobject 家族中的每个 submobject，根据 lag_ratio 计算其对应的 sub_alpha，然后调用 `interpolate_submobject` 进行具体插值（F-108）。

#### finish()：动画结束

`finish()` 方法在动画最后一帧调用（F-103）：

1. 调用 `interpolate(final_alpha_value)` 确保对象到达最终状态
2. 调用 `mobject.turn_off_interpolation_skip()`
3. 调用 `mobject.set_animating_status(False)` 结束动画状态
4. 恢复 mobject 的 updater（如果之前被暂停）

#### clean_up_from_scene(scene)：场景清理

动画完成后，Scene 调用 `clean_up_from_scene(scene)` 进行清理（F-104）。若 `is_remover()` 返回 True，调用 `scene.remove(self.mobject)` 从场景中移除对象。例如 FadeOut 动画设置 `remover=True`，动画结束后对象自动消失。

## starting_mobject：起始状态拷贝

Animation 最关键的设计之一是 `create_starting_mobject()` 方法（F-105）：

```python
def create_starting_mobject(self):
    return self.mobject.copy()
```

动画开始时，Animation 会对目标 mobject 做一次**深拷贝**，将其状态保存为 `starting_mobject`。在整个动画过程中，mobject 的当前状态从 `starting_mobject` 插值到目标状态，而原始对象本身在动画开始前的状态被完整保留。

> **重要**：这意味着动画不会修改"对象原本应该是什么样子"的参考——如果你在动画过程中暂停，`starting_mobject` 仍然持有动画开始前的完整状态。这也是为什么 Transform 不是"A 变成 B"而是"starting_mobject 插值到 target_copy"（洞察 I-02）。

`get_all_mobjects()` 方法返回 `(self.mobject, self.starting_mobject)` 二元组（F-106），供插值过程使用。Transform 等子类会扩展此方法返回更多对象。

## run_time：动画时长控制

`run_time` 参数控制动画持续时间，单位为秒。Scene 在播放动画时，根据 `run_time` 和帧率（fps，默认 30）计算动画总帧数：

```
总帧数 = run_time × fps
```

例如 `run_time=1.0` 时动画持续约 30 帧，`run_time=2.0` 时持续约 60 帧。

run_time 可以通过 `self.play()` 的关键字参数直接设置，也可以通过 Animation 构造函数设置。常用模式：

```python
# 快速动画：0.5 秒淡入
self.play(FadeIn(circle), run_time=0.5)

# 慢速动画：3 秒的平滑变换
self.play(Transform(circle, square), run_time=3)
```

如果多个动画在同一个 `play()` 中且 run_time 不同，Scene 会以最长的 run_time 为准，较短的动画完成后保持最终状态等待其他动画结束。

## lag_ratio：子对象延迟动画

`lag_ratio` 控制 mobject 家族中子对象动画的时间偏移，创造"波浪式"或"依次"动画效果。这是制作群体动画时最常用的参数之一。

### lag_ratio 取值效果

| 值 | 效果 | 适用场景 |
|----|------|----------|
| `0` | 所有子对象同步动画（默认） | 单个对象、需要整体变换的组 |
| `0~1` | 子对象依次开始，前一个完成一部分后下一个开始 | 文字逐字显示、图形依次出现 |
| `1` | 前一个子对象完全动画完，下一个才开始 | 严格的序列动画 |

### 计算方式

`get_sub_alpha(alpha, index, num_submobjects)` 方法根据 lag_ratio 计算每个子对象的 sub_alpha：

```python
def get_sub_alpha(self, alpha, index, num_submobjects):
    if num_submobjects == 1:
        return alpha
    full_length = (num_submobjects - 1) * self.lag_ratio + 1
    start = index * self.lag_ratio / full_length
    end = (index * self.lag_ratio + 1) / full_length
    return np.clip((alpha - start) / (end - start), 0, 1)
```

当 lag_ratio=0 时，所有子对象的 sub_alpha 都等于 alpha（完全同步）。当 lag_ratio>0 时，每个子对象的动画窗口在时间轴上被拉伸并偏移。

### 使用示例

```python
# 创建 VGroup 包含多个圆形
circles = VGroup(*[Circle() for _ in range(5)])
circles.arrange(RIGHT, buff=0.5)

# lag_ratio=0.1：圆形依次出现，有重叠
self.play(LaggedStart(
    *[FadeIn(c) for c in circles],
    lag_ratio=0.1,
    run_time=2
))

# 或者直接给动画设置 lag_ratio（适用于有子对象的单个 mobject）
text = Text("Hello World")
self.play(Write(text, lag_ratio=0.05))  # 文字逐字写入
```

## rate_func：缓动函数

`rate_func`（缓动函数）是 Manim 动画质感的灵魂。它是一个函数 `f(t) -> alpha`，将标准化时间 `t∈[0,1]` 映射为动画进度 `alpha∈[0,1]`，控制动画的加速度变化。

### 默认缓动函数：smooth

Animation 默认使用 `smooth` 作为 rate_func（F-100）。`smooth(t)` 的公式为（F-133）：

```python
def smooth(t):
    s = 1 - t
    return t**3 * (10*s*s + 5*s*t + t*t)
```

这个函数在 t=0 和 t=1 处的一阶和二阶导数均为 0，等价于三次贝塞尔曲线 `[0,0,0,1,1,1]`，实现了"慢入-慢出"（ease-in-out）的自然效果——动画开始时缓慢加速，中间匀速，结束时缓慢减速，没有生硬的启停感。

### 内置缓动函数全集

ManimGL 提供了 15 种内置缓动函数（F-132~F-146）：

| 函数 | 效果 | 公式/特征 |
|------|------|-----------|
| `linear` | 线性匀速（F-132） | `f(t)=t`，无加速度 |
| `smooth` | 默认平滑（F-133） | 两端零导数，最自然 |
| `rush_into` | 前半段加速（F-134） | `2*smooth(0.5*t)`，快速启动 |
| `rush_from` | 后半段减速（F-135） | `2*smooth(0.5*(t+1))-1`，急停效果 |
| `slow_into` | 圆形缓入（F-136） | `sqrt(1-(1-t)^2)`，沿圆弧进入 |
| `double_smooth` | 双端平滑（F-137） | t<0.5 和 t>0.5 分别 smooth，中间更缓 |
| `there_and_back` | 去程+回程（F-138） | 0→1→0，动画到终点再回来 |
| `there_and_back_with_pause` | 去程-暂停-回程（F-139） | 中间 pause_ratio 区间保持在终点 |
| `running_start` | 启动加速（F-140） | 贝塞尔 `[0,0,pull_factor,pull_factor,1,1,1]` |
| `overshoot` | 过冲回弹（F-141） | 贝塞尔 `[0,0,pull_factor,pull_factor,1,1]`，越过终点再回来 |
| `wiggle` | 来回摆动（F-143） | `there_and_back(t)*sin(wiggles*pi*t)`，抖动效果 |
| `lingering` | 线性后保持（F-145） | 0~0.8 线性，0.8 后保持不动 |
| `exponential_decay` | 指数衰减（F-146） | `1-exp(-t/half_life)`，快速趋近终点 |

### 高阶缓动函数

有两个特殊的高阶函数，它们接受参数并返回新的 rate_func：

**squish_rate_func(func, a, b)**（F-144）：将缓动函数压缩到时间区间 `[a, b]` 内，t<a 时返回 func(0)，t>b 时返回 func(1)，中间映射到 func((t-a)/(b-a))。这用于让动画只在时间轴的某一段发生：

```python
# 动画只在中间 20% 时间段（0.4~0.6）发生
self.play(
    circle.animate.shift(RIGHT),
    rate_func=squish_rate_func(smooth, 0.4, 0.6),
    run_time=2
)
```

**not_quite_there(func, proportion)**（F-142）：返回 `proportion * func(t)`，动画只到达目标的 proportion 比例，不到终点。常用于"走近但不完全到位"的效果。

### 使用自定义 rate_func

任何接受单个 float 参数（t∈[0,1]）并返回 float 的函数都可以作为 rate_func：

```python
# 自定义弹跳效果
def bounce(t):
    return 1 - (1 - t)**2 * np.cos(3 * np.pi * t)

self.play(circle.animate.shift(UP), rate_func=bounce)
```

各种缓动函数的曲线图和可视化效果详见 [/references/rate-functions-gallery.md](../references/rate-functions-gallery.md)。

## self.play() 调用机制

Scene 的 `play()` 方法是触发动画的入口，它负责：

1. 接收一个或多个 Animation 对象（或 animate 语法糖构建的 _AnimationBuilder）
2. 计算每个动画的总时长，取最大值作为本次 play 的总时长
3. 调用所有动画的 `begin()` 方法
4. 进入渲染循环：逐帧计算 alpha（经过 rate_func 映射）→ 调用所有动画的 `interpolate(alpha)` → 渲染帧
5. 调用所有动画的 `finish()` 和 `clean_up_from_scene()`
6. 更新 `self.num_plays` 计数器和 `self.time`

```python
# play() 基本用法：一个动画
self.play(FadeIn(circle))

# 多个动画同时播放
self.play(
    FadeIn(circle),
    FadeIn(square),
    Transform(triangle, target),
    run_time=2,
    rate_func=smooth
)

# run_time 和 rate_func 可以作为 play() 的关键字参数，
# 应用到所有没有单独指定这些参数的动画
```

`self.wait(duration)` 本质上是一个空动画（或暂停），不改变任何 mobject 状态，只是等待指定秒数并渲染静态帧。

## 常用内置动画

通过 `manimlib/__init__.py` 的通配导入（F-004），所有内置动画类可直接使用。以下是基于 animation 子包导出的常用动画类型（客观提及，非完整列表）：

### creation 模块：创建动画
- `Write`：逐笔写入（常用于文字、路径）
- `FadeIn` / `FadeOut`：淡入淡出（fading 模块）
- `GrowFromPoint` / `GrowFromCenter`：从点/中心生长（growing 模块）
- `ShowCreation`：逐段绘制路径

### movement 模块：运动动画
- `MoveToTarget`：移动到 target 对象（F-121）
- `Homogenize`：对齐变换
- `Rotate`：旋转动画

### indication 模块：强调动画
- `Indicate`：高亮强调
- `CircleIndicate`：画圈指示
- `Flash`：闪光效果
- `FocusOn`：聚焦效果

### transform 模块：变换动画
- `Transform`：通用插值变换（F-109）
- `ReplacementTransform`：替换变换（F-118）
- `TransformFromCopy`：从副本变换（F-119）
- `MoveToTarget`：移动到目标（F-121）
- `ApplyMethod`：应用方法调用
- `ApplyFunction`：应用函数变换

Transform 系列动画的详细机制见 [06 Transform 深度解析](06-transform-deep-dive.md)。

### composition 模块：组合动画
- `LaggedStart`：延迟启动（配合 lag_ratio）
- `AnimationGroup`：动画组
- `Succession`：连续播放

### specialized 模块：特殊动画
- `Restore`：恢复到 saved_state
- `TransformMatchingShapes` / `TransformMatchingTex`：匹配形状/文字变换
- `Broadcast`：广播效果

所有这些动画类最终都继承自 Animation，遵循相同的 begin→interpolate→finish 生命周期，只是重写了 `interpolate_submobject` 等方法实现特定效果。

## family 递归插值机制

Animation 的插值是递归的——它不只作用于单个 mobject，而是作用于整个 family（mobject 自身及其所有 submobjects，递归展开）。

`get_all_families_zipped()` 方法将 mobject 的 family 和 starting_mobject 的 family 按位置配对，形成 `[(submob, start_submob), ...]` 的列表。然后 `interpolate_mobject` 遍历这些配对，对每一对调用 `interpolate_submobject`。

这意味着：
- 对 VGroup 播放动画时，组内所有元素都会参与插值
- 子对象的 submobjects 也会递归插值
- lag_ratio 是按 family 的扁平列表顺序计算延迟的

```python
# 对包含 3 个圆形的 VGroup 播放动画
vgroup = VGroup(c1, c2, c3)
self.play(
    vgroup.animate.shift(RIGHT * 2),
    lag_ratio=0.2  # c1 先动，然后 c2，然后 c3
)
```

递归插值的前提是 mobject 和 starting_mobject 的 family 结构完全一致（子对象数量和顺序相同），这也是为什么 Transform 需要 `align_data_and_family` 对齐数据结构（F-113）。

## 相关概念

- [03 Mobject：数学对象基类](03-mobject-fundamentals.md)
- [04 VMobject 与几何图形](04-vmobject-and-geometry.md)
- [06 Transform 深度解析](06-transform-deep-dive.md)
- [缓动函数可视化参考](../references/rate-functions-gallery.md)
- [09 GPU 渲染管线](09-rendering-pipeline.md)
