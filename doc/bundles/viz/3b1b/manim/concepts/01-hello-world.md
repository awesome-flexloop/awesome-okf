---
type: Concept
title: 第一个 Scene：Hello World
description: Scene 是 ManimGL 动画的基本编排单元，通过 construct() 方法定义动画序列，play/add/wait 构成基础动画操作原语。
tags: [manimgl, scene, hello-world, construct, lifecycle, animation-basics]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: ManimGL 源码事实采集
---

# 第一个 Scene：Hello World

Scene（场景）是 ManimGL 动画的基本编排单元，所有动画内容都在 Scene 子类的 `construct()` 方法中定义。Scene 类定义在 `manimlib/scene/scene.py` 第52行，继承自 `object`（F-043），负责管理 mobject 生命周期、动画播放、相机控制和渲染循环。理解 Scene 的生命周期和基础 API 是编写 ManimGL 动画的第一步。

## Scene 类结构

Scene 类定义了一系列类属性控制默认行为（F-044）：

| 类属性 | 默认值 | 说明 |
|--------|--------|------|
| `random_seed` | `0` | 随机数种子，保证可复现性 |
| `pan_sensitivity` | `0.5` | 平移灵敏度（鼠标拖拽时） |
| `scroll_sensitivity` | `20` | 缩放灵敏度（滚轮时） |
| `drag_to_pan` | `True` | 是否允许鼠标拖拽平移 |
| `max_num_saved_states` | `50` | 最大保存状态数（用于撤销/重做） |
| `samples` | `0` | 多重采样数（抗锯齿） |
| `default_frame_orientation` | `(0, 0)` | 默认帧朝向（欧拉角，单位度） |

Scene 在 `__init__` 方法中接收多个配置参数（F-045）：`window`、`camera_config`、`file_writer_config`、`skip_animations`、`always_update_mobjects`、`start_at_animation_number`、`end_at_animation_number` 等。其中 `camera_config` 和 `file_writer_config` 通过 `merge_dicts_recursively` 三层合并：全局默认 → 子类默认配置 → 实例化配置（F-046），这种三层合并模式与配置系统的设计保持一致。

Scene 初始化时创建 `self.camera: Camera` 实例和 `self.frame: CameraFrame`（即 `self.camera.frame`）（F-047），CameraFrame 作为特殊 Mobject 加入场景，z_index=-1 保证在最底层（对应洞察 I-03：相机本身是 Mobject）。

## Scene 生命周期

Scene 提供了三个生命周期方法（F-051）：
- `setup()`：空实现，子类可重写用于初始化资源
- `construct()`：空实现，子类必须重写，所有动画序列在此定义
- `tearDown()`：调用 `stop_skipping()`、`file_writer.finish()`、`window.destroy()` 清理资源

`run()` 方法是 Scene 的执行入口，流程如下（F-050）：

```
1. 设置 virtual_animation_start_time 和 real_animation_start_time
2. 调用 file_writer.begin() 开始写入
3. 调用 setup() → 子类初始化
4. 调用 construct() → 执行动画序列（核心）
5. 调用 interact() → 进入交互模式（如窗口存在）
6. 捕获 EndScene 和 KeyboardInterrupt 异常
7. 调用 tearDown() → 清理资源
```

`interact()` 方法在 window 存在时进入交互循环（F-052），反复调用 `update_frame(1 / self.camera.fps)` 直到窗口关闭，允许用户在动画播放完成后继续通过鼠标/键盘与场景交互。

## 帧更新循环

每一帧的更新由 `update_frame(dt, force_draw)` 方法驱动，分为三步（F-053）：

```
update_frame(dt, force_draw)
  → increment_time(dt)           # 推进虚拟时间
  → update_mobjects(dt)          # 更新所有 mobject 状态
  → draw_frame(dt, force_draw)   # 绘制当前帧
```

`update_mobjects(dt)` 遍历 `self.mobjects` 列表，对每个 mobject 调用 `mobject.update(dt, frame_rate=self.camera.fps)`（F-055），这是 updater 机制的执行入口。

`draw_frame(dt, force_draw)` 方法执行实际渲染（F-054）：
- `skip_animations` 且非 `force_draw` 时直接返回
- 检查窗口是否关闭
- 无事件且 `dt=0` 时仅 `poll_events()` 不重绘
- 调用 `camera.capture(*self.mobjects)` 捕获所有 mobject
- 非跳过时根据虚拟时间与实际时间差 sleep 同步帧率

## 三个基础 API：play / add / wait

Scene 提供了三个最基础的动画操作原语：`add()`、`wait()` 和 `play()`。

### add(mobject)：立即添加对象

`self.add(mobject)` 将 mobject 直接添加到场景中，无动画效果，对象立即显示。这是构建静态场景或在动画序列开始前预置对象的方式。

对应的反操作是 `self.remove(mobject)`，将对象从场景中移除。

### wait(duration=1)：等待若干秒

`self.wait(duration)` 在指定时间内不做任何动画，保持当前画面。默认等待 1 秒。wait 期间帧更新循环仍在运行，updater 仍会执行，相机移动等持续动画仍会生效。

### play(*animations, ...)：播放动画

`self.play()` 是最核心的 API，接收一个或多个 Animation 对象，在默认 1 秒内同时播放这些动画。常见用法：

```python
# 播放单个动画
self.play(Transform(circle, square))

# 同时播放多个动画
self.play(
    circle.animate.shift(RIGHT),
    square.animate.set_fill(RED)
)

# 指定动画时长
self.play(Transform(circle, square), run_time=2)

# 指定缓动函数
self.play(circle.animate.scale(2), rate_func=there_and_back)
```

`mobject.animate.method()` 语法糖返回 `_AnimationBuilder` 对象（F-063），可以链式调用方法描述动画终态，这是 ManimGL 声明式动画 API 的核心。

## 完整示例：Hello Manim

下面是一个完整可运行的示例，展示从创建图形到播放动画的完整流程：

```python
from manimlib import *

class HelloManim(Scene):
    def construct(self):
        # 1. 创建一个圆形
        circle = Circle()
        circle.set_fill(BLUE, opacity=0.5)
        circle.set_stroke(BLUE_E, width=4)
        
        # 2. 添加到场景并显示 1 秒
        self.add(circle)
        self.wait(1)
        
        # 3. 创建方形，播放变换动画
        square = Square()
        square.set_fill(RED, opacity=0.5)
        self.play(Transform(circle, square), run_time=1.5)
        self.wait(0.5)
        
        # 4. 使用 animate 语法糖移动对象
        self.play(circle.animate.shift(RIGHT * 2), run_time=1)
        self.wait(0.5)
        
        # 5. 旋转并缩放
        self.play(
            circle.animate.rotate(PI / 4).scale(0.8),
            run_time=1
        )
        self.wait()
```

## 代码逐行解释

让我们逐行分析这个示例：

**1. 导入模块**

```python
from manimlib import *
```

这行利用了 ManimGL 的全量通配导入（F-003 ~ F-009），`Scene`、`Circle`、`Square`、`Transform`、`BLUE`、`BLUE_E`、`RIGHT`、`PI`、`run_time` 参数等所有需要的类和常量都直接可用，无需记住它们在哪个子模块。

**2. 定义 Scene 子类**

```python
class HelloManim(Scene):
```

所有动画都必须定义在继承自 `Scene` 的类中。类名即场景名，通过命令行指定要运行的场景。

**3. 重写 construct() 方法**

```python
def construct(self):
```

`construct()` 是动画逻辑的入口（F-051），ManimGL 在 `run()` 流程中自动调用此方法。`self` 指向 Scene 实例，通过 `self.play()`、`self.add()`、`self.wait()` 控制场景。

**4. 创建并配置圆形**

```python
circle = Circle()
circle.set_fill(BLUE, opacity=0.5)
circle.set_stroke(BLUE_E, width=4)
```

`Circle()` 创建一个圆形 VMobject 实例。`set_fill(color, opacity)` 设置填充颜色和不透明度，`set_stroke(color, width)` 设置描边颜色和线宽。`BLUE` 是中位蓝色（F-039），`BLUE_E` 是最深一级蓝色（F-038）。此时圆形只是在内存中创建，尚未加入场景。

**5. 添加对象并等待**

```python
self.add(circle)
self.wait(1)
```

`self.add(circle)` 将圆形加入 `self.mobjects` 列表（F-048），下一帧开始渲染时圆形就会出现在画面上。`self.wait(1)` 保持当前画面 1 秒。

**6. 创建方形并播放变换动画**

```python
square = Square()
square.set_fill(RED, opacity=0.5)
self.play(Transform(circle, square), run_time=1.5)
self.wait(0.5)
```

创建一个红色方形，然后通过 `Transform(circle, square)` 播放从圆形到方形的变换动画。`run_time=1.5` 指定动画时长为 1.5 秒（默认 1 秒）。Transform 会在两个对象的数据结构之间做插值（对应洞察 I-02：声明式动画三层架构）。

**7. 使用 animate 移动对象**

```python
self.play(circle.animate.shift(RIGHT * 2), run_time=1)
```

`circle.animate` 返回 `_AnimationBuilder`（F-063），链式调用 `.shift(RIGHT * 2)` 描述动画终态——圆形向右移动 2 个单位。ManimGL 自动计算从当前位置到目标位置的插值路径，在 1 秒内平滑过渡。`RIGHT` 是预定义的方向向量 `[1., 0., 0.]`（F-033）。

**8. 链式动画调用**

```python
self.play(
    circle.animate.rotate(PI / 4).scale(0.8),
    run_time=1
)
self.wait()
```

`animate` 支持链式调用多个方法，这里同时旋转 45 度（`PI/4` 弧度）并缩小到 80%。最后的 `self.wait()` 不带参数，使用默认 1 秒等待，construct() 执行完毕后自动进入交互模式。

## 运行脚本

将上述代码保存为 `hello.py`，在命令行运行：

```bash
manimgl hello.py HelloManim
```

`manimgl` 命令的第一个位置参数是 Python 文件路径，第二个位置参数是场景类名（F-013）。默认会打开实时预览窗口。常用命令行选项：

- `-w`：渲染输出为视频文件（F-014）
- `-l/-m/--hd/--uhd`：选择画质（F-016）
- `-s`：跳过动画，只保存最后一帧（F-015）
- `-o`：渲染完成后自动打开文件（F-023）
- `-e LINE_NUMBER`：在指定行插入 iPython 断点调试（F-022）

例如，渲染 1080p 视频并自动打开：

```bash
manimgl hello.py HelloManim -w --hd -o
```

完整 CLI 参数说明参见 [配置系统与 CLI 参数](/concepts/02-configuration.md) 和 [CLI 参数速查表](/references/cli-parameters-reference.md)。

## Scene 核心状态

Scene 在初始化时建立以下核心状态（F-048）：

| 状态属性 | 初始值 | 说明 |
|----------|--------|------|
| `self.mobjects` | `[self.camera.frame]` | 场景中所有 mobject 列表，初始包含相机帧 |
| `self.id_to_mobject_map` | `dict()` | ID 到 mobject 的映射，用于快速查找 |
| `self.num_plays` | `0` | 已调用 play() 的次数计数器 |
| `self.time` | `0.0` | 虚拟时间（动画时间） |
| `self.skip_time` | `0.0` | 跳过动画的累计时间 |
| `self.undo_stack` | `[]` | 撤销栈（最多 `max_num_saved_states` 层） |
| `self.redo_stack` | `[]` | 重做栈 |

交互相关状态（F-049）包括 `self.mouse_point`（鼠标位置点）、`self.mouse_drag_point`（拖拽位置点）、`self.hold_on_wait`（presenter 模式下 wait 时暂停）、`self.quit_interaction`（退出交互标志）。

## 相关概念

- [00 ManimGL 简介与安装](/concepts/00-introduction.md)
- [02 配置系统与 CLI 参数](/concepts/02-configuration.md)
- [03 Mobject：数学对象基类](/concepts/03-mobject-fundamentals.md)
- [05 动画基础](/concepts/05-animation-basics.md)
- [06 Transform 深度解析](/concepts/06-transform-deep-dive.md)
- [ManimGL CLI 参数速查表](/references/cli-parameters-reference.md)
