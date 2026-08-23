---
type: reference
title: scikit-build-core 配置项速查
description: pyproject.toml [tool.scikit-build] 配置项完整速查表，含字段名、类型、默认值、版本要求
tags:
  - scikit-build
  - build
  - configuration
  - reference
generated: true
verified: true
status: stable
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/settings/skbuild_model.py"
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/settings/skbuild_read_settings.py"
---

# scikit-build-core 配置项速查

本文档列出 `[tool.scikit-build]` 表下所有配置项的字段名、类型、默认值和版本要求。

## 顶层配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `minimum-version` | `str` | — | 最低 scikit-build-core 版本，设为 `"build-system.requires"` 自动提取 |
| `build-dir` | `str` | `""`（临时目录） | CMake 构建目录，空值使用临时目录 |
| `cmake.version` | `str (SpecifierSet)` | `None` | CMake 版本约束 |
| `strict-config` | `bool` | `true` | 未识别配置项是否报错 |
| `experimental` | `bool` | `false` | 启用实验性功能 |

## [tool.scikit-build.cmake]

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `version` | `str (SpecifierSet)` | `None` | 兼容的 CMake 版本范围 |
| `args` | `list[str]` | `[]` | 传递给 cmake configure 的额外参数 |
| `define` | `dict[str, Any]` | `{}` | CMake 定义项（-D 标志） |
| `build-type` | `str` | `"Release"` | CMake 构建类型（Release/Debug/RelWithDebInfo/MinSizeRel） |
| `source-dir` | `str (Path)` | `"."` | CMake 源目录 |
| `toolchain-file` | `str (Path)` | `None` | CMake 工具链文件路径（override-only） |
| `fresh` | `bool` | `false` | 每次配置前清空构建缓存 |
| `python-hints` | `bool` | `false` | 使用 Python 路径提示 CMake FindPython |

## [tool.scikit-build.ninja]

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `version` | `str (SpecifierSet)` | `">=1.5"` | Ninja 版本约束 |
| `make-fallback` | `bool` | `true` | 找不到 Ninja 时回退到 Make |

## [tool.scikit-build.wheel]

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `packages` | `list[str] / dict[str,str]` | `None`（自动发现） | Python 包列表或 {源: 目标} 映射 |
| `py-api` | `str` | `""` | Python API 标签（如 `cp39`、`abi3`） |
| `install-dir` | `str` | `""` | CMake install 目录 |
| `license-files` | `list[str]` | `None`（PEP 639 默认） | 许可证文件 glob 列表 |
| `cmake` | `bool` | `true` | 是否执行 CMake 构建 |
| `platlib` | `bool` | `None`（自动判断） | 是否安装到 platlib（纯 Python 为 purelib） |
| `exclude` | `list[str]` | `[]` | 排除的文件 glob 模式 |
| `build-tag` | `str` | `""` | Wheel build tag |
| `tags` | `list[str]` | `None`（override-only） | 自定义 wheel 标签 |
| `force-include` | `dict[str,str]` | `{}` | 强制包含的 {源: 目标} 文件映射 |
| `reproducible` | `bool` | `false`（0.18+ 默认 true） | 可重现构建 |

## [tool.scikit-build.sdist]

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `include` | `list[str]` | `[]` | 额外包含的 glob 模式 |
| `exclude` | `list[str]` | `[]` | 排除的 glob 模式 |
| `reproducible` | `bool` | `true` | 可重现 sdist |
| `cmake` | `bool` | `false` | sdist 时执行 CMake（生成文件等） |
| `force-include` | `dict[str,str]` | `{}` | 强制包含的文件映射 |
| `inclusion-mode` | `str` | `None`（版本门控 0.12+） | 文件包含模式：classic/default/manual/explicit |
| `resolve-symlinks` | `str` | `None` | 符号链接解析：all/external/none/classic |

## [tool.scikit-build.editable]

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `mode` | `"redirect" / "inplace"` | `"redirect"` | Editable 模式 |
| `verbose` | `bool` | `true` | Editable 导入时输出日志 |
| `rebuild` | `bool` | `false` | 导入时自动重编译 |
| `rebuild-dir` | `str` | `""` | 重编译产物安装目录（独立于源码树） |

## [tool.scikit-build.build]

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `tool-args` | `list[str]` | `[]` | 传递给构建工具（ninja/make）的参数 |
| `targets` | `list[str]` | `[]` | CMake 构建目标列表 |
| `verbose` | `bool` | `false` | 详细构建输出 |

## [tool.scikit-build.install]

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `components` | `list[str]` | `[]` | CMake install component 列表 |
| `targets` | `list[str]` | `[]` | CMake install target 列表 |
| `strip` | `bool` | `None` | strip 二进制文件（0.18+ 默认根据 build-type 自动判断） |

## [tool.scikit-build.logging]

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `level` | `str` | `"WARNING"` | 日志级别 |

## 配置来源优先级

配置从三个来源合并，优先级从高到低：

1. **环境变量**（`SKBUILD_*`）：大写、下划线分隔，如 `SKBUILD_CMAKE_BUILD_TYPE=Release`
2. **Config Settings**（`pip install --config-settings` 或 `build -C`）：点分键名，如 `-Ccmake.build-type=Release`
3. **TOML 配置**（`pyproject.toml [tool.scikit-build]`）：嵌套表

> **重要**：`dict` 类型字段（如 `cmake.define`、`wheel.force-include`）跨源**合并**（键值叠加），而非替换。标量和列表取最高优先级源的值。

## override-only 字段

以下字段只能在 `[tool.scikit-build.overrides]` 条件块中或通过 config settings/环境变量设置，不能在静态 `[tool.scikit-build]` 中直接设置：

- `cmake.toolchain-file`
- `wheel.tags`
- `variant`
- `fail`

## Overrides 条件配置

```toml
[tool.scikit-build.overrides]
# 按系统平台覆盖
if.system = "darwin"
cmake.args = ["-DCMAKE_OSX_DEPLOYMENT_TARGET=10.15"]

# 按 Python 版本覆盖
if.implementation-name = "cpython"
if.platform-python-version = ">=3.12"
wheel.py-api = "cp312"

# 多条件组合（all=AND，any=OR）
if.any.system = "windows"
if.any.platform_machine = "arm64"
cmake.define.CROSS_COMPILING = "ON"
```

支持的条件字段：`system`、`sys_platform`、`platform_machine`、`platform_python_implementation`（或 `implementation_name`）、`implementation_version`、`platform_release`、`platform_version`、`platform_system`、`python_version`、`platform_in_virtualenv`、`ci`、`arch`（XCode archs）。
