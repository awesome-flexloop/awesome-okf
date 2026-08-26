---
type: Reference
title: Videos 自定义模块索引
description: custom/目录核心模块功能说明、once_useful_constructs历史组件库登记、统一导入路径与版本兼容性标注。
tags: [videos, custom-modules, once-useful-constructs, module-index, compatibility]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26T00:00:00Z" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: Videos 源码事实采集
  - id: self
    resource: /references/custom-modules-index.md
    title: Videos 自定义模块索引
---

# Videos 自定义模块索引

本文档登记 3Blue1Brown videos 仓库中 `custom/` 自定义扩展模块与 `once_useful_constructs/` 历史组件库的组织方式、模块功能与版本兼容性说明。

## custom/ 目录整体说明

`custom/` 目录是 videos 仓库的核心扩展层，存放从历年视频项目中沉淀出来的可复用组件（F-002、F-061）。与按年份组织的视频脚本目录（`_2015/`~`_2026/`）不同，`custom/` 中的组件是跨项目通用的基础设施：角色系统、背景主题、横幅、片尾、开场白等。

`custom/` 目录下的所有模块通过根目录的 `manim_imports_ext.py` 统一导入（F-003、F-004），视频脚本不需要单独导入每个 custom 子模块——只需要第一行写 `from manim_imports_ext import *` 即可获得所有自定义扩展。

**重要兼容性提示**：`custom/` 目录中的代码跨越 2015-2026 年，存在老 CONFIG 字典风格与新 API 并存的情况（F-073），具体标注见下文各模块说明。

## 主要模块列表及功能

以下模块在 `manim_imports_ext.py` 第4-14行被显式通配导入，是所有视频脚本的标准依赖（F-004）：

| 模块名称 | 文件路径 | 主要功能 | 兼容性标注 | 事实依据 |
|----------|----------|----------|------------|----------|
| PiCreature角色定义 | `custom/characters/pi_creature.py` | PiCreature生物类、mode表情状态机、眼睛追踪、眨眼机制、对话气泡、预定义子类（Randolph/Mortimer/BabyPi/TauCreature） | 基于SVGMobject，使用现代类属性风格，兼容ManimGL | F-012~F-026、F-067、F-068 |
| PiCreature场景基类 | `custom/characters/pi_creature_scene.py` | PiCreatureScene自动眨眼/视线追踪、TeacherStudentsScene师生对话场景、MortyPiCreatureScene教师角色场景、joint_blink错峰眨眼、zoom_in_on_thought_bubble思想放大 | 继承InteractiveScene，setup()方法链式调用父类，兼容ManimGL交互模式 | F-027~F-034、F-066、F-069、F-070 |
| 背景主题 | `custom/backdrops.py` | 视频背景主题样式定义 | 待适配：部分背景样式可能使用老CONFIG字典风格 | F-061 |
| 视频横幅 | `custom/banner.py` | 视频开场横幅Logo动画组件 | 待适配：横幅动画可能使用老API动画类 | F-061 |
| 自定义绘图工具 | `custom/drawings.py` | 各类手绘风格图形、标注工具 | 待适配：绘图组件可能混用老VMobject API | F-061 |
| 标准片尾组件 | `custom/end_screen.py` | 视频标准片尾画面（订阅提示、相关视频推荐等） | 待适配：片尾布局可能使用老位置常量 | F-061 |
| 填充内容 | `custom/filler.py` | 视频过渡填充内容、转场动画 | 待适配：填充动画可能使用老ShowCreation等API | F-061 |
| Logo组件 | `custom/logo.py` | 3Blue1Brown Logo动画组件 | 待适配：Logo动画可能使用老变换API | F-061 |
| 开场白组件 | `custom/opening_quote.py` | OpeningQuote开场白基类，支持配置quote内容、高亮词、作者信息 | 使用CONFIG字典风格（老API），视频脚本中通过类属性CONFIG配置 | F-045、F-061 |
| 废弃API兼容包装 | `custom/deprecated.py` | ShowCreation、GrowFromCenter、FadeInFromDown、FadeOutAndShiftDown、FadeInFromLarge等老动画类的兼容包装 | **纯兼容层**：将老API名包装为新API参数化调用，FadeInFromDown=FadeIn(...,UP)，FadeOutAndShiftDown=FadeOut(...,DOWN) | F-049、F-050 |
| PiCreature动画扩展 | `custom/characters/pi_creature_animations.py` | PiCreature专用动画类（表情切换动画、手臂动画等） | 与pi_creature.py配套，使用现代动画API | F-004 |

## once_useful_constructs/ 历史组件库说明

`once_useful_constructs/` 目录命名直译为"曾经有用的构造"（F-076），存放早期视频项目中沉淀的20个数学场景基类与专用组件（F-062）。目录无 `__init__.py` 文件，依赖Python路径搜索机制直接导入模块（F-009）。

> ⚠️ **重要提示**：该目录中的组件是历史遗留代码，部分已被标注为待废弃或不能正常工作（F-075），仅供研读历史视频源码时参考，不建议在新项目中直接使用。

### 核心场景基类（需特别注意兼容性）

| 模块名称 | 文件路径 | 主要功能 | 兼容性状态 | 事实依据 |
|----------|----------|----------|------------|----------|
| 图表场景基类 | `once_useful_constructs/graph_scene.py` | GraphScene：坐标轴创建、函数图像绘制、黎曼和矩形、坐标点转换 | **标注TODO: should be deprecated**，注释建议用Axes替代；但eoc等经典系列仍大量使用，通过多继承组合功能 | F-035~F-038、F-075 |
| 可重配置场景 | `once_useful_constructs/reconfigurable_scene.py` | ReconfigurableScene：通过创建同场景类新实例+Transform实现配置切换过渡动画（如eoc中dr半径变化演示） | **标注Note: this seems to no longer work as intended**，功能可能已损坏；历史视频通过多继承使用 | F-039~F-040、F-075 |
| 线性代数场景 | `once_useful_constructs/linear_algebra.py` | 线性代数可视化专用基类（向量、矩阵、变换可视化） | 历史组件，基于老版本Mobject API，部分功能可能已被manimlib内置coordinate_systems替代 | F-062 |
| 向量空间场景 | `once_useful_constructs/vector_space_scene.py` | 向量空间可视化基类 | 历史组件，与线性代数场景配套 | F-062 |
| 图论场景 | `once_useful_constructs/graph_theory.py` | 图论可视化基类（节点、边、图算法演示） | 历史组件 | F-062 |
| 矩阵乘法场景 | `once_useful_constructs/matrix_multiplication.py` | 矩阵乘法动画专用基类 | 历史组件 | F-062 |
| 复数变换场景 | `once_useful_constructs/complex_transformation_scene.py` | 复平面变换可视化基类 | 历史组件 | F-062 |
| 分形场景 | `once_useful_constructs/fractals.py` | 分形图形可视化基类 | 历史组件 | F-062 |
| 计数/组合场景 | `once_useful_constructs/counting.py`、`combinatorics.py` | 计数与组合数学可视化基类 | 历史组件 | F-062 |
| 概率/样本空间 | `once_useful_constructs/sample_space_scene.py`、`arithmetic.py` | 概率与样本空间可视化基类 | 历史组件，eop概率系列可能参考其设计 | F-062、F-065 |
| 区域可视化 | `once_useful_constructs/region.py` | 平面区域填充、积分区域可视化 | 历史组件，与GraphScene配套使用 | F-062 |
| 光线/光学场景 | `once_useful_constructs/light.py` | 光学可视化基类 | 历史组件 | F-062 |
| 蝴蝶曲线 | `once_useful_constructs/butterfly_curve.py` | 蝴蝶曲线特殊图形 | 历史组件 | F-062 |

### GPU着色器文件

目录中还包含3个GLSL着色器文件用于GPU加速图形变换（F-063）：
- `map_point_pairs.glsl`：点对映射着色器
- `quadratic_bezier_distance.glsl`：二次贝塞尔距离计算着色器
- `rotate.glsl`：旋转变换着色器

## 模块导入路径

所有视频脚本使用**统一导入入口**，不需要单独导入custom或once_useful_constructs中的模块（F-003、F-004、F-041）：

```python
# 所有视频脚本的标准第一行
from manim_imports_ext import *
```

`manim_imports_ext.py` 的导入顺序（F-004）：
1. 第1行：从 `manimlib` 通配导入所有ManimGL核心API
2. 第2行：导入 `old_tex_mobject`（OldTex/OldTexText老版本TeX兼容）
3. 第4-14行：依次通配导入custom子模块：backdrops、banner、pi_creature、pi_creature_animations、pi_creature_scene、deprecated、drawings、end_screen、filler、logo、opening_quote

`once_useful_constructs/` 中的模块不在统一导入中，需要时按模块名单独导入（F-009）：
```python
# 需要使用历史组件时单独导入
from once_useful_constructs.graph_scene import GraphScene
```

系列视频内部跨章节导入（F-041）：
```python
# 如eoc/chapter1.py中导入chapter2的Car类
from _2017.eoc.chapter2 import Car, MoveCar
```

## 版本兼容性标注

videos仓库代码跨越2015-2026年，存在四组主要API演变（F-073）：

| 老API写法（2015-2018年经典视频） | 新API等价写法 | 兼容处理 | 出现位置 |
|--------------------------------|--------------|----------|----------|
| `class MyScene(Scene): CONFIG = {...}` 字典配置 | 直接定义类属性 `class MyScene(Scene): ...` | deprecated.py不处理，需直接识别CONFIG字典为类属性 | once_useful_constructs/、opening_quote.py、早期视频脚本 |
| `ShowCreation(mobject)` 创建动画 | `Create(mobject)` | custom/deprecated.py保留ShowCreation包装 | 早期视频脚本（eola/eoc等） |
| `OldTex(...)`/`OldTexText(...)` 老版本TeX | `Tex(...)`/`TexText(...)` 新版本TeX | manim_imports_ext.py第2行专门导入old_tex_mobject | 所有老视频脚本 |
| `mobject.generate_target()` + `MoveToTarget(mobject)` | `mobject.animate` 动画语法 | 无包装，两种写法并存 | 早期视频脚本 |
| `FadeInFromDown(mobject)`/`FadeOutAndShiftDown(mobject)` | `FadeIn(mobject, UP)`/`FadeOut(mobject, DOWN)` | custom/deprecated.py提供参数化包装 | 早期视频脚本 |
| `GrowFromCenter(mobject)` | 新API中对应GrowFromCenter仍保留？ | custom/deprecated.py保留包装 | 早期视频脚本 |

**版本声明**：本仓库使用的是3Blue1Brown官方版本Manim（ManimGL），而非ManimCommunity版本，API存在差异（F-074）。研读源码时请参考ManimGL知识包，不要混用ManimCommunity的API文档。

## 相关概念

- [00 Videos仓库总览与环境准备](/concepts/00-videos-overview.md)
- [01 PiCreature角色系统详解](/concepts/01-picreature-characters.md)
- [02 自定义Scene基类体系](/concepts/02-custom-scenes.md)
- [03 视频代码结构与叙事模式](/concepts/03-video-structure-pattern.md)
- [05 代表性系列项目结构解析](/concepts/05-series-projects.md)
- [代表性视频系列目录导航](/references/representative-series.md)
