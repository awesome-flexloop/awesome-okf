---
type: Concept
title: Videos 仓库总览与入门
description: Videos 仓库是 3Blue1Brown 2015-2018 年所有数学动画视频的源码集合，基于 Manim 早期版本构建，包含 PiCreature 角色系统、自定义场景基类和按年份组织的完整视频项目源码。
tags: [videos, overview, getting-started, manim, 3blue1brown, repository-structure]
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

# Videos 仓库总览与入门

> ⚠️ **重要版本说明**：本知识包基于3Blue1Brown 2015-2018年视频源码，代码使用的是Manim早期版本API（CONFIG字典、OldTex、ShowCreation等），与当前ManimGL有差异。建议先学习[ManimGL知识包](/viz/3b1b/manim/index.md)掌握当前API后，再回来研读videos仓库学习叙事设计和动画技巧。

**Videos 仓库**不是一个独立的框架或库，而是 Grant Sanderson（3Blue1Brown）过去11年制作数学科普动画视频的全部源码资产集合（F-001）。从2015年的最早视频到2026年的最新作品，这里沉淀了 PiCreature（π生物）角色系统、可复用场景基类、以及每一期视频的完整实现代码。它的核心价值不在于"如何调用 Manim API"，而在于"如何用代码讲好一个数学故事"——包括叙事节奏编排、角色动画设计、交互式开发工作流等经过上百个视频实战验证的制作经验。

与 ManimGL 知识包聚焦"引擎本身怎么用"不同，本知识包聚焦"用引擎做视频"的实战方法论：你将看到 3Blue1Brown 如何把一个抽象的数学概念拆分成镜头、如何让 Pi 生物看起来有"生命感"、如何通过交互式工作流快速迭代动画效果。

## Videos 仓库是什么

Videos 仓库与 Manim 引擎（manimlib）的关系是"内容生产层"与"渲染引擎层"的关系（F-004）：

- **Manim（manimlib）**：底层渲染引擎，提供 Mobject（数学对象）、Animation（动画）、Scene（场景）、Camera（相机）等基础抽象
- **Videos 仓库**：在 Manim 之上构建的内容资产层，包含：
  - 3Blue1Brown 专属的角色系统（PiCreature）
  - 视频制作中沉淀的可复用场景基类（PiCreatureScene、TeacherStudentsScene、GraphScene 等）
  - 按年份组织的每一期视频的完整源码（从线性代数本质、微积分本质到神经网络、傅里叶级数等经典系列）

所有视频脚本都不直接 `from manimlib import *`，而是通过统一入口文件 `manim_imports_ext.py` 导入（F-003），这个文件在 Manim 基础上额外导入了所有自定义扩展模块，保证视频脚本可以开箱即用地使用 PiCreature、自定义动画、历史兼容层等所有资产。

## 目录结构详解

Videos 根目录采用"时间线沉积"式组织，而非按主题分类，这反映了真实内容生产项目的自然演进特征（洞察 I-01）：

```
videos/
├── manim_imports_ext.py    # 统一导入入口（所有脚本第一行都导入这个）
├── custom_config.yml       # 渲染配置（4K分辨率、资源路径等）
├── custom/                 # 🔧 自定义扩展模块（沉淀层）
│   ├── characters/         # PiCreature角色系统
│   ├── backdrops.py        # 背景主题
│   ├── banner.py           # 视频横幅
│   ├── deprecated.py       # 老API兼容包装层
│   ├── drawings.py         # 自定义绘图工具
│   ├── end_screen.py       # 标准片尾组件
│   ├── logo.py             # Logo组件
│   └── opening_quote.py    # 开场白组件
├── once_useful_constructs/  # 📦 历史可复用组件（"曾经有用的构造"）
│   ├── graph_scene.py      # 坐标图场景（标注待废弃）
│   ├── reconfigurable_scene.py  # 配置切换场景（标注已不工作）
│   ├── linear_algebra.py   # 线性代数可视化组件
│   ├── fractals.py         # 分形可视化
│   ├── combinatorics.py    # 组合数学可视化
│   └── *.glsl              # 3个GPU着色器文件
├── _2015/                  # 🎬 2015年视频源码
├── _2016/                  # 🎬 2016年视频（含eola线性代数本质系列）
│   └── eola/               # Essence of Linear Algebra（chapter0~chapter11）
├── _2017/                  # 🎬 2017年视频（含eoc微积分本质、nn神经网络系列）
│   ├── eoc/                # Essence of Calculus（chapter1~chapter10）
│   └── nn/                 # 神经网络系列（含预训练权重）
├── _2018/                  # 🎬 2018年视频（含eop概率系列，开始出现reusables/）
│   └── eop/reusables/      # 概率系列共享组件目录
├── _2019/ ~ _2026/         # 🎬 后续年度视频
├── outside_videos/         # 外部合作内容
└── sublime_custom_commands/ # Sublime Text编辑器集成插件
```

### 核心目录说明

**1. `_YYYY/` 年度视频目录（F-001）**

从 `_2015/` 到 `_2026/`，每一年的视频独立存放。系列视频（如线性代数本质、微积分本质）在对应年度目录下以子目录形式组织，每个章节对应一个 `chapterN.py` 文件（F-005）：
- 线性代数本质（Essence of Linear Algebra, eola）位于 `_2016/eola/`，包含 16 个 Python 文件（chapter0~chapter11 + 补充内容）（F-006）
- 微积分本质（Essence of Calculus, eoc）位于 `_2017/eoc/`，包含 12 个 Python 文件（F-007）
- 独立视频直接以主题命名放在年度目录根下（如 `_2017/bell.py`、`_2018/fourier.py`）（F-008）

**2. `custom/` 自定义扩展模块**

这是跨视频沉淀的通用组件目录，包含角色系统、UI组件、兼容层等。所有 `custom/` 下的模块都会被 `manim_imports_ext.py` 自动导入（F-004），视频脚本可以直接使用。

**3. `once_useful_constructs/` 历史可复用组件（F-076）**

目录名直译为"曾经有用的构造"，这里存放的是早期视频项目中沉淀的场景基类和数学可视化组件。注意这个目录没有 `__init__.py`，通过 Python 路径搜索机制直接导入（F-009）。其中部分组件已被标注为待废弃或不能正常工作（如 GraphScene、ReconfigurableScene），但历史视频代码仍在广泛使用（F-075）。

## `manim_imports_ext.py`：统一导入入口

所有视频脚本的第一行都是：

```python
from manim_imports_ext import *
```

而不是直接从 manimlib 导入。这个入口文件的结构非常简单（F-004）：

```python
# manim_imports_ext.py 完整内容结构
from manimlib import *                     # 第1行：先导入Manim所有内容
from manimlib.mobject.svg.old_tex_mobject import *  # 第2行：导入老版本TeX兼容类

# 第4-14行：依次导入custom子模块的所有内容
from custom.backdrops import *
from custom.banner import *
from custom.characters.pi_creature import *
from custom.characters.pi_creature_animations import *
from custom.characters.pi_creature_scene import *
from custom.deprecated import *            # 老API兼容包装
from custom.drawings import *
from custom.end_screen import *
from custom.filler import *
from custom.logo import *
from custom.opening_quote import *
```

这种设计的好处是：
1. 视频脚本不需要关心模块路径，所有需要的类（PiCreature、各种场景基类、兼容动画类）都直接可用
2. Manim 引擎升级时，只需要在这一个文件里做兼容调整，不需要修改上百个视频脚本
3. 老版本 TeX 和动画类通过 `old_tex_mobject` 和 `custom/deprecated.py` 统一做兼容包装（F-048、F-049）

## 前置学习要求

研读 Videos 仓库之前，建议先完成以下准备：

**1. 掌握 ManimGL 基础 API**

先学习 [ManimGL 知识包](/viz/3b1b/manim/index.md)，理解以下核心概念：
- Scene 基类和 construct() 方法的作用
- Mobject/VMobject 的创建和样式设置
- Animation 和 self.play() 的基本用法
- 现代 ManimGL 的配置方式（直接类属性而非 CONFIG 字典）

**2. 了解 API 版本差异**

Videos 仓库中 2015-2018 年的经典视频使用 Manim 早期 API，写新代码时请使用现代等价写法：

| 老版本写法（Videos 仓库中常见） | 现代 ManimGL 等价写法 |
|-------------------------------|---------------------|
| `CONFIG = { ... }` 类字典配置 | 直接定义类属性 |
| `ShowCreation(mobject)` | `Create(mobject)` |
| `OldTex("公式")` / `OldTexText("文字")` | `Tex("公式")` / `TexText("文字")` |
| `mobject.generate_target()` + `MoveToTarget(mobject)` | `mobject.animate` 语法 |
| `FadeInFromDown(mobject)` | `FadeIn(mobject, UP)` |
| `FadeOutAndShiftDown(mobject)` | `FadeOut(mobject, DOWN)` |

老版本写法示例（**注意：这是老版本写法，新版本使用 `__init__` 参数或直接类属性**）：

```python
# ⚠️ 老版本写法（2015-2018年视频中常见，不建议新代码使用）
class CircleScene(Scene):
    CONFIG = {
        "radius": 2,
        "stroke_color": BLUE,
        "fill_opacity": 0.5,
    }
    def construct(self):
        circle = Circle(radius=self.radius)
        circle.set_stroke(self.stroke_color)
        circle.set_fill(opacity=self.fill_opacity)
        self.play(ShowCreation(circle))  # 老版本动画类名
```

现代等价写法：

```python
# ✅ 现代 ManimGL 写法
class CircleScene(Scene):
    radius = 2
    stroke_color = BLUE
    fill_opacity = 0.5
    
    def construct(self):
        circle = Circle(radius=self.radius)
        circle.set_stroke(self.stroke_color)
        circle.set_fill(opacity=self.fill_opacity)
        self.play(Create(circle))  # 新版本使用Create
```

## 如何运行一个视频

运行视频的方式与 ManimGL 标准方式一致，只是需要在 videos 仓库根目录下执行，确保可以正确导入 `manim_imports_ext.py`。

**基本命令格式：**

```bash
# 预览模式（弹出窗口实时预览）
manimgl _2017/eoc/chapter1.py Introduction

# 渲染输出视频文件（-w 写文件）
manimgl _2017/eoc/chapter1.py Introduction -w

# 低分辨率快速预览（-l 低清，加快渲染速度）
manimgl _2017/eoc/chapter1.py Introduction -l

# 进入交互式开发模式（-se 在指定行进入iPython）
manimgl _2017/eoc/chapter1.py Introduction -se 100
```

**运行经典线性代数系列第一章示例：**

```bash
# 进入videos仓库根目录
cd path/to/videos

# 预览线性代数本质第一章
manimgl _2016/eola/chapter0.py Introduction
```

首次运行时 Manim 会自动编译 LaTeX 公式和缓存 SVG 资源，可能需要等待一段时间。

## 版本兼容性总览

Videos 仓库跨越 11 年（2015-2026），存在多代 API 并存的情况（洞察 I-05、F-073）：

| 演进维度 | 早期版本（2015-2018） | 现代版本（2019+） |
|---------|---------------------|------------------|
| 场景配置 | `CONFIG` 类字典 | 直接类属性 |
| 创建动画 | `ShowCreation` | `Create` |
| TeX 渲染 | `OldTex` / `OldTexText` | `Tex` / `TexText` |
| 属性动画 | `generate_target()` + `MoveToTarget` | `mobject.animate` 语法 |
| 方向淡入淡出 | `FadeInFromDown` / `FadeOutAndShiftDown` | `FadeIn(mobject, direction)` 参数化 |
| 组件组织 | 直接放在年度目录 | 系列内出现 `reusables/` 子目录（F-065） |

这些历史遗留通过 `custom/deprecated.py` 中的兼容包装层统一处理（F-049、F-050），使得历史视频代码无需修改即可在新版 Manim 上运行。研读老代码时重点学习其叙事设计和动画思想，API 写法本身不必照搬。

## 相关概念

- [01 PiCreature 角色系统](/concepts/01-picreature-characters.md)
- [02 自定义 Scene 基类](/concepts/02-custom-scenes.md)
- [03 视频代码结构与叙事模式](/concepts/03-video-structure-pattern.md)
- [04 checkpoint_paste 交互式开发工作流](/concepts/04-checkpoint-paste-workflow.md)
- [自定义模块索引](/references/custom-modules-index.md)
- [代表性系列目录导航](/references/representative-series.md)
- [ManimGL 知识包首页](/viz/3b1b/manim/index.md)
