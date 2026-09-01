---
type: concept
title: 动态元数据
description: scikit-build-core 的动态元数据插件系统，从源码/文件/命令动态提取版本号、描述等项目元数据
tags:
  - scikit-build
  - build
  - metadata
  - dynamic
generated: true
verified: false
status: stable
stale_after: "2026-12-01"
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/metadata/"
---

# 动态元数据

PEP 621 允许 `[project]` 表中声明 `dynamic` 字段，表示某些元数据不在 pyproject.toml 中静态定义，而是在构建时由构建后端动态提供。scikit-build-core 通过 entry-point 插件系统支持多种动态元数据提供者。

## 基本配置

```toml
[project]
name = "my-package"
dynamic = ["version", "description", "readme"]
```

`dynamic` 数组列出需要动态填充的字段，scikit-build-core 通过 `[tool.scikit-build.metadata]` 配置对应的提供者。

## 内置元数据提供者

### 1. regex：正则提取版本

从源文件中正则提取版本号：

```toml
[tool.scikit-build.metadata.version]
provider = "scikit_build_core.metadata.regex"
input = "src/my_package/__init__.py"
# 默认正则：r'(?i)^(__version__|VERSION) *= *([\'"])v?(?P<value>.+?)\2'
regex = '''__version__\s*=\s*["']([^"']+)["']'''
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | 要搜索的文件路径（相对于 source-dir） | — |
| `regex` | Python 正则表达式，须包含 `(?P<value>...)` 命名组 | 默认匹配 `__version__ = "x.y.z"` |
| `normalize` | 是否规范化版本号（PEP 440） | `true` |

如果版本写在 `__init__.py` 中：
```python
# src/my_package/__init__.py
__version__ = "1.2.3"
```
无需自定义 regex，默认即可工作。

### 2. setuptools-scm：Git 标签版本

使用 setuptools-scm 从 Git 标签自动推断版本：

```toml
[tool.scikit-build.metadata.version]
provider = "scikit_build_core.metadata.setuptools_scm"
```

需要在 `[build-system.requires]` 中添加 `setuptools-scm`。版本格式遵循 setuptools-scm 规则（如 `1.2.3.dev0+gabc123`）。

### 3. template：模板化元数据

使用字符串模板从其他字段组合元数据：

```toml
[tool.scikit-build.metadata]
provider = "scikit_build_core.metadata.template"
```

用于复杂的元数据组合场景。

### 4. fancy-pypi-readme：Markdown 描述

将 Markdown README 转换为 PyPI 兼容格式（支持 GitHub Flavored Markdown 扩展）：

```toml
[tool.scikit-build.metadata.readme]
provider = "scikit_build_core.metadata.fancy_pypi_readme"
input = "README.md"
content-type = "text/markdown"
```

## 元数据提供者接口

动态元数据提供者通过 `scikit-build-core.metadata` entry-point group 注册。每个提供者是一个函数，接收配置参数，返回字段值：

```python
def my_metadata_provider(
    field: str,
    pyproject_path: Path,
    config: dict,
    state: str,
    # 可能还接收 builder/cmaker 等构建上下文
) -> str | dict:
    """返回字段的动态值"""
    ...
```

通过 entry-points 注册：
```toml
[project.entry-points."scikit-build-core.metadata"]
my-provider = "my_package.metadata:my_provider"
```

## 动态字段与构建阶段

| 字段 | 何时可用 | 是否需要构建 |
|------|---------|-------------|
| `version` | 配置解析阶段 | ❌ 不需要 CMake 构建 |
| `description` | 配置解析阶段 | ❌ |
| `readme` | 配置解析阶段 | ❌ |
| `authors` | 配置解析阶段 | ❌ |
| 依赖版本 | 依赖 CMake 结果 | ✅ 需要 configure |

当动态字段依赖 CMake 构建结果时，`prepare_metadata_for_build_wheel` 钩子不可用（因为它要求在构建前返回元数据）。

## 静态元数据回退

如果 pyproject.toml 中不声明 `dynamic`，所有元数据从 `[project]` 表静态读取，使用 vendored 的 `pyproject_metadata` 库解析。

## 推荐配置

### 版本号从 __init__.py 提取

```toml
[project]
name = "my-package"
dynamic = ["version"]

[tool.scikit-build.metadata.version]
provider = "scikit_build_core.metadata.regex"
input = "src/my_package/__init__.py"
```

### 版本从 Git 标签（setuptools-scm）

```toml
[build-system]
requires = ["scikit-build-core>=0.10", "ninja", "setuptools-scm>=8"]

[project]
name = "my-package"
dynamic = ["version"]

[tool.scikit-build.metadata.version]
provider = "scikit_build_core.metadata.setuptools_scm"
```
