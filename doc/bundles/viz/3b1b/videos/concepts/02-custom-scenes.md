---
type: Concept
title: 自定义 Scene 基类体系
description: Videos 仓库提供了一系列预定义的 Scene 子类，包括自动眨眼的 PiCreatureScene、教室场景 TeacherStudentsScene、坐标图场景 GraphScene 等，通过继承和组合实现场景逻辑复用，避免每个视频重复编写样板代码。
tags: [scene, base-class, inheritance, picreature-scene, graph-scene, composition, reusable]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: Videos 源码事实采集
  - id: insights
    resource: /spec/insights.md
    title: Videos 源码架构洞察
---

# 自定义 Scene 基类体系

在 Manim 中，每个视频对应一个继承自 `Scene` 的 Python 类，`construct()` 方法是动画编排的入口。如果每个视频都从零开始写——创建角色、设置眨眼逻辑、添加坐标轴、配置师生对话——会产生大量重复代码。Videos 仓库通过**自定义 Scene 基类**解决这个问题：把可复用的场景逻辑（自动角色创建、自然眨眼、视线追踪、坐标图设置、师生对话模式）封装到基类中，具体视频场景只需要继承基类，专注于数学内容本身即可。

这种设计遵循"框架模式"：基类封装"不变的流程"（setup、wait时自动眨眼、play时自动视线追踪），子类通过重写钩子方法或配置类属性定义"变化的部分"（创建几个角色、说什么话、画什么图）。本文档详解 Videos 仓库中的核心 Scene 基类、继承组合模式，以及如何选择和编写适合自己的自定义 Scene。

## 为什么要自定义 Scene 基类

直接使用 `Scene` 写带角色的视频时，你需要手动处理很多样板逻辑：

```python
# ❌ 不使用基类：每个场景都要重复写这些逻辑
class MyVideo(Scene):
    def construct(self):
        # 1. 手动创建角色
        teacher = Mortimer().to_corner(DR)
        s1 = Randolph(color=BLUE_D).to_corner(DL)
        s2 = Randolph(color=BLUE_E).next_to(s1, RIGHT)
        s3 = Randolph(color=BLUE_C).next_to(s2, RIGHT)
        self.add(teacher, s1, s2, s3)
        self.pi_creatures = VGroup(teacher, s1, s2, s3)
        
        # 2. 手动在wait中实现眨眼（很容易忘！）
        # 3. 手动在play中让角色看向动画对象
        # 4. 手动创建对话气泡、处理气泡移除
        # ... 真正的数学内容代码
```

使用自定义基类后：

```python
# ✅ 使用TeacherStudentsScene：样板逻辑全部封装好了
class MyVideo(TeacherStudentsScene):
    def construct(self):
        # 角色已经自动创建好：self.teacher + self.students
        # wait()时自动眨眼，play()时自动视线追踪
        # 直接写数学内容，或调用teacher_says()便捷方法
        self.teacher_says("今天学微积分！")
        self.wait(2)
```

基类封装的核心价值：
1. **消除重复代码**：角色创建、眨眼、视线追踪等逻辑只在基类写一次
2. **统一行为**：所有使用该基类的场景行为一致（如都是每3秒眨一次眼）
3. **语义化便捷方法**：`teacher_says()` 比手动创建 SpeechBubble 更易读
4. **约定优于配置**：基类提供合理默认值，子类只在需要时覆盖

## PiCreatureScene：带角色的自动场景

PiCreatureScene 是最常用的自定义基类，定义在 `custom/characters/pi_creature_scene.py`，继承自 InteractiveScene（F-027）。它是所有带 Pi 生物场景的基类，提供自动角色创建、自然眨眼、视线自动追踪三大核心功能。

### 类属性配置

PiCreatureScene 通过类属性提供配置钩子，子类可以覆盖这些属性自定义行为（F-028）：

```python
# custom/characters/pi_creature_scene.py:38-45
class PiCreatureScene(InteractiveScene):
    total_wait_time = 0              # 累计等待时间（内部用）
    seconds_to_blink = 3             # 每3秒自动眨眼一次
    pi_creatures_start_on_screen = True  # 角色是否初始就在屏幕上
    default_pi_creature_kwargs = {
        "color": BLUE,               # 默认角色颜色
    }
    default_pi_creature_start_corner = DL  # 默认起始角落（左下角）
```

**注意**：这是老版本 CONFIG 字典风格，现代 ManimGL 写法直接定义类属性即可（如上面代码所示）。

### setup()：自动创建角色

PiCreatureScene 重写了 `setup()` 方法（Scene 的生命周期钩子，在 construct() 之前自动调用），自动调用 `create_pi_creatures()` 创建角色（F-029）：

```python
# custom/characters/pi_creature_scene.py:47-52（简化逻辑）
def setup(self):
    super().setup()
    self.pi_creatures = self.create_pi_creatures()
    self.primary_pi_creature = self.pi_creatures[0]
    if self.pi_creatures_start_on_screen:
        self.add(self.pi_creatures)
```

子类通过重写 `create_pi_creatures()` 返回想要的角色组即可：

```python
class SingleTeacherScene(PiCreatureScene):
    def create_pi_creatures(self):
        # 只创建一个Mortimer老师放在右下角
        teacher = Mortimer().to_corner(DR)
        return VGroup(teacher)

class SimpleClassroom(PiCreatureScene):
    def create_pi_creatures(self):
        # 创建一个老师+两个学生
        teacher = Mortimer().to_corner(DR)
        s1 = Randolph(color=BLUE_D).to_corner(DL)
        s2 = Randolph(color=BLUE_E).next_to(s1, RIGHT)
        return VGroup(teacher, s1, s2)
```

### wait() 重写：自动眨眼机制

PiCreatureScene 最"隐形"也最能提升生命感的设计是重写了 `wait()` 方法（F-030）：在等待期间，每 `seconds_to_blink`（默认3秒）自动触发一次眨眼，无需手动调用。

```python
# custom/characters/pi_creature_scene.py:212-226（简化逻辑）
def wait(self, duration=1, ...):
    # 如果有停止条件（如交互模式），跳过眨眼
    if stop_condition is not None:
        return self.non_blink_wait(...)
    
    # 正常等待：在等待期间插入眨眼
    time_increments = self.get_wait_time_increments(duration)
    for t in time_increments:
        super().wait(t)
        self.total_wait_time += t
        # 每seconds_to_blink秒眨一次眼
        if self.total_wait_time >= self.seconds_to_blink:
            self.blink()
            self.total_wait_time = 0
```

效果：你只需要正常写 `self.wait(5)`，场景里的所有 Pi 生物会在等待期间自然眨眼3次，就像真实的动画角色一样。如果你需要在某些等待时跳过眨眼（比如快速预览时），使用 `non_blink_wait()` 即可。

### joint_blink()：错峰眨眼效果

如果场景里有多个 Pi 生物，同时眨眼会显得很机械。PiCreatureScene 提供了 `joint_blink()` 方法实现错峰眨眼——多个角色依次眨眼，更加自然（F-069）：

```python
# custom/characters/pi_creature_scene.py:190-210（简化逻辑）
def joint_blink(self, pi_creatures=None, shuffle=True, **kwargs):
    if pi_creatures is None:
        pi_creatures = self.pi_creatures
    if shuffle:
        random.shuffle(pi_creatures)  # 随机化眨眼顺序
    # 使用squish_rate_func和there_and_back实现错峰动画
    anims = []
    for pi in pi_creatures:
        anims.append(ApplyMethod(pi.blink, ...))
    self.play(LaggedStart(*anims, lag_ratio=0.2))
```

### anims_from_play_args() 重写：视线自动追踪

PiCreatureScene 重写的另一个关键方法是 `anims_from_play_args()`，它会在每次调用 `self.play()` 时自动让所有屏幕上的 Pi 生物看向第一个被动画的 Mobject（F-031）。这意味着你不需要手动调用 `look_at()`，角色会自动"关注"正在发生的动画。

```python
# custom/characters/pi_creature_scene.py:156-185（简化逻辑）
def anims_from_play_args(self, args, **kwargs):
    # 1. 先调用父类方法解析所有动画
    anims = super().anims_from_play_args(args, **kwargs)
    
    # 2. 找到第一个被动画的mobject
    target = None
    for anim in anims:
        if hasattr(anim, "mobject") and anim.mobject in self.mobjects:
            target = anim.mobject
            break
    
    # 3. 让所有屏幕上的Pi生物看向这个目标
    if target is not None:
        for pi in self.pi_creatures:
            if pi in self.mobjects:  # 只看屏幕上的
                anims.append(ApplyMethod(pi.look_at, target))
    
    return anims
```

效果：当你写 `self.play(ShowCreation(graph))` 时，场景里的 Pi 生物会自动转头看向正在画出的图像，就像他们在"看"你展示的内容一样自然。

### MortyPiCreatureScene：Mortimer 专用子类

`MortyPiCreatureScene` 是 PiCreatureScene 的简单子类，仅修改默认配置（F-066）：

```python
# custom/characters/pi_creature_scene.py:247-252
class MortyPiCreatureScene(PiCreatureScene):
    default_pi_creature_kwargs = {
        "color": GREY_BROWN,
        "flip_at_start": True,
    }
    default_pi_creature_start_corner = DR  # 右下角
```

这个子类只是省去了你每次手动创建 Mortimer 并放到右下角的样板代码。

## TeacherStudentsScene：教室场景基类

TeacherStudentsScene 继承自 PiCreatureScene，是专门为"老师讲解+学生互动"的教室场景设计的基类（F-032）。这是 Videos 仓库中最"全能"的场景基类之一，3Blue1Brown 视频中大量讲解段落都使用这个基类。

### 默认配置与场景布局

TeacherStudentsScene 预配置了完整的教室布局（F-032、F-033）：

```python
# custom/characters/pi_creature_scene.py:255-298（简化）
class TeacherStudentsScene(PiCreatureScene):
    # 背景色为深灰色，模拟教室环境
    background_color = GREY_E
    # 学生颜色：深浅不同的蓝色
    student_colors = [BLUE_D, BLUE_E, BLUE_C]
    # 老师颜色：灰棕色
    teacher_color = GREY_BROWN
    # 学生缩放0.8（比老师小一点）
    student_scale_factor = 0.8
    # 每2秒眨眼一次（比普通场景更频繁，更活泼）
    seconds_to_blink = 2
    
    def create_pi_creatures(self):
        # 1. 创建老师（Mortimer）放在右下角
        self.teacher = Mortimer(color=self.teacher_color)
        self.teacher.to_corner(DR)
        self.teacher.scale(self.student_scale_factor * 1.2)
        
        # 2. 创建三个学生（Randolph）放在左下角，排成一排
        self.students = VGroup(*[
            Randolph(color=c) for c in self.student_colors
        ])
        self.students.arrange(RIGHT, buff=1.0)
        self.students.scale(self.student_scale_factor)
        self.students.to_corner(DL)
        
        # 3. 创建黑板（ScreenRectangle）在背景
        self.screen = ScreenRectangle()
        self.screen.set_fill(BLACK, opacity=1)
        self.screen.set_stroke(width=0)
        self.screen.center().scale(2)
        
        return VGroup(self.teacher, self.students)
```

默认场景布局：
- 右下角：Mortimer 老师（灰棕色，略大）
- 左下角：三个 Randolph 学生（蓝色渐变，略小，并排）
- 背景：深灰色 + 黑色"黑板"区域

### 便捷方法：师生对话封装

TeacherStudentsScene 提供了一系列语义化便捷方法，封装师生对话的常见模式（F-034）：

| 方法 | 用途 | 示例 |
|------|------|------|
| `teacher_says(content, **kwargs)` | 老师说一句话，带对话气泡 | `self.teacher_says("导数就是斜率")` |
| `student_says(index, content, **kwargs)` | 指定学生说话（index=0/1/2） | `self.student_says(0, "我明白了！")` |
| `teacher_thinks(content, **kwargs)` | 老师思考（思考气泡） | `self.teacher_thinks("这该怎么解释呢...")` |
| `student_thinks(index, content, **kwargs)` | 学生思考 | `self.student_thinks(1, "这不对吧...")` |
| `play_student_changes(*modes, **kwargs)` | 切换学生表情 | `self.play_student_changes("happy", "confused", "erm")` |
| `zoom_in_on_thought_bubble()` | 聚焦放大思考气泡 | 用于"思想实验"或重点讲解（F-070） |

使用示例：

```python
class DerivativeIntro(TeacherStudentsScene):
    def construct(self):
        # 开场：老师说话
        self.teacher_says("导数是什么？")
        self.wait(2)
        
        # 第一个学生开心回答
        self.student_says(0, "斜率！")
        self.play_student_changes("happy", "plain", "plain")
        self.wait()
        
        # 老师表示赞许
        self.teacher_says("非常好！")
        self.play(self.teacher.change_mode, "happy")
        self.wait(2)
        
        # 老师思考，然后放大思考气泡展开讲解
        self.teacher_thinks("但为什么要学导数？")
        self.wait()
        self.zoom_in_on_thought_bubble()
        # ... 在黑板区域展开数学内容
```

### zoom_in_on_thought_bubble()：思想放大效果

这是一个很有创意的方法，通过 ApplyPointwiseFunction 对场景所有 mobject 应用径向变换，实现"聚焦到思考气泡"的视觉效果——背景的角色和物体淡远，思考气泡被放大充满屏幕，自然过渡到深入讲解（F-070）。

## GraphScene：坐标图场景基类（标注废弃风险）

GraphScene 位于 `once_useful_constructs/graph_scene.py`，是专门用于绘制函数图像、坐标轴、黎曼和等数学图表的场景基类。**注意：该类文件开头注释标注了"TODO: this class should be deprecated"，说明在现代 ManimGL 中已经有更好的 Axes 坐标系统替代，但历史视频（如微积分本质系列）大量使用了这个基类（F-035、F-075）。**

### 坐标轴配置

GraphScene 通过类属性配置坐标轴范围和外观（F-036）：

```python
# once_useful_constructs/graph_scene.py:28-51
class GraphScene(Scene):
    # ⚠️ 老版本CONFIG字典写法，新版本使用直接类属性
    CONFIG = {
        "x_min": -1,
        "x_max": 10,
        "x_axis_width": 9,
        "x_tick_frequency": 1,
        "x_leftmost_tick": None,
        "x_labeled_nums": None,
        "x_axis_label": "$x$",
        
        "y_min": -1,
        "y_max": 10,
        "y_axis_height": 6,
        "y_tick_frequency": 1,
        "y_bottom_tick": None,
        "y_labeled_nums": None,
        "y_axis_label": "$y$",
        
        "graph_origin": 2.5 * DOWN + 4 * LEFT,  # 坐标原点位置
        "axes_color": GREY,
        "graph_origin_color": WHITE,
    }
```

### setup_axes()：创建坐标轴

`setup_axes()` 方法在 setup 中调用，创建 NumberLine 作为 x 轴和 y 轴（y 轴旋转 90 度），支持自动添加数字标签和轴名称（F-037）：

```python
# once_useful_constructs/graph_scene.py:61-132（简化）
def setup_axes(self):
    # 1. 创建x轴
    self.x_axis = NumberLine(
        x_min=self.x_min,
        x_max=self.x_max,
        width=self.x_axis_width,
        tick_frequency=self.x_tick_frequency,
        color=self.axes_color,
    )
    self.x_axis.move_to(self.graph_origin, LEFT)
    
    # 2. 创建y轴（x轴旋转90度）
    self.y_axis = self.x_axis.copy().rotate(90 * DEGREES)
    self.y_axis.move_to(self.graph_origin, DOWN)
    
    # 3. 添加数字标签
    if self.x_labeled_nums:
        self.x_axis.add_numbers(*self.x_labeled_nums)
    # ... y轴标签同理
    
    # 4. 添加轴名称
    self.x_axis_label = Tex(self.x_axis_label).next_to(self.x_axis, RIGHT)
    # ... y轴标签同理
    
    self.axes = VGroup(self.x_axis, self.y_axis)
    self.add(self.axes)
```

### 核心功能方法

GraphScene 提供了一系列图表绘制的核心方法（F-038）：

| 方法 | 功能 |
|------|------|
| `coords_to_point(x, y)` | 数学坐标 → 屏幕坐标转换 |
| `point_to_coords(point)` | 屏幕坐标 → 数学坐标转换 |
| `get_graph(func, color=BLUE, **kwargs)` | 绘制函数图像（传入lambda函数） |
| `get_riemann_rectangles(graph, dx=0.1, ...)` | 生成黎曼和矩形 |
| `input_to_graph_point(x, graph)` | 获取函数图像上x对应的点 |
| `get_secant_slope_group(x, dx, graph, ...)` | 获取割线斜率组（用于导数讲解） |

使用示例（微积分本质中常见的模式）：

```python
# ⚠️ 老版本写法（GraphScene+CONFIG字典），现代Manim使用Axes类
class PlotFunction(GraphScene):
    CONFIG = {
        "x_min": -3,
        "x_max": 3,
        "y_min": -2,
        "y_max": 10,
        "graph_origin": UP + LEFT,
        "x_labeled_nums": range(-3, 4),
        "y_labeled_nums": range(0, 11, 2),
    }
    
    def construct(self):
        self.setup_axes()
        # 绘制 f(x) = x²
        graph = self.get_graph(lambda x: x**2, color=BLUE)
        self.play(ShowCreation(graph))  # 老版本动画名
        self.wait()
        
        # 绘制黎曼和矩形
        rects = self.get_riemann_rectangles(graph, dx=0.5)
        self.play(ShowCreation(rects))
        self.wait()
```

## ReconfigurableScene：配置切换场景（标注已不工作）

ReconfigurableScene 位于 `once_useful_constructs/reconfigurable_scene.py`，文档注释标注"Note, this seems to no longer work as intended"（已不能按预期工作），但在微积分本质等历史视频中被用于演示参数变化效果（F-039、F-075）。

### 设计意图：同一场景的不同配置过渡

ReconfigurableScene 的核心方法 `transition_to_alt_config(**kwargs)` 可以在运行时切换场景的配置参数，并用 Transform 动画平滑过渡——比如演示"当 dr 从大变小，黎曼和矩形越来越密趋近于真实面积"的效果（F-040）：

```python
# once_useful_constructs/reconfigurable_scene.py:19-56（简化）
def transition_to_alt_config(self, **kwargs):
    # 1. 创建同一场景类的新实例，skip_animations=True
    #    这样新实例会完成所有构造但不播放动画
    alt_scene = self.__class__(skip_animations=True, **kwargs)
    
    # 2. 将alt_scene中的所有mobject拷贝过来
    alt_mobjects = alt_scene.mobjects
    
    # 3. 用Transform平滑过渡到新配置下的状态
    anims = []
    for old, new in zip(self.mobjects, alt_mobjects):
        anims.append(Transform(old, new))
    self.play(*anims)
```

**注意**：这个类依赖 Manim 老版本的内部机制，在新版 ManimGL 中可能无法正常工作。如果需要类似功能，建议自己实现：手动创建两组状态的 mobject，用 Transform 做过渡动画即可，不需要依赖这个基类。

## 其他历史场景基类

`once_useful_constructs/` 目录中还包含约 20 个其他历史场景基类，覆盖各类数学可视化场景（F-062、F-076）：

| 基类文件 | 用途 | 注意事项 |
|---------|------|---------|
| `linear_algebra.py` | 线性代数可视化（向量、矩阵、变换） | eola系列使用 |
| `complex_transformation_scene.py` | 复平面变换可视化 | 复分析视频使用 |
| `vector_space_scene.py` | 向量空间抽象可视化 | 高维线性代数 |
| `fractals.py` | 分形图形绘制 | 分形主题视频 |
| `combinatorics.py` | 组合数学可视化 | 概率/组合视频 |
| `counting.py` | 计数原理可视化 | 计数主题 |
| `matrix_multiplication.py` | 矩阵乘法动画 | 线性代数系列使用 |
| `sample_space_scene.py` | 概率样本空间可视化 | 概率系列使用 |
| `region.py` | 平面区域可视化 | 积分区域演示 |
| `graph_theory.py` | 图论可视化 | 图论主题 |
| `light.py` | 光学效果 | 物理相关视频 |
| `butterfly_curve.py` | 蝴蝶曲线绘制 | 单集视频使用 |
| `arithmetic.py` | 算术可视化 | 基础算术 |

> **重要提示**：`once_useful_constructs/` 的命名意为"曾经有用的构造"（F-076），其中大部分是为特定历史视频编写的专用组件，设计上没有考虑通用性，且与老版本 Manim API 耦合较深。研读这些组件时重点学习其可视化思路和动画设计，不要直接在新项目中照搬——新版 ManimGL 的 Axes、ThreeDAxes 等内置类已经覆盖了大部分功能，设计更优。

## Scene 继承与组合模式

Videos 仓库中展示了两种场景逻辑复用模式：**继承**（单基类）和**多继承组合**（Mixin 模式）。

### 模式1：单继承（最常用）

简单场景直接继承一个基类，通过重写 `create_pi_creatures()` 和 `construct()` 定制行为：

```python
class MyLesson(PiCreatureScene):
    # 覆盖配置属性
    seconds_to_blink = 4
    
    def create_pi_creatures(self):
        return VGroup(Mortimer().to_corner(DR))
    
    def construct(self):
        # 教学内容...
```

### 模式2：多继承组合功能

复杂场景通过多继承组合多个基类的功能，在 `setup()` 中依次调用各父类的 `setup()`（F-046）：

```python
# eoc/chapter1.py中的实际例子：同时继承CircleScene和ReconfigurableScene
class ApproximateOneRing(CircleScene, ReconfigurableScene):
    def setup(self):
        # 重要：多继承时必须显式调用每个父类的setup()
        CircleScene.setup(self)
        ReconfigurableScene.setup(self)
    
    def construct(self):
        # 同时拥有CircleScene画圆能力和ReconfigurableScene配置切换能力
        ...

# 另一个例子：CircleScene + GraphScene组合
class GraphRectangles(CircleScene, GraphScene):
    def setup(self):
        CircleScene.setup(self)
        GraphScene.setup_axes(self)  # 注意可能需要显式调用特定方法
```

**多继承注意事项**：
1. 必须在 `setup()` 中依次调用各父类的 `setup()`，Python 的 super() 链在多继承时可能不按预期工作
2. 如果不同父类有同名方法，需要明确指定调用哪个父类的方法
3. 优先使用组合而非多继承——如果只是需要某个功能，考虑把功能封装成方法调用而非继承

### 模式3：get_* 方法封装可复用构造

除了继承基类，Videos 代码还大量使用 `get_*` 方法封装可复用的几何构造（F-047）：

```python
class CircleScene(Scene):
    def get_ring(self, radius, color=BLUE):
        """返回一个圆环构造"""
        ring = Circle(radius=radius)
        ring.set_stroke(color, width=3)
        return ring
    
    def get_unwrapped(self, ring, n_segments=100):
        """把圆环"展开"成直线的几何构造"""
        # ...复杂构造逻辑
        return unwrapped_mobject
```

这种模式比继承更轻量：你不需要继承某个类就能使用某个几何构造，只要调用 `get_*` 方法拿到构造好的 VMobject 即可。

## 如何选择合适的基类

| 场景需求 | 推荐基类 |
|---------|---------|
| 纯数学动画，不需要角色 | `Scene` 或 `InteractiveScene` |
| 需要一两个角色做简单互动 | `PiCreatureScene`，重写 `create_pi_creatures()` |
| 老师讲解+学生互动的教室场景 | `TeacherStudentsScene`（开箱即用） |
| 只需要一个 Mortimer 在右下角 | `MortyPiCreatureScene` |
| 需要绘制函数图像/坐标轴 | 现代 ManimGL 用内置 `Axes`；读老代码参考 `GraphScene` |
| 需要演示参数变化的平滑过渡 | 手动用 Transform 实现，避免用 ReconfigurableScene（已损坏） |
| 读历史视频源码 | 根据视频实际使用的基类来 |

## 写自己的自定义 Scene

如果你发现自己在多个视频场景中重复写相似的样板代码，可以考虑提炼成自定义 Scene 基类，步骤如下：

**步骤1：识别重复模式**

先在 2-3 个具体场景中把代码写出来，观察哪些部分是重复的（比如都要创建同样布局的角色、都要设置同样的背景、都要调用某些初始化方法）。

**步骤2：创建基类，封装不变部分**

```python
# my_custom_scenes.py
class MySignatureScene(InteractiveScene):
    # 配置属性作为类属性（新版本写法，不用CONFIG字典）
    background_color = DARK_GREY
    logo_corner = UR
    
    def setup(self):
        super().setup()
        # 自动添加固定元素：Logo、水印等
        self.logo = ImageMobject("my_logo").to_corner(self.logo_corner)
        self.add(self.logo)
    
    # 提供便捷方法
    def add_title(self, text):
        title = TexText(text).scale(1.2).to_edge(UP)
        self.play(Write(title))
        self.title = title
        return title
```

**步骤3：在具体场景中继承使用**

```python
from my_custom_scenes import MySignatureScene

class Episode1(MySignatureScene):
    def construct(self):
        self.add_title("第一集：什么是导数")
        # ... 具体内容
```

**步骤4：不要过度设计**

基类的价值在于"消除实际重复"，不要提前为"未来可能的需求"设计复杂的基类层级——`once_useful_constructs/` 中很多类就是前车之鉴，过度通用化的设计反而随着 API 演进而失效。等重复模式出现 3 次以上再提炼基类是比较稳妥的节奏。

## 相关概念

- [00 Videos 仓库总览](00-videos-overview.md)
- [01 PiCreature 角色系统详解](01-picreature-characters.md)
- [03 视频代码结构与叙事模式](03-video-structure-pattern.md)
- [04 checkpoint_paste 交互式开发工作流](04-checkpoint-paste-workflow.md)
- [自定义模块索引](../references/custom-modules-index.md)
- [代表性系列目录导航](../references/representative-series.md)
