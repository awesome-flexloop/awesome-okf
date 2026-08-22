---
type: concept
title: Wheel 与 SDist 打包
description: scikit-build-core 如何组装 wheel 文件和 sdist 源码包，文件发现规则与安装目录控制
tags:
  - scikit-build
  - build
  - wheel
  - sdist
  - packaging
generated: true
verified: false
status: stable
stale_after: "2026-12-01"
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/settings/skbuild_model.py"
---

# Wheel 与 SDist 打包

## Wheel 打包

Wheel（`.whl`）是 Python 的二进制分发包格式，包含编译后的扩展模块和 Python 源码。scikit-build-core 的 wheel 组装分为两部分：CMake 安装产物 + Python 包文件。

### 安装目录（platlib vs purelib）

Wheel 有两个安装位置：

| 目录 | 内容 | 自动判断条件 |
|------|------|-------------|
| `platlib` | 含编译扩展的包 | 存在 CMake 编译产物或 `wheel.platlib = true` |
| `purelib` | 纯 Python 包 | `wheel.cmake = false` 且无扩展 |

通过 `wheel.platlib` 可显式控制：
```toml
[tool.scikit-build.wheel]
platlib = true   # 强制安装到 platlib
```

### Python 包发现

`wheel.packages` 控制哪些 Python 包被打包：

```toml
# 方式1：手动列出包名（自动从 src/ 或根目录查找）
[tool.scikit-build.wheel]
packages = ["my_package", "my_package.tests"]

# 方式2：{源目录: 目标包名} 映射（灵活控制路径）
[tool.scikit-build.wheel.packages]
"src/my_package" = "my_package"

# 方式3：null（默认）—— 自动发现
# 扫描 src/ 或根目录下的 Python 包（含 __init__.py 的目录）
```

### install-dir：CMake 安装目标目录

`wheel.install-dir` 控制 CMake `install()` 安装到 wheel 内的子目录：

```toml
[tool.scikit-build.wheel]
install-dir = "my_package"   # CMake 产物安装到 my_package/ 下
```

CMakeLists.txt 中使用 `SKBUILD_PROJECT_NAME` 或直接写目标路径：
```cmake
install(TARGETS _core DESTINATION my_package)
```

### 文件排除

`wheel.exclude` 使用 glob 模式排除文件：

```toml
[tool.scikit-build.wheel]
exclude = [
    "**/*.pyc",
    "**/__pycache__/**",
    "**/tests/**",
]
```

### 强制包含

`wheel.force-include` 将任意文件映射到 wheel 内路径：

```toml
[tool.scikit-build.wheel.force-include]
"config/default.toml" = "my_package/default_config.toml"
"../LICENSE" = "my_package/../../LICENSE"
```

### 许可证文件

PEP 639 许可证文件处理：

- `wheel.license-files` 默认为 PEP 639 标准 glob（`LICENSE*`、`COPYING*` 等）
- 自动检测根目录和 `src/` 目录下的许可证文件

### Wheel 标签

Wheel 文件名包含平台标签：

```
mypackage-0.1.0-cp312-cp312-manylinux_2_28_x86_64.whl
            ─┬───  ─┬───  ──────────┬─────────────
             │      │                └── 平台标签
             │      └── ABI 标签
             └── Python 标签
```

标签控制：

- `wheel.py-api`：Python 标签（如 `"cp39"`、`"abi3"`、`"py3"`）
  - `"abi3"`：使用稳定 ABI（需要 CMake 中定义 `Py_LIMITED_API`）
  - `"py3"`：纯 Python
  - `"cp3X"`：特定 CPython 版本
- `wheel.tags`（override-only）：完全自定义标签列表
- macOS universal2 自动检测（arm64 + x86_64 双架构）

### Build Tag

`wheel.build-tag` 设置 wheel build tag（用于同一版本的多次构建）：

```toml
[tool.scikit-build.wheel]
build-tag = "1"
```

### 可重现构建

`wheel.reproducible = true`（0.18+ 默认）时：

- 文件 mtime 使用 `SOURCE_DATE_EPOCH` 或固定时间
- 文件权限统一为 0o644（文件）/0o755（目录）
- RECORD 文件按路径排序
- gzip 压缩使用固定 mtime

## SDist 打包

SDist（`.tar.gz`）是源码分发包，包含构建 wheel 所需的所有文件。

### 文件包含模式

`sdist.inclusion-mode`（0.12+）控制 sdist 文件选择策略：

| 模式 | 行为 | 版本要求 |
|------|------|---------|
| `default` | git-tracked 文件 + scikit-build 自动添加文件 | 0.12+ |
| `classic` | scikit-build 经典版行为（手动 include/exclude） | 所有版本 |
| `manual` | 仅显式 include 的文件 + 必需文件 | 0.12+ |
| `explicit` | 仅 include 指定文件 | 0.12+ |

默认行为：使用 git ls-files 获取 tracked 文件，再自动添加必要文件（pyproject.toml、CMakeLists.txt、src/ 等）。

### Include/Exclude 规则

```toml
[tool.scikit-build.sdist]
include = [
    "src/**/*.pyx",
    "cmake/**/*.cmake",
]
exclude = [
    "**/*.pyc",
    "tests/**",
    "docs/**",
]
```

排除优先于包含。`force-include` 始终生效。

### CMake 执行

`sdist.cmake = true` 时，构建 sdist 前先执行 CMake configure（用于生成需要包含在 sdist 中的文件，如配置头文件）：

```toml
[tool.scikit-build.sdist]
cmake = true
```

### 符号链接处理

`sdist.resolve-symlinks` 控制符号链接处理：

| 值 | 行为 |
|----|------|
| `all` | 所有符号链接解析为实际文件 |
| `external` | 仅解析指向 sdist 外的链接 |
| `none` | 保留符号链接 |
| `classic` | 经典 scikit-build 行为 |

## 动态元数据

`[project]` 表中的动态字段通过 metadata provider 插件填充：

```toml
[project]
dynamic = ["version", "description"]
```

内置 provider：

- `scikit_build_core.metadata.regex`：从文件中正则提取版本
- `scikit_build_core.metadata.template`：模板化元数据
- `scikit_build_core.metadata.setuptools_scm`：集成 setuptools-scm
- `scikit_build_core.metadata.fancy_pypi_readme`：Markdown 转 RST 描述
