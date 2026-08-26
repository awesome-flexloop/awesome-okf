# 概念文档

ManimGL 核心架构概念，共 11 篇，按学习路径组织。

## 基础入门

* [00 ManimGL 简介与安装](00-introduction.md) — ManimGL 是 3Blue1Brown 用于制作数学动画的 Python 引擎，采用数学动画 DSL 设计，通配导入所有模块实现开箱即用。
* [01 第一个 Scene：Hello World](01-hello-world.md) — Scene 是 ManimGL 动画的基本编排单元，通过 construct() 方法定义动画序列，play/add/wait 构成基础动画操作原语。
* [02 配置系统与 CLI 参数](02-configuration.md) — ManimGL 采用三层配置递归合并机制（default_config.yml→custom_config.yml→CLI），CLI 参数覆盖画质、输出、调试等分组。

## 核心机制

* [03 Mobject：数学对象基类](03-mobject-fundamentals.md) — Mobject 是 ManimGL 核心抽象，同时承担数学对象语义和 GPU 渲染原语职责，通过 data/uniforms 双数组实现 CPU-GPU 数据统一。
* [04 VMobject 与几何图形](04-vmobject-and-geometry.md) — VMobject 继承 Mobject，以贝塞尔路径存储矢量数据，扩展 data_dtype 和 uniform_dtype 支持描边填充，是 Circle/Square/Line/Arrow 等几何类的基类。
* [05 动画基础](05-animation-basics.md) — Animation 是 ManimGL 动画系统的基类，定义了 begin→interpolate→finish 生命周期，通过 starting_mobject 状态拷贝、lag_ratio 子对象延迟、rate_func 缓动函数实现流畅插值动画。
* [06 Transform 深度解析](06-transform-deep-dive.md) — Transform 是 ManimGL 变换动画的核心，通过 starting_mobject 到 target_copy 的插值实现变形，align_data_and_family 数据对齐是初学者最易踩坑的关键点。
* [07 相机与视角控制](07-camera-and-frame.md) — CameraFrame 继承自 Mobject，相机本身是场景中的特殊对象，通过四元数 orientation 和视图矩阵实现视角变换，支持移动/旋转/缩放等与普通对象一致的操作。

## 高级主题

* [08 常量系统与颜色体系](08-constants-and-colors.md) — ManimGL 常量模块动态计算帧尺寸和分辨率，提供方向向量系统、角度常量和五级分级颜色体系，默认颜色从配置读取支持自定义。
* [09 GPU 渲染管线](09-rendering-pipeline.md) — Renderer 采用三级 GPU 优化策略：Bundling 渲染束复用绘制命令、Draw 分组合并 draw call、FrameStream 异步帧流实现流水线并行，默认开启所有优化保证流畅渲染。
* [10 更新器与交互式动画](10-updaters-and-interactivity.md) — Updater（更新器）是 ManimGL 实现每帧动态行为的核心机制，通过 always/f_always 构建器、鼠标交互、撤销重做与 iPython 断点，支持响应式动画与交互式探索。

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-hello-world
02-configuration
03-mobject-fundamentals
04-vmobject-and-geometry
05-animation-basics
06-transform-deep-dive
07-camera-and-frame
08-constants-and-colors
09-rendering-pipeline
10-updaters-and-interactivity
```
