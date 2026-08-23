---
type: concept
title: 插件与兼容层
description: scikit-build-core 的 Hatch 插件、setuptools 兼容层、配置提供者插件和 JSON Schema 验证
tags:
  - scikit-build
  - build
  - plugins
  - hatch
  - setuptools
  - compatibility
generated: true
verified: false
status: stable
stale_after: "2026-12-01"
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/hatch/"
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/setuptools/"
---

# 插件与兼容层

scikit-build-core 不仅是独立的 PEP 517 后端，还通过插件系统与 Hatch 集成，并提供 setuptools 兼容层。

## Hatch 插件

[Hatch](https://hatch.pypa.io/) 是一个 Python 项目管理工具，支持自定义构建后端插件。scikit-build-core 提供了 Hatch 构建插件，允许在 Hatch 项目中使用 CMake 构建。

### 配置方式

```toml
[build-system]
requires = ["hatchling", "scikit-build-core", "ninja"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel.hooks.scikit-build]
# scikit-build 配置通过 [tool.scikit-build] 设置
```

或者直接使用 hatch build hook：

```toml
[tool.hatch.build.hooks.scikit-build]
# 启用 scikit-build hatch hook
```

### 工作方式

Hatch 插件在 Hatch 的 wheel 构建流程中插入 scikit-build-core 的 CMake 构建步骤：

1. Hatch 收集 Python 包文件
2. scikit-build-core hook 执行 CMake configure → build → install
3. CMake 安装产物被合并到 Hatch 的 wheel 中
4. Hatch 完成 wheel 打包

### 适用场景

- 项目使用 Hatchling 作为构建后端（纯 Python 部分）
- 只需要 CMake 构建 C 扩展，其余 Python 部分由 Hatch 管理
- 需要 Hatch 的环境管理和版本管理功能

### 限制

- 部分 scikit-build-core 高级功能（如 dynamic metadata 的 CMake 依赖字段）可能不完全支持
- Editable 安装行为可能与纯 scikit-build-core 不同

## setuptools 兼容层

scikit-build-core 提供了 setuptools `build_cmake` 命令，允许在 setuptools 项目中使用 CMake 构建扩展。

### 配置方式

```toml
[build-system]
requires = ["setuptools", "wheel", "scikit-build-core", "ninja"]
build-backend = "setuptools.build_meta"
```

在 `setup.py`（或 `setup.cfg`/`pyproject.toml`）中：

```python
# setup.py
from setuptools import setup
# build_cmake 命令通过 distutils entry-point 自动注册
setup(
    name="my-package",
    cmake_args=["-DCMAKE_BUILD_TYPE=Release"],
    cmake_source_dir=".",
)
```

`pyproject.toml` 中使用 setup keyword 注册：
```toml
[tool.setuptools]
cmake-args = ["-DCMAKE_BUILD_TYPE=Release"]
```

### Entry Points

scikit-build-core 通过 distutils entry-points 注册：

| Entry Point | 目标 | 功能 |
|------------|------|------|
| `distutils.commands: build_cmake` | `setuptools.command:CMakeBuild` | 注册 `build_cmake` 命令 |
| `distutils.setup_keywords: cmake_args` | — | 识别 `cmake_args` setup 参数 |
| `distutils.setup_keywords: cmake_source_dir` | — | 识别 `cmake_source_dir` 参数 |
| `distutils.setup_keywords: cmake_install_dir` | — | 识别 `cmake_install_dir` 参数 |

### 适用场景

- 已有 setuptools 项目，需要逐步迁移到 CMake 构建
- 项目重度依赖 setuptools 生态（entry-points 大量使用、复杂的 setup.py 逻辑）
- 过渡期间的兼容方案

### 建议

对于新项目，推荐直接使用 `build-backend = "scikit_build_core.build"` 而非 setuptools 兼容层。setuptools 兼容层主要用于迁移过渡期。

## 配置提供者插件

通过 `scikit-build-core.config.default` 和 `scikit-build-core.config.override` entry-point groups，可以注册配置提供者插件：

### 默认配置提供者

```toml
[project.entry-points."scikit-build-core.config.default"]
my-config = "my_package.config:default_config"
```

在 TOML 配置加载后、override 应用前，修改默认配置。

### 覆盖配置提供者

```toml
[project.entry-points."scikit-build-core.config.override"]
my-override = "my_package.config:override_config"
```

在所有配置合并后应用最终覆盖。

### 禁用

设置环境变量 `SKBUILD_NO_ENTRYPOINT_CONFIG=1` 可禁用所有外部配置提供者。

## CMake 工具提供者插件

`scikit-build-core.cmake` entry-point group 注册自定义 CMake/Ninja 获取方式：

| Name | 目标 | 功能 |
|------|------|------|
| `ninja` | `builder.get_requires:GetNinja` | Ninja 获取逻辑 |
| `cmake` | `builder.get_requires:GetCMake` | CMake 获取逻辑 |

## JSON Schema 验证

scikit-build-core 通过 `validate_pyproject.tool_schema` entry-point 提供 `[tool.scikit-build]` 的 JSON Schema：

```
scikit-build-core.settings.skbuild_schema:get_skbuild_schema
```

这使得 [validate-pyproject](https://github.com/abravalheri/validate-pyproject) 等工具可以验证 scikit-build-core 配置的正确性。

Schema 文件位于 `resources/scikit-build.schema.json`，支持 IDE 自动补全（VS Code 配合 Even Better TOML 插件）。

## 构建工具提供者

除了内置的 `GetCMake`/`GetNinja`，还可以通过 `scikit-build-core.cmake` entry-point 注册自定义工具获取逻辑。例如，为特定平台提供预编译的 CMake 二进制包。
