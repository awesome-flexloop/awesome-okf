---
type: Concept
title: Transform 深度解析
description: Transform 是 ManimGL 变换动画的核心，通过 starting_mobject 到 target_copy 的插值实现变形，align_data_and_family 数据对齐是初学者最易踩坑的关键点。
tags: [manimgl, transform, animation, interpolation, path-arc, animate, replacement-transform, move-to-target]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: ManimGL 源码事实采集
---

# Transform 深度解析

Transform（变换动画）是 ManimGL 动画系统中最核心、最常用的动画类，定义在 `manimlib/animation/transform.py` 第24行（F-109），继承自 Animation。Transform 实现了"一个对象平滑变形为另一个对象"的效果，是 3Blue1Brown 视频中那种流畅形变动画的底层机制。理解 Transform 的工作原理——尤其是数据对齐机制——是避免 Manim 动画出现怪异结果的关键（洞察 I-02）。

## Transform 核心原理：不是 A 变 B，而是状态插值

Transform 最容易被误解的一点是：它**不是**"将对象 A 变形为对象 B"。Transform 的实际工作机制是（洞察 I-02）：

1. 动画开始前，创建 `starting_mobject`：即源 mobject 的拷贝（继承自 Animation）
2. 创建 `target_mobject`：用户传入的目标对象
3. 创建 `target_copy`：对 target_mobject 进行拷贝，并调用 `align_data_and_family(target_copy)` 将其数据结构与 starting_mobject 对齐
4. 动画过程中，mobject 从 starting_mobject 的状态**插值**到 target_copy 的状态
5. 动画结束后，若 `replace_mobject_with_target_in_scene` 为 True，在场景中用 target_mobject 替换源 mobject

```python
# 很多初学者以为：circle "变成了" square
self.play(Transform(circle, square))
# 实际发生的是：circle 的顶点数据从圆形插值到（对齐后的）方形顶点数据
# square 本身在动画过程中并没有被修改！
```

理解这一点至关重要——动画结束后，场景中仍然是原来的 `circle` 对象（只是它的顶点数据变成了方形的样子），`square` 对象自始至终没有被加入场景，除非你显式 `self.add(square)` 或使用 ReplacementTransform。

## Transform 类定义与参数

Transform 类有一个关键的类属性 `replace_mobject_with_target_in_scene = False`（F-110），控制动画结束后是否在场景中替换对象。

### __init__ 参数

Transform `__init__` 在 Animation 参数基础上增加了以下参数（F-111）：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `mobject` | 必填 | 源对象（起始状态） |
| `target_mobject` | `None` | 目标对象（结束状态） |
| `path_arc` | `0.0` | 弧形路径半径，float 或 `(radius, axis)` 元组 |
| `path_arc_axis` | `OUT` | 弧形路径的旋转轴（默认垂直屏幕） |
| `path_func` | `None` | 自定义路径函数，覆盖 path_arc |

如果 `target_mobject` 为 None，Transform 会期望 mobject 自身有 `.target` 属性（配合 `generate_target()` 和 MoveToTarget 使用）。

## begin()：数据对齐是最大坑点

Transform 重写了 `begin()` 方法，这是整个 Transform 最关键的步骤（F-113）：

```python
def begin(self):
    self.create_target()                     # 创建或获取 target_mobject
    self.check_target_mobject_validity()    # 验证目标对象有效性
    
    if self.is_aligned_with:
        self.target_copy = self.target_mobject
    else:
        self.target_copy = self.target_mobject.copy()
        self.mobject.align_data_and_family(self.target_copy)  # 数据对齐！
    
    super().begin()  # 调用 Animation.begin()，创建 starting_mobject 等
```

### align_data_and_family：为什么你的变换结果很奇怪

初学者使用 Transform 最常遇到的问题是"变换结果乱七八糟"或"顶点飞得到处都是"，99% 的原因是没有理解 `align_data_and_family` 的作用。

Transform 做插值时，要求 starting_mobject 和 target_copy 满足以下条件：
1. **子对象数量相同**：两者的 family 列表长度必须一致
2. **顶点数量相同**：对应 submobject 的 data 数组长度（顶点数）必须相同
3. **子对象结构一致**：对应 submobject 的类型和结构要兼容

如果不满足这些条件，Mobject 的插值是按顶点位置一一对应的——第 i 个顶点从起点插值到终点的第 i 个顶点。如果圆形有 4 个顶点而方形有 4 个顶点，刚好对应；但如果圆形有 8 个顶点（更平滑的圆）而三角形只有 3 个顶点，多余的顶点会飞到奇怪的位置。

`align_data_and_family` 方法的作用就是让 target_copy 的数据结构与 mobject 对齐，包括：
- 对齐 submobjects 数量和层级
- 对齐顶点数量（通过补点或采样）
- 对齐 data 数组长度

```python
# 错误示范：两个结构不兼容的对象直接 Transform
# Circle() 默认是 4 个贝塞尔曲线段共 8 个控制点？不，实际上 Manim 的 Circle
# 由 4 段三次贝塞尔曲线构成，每段 4 个控制点...
# 实际中更常见的坑是 Tex 字符数量不同导致的变换问题

# 正确做法：当结构可能不兼容时，使用 ReplacementTransform
self.play(ReplacementTransform(circle, text))  # 不要求结构兼容
```

### create_target 与 target_copy

`create_target()` 方法负责创建或获取 target_mobject：
- 如果构造时传入了 target_mobject，直接使用
- 如果未传入，检查 mobject.target 属性（需要先调用 `mobject.generate_target()`）

`target_copy` 是 target_mobject 的拷贝（或引用，当 is_aligned_with 为 True 时），所有插值计算都在 target_copy 上进行，不会修改原始的 target_mobject。这保证了 target_mobject 可以被多个 Transform 复用。

## path_arc：弧形路径变换

默认情况下，Transform 中的每个顶点沿直线从起点移动到终点（使用 `straight_path` 函数）。`path_arc` 参数可以让顶点沿圆弧运动，创造弧形变换效果。

### 直线 vs 弧形路径

```python
# 默认直线变换：顶点沿直线路径移动
self.play(Transform(circle, square))

# path_arc=PI/2：每个顶点沿 90 度圆弧移动
self.play(Transform(circle, square, path_arc=PI / 2))

# path_arc=PI：半圆弧，顶点绕一大圈到终点
self.play(Transform(circle, square, path_arc=PI))

# 指定弧形轴（3D 场景中有用）
self.play(Transform(circle, square, path_arc=PI / 2, path_arc_axis=RIGHT))
```

`path_arc` 参数表示圆弧对应的圆心角（弧度）。值越大，弧度越弯。`path_arc_axis` 指定圆弧所在平面的法向量。

### init_path_func() 路径函数初始化

`init_path_func()` 方法在 Transform.begin() 中被调用（F-112）：

```python
def init_path_func(self):
    if self.path_func is not None:
        return  # 用户已指定自定义路径函数
    if self.path_arc == 0:
        self.path_func = straight_path
    else:
        self.path_func = path_along_arc(self.path_arc, self.path_arc_axis)
```

- `straight_path(start, end, alpha)`：返回 `start + alpha * (end - start)`，线性插值
- `path_along_arc(arc, axis)` 返回一个路径函数，计算沿圆弧的中间点位置

## path_func：自定义路径函数

如果 `path_arc` 不够灵活，可以传入自定义 `path_func` 完全控制顶点的运动轨迹。

### 路径函数签名

```python
def custom_path(start_points: np.ndarray, end_points: np.ndarray, alpha: float) -> np.ndarray:
    """
    参数:
        start_points: 起点位置，shape=(N, 3) 的 numpy 数组
        end_points: 终点位置，shape=(N, 3) 的 numpy 数组
        alpha: 当前动画进度，0~1
    返回:
        shape=(N, 3) 的中间点位置数组
    """
    # 例如：正弦波动路径
    mid = start_points + alpha * (end_points - start_points)
    mid[:, 1] += 0.5 * np.sin(alpha * PI)  # 加一个上下波动
    return mid
```

### 使用示例

```python
# 让所有顶点在变换过程中绕一个螺旋线移动
def spiral_path(start, end, alpha):
    center = (start + end) / 2
    radius = np.linalg.norm(end - start, axis=1) / 2
    angle = alpha * TAU  # 转一整圈
    offset = np.zeros_like(start)
    offset[:, 0] = radius * np.cos(angle) * (1 - alpha)
    offset[:, 1] = radius * np.sin(angle) * (1 - alpha)
    return start + alpha * (end - start) + offset

self.play(Transform(circle, square, path_func=spiral_path))
```

## interpolate_submobject：插值内核

Transform 的插值过程最终落到 `interpolate_submobject` 方法（F-117）：

```python
def interpolate_submobject(self, submob, start, target_copy, alpha):
    submob.interpolate(start, target_copy, alpha, self.path_func)
```

Mobject 的 `interpolate` 方法对 data 数组中的每个字段进行插值：
- 对 `point` 字段（顶点位置）：使用 `path_func(start_point, end_point, alpha)` 计算中间位置
- 对其他字段（rgba、stroke_width 等）：使用线性插值

这就是为什么 path_func 能控制顶点运动轨迹的原因——它被传入了最底层的顶点插值方法。

## get_all_mobjects：四元组

Transform 重写了 `get_all_mobjects()` 方法，返回四元组而非 Animation 的二元组（F-115）：

```python
def get_all_mobjects(self):
    return [
        self.mobject,          # 当前正在被插值的对象
        self.starting_mobject, # 起始状态（拷贝）
        self.target_mobject,   # 原始目标对象
        self.target_copy       # 对齐后的目标拷贝（用于插值）
    ]
```

`get_interpolation_ends()` 返回 `(starting_mobject, target_copy)`（F-116），这是实际参与插值的两个端点。family zipping 操作将 starting_mobject 和 target_copy 的 family 列表按位置配对。

## animate 语法糖：声明式变换

`mobject.animate` 属性返回 `_AnimationBuilder` 对象（F-063），是 Transform 的声明式语法糖，让动画代码读起来像自然语言。这是 ManimGL 最优雅的 API 设计之一。

### 基本用法

```python
# 链式调用描述终态："圆形动画化地 缩放→移动→变色"
self.play(
    circle.animate.scale(2).shift(RIGHT * 3).set_color(RED),
    run_time=2
)

# 等价于手动创建目标对象和 Transform：
circle.generate_target()
circle.target.scale(2).shift(RIGHT * 3).set_color(RED)
self.play(MoveToTarget(circle), run_time=2)
```

### 工作原理

`_AnimationBuilder` 采用构建器模式：
1. 访问 `mobject.animate` 时创建 `_AnimationBuilder` 实例，持有 mobject 引用
2. 调用 `.scale(2)` 等方法时，构建器**不立即执行**方法，而是记录方法名和参数，返回自身支持链式调用
3. 当 `_AnimationBuilder` 被传入 `self.play()` 时，Scene 调用其 `build()` 方法：
   - 创建 mobject 的一个拷贝作为 target
   - 在拷贝上按链式调用顺序依次执行所有记录的方法
   - 返回一个 Transform（或 MoveToTarget）动画，将原始 mobject 变换到 target 状态

这种设计让动画代码极其简洁，且避免了手动管理 target 对象的麻烦。

### animate 的限制

animate 语法糖虽然方便，但有一个限制：链式调用的方法必须是 Mobject 上返回 self 的方法（即可以链式调用的变换方法）。animate 不能处理有复杂逻辑或需要外部引用的方法，这时仍然需要手动创建 Transform 或使用 updater。

## Transform 变体

Transform 有几个常用的子类变体，适用于不同场景。

### ReplacementTransform：替换变换

`ReplacementTransform` 定义在 `manimlib/animation/transform.py` 第127行（F-118），类属性 `replace_mobject_with_target_in_scene = True`。

与普通 Transform 的关键区别：
- **不要求数据结构兼容**：因为动画结束后，源 mobject 被从场景移除，target_mobject 被加入场景
- **视觉上看起来像变换**：动画过程中仍然做插值，但结束后是真正的"对象替换"
- **适用于不同结构对象间的变换**：圆形变文字、一个图形变另一个结构完全不同的图形

```python
# 圆形变成文字——结构完全不同，必须用 ReplacementTransform
text = Text("Hello")
self.play(ReplacementTransform(circle, text))
# 动画结束后：circle 被 remove，text 在场景中

# 对比：普通 Transform 在结构不兼容时结果不可预测
# self.play(Transform(circle, text))  # 不推荐，可能出现怪异结果
```

`clean_up_from_scene` 方法（F-114）在动画结束时执行替换逻辑：
```python
def clean_up_from_scene(self, scene):
    super().clean_up_from_scene(scene)
    if self.replace_mobject_with_target_in_scene:
        scene.remove(self.mobject)
        scene.add(self.target_mobject)
```

### TransformFromCopy：从副本变换

`TransformFromCopy` 定义在 F-119，同样 `replace_mobject_with_target_in_scene = True`（F-119）。它的构造函数特殊（F-120）：

```python
class TransformFromCopy(Transform):
    def __init__(self, mobject, target_mobject, **kwargs):
        super().__init__(mobject.copy(), target_mobject, **kwargs)
```

`TransformFromCopy(A, B)` 的效果是：看起来从 A 那里"拷贝"出一个新对象，这个新对象变换成 B，而 A 本身保持不动、不消失。这常用于"从已有元素生成新元素"的动画，如从一个公式推出另一个公式。

```python
# 从圆形"复制"出一个方形，圆形留在原地
self.play(TransformFromCopy(circle, square))
# 动画后：circle 和 square 都在场景中
```

### MoveToTarget：移动到目标

`MoveToTarget` 定义在 F-121，是配合 `generate_target()` 使用的便捷动画类（F-122）：

```python
class MoveToTarget(Transform):
    def __init__(self, mobject, **kwargs):
        self.check_validity_of_input(mobject)
        super().__init__(mobject, mobject.target, **kwargs)
```

使用模式：

```python
circle = Circle()
self.add(circle)

# 1. 生成 target
circle.generate_target()

# 2. 修改 target 属性（这不会改变当前显示的 circle）
circle.target.set_color(RED)
circle.target.scale(2)
circle.target.shift(UP * 2)

# 3. 播放动画：circle 平滑变换到 target 状态
self.play(MoveToTarget(circle))

# animate 语法糖就是这种模式的自动化封装
self.play(circle.animate.set_color(BLUE).scale(0.5))
```

MoveToTarget 本质就是 `Transform(mobject, mobject.target)`，它要求你事先调用 `generate_target()` 创建 `.target` 属性。

### 其他常见变体

基于 facts.md 中 animation 子包的导出列表（F-004），还包括：
- `ApplyMethod`：对对象应用一个方法调用作为动画（`ApplyMethod(mobject.shift, RIGHT)` 等价于 `mobject.animate.shift(RIGHT)`）
- `ApplyFunction`：对对象应用一个函数变换
- `TransformMatchingShapes` / `TransformMatchingTex`：智能匹配形状/TeX 部分进行变换（用于公式推导等场景，源和目标有相似结构但顺序不同）
- `Restore`：恢复到 `saved_state`（配合 `mobject.save_state()` 使用）
- `CyclicReplace`：循环替换多个对象
- `Swap`：交换两个对象

## 选择合适的 Transform 类型

| 场景 | 推荐动画类 | 原因 |
|------|-----------|------|
| 同一对象改变属性（位置/颜色/大小） | `mobject.animate.method()` / `MoveToTarget` | 最简洁，对象保持同一个引用 |
| 两个结构兼容的对象之间变换 | `Transform(A, B)` | 顶点一一对应，结果可预测 |
| 两个结构不同的对象之间变换 | `ReplacementTransform(A, B)` | 动画结束后真正替换对象 |
| 从 A 生成 B，A 保留 | `TransformFromCopy(A, B)` | A 不动，B 从 A 的位置"飞出" |
| 公式推导/文字变形，智能匹配部分 | `TransformMatchingTex` / `TransformMatchingShapes` | 自动匹配对应部分，避免整体混乱 |

> **初学者口诀**：同一个对象改属性用 animate；A 变成 B 用 Transform（结构兼容）或 ReplacementTransform（结构不兼容）；从 A 复制出 B 用 TransformFromCopy。

## 相关概念

- [03 Mobject：数学对象基类](/concepts/03-mobject-fundamentals.md)
- [05 动画基础](/concepts/05-animation-basics.md)
- [07 相机与视角控制](/concepts/07-camera-and-frame.md)
- [缓动函数可视化参考](/references/rate-functions-gallery.md)
