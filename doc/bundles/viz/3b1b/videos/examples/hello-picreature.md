---
type: Example
title: 第一个 PiCreature 场景
description: 学习如何在ManimGL中创建PiCreature角色场景，诚实标注原版PiCreature的API依赖，展示创建角色、切换表情、对话气泡的核心模式，并给出在纯净ManimGL中实现类似效果的简化方案。
tags: [picreature, characters, scene, animation, mode, speech-bubble, manimgl, 3blue1brown]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: Videos 源码事实采集
  - id: concepts-01
    resource: /concepts/01-picreature-characters.md
    title: PiCreature 角色系统详解
  - id: concepts-02
    resource: /concepts/02-custom-scenes.md
    title: 自定义 Scene 基类
  - id: manim-examples-basic-shapes
    resource: /viz/3b1b/manim/examples/basic-shapes.md
    title: ManimGL 基础图形绘制示例
---

# 第一个 PiCreature 场景

> ⚠️ **重要兼容性说明**：本示例中演示的 `PiCreature`、`Randolph`、`Mortimer`、`PiCreatureScene`、`says()`/`thinks()` 等类和方法是 3Blue1Brown 的 `videos` 仓库自定义扩展（位于 `custom/characters/` 目录），**不在标准 ManimGL 库中**（F-012~F-034）。你无法在纯净安装的 ManimGL 中直接 `from manimlib import PiCreature`。
>
> 本示例分为两部分：
> 1. **第一部分**：展示 videos 仓库中原版 PiCreature 的典型使用模式（基于 `from manim_imports_ext import *`），帮助你理解 3B1B 视频源码中的角色写法
> 2. **第二部分**：给出一个在**纯净 ManimGL** 中实现类似"会说话的角色"效果的简化示例，不依赖 videos 仓库自定义代码，可以直接运行

## 第一部分：videos 仓库中的原版 PiCreature 使用模式

以下代码展示 videos 仓库中 PiCreature 场景的典型写法，使用统一入口 `manim_imports_ext`（F-003、F-004）。这段代码需要在完整的 videos 仓库环境中才能运行（需要 `custom/` 目录下的 SVG 资源和自定义类）。

### 完整代码（videos 仓库模式）

```python
# ⚠️ 注意：此代码基于 videos 仓库的老代码模式，需要 custom/ 目录资源
# 需要在 videos 仓库根目录下，使用 from manim_imports_ext import *
from manim_imports_ext import *

class HelloPiCreature(PiCreatureScene):
    def construct(self):
        # 1. 创建角色：默认蓝色 Randolph 放在屏幕中央
        randy = self.pi_creature
        randy.scale(1.5)
        self.add(randy)
        self.wait()

        # 2. 让角色开心地打招呼
        self.play(randy.change_mode, "happy")
        self.wait(0.5)

        # 3. 角色说第一句话（带对话气泡）
        self.play(randy.says("大家好！我是 Randolph！"))
        self.wait(2)

        # 4. 切换到思考表情
        self.play(randy.change_mode, "thinking")
        self.wait(0.5)

        # 5. 角色思考（思考气泡）
        self.play(randy.thinks("让我想想..."))
        self.wait(1.5)

        # 6. 切换回开心表情，说第二句话
        self.play(randy.change_mode, "happy")
        bubbles = randy.bubble
        self.play(
            bubbles.animate.fade(1),
            randy.says("让我们开始学习 Manim 吧！"),
        )
        self.wait(2)

        # 7. 移除气泡，角色挥手告别（示意）
        self.play(BubbleRemove(randy.bubble))
        self.play(randy.change_mode, "plain")
        self.wait()
```

### 代码分段解释

#### 1. 导入与场景基类

```python
from manim_imports_ext import *

class HelloPiCreature(PiCreatureScene):
```

- `from manim_imports_ext import *` 是 videos 仓库所有脚本的标准入口（F-003），它不仅导入 manimlib 核心，还自动导入 `custom/` 下所有扩展模块，包括 PiCreature 及其子类、PiCreatureScene、对话气泡等（F-004）
- `PiCreatureScene` 是所有带 Pi 生物场景的基类（F-027），它继承自 InteractiveScene，自动提供：
  - 默认创建一个 primary pi_creature（`self.pi_creature`）
  - `wait()` 时自动每 3 秒眨眼（F-030）
  - `play()` 时自动让所有 Pi 生物看向第一个动画的 mobject（F-031）

#### 2. 获取默认角色

```python
randy = self.pi_creature
randy.scale(1.5)
self.add(randy)
self.wait()
```

- `PiCreatureScene.setup()` 自动创建一个默认颜色为 BLUE 的 PiCreature（即 Randolph，F-025、F-029），赋值给 `self.pi_creature`
- 因为 PiCreatureScene 默认 `pi_creatures_start_on_screen=True`（F-028），其实 `self.add(randy)` 可以省略——基类已经帮你加了，这里显式写出是为了清晰
- `self.wait()` 在 PiCreatureScene 中会触发自动眨眼，你会看到角色自然眨眼睛

#### 3. 表情切换

```python
self.play(randy.change_mode, "happy")
```

- `change_mode(mode)` 是 PiCreature 的表情切换方法（F-020），它不是简单的图片切换，而是：
  1. 创建一个目标 mode 的新 PiCreature 实例
  2. 匹配样式、高度、眼睛位置
  3. 用 `become()` 实现平滑变形动画
- 常用 mode 包括：`"plain"`（平静）、`"happy"`（开心）、`"speaking"`（说话）、`"thinking"`（思考）、`"surprised"`（惊讶）、`"confused"`（困惑）等

#### 4. 对话与思考气泡

```python
self.play(randy.says("大家好！我是 Randolph！"))
# ...
self.play(randy.thinks("让我想想..."))
```

- `says(content)` 返回 `PiCreatureBubbleIntroduction` 动画（F-024），使用 `SpeechBubble`（尖角指向角色的对话气泡）
- `thinks(content)` 使用 `ThoughtBubble`（多个圆点连接的思考气泡）
- `content` 可以是字符串（自动转为 TexText），也可以是 Tex/TexText 对象
- 气泡在动画结束后保留在屏幕上，可以通过 `randy.bubble` 访问，用 `BubbleRemove` 动画移除

---

## 第二部分：纯净 ManimGL 中的简化角色实现

如果你没有使用 videos 仓库，只是想在自己的 ManimGL 项目中创建一个"会说话、有表情"的简单角色，可以用以下思路实现类似效果。这个示例**完全基于标准 ManimGL API**，可以直接运行。

### 简化版代码（可直接在纯净 ManimGL 运行）

```python
from manimlib import *

class SimpleCharacter(VGroup):
    """一个简化的角色类：圆形身体 + 眼睛 + 嘴巴，支持表情切换和说话气泡"""
    def __init__(self, color=BLUE, **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.body = Circle(radius=1.0, fill_color=color, fill_opacity=1, stroke_width=0)
        self.eyes = VGroup(
            Circle(radius=0.15, fill_color=WHITE, fill_opacity=1, stroke_width=0),
            Circle(radius=0.15, fill_color=WHITE, fill_opacity=1, stroke_width=0),
        )
        self.eyes.arrange(RIGHT, buff=0.3)
        self.eyes.move_to(self.body.get_center() + UP * 0.2)
        self.pupils = VGroup(
            Circle(radius=0.07, fill_color=BLACK, fill_opacity=1, stroke_width=0),
            Circle(radius=0.07, fill_color=BLACK, fill_opacity=1, stroke_width=0),
        )
        for pupil, eye in zip(self.pupils, self.eyes):
            pupil.move_to(eye.get_center())
        self.mouth = VMobject()  # 嘴巴，会根据mode变化
        self.create_mouth("plain")
        self.add(self.body, self.eyes, self.pupils, self.mouth)
        self.current_mode = "plain"

    def create_mouth(self, mode):
        """根据表情创建嘴巴形状"""
        if mode == "plain":
            self.mouth.become(Line(LEFT * 0.2, RIGHT * 0.2, stroke_width=3))
        elif mode == "happy":
            # 微笑：向上弯的弧线
            self.mouth.become(
                Arc(radius=0.25, start_angle=PI * 1.1, angle=PI * 0.8, stroke_width=3)
            )
        elif mode == "surprised":
            # 惊讶：圆形嘴巴
            self.mouth.become(
                Circle(radius=0.1, fill_color=BLACK, fill_opacity=1, stroke_width=0)
            )
        elif mode == "thinking":
            # 思考：横线偏右
            self.mouth.become(
                Line(LEFT * 0.05, RIGHT * 0.25, stroke_width=3).shift(DOWN * 0.35 + RIGHT * 0.1)
            )
        self.mouth.move_to(self.body.get_center() + DOWN * 0.3)

    def change_mode(self, mode):
        """切换表情的动画"""
        self.current_mode = mode
        new_mouth = VMobject()
        if mode == "plain":
            new_mouth.become(Line(LEFT * 0.2, RIGHT * 0.2, stroke_width=3))
        elif mode == "happy":
            new_mouth.become(
                Arc(radius=0.25, start_angle=PI * 1.1, angle=PI * 0.8, stroke_width=3)
            )
        elif mode == "surprised":
            new_mouth.become(
                Circle(radius=0.1, fill_color=BLACK, fill_opacity=1, stroke_width=0)
            )
        elif mode == "thinking":
            new_mouth.become(
                Line(LEFT * 0.05, RIGHT * 0.25, stroke_width=3).shift(DOWN * 0.35 + RIGHT * 0.1)
            )
        new_mouth.move_to(self.body.get_center() + DOWN * 0.3)
        return Transform(self.mouth, new_mouth)

    def says(self, text):
        """简单的说话气泡（在角色上方显示文字）"""
        bubble = RoundedRectangle(
            width=3, height=0.8, corner_radius=0.2,
            fill_color=WHITE, fill_opacity=0.95, stroke_width=2, stroke_color=GREY
        )
        bubble.next_to(self, UP, buff=0.5)
        text_mob = TexText(text, color=BLACK)
        text_mob.move_to(bubble.get_center())
        # 小尖角指向角色
        pointer = Triangle(fill_color=WHITE, fill_opacity=0.95, stroke_width=0)
        pointer.scale(0.15)
        pointer.rotate(PI)
        pointer.next_to(bubble, DOWN, buff=-0.1)
        bubble_group = VGroup(bubble, text_mob, pointer)
        return FadeIn(bubble_group, shift=DOWN * 0.3), bubble_group


class HelloSimpleCharacter(Scene):
    def construct(self):
        # 1. 创建简化角色放在中央
        char = SimpleCharacter(color=BLUE_D)
        char.scale(1.2)
        self.play(FadeIn(char, scale=0.5))
        self.wait()

        # 2. 开心打招呼
        self.play(char.change_mode("happy"))
        self.wait(0.5)

        # 3. 说话气泡
        bubble_anim, bubble = char.says("你好！Manim！")
        self.play(bubble_anim)
        self.wait(2)

        # 4. 切换到惊讶表情
        self.play(
            FadeOut(bubble),
            char.change_mode("surprised"),
        )
        self.wait(0.8)

        # 5. 思考
        self.play(char.change_mode("thinking"))
        bubble_anim2, bubble2 = char.says("这很有趣...")
        self.play(bubble_anim2)
        self.wait(2)

        # 6. 回到开心
        self.play(
            FadeOut(bubble2),
            char.change_mode("happy"),
        )
        self.wait(2)
```

### 简化版代码说明

- `SimpleCharacter` 继承自 VGroup（而非 SVGMobject），用纯代码绘制身体（圆形）、眼睛、嘴巴，不依赖外部 SVG 资源
- `change_mode()` 通过 Transform 动画在不同嘴巴形状之间过渡，模拟原版 PiCreature 的表情切换效果
- `says()` 返回 FadeIn 动画和气泡 VGroup，用简单的 RoundedRectangle + Triangle 模拟对话气泡
- 这个示例展示了 PiCreature 模式的核心思想：**角色是一个可以改变状态（mode）的复合 Mobject**，通过改变子部件形状实现表情变化，配合气泡动画实现"说话"效果

### 如何移植原版 PiCreature

如果你想在自己的项目中使用完整的原版 PiCreature：
1. 从 videos 仓库复制以下文件/目录到你的项目：
   - `custom/characters/pi_creature.py`
   - `custom/characters/pi_creature_animations.py`
   - `custom/characters/pi_creature_scene.py`
   - `custom/drawings.py`（气泡依赖）
   - `assets/pi_creature_images/`（SVG 资源目录）
2. 创建自己的 `my_imports.py`，类似 `manim_imports_ext.py` 统一导入
3. 注意老代码使用的 `CONFIG` 字典风格需要适配新版本 ManimGL 的类属性风格

## 运行说明

### videos 仓库原版代码

在 videos 仓库根目录下运行：

```bash
# 低分辨率预览
manimgl examples/hello_picreature.py HelloPiCreature -p

# 渲染为视频文件
manimgl examples/hello_picreature.py HelloPiCreature -w
```

### 纯净 ManimGL 简化版

将简化版代码保存为 `hello_simple_char.py`，直接运行：

```bash
manimgl hello_simple_char.py HelloSimpleCharacter
```

## 预期效果

### 原版 PiCreature 效果

运行后你将看到：
1. 蓝色的 Pi 生物出现在屏幕中央，**自然地眨眼睛**（PiCreatureScene 自动处理）
2. 表情平滑地从平静切换到开心，嘴巴变成微笑弧线
3. 角色上方出现白色对话气泡，尖角指向角色，显示文字"大家好！我是 Randolph！"
4. 表情切换到思考状，眼睛略微看向一侧，气泡变为思考气泡样式
5. 气泡淡出，新的对话气泡出现显示第二句话
6. 气泡移除，角色回到平静表情

整个过程中角色会自然眨眼，眼神会跟随动画中的 mobject 移动（视线自动追踪）。

### 简化版效果

运行后你将看到：
1. 蓝色圆形角色（带眼睛和嘴巴）从中心淡入放大
2. 嘴巴从直线变成向上弯的微笑弧线
3. 角色上方出现白色圆角矩形气泡，带小尖角，显示"你好！Manim！"
4. 气泡淡出，嘴巴变成圆形（惊讶表情）
5. 嘴巴变成思考状的横线，新气泡显示"这很有趣..."
6. 气泡淡出，回到开心表情

虽然视觉上比原版简单，但完整展示了"角色创建→表情切换→说话气泡"的核心交互模式。

## 与原版 PiCreature 的关键差异

| 特性 | 原版 PiCreature (videos仓库) | 简化版实现 | 说明 |
|------|-----------------------------|-----------|------|
| **身体形态** | 基于外部 SVG 文件（π形） | 代码绘制圆形 | 原版通过 SVGMobject 加载专业设计的角色SVG |
| **眼睛重绘** | 用Circle独立重绘眼睛（F-018） | 简单Circle眼睛 | 原版重绘眼睛是为了保证不同表情眼睛位置一致，支持平滑视线追踪 |
| **表情切换** | `become()`新实例+眼睛对齐（F-020） | Transform嘴巴 | 原版是整个身体平滑变形，简化版只变形嘴巴 |
| **视线追踪** | `look()`/`look_at()` 移动瞳孔（F-021） | 无 | 原版瞳孔可以在虹膜内独立移动，实现眼睛看向不同方向 |
| **自动眨眼** | PiCreatureScene 重写 wait() 每3秒眨眼（F-030） | 无 | 自动眨眼是让角色"活"起来的关键微动作 |
| **自动视线跟随** | PiCreatureScene 重写 play() 自动看向动画目标（F-031） | 无 | 场景层面的自动化，不需要手动调用look_at |
| **气泡样式** | SpeechBubble/ThoughtBubble 专业样式 | 简单RoundedRectangle | 原版气泡有自动调整宽度、尾巴位置等智能逻辑 |
| **身体平滑度** | `insert_n_curves(100)` 插入曲线点（F-019） | 无 | 插入额外顶点让不同mode间变换更平滑，避免变形抖动 |

> 💡 **学习建议**：如果你只是想快速做数学动画，不需要 PiCreature——直接用几何图形和公式就够了。如果你想做带角色讲解风格的视频，建议完整复制 videos 仓库的 custom/characters/ 模块使用，或者基于上述简化思路打造自己的角色系统。

## 相关概念

- [01 PiCreature 角色系统详解](/concepts/01-picreature-characters.md) — PiCreature类结构、mode表情状态机、视线追踪、眨眼机制、says/thinks对话气泡
- [02 自定义 Scene 基类](/concepts/02-custom-scenes.md) — PiCreatureScene自动眨眼与视线追踪、TeacherStudentsScene教室场景
- [ManimGL：基础图形绘制](/viz/3b1b/manim/examples/basic-shapes.md) — VGroup组合、颜色填充描边、arrange布局等ManimGL基础用法
