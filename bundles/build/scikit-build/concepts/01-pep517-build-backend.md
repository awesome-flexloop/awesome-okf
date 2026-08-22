---
type: concept
title: PEP 517 构建后端接口
description: scikit-build-core 如何实现 PEP 517 构建后端接口，与 pip/build 等前端工具交互
tags:
  - scikit-build
  - build
  - pep517
  - build-backend
generated: true
verified: false
status: stable
stale_after: "2026-12-01"
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/build/__init__.py"
---

# PEP 517 构建后端接口

## PEP 517 概述

[PEP 517](https://peps.python.org/pep-0517/) 定义了 Python 构建前端（pip、build 等）与构建后端（setuptools、scikit-build-core 等）之间的标准接口。构建后端通过一组约定的函数签名响应前端的构建请求。

scikit-build-core 在 `scikit_build_core.build` 模块中实现了 PEP 517 接口。

## 必需钩子

### build_wheel

```python
def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, str | list[str]] | None = None,
    metadata_directory: str | None = None,
) -> str:
```

当前端（pip）执行 `pip install .` 或 `python -m build --wheel` 时调用。scikit-build-core 的实现调用内部 `_build_wheel_impl(..., editable=False)`，执行完整的 CMake 配置→构建→安装→wheel 打包流程，返回 wheel 文件名字符串。

### build_sdist

```python
def build_sdist(
    sdist_directory: str,
    config_settings: dict[str, str | list[str]] | None = None,
) -> str:
```

执行 `python -m build --sdist` 时调用。委托给 `build/sdist.py` 中的实现，基于 pathspec 的 include/exclude 规则打包源码。返回 sdist 文件名字符串。

## 可选钩子

### build_editable

```python
def build_editable(
    wheel_directory: str,
    config_settings: dict[str, str | list[str]] | None = None,
    metadata_directory: str | None = None,
) -> str:
```

执行 `pip install -e .`（可编辑安装）时调用。scikit-build-core 支持两种 editable 模式（redirect 和 inplace），详见[可编辑安装](08-editable-installs.md)。

### get_requires_for_build_*

```python
def get_requires_for_build_wheel(
    config_settings: dict[str, str | list[str]] | None = None,
) -> list[str]:

def get_requires_for_build_sdist(...) -> list[str]:
def get_requires_for_build_editable(...) -> list[str]:
```

返回构建 wheel/sdist/editable 之前需要安装的额外依赖列表。scikit-build-core 在此动态计算是否需要 cmake、ninja 等构建工具依赖。

### prepare_metadata_for_build_*

```python
def prepare_metadata_for_build_wheel(
    metadata_directory: str,
    config_settings: dict[str, str | list[str]] | None = None,
) -> str:
```

可选钩子，允许前端在完整构建之前预先获取包元数据（名称、版本、依赖等）。scikit-build-core 在满足以下条件时提供此钩子：

- pyproject.toml 中没有使用 `if.failed` 或 `if.any.failed` 条件覆盖（即元数据不依赖构建结果）
- 此时可以安全地仅解析 `[project]` 表而不执行 CMake

## config_settings 传递

前端通过 `config_settings` 参数向构建后端传递构建时配置：

```bash
# pip 方式
pip install . --config-setting=cmake.build-type=Debug

# build 方式
python -m build -Ccmake.build-type=Debug -Cbuild.verbose=true
```

在 scikit-build-core 中，config_settings 是三源配置之一（优先级高于 TOML，低于环境变量），详见[配置系统详解](03-settings-system.md)。

## 构建生命周期

scikit-build-core 在 `build_wheel` 中执行以下步骤：

```
1. 读取 pyproject.toml 和 config_settings
2. SettingsReader 解析并验证配置
3. 搜索 CMake/Ninja 程序
4. 生成 CMakeInit.txt 初始缓存文件
5. 创建（或复用）CMake 构建目录
6. cmake -S source -B build 配置
7. 通过 CMake File API 读取 CodeModel
8. cmake --build build 编译
9. cmake --install build 安装到 wheel 临时目录
10. 收集 Python 包文件和 CMake 安装产物
11. 生成 METADATA/WHEEL/RECORD 等 wheel 元数据
12. 打包为 .whl 文件
```

## 多前端兼容

scikit-build-core 兼容所有遵循 PEP 517 的前端：

| 前端 | 命令 | 说明 |
|------|------|------|
| pip | `pip install .` / `pip wheel .` | 最常用，自动安装构建依赖 |
| build | `python -m build` | 参考实现，支持 wheel/sdist |
| cibuildwheel | CI wheel 构建 | 跨平台 wheel 构建 |
| uv | `uv build` / `uv pip install` | 高性能 Rust 实现 |
| Hatch | `hatch build` | 通过 Hatch 插件集成 |
