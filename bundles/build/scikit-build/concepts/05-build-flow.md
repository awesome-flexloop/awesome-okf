---
type: concept
title: 构建流程
description: scikit-build-core 从 PEP 517 调用到最终 wheel 产出的完整构建链路
tags:
  - scikit-build
  - build
  - pipeline
  - wheel
generated: true
verified: false
status: stable
stale_after: "2026-12-01"
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/build/__init__.py"
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/builder/builder.py"
---

# 构建流程

本文描述 `build_wheel` 从被前端调用到产出 `.whl` 文件的完整流程。

## 总体流程图

```
PEP 517 前端调用 build_wheel()
        │
        ▼
  ┌─ _build_wheel_impl() ─────────────────────────────┐
  │                                                     │
  │  1. SettingsReader 解析配置                        │
  │  2. 搜索 CMake/Ninja 程序                          │
  │  3. 创建临时构建目录（或复用 build-dir）            │
  │  4. 生成 CMakeInit.txt                             │
  │  5. 写入 CMake File API query                      │
  │  6. CMaker.configure()                             │
  │  7. CMaker.build()                                 │
  │  8. CMaker.install() → wheel 临时目录              │
  │  9. 复制 Python 包到 wheel 目录                    │
  │ 10. 处理可编辑安装（如需要）                       │
  │ 11. 生成 METADATA/WHEEL/RECORD/entry_points.txt    │
  │ 12. 打包为 .whl 文件                               │
  │                                                     │
  └─────────────────────────────────────────────────────┘
        │
        ▼
  返回 wheel 文件名
```

## 阶段详解

### 阶段1：配置解析

`SettingsReader.from_file()` 完成：

1. 读取 `pyproject.toml`
2. 创建 `SourceChain`（EnvSource → ConfSource → TOMLSource）
3. 构建 `ScikitBuildSettings` dataclass
4. 处理 minimum-version 迁移
5. 匹配并应用 override 条件块
6. 加载 entry-point 配置提供者
7. 严格验证（`validate_may_exit()`）

### 阶段2：程序搜索

通过 `program_search.py` 中的函数搜索构建工具：

- `get_cmake_programs()`：按 pip 模块 → PATH 的顺序搜索 CMake
- `get_ninja_programs()`：按 pip 模块 → PATH 的顺序搜索 Ninja
- `best_program()`：选择版本满足 SpecifierSet 的第一个程序
- 如果未找到 Ninja 且 `ninja.make-fallback = true`，回退到 Make

### 阶段3：构建目录准备

- 如果 `build-dir` 为空，使用 `tempfile.mkdtemp()` 创建临时目录
- 如果指定了 `build-dir`，复用该目录（增量构建）
- `cmake.fresh = true` 时删除构建目录重新创建
- macOS 上解析 `ARCHFLAGS` 环境变量确定目标架构

### 阶段4：CMake Configure

1. 创建 `CMaker` 实例
2. `CMaker.init_cache()` 写入 `CMakeInit.txt`：
   - `SKBUILD_PROJECT_NAME/VERSION`
   - `Python_EXECUTABLE/VERSION/INCLUDE_DIR/LIBRARY/SOABI`
   - `CMAKE_MODULE_PATH/PREFIX_PATH`
   - 用户 `cmake.define` 项
3. `CMaker.configure()` 执行 cmake 命令：
   ```
   cmake -S <source_dir> -B <build_dir>
         -G Ninja
         -C <build_dir>/CMakeInit.txt
         -DCMAKE_BUILD_TYPE=Release
         -D<user defines...>
         <cmake.args...>
   ```
4. 读取 CMake File API reply，获取 CodeModel（目标列表、安装路径等）

### 阶段5：CMake Build

`CMaker.build()` 执行：

```
cmake --build <build_dir>
       --config Release          # 多配置生成器
       --target <targets...>     # build.targets 或默认 all
       -v                        # build.verbose
       -- <tool_args...>         # build.tool-args
```

构建目标：
- 如果 `build.targets` 非空，仅构建指定目标
- 否则构建 CMake 默认目标（通常是 all）

### 阶段6：CMake Install

`CMaker.install()` 执行：

```
cmake --install <build_dir>
         --prefix <wheel_temp>/platlib_or_purelib
         --config Release
         --component <components...>  # install.components
         --strip                    # install.strip
```

安装目标由 `install.targets` 控制（为空则安装全部）。

### 阶段7：Python 包收集

CMake install 只处理 C++ 编译产物。Python 源码包通过以下方式收集：

- `wheel.packages` 显式指定包列表或 `{src: dest}` 映射
- 未指定时自动发现（扫描 `src/` 或根目录下的 Python 包）
- `wheel.exclude` 排除指定模式
- `wheel.force-include` 强制包含额外文件

### 阶段8：Editable 处理（仅 build_editable）

- `editable.mode = "redirect"`：生成 `_editable_redirect.py` 和 `.pth` 文件，使用 `sys.meta_path` finder 重定向导入
- `editable.mode = "inplace"`：生成简单 `.pth` 文件指向源码目录
- 详见[可编辑安装](08-editable-installs.md)

### 阶段9：Wheel 元数据生成

生成标准 wheel 元数据文件：

| 文件 | 内容 |
|------|------|
| `METADATA` | 包名、版本、依赖、描述（PEP 621） |
| `WHEEL` | Wheel 版本、构建标签、是否纯 Python |
| `RECORD` | 所有文件的 SHA256 哈希和大小 |
| `entry_points.txt` | console_scripts/gui_scripts（如有） |
| `LICENSE/*` | 许可证文件（PEP 639） |

### 阶段10：打包

将 wheel 临时目录中的所有文件打包为 ZIP 格式的 `.whl` 文件，文件名遵循 PEP 427 规范：

```
{distribution}-{version}(-{build_tag})?-{python_tag}-{abi_tag}-{platform_tag}.whl
```

例如：`my_package-0.1.0-cp312-cp312-linux_x86_64.whl`

## 架构检测

在构建前，`builder/builder.py` 中的函数处理架构相关逻辑：

- `get_archs(env, cmake_args)`：从 `ARCHFLAGS` 和 `CMAKE_OSX_ARCHITECTURES` 提取目标架构
- `archs_to_tags(archs)`：双架构 `["arm64", "x86_64"]` 转换为 `["universal2"]`
- 平台标签由 `sysconfig.get_platform()` 确定，可通过 `wheel.tags` override

## SDist 构建差异

`build_sdist` 不执行 CMake，而是：

1. 基于 pathspec 的 include/exclude 规则选择文件
2. 如 `sdist.cmake = true`，先执行 CMake configure 生成文件
3. 按 PEP 625 格式打包为 `.tar.gz`
4. 默认 `sdist.reproducible = true`，使用固定时间戳

## 可重现构建

设置 `wheel.reproducible = true`（0.18+ 默认开启）时：

- SOURCE_DATE_EPOCH 环境变量控制时间戳
- 文件权限归一化
- RECORD 中的文件顺序排序
- gzip 压缩设置固定 mtime

## 构建失败处理

- `FailedLiveProcessError`：CMake configure/build/install 命令失败时抛出，包含退出码和 stderr
- `CMakeConfigError`：CMakeLists.txt 配置错误
- `CMakeNotFoundError`：找不到满足版本要求的 CMake
- 默认通过 `_exit_on_failed_live_process()` 上下文管理器转为 `SystemExit(1)`
