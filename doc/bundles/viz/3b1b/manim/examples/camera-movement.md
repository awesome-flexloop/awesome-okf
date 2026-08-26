---
type: Example
title: 相机运动
description: 学习操控 self.frame 实现镜头推拉摇移：平移(shift)、缩放(scale)、旋转(rotate)、跟随移动对象、2D/3D 视角切换，复现 3Blue1Brown 视频中流畅的镜头语言。
tags: [manimgl, camera, camera-frame, zoom, pan, rotate, 3d, perspective, frame, cinematography]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: ManimGL 源码事实采集
  - id: concepts-07
    resource: /concepts/07-camera-and-frame.md
    title: 相机与视角控制
  - id: concepts-03
    resource: /concepts/03-mobject-fundamentals.md
    title: Mobject：数学对象基类
  - id: concepts-08
    resource: /concepts/08-constants-and-colors.md
    title: 常量系统与颜色体系
  - id: source-code
    resource: /references/manimgl-source-code.md
    title: ManimGL 源码登记
---

# 相机运动

本示例演示 ManimGL 相机系统的核心操作。ManimGL 最优雅的设计之一是**相机本身也是 Mobject**——CameraFrame 继承自 Mobject（F-087），你可以像操作普通图形一样移动、缩放、旋转相机（F-095），无需学习独立的相机 API。通过 `self.frame` 引用相机帧（F-047），你可以复现 3Blue1Brown 视频中常见的镜头推拉、平移、环绕、3D 视角切换等效果。

## 完整代码

```python
from manimlib import *

class CameraMovement(Scene):
    def construct(self):
        # ========== 第一部分：创建参考场景 ==========
        # 创建一个网格平面作为参照物
        grid = NumberPlane()
        grid.set_stroke(GREY_C, width=1)
        title = Text("相机运动演示", font_size=36)
        title.to_edge(UP)
        title.is_fixed_in_frame = True
        self.add(grid, title)

        # 创建几个不同颜色的圆形作为参考对象
        circles = VGroup()
        colors = [BLUE, GREEN, RED, YELLOW, PURPLE]
        positions = [
            ORIGIN,
            LEFT * 4 + UP * 2,
            RIGHT * 4 + UP * 2,
            LEFT * 4 + DOWN * 2,
            RIGHT * 4 + DOWN * 2,
        ]
        for color, pos in zip(colors, positions):
            c = Circle(radius=0.5)
            c.set_fill(color, opacity=0.6)
            c.set_stroke(width=2)
            c.move_to(pos)
            circles.add(c)

        for i, c in enumerate(circles):
            self.play(FadeIn(c, scale=0.5), run_time=0.3)
        self.wait(0.5)

        # ========== 第二部分：镜头推拉（缩放） ==========
        subtitle = Text("镜头推进 (scale in)", font_size=24, color=YELLOW)
        subtitle.to_corner(UL)
        subtitle.is_fixed_in_frame = True
        self.play(FadeIn(subtitle, shift=RIGHT * 0.3), run_time=0.5)

        # 推进：frame.scale(0.5) 让帧变小 = 物体看起来变大（焦距拉近）
        self.play(self.frame.animate.scale(0.5), run_time=2, rate_func=smooth)
        self.wait(0.5)

        # 拉远：frame.scale(2) 恢复原视野
        self.play(
            Transform(subtitle, Text("镜头拉远 (scale out)", font_size=24, color=YELLOW).to_corner(UL)),
            run_time=0.5
        )
        self.play(self.frame.animate.scale(2), run_time=2, rate_func=smooth)
        self.wait(0.5)

        # ========== 第三部分：镜头平移 ==========
        self.play(
            Transform(subtitle, Text("镜头平移 (shift)", font_size=24, color=YELLOW).to_corner(UL)),
            run_time=0.5
        )

        # 相机向右移动（视觉效果：场景向左移动）
        self.play(self.frame.animate.shift(RIGHT * 3), run_time=1.5)
        self.wait(0.3)

        # 相机向左上移动
        self.play(self.frame.animate.shift(LEFT * 6 + UP * 2), run_time=2)
        self.wait(0.3)

        # 回到中心
        self.play(self.frame.animate.move_to(ORIGIN), run_time=1.5)
        self.wait(0.5)

        # ========== 第四部分：聚焦到特定对象 ==========
        self.play(
            Transform(subtitle, Text("聚焦目标 (move_to + scale)", font_size=24, color=YELLOW).to_corner(UL)),
            run_time=0.5
        )

        # 平滑推进到左上角的绿色圆形
        target = circles[1]
        self.play(
            self.frame.animate.scale(0.4).move_to(target),
            run_time=2,
            rate_func=smooth
        )
        self.wait(0.8)

        # 快速跳到右下角
        target2 = circles[4]
        self.play(
            self.frame.animate.scale(1 / 0.4).move_to(target2).scale(0.4),
            run_time=2
        )
        self.wait(0.8)

        # 回到全景
        self.play(
            self.frame.animate.scale(1 / 0.4).move_to(ORIGIN),
            run_time=2
        )
        self.wait(0.5)

        # ========== 第五部分：跟随移动对象 ==========
        self.play(
            Transform(subtitle, Text("跟随移动对象", font_size=24, color=YELLOW).to_corner(UL)),
            run_time=0.5
        )

        # 创建一个移动的圆点
        moving_dot = Dot(radius=0.2, color=GOLD)
        moving_dot.move_to(LEFT * 6)
        self.play(FadeIn(moving_dot), run_time=0.5)

        # 圆点向右移动，相机同步跟随
        self.play(
            moving_dot.animate.shift(RIGHT * 12),
            self.frame.animate.shift(RIGHT * 12),
            run_time=4,
            rate_func=linear
        )
        self.wait(0.5)

        # 回到中心，移除移动圆点
        self.play(
            self.frame.animate.move_to(ORIGIN),
            FadeOut(moving_dot),
            run_time=1.5
        )
        self.wait(0.3)

        # ========== 第六部分：2D 旋转 ==========
        self.play(
            Transform(subtitle, Text("2D 旋转 (rotate, axis=OUT)", font_size=24, color=YELLOW).to_corner(UL)),
            run_time=0.5
        )

        # 绕 Z 轴（垂直屏幕）旋转 45 度
        self.play(self.frame.animate.rotate(PI / 6), run_time=1.5)
        self.wait(0.5)

        # 继续旋转到 90 度
        self.play(self.frame.animate.rotate(PI / 6), run_time=1)
        self.wait(0.3)

        # 旋转回正
        self.play(self.frame.animate.rotate(-PI / 3), run_time=1.5)
        self.wait(0.5)

        # ========== 第七部分：切换到 3D 视角 ==========
        self.play(FadeOut(subtitle), run_time=0.5)

        # 清除 2D 参考对象
        self.play(
            FadeOut(grid),
            FadeOut(circles),
            run_time=0.8
        )

        # 使用 reorient 设置 3D 视角（角度单位是度）
        self.frame.reorient(phi_degrees=-25, theta_degrees=65)

        # 创建 3D 坐标轴和立方体
        axes = ThreeDAxes()
        cube = Cube()
        cube.set_fill(BLUE, opacity=0.4)
        cube.set_stroke(BLUE_E, width=2)
        cube.scale(1.5)

        sphere = Sphere(radius=0.8)
        sphere.set_fill(RED, opacity=0.5)
        sphere.set_stroke(RED_E, width=1)
        sphere.shift(RIGHT * 3 + UP)

        self.play(ShowCreation(axes), run_time=1.5)
        self.play(FadeIn(cube), FadeIn(sphere), run_time=1)
        self.wait(0.5)

        # ========== 第八部分：3D 环绕旋转 ==========
        subtitle3d = Text("3D 环绕旋转", font_size=24, color=YELLOW)
        subtitle3d.to_corner(UL)
        subtitle3d.is_fixed_in_frame = True
        self.play(FadeIn(subtitle3d, shift=RIGHT * 0.3), run_time=0.5)

        # 相机绕 Y 轴旋转一圈（线性匀速），呈现环绕效果
        self.play(
            self.frame.animate.rotate(TAU, axis=UP),
            run_time=6,
            rate_func=linear
        )
        self.wait(0.5)

        # 推进查看立方体细节
        self.play(
            self.frame.animate.scale(0.5).move_to(cube),
            run_time=2
        )
        self.wait(0.5)

        # 再绕 Y 轴旋转半圈看不同面
        self.play(
            self.frame.animate.rotate(PI, axis=UP),
            run_time=3,
            rate_func=linear
        )
        self.wait(0.5)

        # 拉远并回到 2D 俯视
        self.play(
            self.frame.animate.scale(2).reorient(0, 0).move_to(ORIGIN),
            FadeOut(axes),
            FadeOut(cube),
            FadeOut(sphere),
            FadeOut(subtitle3d),
            run_time=2
        )
        self.wait(0.5)

        # ========== 结束 ==========
        end_text = Text("相机运动演示完成", font_size=36, color=GREEN)
        self.play(FadeIn(end_text, scale=1.5), run_time=1)
        self.wait(1)
```

## 代码分段解释

### Scene 初始化与固定帧文字

```python
class CameraMovement(Scene):
    def construct(self):
        grid = NumberPlane()
        title = Text("相机运动演示", font_size=36)
        title.to_edge(UP)
        title.is_fixed_in_frame = True
```

- `NumberPlane()` 创建坐标网格平面，作为场景参照物，方便观察相机运动效果。
- `title.is_fixed_in_frame = True` 是关键设置（F-058 中 Mobject 初始化参数，F-07 概念文档）：将标题固定在相机帧上，不随相机移动/旋转/缩放而变化。这是 UI 元素（标题、标签、图例）的标准做法——它们始终"粘"在屏幕上。

### 第一部分：镜头推拉（scale）

```python
self.play(self.frame.animate.scale(0.5), run_time=2, rate_func=smooth)
self.play(self.frame.animate.scale(2), run_time=2, rate_func=smooth)
```

`self.frame` 即 CameraFrame 实例（F-047），继承自 Mobject，因此支持所有 Mobject 的变换方法（F-095）。**理解 scale 的方向很重要**：
- `frame.scale(0.5)`：帧尺寸缩小到原来的一半 → 同样的 fovy 下，物体看起来变大（焦距拉近，镜头推进）
- `frame.scale(2)`：帧尺寸放大到 2 倍 → 视野变宽，物体看起来变小（焦距拉远，镜头拉远）

这与直觉相反——scale 值越小，"放大倍数"越大。可以记忆为：scale 控制的是"取景框大小"，框越小看到的内容越少（物体越大）。

### 第二部分：镜头平移（shift）

```python
self.play(self.frame.animate.shift(RIGHT * 3), run_time=1.5)
self.play(self.frame.animate.shift(LEFT * 6 + UP * 2), run_time=2)
self.play(self.frame.animate.move_to(ORIGIN), run_time=1.5)
```

- `frame.shift(RIGHT * 3)`：相机向右移动 3 个单位。**注意方向相反**——相机右移，视觉效果是场景向左移动（F-07 概念文档）。这与真实摄像机一致：你向右走，画面中的景物看起来向左。
- `shift(LEFT * 6 + UP * 2)`：方向向量支持加法组合（F-033），同时向左上移动。
- `move_to(ORIGIN)`：绝对定位，将相机中心移回原点（屏幕中心），恢复全景。

### 第三部分：聚焦到特定对象

```python
target = circles[1]
self.play(
    self.frame.animate.scale(0.4).move_to(target),
    run_time=2,
    rate_func=smooth
)
```

animate 语法糖支持链式调用（F-063），同时进行缩放和平移：`scale(0.4)` 推进放大，`move_to(target)` 将相机中心移到目标对象位置。两个变换同时发生，创造出"镜头平滑推进聚焦"的电影感效果。这是 3Blue1Brown 视频中最常用的镜头语言之一。

切换焦点时先恢复原缩放再推进到新目标：
```python
self.play(
    self.frame.animate.scale(1 / 0.4).move_to(target2).scale(0.4),
    run_time=2
)
```

这里链式调用了三个操作：先 scale 回 1.0（`1/0.4`），再 move_to 新目标，再 scale(0.4) 推进。由于 animate 只关心终态，最终效果是平滑地从第一个目标跳到第二个目标并保持放大。

### 第四部分：跟随移动对象

```python
self.play(
    moving_dot.animate.shift(RIGHT * 12),
    self.frame.animate.shift(RIGHT * 12),
    run_time=4,
    rate_func=linear
)
```

在同一个 `play()` 中同时动画化对象和相机：圆点向右移动 12 个单位，相机也向右移动相同距离。因为两者移动距离相同，圆点在画面中始终保持相对位置不变（就像跟踪摄影），而背景（网格和其他圆形）在画面中滑过，创造出"跟拍"效果。使用 `rate_func=linear` 保持匀速运动。

### 第五部分：2D 旋转

```python
self.play(self.frame.animate.rotate(PI / 6), run_time=1.5)
self.play(self.frame.animate.rotate(-PI / 3), run_time=1.5)
```

`frame.rotate(angle, axis=OUT)` 绕指定轴旋转相机（F-095）。默认轴是 `OUT`（即 `[0,0,1]`，从屏幕指向观众的方向），这是 2D 旋转的默认轴。旋转 `PI/6`（30度）后画面倾斜，再旋转 `-PI/3`（-60度）回到 -30度，最后旋转 `-PI/3` 回到 0 度。

CameraFrame 的 rotate 方法内部使用四元数乘法复合旋转（F-095），避免万向锁问题。

### 第六部分：切换到 3D 视角

```python
self.frame.reorient(phi_degrees=-25, theta_degrees=70)
```

`reorient(theta_degrees, phi_degrees, gamma_degrees, center, height)` 是设置相机朝向的快捷方法（F-097），**角度参数单位是度**（不是弧度）：
- `phi_degrees`：俯仰角，-25° 表示相机略微向下俯视
- `theta_degrees`：方位角，70° 表示从斜侧方观察（0° 是正面，90° 是正侧面）

这与 Scene 的 `default_frame_orientation = (-30, 70)` 类似（F-044），直接在运行时设置 3D 视角。reorient 内部调用 `set_euler_angles`（F-096），使用 z-x-z 欧拉角约定。

3D 对象：
```python
cube = Cube()
cube.set_fill(BLUE, opacity=0.4)
sphere = Sphere(radius=0.8)
sphere.shift(RIGHT * 3 + UP)
```

`Cube()` 和 `Sphere()` 是 three_dimensions 模块导出的 3D 几何体（F-006），在 3D 视角下可以看到立体感。

### 第七部分：3D 环绕旋转

```python
self.play(
    self.frame.animate.rotate(TAU, axis=UP),
    run_time=6,
    rate_func=linear
)
```

绕 `UP` 轴（Y轴）旋转 `TAU`（即 2π，360度）（F-036），相机围绕场景旋转一整圈。使用 `rate_func=linear` 匀速旋转，创造出平滑的环绕展示效果——这是 3Blue1Brown 展示 3D 几何体时的经典镜头。注意 3D 旋转时轴是 `UP` 而非 `OUT`，因为我们要绕竖直轴旋转（水平环绕）。

### 第八部分：回到 2D

```python
self.play(
    self.frame.animate.scale(2).reorient(0, 0).move_to(ORIGIN),
    ...
    run_time=2
)
```

通过 `reorient(0, 0)` 恢复默认 2D 俯视角度（theta=0, phi=0），同时 scale 回正常大小并 move_to 原点，一气呵成回到初始状态。animate 链式调用让多个相机参数同时恢复，过渡自然。

## 运行说明

1. 将代码保存为 `camera_movement.py`
2. 运行命令：

```bash
manimgl camera_movement.py CameraMovement
```

3. 预览窗口会按顺序播放 8 个部分的相机运动演示，总时长约 40 秒。

渲染为视频文件（推荐 1080p 或更高画质以看清 3D 效果）：

```bash
manimgl camera_movement.py CameraMovement -w --hd
```

交互模式提示：动画播放结束后，你可以手动操控相机：
- 鼠标拖拽：平移相机（drag_to_pan=True，F-044）
- 鼠标滚轮：缩放相机
- 键盘快捷键：撤销/重做

## 预期效果

动画按 8 个段落依次播放：

1. **场景建立**：灰色坐标网格淡入，"相机运动演示"标题固定在顶部；5 个不同颜色的圆形依次出现在中心和四角位置。
2. **镜头推拉**：镜头平滑推进（scale 0.5），中心蓝色圆形变大、视野变窄；然后拉远（scale 2）恢复全景。
3. **镜头平移**：相机向右移动（场景向左滑动），再向左上移动，最后平滑回到中心。
4. **聚焦对象**：镜头推进并移动到左上角绿色圆形（特写效果），然后平滑切换到右下角紫色圆形，最后回到全景。
5. **跟随对象**：一个金色圆点从左向右匀速移动，相机同步跟随（圆点保持在画面中，背景滑过），最后回到中心。
6. **2D 旋转**：整个画面绕中心倾斜 30°，再继续倾斜到 60°，最后旋转回正。
7. **3D 切换**：2D 网格和圆形淡出，相机通过 reorient 切换到 3D 斜俯视角度；3D 坐标轴、蓝色半透明立方体和红色球体出现。
8. **3D 环绕**：相机绕 Y 轴匀速旋转一整圈（TAU=360°），立方体和球体从各个角度展现；镜头推进到立方体特写，再旋转半圈看不同面；最后拉远并平滑回到 2D 俯视图，显示"相机运动演示完成"。

固定在帧上的标题和副标题始终保持在屏幕左上角/顶部，不受相机运动影响。

## 相关概念

- [07 相机与视角控制](/concepts/07-camera-and-frame.md) — CameraFrame 作为 Mobject 的统一抽象、四元数旋转、reorient 欧拉角、视图矩阵、2D/3D 切换、is_fixed_in_frame
- [03 Mobject：数学对象基类](/concepts/03-mobject-fundamentals.md) — shift/scale/rotate/move_to 几何变换方法、animate 链式语法糖、family 机制
- [05 动画基础](/concepts/05-animation-basics.md) — run_time、rate_func（smooth/linear 等）、self.play() 多动画同时播放
- [08 常量系统与颜色体系](/concepts/08-constants-and-colors.md) — 方向向量（UP/RIGHT/OUT 等）、角度常量（PI/TAU/DEG）、颜色常量
