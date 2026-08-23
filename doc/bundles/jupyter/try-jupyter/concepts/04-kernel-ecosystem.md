---
type: Concept
title: "内核生态：Pyodide与Xeus多语言内核"
description: "详解Try Jupyter的双Python内核（Pyodide + Xeus-Python）和Xeus多语言内核（C++23/R/SQLite），包括环境定义文件、包管理、内核过滤机制。"
tags: [kernel, pyodide, xeus, python-kernel, cpp-kernel, r-kernel, sqlite-kernel, wasm, emscripten-forge]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: config
    resource: "/references/config-source.md"
    title: "配置文件信源"
  - id: scripts
    resource: "/references/scripts-source.md"
    title: "构建脚本信源"
  - id: pyproject
    resource: "/references/pyproject-source.md"
    title: "pyproject.toml信源"
---

# 内核生态：Pyodide与Xeus多语言内核

Try Jupyter 最显著的特点是支持**多种编程语言内核**，全部运行在浏览器中的WebAssembly（WASM）环境中。这得益于JupyterLite的两种内核技术路线：Pyodide和Xeus。

## 内核技术路线对比

JupyterLite支持两类WASM内核：

| 特性 | Pyodide内核 | Xeus内核 |
|------|------------|---------|
| 内核包 | `jupyterlite-pyodide-kernel` | `jupyterlite-xeus` |
| Python实现 | CPython编译为WASM | 通过xeus-python框架 |
| 多语言支持 | 仅Python | Python/C++/R/SQLite/更多 |
| 包来源 | Pyodide包仓库（pyodide.org） | emscripten-forge + conda-forge |
| 包安装方式 | `piplite`（Pyodide专用） | `micromamba`（conda风格） |
| C扩展支持 | 有限（需Pyodide特定构建） | 更好（通过conda-forge WASM栈） |
| 性能 | 优秀（CPython原生） | 良好（各语言独立WASM运行时） |

## Pyodide Python内核

Pyodide是Mozilla发起的项目，将CPython编译为WebAssembly，使Python能在浏览器中运行。

### 预装特性

Pyodide内核由 `jupyterlite-pyodide-kernel≥0.8.0` 包提供，内置对Python科学计算生态的良好支持，包括NumPy、Pandas、Matplotlib等。Pyodide有自己的包分发系统，预装包通过JupyterLite配置管理。

### 在notebook中安装额外包

```python
import piplite
await piplite.install("package-name")
```

## Xeus多语言内核框架

Xeus是一个C++实现的Jupyter内核协议库，支持将各种编程语言编译为WASM在浏览器中运行。Try Jupyter使用 `jupyterlite-xeus≥5.0.0` 包，搭载了4种Xeus内核。

### Xeus环境定义文件

每个Xeus内核通过一个conda环境YAML文件定义其依赖，文件在 `jupyter_lite_config.json` 的 `XeusAddon.environment_file` 中注册：

```json
{
  "XeusAddon": {
    "environment_file": [
      "environment-cpp.yml",
      "environment-python.yml",
      "environment-r.yml",
      "environment-sqlite.yml"
    ]
  }
}
```

所有环境文件使用统一的channel配置：
- `https://prefix.dev/emscripten-forge-4x`：WASM编译的包（emscripten目标平台）
- `https://prefix.dev/conda-forge`：标准conda-forge包（noarch包可共用）

### Xeus-Python内核（environment-python.yml）

```yaml
name: xeus-python-kernel
channels:
  - https://prefix.dev/emscripten-forge-4x
  - https://prefix.dev/conda-forge
dependencies:
  - xeus-python
  - numpy
  - matplotlib
  - pillow
  - ipywidgets>=8.1.6
  - ipyleaflet
  - scipy
```

| 包 | 用途 |
|----|------|
| `xeus-python` | Python内核实现 |
| `numpy` | 数值计算 |
| `matplotlib` | 数据可视化 |
| `pillow` | 图像处理 |
| `ipywidgets>=8.1.6` | 交互式Widget |
| `ipyleaflet` | 交互式地图 |
| `scipy` | 科学计算 |

> **注意**：Try Jupyter同时拥有Pyodide-Python和Xeus-Python两个Python内核，它们是独立的运行时，包不互通。

### Xeus-C++内核（environment-cpp.yml）

```yaml
name: xeus-cpp-kernel
channels:
  - https://prefix.dev/emscripten-forge-4x
  - https://prefix.dev/conda-forge
dependencies:
  - xeus-cpp
  - symengine
  - xtensor-blas
  - xsimd
```

| 包 | 用途 |
|----|------|
| `xeus-cpp` | C++内核实现（支持C++23） |
| `symengine` | 符号数学库 |
| `xtensor-blas` | 张量运算+BLAS线性代数 |
| `xsimd` | SIMD向量化运算 |

C++内核支持C++23标准，并提供了丰富的数值计算库，使浏览器中的C++科学计算成为可能。站点中提供了3个C++ notebook：
- `cpp.ipynb`：C++基础入门
- `cpp-third-party-libs.ipynb`：第三方库使用演示
- `cpp-tiny-ray-tracer.ipynb`：光线追踪器示例

### Xeus-R内核（environment-r.yml）

```yaml
name: xeus-r-kernel
channels:
  - https://prefix.dev/emscripten-forge-4x
  - https://prefix.dev/conda-forge
dependencies:
  - xeus-r >= 0.7.0
  - r-ggplot2
```

| 包 | 用途 |
|----|------|
| `xeus-r >= 0.7.0` | R语言内核实现 |
| `r-ggplot2` | R数据可视化包 |

R内核支持R语言编程和ggplot2可视化，演示notebook为 `r.ipynb`。

### Xeus-SQLite内核（environment-sqlite.yml）

```yaml
name: xeus-sqlite-kernel
channels:
  - https://prefix.dev/emscripten-forge-4x
  - https://prefix.dev/conda-forge
dependencies:
  - xeus-sqlite
```

| 包 | 用途 |
|----|------|
| `xeus-sqlite` | SQLite内核实现 |

SQLite内核允许在浏览器中直接执行SQL查询，演示notebook为 `sqlite.ipynb`。注意该notebook包含一个预期的错误信息 `"Error: no such table: players"`（在已知警告中注册），用于演示错误处理。

## 内核过滤机制

Xeus构建默认可能包含更多内核（如xeus-lua、xeus-rust等），Try Jupyter通过后处理脚本 `scripts/filter_xeus_kernels.py` 精简内核列表：

### 保留的内核（KERNELS_TO_KEEP）

```python
KERNELS_TO_KEEP = {"xcpp23", "xc23", "xr", "xpython", "xsqlite"}
```

| 内核ID | 对应环境 | 语言 |
|--------|---------|------|
| `xpython` | environment-python.yml | Python (Xeus) |
| `xcpp23` | environment-cpp.yml | C++23 |
| `xc23` | environment-cpp.yml | C++23（备用ID） |
| `xr` | environment-r.yml | R |
| `xsqlite` | environment-sqlite.yml | SQLite |

> C++内核保留两个ID（`xcpp23`和`xc23`）以兼容不同版本的内核标识。

### 过滤流程

1. 读取 `dist/xeus/kernels.json`（JupyterLite构建生成的内核列表）
2. 过滤出kernel ID在白名单中的条目
3. 写回精简后的kernels.json

此步骤的目的：
- 减小站点体积（不打包未使用的内核WASM文件）
- 简化内核选择器（不让用户看到太多内核选项）
- 确保只展示经过测试的内核

## 用户视角的内核选择

在JupyterLab界面中，用户可以通过右上角的内核选择器切换内核：

```
Kernel → Change Kernel → 选择内核
```

可选内核包括：
- **Python (Pyodide)**：Pyodide内核（默认）
- **Python (Xeus)**：Xeus-Python内核
- **C++23**：Xeus-Cpp内核
- **R**：Xeus-R内核
- **SQLite**：Xeus-SQLite内核

## 添加自定义内核

要添加新的Xeus内核（如Julia、Ruby等）：

1. 在emscripten-forge或conda-forge中确认存在对应的xeus内核包（如xeus-julia）
2. 创建新的环境文件 `environment-julia.yml`：
   ```yaml
   name: xeus-julia-kernel
   channels:
     - https://prefix.dev/emscripten-forge-4x
     - https://prefix.dev/conda-forge
   dependencies:
     - xeus-julia
   ```
3. 在 `jupyter_lite_config.json` 的 `XeusAddon.environment_file` 数组中添加该文件
4. 在 `scripts/filter_xeus_kernels.py` 的 `KERNELS_TO_KEEP` 集合中添加对应的内核ID
5. 重新构建站点

## 相关概念

- [架构总览](02-architecture-overview.md)
- [配置系统](03-configuration-system.md)
- [构建管线](05-build-pipeline.md)
- [Notebook内容与数据](06-notebooks-and-content.md)
