---
type: Concept
title: Mobject：数学对象基类
description: Mobject 是 ManimGL 核心抽象，同时承担数学对象语义和 GPU 渲染原语职责，通过 data/uniforms 双数组实现 CPU-GPU 数据统一。
tags: [manimgl, mobject, mathematical-object, data-structure, gpu, opengl]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: ManimGL 源码事实采集
---

# Mobject：数学对象基类

Mobject（Mathematical Object，数学对象）是 ManimGL 的核心抽象基类，定义在 `manimlib/mobject/mobject.py` 第66行（F-056），文档字符串为 "Mathematical Object"。Mobject 采用数据驱动的统一抽象设计——它既是场景图中的数学对象节点（承载点集、子对象层级、几何变换语义），也是 GPU 渲染的原语（直接持有顶点数据和着色器参数）。理解 Mobject 的双数组数据结构和 family 树形组织，是掌握整个 ManimGL 系统的关键（洞察 I-01）。

## 核心抽象：双数组数据驱动

与传统图形引擎"场景图节点"和"GPU 资源"分离的设计不同，Mobject 直接持有两个关键数据结构：`data`（StructuredArray 逐顶点数据）和 `uniforms`（Uniforms 逐对象着色器参数）。这种设计让变换、插值、动画可以直接操作底层 numpy 数组，避免了场景图遍历开销和 CPU-GPU 数据拷贝。

### data_dtype：顶点数据结构

Mobject 类属性 `data_dtype` 是一个 numpy 结构化数据类型，定义了每个顶点的内存布局（F-057）：

```python
data_dtype: np.dtype = [
    ('point', np.float32, (3,)),   # 顶点位置 (x, y, z)
    ('rgba', np.float32, (4,))     # 顶点颜色 (r, g, b, a)
]
```

- `point` 字段：3个 float32，存储顶点的三维坐标
- `rgba` 字段：4个 float32，存储顶点的颜色和不透明度

子类可以扩展 `data_dtype` 增加额外字段。例如 VMobject 增加了 `stroke_rgba`、`stroke_width`、`subpath_range` 等字段（F-071）。

### uniform_dtype：着色器 uniform 参数

Mobject 类属性 `uniform_dtype` 由 `uniform_block_dtype(*COMMON_UNIFORMS)` 生成（F-057），存储逐对象的着色器 uniform 参数。这些参数对整个对象的所有顶点生效，而非逐顶点变化。

`pointlike_data_keys` 类属性为 `['point']`（F-057），标记哪些 data 字段是点位置数据，参与几何变换。`structural_data_keys` 类属性默认为空列表（F-057），子类可扩展用于标记结构相关字段。`pointlike_uniform_keys` 默认为空列表（F-057）。

### data 与 uniforms 的初始化

Mobject 在 `__init__` 中按固定顺序调用初始化方法（F-060）：

```
init_data() → init_uniforms() → init_updaters() → init_event_listners() → init_points() → init_colors()
```

`init_data(length=0)` 方法创建 `self.data: StructuredArray = StructuredArray(self.data_dtype, length)`（F-061），StructuredArray 是 ManimGL 自定义的结构化数组类型，底层基于 numpy 数组但提供了 GPU 友好的内存布局和访问接口。

`init_uniforms()` 方法创建 `self.uniforms: Uniforms = Uniforms(self.uniform_dtype)`（F-062），并设置 `self.uniforms["shading"] = self.shading`（F-062），shading 参数控制三维着色效果。

## submobjects 树形结构与 family 概念

Mobject 通过 `submobjects` 列表组织成树形结构，这是场景图的核心组织方式。

### submobjects、parents 与 family

Mobject 初始化时建立以下树形关系属性（F-059）：

| 属性 | 类型 | 初始值 | 说明 |
|------|------|--------|------|
| `self.submobjects` | `list[Mobject]` | `[]` | 子对象列表 |
| `self.parents` | `list[Mobject]` | `[]` | 父对象列表（支持多个父对象） |
| `self.family` | `list[Mobject] \| None` | `[self]` | 家族列表：包含自身及所有后代 submobjects |

`family` 是一个关键概念——它是"自身 + 递归所有子对象"的扁平列表。当对一个 Mobject 执行变换（shift/scale/rotate）或播放动画时，实际上是对其整个 family 生效。例如对一个 `VGroup` 调用 `shift()`，组内所有元素都会一起移动。

`family` 采用缓存设计：初始为 `[self]`，当 submobjects 变化时需要重新计算。这种设计避免了每次操作都递归遍历子对象树，提升了性能。

### 树形操作方法

Mobject 提供了一系列方法操作 submobject 树：

- `add(*mobjects)`：添加子对象
- `remove(*mobjects)`：移除子对象
- `add_to_back(*mobjects)`：添加到子对象列表末尾（渲染时在底层）
- `get_family()`：获取（并在必要时重新计算）family 列表
- `family_members_with_points()`：过滤掉无点的家族成员

### 与 CameraFrame 的关系

CameraFrame（相机帧）本身也继承自 Mobject（F-087），这意味着相机也是场景图中的一个节点，与其他 mobject 一样在 submobjects 树中。Scene 初始化时 `self.mobjects = [self.camera.frame]`（F-048），相机帧是场景的第一个 mobject，z_index=-1 保证在最底层渲染（F-089）。这种"相机也是 Mobject"的统一抽象是 ManimGL 的优雅设计之一（洞察 I-03）。

## Mobject 初始化参数

Mobject `__init__` 方法接收以下参数（F-058）：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `color` | `DEFAULT_MOBJECT_COLOR` | 对象主颜色，默认从配置读取（F-041），默认 WHITE |
| `opacity` | `1.0` | 不透明度，1.0 完全不透明 |
| `shading` | `(0.0, 0.0, 0.0)` | 三维着色参数 |
| `texture_paths` | `None` | 纹理路径列表 |
| `is_fixed_in_frame` | `False` | 是否固定在相机帧上（不随相机移动） |
| `depth_test` | `False` | 是否启用深度测试（3D 场景用） |
| `z_index` | `0` | 渲染层级，数值越大越靠前 |

这些参数在初始化时被设置为对象属性，并通过 `init_colors()` 等方法写入 data 和 uniforms 数组。

## animate：声明式动画语法糖

`animate` 属性是 ManimGL 声明式动画 API 的核心，它返回一个 `_AnimationBuilder(self)` 对象（F-063），支持链式调用方法描述动画终态。

### 基本用法

```python
# 将圆形向右移动 2 个单位
self.play(circle.animate.shift(RIGHT * 2))

# 链式调用多个方法：同时放大、旋转、变色
self.play(
    circle.animate.scale(2).rotate(PI / 4).set_color(RED),
    run_time=2
)
```

`_AnimationBuilder` 会记录链式调用的方法名和参数，在 `play()` 时自动构建对应的 Animation 对象。这种语法让动画代码读起来像自然语言描述："圆形动画化地 缩放→旋转→设置颜色为红色"。

### 工作原理

当访问 `mobject.animate` 时：
1. 创建 `_AnimationBuilder` 实例，持有对 mobject 的引用
2. 调用 `.method(*args, **kwargs)` 时，将方法名和参数记录到构建器中，返回自身以支持链式调用
3. 当 `_AnimationBuilder` 被传入 `self.play()` 时，Scene 会调用构建器的 `build()` 方法，生成实际的 Animation 对象（通常是 MoveToTarget 或 Transform）

animate 语法糖本质上是 Transform 系统的声明式封装（洞察 I-02），它自动创建目标对象、对齐数据结构、生成插值动画。

## always 与 f_always：每帧更新器

除了一次性的 `play()` 动画，Mobject 还支持持续运行的更新器（updater），每帧都会执行。更新器通过 `always` 和 `f_always` 两个属性构建。

### always：方法调用更新器

`always` 属性返回 `_UpdaterBuilder(self)`（F-064），支持 `mobject.always.method(*args, **kwargs)` 语法，每帧调用指定方法：

```python
# 让圆形每帧都旋转 0.01 弧度
circle.always.rotate(0.01)

# 等价于手动添加 updater：
def update_rotate(mob, dt):
    mob.rotate(0.01)
circle.add_updater(update_rotate)
```

### f_always：函数式更新器

`f_always` 属性返回 `_FunctionalUpdaterBuilder(self)`（F-065），方法参数为函数，每帧调用函数获取参数值再调用方法。这在参数需要动态计算时非常有用：

```python
# 让方形始终跟随圆形位置（偏移一定距离）
square.f_always.move_to(lambda: circle.get_center() + RIGHT * 2)

# 让对象始终面向鼠标
arrow.f_always.rotate(
    lambda: angle_of_vector(self.mouse_point.get_center() - arrow.get_center()),
)
```

`f_always` 比 `always` 更灵活，因为方法参数可以是依赖于其他对象状态或鼠标位置的动态值。

### 更新器执行时机

更新器在 Scene 的 `update_mobjects(dt)` 方法中执行（F-055）——该方法遍历 `self.mobjects`，对每个 mobject 调用 `mobject.update(dt, frame_rate=self.camera.fps)`，dt 是距上一帧的时间间隔（秒）。这意味着更新器可以基于 dt 做帧率无关的运动计算。

## 常用几何变换方法

Mobject 提供了一组基础几何变换方法，这些方法直接操作 `data['point']` 数组中的顶点坐标。所有变换方法都返回 `self`，支持链式调用。

### shift(vector)：平移

沿指定向量平移对象：

```python
circle.shift(RIGHT * 2)       # 右移 2 单位
circle.shift(UP + LEFT * 0.5) # 斜向移动
```

`shift()` 是相对位移，在当前位置基础上移动。对应的绝对定位方法是 `move_to(point)`。

### scale(factor, **kwargs)：缩放

```python
circle.scale(2)        # 放大到 2 倍
circle.scale(0.5)      # 缩小到一半
circle.scale(2, about_point=ORIGIN)  # 以原点为中心缩放
```

默认以对象中心为缩放中心，可通过 `about_point` 参数指定缩放中心。

### rotate(angle, axis=OUT, **kwargs)：旋转

```python
circle.rotate(PI / 4)              # 绕垂直屏幕轴旋转 45 度
circle.rotate(PI / 2, axis=RIGHT)  # 绕 X 轴旋转（3D 效果）
circle.rotate(90 * DEGREES)        # 使用 DEGREES 常量
```

angle 参数单位是弧度。`PI`、`TAU`（2π）、`DEG`（度到弧度转换因子）等常量在 constants.py 中定义（F-036）。

### set_color(color, ...)：设置颜色

```python
circle.set_color(BLUE)
circle.set_color("#FF0000")  # 十六进制颜色
```

`set_color` 会同时影响填充和描边颜色（对 VMobject 而言）。

### move_to(point) / to_edge() / to_corner()：定位

```python
circle.move_to(ORIGIN)         # 移动到原点
circle.to_edge(UP)             # 移动到上边缘
circle.to_corner(UL)           # 移动到左上角
circle.next_to(square, RIGHT)  # 放在 square 右侧，buffered distance 间隔
```

定位方法用于精确控制对象在场景中的位置，是场景布局的基础。

## 运算符重载

Mobject 重载了两个 Python 运算符，提供了简洁的组合语法（F-066、F-067）。

### __add__：对象组合

`self + other` 返回 `self.get_group_class()(self, other)`，将两个 Mobject 组合成一个 Group（F-066）。要求 other 是 Mobject 实例：

```python
group = circle + square  # 创建包含 circle 和 square 的 Group
self.add(group)
self.play(group.animate.shift(UP))  # 两个对象一起移动
```

Group 本身也是 Mobject，它的 submobjects 包含组合的对象，因此对 Group 的操作会应用到所有成员。这等价于 `VGroup(circle, square)`。

### __mul__：复制对象

`self * n`（n 为 int）返回 `self.replicate(n)`，创建 n 个对象的副本（F-067）：

```python
circles = circle * 5  # 创建 5 个圆形副本
for i, c in enumerate(circles):
    c.shift(RIGHT * i)
```

这在需要创建多个相同对象并排列时非常方便。

## 内部状态属性

除了核心的 data、uniforms 和 submobjects 树，Mobject 还维护以下内部状态（F-059）：

| 属性 | 说明 |
|------|------|
| `self.saved_state` | 保存的状态，用于 `save_state()` / `restore()` |
| `self.target` | 动画目标对象，用于 MoveToTarget |
| `self.bounding_box` | 包围盒，shape=(3,3) 的 Vect3Array，存储 min/center/max 点 |
| `self.skip_box_interpolation` | 是否跳过包围盒插值 |
| `self._is_animating` | 是否正在动画中 |
| `self._needs_new_bounding_box` | 包围盒是否需要重新计算 |
| `self.shader_code_replacements` | 着色器代码替换字典，用于自定义着色器 |

`saved_state` 和 `restore()` 用于状态回退：`circle.save_state()` 保存当前状态，经过一系列变换后 `circle.restore()` 可以回到保存的状态。`target` 属性配合 `MoveToTarget` 动画使用（F-121、F-122）。

## Mobject 继承体系

Mobject 是一个抽象基类，ManimGL 中几乎所有可见元素都直接或间接继承自 Mobject：

```
Mobject (mobject.py, F-056)
├── VMobject (types/vectorized_mobject.py, F-068) — 矢量图形基类
│   ├── TipableVMobject (geometry.py, F-075) — 可加箭头的矢量对象
│   │   ├── Arc
│   │   └── Line
│   ├── Circle / Square / Triangle / RegularPolygon — 基础几何图形
│   ├── Arrow / CurvedArrow — 箭头
│   ├── Tex / TexText / MathTex — LaTeX 文字
│   └── SVGPath — SVG 路径
├── CameraFrame (camera/camera_frame.py, F-087) — 相机帧
├── ValueTracker — 值追踪器（不可见，用于驱动动画）
├── Point / Dot — 点
├── Vector — 向量
├── MobjectMatrix / Matrix — 矩阵
└── Group / VGroup — 对象组
```

后续概念文档将详细介绍 VMobject、CameraFrame 等重要子类。

## 相关概念

- [01 第一个 Scene：Hello World](01-hello-world.md)
- [04 VMobject 与几何图形](04-vmobject-and-geometry.md)
- [05 动画基础](05-animation-basics.md)
- [06 Transform 深度解析](06-transform-deep-dive.md)
- [07 相机与视角控制](07-camera-and-frame.md)
