---
type: Concept
title: 视频Scene代码结构与叙事模式
description: 一个视频=一个Scene子类的编码范式，详解construct()叙事分调、CONFIG配置字典、generate_target动画模式、多继承组合、get_*复用构造等3Blue1Brown视频源码的经典代码结构。
tags: [videos, scene, structure, narrative, construct, config, manim, 3blue1brown]
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

# 视频Scene代码结构与叙事模式

> ⚠️ **重要版本说明**：本文展示的是2015-2018年经典视频的代码模式，包含CONFIG字典、ShowCreation、generate_target()+MoveToTarget、OldTex等老版本API写法，与当前ManimGL存在差异。学习时重点理解**叙事编排思想**而非照搬API写法，新代码请使用现代等价写法。

在3Blue1Brown的Videos仓库中，**一个视频对应一个Scene子类**——这不是简单的代码组织约定，而是一套经过上百个视频验证的叙事编码范式（洞察I-04）。新手最容易犯的错误是把`construct()`写成一个几百行的巨型方法，把所有创建图形、播放动画、等待的代码堆在一起；但在Grant的代码中，`construct()`往往只有短短几行，它不是"画所有图形"的地方，而是**叙事节奏编排器**——按时间顺序调用多个命名清晰的子方法，每个子方法对应视频的一个段落/镜头。本文将系统拆解这套编码模式，包括CONFIG配置、子方法拆分、可复用构造封装、老版本动画模式等。

## 核心范式：一个视频=一个Scene子类

所有视频脚本的第一行都是统一导入（F-041）：

```python
from manim_imports_ext import *
```

系列视频（如微积分本质Essence of Calculus, eoc）还会从其他章节导入需要复用的类：

```python
# 例如 _2017/eoc/chapter1.py 第2行
from _2017.eoc.chapter2 import Car, MoveCar
```

每个独立视频或章节对应一个或多个Scene子类，典型的5分钟视频文件结构如下（F-042、F-043）：

```python
# ⚠️ 老版本写法示例（2015-2018年视频）
class CircleIntroduction(Scene):
    # 1. CONFIG配置字典（老版本，新版本用直接类属性）
    CONFIG = {
        "radius": 2,
        "circle_color": BLUE,
        "fill_opacity": 0.3,
    }
    
    # 2. construct()：叙事编排入口——只有几行，按顺序调用子方法
    def construct(self):
        self.setup_problem()
        self.show_definition()
        self.demonstrate_properties()
        self.introduce_pi()
        self.outro()
    
    # 3. 每个子方法对应一个叙事段落
    def setup_problem(self):
        # 创建开场图形、设置背景
        pass
    
    def show_definition(self):
        # 展示圆的定义、动画演示
        pass
    
    # ...更多子方法...
    
    def outro(self):
        # 片尾、总结
        pass
```

> ✅ **现代ManimGL等价写法**：新版本不再使用`CONFIG = {}`字典，直接定义类属性即可：
> ```python
> class CircleIntroduction(Scene):
>     radius = 2
>     circle_color = BLUE
>     fill_opacity = 0.3
> ```

这种结构的核心思想是：**读construct()就像看视频分镜脚本**——你不需要知道每个段落的具体实现细节，只看方法名和调用顺序就能理解整个视频的叙事流程（洞察I-04）。

## CONFIG类配置字典（老版本）

2015-2018年的经典视频大量使用`CONFIG`类字典配置场景参数（F-042），这是Manim早期版本的配置方式。在老版本中，Manim会自动将CONFIG字典中的键值对设置为实例属性，你可以通过`self.xxx`访问。

**老版本CONFIG写法示例**（来自eoc/chapter1.py的CircleScene）：

```python
# ⚠️ 老版本写法，不建议新代码使用
class CircleScene(Scene):
    CONFIG = {
        "R": 2,
        "stroke_color": BLUE,
        "fill_color": BLUE_D,
        "fill_opacity": 0.0,
        "theta_label_color": MAROON_B,
        "radial_line_color": YELLOW,
    }
    
    def construct(self):
        circle = Circle(radius=self.R)  # 通过self.R访问CONFIG中的值
        circle.set_stroke(self.stroke_color)
        circle.set_fill(self.fill_color, self.fill_opacity)
        self.play(ShowCreation(circle))  # 老版本动画类名，新版本用Create
```

**CONFIG模式的特点**：
1. 所有可配置参数集中在类顶部，一目了然
2. 子类可以通过覆盖CONFIG字典继承并修改父类配置
3. 与现在直接定义类属性的效果等价，但字典形式在早期Python版本中更灵活

**版本迁移对照**：

| 老版本CONFIG写法 | 现代ManimGL等价写法 |
|-----------------|-------------------|
| `CONFIG = { "R": 2, "color": BLUE }` | `R = 2`<br>`color = BLUE` |
| `self.R` 访问配置 | `self.R` 直接访问类属性（不变） |
| 子类覆盖CONFIG部分键 | 子类直接重定义对应类属性 |

## construct()的叙事分调子方法

`construct()`是Scene的入口方法，但在3Blue1Brown的代码中，它几乎不包含直接的动画代码——它的唯一职责是**按叙事顺序调用子方法**（F-043）。以微积分本质第一章`Introduction.construct()`为例（F-043）：

```python
# _2017/eoc/chapter1.py 第271-275行
def construct(self):
    self.show_series_title()      # 展示系列标题
    self.show_many_facts()        # 展示多个需要微积分的问题
    self.invent_calculus()        # 引入微积分思想
```

短短三行调用，清晰地勾勒出整个视频的三段式叙事结构。每个子方法内部封装了该段落需要的：
- Mobject（数学对象）创建
- 动画序列（self.play()调用）
- 等待时间（self.wait()）
- PiCreature对话（self.teacher_says()等）
- 相机变换、元素退场等

### 典型的叙事段落拆分

一个标准的5分钟教学视频通常拆分为以下几类子方法：

| 方法类型 | 命名示例 | 职责 |
|---------|---------|------|
| **开场** | `setup()`、`intro()`、`show_title()` | 创建背景、展示标题、设置初始状态 |
| **概念引入** | `introduce_topic()`、`show_problem()` | 提出问题、展示 motivating example |
| **核心演示** | `show_definition()`、`demonstrate_X()` | 多个并列的演示段落，每段讲一个点 |
| **证明/推导** | `prove_theorem()`、`derive_formula()` | 逻辑推导、公式变形动画 |
| **总结过渡** | `summarize()`、`transition_to_next()` | 回顾要点、过渡到下一章 |
| **片尾** | `outro()`、`show_outro()` | 片尾Logo、下期预告 |

### 可复用几何构造：get_*方法模式

场景中需要重复使用或结构复杂的几何构造，通常封装为`get_*`开头的方法，返回构造好的VMobject供动画调用（F-047）：

```python
# _2017/eoc/chapter1.py CircleScene 中的get_*方法示例
def get_ring(self):
    """返回一个圆环图形"""
    ring = Circle(radius=self.R)
    ring.set_stroke(self.stroke_color, width=4)
    return ring

def get_rings(self, n_rings=20):
    """返回n个同心圆环组成的VGroup"""
    rings = VGroup(*[
        Circle(radius=r)
        for r in np.linspace(0, self.R, n_rings)
    ])
    rings.set_stroke(self.stroke_color, width=1)
    return rings

def get_unwrapped_ring(self, ring):
    """将圆环展开为矩形的目标状态（用于动画）"""
    result = ring.copy()
    # ...展开变形的几何计算...
    return result
```

这种模式的好处是：
1. `construct()`和子方法中的动画代码保持简洁，不被几何构造细节淹没
2. 同一个构造可以在多个动画中复用（如get_ring()既可以用于开场，也可以用于面积推导）
3. 几何逻辑和动画逻辑分离，便于独立调试

## generate_target() → MoveToTarget 老版本动画模式

老版本Manim中，实现"从当前状态平滑过渡到目标状态"的标准模式是`generate_target()` + `MoveToTarget()`组合（F-052），这是现代ManimGL中`mobject.animate`语法的前身。

**老版本模式示例**（来自eoc/chapter1.py第524-529行）：

```python
# ⚠️ 老版本写法，新版本用mobject.animate
# 1. 为mobject生成target副本
fg_group.generate_target()

# 2. 修改target的属性（位置、大小、颜色等）
fg_group.target.scale(0.5)
fg_group.target.to_corner(UP + LEFT)
fg_group.target.set_opacity(0.7)

# 3. 播放MoveToTarget动画，从当前状态平滑过渡到target状态
self.play(MoveToTarget(fg_group))
```

**现代ManimGL等价写法**——更简洁的`.animate`语法：

```python
# ✅ 新版本推荐写法
self.play(
    fg_group.animate
    .scale(0.5)
    .to_corner(UP + LEFT)
    .set_opacity(0.7)
)
```

### 为什么老版本用generate_target模式？

在Manim早期，没有链式调用的`.animate`语法，要实现多属性同时变化的平滑动画，必须显式创建一个目标状态副本，修改副本属性，然后用`MoveToTarget`在两个状态间插值。这种模式虽然啰嗦，但思路非常清晰——你能明确看到"初始状态是什么"、"目标状态是什么"、"动画在两个状态间过渡"。

研读老代码时遇到`generate_target()`，自动在脑中替换为`.animate`即可，动画逻辑和设计思想完全一致。

## 特殊场景约定：Thumbnail与OpeningQuote

Videos仓库中有两类约定俗成的特殊Scene子类（F-044、F-045）：

### Thumbnail缩略图场景

类名以`Thumbnail`结尾（如`Eoc1Thumbnail`），只包含静态元素，**无动画逻辑**，专门用于生成视频封面缩略图：

```python
# _2017/eoc/chapter1.py 第5-62行
class Eoc1Thumbnail(Scene):
    def construct(self):
        # 只创建静态图形，没有self.play()动画
        title = TexText("Essence of Calculus, Chapter 1")
        title.scale(1.5)
        title.to_edge(UP)
        
        circle = Circle(radius=2, color=BLUE)
        formula = OldTex(R"\pi r^2")
        formula.scale(2)
        
        self.add(title, circle, formula)
```

Thumbnail场景通常非常短，只做静态排版，因为它不需要动画——只需要渲染一帧作为封面。

### OpeningQuote开场白场景

章节开场白使用`OpeningQuote`基类，通过CONFIG字典配置引用内容、高亮词、作者信息（F-045）：

```python
# _2017/eoc/chapter1.py 第256-269行
class Chapter1OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote": [
            "If I have seen further, it is by",
            "standing on the shoulders of giants."
        ],
        "highlight_words": ["standing on the shoulders of giants"],
        "author": "Isaac Newton",
        "fade_in_kwargs": {"lag_ratio": 0.5},
    }
```

`OpeningQuote`是Videos仓库custom/中预定义的组件，自动处理排版、字体、淡入动画等，你只需要填内容即可。

## 多继承组合功能

复杂场景经常使用**多继承**来组合多个基类的功能（F-046），例如同时需要圆形场景功能和配置切换功能：

```python
# _2017/eoc/chapter1.py 第699-709行
class ApproximateOneRing(CircleScene, ReconfigurableScene):
    """同时继承CircleScene（圆形几何功能）和ReconfigurableScene（配置切换动画）"""
    CONFIG = {
        "n_rings": 10,
        "ring_width": 0.2,
    }
    
    def setup(self):
        # ⚠️ 多继承时必须手动依次调用各父类的setup()
        CircleScene.setup(self)
        ReconfigurableScene.setup(self)
    
    def construct(self):
        # 可以使用两个父类的所有方法
        self.show_circle()
        self.transition_to_alt_config(n_rings=100)  # 来自ReconfigurableScene
```

另一个例子是图表场景和圆形场景组合：

```python
# 第1001-1021行
class GraphRectangles(CircleScene, GraphScene):
    """圆形几何 + 坐标图功能"""
    def setup(self):
        CircleScene.setup(self)
        GraphScene.setup(self)
```

**多继承注意事项**：
1. `setup()`方法中必须**按顺序手动调用每个父类的setup()**——Python的super()在多继承时不会自动调用所有父类setup（F-046）
2. 注意CONFIG字典的键名冲突，如果两个父类有同名配置键，子类CONFIG中的值会覆盖
3. 优先使用组合而非多继承，只有当两个基类确实是"正交"的独立功能时才用多继承

## 老版本TeX兼容：OldTex与OldTexText

2015-2018年视频使用`OldTex`和`OldTexText`类渲染数学公式和文字（F-048），而不是新版本的`Tex`和`TexText`。这些老版本类在`manim_imports_ext.py`第2行专门从`old_tex_mobject`导入以保持兼容：

```python
# manim_imports_ext.py 第2行
from manimlib.mobject.svg.old_tex_mobject import *
```

**老版本TeX写法**：

```python
# ⚠️ 老版本写法
formula = OldTex(R"A = \pi r^2")
text = OldTexText("The area of a circle")
```

**现代等价写法**：直接用`Tex`和`TexText`即可，新的TeX类在排版质量和性能上都有提升：

```python
# ✅ 新版本写法
formula = Tex(R"A = \pi r^2")
text = TexText("The area of a circle")
```

> 💡 **raw字符串前缀R**：LaTeX公式中大量使用反斜杠（如`\pi`、`\frac`），使用`R"..."`raw字符串可以避免Python转义字符冲突（F-059），这个习惯在新版本中仍然保留。

## 如何组织一个5分钟视频的Scene代码

综合以上模式，一个标准5分钟教学视频的Scene代码组织遵循以下步骤：

**Step 1：先搭叙事骨架**

先只写`construct()`和空子方法，确定视频的段落划分：

```python
class MyVideo(Scene):
    def construct(self):
        self.intro()          # 0:00-0:30 开场
        self.define_concept() # 0:30-1:30 定义概念
        self.show_example()   # 1:30-3:00 例子演示
        self.prove_it()       # 3:00-4:30 证明推导
        self.outro()          # 4:30-5:00 总结片尾
    
    def intro(self): pass
    def define_concept(self): pass
    def show_example(self): pass
    def prove_it(self): pass
    def outro(self): pass
```

运行确认结构没问题，再逐个填充子方法。

**Step 2：逐个填充子方法**

每个子方法内部遵循"创建→动画→等待"的基本节奏，把复杂几何构造抽成`get_*`方法。

**Step 3：用checkpoint_paste交互式调试**

每写完一个子方法，用`manimgl -se`进入交互式模式，边写边看效果（详见[04-checkpoint-paste-workflow](04-checkpoint-paste-workflow.md)）。

**Step 4：添加Thumbnail和OpeningQuote（可选）**

如果是系列视频，在文件开头添加对应的`*Thumbnail`和`*OpeningQuote`类。

## 读视频源码的正确方式

拿到一个陌生的视频源码文件，不要从第一行开始逐行往下读——正确的阅读顺序是（洞察I-04）：

1. **先看`construct()`方法**（通常在类定义后不久）：只看它调用了哪些子方法，了解整个视频的叙事结构，不要深究每个子方法的实现
2. **确定你感兴趣的段落**：找到对应子方法名
3. **阅读该子方法**：理解该段落的动画流程
4. **遇到`get_*`调用时跳转到对应方法**：看几何构造细节
5. **遇到不熟悉的动画类/方法时**：查custom/或once_useful_constructs/，判断是基类方法还是自定义方法

用这种方法，即使是上千行的视频文件，你也能快速定位到自己关心的部分，而不会被细节淹没。

## 老版本动画类兼容一览

老代码中常见的动画类在`custom/deprecated.py`中都有兼容包装（F-049、F-050），遇到时按以下对照表理解即可：

| 老版本动画类 | 现代ManimGL等价写法 |
|-------------|-------------------|
| `ShowCreation(mob)` | `Create(mob)` |
| `FadeInFromDown(mob)` | `FadeIn(mob, UP)` |
| `FadeOutAndShiftDown(mob)` | `FadeOut(mob, DOWN)` |
| `FadeInFromLarge(mob)` | `FadeIn(mob, scale=1/scale_factor)` |
| `GrowFromCenter(mob)` | `GrowFromCenter(mob)`（仍可用） |
| `MoveToTarget(mob)` | `mob.animate`链式语法 |

## 相关概念

- [00 Videos 仓库总览与入门](00-videos-overview.md)
- [01 PiCreature 角色系统详解](01-picreature-characters.md)
- [02 自定义 Scene 基类体系](02-custom-scenes.md)
- [04 checkpoint_paste 交互式开发工作流](04-checkpoint-paste-workflow.md)
- [05 代表性系列项目结构解析](05-series-projects.md)
- [ManimGL 知识包：Scene与动画基础](../../manim/index.md)
