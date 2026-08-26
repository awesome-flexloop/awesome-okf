---
type: Concept
title: 配置系统与 CLI 参数
description: ManimGL 采用三层配置递归合并机制（default_config.yml→custom_config.yml→CLI），CLI 参数覆盖画质、输出、调试等分组。
tags: [manimgl, configuration, cli, config-file, yml, parameters]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: ManimGL 源码事实采集
  - id: cli-ref
    resource: /references/cli-parameters-reference.md
    title: ManimGL CLI 参数速查表
---

# 配置系统与 CLI 参数

ManimGL 的配置系统定义在 `manimlib/config.py` 模块，负责 YAML 配置文件加载、命令行参数解析和配置递归合并（F-010 ~ F-030）。模块在导入时自动调用 `initialize_manim_config()` 创建全局配置实例 `manim_config`（F-030），常量模块（`constants.py`）从该全局对象读取分辨率、默认颜色等参数动态计算帧尺寸常量。配置采用三层优先级递归合并设计，后加载的配置覆盖先加载的同名配置项。

## 三层配置合并机制

配置加载由 `initialize_manim_config()` 函数实现（F-010），加载顺序由 `manimlib/config.py` 第34行确定（F-011）：

```
第一层（最低优先级）：manimlib/default_config.yml（包内置默认配置）
        ↓ 递归合并
第二层（中等优先级）：当前工作目录/custom_config.yml（用户项目配置）
        ↓ 递归合并
第三层（最高优先级）：CLI 参数 --config_file 指定的配置文件
        ↓ 递归合并
命令行参数（parse_cli() 解析结果，最终覆盖）
```

合并方式使用 `merge_dicts_recursively` 函数递归合并字典，这意味着嵌套字典会逐层合并而非整体替换，用户配置只需指定需要覆盖的项，无需复制完整默认配置。

配置文件加载通过 `load_yaml(file_path)` 函数实现（F-026），使用 `yaml.safe_load` 解析 YAML 文件，文件不存在时返回空字典而非抛出异常，这保证了 `custom_config.yml` 是可选的——不存在时自动跳过。

ManimGL 安装路径通过 `get_manim_dir()` 函数获取（F-027），该函数通过 `importlib.import_module("manimlib")` 获取模块路径，返回 manimlib 父目录的绝对路径，用于定位包内置的 `default_config.yml`。

## 配置初始化后处理

配置加载完成后，两个后处理函数负责将相对配置转换为可用状态：

### update_directory_config()

`update_directory_config()` 函数（F-024）将 `config.directories.base` 与 `config.directories.subdirs` 中各子目录拼接为完整绝对路径。这意味着用户在配置文件中可以指定相对于 base 目录的子目录名，无需写完整路径。

### update_camera_config()

`update_camera_config()` 函数（F-025）处理相机相关配置：
- 根据 CLI 参数或配置文件设置分辨率（通过 `get_resolution_from_args()` 推导）
- 设置帧率 fps
- 使用 `colour.Color` 解析背景颜色字符串为 RGBA 值
- 设置背景透明度

## CLI 参数分组详解

命令行参数由 `parse_cli()` 函数（F-012）使用 argparse 解析，第58-232行定义了所有参数。参数按功能可分为六组。

### 位置参数

位置参数是最常用的参数，无需短/长选项前缀（F-013）：

| 参数 | 类型 | 说明 |
|------|------|------|
| `file` | 路径 | 场景 Python 文件路径 |
| `scene_names` | 字符串列表 | 场景类名列表，`nargs="*"`，可指定多个场景 |

示例：
```bash
# 运行 hello.py 中的 HelloManim 场景
manimgl hello.py HelloManim

# 运行 hello.py 中的多个场景
manimgl hello.py OpeningScene MainScene EndingScene
```

### 画质参数

画质参数控制渲染分辨率，四个参数互斥（F-016）：

| 短选项 | 长选项 | 分辨率 | 说明 |
|--------|--------|--------|------|
| `-l` | `--low_quality` | 480p | 低画质，快速预览用 |
| `-m` | `--medium_quality` | 720p | 中等画质 |
| | `--hd` | 1080p | 全高清 |
| | `--uhd` | 4k | 超高清 |

分辨率通过 `get_resolution_from_args()` 函数（F-028）解析：按 `-l` → `-m` → `--hd` → `--uhd` 的优先级匹配，无匹配参数时返回 `None`，使用配置文件中的默认分辨率。如果同时指定多个画质参数，优先匹配排在前面的。

### 输出参数

输出参数控制渲染结果的输出方式和格式：

| 短选项 | 长选项 | 类型 | 默认值 | 说明 | 事实依据 |
|--------|--------|------|--------|------|----------|
| `-w` | `--write_file` | 布尔值 | `False` | 渲染为视频/图片文件 | F-014 |
| `-s` | `--skip_animations` | 布尔值 | `False` | 跳过动画，仅保存最后一帧 | F-015 |
| `-i` | `--gif` | 布尔值 | `False` | 输出 GIF 动图格式 | F-017 |
| `-t` | `--transparent` | 布尔值 | `False` | 渲染带 alpha 通道的透明背景 | F-018 |
| `-o` | `--open` | 布尔值 | `False` | 渲染完成后自动打开文件 | F-023 |
| | `--finder` | 布尔值 | `False` | 渲染完成后在文件管理器显示 | F-023 |
| `-a` | `--write_all` | 布尔值 | `False` | 写入文件中所有场景 | F-020 |

文件扩展名由 `get_file_ext(args)` 函数确定（F-029）：
- `--transparent` → `.mov`（支持 alpha 通道）
- `--gif` → `.gif`
- 默认 → `.mp4`

**隐式启用规则**（F-023）：`-o/--open` 和 `--finder` 会自动将 `args.write_file` 设为 `True`，无需显式添加 `-w`。例如 `manimgl hello.py HelloManim -o` 等价于 `manimgl hello.py HelloManim -w -o`。

### 调试参数

调试参数用于开发和问题排查：

| 短选项 | 长选项 | 类型 | 说明 | 事实依据 |
|--------|--------|------|------|----------|
| `-n` | `--start_at_animation_number` | 字符串 | 从指定动画编号开始渲染，支持 `"3,6"` 格式表示第3到第6个动画 | F-021 |
| `-e` | `--embed` | 整数 | 在指定行号插入 iPython 断点，进入交互式调试 | F-022 |
| `-q` | `--quiet` | 布尔值 | 安静模式，减少控制台输出 | F-019 |

`-n` 参数对于调试长动画非常有用，无需每次从头开始播放。例如 `-n 5` 从第5个动画开始，`-n 3,7` 只渲染第3到第7个动画。

`-e LINE_NUMBER` 在源码指定行插入 iPython 断点（F-022），允许在动画执行过程中检查变量状态、测试代码、调用场景方法，是调试复杂场景的强大工具。

### 其他参数

| 长选项 | 类型 | 说明 | 事实依据 |
|--------|------|------|----------|
| `--config_file` | 路径 | 指定第三层配置文件路径（优先级高于 custom_config.yml） | F-011 |

## custom_config.yml 示例

在项目根目录创建 `custom_config.yml` 可以设置项目级默认配置。以下是一个典型的配置示例：

```yaml
directories:
  base: "./"
  subdirs:
    output: "videos"
    raster_images: "assets/raster"
    vector_images: "assets/vector"
    sounds: "assets/sounds"
    temporary_storage: "temp"

window:
  position: "+100+100"
  size: [1280, 720]

camera:
  resolution: [1920, 1080]
  fps: 30
  background_color: "#000000"
  background_opacity: 1.0

file_writer:
  write_to_movie: false
  save_last_frame: false
  movie_file_extension: ".mp4"
  png_mode: "RGBA"
```

由于使用递归合并，`custom_config.yml` 只需包含需要覆盖的配置项，未指定的项使用 `default_config.yml` 的默认值。

## 配置项分组

根据 `default_config.yml` 的结构和源码中的处理逻辑，配置项分为以下几组：

### directories 组

控制输出目录和资源目录：
- `base`：基础目录，默认相对于当前工作目录
- `subdirs`：子目录配置，包括 `output`（视频输出）、`raster_images`（光栅图片）、`vector_images`（矢量图片/SVG）、`sounds`（音效）、`temporary_storage`（临时文件）等
- 通过 `update_directory_config()` 拼接为绝对路径（F-024）

### window 组

控制预览窗口行为：
- `position`：窗口位置（X11 格式如 `+100+100`）
- `size`：窗口初始尺寸 `[width, height]`
- 窗口存在时按窗口尺寸绘制而非输出分辨率（`draw_at_window_size`，F-083）

### camera 组

控制相机和渲染参数：
- `resolution`：输出分辨率 `[width, height]`
- `fps`：帧率，默认 30
- `background_color`：背景颜色，支持十六进制或颜色名
- `background_opacity`：背景不透明度，1.0 不透明，0.0 完全透明
- 背景颜色使用 `colour.Color` 解析（F-025）

### file_writer 组

控制文件写入行为：
- `write_to_movie`：是否写入视频文件（CLI `-w` 覆盖此设置）
- `save_last_frame`：是否保存最后一帧（CLI `-s` 覆盖此设置）
- `movie_file_extension`：视频文件扩展名（被 `get_file_ext()` 覆盖，F-029）
- `png_mode`：PNG 图片模式，`"RGB"` 或 `"RGBA"`
- `gif`：是否输出 GIF（CLI `-i` 覆盖）
- `transparent`：是否透明背景（CLI `-t` 覆盖）

## 常量与配置的联动

常量模块（`constants.py`）在导入时从 `manim_config` 动态计算多个关键常量：

- `DEFAULT_RESOLUTION` 从 `manim_config.camera.resolution` 读取（F-031），拆分为 `DEFAULT_PIXEL_WIDTH` 和 `DEFAULT_PIXEL_HEIGHT`
- `ASPECT_RATIO = DEFAULT_PIXEL_WIDTH / DEFAULT_PIXEL_HEIGHT`（F-032）
- `FRAME_HEIGHT` 从配置读取，`FRAME_WIDTH = FRAME_HEIGHT * ASPECT_RATIO`（F-032）
- `FRAME_SHAPE = (FRAME_WIDTH, FRAME_HEIGHT)`（F-032）
- `FRAME_X_RADIUS`、`FRAME_Y_RADIUS` 从帧尺寸派生（F-032）
- `DEFAULT_MOBJECT_COLOR`、`DEFAULT_LIGHT_COLOR`、`DEFAULT_VMOBJECT_STROKE_COLOR`、`DEFAULT_VMOBJECT_FILL_COLOR` 均从配置读取（F-041、F-042）

这意味着通过 `custom_config.yml` 修改相机分辨率会自动改变整个坐标系统——帧宽高比始终与输出分辨率匹配，保证渲染内容在不同分辨率下比例一致。

## 常用命令组合

基于 CLI 参数规范，以下是常用命令组合：

### 预览模式（默认）
```bash
# 打开预览窗口交互查看（不写文件）
manimgl scene.py MyScene

# 低画质快速预览
manimgl scene.py MyScene -l
```

### 渲染输出
```bash
# 1080p 渲染 MP4
manimgl scene.py MyScene -w --hd

# 4K 渲染并自动打开
manimgl scene.py MyScene -w --uhd -o

# 输出 GIF 动图
manimgl scene.py MyScene -w -i

# 输出透明背景视频
manimgl scene.py MyScene -w -t
```

### 调试模式
```bash
# 在第42行插入断点
manimgl scene.py MyScene -e 42

# 从第3个动画渲染到第6个动画
manimgl scene.py MyScene -w -n 3,6

# 只保存最后一帧（快速检查构图）
manimgl scene.py MyScene -s
```

### 批量渲染
```bash
# 渲染文件中所有场景
manimgl scene.py -a -w --hd

# 使用自定义配置文件
manimgl scene.py MyScene -w --config_file ./my_config.yml
```

完整 CLI 参数列表和速查表参见 [ManimGL CLI 参数速查表](/references/cli-parameters-reference.md)。

## 相关概念

- [00 ManimGL 简介与安装](/concepts/00-introduction.md)
- [01 第一个 Scene：Hello World](/concepts/01-hello-world.md)
- [08 常量系统与颜色体系](/concepts/08-constants-and-colors.md)
- [ManimGL CLI 参数速查表](/references/cli-parameters-reference.md)
- [ManimGL 源码结构与核心模块索引](/references/manimgl-source-code.md)
