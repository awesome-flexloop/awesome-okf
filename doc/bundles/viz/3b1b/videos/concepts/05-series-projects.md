---
type: Concept
title: 代表性系列项目结构解析
description: 深度解析3Blue1Brown四大经典系列源码结构——线性代数本质(eola)、微积分本质(eoc)、神经网络(nn)、概率系列(eop)，理解系列项目的reusables复用模式、章节组织、跨章共享组件的最佳实践。
tags: [videos, series, projects, eola, eoc, nn, eop, linear-algebra, calculus, neural-networks, probability, manim, 3blue1brown]
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

# 代表性系列项目结构解析

> ⚠️ **重要版本说明**：本文解析的四大经典系列（eola/eoc/nn/eop）主要制作于2016-2018年，使用Manim老版本API（CONFIG字典、ShowCreation、OldTex、generate_target()等）。研读时重点关注**系列项目的组织结构、组件复用模式、动画设计思想**，API写法本身请对照现代ManimGL等价方式理解。

3Blue1Brown的视频不是零散的独立作品——绝大多数高质量内容都是以**系列（Series）**形式推出的：线性代数本质（Essence of Linear Algebra, eola）12集、微积分本质（Essence of Calculus, eoc）10集、神经网络系列3集、概率系列（Essence of Probability, eop）多集。系列化制作有其独特的工程挑战：如何在多集之间保持视觉风格统一？如何复用通用图形组件？如何组织十多个相关视频文件的代码？

从2016年的eola到2018年的eop，我们能清晰看到系列项目组织模式的演进：从"每章一个独立文件，共享组件散落在各章"到"reusables/目录集中存放共享组件"的标准化模式。本文将逐一解析四大经典系列的目录结构、核心文件、复用模式，并总结研读系列源码的方法论。

## 线性代数本质（eola/）：数字编号的章节式结构

**位置**：`_2016/eola/`（F-006）
**集数**：chapter0 ~ chapter11（共12个正篇章节）+ chapter8p2 + footnote + footnote2 = 16个Python文件
**主题**：向量是什么、线性组合、矩阵、行列式、逆矩阵、点积、叉积、基变换、特征向量、抽象向量空间等

### eola目录结构

```
_2016/eola/
├── chapter0.py              # 序章：向量是什么？
├── chapter1.py              # 第1章：线性组合与张成空间
├── chapter2.py              # 第2章：矩阵与线性变换
├── chapter3.py              # 第3章：矩阵乘法与线性变换复合
├── chapter4.py              # 第4章：行列式
├── chapter5.py              # 第5章：逆矩阵、列空间与零空间
├── chapter6.py              # 第6章：点积与对偶性
├── chapter7.py              # 第7章：叉积
├── chapter8.py              # 第8章：基变换
├── chapter8p2.py            # 第8章补充：特征向量与特征值
├── chapter9.py              # 第9章：抽象向量空间
├── chapter10.py             # 第10章：（对应视频的某一主题）
├── chapter11.py             # 第11章：（系列总结/进阶主题）
├── footnote.py              # 脚注补充视频
├── footnote2.py             # 第二个脚注补充
└── thumbnails/              # 缩略图资源目录（部分版本）
```

### eola的文件结构特点

作为第一个大型系列，eola的组织方式相对朴素直接（F-005、F-006）：

**1. 纯数字编号命名**

每个章节文件以`chapterN.py`命名，N从0开始连续编号，对应视频发布顺序。这种命名方式的好处是简单直观——你知道chapter0是第一集，chapter3是第四集，文件排序就是观看顺序。但缺点也明显：从文件名看不出这一章讲什么主题，需要打开文件或对照视频标题。

**2. 每章是自包含的Scene类集合**

每个chapterN.py文件包含：
- 该章的主Scene类（通常与章节主题相关，如`WhatIsAVector`、`LinearCombinations`等）
- 该章专用的自定义Mobject子类（如`Vector`、`BasisVector`等，注意这是eola本地定义的，不是manimlib内置的）
- 该章专用的辅助函数和动画类
- 章末可能有Thumbnail场景类

**3. 组件复用方式：跨章导入 + once_useful_constructs**

eola系列**没有自己的reusables目录**——这是2016年时还没形成的模式。组件复用通过两种方式：
- 跨章节直接导入：比如某章定义了一个好用的`Vector`类，其他章`from _2016.eola.chapter1 import Vector`
- 通用线性代数组件沉淀到上层：`once_useful_constructs/linear_algebra.py`存放跨系列通用的线性代数可视化组件（F-062）

**典型的eola章节文件开头**：

```python
# ⚠️ 老版本写法（2016年eola系列）
from manim_imports_ext import *
# 如果需要其他章的组件，直接跨章导入
from _2016.eola.chapter2 import LinearTransformationScene

class Chapter4Determinants(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors": True,
        "foreground_plane_kwargs": {
            "x_radius": 8,
            "y_radius": 8,
        },
    }
    
    def construct(self):
        self.setup()
        self.introduce_determinant()
        self.show_area_scaling()
        self.compute_2x2()
        # ...更多叙事子方法...
```

注意这里的`LinearTransformationScene`——这是eola系列中最重要的共享场景基类之一，它在早期章节定义，后面讲线性变换、行列式、特征值的章节都继承它，自动获得网格平面、基向量、变换动画等基础功能。

### eola的学习价值

eola是3Blue1Brown的成名之作，也是视频动画与数学教学结合的巅峰之一。研读eola源码重点关注：
- 如何用动画直观演示抽象的线性代数概念（线性变换是"网格扭曲"、行列式是"面积缩放比例"）
- `LinearTransformationScene`基类如何设计才能支撑十几章不同的内容
- 如何用颜色编码不同数学对象（基向量i/j分别用不同颜色、矩阵列对应基向量颜色）

## 微积分本质（eoc/）：多继承组合场景的典范

**位置**：`_2017/eoc/`（F-007）
**集数**：chapter1 ~ chapter10（10个正篇）+ footnote + old_chapter1 = 12个Python文件
**主题**：导数、链式法则、乘积法则、隐函数求导、积分、微积分基本定理、泰勒级数等

### eoc目录结构

```
_2017/eoc/
├── chapter1.py              # 第1章：微积分导论（面积、斜率、变化率）
├── chapter2.py              # 第2章：导数的悖论
├── chapter3.py              # 第3章：用几何来求导（幂函数、三角函数）
├── chapter4.py              # 第4章：链式法则与乘积法则
├── chapter5.py              # 第5章：隐函数求导
├── chapter6.py              # 第6章：积分是什么？
├── chapter7.py              # 第7章：微积分基本定理
├── chapter8.py              # 第8章：积分与换元法
├── chapter9.py              # 第9章：泰勒级数
├── chapter10.py             # 第10章：（系列总结/进阶）
├── footnote.py              # 脚注补充视频
└── old_chapter1.py          # 第1章的旧版本（保留参考）
```

### eoc的核心特色：多继承组合场景

eoc系列最值得学习的是其**多继承场景组合模式**——这在[03-video-structure-pattern.md](/concepts/03-video-structure-pattern.md)中已有提及，eoc把这种模式用到了极致（F-046）。

以chapter1.py为例，文件中定义了多个Scene子类，很多都用了多继承：

```python
# _2017/eoc/chapter1.py
class CircleScene(Scene):
    """圆形几何场景基类：提供圆形、圆环、展开等几何构造"""
    CONFIG = {
        "R": 2,
        "stroke_color": BLUE,
        # ...圆形相关配置...
    }
    def get_ring(self): ...
    def get_rings(self, n=20): ...
    def get_unwrapped_ring(self): ...

# 同时继承圆形功能和配置切换功能
class ApproximateOneRing(CircleScene, ReconfigurableScene):
    """用圆环近似圆形面积，支持n_rings参数切换动画"""
    CONFIG = {"n_rings": 10, "ring_width": 0.2}
    def setup(self):
        CircleScene.setup(self)
        ReconfigurableScene.setup(self)  # 必须手动调用两个父类setup

# 同时继承圆形功能和图表功能
class GraphRectangles(CircleScene, GraphScene):
    """在坐标图上展示黎曼矩形与圆形面积的关系"""
    def setup(self):
        CircleScene.setup(self)
        GraphScene.setup(self)
```

这种"Mix-in"式的多继承让场景功能组合非常灵活：
- 需要圆形几何？继承`CircleScene`
- 需要配置切换动画？继承`ReconfigurableScene`
- 需要画坐标图和函数曲线？继承`GraphScene`
- 需要两个？都继承，记得调用setup()

### chapter1.py中的Car和MoveCar

注意eoc/chapter1.py第2行的导入（F-041）：

```python
from _2017.eoc.chapter2 import Car, MoveCar
```

chapter2（导数章）中定义了汽车位置-速度可视化的`Car`类和对应的动画类`MoveCar`，chapter1引入它来展示"变化率"的直观例子——这就是跨章节组件复用：哪章定义的组件最"属于"那个主题，就放在哪章，其他章需要时直接导入。

### ReconfigurableScene的妙用

eoc大量使用`once_useful_constructs/reconfigurable_scene.py`中的`ReconfigurableScene`（虽然注释标注"已不能按预期工作"，但eoc中仍大量使用F-075）。它的核心方法`transition_to_alt_config()`允许你在同一个场景内平滑切换CONFIG参数，比如：

- 圆环数量n_rings从10渐变到100，展示"近似→精确"的极限过程
- 网格密度从粗变细，展示积分是"黎曼和取极限"

这种动画模式对于讲解微积分中的"极限"思想至关重要——你能亲眼看到近似值如何一步步逼近精确值。

### eoc的学习价值

eoc是多继承场景组合、极限思想可视化、ReconfigurableScene用法的最佳教材，研读时重点关注：
- 如何用`CircleScene`、`GraphScene`、`ReconfigurableScene`等基类组合出复杂场景
- 如何用`transition_to_alt_config()`做参数渐变动画演示极限
- 导数、积分等概念如何转化为可视的几何动画（汽车位置/速度、圆环展开成长方形）

## 神经网络系列（nn/）：带外部数据与预训练模型

**位置**：`_2017/nn/`（F-064）
**集数**：part1.py、part2.py、part3.py（3集）
**主题**：神经网络是什么、梯度下降与反向传播、手写数字识别（MNIST）
**特色**：这是Videos仓库中唯一包含**真实数据和预训练模型**的系列

### nn目录结构

```
_2017/nn/
├── part1.py                         # 第1部分：神经网络结构介绍
├── part2.py                         # 第2部分：梯度下降与反向传播
├── part3.py                         # 第3部分：MNIST手写数字识别实战
├── network.py                       # 神经网络Python实现（纯numpy）
├── mnist_loader.py                  # MNIST数据集加载工具
└── pretrained_weights_and_biases/   # 预训练权重目录
    ├── weights_0.npy                # 第0层权重
    ├── biases_0.npy                 # 第0层偏置
    ├── weights_1.npy                # 第1层权重
    ├── biases_1.npy                 # 第1层偏置
    └── ...更多权重文件...
```

### nn系列的独特之处

与eola/eoc纯数学可视化不同，nn系列是**"代码+真实数据+动画"三者结合**的范例（F-064）：

**1. 真实神经网络实现**

`network.py`不是伪代码或示意，而是一个**真实可运行的两层全连接神经网络**，用纯numpy实现前向传播、反向传播、梯度下降。part3.py运行时会实际加载MNIST数据、加载预训练权重、做前向传播识别数字——你在视频中看到的"神经网络识别手写数字"不是动画模拟，是真实推理结果的可视化。

**2. 预训练权重文件**

`pretrained_weights_and_biases/`目录下的`.npy`文件是numpy数组格式的预训练权重，避免每次运行视频都重新训练网络（训练MNIST即使是小网络也需要时间）。part3直接加载这些权重，展示训练好的网络如何工作。

**3. MNIST数据加载**

`mnist_loader.py`负责加载MNIST手写数字数据集——这意味着你运行part3时，本地需要有MNIST数据文件（或脚本会自动下载）。这也让nn系列成为Videos仓库中少数依赖外部数据的系列。

### nn系列的典型代码模式

```python
# _2017/nn/part3.py 概念性示例
from manim_imports_ext import *
from _2017.nn.network import Network
from _2017.nn.mnist_loader import load_data_wrapper

class DigitRecognition(Scene):
    def construct(self):
        # 1. 加载真实数据和预训练网络
        training_data, validation_data, test_data = load_data_wrapper()
        net = Network([784, 30, 10])
        net.load_weights("pretrained_weights_and_biases/")
        
        # 2. 取一个测试数字
        digit_image, correct_label = test_data[0]
        
        # 3. 可视化像素网格（28x28）
        pixels = self.get_pixel_grid(digit_image)
        self.play(FadeIn(pixels))
        
        # 4. 可视化网络层与激活值
        network_mobject = self.get_network_mobject(net)
        self.play(ShowCreation(network_mobject))
        
        # 5. 真实前向传播，可视化激活传播过程
        activations = net.forward_pass_with_activations(digit_image)
        self.animate_activations(network_mobject, activations)
        
        # 6. 显示识别结果
        prediction = np.argmax(activations[-1])
        result_text = TexText(f"Prediction: {prediction}")
        self.play(Write(result_text))
```

### nn系列的学习价值

nn系列展示了如何把"真实运行的代码"与"动画可视化"结合起来——这对做技术类、编程类视频非常有启发：
- 动画不只是"画示意图"，可以是真实程序运行状态的可视化
- 预训练权重/预计算结果能避免每次渲染视频都重跑昂贵计算
- 把抽象算法（梯度下降、反向传播）映射为直观的几何/图形动画

## 概率系列（eop/）：reusables/共享组件模式

**位置**：`_2018/eop/`（F-065）
**特色**：这是Videos仓库中**第一个使用reusables/子目录**标准化共享组件的系列，这种模式后来被广泛采用

### eop目录结构

```
_2018/eop/
├── part1.py              # 概率第1部分
├── part2.py              # 概率第2部分
├── ...更多章节...
└── reusables/            # ✨ 系列共享组件目录（2018年开始出现的新模式）
    ├── __init__.py       # 标记为Python包
    ├── binary_option.py  # 二叉期权模型可视化
    ├── brick_row.py      # 砖块行（用于概率分布柱状图）
    ├── coin_flip_tree.py # 抛硬币概率树
    ├── dice.py           # 骰子可视化组件
    ├── histograms.py     # 直方图组件
    ├── distributions.py  # 概率分布曲线
    └── ...更多概率相关组件...
```

### reusables/模式的优势

2016年eola和2017年eoc的组件复用都是"跨文件直接导入"，但这种方式有明显问题：
- 共享组件散落在各个chapter文件中，不知道哪个组件定义在哪
- 某个组件可能被多个chapter导入，但它"属于"哪个chapter并不清晰
- 通用组件和章节特定代码混在一起

eop从2018年开始采用的`reusables/`模式完美解决了这些问题（F-065）：

**1. 集中存放，职责清晰**

所有在多个章节间复用的组件都集中放在`reusables/`目录下，每个文件是一类组件：骰子相关放`dice.py`、直方图放`histograms.py`、概率树放`coin_flip_tree.py`。你需要骰子组件就去reusables/dice.py找，不需要翻遍所有章节。

**2. 章节文件只包含章节特有的代码**

每个partN.py（或chapterN.py）只包含：
- 该章的Scene类和叙事逻辑
- 该章特有的、不会被其他章复用的组件
- 从reusables导入需要的共享组件

**3. 可发现性和可维护性大幅提升**

新加入系列开发的人，只需要看reusables/目录就能知道系列有哪些可复用的"积木块"，不需要读完所有章节代码。

**典型的eop章节文件开头**：

```python
from manim_imports_ext import *
# 从reusables导入共享组件
from _2018.eop.reusables.dice import Die, SixSidedDie
from _2018.eop.reusables.histograms import Histogram
from _2018.eop.reusables.coin_flip_tree import CoinFlipTree

class DiceProbability(Scene):
    def construct(self):
        die = SixSidedDie()
        self.play(RollDie(die))
        # ...使用reusables组件构建叙事...
```

### reusables/模式的演进意义

`reusables/`目录的出现标志着Videos仓库从"个人代码堆积"向"可维护的内容工程"演进——这是真实项目自然演化的典型案例（洞察I-01）：
- 2015年：最早的单文件视频，无复用
- 2016年eola：开始有跨章导入，但共享组件散落在各文件
- 2017年eoc：大量多继承组合，组件复用更多但组织方式仍不清晰
- 2018年eop：reusables/模式出现，共享组件有了专门的目录
- 2019年及之后：reusables/成为标准模式，所有新系列都采用这种组织方式

## 系列项目的common模式总结

对比四大系列，我们可以总结出3Blue1Brown系列项目的通用组织模式：

### 1. 文件命名规范（F-056）

| 内容类型 | 命名规范 | 示例 |
|---------|---------|------|
| 系列正篇章节 | `chapterN.py` 或 `partN.py`（按数字顺序编号） | `chapter1.py`、`part3.py` |
| 系列共享组件 | `reusables/`子目录，按功能分文件 | `reusables/dice.py`、`reusables/histograms.py` |
| 补充/脚注视频 | `footnote.py`、`supplements.py` | `footnote.py`、`footnote2.py` |
| 独立单集视频 | 描述性主题命名 | `fourier.py`、`bell.py`、`crypto.py` |
| 缩略图场景 | 类名以`Thumbnail`结尾 | `Eoc1Thumbnail`、`EolaChapter4Thumbnail` |

### 2. 章间共享的典型内容

系列中通常在章节间共享的内容包括：
- **自定义Mobject子类**：该系列主题领域的专用图形（如线性代数的向量/网格、概率的骰子/硬币、微积分的圆环/黎曼矩形）
- **自定义Scene基类**：封装该系列通用的场景设置（如eola的LinearTransformationScene自动带网格和基向量）
- **自定义Animation类**：该系列特有的动画效果（如神经网络中激活值传播动画、骰子滚动动画）
- **配色方案常量**：系列统一的颜色编码（如向量i用什么颜色、矩阵列用什么颜色）
- **工具函数**：该领域常用的几何/数学计算辅助函数

### 3. 从once_useful_constructs到系列reusables

组件沉淀有两层：
- **跨系列通用组件**：沉淀到根目录的`once_useful_constructs/`，如`graph_scene.py`、`linear_algebra.py`、`reconfigurable_scene.py`——多个系列都可能用到
- **系列内专用组件**：放在系列目录下的`reusables/`——如eop的骰子/硬币只在概率系列用，eoc的圆环展开只在微积分系列用

"先用再抽"是核心原则：组件最开始总是在某一章的代码里定义，发现其他章也需要时才抽出来放到reusables；发现其他系列也需要时才进一步抽到once_useful_constructs。**不要过早抽象**。

## 如何研读一个系列的源码

拿到一个不熟悉的系列，按以下顺序研读效率最高：

### Step 1：先看目录结构，了解系列规模

先`ls`系列目录：
- 有多少chapter/part文件？
- 有没有reusables目录？
- 有没有额外的数据文件或资源？

这能让你对系列的规模和组织方式有个整体概念。

### Step 2：如果有reusables，先读reusables（F-065）

如果系列有`reusables/`目录，**先读这里**！这是系列的"积木块工具箱"：
- 看每个文件定义了哪些Mobject类
- 看基类Scene提供了什么通用功能
- 理解这个系列的视觉语言由哪些基本元素构成

先知道"有哪些积木可用"，再看用积木搭出来的房子（各章节）就容易理解多了。

### Step 3：读第一章的基类Scene

第一章通常会定义整个系列使用的基础Scene基类（如eola的LinearTransformationScene），理解这个基类的setup做了什么、提供了哪些便捷方法，后面所有章节都是在这个基类上构建的。

### Step 4：选一个你熟悉的主题章节深入读

选一个你对视频内容印象最深的章节（比如你最懂行列式就先看chapter4.py，最懂神经网络就先看nn/part3.py）：
1. 先读construct()，看叙事子方法调用顺序，理解整章结构
2. 再逐个读子方法，看每个段落的动画实现
3. 遇到从reusables或其他章导入的类，跳过去看定义
4. 思考"这个动画效果是怎么做出来的？"

### Step 5：找跨章节的动画模式共性

读了2-3个章节后，停下来总结：
- 这个系列常用的动画模式有哪些？
- 配色方案有没有统一规律？
- 讲解新概念时遵循什么固定叙事节奏？

这些跨章节的共性模式，才是比单个章节实现更有价值的"方法论"——你学会了这些模式，就能用同样的风格做自己的同主题视频。

## 版本兼容性：读老代码学思想，写新代码用新API

四大经典系列都使用老版本Manim API（F-073），研读时遇到以下写法请自动映射：

| 老代码中常见写法 | 现代ManimGL等价写法 | 出现在哪些系列 |
|-----------------|-------------------|--------------|
| `CONFIG = { ... }` | 直接类属性 | 所有系列（eola/eoc/nn/eop全是） |
| `ShowCreation(mob)` | `Create(mob)` | 所有系列 |
| `OldTex(...)`/`OldTexText(...)` | `Tex(...)`/`TexText(...)` | 所有系列 |
| `mob.generate_target()`<br>`mob.target.xxx`<br>`self.play(MoveToTarget(mob))` | `self.play(mob.animate.xxx)` | eoc/nn中大量使用 |
| `FadeInFromDown(mob)` | `FadeIn(mob, UP)` | eola/eoc |
| `from once_useful_constructs.graph_scene import *` | 使用现代Axes/CoordinateSystem | eoc等使用GraphScene的系列 |
| `ReconfigurableScene` | 无直接等价，需手动实现状态切换动画 | eoc系列 |

**再次强调**：老代码的价值不在于API写法——API会过时，但以下东西永远不会过时：
- 如何把抽象数学概念转化为可视动画
- 如何拆分叙事段落控制节奏
- 如何设计可复用的场景基类和组件
- 如何在系列中保持视觉风格统一
- 如何用即时反馈的工作流快速迭代视觉效果

## 相关概念

- [00 Videos 仓库总览与入门](/concepts/00-videos-overview.md)
- [02 自定义 Scene 基类体系](/concepts/02-custom-scenes.md)
- [03 视频Scene代码结构与叙事模式](/concepts/03-video-structure-pattern.md)
- [04 checkpoint_paste 交互式开发工作流](/concepts/04-checkpoint-paste-workflow.md)
- [信源：代表性系列目录导航](/references/representative-series.md)
- [信源：自定义模块索引](/references/custom-modules-index.md)
- [ManimGL 知识包首页](/viz/3b1b/manim/index.md)
