---
type: Concept
title: 常量系统与颜色体系
description: ManimGL 常量模块动态计算帧尺寸和分辨率，提供方向向量系统、角度常量和五级分级颜色体系，默认颜色从配置读取支持自定义。
tags: [manimgl, constants, colors, coordinate-system, direction-vectors, color-palette, 3b1b-colors]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: ManimGL 源码事实采集
  - id: config
    resource: /concepts/02-configuration.md
    title: 配置系统与 CLI 参数
---

# 常量系统与颜色体系

常量模块 `manimlib/constants.py` 定义了 ManimGL 中所有全局可用的常量，包括帧尺寸、方向向量、角度常量、颜色常量等（F-031~F-042）。这些常量通过 `from manimlib.constants import *` 在入口模块通配导入（F-003），编写动画脚本时可以直接使用，无需导入额外模块。ManimGL 的常量系统有一个重要特点——**帧尺寸等常量是从配置动态计算的**，而非硬编码值。

## 分辨率与帧尺寸动态计算

ManimGL 的帧尺寸常量不是硬编码的，而是在模块导入时从配置动态计算得出（F-031、F-032）。这是为了支持不同画质设置下自动调整坐标映射。

### 分辨率常量

```python
# F-031：从配置读取默认分辨率
DEFAULT_RESOLUTION = manim_config.camera.resolution  # 元组 (width, height)
DEFAULT_PIXEL_WIDTH, DEFAULT_PIXEL_HEIGHT = DEFAULT_RESOLUTION
```

分辨率受 CLI 参数 `-l`/`-m`/`--hd`/`--uhd` 影响（F-016）：
- `-l`（low_quality）：480p，854×480
- `-m`（medium_quality）：720p，1280×720
- 默认（无画质参数）：1080p，1920×1080
- `--hd`：1080p，1920×1080
- `--uhd`：4K，3840×2160

### 帧尺寸常量

基于分辨率和配置中的 `frame_height`，动态计算帧坐标空间尺寸（F-032）：

```python
ASPECT_RATIO = DEFAULT_PIXEL_WIDTH / DEFAULT_PIXEL_HEIGHT  # 宽高比，16:9 约为 1.777
FRAME_HEIGHT = manim_config.camera.frame_height           # 帧高度，从配置读取
FRAME_WIDTH = FRAME_HEIGHT * ASPECT_RATIO                 # 帧宽度 = 高 × 宽高比
FRAME_SHAPE = (FRAME_WIDTH, FRAME_HEIGHT)                 # (宽, 高) 元组
FRAME_Y_RADIUS = FRAME_HEIGHT / 2                         # 半高
FRAME_X_RADIUS = FRAME_WIDTH / 2                          # 半宽
```

默认 FRAME_HEIGHT 为 8.0 个单位，因此默认 FRAME_WIDTH ≈ 14.22 个单位（16:9 比例）。这意味着在 Manim 的坐标空间中，从屏幕顶部到底部是 8 个单位，从左到右约 14.22 个单位。

### 帧坐标 vs 屏幕坐标

理解这两种坐标的区别很重要：

| 坐标类型 | 单位 | 原点 | 范围 | 用途 |
|---------|------|------|------|------|
| **帧坐标**（世界坐标） | Manim 单位 | 屏幕中心 ORIGIN | x: [-7.11, 7.11], y: [-4, 4]（默认） | 对象定位、变换、动画 |
| **屏幕坐标**（像素） | 像素 | 左上角或中心 | 依分辨率而定（如 1920×1080） | 窗口、视频输出、像素级操作 |

```
帧坐标（Manim 世界，固定数学空间）
┌─────────────────────────────┐ y=+4 (TOP)
│                             │
│         UP (0,1,0)          │
│          ↑                  │
│ LEFT ←─ ORIGIN ─→ RIGHT     │ x 从 -FRAME_X_RADIUS 到 +FRAME_X_RADIUS
│          ↓                  │
│         DOWN (0,-1,0)       │
│                             │
└─────────────────────────────┘ y=-4 (BOTTOM)
x=-FRAME_X_RADIUS          x=+FRAME_X_RADIUS
```

所有 Mobject 的 `shift()`、`move_to()`、`scale()` 等方法都使用帧坐标。`FRAME_WIDTH` 和 `FRAME_HEIGHT` 会随画质设置变化吗？实际上它们只受 `frame_height` 配置影响——不同画质只改变像素分辨率，不改变帧坐标空间的大小。这保证了同样的动画代码在不同画质下对象的相对位置完全一致。

## 方向向量系统

constants.py 定义了一套标准化的三维方向向量，都是 numpy 数组，用于指定移动方向、旋转轴、位置偏移等（F-033）。

### 基本方向向量

| 常量 | 值 | 方向 | 说明 |
|------|------|------|------|
| `ORIGIN` | `[0., 0., 0.]` | 原点 | 屏幕中心 |
| `UP` | `[0., 1., 0.]` | Y轴正方向 | 屏幕上方 |
| `DOWN` | `[0., -1., 0.]` | Y轴负方向 | 屏幕下方 |
| `RIGHT` | `[1., 0., 0.]` | X轴正方向 | 屏幕右侧 |
| `LEFT` | `[-1., 0., 0.]` | X轴负方向 | 屏幕左侧 |
| `OUT` | `[0., 0., 1.]` | Z轴正方向 | 从屏幕指向观众 |
| `IN` | `[0., 0., -1.]` | Z轴负方向 | 从观众指向屏幕 |
| `X_AXIS` | `RIGHT` | X轴 | 同 RIGHT |
| `Y_AXIS` | `UP` | Y轴 | 同 UP |
| `Z_AXIS` | `OUT` | Z轴 | 同 OUT |

这些向量可以直接进行标量乘法和加法运算：

```python
circle.shift(RIGHT * 2)           # 右移 2 个单位
circle.shift(UP * 1.5 + LEFT)     # 上移 1.5，左移 1
circle.move_to(ORIGIN)            # 回到中心
```

### 对角线方向缩写

基于基本方向向量组合，定义了四个对角线常量（F-034）：

| 常量 | 等价计算 | 位置 |
|------|---------|------|
| `UL` | `UP + LEFT` | 左上角 |
| `UR` | `UP + RIGHT` | 右上角 |
| `DL` | `DOWN + LEFT` | 左下角 |
| `DR` | `DOWN + RIGHT` | 右下角 |

```python
circle.to_corner(UL)   # 移动到左上角
title.to_corner(UR)    # 标题放在右上角
```

### 边缘位置常量

基于帧半径定义了四个边缘中点位置（F-035）：

| 常量 | 计算 | 位置 |
|------|------|------|
| `TOP` | `FRAME_Y_RADIUS * UP` | 上边缘中点 |
| `BOTTOM` | `FRAME_Y_RADIUS * DOWN` | 下边缘中点 |
| `LEFT_SIDE` | `FRAME_X_RADIUS * LEFT` | 左边缘中点 |
| `RIGHT_SIDE` | `FRAME_X_RADIUS * RIGHT` | 右边缘中点 |

```python
line = Line(LEFT_SIDE, RIGHT_SIDE)  # 贯穿屏幕的水平线
circle.to_edge(TOP)                 # 移到上边缘
```

## 角度常量

constants.py 定义了常用角度常量，避免每次手动写 `np.pi`（F-036）：

| 常量 | 值 | 说明 |
|------|------|------|
| `PI` | `np.pi` ≈ 3.14159 | π 弧度（180度） |
| `TAU` | `2 * PI` ≈ 6.28319 | 2π 弧度（360度，一整圈） |
| `DEG` | `TAU / 360` ≈ 0.01745 | 1度对应的弧度值 |
| `DEGREES` | `DEG` | DEG 的别名 |
| `RADIANS` | `1` | 弧度单位标识（值为1，无转换） |

### 使用方式

Manim 中所有角度参数（如 `rotate()` 的 angle 参数、相机 fovy）使用**弧度**为单位：

```python
circle.rotate(PI / 4)              # 旋转 45 度
circle.rotate(90 * DEGREES)        # 旋转 90 度（DEG 作为转换因子）
circle.rotate(TAU / 6)             # 旋转 60 度
self.frame.reorient(theta_degrees=70, phi_degrees=-30)  # reorient 默认用度
```

注意 `rotate()` 等方法默认接受弧度，但 `reorient()` 等某些快捷方法默认接受角度（度数），使用时需查阅对应方法文档。

## 字体样式常量

constants.py 定义了字体样式字符串常量（F-037）：

| 常量 | 值 | 说明 |
|------|------|------|
| `NORMAL` | `"NORMAL"` | 正常字体 |
| `ITALIC` | `"ITALIC"` | 斜体 |
| `OBLIQUE` | `"OBLIQUE"` | 倾斜体 |
| `BOLD` | `"BOLD"` | 粗体 |

这些常量用于 Text/Tex 等文字对象的样式设置。

## 五级颜色体系

ManimGL 采用按色系分级的颜色体系，每个色系包含 E/D/C/B/A 五个深浅级别（F-038），提供统一且协调的配色方案。这是 3Blue1Brown 视频视觉风格的核心元素之一。

### 分级规则

每个色系从 E 到 A 由深到浅：
- **E 级**（如 `BLUE_E`）：最深，用于暗部、描边
- **D 级**（如 `BLUE_D`）：深色
- **C 级**（如 `BLUE_C`）：中位色，最常用的默认色（F-039）
- **B 级**（如 `BLUE_B`）：浅色
- **A 级**（如 `BLUE_A`）：最浅，接近白色，用于高亮、填充

### 九个色系

共九个色系，每个色系有 5 个级别（F-038）：

| 色系 | 最深 | 深 | 中（默认） | 浅 | 最浅 |
|------|------|-----|-----------|-----|------|
| 蓝色 | `BLUE_E` | `BLUE_D` | **`BLUE_C`** | `BLUE_B` | `BLUE_A` |
| 青色 | `TEAL_E` | `TEAL_D` | **`TEAL_C`** | `TEAL_B` | `TEAL_A` |
| 绿色 | `GREEN_E` | `GREEN_D` | **`GREEN_C`** | `GREEN_B` | `GREEN_A` |
| 黄色 | `YELLOW_E` | `YELLOW_D` | **`YELLOW_C`** | `YELLOW_B` | `YELLOW_A` |
| 金色 | `GOLD_E` | `GOLD_D` | **`GOLD_C`** | `GOLD_B` | `GOLD_A` |
| 红色 | `RED_E` | `RED_D` | **`RED_C`** | `RED_B` | `RED_A` |
| 栗色 | `MAROON_E` | `MAROON_D` | **`MAROON_C`** | `MAROON_B` | `MAROON_A` |
| 紫色 | `PURPLE_E` | `PURPLE_D` | **`PURPLE_C`** | `PURPLE_B` | `PURPLE_A` |
| 灰色 | `GREY_E` | `GREY_D` | **`GREY_C`** | `GREY_B` | `GREY_A` |

> **注意**：灰色拼写是 `GREY`（英式拼写），不是 `GRAY`。

### 中位色别名

每个色系的 C 级（中位色）有简化别名（F-039）：

```python
BLUE = BLUE_C
TEAL = TEAL_C
GREEN = GREEN_C
YELLOW = YELLOW_C
GOLD = GOLD_C
RED = RED_C
MAROON = MAROON_C
PURPLE = PURPLE_C
GREY = GREY_C
```

这意味着直接使用 `BLUE` 等价于 `BLUE_C`，是日常编码中最常用的颜色写法。

### 其他基础颜色

除了分级颜色，还定义了白色和黑色：
- `WHITE`：白色
- `BLACK`：黑色（默认背景色）

```python
circle.set_fill(BLUE, opacity=0.5)      # 使用中位蓝填充
circle.set_stroke(BLUE_E, width=4)      # 使用深蓝描边
circle.set_color(RED_C)                  # 显式指定级别
label.set_color(YELLOW)                  # 使用中位黄
```

### 颜色选择建议

3Blue1Brown 视频的典型配色模式：
- **主要图形**：使用 C 级（如 `BLUE`、`GREEN`、`RED`）
- **描边/强调**：使用 D 级或 E 级（如 `BLUE_D`、`BLUE_E`）
- **填充/高亮**：使用 B 级或 A 级（如 `BLUE_B`、`BLUE_A`）
- **背景**：`BLACK` 或深灰色
- **文字**：`WHITE` 或 `GREY_B`/`GREY_A`

## 3B1B 经典配色方案

constants.py 定义了 3Blue1Brown 频道标志性的四色调色板（F-040）：

```python
COLORMAP_3B1B = [BLUE_E, GREEN, YELLOW, RED]
```

这四个颜色——深蓝、绿、黄、红——是 Grant Sanderson 在绝大多数视频中使用的核心配色：
- `BLUE_E`：主色调，用于主要数学对象
- `GREEN`：辅助色，用于第二个对象或正确答案
- `YELLOW`：强调色，用于高亮或重点
- `RED`：对比色，用于错误、警告或对立概念

```python
# 经典的 3b1b 配色循环使用
colors = [BLUE_E, GREEN, YELLOW, RED]
for i, dot in enumerate(dots):
    dot.set_color(colors[i % len(colors)])
```

## 配置驱动的默认颜色

ManimGL 的默认对象颜色不是硬编码的，而是从配置读取（F-041、F-042）：

| 默认颜色常量 | 默认值 | 说明 |
|-------------|--------|------|
| `DEFAULT_MOBJECT_COLOR` | `WHITE` | Mobject 默认主颜色，从配置读取 |
| `DEFAULT_LIGHT_COLOR` | `GREY_B` | 默认浅色，从配置读取 |
| `DEFAULT_VMOBJECT_STROKE_COLOR` | `GREY_A` | VMobject 默认描边颜色，从配置读取 |
| `DEFAULT_VMOBJECT_FILL_COLOR` | `GREY_C` | VMobject 默认填充颜色，从配置读取 |

这意味着你可以通过 `custom_config.yml` 或 CLI 参数修改全局默认颜色，而无需改动每个对象的颜色设置。配置中未指定时使用上述默认值。

```yaml
# custom_config.yml 中自定义默认颜色
camera:
  background_color: "#1a1a2e"  # 深蓝黑色背景
style:
  mobject_color: "#e0e0e0"     # 默认对象颜色改为浅灰
```

## 颜色使用方式

### set_color / set_fill / set_stroke

VMobject 提供三个主要颜色设置方法：

```python
# set_color：同时设置填充和描边颜色
circle.set_color(BLUE)

# set_fill：设置填充颜色和透明度
circle.set_fill(BLUE_C, opacity=0.7)
circle.set_fill("#FF5733", opacity=0.5)  # 支持十六进制

# set_stroke：设置描边颜色和宽度
circle.set_stroke(BLUE_E, width=3)
circle.set_stroke(WHITE, width=2, opacity=0.8)
```

颜色参数支持多种格式：
- Manim 颜色常量：`BLUE`、`RED_C`、`GREEN_E`
- 十六进制字符串：`"#FF0000"`、`"#3498db"`
- RGB 元组：`(255, 0, 0)` 或 `(1.0, 0.0, 0.0)`（0-1 浮点）
- colour.Color 对象：Manim 使用 `colour` 库解析颜色（F-025）

### 颜色插值与渐变

Transform 动画在颜色不同的对象之间变换时，颜色也会平滑插值过渡——从起始颜色平滑渐变到目标颜色，使用 RGBA 四通道线性插值。

VMobject 还支持渐变填充（通过 uniforms 中的 `fill_rgba_end`、`gradient_start`、`gradient_end` 参数，F-072），但渐变的具体使用方式涉及 VMobject 的高级 API，超出本概念文档范围。

## 常量导入约定

由于 `from manimlib.constants import *` 在 `__init__.py` 中已经执行（F-003），所有常量在导入 manimlib 后直接可用：

```python
from manimlib import *  # 这就足够了，UP、BLUE、PI、ORIGIN 等都已导入

class MyScene(Scene):
    def construct(self):
        circ = Circle()
        circ.set_fill(BLUE, opacity=0.5)
        circ.set_stroke(BLUE_E, width=4)
        circ.move_to(UP * 2 + RIGHT * 0.5)
        self.play(circ.animate.scale(2).rotate(PI / 4), run_time=2)
```

不需要单独 `from manimlib.constants import UP, BLUE`，通配导入已覆盖所有常量。这是 ManimGL DSL 设计的一部分（洞察 I-04）——牺牲命名空间纯净度换取脚本的极致简洁。

## 常见使用模式

### 定位对象

```python
# 四角定位
title = Text("Title")
title.to_corner(UL)

# 边缘排列
for i, color in enumerate([BLUE, GREEN, YELLOW, RED]):
    dot = Dot(color=color)
    dot.to_edge(UP)
    dot.shift(RIGHT * (i - 1.5) * 1.5)
    self.add(dot)

# 居中
circle.move_to(ORIGIN)
```

### 与 animate 配合

```python
# 从左下角移动到右上角
self.play(
    square.animate.move_to(UR).scale(1.5).set_color(GOLD),
    run_time=2,
    rate_func=smooth
)
```

### 方向向量运算

```python
# 计算两点之间方向
direction = normalize(target.get_center() - source.get_center())
self.play(source.animate.shift(direction * 3))

# 垂直方向
perpendicular = rotate_vector(direction, PI / 2)
```

## 相关概念

- [02 配置系统与 CLI 参数](02-configuration.md)
- [03 Mobject：数学对象基类](03-mobject-fundamentals.md)
- [04 VMobject 与几何图形](04-vmobject-and-geometry.md)
- [07 相机与视角控制](07-camera-and-frame.md)
