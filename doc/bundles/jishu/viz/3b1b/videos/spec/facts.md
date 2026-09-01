---
type: spec
title: "3b1b Videos 源码事实采集（R阶段）"
---

# 3b1b Videos 源码事实采集（R阶段）

## 模块概览表

| 分类 | 路径 | 核心内容 |
|------|------|----------|
| 入口文件 | `manim_imports_ext.py` | 统一导入入口，导入manimlib+所有自定义扩展 |
| 角色系统 | `custom/characters/` | PiCreature、PiCreatureScene、TeacherStudentsScene |
| 可复用组件 | `once_useful_constructs/` | GraphScene、ReconfigurableScene、线性代数/图论等场景基类 |
| 年度目录 | `_2015/` ~ `_2026/` | 按年份组织的视频项目源码 |
| 自定义模块 | `custom/` | backdrops、banner、drawings、end_screen、deprecated等 |
| 废弃内容 | `custom/deprecated.py` | 老版本动画类的兼容包装 |

---

## 一、目录结构与组织模式

F-001：videos/ 根目录下按年份组织视频项目，目录命名格式为 `_YYYY/`（如 `_2015/`、`_2016/`、...、`_2026/`），从2015年持续更新至2026年。
- 源码路径：`/`:1-40（根目录结构）

F-002：除年度目录外，根目录包含三个核心模块目录：`custom/`（自定义扩展）、`once_useful_constructs/`（历史可复用组件）、`outside_videos/`（外部合作内容）。
- 源码路径：`/`:1-40

F-003：根目录存在统一导入文件 `manim_imports_ext.py`，是所有视频脚本的标准入口，替代直接 `from manimlib import *`。
- 源码路径：`manim_imports_ext.py`:1-14

F-004：`manim_imports_ext.py` 第1行从 `manimlib` 通配导入，第2行导入 `old_tex_mobject`，第4-14行依次导入 custom 子模块的所有内容（backdrops、banner、pi_creature、pi_creature_animations、pi_creature_scene、deprecated、drawings、end_screen、filler、logo、opening_quote）。
- 源码路径：`manim_imports_ext.py`:1-14

F-005：系列视频（如Essence of Linear Algebra、Essence of Calculus）在对应年度目录下以子目录形式组织，每个章节对应一个 `chapterN.py` 文件。
- 源码路径：`_2016/eola/`、`_2017/eoc/` 目录结构

F-006：线性代数本质系列（Essence of Linear Algebra, eola）位于 `_2016/eola/`，包含 chapter0-chapter11、chapter8p2、footnote、footnote2、thumbnails 共16个Python文件。
- 源码路径：`_2016/eola/` 目录结构

F-007：微积分本质系列（Essence of Calculus, eoc）位于 `_2017/eoc/`，包含 chapter1-chapter10、footnote、old_chapter1 共12个Python文件。
- 源码路径：`_2017/eoc/` 目录结构

F-008：年度目录中除系列子目录外，还存在大量独立视频的单文件脚本（如 `_2017/bell.py`、`_2017/crypto.py`、`_2018/fourier.py` 等），文件以视频主题命名。
- 源码路径：`_2017/`、`_2018/` 根文件列表

F-009：`once_useful_constructs/` 目录无 `__init__.py` 文件，导入时通过 `from once_useful_constructs import *` 依赖Python路径搜索机制直接导入模块。
- 源码路径：`once_useful_constructs/`（无__init__.py）

F-010：根目录存在 `custom_config.yml` 配置文件，用于自定义Manim的渲染路径、资源目录等配置。
- 源码路径：`custom_config.yml`（根目录）

F-011：根目录存在 `sublime_custom_commands/` 目录，包含Sublime Text编辑器的集成插件，提供checkpoint_paste等快捷键命令。
- 源码路径：`sublime_custom_commands/` 目录

---

## 二、PiCreature 角色系统

F-012：`custom/characters/pi_creature.py` 第31行定义 `PI_CREATURE_SCALE_FACTOR = 0.5` 作为Pi生物的默认缩放因子。
- 源码路径：`custom/characters/pi_creature.py`:31

F-013：`custom/characters/pi_creature.py` 第33-38行定义PiCreature SVG部件索引常量：LEFT_EYE_INDEX=0、RIGHT_EYE_INDEX=1、LEFT_PUPIL_INDEX=2、RIGHT_PUPIL_INDEX=3、BODY_INDEX=4、MOUTH_INDEX=5。
- 源码路径：`custom/characters/pi_creature.py`:33-38

F-014：PiCreature类继承自SVGMobject（第41行），而非直接继承VMobject，基于外部SVG文件加载角色形态。
- 源码路径：`custom/characters/pi_creature.py`:41

F-015：PiCreature类属性定义手臂位置范围：`right_arm_range=(0.55, 0.7)`、`left_arm_range=(0.34, 0.462)`；眼睛比例：`pupil_to_eye_width_ratio=0.4`、`pupil_dot_to_pupil_width_ratio=0.3`。
- 源码路径：`custom/characters/pi_creature.py`:43-46

F-016：PiCreature.__init__ 接受mode参数（默认"plain"），通过mode名称从 `pi_creature_images` 目录加载对应的SVG文件，mode切换即切换不同表情形态。
- 源码路径：`custom/characters/pi_creature.py`:48-72,83-94

F-017：PiCreature通过 `init_structure()` 方法（第96-107行）重构SVG结构，不直接使用Figma导出的原始submobjects，而是手动提取eyes、body、mouth三个核心部件。
- 源码路径：`custom/characters/pi_creature.py`:96-107

F-018：PiCreature的眼睛不使用SVG原始路径，而是在 `draw_eyes()` 方法（第109-131行）中用Circle重新绘制黑色瞳孔和白色光点，解决原始SVG眼睛路径不一致问题。
- 源码路径：`custom/characters/pi_creature.py`:109-131

F-019：PiCreature初始化时调用 `self.body.insert_n_curves(100)`（第81行），为身体路径插入额外曲线点，使不同mode之间的形态变换动画更平滑。
- 源码路径：`custom/characters/pi_creature.py`:81

F-020：PiCreature.`change_mode(mode)` 方法（第147-158行）通过创建新PiCreature实例、匹配样式和高度、对齐眼睛位置，再调用 `self.become(new_self)` 实现形态切换动画。
- 源码路径：`custom/characters/pi_creature.py`:147-158

F-021：PiCreature.`look(direction)` 方法（第163-177行）根据方向向量移动瞳孔位置，实现眼睛看向指定方向的效果，瞳孔移动范围限制在虹膜内（`v_norm - 0.75 * pupil_radius`）。
- 源码路径：`custom/characters/pi_creature.py`:163-177

F-022：PiCreature.`look_at(point_or_mobject)` 方法（第179-185行）接受坐标点或Mobject，自动计算看向目标的方向向量并调用look()。
- 源码路径：`custom/characters/pi_creature.py`:179-185

F-023：PiCreature.`blink()` 方法（第198-207行）通过将眼睛所有点的y坐标压到眼睛底部实现眨眼效果（压扁成一条线）。
- 源码路径：`custom/characters/pi_creature.py`:198-207

F-024：PiCreature.`says()` 方法（第253-261行）返回PiCreatureBubbleIntroduction动画，使用SpeechBubble（对话气泡）；`thinks()` 方法（第263-271行）使用ThoughtBubble（思考气泡）。
- 源码路径：`custom/characters/pi_creature.py`:253-271

F-025：PiCreature有四个预定义子类：Randolph（蓝色默认Pi，第299-300行，只是别名）、Mortimer（灰色棕色，默认翻转，第303-311行，用于教师角色）、Mathematician（灰色，第314-316行）、BabyPiCreature（高度1.5，大眼睛，第319-337行）。
- 源码路径：`custom/characters/pi_creature.py`:299-337

F-026：独立Eyes类（第368-405行）可以为非PiCreature的VMobject添加眼睛部件，内部通过创建临时PiCreature实例提取眼睛部分实现。
- 源码路径：`custom/characters/pi_creature.py`:368-405

---

## 三、Scene基类与自定义场景

F-027：PiCreatureScene继承自InteractiveScene（`pi_creature_scene.py`第37行），是所有带Pi生物场景的基类，提供自动眨眼、视线追踪、对话气泡管理等功能。
- 源码路径：`custom/characters/pi_creature_scene.py`:37

F-028：PiCreatureScene类属性：`total_wait_time=0`、`seconds_to_blink=3`（每3秒自动眨眼）、`pi_creatures_start_on_screen=True`、默认PiCreature颜色为BLUE、默认起始角落为DL（左下角）。
- 源码路径：`custom/characters/pi_creature_scene.py`:38-45

F-029：PiCreatureScene.setup()方法（第47-52行）自动调用create_pi_creatures()创建VGroup，取第一个作为primary pi_creature，并默认添加到场景中。
- 源码路径：`custom/characters/pi_creature_scene.py`:47-52

F-030：PiCreatureScene重写 `wait()` 方法（第212-226行），在等待期间每3秒自动触发一次blink()，实现自然眨眼效果；stop_condition存在时调用non_blink_wait()跳过眨眼。
- 源码路径：`custom/characters/pi_creature_scene.py`:212-226

F-031：PiCreatureScene重写 `anims_from_play_args()` 方法（第156-185行），在每次play()时自动让所有屏幕上的Pi生物看向第一个被动画的mobject，实现视线自动追踪。
- 源码路径：`custom/characters/pi_creature_scene.py`:156-185

F-032：TeacherStudentsScene继承自PiCreatureScene（第255行），实现教室场景：1个Mortimer教师（右下角）+3个Randolph学生（左下角），背景色为GREY_E，包含黑板（ScreenRectangle）。
- 源码路径：`custom/characters/pi_creature_scene.py`:255-298

F-033：TeacherStudentsScene学生颜色为 `[BLUE_D, BLUE_E, BLUE_C]`，教师颜色为GREY_BROWN，学生缩放因子0.8，每2秒眨眼一次（比普通场景频繁）。
- 源码路径：`custom/characters/pi_creature_scene.py`:256-261

F-034：TeacherStudentsScene提供 `teacher_says()`、`student_says()`、`teacher_thinks()`、`student_thinks()`、`play_student_changes()` 等便捷方法，封装师生对话的常见模式。
- 源码路径：`custom/characters/pi_creature_scene.py`:306-360

F-035：GraphScene位于 `once_useful_constructs/graph_scene.py` 第27行，继承自Scene，提供坐标轴创建、函数图像绘制、黎曼和矩形等图表功能；文件注释标注"TODO: this class should be deprecated"（应被Axes替代）。
- 源码路径：`once_useful_constructs/graph_scene.py`:22-27

F-036：GraphScene通过类属性配置坐标轴：x_min/x_max（默认-1到10）、x_axis_width（默认9）、x_tick_frequency（默认1）、y_min/y_max、y_axis_height、graph_origin（默认2.5DOWN+4LEFT）等。
- 源码路径：`once_useful_constructs/graph_scene.py`:28-51

F-037：GraphScene.`setup_axes()` 方法（第61-132行）创建NumberLine作为x轴和y轴，y轴旋转90度，支持自动添加数字标签和轴名称。
- 源码路径：`once_useful_constructs/graph_scene.py`:61-132

F-038：GraphScene提供 `coords_to_point(x,y)` 和 `point_to_coords(point)` 进行数学坐标与屏幕坐标转换，`get_graph(func)` 绘制函数曲线，`get_riemann_rectangles()` 生成黎曼和矩形。
- 源码路径：`once_useful_constructs/graph_scene.py`:134-150

F-039：ReconfigurableScene位于 `once_useful_constructs/reconfigurable_scene.py` 第7行，继承自Scene，文档注释标注"Note, this seems to no longer work as intended"（已不能按预期工作）。
- 源码路径：`once_useful_constructs/reconfigurable_scene.py`:7-10

F-040：ReconfigurableScene.`transition_to_alt_config()` 方法（第19-56行）通过创建同一场景类的新实例（skip_animations=True）获取不同配置下的状态，再用Transform动画过渡，用于演示参数变化效果（如eoc中dr从大变小）。
- 源码路径：`once_useful_constructs/reconfigurable_scene.py`:19-56

---

## 四、典型视频Scene代码模式

F-041：所有视频脚本第一行均为 `from manim_imports_ext import *`，系列视频（如eoc）会额外从其他章节导入需要的类（如eoc/chapter1.py第2行 `from _2017.eoc.chapter2 import Car, MoveCar`）。
- 源码路径：`_2017/eoc/chapter1.py`:1-2

F-042：老代码（2015-2018年视频）使用CONFIG类字典配置场景参数（如CircleScene第66-79行的CONFIG字典），这是Manim老版本的配置方式，新版本Manim已改为直接使用类属性。
- 源码路径：`_2017/eoc/chapter1.py`:65-79

F-043：典型视频Scene的construct()方法按叙事顺序调用多个子方法，每个子方法对应视频的一个片段/段落（如Introduction.construct()调用show_series()→show_many_facts()→invent_calculus()）。
- 源码路径：`_2017/eoc/chapter1.py`:271-275

F-044：视频缩略图使用专门的Scene类（如Eoc1Thumbnail，第5行），类名以Thumbnail结尾，只包含静态元素无动画逻辑。
- 源码路径：`_2017/eoc/chapter1.py`:5-62

F-045：章节开场白使用OpeningQuote基类（如Chapter1OpeningQuote，第256行），通过CONFIG字典配置quote内容、高亮词、作者信息。
- 源码路径：`_2017/eoc/chapter1.py`:256-269

F-046：复杂场景使用多继承组合功能（如ApproximateOneRing第699行继承CircleScene和ReconfigurableScene，GraphRectangles第1001行继承CircleScene和GraphScene），setup()方法中依次调用各父类setup()。
- 源码路径：`_2017/eoc/chapter1.py`:699-709,1001-1021

F-047：场景中可复用的几何构造封装为get_*方法（如CircleScene.get_ring()、get_rings()、get_unwrapped()），返回构造好的VMobject供动画调用。
- 源码路径：`_2017/eoc/chapter1.py`:172-194,223-246

F-048：老版本TeX使用OldTex和OldTexText类（而非新版本的Tex/TexText），在manim_imports_ext.py第2行从 `manimlib.mobject.svg.old_tex_mobject` 导入，保持历史代码兼容。
- 源码路径：`manim_imports_ext.py`:2，以及各视频文件中的OldTex/OldTexText用法

F-049：老代码使用ShowCreation动画（新版本已改为Create），GrowFromCenter、FadeInFromDown、FadeOutAndShiftDown等动画类在custom/deprecated.py中保留为兼容包装。
- 源码路径：`custom/deprecated.py`:1-22

F-050：custom/deprecated.py中FadeInFromDown是FadeIn(..., UP)的包装，FadeOutAndShiftDown是FadeOut(..., DOWN)的包装，FadeInFromLarge是FadeIn(..., scale=1/scale_factor)的包装，用于兼容老版本命名。
- 源码路径：`custom/deprecated.py`:10-22

F-051：Pi生物场景中通过 `self.force_skipping()` 和 `self.revert_to_original_skipping_status()` 跳过部分动画快速到达编辑位置，配合checkpoint_paste实现交互式开发（如IntroduceCircle.construct()第600-604行）。
- 源码路径：`_2017/eoc/chapter1.py`:600-604,712-723

F-052：使用 `mobject.generate_target()` 创建目标状态，再通过MoveToTarget动画实现从当前状态到目标状态的过渡，是老代码中常用的动画模式（如fg_group.generate_target()，第524-529行）。
- 源码路径：`_2017/eoc/chapter1.py`:524-529

---

## 五、工作流与开发工具

F-053：checkpoint_paste是交互式开发的核心工具，在iPython嵌入模式下运行剪贴板中的代码，支持状态管理；参数skip=True跳过所有动画（零运行时间），record=True录制动画。
- 源码路径：CLAUDE.md中描述，以及sublime_custom_commands集成

F-054：sublime_custom_commands/manim_plugins.py提供Sublime Text插件集成，包含三个Sublime命令文件：ManimCheckpointPaste、ManimSkippedCheckpointPaste、ManimRecordedCheckpointPaste，对应三种checkpoint_paste模式。
- 源码路径：`sublime_custom_commands/` 目录文件

F-055：开发工作流：1)创建继承InteractiveScene/Scene的类；2)使用 `manimgl -se <line_number>` 在指定行进入交互模式；3)用checkpoint_paste()迭代开发动画代码；4)-p标志预览不写文件。
- 源码路径：CLAUDE.md中Key Commands和Development Workflow部分

F-056：视频文件命名规范：单集视频使用描述性名称（如 `fourier.py`、`bell.py`），系列视频使用chapterN.py按章节编号，补充内容用footnote.py、supplements.py命名。
- 源码路径：各年度目录文件命名

F-057：`python stage_scenes.py <module_name>` 用于按顺序暂存渲染好的场景片段，用于视频后期拼接。
- 源码路径：CLAUDE.md中Staging Scenes部分

F-058：相机配置为4K分辨率（3840x2160），30fps，配置在custom_config.yml中；资源管理通过Dropbox集成，使用自定义路径配置。
- 源码路径：CLAUDE.md中Configuration部分

F-059：数学排版使用Tex()而非ManimCommunity的MathTex()，LaTeX字符串使用raw字符串前缀R（如 `Tex(R"\pi")`、`Tex(R"\frac{1}{2}")`）。
- 源码路径：CLAUDE.md中Code Patterns部分

F-060：颜色使用t2c（tex_to_color_map）参数为公式中特定符号着色，如 `Tex(formula, t2c={"x": BLUE, "y": RED})`，老代码使用set_color_by_tex()方法。
- 源码路径：CLAUDE.md中Color and Styling，以及eoc代码中用法

---

## 六、其他组件与注意事项

F-061：`custom/` 目录包含多个功能模块：backdrops.py（背景主题）、banner.py（视频横幅）、drawings.py（自定义绘图工具）、end_screen.py（标准片尾组件）、filler.py（填充内容）、logo.py（Logo组件）、opening_quote.py（开场白组件）。
- 源码路径：`custom/` 目录结构

F-062：`once_useful_constructs/` 包含20个模块：arithmetic、butterfly_curve、combinatorics、complex_transformation_scene、counting、fractals、graph_scene、graph_theory、light、linear_algebra、matrix_multiplication、reconfigurable_scene、region、sample_space_scene、vector_space_scene等，涵盖各类数学可视化场景基类。
- 源码路径：`once_useful_constructs/` 目录结构

F-063：`once_useful_constructs/` 包含3个GLSL着色器文件：map_point_pairs.glsl、quadratic_bezier_distance.glsl、rotate.glsl，用于GPU加速的图形变换效果。
- 源码路径：`once_useful_constructs/*.glsl`

F-064：神经网络系列（nn）位于 `_2017/nn/`，包含part1.py、part2.py、part3.py三个视频文件，以及network.py（网络实现）、mnist_loader.py（MNIST数据加载），还有预训练权重文件目录pretrained_weights_and_biases。
- 源码路径：`_2017/nn/` 目录结构

F-065：2018年及之后的系列视频开始在子目录下使用reusables/目录存放共享组件（如 `_2018/eop/reusables/` 包含binary_option、brick_row、coin_flip_tree、dice、histograms等概率相关可复用组件）。
- 源码路径：`_2018/eop/reusables/` 目录结构

F-066：MortyPiCreatureScene（`pi_creature_scene.py`第247行）是PiCreatureScene的简单子类，仅修改默认配置：颜色为GREY_BROWN、flip_at_start=True、默认角落为DR（右下角）。
- 源码路径：`custom/characters/pi_creature_scene.py`:247-252

F-067：TauCreature（`pi_creature.py`第340行）是PiCreature的变体，从vector_images目录而非pi_creature_images目录加载SVG，文件前缀为"TauCreatures_"，init_structure()为空实现。
- 源码路径：`custom/characters/pi_creature.py`:340-356

F-068：PiCreature.`get_arm_copies()` 方法（第230-235行）通过 `pointwise_become_partial()` 从身体路径中提取手臂部分的副本，用于手臂动画效果。
- 源码路径：`custom/characters/pi_creature.py`:230-235

F-069：PiCreatureScene.`joint_blink()` 方法（第190-210行）使用squish_rate_func和there_and_back实现多个Pi生物依次眨眼的错峰效果，shuffle参数可随机化顺序。
- 源码路径：`custom/characters/pi_creature_scene.py`:190-210

F-070：TeacherStudentsScene.`zoom_in_on_thought_bubble()` 方法（第362-378行）通过ApplyPointwiseFunction对场景所有mobject应用径向变换，实现聚焦到思考气泡的"思想放大"效果。
- 源码路径：`custom/characters/pi_creature_scene.py`:362-378

F-071：老代码中大量使用itertools简写 `import itertools as it`，通过it.starmap、it.chain、it.count等函数式编程工具构造VGroup和动画序列。
- 源码路径：`_2017/eoc/chapter1.py`:342,587等位置的it.用法

F-072：老代码中使用 `Animation(mobject)` 创建"空动画"（仅保持mobject在动画期间不动），用于在LaggedStart或AnimationGroup中占位，保持某些元素不变化（如第322-323行对bubble的处理）。
- 源码路径：`_2017/eoc/chapter1.py`:322-323等多处

---

## 七、版本兼容与历史遗留说明

F-073：videos/中的代码覆盖2015-2026年，基于不同时期的Manim版本，存在多种历史遗留写法并存的情况：CONFIG字典vs类属性、ShowCreationvs Create、OldTexvs Tex、generate_target()+MoveToTargetvs mobject.animate语法。
- 源码路径：跨年度文件对比可见写法演变

F-074：CLAUDE.md明确说明本仓库使用的是3b1b版本的Manim（即ManimGL），而非ManimCommunity版本，API存在差异。
- 源码路径：CLAUDE.md中Notes部分

F-075：ReconfigurableScene和GraphScene均被标注为待废弃/不能正常工作的遗留组件，但历史视频代码中仍在广泛使用（如eoc系列大量使用GraphScene）。
- 源码路径：对应类文件的TODO/Note注释，以及eoc中的多继承用法

F-076：once_useful_constructs/目录命名意为"曾经有用的构造"，表明其中大部分是历史项目中沉淀的组件，不一定适用于新版本Manim的新项目开发。
- 源码路径：目录命名本身的含义

