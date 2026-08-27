---
type: Reference
title: ManimGL CLI 参数速查表
description: ManimGL 命令行接口所有参数的完整速查表，按功能分组，含常用命令示例。
tags: [manimgl, cli, parameters, command-line, reference]
generated: { by: "reference_agent/trae-solo", at: "2026-08-26T00:00:00Z" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: ManimGL 源码事实采集
  - id: self
    resource: /references/cli-parameters-reference.md
    title: ManimGL CLI 参数速查表
---

# ManimGL CLI 参数速查表

本文档基于 `manimlib/config.py` 中 `parse_cli()` 函数（第54-232行）登记所有命令行参数（F-012）。

## 位置参数

| 参数名 | 类型 | 说明 | 事实依据 |
|--------|------|------|----------|
| `file` | 路径 | 场景 Python 文件路径（位置参数） | F-013 |
| `scene_names` | 字符串列表 | 场景类名列表，nargs="*"，可指定多个场景（位置参数） | F-013 |

## 文件与场景选择

| 短选项 | 长选项 | 类型 | 默认值 | 说明 | 事实依据 |
|--------|--------|------|--------|------|----------|
| `-a` | `--write_all` | 布尔值 | `False` | 写入文件中所有场景，而非仅指定的场景 | F-020 |
| `-w` | `--write_file` | 布尔值 | `False` | 渲染并写入视频文件 | F-014 |
| `-o` | `--open` | 布尔值 | `False` | 渲染完成后自动打开输出文件（隐式启用 `--write_file`） | F-023 |
| | `--finder` | 布尔值 | `False` | 渲染完成后在文件管理器中显示输出文件（隐式启用 `--write_file`） | F-023 |
| `-s` | `--skip_animations` | 布尔值 | `False` | 跳过动画，仅保存最后一帧为图片 | F-015 |
| `-n` | `--start_at_animation_number` | 字符串 | | 从指定动画编号开始渲染，支持逗号分隔的起止值（如 `"3,6"` 表示第3到第6个动画） | F-021 |

## 画质与输出格式

| 短选项 | 长选项 | 类型 | 默认值 | 说明 | 事实依据 |
|--------|--------|------|--------|------|----------|
| `-l` | `--low_quality` | 布尔值 | `False` | 低画质渲染，分辨率 480p | F-016 |
| `-m` | `--medium_quality` | 布尔值 | `False` | 中等画质渲染，分辨率 720p | F-016 |
| | `--hd` | 布尔值 | `False` | 高清渲染，分辨率 1080p | F-016 |
| | `--uhd` | 布尔值 | `False` | 超高清渲染，分辨率 4k | F-016 |
| `-i` | `--gif` | 布尔值 | `False` | 输出格式为 GIF 动图（文件扩展名 `.gif`） | F-017、F-029 |
| `-t` | `--transparent` | 布尔值 | `False` | 渲染带 alpha 通道的透明背景视频（文件扩展名 `.mov`） | F-018、F-029 |

> **文件扩展名规则**（F-029）：
> - `--transparent` → `.mov`
> - `--gif` → `.gif`
> - 默认 → `.mp4`

## 调试与交互

| 短选项 | 长选项 | 类型 | 默认值 | 说明 | 事实依据 |
|--------|--------|------|--------|------|----------|
| `-e` | `--embed` | 整数 | | 在指定行号插入 iPython 断点，用于交互式调试 | F-022 |
| `-q` | `--quiet` | 布尔值 | `False` | 安静模式，减少输出信息 | F-019 |

## 其他参数

| 短选项 | 长选项 | 类型 | 默认值 | 说明 | 事实依据 |
|--------|--------|------|--------|------|----------|
| | `--config_file` | 路径 | | 指定自定义配置文件路径（第三级配置，优先级最高） | F-011 |

## 隐式行为

- **`-w/--write_file` 自动启用**（F-023）：当使用 `-o/--open` 或 `--finder` 时，`args.write_file` 自动设为 `True`，无需显式指定 `-w`。

## 分辨率推导逻辑

画质参数通过 `get_resolution_from_args()` 函数（F-028）解析：
- 按 `-l` → `-m` → `--hd` → `--uhd` 优先级匹配
- 无匹配参数时返回 `None`，使用配置文件默认值
- 相机配置通过 `update_camera_config()` 函数（F-025）处理分辨率、fps、背景颜色（使用 `colour.Color` 解析）、背景透明度

## 目录配置

目录路径通过 `update_directory_config()` 函数（F-024）处理：
- 将 `config.directories.base` 与 `config.directories.subdirs` 中各子目录拼接为完整绝对路径

## 常用命令示例

以下示例基于 CLI 参数规范推导的典型用法：

### 基础渲染
```bash
# 渲染指定场景为 MP4（1080p）
manimgl scene.py MyScene -w --hd

# 低画质快速预览
manimgl scene.py MyScene -w -l

# 渲染文件中所有场景
manimgl scene.py -a -w
```

### 输出格式
```bash
# 输出 GIF 动图
manimgl scene.py MyScene -w -i

# 输出透明背景视频
manimgl scene.py MyScene -w -t
```

### 调试与交互
```bash
# 渲染完成后自动打开
manimgl scene.py MyScene -o

# 在第42行插入断点调试
manimgl scene.py MyScene -e 42

# 从第3个动画渲染到第6个动画
manimgl scene.py MyScene -w -n 3,6
```

### 其他
```bash
# 仅保存最后一帧（跳过动画）
manimgl scene.py MyScene -s

# 安静模式渲染 4K 视频
manimgl scene.py MyScene -w --uhd -q

# 使用自定义配置文件
manimgl scene.py MyScene -w --config_file my_config.yml
```

## 相关概念

- [00 ManimGL 简介与整体架构](../concepts/00-introduction.md)
- [02 配置系统](../concepts/02-configuration.md)
- [ManimGL 源码结构与核心模块索引](manimgl-source-code.md)
