---
type: Reference
title: 代表性视频系列目录导航
description: 按年度列出eola/eoc/nn/eop等经典视频系列的目录结构、文件命名规范、运行命令示例与老代码兼容性注意事项。
tags: [videos, series, eola, eoc, nn, eop, directory-guide, running-videos]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26T00:00:00Z" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: Videos 源码事实采集
  - id: self
    resource: /references/representative-series.md
    title: 代表性视频系列目录导航
---

# 代表性视频系列目录导航

本文档按年度索引 3Blue1Brown videos 仓库中的经典系列视频，说明目录结构模式、文件命名规范、运行命令示例，以及研读老代码时的兼容性注意事项。

## 目录组织总览

videos 仓库根目录采用 `_YYYY/` 按年份命名的目录结构，从 2015 年持续更新至 2026 年（F-001）。除年度目录外，根目录包含三个核心支撑目录：`custom/`（自定义扩展）、`once_useful_constructs/`（历史可复用组件）、`outside_videos/`（外部合作内容）（F-002）。

系列视频在对应年度目录下以子目录形式组织，每个章节对应一个 `chapterN.py` 文件（F-005）；独立视频则直接在年度目录根下以主题命名单文件脚本（F-008）。

## 按年度列出主要系列

### 2016年：线性代数本质（Essence of Linear Algebra, eola）

**目录位置**：`_2016/eola/`（F-006）

| 项目 | 说明 |
|------|------|
| 章节数量 | 包含 chapter0-chapter11 共12个正篇章节 |
| 补充内容 | chapter8p2（第8章补充）、footnote、footnote2（脚注补充） |
| 辅助内容 | thumbnails（缩略图专用Scene） |
| Python文件总数 | 16个 |

**核心学习点**：
- 向量、矩阵、线性变换、行列式、特征值等核心概念的可视化叙事编排
- 早期PiCreature角色系统的使用模式
- 基础几何变换动画的构造方法

> ⚠️ 兼容性提示：本系列基于2016年Manim老版本编写，大量使用CONFIG字典配置（F-042）、ShowCreation动画（F-049）、OldTeX排版（F-048）。研读时重点学习叙事逻辑和可视化设计思想，API写法请参考ManimGL知识包的现代等价写法。

### 2017年：微积分本质（Essence of Calculus, eoc）

**目录位置**：`_2017/eoc/`（F-007）

| 项目 | 说明 |
|------|------|
| 章节数量 | 包含 chapter1-chapter10 共10个正篇章节 |
| 补充内容 | footnote（脚注补充）、old_chapter1（第1章早期版本，历史遗留） |
| Python文件总数 | 12个 |

**核心学习点**：
- CircleScene 与 ReconfigurableScene 的多继承组合使用（F-046）
- GraphScene 绘制函数图像与黎曼和矩形（F-035~F-038）
- `get_*` 方法封装可复用几何构造（F-047）
- construct() 方法按叙事顺序调用子方法的经典编排模式（F-043）
- OpeningQuote 开场白与 Thumbnail 缩略图的标准写法（F-044、F-045）
- `generate_target()` + `MoveToTarget` 动画模式（F-052）
- force_skipping() 交互式开发快速跳转技巧（F-051）

**典型代码片段参考**（eoc/chapter1.py）：
- 第1-2行：统一导入 + 跨章节导入（F-041）
- 第65-79行：CircleScene 的 CONFIG 字典配置（F-042）
- 第256-269行：Chapter1OpeningQuote 开场白配置（F-045）
- 第271-275行：Introduction.construct() 叙事编排（F-043）
- 第699-709行：ApproximateOneRing 多继承 CircleScene + ReconfigurableScene（F-046）

> ⚠️ 兼容性提示：本系列是"老API写法"的典型代表，大量使用：CONFIG字典配置、ShowCreation、FadeInFromDown、OldTex、generate_target()、itertools函数式构造VGroup（F-071）。所有这些老API在custom/deprecated.py中有兼容包装（F-049、F-050），可以在ManimGL环境中直接运行，但写新代码时请勿照搬这些写法。

### 2017年：神经网络系列（Neural Networks, nn）

**目录位置**：`_2017/nn/`（F-064）

| 项目 | 说明 |
|------|------|
| 章节结构 | part1.py、part2.py、part3.py 三个视频文件（不使用chapterN命名） |
| 核心实现 | network.py（神经网络可视化实现） |
| 数据加载 | mnist_loader.py（MNIST手写数字数据集加载） |
| 模型资源 | pretrained_weights_and_biases/（预训练权重与偏置目录） |

**核心学习点**：
- 非数学动画主题（计算机科学/AI）的可视化叙事方法
- 外部数据资源（预训练权重）与动画代码的集成方式
- partN.py 命名模式（适用于不按"章节"叙事的系列）

### 2018年：概率系列（Essence of Probability, eop）

**目录位置**：`_2018/eop/`（F-065）

| 项目 | 说明 |
|------|------|
| 新特征 | 系列目录下出现 `reusables/` 子目录 |
| 共享组件 | binary_option、brick_row、coin_flip_tree、dice、histograms 等概率相关可复用组件 |
| 目录演化标志 | 这是系列内部开始沉淀共享组件的起点（F-065） |

**核心学习点**：
- `reusables/` 模式：系列内共享组件的组织方式
- 概率可视化的专用组件设计（骰子、硬币、直方图、二叉树等）
- 从"系列内临时复用"到"沉淀到custom/通用层"的组件演化路径观察

### 其他年度独立视频

除系列子目录外，各年度目录根下存在大量独立视频单文件脚本（F-008），例如：
- `_2017/bell.py`：贝尔不等式相关视频
- `_2017/crypto.py`：密码学相关视频
- `_2018/fourier.py`：傅里叶变换相关视频

独立视频文件以视频主题命名，不使用chapterN前缀（F-056）。

## 目录结构模式

### 系列视频标准目录结构

```
_YYYY/series-name/
├── chapter0.py           # 第0章（可选，如预备知识）
├── chapter1.py           # 第1章正篇
├── chapter2.py           # 第2章正篇
├── ...
├── chapterN.py           # 第N章正篇
├── chapterMp2.py         # 第M章补充（可选）
├── footnote.py           # 脚注补充（可选）
├── footnotes.py          # 多个脚注（可选）
├── supplements.py        # 补充内容（可选）
├── thumbnails.py         # 缩略图专用Scene（可选）
└── reusables/            # 系列内共享组件目录（2018年后出现）
    ├── component1.py
    └── component2.py
```

### 文件命名规范（F-056）

| 文件类型 | 命名模式 | 示例 |
|----------|----------|------|
| 系列正篇章节 | `chapterN.py` | chapter1.py、chapter2.py、...、chapter10.py |
| 章节补充内容 | `chapterNpM.py` | chapter8p2.py（第8章第2部分） |
| 系列脚注/补充 | `footnote.py`、`supplements.py` | footnote.py、footnote2.py |
| 缩略图 | `thumbnails.py` 或独立Thumbnail类 | Eoc1Thumbnail类（在chapter文件内） |
| 独立视频 | 主题描述性名称 | `fourier.py`、`bell.py`、`crypto.py` |
| 分P系列（非章节） | `partN.py` | part1.py、part2.py、part3.py（nn系列） |
| 系列内共享组件 | `reusables/` 目录下模块名 | dice.py、coin_flip_tree.py |

### chapterN.py 文件内部结构模式

每个chapter文件内部通常包含多个Scene子类，按视频叙事顺序排列（F-041~F-047）：

1. **Thumbnail场景**（可选）：类名以Thumbnail结尾，只包含静态元素，无动画逻辑（F-044）
2. **OpeningQuote场景**（可选）：继承OpeningQuote基类，配置开场白文字、高亮词、作者（F-045）
3. **主场景类**：按视频段落划分多个Scene子类，每个类对应一个叙事片段
4. **可复用几何构造**：get_* 方法，返回构造好的VMobject（F-047）
5. **跨章节导入**：系列中其他章节定义的类通过相对导入复用（F-041）

## 如何运行一个视频脚本

### 标准运行命令

ManimGL 使用 `manimgl` 命令行工具运行视频脚本（F-055）：

```bash
# 基本语法：manimgl <脚本文件> <Scene类名>
# 示例：运行eoc第1章的Introduction场景
manimgl _2017/eoc/chapter1.py Introduction

# 预览模式（不写入文件，直接预览）
manimgl -p _2017/eoc/chapter1.py Introduction

# 低质量预览（快速渲染）
manimgl -pl _2017/eoc/chapter1.py Introduction

# 4K高质量渲染（写入视频文件）
manimgl -w --hd _2017/eoc/chapter1.py Introduction
# 注：默认配置已是4K 3840x2160 30fps（F-058）
```

### 交互式开发模式（推荐研读源码时使用）

checkpoint_paste 交互式工作流是3Blue1Brown的标准开发方式（F-053、F-055）：

```bash
# 在指定行进入iPython嵌入交互模式
manimgl -se <line_number> _2017/eoc/chapter1.py Chapter1

# 示例：在第600行进入交互模式（跳过前面所有动画）
manimgl -se 600 _2017/eoc/chapter1.py IntroduceCircle
```

进入交互模式后：
- 使用 `checkpoint_paste()` 粘贴剪贴板中的代码片段即时执行
- `checkpoint_paste(skip=True)` 跳过所有动画（零运行时间快速到达状态）
- `checkpoint_paste(record=True)` 录制最终动画
- `self.force_skipping()` 快速跳过后续动画到编辑位置（F-051）
- `self.revert_to_original_skipping_status()` 恢复正常动画播放

Sublime Text 用户可使用 `sublime_custom_commands/` 提供的三个快捷键命令（F-054）：
- ManimCheckpointPaste：普通模式
- ManimSkippedCheckpointPaste：skip=True 模式
- ManimRecordedCheckpointPaste：record=True 模式

### 后期拼接

渲染完多个场景片段后，使用 stage_scenes.py 按顺序暂存片段用于后期拼接（F-057）：

```bash
python stage_scenes.py <module_name>
```

## 老代码兼容性注意事项（必读）

### ⚠️ API差异总览

videos仓库中的经典系列（2016-2018年）基于Manim老版本编写，与当前ManimGL存在以下关键差异（F-073）：

| 差异类别 | 老代码写法 | 现代等价写法 | 兼容状态 |
|----------|-----------|-------------|----------|
| 场景配置 | `CONFIG = {...}` 类字典 | 直接定义类属性 | ✅ deprecated.py 不处理，Python语法天然兼容（CONFIG作为类属性仍可访问） |
| 创建动画 | `ShowCreation(mobject)` | `Create(mobject)` | ✅ custom/deprecated.py 保留包装 |
| TeX排版 | `OldTex(...)`/`OldTexText(...)` | `Tex(...)`/`TexText(...)` | ✅ manim_imports_ext.py 第2行专门导入 |
| 淡入方向 | `FadeInFromDown(mobject)` | `FadeIn(mobject, UP)` | ✅ custom/deprecated.py 参数化包装（F-050） |
| 淡出方向 | `FadeOutAndShiftDown(mobject)` | `FadeOut(mobject, DOWN)` | ✅ custom/deprecated.py 参数化包装 |
| 放大出现 | `FadeInFromLarge(mobject, scale_factor=2)` | `FadeIn(mobject, scale=1/scale_factor)` | ✅ custom/deprecated.py 参数化包装 |
| 中心生长 | `GrowFromCenter(mobject)` | （新版仍保留或有等价） | ✅ custom/deprecated.py 保留 |
| 目标状态动画 | `mob.generate_target()` + `MoveToTarget(mob)` | `mob.animate.xxx()` 语法 | ⚠️ 无兼容包装，两种写法均可运行 |
| 函数式构造 | `import itertools as it` + it.starmap/it.chain | 直接用VGroup构造或列表推导 | ✅ itertools是Python标准库，仍可正常使用（F-071） |
| 空动画占位 | `Animation(mobject)` | （新版仍支持或可用Wait替代） | ✅ 仍可运行（F-072） |

### ⚠️ 已废弃但仍在使用的基类

两个核心场景基类已被源码头文件标注为废弃/不可用，但历史视频中大量使用（F-075）：

1. **GraphScene**（once_useful_constructs/graph_scene.py:27）
   - 文件注释标注：`# TODO: this class should be deprecated`
   - 建议替代：使用manimlib内置的Axes坐标系统
   - 使用现状：eoc微积分系列几乎每章都通过多继承使用GraphScene
   - 运行状态：在兼容层支持下仍可运行，但新项目不建议使用

2. **ReconfigurableScene**（once_useful_constructs/reconfigurable_scene.py:7）
   - 文件注释标注：`# Note, this seems to no longer work as intended`
   - 功能：通过创建新场景实例+Transform实现配置切换过渡
   - 使用现状：eoc中演示参数变化效果（如圆的半径dr从大变小）时使用
   - 运行状态：功能可能已损坏，研读源码时理解其设计意图即可

### ⚠️ 版本声明

- 本仓库使用的是 **3Blue1Brown官方ManimGL**，不是ManimCommunity版本（F-074）
- 两个版本API存在显著差异，不要混用ManimCommunity的文档和示例
- TeX相关：使用 `Tex()` 而非ManimCommunity的 `MathTex()`（F-059）
- LaTeX字符串使用raw字符串前缀R：`Tex(R"\frac{1}{2}")`
- 颜色着色：使用 `t2c`（tex_to_color_map）参数，如 `Tex(formula, t2c={"x": BLUE})`；老代码使用 `set_color_by_tex()` 方法（F-060）

### 研读源码的正确姿势

1. **先学现代API**：先掌握ManimGL知识包中的当前API写法，建立正确的心智模型
2. **重点学思想**：读老代码时重点关注**叙事编排**、**视觉设计**、**组件抽象**——这些不随API变化而过时
3. **API差异速查**：遇到不认识的类名/方法名，先查本文档的兼容性表格，再查custom/deprecated.py
4. **不要照搬老写法**：理解老代码的设计意图后，用现代API重新实现是更好的学习方式
5. **从新到旧读**：可以先看2020年后较新的视频代码（API更接近现代），再回头看2016-2018年的经典系列

## 相关概念

- [00 Videos仓库总览与环境准备](/concepts/00-videos-overview.md)
- [02 自定义Scene基类体系](/concepts/02-custom-scenes.md)
- [03 视频代码结构与叙事模式](/concepts/03-video-structure-pattern.md)
- [04 checkpoint_paste交互式开发工作流](/concepts/04-checkpoint-paste-workflow.md)
- [05 代表性系列项目结构解析](/concepts/05-series-projects.md)
- [Videos 自定义模块索引](/references/custom-modules-index.md)
