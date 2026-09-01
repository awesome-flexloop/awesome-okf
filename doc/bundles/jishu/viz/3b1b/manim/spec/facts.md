---
type: spec
title: "ManimGL 源码事实采集（R阶段）"
---

# ManimGL 源码事实采集（R阶段）

## 模块概览表

| 模块 | 文件路径 | 核心内容 |
|------|----------|----------|
| 入口模块 | `manimlib/__init__.py` | 版本号、全局配置、全量导出 |
| 配置系统 | `manimlib/config.py` | CLI解析、配置加载、配置合并 |
| 常量定义 | `manimlib/constants.py` | 方向向量、颜色常量、尺寸常量 |
| 场景系统 | `manimlib/scene/scene.py` | Scene基类、渲染循环、交互 |
| 对象基类 | `manimlib/mobject/mobject.py` | Mobject基类、数据结构、变换 |
| 矢量对象 | `manimlib/mobject/types/vectorized_mobject.py` | VMobject、贝塞尔路径、描边填充 |
| 几何图形 | `manimlib/mobject/geometry.py` | TipableVMobject、ArrowTip、几何常量 |
| 相机系统 | `manimlib/camera/camera.py` | Camera类、FrameStream、GPU渲染目标 |
| 相机帧 | `manimlib/camera/camera_frame.py` | CameraFrame、欧拉角、视图矩阵 |
| 动画基类 | `manimlib/animation/animation.py` | Animation基类、插值、时间控制 |
| 变换动画 | `manimlib/animation/transform.py` | Transform、ReplacementTransform、路径弧 |
| 渲染器 | `manimlib/renderer/renderer.py` | Renderer、Bundling、Draw分组 |
| 缓动函数 | `manimlib/utils/rate_functions.py` | smooth、linear、there_and_back等 |

---

## 一、入口模块（__init__.py）

F-001：`manimlib/__init__.py` 第7-9行定义 `__version__`，通过 `importlib.metadata.version("manimgl")` 获取版本号，失败时设为 `"unknown"`。

F-002：`manimlib/__init__.py` 第12行从 `manimlib.config` 导入全局配置对象 `manim_config`。

F-003：`manimlib/__init__.py` 第19行使用 `from manimlib.constants import *` 通配导入所有常量。

F-004：`manimlib/__init__.py` 第23-35行通配导入 animation 子包下13个模块：animation、composition、creation、fading、growing、indication、movement、numbers、rotation、specialized、transform、transform_matching_parts、update。

F-005：`manimlib/__init__.py` 第37行通配导入 camera 模块。

F-006：`manimlib/__init__.py` 第39-68行通配导入 mobject 子包下27个模块，包括 boolean_ops、changing、coordinate_systems、fractals、frame、functions、geometry、interactive、matrix、mobject、mobject_update_utils、number_line、numbers、probability、shape_matchers、svg 子包7个模块、three_dimensions、types 子包5个模块、value_tracker、vector_field。

F-007：`manimlib/__init__.py` 第70-71行通配导入 scene 子包下 interactive_scene 和 scene 两个模块。

F-008：`manimlib/__init__.py` 第73-74行从 renderer 模块导入 `get_colormap_code` 和 uniform_block 模块的所有内容。

F-009：`manimlib/__init__.py` 第76-91行通配导入 utils 子包下15个模块：bezier、cache、color、dict_ops、debug、directories、file_ops、images、iterables、paths、rate_functions、simple_functions、sounds、space_ops、svg_export、tex。

---

## 二、配置系统（config.py）

F-010：`manimlib/config.py` 第23-51行定义函数 `initialize_manim_config() -> Dict`，返回 addict.Dict 类型的配置对象。

F-011：`manimlib/config.py` 第34行配置文件加载顺序：先加载 `manimlib/default_config.yml`，再加载当前工作目录的 `custom_config.yml`，最后加载 `args.config_file` 指定的配置文件，使用 `merge_dicts_recursively` 递归合并。

F-012：`manimlib/config.py` 第54-232行定义 `parse_cli()` 函数，使用 argparse 解析命令行参数。

F-013：`manimlib/config.py` 第58-62行 CLI 接受位置参数 `file`（场景Python文件路径）和 `scene_names`（场景类名列表，nargs="*"）。

F-014：`manimlib/config.py` 第69-71行 CLI 参数 `-w/--write_file`（布尔值），渲染为视频文件。

F-015：`manimlib/config.py` 第74-76行 CLI 参数 `-s/--skip_animations`（布尔值），保存最后一帧。

F-016：`manimlib/config.py` 第79-97行定义四个画质参数：`-l/--low_quality`（480p）、`-m/--medium_quality`（720p）、`--hd`（1080p）、`--uhd`（4k）。

F-017：`manimlib/config.py` 第110-112行 CLI 参数 `-i/--gif`（布尔值），保存为 GIF 格式。

F-018：`manimlib/config.py` 第115-117行 CLI 参数 `-t/--transparent`（布尔值），渲染带 alpha 通道的视频。

F-019：`manimlib/config.py` 第128-130行 CLI 参数 `-q/--quiet`（布尔值），安静模式。

F-020：`manimlib/config.py` 第133-135行 CLI 参数 `-a/--write_all`（布尔值），写入文件中所有场景。

F-021：`manimlib/config.py` 第158-163行 CLI 参数 `-n/--start_at_animation_number`，支持逗号分隔的起止值（如"3,6"）。

F-022：`manimlib/config.py` 第165-168行 CLI 参数 `-e/--embed` 接受 LINE_NUMBER，在指定行插入 iPython 断点。

F-023：`manimlib/config.py` 第228行 `args.write_file = any([args.write_file, args.open, args.finder])`，`-o/--open` 和 `--finder` 隐式启用 write_file。

F-024：`manimlib/config.py` 第235-239行 `update_directory_config()` 函数，将 `config.directories.base` 与 `config.directories.subdirs` 中各子目录拼接为完整路径。

F-025：`manimlib/config.py` 第251-265行 `update_camera_config()` 函数，处理分辨率、fps、背景颜色（使用 colour.Color 解析）、背景透明度。

F-026：`manimlib/config.py` 第336-341行 `load_yaml(file_path)` 函数，使用 `yaml.safe_load` 加载 YAML 文件，文件不存在时返回空字典。

F-027：`manimlib/config.py` 第344-347行 `get_manim_dir()` 函数，通过 `importlib.import_module("manimlib")` 获取模块路径，返回 manimlib 父目录的绝对路径。

F-028：`manimlib/config.py` 第350-361行 `get_resolution_from_args()` 函数，根据参数返回对应分辨率元组，无匹配时返回 None。

F-029：`manimlib/config.py` 第364-371行 `get_file_ext(args)` 函数，transparent 返回 `.mov`，gif 返回 `.gif`，否则返回 `.mp4`。

F-030：`manimlib/config.py` 第399行模块末尾创建全局配置实例 `manim_config: Dict = initialize_manim_config()`。

---

## 三、常量定义（constants.py）

F-031：`manimlib/constants.py` 第13-15行从 `manim_config.camera.resolution` 读取 `DEFAULT_RESOLUTION` 元组，并拆分为 `DEFAULT_PIXEL_WIDTH` 和 `DEFAULT_PIXEL_HEIGHT`。

F-032：`manimlib/constants.py` 第18-23行计算帧相关常量：`ASPECT_RATIO = DEFAULT_PIXEL_WIDTH / DEFAULT_PIXEL_HEIGHT`，`FRAME_HEIGHT` 从配置读取，`FRAME_WIDTH = FRAME_HEIGHT * ASPECT_RATIO`，`FRAME_SHAPE = (FRAME_WIDTH, FRAME_HEIGHT)`，`FRAME_Y_RADIUS = FRAME_HEIGHT / 2`，`FRAME_X_RADIUS = FRAME_WIDTH / 2`。

F-033：`manimlib/constants.py` 第37-46行定义标准方向向量（numpy数组）：`ORIGIN = [0., 0., 0.]`，`UP = [0., 1., 0.]`，`DOWN = [0., -1., 0.]`，`RIGHT = [1., 0., 0.]`，`LEFT = [-1., 0., 0.]`，`IN = [0., 0., -1.]`，`OUT = [0., 0., 1.]`，`X_AXIS/Y_AXIS/Z_AXIS` 分别为对应轴向单位向量。

F-034：`manimlib/constants.py` 第51-54行定义对角线方向缩写：`UL = UP + LEFT`，`UR = UP + RIGHT`，`DL = DOWN + LEFT`，`DR = DOWN + RIGHT`。

F-035：`manimlib/constants.py` 第56-59行定义边缘位置：`TOP = FRAME_Y_RADIUS * UP`，`BOTTOM = FRAME_Y_RADIUS * DOWN`，`LEFT_SIDE = FRAME_X_RADIUS * LEFT`，`RIGHT_SIDE = FRAME_X_RADIUS * RIGHT`。

F-036：`manimlib/constants.py` 第62-68行定义角度常量：`PI = np.pi`，`TAU = 2 * PI`，`DEG = TAU / 360`，`DEGREES = DEG`（别名），`RADIANS = 1`。

F-037：`manimlib/constants.py` 第71-74行定义字体样式常量字符串：`NORMAL = "NORMAL"`，`ITALIC = "ITALIC"`，`OBLIQUE = "OBLIQUE"`，`BOLD = "BOLD"`。

F-038：`manimlib/constants.py` 第79-136行定义按色系分级的颜色常量，每个色系有 E/D/C/B/A 五个深浅级别（E最深，A最浅），色系包括：BLUE、TEAL、GREEN、YELLOW、GOLD、RED、MAROON、PURPLE、GREY。

F-039：`manimlib/constants.py` 第140-148行定义各色系中位色别名：`BLUE = BLUE_C`，`TEAL = TEAL_C`，`GREEN = GREEN_C`，`YELLOW = YELLOW_C`，`GOLD = GOLD_C`，`RED = RED_C`，`MAROON = MAROON_C`，`PURPLE = PURPLE_C`，`GREY = GREY_C`。

F-040：`manimlib/constants.py` 第150行定义3Blue1Brown配色方案 `COLORMAP_3B1B = [BLUE_E, GREEN, YELLOW, RED]`。

F-041：`manimlib/constants.py` 第155-156行 `DEFAULT_MOBJECT_COLOR` 从配置读取，默认 `WHITE`；`DEFAULT_LIGHT_COLOR` 从配置读取，默认 `GREY_B`。

F-042：`manimlib/constants.py` 第158-159行 `DEFAULT_VMOBJECT_STROKE_COLOR` 从配置读取，默认 `GREY_A`；`DEFAULT_VMOBJECT_FILL_COLOR` 从配置读取，默认 `GREY_C`。

---

## 四、场景系统（scene/scene.py）

F-043：`manimlib/scene/scene.py` 第52行定义 `class Scene(object)`，继承自 object。

F-044：`manimlib/scene/scene.py` 第53-62行 Scene 类属性：`random_seed = 0`，`pan_sensitivity = 0.5`，`scroll_sensitivity = 20`，`drag_to_pan = True`，`max_num_saved_states = 50`，`default_camera_config = dict()`，`default_file_writer_config = dict()`，`samples = 0`，`default_frame_orientation = (0, 0)`（欧拉角，单位度）。

F-045：`manimlib/scene/scene.py` 第64-79行 Scene.__init__ 参数包括：window、camera_config、file_writer_config、skip_animations、always_update_mobjects、start_at_animation_number、end_at_animation_number、show_animation_progress、leave_progress_bars、preview_while_skipping、presenter_mode、default_wait_time、invert_zoom_scroll。

F-046：`manimlib/scene/scene.py` 第91-100行 camera_config 和 file_writer_config 通过 `merge_dicts_recursively` 三层合并：全局默认 → 子类默认配置 → 实例化配置。

F-047：`manimlib/scene/scene.py` 第109-114行 Scene 持有 `self.camera: Camera` 实例和 `self.frame: CameraFrame`（即 `self.camera.frame`），并调用 `frame.reorient(*self.default_frame_orientation)` 和 `frame.make_orientation_default()`。

F-048：`manimlib/scene/scene.py` 第119-126行 Scene 核心状态：`self.mobjects: list[Mobject] = [self.camera.frame]`（初始包含相机帧），`self.id_to_mobject_map: dict[int, Mobject] = dict()`，`self.num_plays: int = 0`，`self.time: float = 0`，`self.skip_time: float = 0`，`self.undo_stack = []`，`self.redo_stack = []`。

F-049：`manimlib/scene/scene.py` 第134-137行交互相关状态：`self.mouse_point = Point()`，`self.mouse_drag_point = Point()`，`self.hold_on_wait = self.presenter_mode`，`self.quit_interaction = False`。

F-050：`manimlib/scene/scene.py` 第150-165行 `run()` 方法流程：设置 virtual_animation_start_time 和 real_animation_start_time → 调用 `file_writer.begin()` → `setup()` → `construct()` → `interact()` → 捕获 EndScene 和 KeyboardInterrupt → `tear_down()`。

F-051：`manimlib/scene/scene.py` 第167-178行三个生命周期方法：`setup()`（空实现，子类重写）、`construct()`（空实现，子类重写，所有动画在此发生）、`tear_down()`（调用 stop_skipping()、file_writer.finish()、window.destroy()）。

F-052：`manimlib/scene/scene.py` 第187-201行 `interact()` 方法：window 存在时进入循环，调用 `update_frame(1 / self.camera.fps)` 直到窗口关闭。

F-053：`manimlib/scene/scene.py` 第236-239行 `update_frame(dt, force_draw)` 方法三步：`increment_time(dt)` → `update_mobjects(dt)` → `draw_frame(dt, force_draw)`。

F-054：`manimlib/scene/scene.py` 第241-260行 `draw_frame(dt, force_draw)` 方法：skip_animations 且非 force_draw 时返回；检查窗口关闭；无事件且 dt=0 时仅 poll_events；调用 `camera.capture(*self.mobjects)`；非跳过时根据虚拟时间与实际时间差 sleep 同步帧率。

F-055：`manimlib/scene/scene.py` 第267-272行 `update_mobjects(dt)` 方法遍历 self.mobjects，对每个 mobject 调用 `mobject.update(dt, frame_rate=self.camera.fps)`。

---

## 五、对象基类（mobject/mobject.py）

F-056：`manimlib/mobject/mobject.py` 第66行定义 `class Mobject(object)`，文档字符串为 "Mathematical Object"。

F-057：`manimlib/mobject/mobject.py` 第70-92行 Mobject 类属性：`dim: int = 3`，`drawing_class: type = Drawing`，`shader_file: str = ""`，`verts_per_record: int = 0`，`data_dtype: np.dtype` 包含 `('point', np.float32, (3,))` 和 `('rgba', np.float32, (4,))` 两个字段，`uniform_dtype` 由 `uniform_block_dtype(*COMMON_UNIFORMS)` 生成，`pointlike_data_keys = ['point']`，`structural_data_keys: list[str] = []`，`pointlike_uniform_keys: list[str] = []`。

F-058：`manimlib/mobject/mobject.py` 第94-105行 Mobject.__init__ 参数：color（默认 DEFAULT_MOBJECT_COLOR）、opacity（默认 1.0）、shading（默认 (0.0, 0.0, 0.0)）、texture_paths（默认 None）、is_fixed_in_frame（默认 False）、depth_test（默认 False）、z_index（默认 0）。

F-059：`manimlib/mobject/mobject.py` 第114-125行 Mobject 内部状态：`self.submobjects: list[Mobject] = []`，`self.parents: list[Mobject] = []`，`self.family: list[Mobject] | None = [self]`，`self.saved_state = None`，`self.target = None`，`self.bounding_box: Vect3Array = np.zeros((3, 3))`，`self.skip_box_interpolation: bool = False`，`self._is_animating: bool = False`，`self._needs_new_bounding_box: bool = True`，`self.shader_code_replacements: dict[str, str] = dict()`。

F-060：`manimlib/mobject/mobject.py` 第127-132行 Mobject.__init__ 初始化调用序列：`init_data()` → `init_uniforms()` → `init_updaters()` → `init_event_listners()` → `init_points()` → `init_colors()`。

F-061：`manimlib/mobject/mobject.py` 第150-151行 `init_data(length=0)` 方法创建 `self.data: StructuredArray = StructuredArray(self.data_dtype, length)`。

F-062：`manimlib/mobject/mobject.py` 第153-156行 `init_uniforms()` 方法创建 `self.uniforms: Uniforms = Uniforms(self.uniform_dtype)`，并设置 `self.uniforms["shading"] = self.shading`。

F-063：`manimlib/mobject/mobject.py` 第169-178行 `animate` 属性返回 `_AnimationBuilder(self)`，支持 `mobject.animate.method()` 语法生成动画。

F-064：`manimlib/mobject/mobject.py` 第180-187行 `always` 属性返回 `_UpdaterBuilder(self)`，支持 `mobject.always.method(*args, **kwargs)` 语法每帧调用方法。

F-065：`manimlib/mobject/mobject.py` 第189-210行 `f_always` 属性返回 `_FunctionalUpdaterBuilder(self)`，方法参数为函数，每帧调用函数获取参数值再调用方法。

F-066：`manimlib/mobject/mobject.py` 第142-144行 `__add__` 运算符：`self + other` 返回 `self.get_group_class()(self, other)`，要求 other 是 Mobject 实例。

F-067：`manimlib/mobject/mobject.py` 第146-148行 `__mul__` 运算符：`self * n`（n为int）返回 `self.replicate(n)`。

---

## 六、矢量对象（mobject/types/vectorized_mobject.py）

F-068：`manimlib/mobject/types/vectorized_mobject.py` 第64行定义 `class VMobject(Mobject)`，继承自 Mobject。

F-069：`manimlib/mobject/types/vectorized_mobject.py` 第65行 VMobject.drawing_class = VDrawing。

F-070：`manimlib/mobject/types/vectorized_mobject.py` 第66行 VMobject.structural_data_keys = ['subpath_range']。

F-071：`manimlib/mobject/types/vectorized_mobject.py` 第67-75行 VMobject.data_dtype 包含四个字段：`('point', np.float32, (3,))`、`('stroke_rgba', np.float32, (4,))`、`('stroke_width', np.float32, (1,))`、`('subpath_range', np.float32, (2,))`。

F-072：`manimlib/mobject/types/vectorized_mobject.py` 第76-88行 VMobject.uniform_dtype 在 COMMON_UNIFORMS 基础上增加：anti_alias_width(1)、joint_roundness(1)、flat_stroke(1)、stroke_width_in_scene_units(1)、unit_normal(3)、fill_rgba(4)、fill_rgba_end(4)、gradient_start(3)、gradient_end(3)、fill_border_width(1)。

F-073：`manimlib/mobject/types/vectorized_mobject.py` 第94-118行 VMobject.__init__ 参数：color、fill_color、fill_opacity（默认0.0）、stroke_color、stroke_opacity（默认1.0）、stroke_width（默认DEFAULT_STROKE_WIDTH）、stroke_behind（默认False）、background_image_file、long_lines（默认False）、joint_roundness（默认0.0）、flat_stroke（默认False）、stroke_width_in_scene_units（默认False）、use_simple_quadratic_approx（默认False）、anti_alias_width（默认1.5）、fill_border_width（默认0.0）。

---

## 七、几何图形（mobject/geometry.py）

F-074：`manimlib/mobject/geometry.py` 第38-42行定义几何常量：`DEFAULT_DOT_RADIUS = 0.08`，`DEFAULT_SMALL_DOT_RADIUS = 0.04`，`DEFAULT_DASH_LENGTH = 0.05`，`DEFAULT_ARROW_TIP_LENGTH = 0.35`，`DEFAULT_ARROW_TIP_WIDTH = 0.35`。

F-075：`manimlib/mobject/geometry.py` 第46行定义 `class TipableVMobject(VMobject)`，继承自 VMobject，为 Arc 和 Line 提供箭头尖端共享功能。

F-076：`manimlib/mobject/geometry.py` 第64-68行 TipableVMobject.tip_config 字典默认值：fill_opacity=1.0，stroke_width=0.0，tip_style=0.0（0=三角形，1=内平滑，2=点）。

F-077：`manimlib/mobject/geometry.py` 第71-82行 `add_tip(at_start=False, **kwargs)` 方法调用 create_tip → reset_endpoints_based_on_tip → asign_tip_attr → tip.set_color → self.add(tip)。

---

## 八、相机系统（camera/camera.py）

F-078：`manimlib/camera/camera.py` 第30行定义 `class FrameStream(object)`，处理GPU帧到输出的异步拷贝，保持一帧延迟以实现流水线并行。

F-079：`manimlib/camera/camera.py` 第44-70行 FrameStream.__init__(camera, sink, behind=1)：创建 behind+1 个 GPU 缓冲区（wgpu.BufferUsage.COPY_DST | wgpu.BufferUsage.MAP_READ），维护 waiting 列表记录待读取缓冲区和 asked 计数器。

F-080：`manimlib/camera/camera.py` 第108行定义 `class Camera(object)`。

F-081：`manimlib/camera/camera.py` 第109-125行 Camera.__init__ 参数：window（默认None）、frame_config（默认空dict）、resolution（默认DEFAULT_RESOLUTION）、fps（默认30）、background_color（默认BLACK）、background_opacity（默认1.0）、light_source_position（默认[-10, 10, 10]）、bundle_draws（默认True）、draw_together（默认True）、samples（默认0，多重采样数）。

F-082：`manimlib/camera/camera.py` 第134-136行 Camera.background_rgba = list(color_to_rgba(background_color, background_opacity))，长度为4的浮点数列表。

F-083：`manimlib/camera/camera.py` 第140行 Camera.draw_at_window_size = (window is not None)，窗口存在时按窗口尺寸绘制而非输出分辨率。

F-084：`manimlib/camera/camera.py` 第147-148行 `init_frame(**config)` 方法创建 `self.frame = CameraFrame(**config)`。

F-085：`manimlib/camera/camera.py` 第150-158行 `init_renderer()` 方法：window 存在时复用 window.gpu，否则新建 Gpu()；创建 `self.renderer = Renderer(self.gpu, bundle=self.bundle_draws, together=self.draw_together)`。

F-086：`manimlib/camera/camera.py` 第173-189行 `at_output_resolution()` 上下文管理器：临时设置 draw_at_window_size=False 并 resize_target，退出时恢复，用于按输出分辨率绘制帧（如截图、写文件时）。

---

## 九、相机帧（camera/camera_frame.py）

F-087：`manimlib/camera/camera_frame.py` 第25行定义 `class CameraFrame(Mobject)`，继承自 Mobject。

F-088：`manimlib/camera/camera_frame.py` 第29-33行 CameraFrame.uniform_dtype 在 COMMON_UNIFORMS 基础上增加 orientation(4)（四元数）和 fovy(1)（垂直视场角）。

F-089：`manimlib/camera/camera_frame.py` 第35-45行 CameraFrame.__init__ 参数：frame_shape（默认FRAME_SHAPE）、center_point（默认ORIGIN）、fovy（默认45*DEG）、euler_axes（默认"zxz"）、z_index（默认-1，保证在场景最底层）。

F-090：`manimlib/camera/camera_frame.py` 第48-49行 CameraFrame 初始化时设置 uniforms["orientation"] = Rotation.identity().as_quat()，uniforms["fovy"] = fovy。

F-091：`manimlib/camera/camera_frame.py` 第51-54行 CameraFrame 持有 `self.default_orientation = Rotation.identity()`，`self.view_matrix = np.identity(4)`，`self.id4x4 = np.identity(4)`，`self.euler_axes = euler_axes`。

F-092：`manimlib/camera/camera_frame.py` 第56-59行 CameraFrame 初始化点集为 `[ORIGIN, LEFT, RIGHT, DOWN, UP]`，然后调用 set_width、set_height、move_to 定位。

F-093：`manimlib/camera/camera_frame.py` 第61-66行 `set_orientation(rotation)` 接收 scipy Rotation 对象，设置 uniforms["orientation"] = rotation.as_quat()；`get_orientation()` 返回 Rotation.from_quat(uniforms["orientation"])。

F-094：`manimlib/camera/camera_frame.py` 第110-127行 `get_view_matrix(refresh=False)` 方法计算4x4仿射变换矩阵：先平移（-center）→ 旋转（逆相机旋转矩阵）→ 缩放（除以scale），结果存入 self.view_matrix。

F-095：`manimlib/camera/camera_frame.py` 第132-135行 `rotate(angle, axis=OUT, **kwargs)` 方法：创建 Rotation.from_rotvec(angle * normalize(axis))，与当前 orientation 相乘后设置。

F-096：`manimlib/camera/camera_frame.py` 第137-153行 `set_euler_angles(theta, phi, gamma, units=RADIANS)` 方法按 euler_axes 顺序设置欧拉角。

F-097：`manimlib/camera/camera_frame.py` 第178-195行 `reorient(theta_degrees, phi_degrees, gamma_degrees, center, height)` 方法是 set_euler_angles 的快捷方式，默认角度单位为度，同时可设置 center 和 height。

---

## 十、动画基类（animation/animation.py）

F-098：`manimlib/animation/animation.py` 第19-20行定义动画默认常量：`DEFAULT_ANIMATION_RUN_TIME = 1.0`，`DEFAULT_ANIMATION_LAG_RATIO = 0`。

F-099：`manimlib/animation/animation.py` 第23行定义 `class Animation(object)`。

F-100：`manimlib/animation/animation.py` 第24-44行 Animation.__init__ 参数：mobject（Mobject实例）、run_time（默认1.0）、time_span（默认None，(start, end)元组）、lag_ratio（默认0，0=同步，1=逐次，0<值<1=滞后重叠）、rate_func（默认smooth）、name（默认空字符串）、remover（默认False，动画结束是否移除mobject）、final_alpha_value（默认1.0）、suspend_mobject_updating（默认False）。

F-101：`manimlib/animation/animation.py` 第56-58行 `_validate_input_type(mobject)` 检查 mobject 是否为 Mobject 实例，否则抛出 TypeError。

F-102：`manimlib/animation/animation.py` 第63-78行 `begin()` 方法：处理 time_span → mobject.set_animating_status(True) → create_starting_mobject（拷贝mobject）→ 处理 suspend_mobject_updating → get_all_families_zipped → prepare_interpolation → interpolate(0)。

F-103：`manimlib/animation/animation.py` 第103-108行 `finish()` 方法：interpolate(final_alpha_value) → mobject.turn_off_interpolation_skip() → mobject.set_animating_status(False) → 恢复 mobject 更新（如被暂停）。

F-104：`manimlib/animation/animation.py` 第110-112行 `clean_up_from_scene(scene)` 方法：若 is_remover() 为真，调用 scene.remove(self.mobject)。

F-105：`manimlib/animation/animation.py` 第114-116行 `create_starting_mobject()` 返回 `self.mobject.copy()`，用于记录起始状态。

F-106：`manimlib/animation/animation.py` 第118-122行 `get_all_mobjects()` 返回 `(self.mobject, self.starting_mobject)` 二元组。

F-107：`manimlib/animation/animation.py` 第166-167行 `interpolate(alpha)` 方法调用 `self.interpolate_mobject(alpha)`。

F-108：`manimlib/animation/animation.py` 第182-185行 `interpolate_mobject(alpha)` 方法：遍历 families（已zipped），对每个 submobject 计算 sub_alpha，调用 interpolate_submobject。

---

## 十一、变换动画（animation/transform.py）

F-109：`manimlib/animation/transform.py` 第24行定义 `class Transform(Animation)`，继承自 Animation。

F-110：`manimlib/animation/transform.py` 第25行 Transform.replace_mobject_with_target_in_scene = False（类属性）。

F-111：`manimlib/animation/transform.py` 第27-35行 Transform.__init__ 参数：mobject、target_mobject（默认None）、path_arc（默认0.0，float或(float,float)元组）、path_arc_axis（默认OUT）、path_func（默认None）。

F-112：`manimlib/animation/transform.py` 第43-52行 `init_path_func()` 方法：path_func 已设置则直接返回；path_arc=0 时使用 straight_path；否则使用 path_along_arc(path_arc, path_arc_axis)。

F-113：`manimlib/animation/transform.py` 第54-68行 `begin()` 方法：create_target() → check_target_mobject_validity() → 若 is_aligned_with 则 target_copy = target_mobject，否则拷贝 target_copy 并调用 mobject.align_data_and_family(target_copy) → 调用 super().begin()。

F-114：`manimlib/animation/transform.py` 第81-85行 `clean_up_from_scene(scene)` 方法：调用父类 clean_up_from_scene；若 replace_mobject_with_target_in_scene 为真，scene.remove(self.mobject) 并 scene.add(self.target_mobject)。

F-115：`manimlib/animation/transform.py` 第95-101行 `get_all_mobjects()` 返回四元组：[mobject, starting_mobject, target_mobject, target_copy]。

F-116：`manimlib/animation/transform.py` 第113-114行 `get_interpolation_ends()` 返回 (starting_mobject, target_copy)。

F-117：`manimlib/animation/transform.py` 第116-124行 `interpolate_submobject(submob, start, target_copy, alpha)` 调用 `submob.interpolate(start, target_copy, alpha, self.path_func)`。

F-118：`manimlib/animation/transform.py` 第127行定义 `class ReplacementTransform(Transform)`，replace_mobject_with_target_in_scene = True。

F-119：`manimlib/animation/transform.py` 第131行定义 `class TransformFromCopy(Transform)`，replace_mobject_with_target_in_scene = True。

F-120：`manimlib/animation/transform.py` 第134-135行 TransformFromCopy.__init__ 调用 super().__init__(mobject.copy(), target_mobject, **kwargs)。

F-121：`manimlib/animation/transform.py` 第138行定义 `class MoveToTarget(Transform)`。

F-122：`manimlib/animation/transform.py` 第139-141行 MoveToTarget.__init__(mobject, **kwargs) 先 check_validity_of_input，再调用 super().__init__(mobject, mobject.target, **kwargs)。

---

## 十二、渲染器（renderer/renderer.py）

F-123：`manimlib/renderer/renderer.py` 第20行定义常量 `FRAMES_BEFORE_BUNDLING = 2`，连续相同帧数达到此值后开始使用渲染束。

F-124：`manimlib/renderer/renderer.py` 第23行定义 `class Bundling(object)`，管理渲染束（render bundle）的创建与失效。

F-125：`manimlib/renderer/renderer.py` 第32-36行 Bundling.__init__(allowed=True)：self.allowed = allowed，self.bundle = None，self.settled = 0，self.stale = True。

F-126：`manimlib/renderer/renderer.py` 第38-39行 Bundling.invalidate() 方法设置 self.stale = True。

F-127：`manimlib/renderer/renderer.py` 第41-55行 Bundling.take(make) 方法：stale时重置settled和bundle；否则settled计数加1；settled >= FRAMES_BEFORE_BUNDLING 且允许时调用 make() 创建 bundle；返回 bundle 或 None。

F-128：`manimlib/renderer/renderer.py` 第58行定义 `class Renderer(object)`。

F-129：`manimlib/renderer/renderer.py` 第82-91行 Renderer.__init__(gpu, bundle=True, together=True)：持有 self.gpu，self.may_merge = together，self.bundling = Bundling(allowed=bundle)，self.materials: dict[tuple, Material] = dict()，self.drawings: dict[Mobject, Drawing] = dict()，self.drawn: list[Drawing] = []，self.leaders: list[Drawing] = []，self.run_lengths: tuple = ()。

F-130：`manimlib/renderer/renderer.py` 第93-128行 `draw(mobjects, attachments)` 方法流程：resolve(mobjects) 获取 drawings → 变化时 invalidate bundling → gpu.begin_writes() → 遍历 drawings 写 uniforms，invalidated 时 invalidate bundling → stale 或 regroup 时调用 group(drawings) 分组 → leaders 写 records → gpu.end_writes() → 获取 bundle → 有 bundle 时 replay，否则 make_draws。

F-131：`manimlib/renderer/renderer.py` 第134-159行 `group(drawings)` 方法：may_merge=False 时每个drawing为独立run；否则通过 batch_by_comparison 和 can_follow 连续可合并的drawing；每个run的第一个作为leader，持有 members 列表；返回 run 长度元组。

---

## 十三、缓动函数（utils/rate_functions.py）

F-132：`manimlib/utils/rate_functions.py` 第13-14行 `linear(t: float) -> float` 返回 t，线性插值。

F-133：`manimlib/utils/rate_functions.py` 第17-21行 `smooth(t: float) -> float`：公式 `t**3 * (10*s*s + 5*s*t + t*t)` 其中 s=1-t，t=0和t=1处一二阶导数为0，等价于贝塞尔曲线 [0,0,0,1,1,1]。

F-134：`manimlib/utils/rate_functions.py` 第24-25行 `rush_into(t)` 返回 `2 * smooth(0.5 * t)`，前半段加速。

F-135：`manimlib/utils/rate_functions.py` 第28-29行 `rush_from(t)` 返回 `2 * smooth(0.5 * (t + 1)) - 1`，后半段减速。

F-136：`manimlib/utils/rate_functions.py` 第32-33行 `slow_into(t)` 返回 `sqrt(1 - (1-t)^2)`，圆形缓入。

F-137：`manimlib/utils/rate_functions.py` 第36-40行 `double_smooth(t)`：t<0.5 时返回 0.5*smooth(2t)，否则返回 0.5*(1+smooth(2t-1))，两端平滑。

F-138：`manimlib/utils/rate_functions.py` 第43-45行 `there_and_back(t)`：t<0.5 时 smooth(2t)，否则 smooth(2(1-t))，去程+回程。

F-139：`manimlib/utils/rate_functions.py` 第48-55行 `there_and_back_with_pause(t, pause_ratio=1/3)`：去程smooth→中间pause_ratio区间保持1→回程smooth。

F-140：`manimlib/utils/rate_functions.py` 第58-59行 `running_start(t, pull_factor=-0.5)` 返回 bezier([0,0,pull_factor,pull_factor,1,1,1])(t)。

F-141：`manimlib/utils/rate_functions.py` 第62-63行 `overshoot(t, pull_factor=1.5)` 返回 bezier([0,0,pull_factor,pull_factor,1,1])(t)，过冲效果。

F-142：`manimlib/utils/rate_functions.py` 第66-72行 `not_quite_there(func=smooth, proportion=0.7)` 高阶函数，返回 `proportion * func(t)`，不到终点。

F-143：`manimlib/utils/rate_functions.py` 第75-76行 `wiggle(t, wiggles=2)` 返回 `there_and_back(t) * sin(wiggles * pi * t)`，来回摆动。

F-144：`manimlib/utils/rate_functions.py` 第79-94行 `squish_rate_func(func, a=0.4, b=0.6)` 高阶函数：t<a时返回func(0)，t>b时返回func(1)，中间映射func((t-a)/(b-a))，压缩函数到区间[a,b]。

F-145：`manimlib/utils/rate_functions.py` 第102-103行 `lingering(t)` 返回 `squish_rate_func(lambda t: t, 0, 0.8)(t)`，0-0.8区间线性，0.8后保持。

F-146：`manimlib/utils/rate_functions.py` 第106-108行 `exponential_decay(t, half_life=0.1)` 返回 `1 - exp(-t / half_life)`，指数衰减。
