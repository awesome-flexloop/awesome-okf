---
type: Concept
title: PiCreature 角色系统详解
description: PiCreature 是 3Blue1Brown 视频中的标志性π形角色，不是简单SVG图形而是具备表情切换、视线追踪、自然眨眼、对话气泡的完整角色系统，让动画中的角色具备"生命感"。
tags: [picreature, characters, animation, svg, emotion, eye-tracking, pi-creature]
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

# PiCreature 角色系统详解

PiCreature（π生物）是 3Blue1Brown 视频中最具辨识度的标志性元素——那个圆圆的、有两只大眼睛、会做各种表情的π形小人。直觉上你可能以为它只是"几个不同表情的SVG切换显示"，但实际上 PiCreature 是一个经过精心设计的完整角色系统（洞察 I-02）：它有 mode（表情状态机）实现表情切换、独立重绘的眼睛实现视线追踪、自动眨眼机制让角色看起来"活"着、对话/思考气泡实现角色交互，再加上 PiCreatureScene 基类在场景层面提供自动视线跟随和批量眨眼功能。这些"看不见的细节"才是让 Pi 生物看起来有生命感的关键。

## PiCreature 类基础结构

PiCreature 类定义在 `custom/characters/pi_creature.py` 中，它不是直接继承自 VMobject，而是继承自 SVGMobject（F-014），基于外部 SVG 文件加载角色形态，然后在代码中重构部件结构、重绘眼睛、添加交互逻辑。

### SVG 部件索引常量

PiCreature 定义了6个常量标识 SVG 中的不同部件索引（F-013）：

```python
# custom/characters/pi_creature.py:33-38
LEFT_EYE_INDEX = 0
RIGHT_EYE_INDEX = 1
LEFT_PUPIL_INDEX = 2
RIGHT_PUPIL_INDEX = 3
BODY_INDEX = 4
MOUTH_INDEX = 5
```

这些索引对应 SVG 文件中的子路径顺序，但 PiCreature 并不直接使用 Figma 导出的原始 submobjects，而是通过 `init_structure()` 方法手动重构（F-017）。

### 类属性与默认参数

PiCreature 定义了一系列类属性控制角色外观和行为（F-012、F-015）：

```python
# custom/characters/pi_creature.py:31,43-46
PI_CREATURE_SCALE_FACTOR = 0.5  # 默认缩放因子

class PiCreature(SVGMobject):
    right_arm_range = (0.55, 0.7)       # 右手臂在身体路径上的区间
    left_arm_range = (0.34, 0.462)      # 左手臂在身体路径上的区间
    pupil_to_eye_width_ratio = 0.4      # 瞳孔与眼睛的宽度比例
    pupil_dot_to_pupil_width_ratio = 0.3  # 瞳孔光点与瞳孔的宽度比例
```

初始化时接受 `mode` 参数（默认 `"plain"`），通过 mode 名称从 `pi_creature_images` 目录加载对应表情的 SVG 文件（F-016）。

### 初始化核心流程

`__init__` 方法执行以下关键步骤（F-016~F-019）：

```python
# ⚠️ 老版本写法（CONFIG字典风格，新版本使用__init__参数）
class PiCreature(SVGMobject):
    CONFIG = {
        "color": BLUE,
        "flipped": False,
        "start_mode": "plain",
    }
    
    def __init__(self, mode="plain", **kwargs):
        # 1. 根据mode名称加载对应SVG文件
        self.mode = mode
        svg_file = self.get_svg_file(mode)  # 从pi_creature_images目录加载
        super().__init__(svg_file, **kwargs)
        
        # 2. 为身体插入100个额外曲线点，让不同mode间变换更平滑
        self.body.insert_n_curves(100)  # F-019
        
        # 3. 重构SVG结构，手动提取eyes/body/mouth
        self.init_structure()  # F-017
        
        # 4. 用Circle重新绘制眼睛（不使用SVG原始路径）
        self.draw_eyes()  # F-018
        
        # 5. 处理翻转
        if self.flipped:
            self.flip()
```

两个关键设计细节值得注意：
1. **`body.insert_n_curves(100)`**：为身体路径插入100个额外的曲线点（F-019），这使得不同表情模式之间的形态变换（如从 plain 切换到 happy）动画更加平滑，不会出现顶点数不匹配导致的变形抖动
2. **`init_structure()` 手动重构**：不直接使用 SVG 导出的原始 submobjects 结构，而是手动按索引提取 eyes、body、mouth 三个核心部件（F-017），解决不同表情 SVG 文件结构不一致的问题

## 眼睛独立重绘逻辑

PiCreature 的眼睛设计是整个角色系统最精妙的部分之一——它不使用 SVG 文件中预定义的眼睛路径，而是在 `draw_eyes()` 方法中用 Circle 完全重新绘制（F-018）。

为什么要"舍近求远"重绘眼睛？因为不同表情的 SVG 文件中眼睛的位置、大小、路径形状可能不一致，如果直接使用 SVG 原始路径，切换表情时眼睛会出现"跳变"，无法实现平滑的视线追踪动画。用代码统一绘制眼睛保证了：
- 所有表情的眼睛位置和大小完全一致
- 瞳孔可以独立移动实现视线追踪
- 眨眼动画可以通过简单的坐标变换实现

`draw_eyes()` 方法结构（F-018）：

```python
# custom/characters/pi_creature.py:109-131（简化逻辑）
def draw_eyes(self):
    # 1. 获取左右眼的参考位置（从原始SVG的眼睛位置提取锚点）
    left_eye = self.submobjects[LEFT_EYE_INDEX]
    right_eye = self.submobjects[RIGHT_EYE_INDEX]
    
    # 2. 删除原始SVG眼睛，替换为代码绘制的眼睛
    # 3. 用Circle绘制眼白、瞳孔、瞳孔光点
    #    - pupil_to_eye_width_ratio = 0.4 控制瞳孔大小
    #    - pupil_dot_to_pupil_width_ratio = 0.3 控制光点大小
    # 4. 将新眼睛部件赋值给 self.left_eye / self.right_eye 等属性
```

## mode 表情状态机

PiCreature 通过 `mode` 参数控制当前表情状态，每个 mode 对应一个独立的 SVG 文件，存储了该表情下的身体和嘴巴形态。mode 切换通过 `change_mode()` 方法实现平滑过渡动画（F-020）。

### 常用表情模式

PiCreature 支持多种表情 mode，常用的包括：
- `"plain"`：默认平静表情
- `"happy"`：开心微笑
- `"speaking"`：说话中（嘴巴微张）
- `"thinking"`：思考状
- `"surprised"`：惊讶
- `"sad"`：难过
- `"confused"`：困惑
- `"erm"`：犹豫/沉吟
- `"sassy"`：傲娇/俏皮

### change_mode() 实现原理

`change_mode(mode)` 不是简单的图片切换，而是通过创建新实例+形态对齐+become()实现平滑变形（F-020）：

```python
# custom/characters/pi_creature.py:147-158（简化逻辑）
def change_mode(self, mode):
    # 1. 创建一个目标mode的新PiCreature实例
    new_self = self.__class__(mode=mode)
    new_self.match_style(self)       # 匹配颜色、样式
    new_self.match_height(self)      # 匹配大小
    # 2. 对齐眼睛位置（关键：保证眼睛在切换时不跳变）
    new_self.look_at(self.eyes.get_center())
    # 3. 对齐位置
    new_self.move_to(self)
    if self.flipped:
        new_self.flip()
    # 4. 用become()将当前对象变形为新对象
    self.become(new_self)
    return self
```

使用示例：

```python
# 创建一个默认plain表情的PiCreature
pi = Randolph()
self.add(pi)
self.wait()

# 切换到开心表情（带平滑变形动画）
self.play(pi.change_mode, "happy")
self.wait()

# 切换到思考表情
self.play(pi.change_mode, "thinking")
self.wait()
```

## 视线追踪：look() 与 look_at()

PiCreature 支持眼睛看向指定方向或目标对象，这是让角色"活"起来的关键微动作之一。视线追踪通过移动瞳孔位置实现（F-021、F-022）。

### look(direction)：看向指定方向

`look(direction)` 方法接受一个方向向量，计算瞳孔应该移动到的位置，瞳孔移动范围被限制在虹膜内（F-021）：

```python
# custom/characters/pi_creature.py:163-177（简化逻辑）
def look(self, direction):
    # 1. 归一化方向向量
    direction = direction / np.linalg.norm(direction)
    # 2. 计算瞳孔最大移动距离（不能移出虹膜）
    #    v_norm - 0.75 * pupil_radius
    # 3. 移动左右瞳孔到目标位置
    for eye, pupil in [(self.left_eye, self.left_pupil),
                       (self.right_eye, self.right_pupil)]:
        pupil.move_to(eye.get_center())
        pupil.shift(direction * max_distance)
    return self
```

### look_at(point_or_mobject)：看向指定目标

`look_at()` 是更便捷的高层方法，接受一个坐标点或 Mobject 对象，自动计算从眼睛到目标的方向向量并调用 `look()`（F-022）：

```python
# custom/characters/pi_creature.py:179-185
def look_at(self, point_or_mobject):
    if isinstance(point_or_mobject, Mobject):
        point = point_or_mobject.get_center()
    else:
        point = point_or_mobject
    self.look(point - self.eyes.get_center())
    return self
```

使用示例：

```python
pi = Mortimer()
self.add(pi)

# 创建一个移动的圆形目标
dot = Dot().shift(RIGHT * 3)
self.add(dot)

# 让Pi生物看向dot
pi.look_at(dot)
self.wait()

# 让视线跟随dot移动
self.play(dot.animate.shift(UP * 2),
          UpdateFromFunc(pi, lambda m: m.look_at(dot)))
self.wait()
```

## 眨眼机制：blink()

PiCreature 通过 `blink()` 方法实现眨眼效果——不是切换图片，而是通过将眼睛所有点的 y 坐标压到眼睛底部，把眼睛"压扁"成一条线（F-023）：

```python
# custom/characters/pi_creature.py:198-207（简化逻辑）
def blink(self):
    # 保存眼睛当前状态
    # 对眼睛的所有点应用变换：y坐标映射到眼睛底部
    eyes = VGroup(self.left_eye, self.right_eye)
    bottom_y = eyes.get_bottom()[1]
    def squish(points):
        points[:, 1] = bottom_y  # 所有点压到底部
        return points
    # 创建眨眼动画：压扁 -> 恢复
    self.play(ApplyPointwiseFunction(squish, eyes, run_time=0.1))
    self.wait(0.05)
    self.play(ApplyPointwiseFunction(..., eyes, run_time=0.1))  # 恢复
    return self
```

在实际视频中，你不需要手动调用 `blink()`——PiCreatureScene 基类会自动在 `wait()` 期间每3秒触发一次自然眨眼（详见[02 自定义 Scene 基类](/concepts/02-custom-scenes.md)）。

## 对话与思考气泡：says() / thinks()

PiCreature 提供 `says()` 和 `thinks()` 方法快速创建对话气泡和思考气泡（F-024）：
- `says()`：使用 SpeechBubble（对话气泡，带尖角指向角色）
- `thinks()`：使用 ThoughtBubble（思考气泡，用圆点连接）

```python
# custom/characters/pi_creature.py:253-271
def says(self, content, **kwargs):
    """返回对话气泡引入动画，content可以是字符串或Tex/TexText"""
    return PiCreatureBubbleIntroduction(
        self, content,
        bubble_type=SpeechBubble,
        **kwargs
    )

def thinks(self, content, **kwargs):
    """返回思考气泡引入动画"""
    return PiCreatureBubbleIntroduction(
        self, content,
        bubble_type=ThoughtBubble,
        **kwargs
    )
```

使用示例：

```python
teacher = Mortimer().to_corner(DR)
self.add(teacher)

# 老师说一句话
self.play(teacher.says("今天我们来学习微积分"))
self.wait(2)

# 气泡会在动画结束后自动移除，或者可以手动清理
self.play(BubbleRemove(teacher.bubble))
```

## PiCreature 预定义子类

PiCreature 有四个预定义子类，对应视频中常见的角色形象（F-025、F-066、F-067）：

| 子类 | 颜色 | 特征 | 典型用途 |
|------|------|------|---------|
| **Randolph** | BLUE（蓝色） | 默认 Pi 生物，无特殊修改 | 普通角色、学生（F-025） |
| **Mortimer** | GREY_BROWN（灰棕色） | 默认翻转（flipped=True），默认放在右下角 | 教师角色、主持人（F-025） |
| **Mathematician** | GREY（灰色） | 朴素灰色外观 | 数学家角色（F-025） |
| **BabyPiCreature** | 同默认 | 高度1.5倍，大眼睛比例 | 婴儿/小学员角色（F-025） |
| **TauCreature** | 自定义 | 从 `vector_images` 目录而非 `pi_creature_images` 加载SVG，文件前缀为"TauCreatures_" | Tau 相关主题（F-067） |
| **MortyPiCreatureScene** | - | 是 Scene 子类而非 PiCreature 子类，默认使用 Mortimer、翻转、右下角 | Mortimer 专属场景基类（F-066） |

子类实现示例：

```python
# custom/characters/pi_creature.py:299-337（简化）
class Randolph(PiCreature):
    pass  # 就是PiCreature的别名，蓝色默认

class Mortimer(PiCreature):
    CONFIG = {
        "color": GREY_BROWN,
        "flip_at_start": True,  # 默认翻转朝向左边
    }

class Mathematician(PiCreature):
    CONFIG = {
        "color": GREY,
    }

class BabyPiCreature(PiCreature):
    CONFIG = {
        "scale_factor": 1.5,  # 更大尺寸
        "pupil_to_eye_width_ratio": 0.5,  # 更大的眼睛
    }
```

## 独立 Eyes 类：为任意对象添加眼睛

PiCreature 还提供了一个独立的 `Eyes` 类（F-026），可以为任何非 PiCreature 的 VMobject 添加眼睛部件——比如让几何图形、坐标轴、甚至公式"长眼睛"看向观众。

Eyes 内部实现很巧妙：它创建一个临时的 PiCreature 实例，提取出眼睛部分，然后把眼睛"安装"到目标对象上（F-026）：

```python
# custom/characters/pi_creature.py:368-405（简化逻辑）
class Eyes(VGroup):
    def __init__(self, mobject, **kwargs):
        # 1. 创建一个临时PiCreature来"借用"眼睛
        dummy = PiCreature()
        # 2. 提取眼睛部分
        eyes = VGroup(dummy.left_eye, dummy.right_eye).copy()
        # 3. 根据目标mobject的大小调整眼睛大小和位置
        # 4. 把眼睛放到目标mobject上方
        super().__init__(eyes, **kwargs)
        self.look_at = lambda point: ...  # 同样支持look_at视线追踪
```

使用示例：

```python
# 让一个圆形"活"起来
circle = Circle(fill_color=BLUE, fill_opacity=0.5)
eyes = Eyes(circle)
self.add(circle, eyes)
eyes.look_at(UP + RIGHT)
self.wait()
```

## 手臂动画：get_arm_copies()

PiCreature 还支持手臂动画效果，通过 `get_arm_copies()` 方法从身体路径中提取手臂部分的副本（F-068）：

```python
# custom/characters/pi_creature.py:230-235
def get_arm_copies(self):
    # 通过pointwise_become_partial()从身体路径中提取
    # right_arm_range=(0.55, 0.7)和left_arm_range=(0.34, 0.462)
    # 定义的区间，复制出手臂形状
    body = self.body
    return VGroup(
        body.copy().pointwise_become_partial(body, *self.right_arm_range),
        body.copy().pointwise_become_partial(body, *self.left_arm_range),
    )
```

这个方法可以用于实现挥手、指向等手势动画——复制出手臂路径，然后对手臂应用旋转或位移动画即可。

## 如何在自己的视频中使用 PiCreature

使用 PiCreature 的最简步骤：

**步骤1：使用统一导入入口**

```python
from manim_imports_ext import *  # 自动导入PiCreature及所有子类
```

**步骤2：创建角色并添加到场景**

```python
class MyPiScene(Scene):
    def construct(self):
        # 创建一个Mortimer教师放在右下角
        teacher = Mortimer().to_corner(DR)
        self.add(teacher)
        
        # 创建三个学生放在左下角
        students = VGroup(Randolph(color=BLUE_D),
                         Randolph(color=BLUE_E),
                         Randolph(color=BLUE_C))
        students.arrange(RIGHT).to_corner(DL)
        self.add(students)
```

**步骤3：使用对话和表情**

```python
        # 老师说话
        self.play(teacher.says("大家好！"))
        self.wait(2)
        
        # 切换表情
        self.play(teacher.change_mode, "happy")
        self.wait()
```

**提示**：对于需要频繁使用 Pi 生物的场景，建议直接继承 PiCreatureScene 或 TeacherStudentsScene 基类，它们会自动处理眨眼、视线追踪等功能（详见[02 自定义 Scene 基类](/concepts/02-custom-scenes.md)）。

## 相关概念

- [00 Videos 仓库总览](/concepts/00-videos-overview.md)
- [02 自定义 Scene 基类](/concepts/02-custom-scenes.md)（PiCreatureScene 自动眨眼与视线追踪）
- [03 视频代码结构与叙事模式](/concepts/03-video-structure-pattern.md)
- [自定义模块索引](/references/custom-modules-index.md)
