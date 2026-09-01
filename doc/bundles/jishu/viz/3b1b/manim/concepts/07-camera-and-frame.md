---
type: Concept
title: 相机与视角控制
description: CameraFrame 继承自 Mobject，相机本身是场景中的特殊对象，通过四元数 orientation 和视图矩阵实现视角变换，支持移动/旋转/缩放等与普通对象一致的操作。
tags: [manimgl, camera, camera-frame, perspective, 3d, view-matrix, euler-angles, quaternion]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: ManimGL 源码事实采集
---

# 相机与视角控制

ManimGL 的相机系统由两个核心类组成：`Camera`（定义在 `manimlib/camera/camera.py` 第108行，F-080）负责 GPU 渲染目标管理和帧输出，`CameraFrame`（定义在 `manimlib/camera/camera_frame.py` 第25行，F-087）负责视角控制。ManimGL 相机系统最优雅的设计是——**相机本身也是 Mobject**（洞察 I-03），CameraFrame 继承自 Mobject，可以像操作普通图形对象一样移动、旋转、缩放相机，这使得 3Blue1Brown 视频中那种流畅的镜头推拉摇移成为极其自然的操作。

## Camera 类：渲染入口

Camera 类是 GPU 渲染的入口，负责管理渲染器、帧缓冲区和帧输出流。

### Camera.__init__ 参数

Camera 初始化接收以下参数（F-081）：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `window` | `None` | 预览窗口对象，存在时实时渲染到窗口 |
| `frame_config` | `{}` | CameraFrame 配置参数 |
| `resolution` | `DEFAULT_RESOLUTION` | 输出分辨率元组 `(width, height)` |
| `fps` | `30` | 帧率，每秒帧数 |
| `background_color` | `BLACK` | 背景颜色 |
| `background_opacity` | `1.0` | 背景不透明度（透明视频用） |
| `light_source_position` | `[-10, 10, 10]` | 3D 光照位置 |
| `bundle_draws` | `True` | 是否启用 Bundling 渲染束优化 |
| `draw_together` | `True` | 是否启用 Draw 分组合并优化 |
| `samples` | `0` | MSAA 多重采样数（抗锯齿） |

`background_rgba` 被转换为长度为 4 的浮点数列表 `[r, g, b, a]`（F-082）。`draw_at_window_size` 属性在 window 存在时为 True（F-083），表示渲染到窗口时使用窗口尺寸而非输出分辨率。

### Camera 初始化流程

Camera 在 `__init__` 中完成以下关键初始化：

1. **创建 CameraFrame**：通过 `init_frame(**config)` 创建 `self.frame = CameraFrame(**config)`（F-084）
2. **创建渲染器**：通过 `init_renderer()` 创建 Gpu 实例和 Renderer 实例（F-085）
3. **设置帧流**：创建 FrameStream 管理 GPU 帧到 CPU 的异步拷贝

Scene 在初始化时持有 Camera 实例和 CameraFrame 引用（F-047）：
```python
self.camera: Camera = Camera(**camera_config)
self.frame: CameraFrame = self.camera.frame
```

### at_output_resolution：输出分辨率上下文管理器

`at_output_resolution()` 是一个上下文管理器（F-086），用于在截图或写文件时临时按输出分辨率渲染而非窗口尺寸：

```python
with camera.at_output_resolution():
    camera.capture(*mobjects)
    # 此时渲染分辨率为配置的输出分辨率，而非窗口尺寸
```

进入时设置 `draw_at_window_size=False` 并 resize 渲染目标，退出时恢复原始设置。

## FrameStream：异步帧流

`FrameStream` 定义在 `manimlib/camera/camera.py` 第30行（F-078），处理 GPU 帧缓冲区到输出目标（窗口或视频编码器）的异步拷贝，采用一帧延迟策略实现 CPU-GPU 流水线并行。

### 一帧延迟流水线

FrameStream 的核心设计是保持 **一帧延迟**（behind=1）（F-079）：

1. 创建 `behind + 1 = 2` 个 GPU 缓冲区（支持 MAP_READ 的拷贝目标缓冲区）
2. 当前帧渲染完成后，将结果拷贝到"当前写入缓冲区"
3. 下一帧渲染的同时，CPU 可以读取"上一帧的缓冲区"数据
4. 双缓冲区交替使用，GPU 渲染和 CPU 读取并行执行

这种流水线设计避免了 GPU 等待 CPU 读取完成的空闲时间，是 ManimGL 流畅实时预览的关键之一。FrameStream 维护 `waiting` 列表记录待读取的缓冲区和 `asked` 计数器追踪状态。

FrameStream 的异步机制与 Renderer 的 Bundling 优化共同构成 GPU 渲染三级优化体系（洞察 I-05），详见 [09 GPU 渲染管线](09-rendering-pipeline.md)。

## CameraFrame：作为 Mobject 的相机

`CameraFrame` 继承自 Mobject（F-087），这是 ManimGL 相机系统最核心的设计洞察。相机不是"在场景外观察的眼睛"，而是"场景里的一个特殊对象"——你可以对相机做任何能对普通 Mobject 做的操作。

### z_index=-1：最底层的特殊对象

Scene 初始化时，`self.mobjects` 列表初始值为 `[self.camera.frame]`（F-048），相机帧是场景中的第一个 mobject。CameraFrame 的 `z_index` 默认值为 `-1`（F-089），这保证它在渲染时位于所有对象的最底层，不会遮挡其他物体。

### 扩展的 uniform_dtype

CameraFrame 在 Mobject 的 COMMON_UNIFORMS 基础上，扩展了两个关键 uniform 参数（F-088）：

| Uniform 字段 | 类型 | 说明 |
|-------------|------|------|
| `orientation` | `(4,)` float32 | 相机旋转四元数 (x, y, z, w) |
| `fovy` | `(1,)` float32 | 垂直视场角（Field of View Y），单位弧度 |

这两个参数是 GPU 着色器计算视图矩阵和投影矩阵的关键输入。

初始化时，`uniforms["orientation"]` 设为单位四元数（无旋转），`uniforms["fovy"]` 设为 `fovy` 参数值（默认 45°，即 `45 * DEG`）（F-090）。

### CameraFrame 初始化参数

CameraFrame `__init__` 接收以下参数（F-089）：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `frame_shape` | `FRAME_SHAPE` | 帧尺寸 `(width, height)`，从 constants 动态计算 |
| `center_point` | `ORIGIN` | 相机中心点位置 |
| `fovy` | `45 * DEG` | 垂直视场角（弧度） |
| `euler_axes` | `"zxz"` | 欧拉角旋转轴顺序 |
| `z_index` | `-1` | 渲染层级，保证在最底层 |

CameraFrame 初始化时还建立以下状态（F-091）：
- `self.default_orientation = Rotation.identity()`：默认朝向（无旋转）
- `self.view_matrix = np.identity(4)`：4x4 视图矩阵，初始为单位矩阵
- `self.id4x4 = np.identity(4)`：单位矩阵缓存
- `self.euler_axes = euler_axes`：欧拉角轴顺序

### 初始化点集

CameraFrame 初始化点集为 5 个关键点（F-092）：`[ORIGIN, LEFT, RIGHT, DOWN, UP]`，然后调用 `set_width`、`set_height`、`move_to` 将帧框定位到正确大小和位置。这 5 个点定义了相机的可视边界——在 2D 模式下你看到的"帧矩形"就是 CameraFrame 的可视化表现。

在交互式预览中，你可以看到这个帧边框（通常是灰色虚线），它代表当前相机可见的区域。

## orientation：四元数旋转

CameraFrame 使用 **四元数**（quaternion）表示旋转，存储在 `uniforms["orientation"]` 中（F-088）。四元数是一种无万向锁（gimbal lock）的三维旋转表示法，比欧拉角更适合插值计算。

### set_orientation / get_orientation

```python
def set_orientation(self, rotation: Rotation):
    self.uniforms["orientation"] = rotation.as_quat()

def get_orientation(self) -> Rotation:
    return Rotation.from_quat(self.uniforms["orientation"])
```

这两个方法使用 scipy 的 `Rotation` 类进行四元数和旋转矩阵之间的转换（F-093）。`set_orientation` 接收一个 scipy Rotation 对象，将其转换为四元数存入 uniforms；`get_orientation` 从 uniforms 读取四元数，构造 Rotation 对象返回。

### rotate 方法

CameraFrame 重写了 `rotate` 方法（F-095）：

```python
def rotate(self, angle, axis=OUT, **kwargs):
    rot = Rotation.from_rotvec(angle * normalize(axis))
    curr = self.get_orientation()
    self.set_orientation(curr * rot)  # 四元数乘法 = 旋转复合
    return self
```

旋转通过**四元数乘法**复合：当前朝向 `curr` 乘以新旋转 `rot`，得到新的朝向。`axis` 参数默认是 `OUT`（即从屏幕指向观众的方向），这是 2D 旋转的默认轴。

### fovy：垂直视场角

`fovy`（Field of View Y）控制相机的垂直视场角，类似真实相机的焦距：
- **fovy 越小**（如 20°）：视野越窄，看到的物体越大（"长焦"效果）
- **fovy 越大**（如 90°）：视野越宽，看到的物体越小（"广角"效果），透视变形越明显

默认 fovy 为 45°，这是一个自然的透视角度，接近人眼的舒适视野。在 2D 场景中，fovy 配合相机距离控制可视范围；在 3D 场景中，fovy 决定透视强度。

## 视图矩阵计算

`get_view_matrix(refresh=False)` 方法计算 4x4 仿射视图矩阵，这是 GPU 着色器将世界坐标转换为相机坐标的关键（F-094）。

### 计算流程

视图矩阵通过三步变换复合得到：**平移 → 旋转 → 缩放**：

```python
def get_view_matrix(self, refresh=False):
    if not refresh:
        return self.view_matrix
    
    # 1. 平移矩阵：将相机中心移到原点
    translation = self.id4x4.copy()
    translation[:3, 3] = -self.get_center()
    
    # 2. 旋转矩阵：应用相机朝向的逆旋转
    rotation = np.identity(4)
    rotation[:3, :3] = self.get_orientation().as_matrix().T
    
    # 3. 缩放矩阵：根据相机缩放因子调整
    scale = self.id4x4.copy()
    scale[:3, :3] /= self.get_scale()
    
    # 矩阵乘法：M = scale × rotation × translation（右乘，应用顺序相反）
    self.view_matrix = scale @ rotation @ translation
    return self.view_matrix
```

矩阵采用右乘约定：点向量在右侧，所以变换应用顺序是 translation（先移中心到原点）→ rotation（再旋转到相机朝向）→ scale（最后缩放）。矩阵复合顺序是反向的：`scale @ rotation @ translation`。

视图矩阵在每次相机移动/旋转/缩放后需要 refresh，它被上传到 GPU 作为 uniform 变量，顶点着色器使用它将世界坐标变换到相机视角空间。

## 欧拉角与 reorient 快捷设置

虽然内部使用四元数，但 CameraFrame 也提供了欧拉角接口方便设置朝向。

### set_euler_angles

`set_euler_angles(theta, phi, gamma, units=RADIANS)` 方法按 `euler_axes` 指定的轴顺序设置欧拉角（F-096）：

```python
def set_euler_angles(self, theta, phi, gamma, units=RADIANS):
    if units == DEGREES:
        theta, phi, gamma = (angle * DEG for angle in (theta, phi, gamma))
    rotation = Rotation.from_euler(self.euler_axes, [theta, phi, gamma])
    self.set_orientation(rotation)
```

默认 `euler_axes="zxz"` 表示先绕 Z 轴旋转 theta，再绕新的 X 轴旋转 phi，最后绕新的 Z 轴旋转 gamma（这是经典的 z-x-z 欧拉角约定，常用于物理和数学）。

### reorient：快捷设置方法

`reorient(theta_degrees, phi_degrees, gamma_degrees, center, height)` 是设置相机朝向和位置的快捷方法（F-097）：

- 角度参数默认单位是**度**（不是弧度）
- 可同时设置 `center`（相机中心点）和 `height`（帧高度/缩放）
- 等价于先 set_euler_angles，再 move_to，再设置高度

```python
# Scene.default_frame_orientation = (0, 0)（F-044），默认 2D 俯视
# 在子类中重写 default_frame_orientation 可设置默认 3D 视角
class ThreeDScene(Scene):
    default_frame_orientation = (-30, 70)  # phi=-30°, theta=70° 的 3D 视角
```

Scene 初始化时调用 `frame.reorient(*self.default_frame_orientation)` 然后 `frame.make_orientation_default()` 保存默认朝向（F-047）。

## 相机操作：移动、旋转、缩放

因为 CameraFrame 是 Mobject，所有 Mobject 的变换方法（shift、scale、rotate、move_to 等）都可以直接用在 self.frame 上。这是 ManimGL 相机系统最直观的特性。

### 相机移动：shift / move_to

```python
# 相机向右移动 3 个单位（视觉效果：场景内容向左移动）
self.play(self.frame.animate.shift(RIGHT * 3))

# 相机移动到指定位置
self.play(self.frame.animate.move_to(UP * 2 + RIGHT))

# 跟随移动对象
obj = Circle().shift(LEFT * 5)
self.add(obj)
self.play(
    obj.animate.shift(RIGHT * 10),
    self.frame.animate.shift(RIGHT * 10),
    run_time=3
)
```

> **注意**：相机移动方向与视觉效果相反——相机向右移，看起来场景向左移。这与真实摄像机一致：你拿着摄像机向右走，画面中的景物看起来向左移动。

### 相机缩放：scale

```python
# 放大 2 倍（焦距拉进，看到的物体变大，视野变窄）
self.play(self.frame.animate.scale(0.5))  # 注意：frame.scale(0.5) 是帧变小=物体看起来变大

# 缩小到 0.5 倍（焦距拉远，视野变大，看到更多内容）
self.play(self.frame.animate.scale(2))
```

CameraFrame 的 scale 与 fovy 共同决定视野大小。scale 值越小，帧尺寸越小，同样 fovy 下物体显得越大。可以理解为：scale 是"放大/缩小画面"，fovy 是"改变镜头焦距"。

```python
# 常用：让相机聚焦到某个对象
self.play(self.frame.animate.scale(0.3).move_to(circle))
```

### 相机旋转：rotate

```python
# 2D 旋转：绕垂直屏幕轴旋转 45 度
self.play(self.frame.animate.rotate(PI / 4))

# 3D 旋转：绕 X 轴旋转（俯视变斜视）
self.play(self.frame.animate.rotate(PI / 6, axis=RIGHT))

# 绕 Y 轴旋转（左右转头效果）
self.play(self.frame.animate.rotate(PI / 4, axis=UP))
```

2D 场景中相机通常只绕 OUT 轴（Z 轴）旋转；3D 场景中可以绕任意轴旋转创造立体效果。

## 2D/3D 场景切换

ManimGL 原生支持 2D 和 3D 场景，切换的核心就是设置 CameraFrame 的 orientation。

### 2D 模式（默认）

默认 `default_frame_orientation = (0, 0)`（F-044），相机沿 Z 轴负方向俯视 XY 平面：
- fovy 默认 45°
- orientation 为单位四元数（无旋转）
- 所有对象的 Z 坐标不影响视觉大小（正交感近似，但实际是透视投影）

### 3D 模式

通过设置相机欧拉角进入 3D 视角：

```python
class My3DScene(Scene):
    def construct(self):
        # 设置 3D 视角：phi=70°（俯仰角），theta=-30°（方位角）
        self.frame.reorient(phi_degrees=-30, theta_degrees=70)
        
        # 创建 3D 对象
        cube = Cube()
        sphere = Sphere()
        self.add(cube, sphere)
        
        # 相机绕 3D 空间旋转
        self.play(self.frame.animate.rotate(TAU, axis=UP), run_time=5)
```

在 3D 模式下：
- 需要启用 `depth_test=True` 让对象正确遮挡（Mobject 初始化参数，F-058）
- `IN` 和 `OUT` 向量（Z 轴方向）变得有意义
- 旋转轴可以是 RIGHT、UP、OUT 或任意三维向量
- 光照位置 `light_source_position` 影响 3D 着色效果

### is_fixed_in_frame：固定在帧上的对象

某些 UI 元素（如标题、标签）不希望随相机移动，可以在创建时设置 `is_fixed_in_frame=True`（F-058）：

```python
title = Text("ManimGL", font_size=48)
title.to_corner(UL)
title.is_fixed_in_frame = True  # 标题固定在屏幕左上角，不随相机移动
self.add(title)

# 即使相机移动/旋转，标题始终在屏幕左上角
self.play(self.frame.animate.shift(RIGHT * 5).rotate(PI/4))
```

## 相机动画示例

以下是一些常用相机动画模式：

### 镜头推进

```python
# 缓慢推进到目标对象
self.play(
    self.frame.animate.scale(0.4).move_to(target),
    run_time=3,
    rate_func=smooth
)
```

### 环绕旋转

```python
# 相机绕目标对象旋转一圈
self.frame.move_to(target.get_center())
self.play(
    self.frame.animate.rotate(TAU, axis=UP).scale(0.5),
    run_time=6,
    rate_func=linear
)
```

### 多焦点切换

```python
# 先看 A，再平滑移动到 B
self.play(self.frame.animate.move_to(A).scale(0.8), run_time=2)
self.wait()
self.play(self.frame.animate.move_to(B).scale(1.0), run_time=2)
```

### 焦点推拉

```python
# 快速推进再拉回（强调效果）
self.play(self.frame.animate.scale(0.3), run_time=0.5, rate_func=rush_into)
self.play(self.frame.animate.scale(1/0.3), run_time=0.8, rate_func=overshoot)
```

## 相机即 Mobject 的统一抽象

总结 CameraFrame 作为 Mobject 的意义（洞察 I-03）：

1. **API 统一**：移动、旋转、缩放相机不需要学习新 API，使用和操作普通对象相同的方法
2. **动画统一**：相机可以和普通对象一起在 `self.play()` 中动画，甚至可以对相机使用 Transform
3. **场景图统一**：相机在 mobjects 列表中，与其他对象在同一个变换体系中
4. **updater 统一**：可以给相机添加 updater，实现自动追踪、跟随等效果
5. **数据结构统一**：相机的位置/旋转通过 Mobject 的 data/uniforms 机制自动同步到 GPU

对比传统图形引擎（如 OpenGL、Three.js）中相机作为独立实体需要单独的 lookAt、perspective 等 API，ManimGL 的这一设计极大降低了镜头语言的学习成本——创作者只需要掌握一种变换体系就能同时操作内容和视角。

## 相关概念

- [03 Mobject：数学对象基类](03-mobject-fundamentals.md)
- [05 动画基础](05-animation-basics.md)
- [06 Transform 深度解析](06-transform-deep-dive.md)
- [08 常量系统与颜色体系](08-constants-and-colors.md)
- [09 GPU 渲染管线](09-rendering-pipeline.md)
