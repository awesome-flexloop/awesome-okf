---
type: Concept
title: Pyodide 与 Xeus 内核对比选型
description: Pyodide 和 Xeus 两种 JupyterLite 内核的差异对比、适用场景、包管理方式和配置区别
tags: [kernel, pyodide, xeus, comparison, emscripten-forge]
difficulty: intermediate
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: kernel-comparison
    resource: /references/conf-py-source.md
    title: Pyodide/Xeus 配置对比
---

## 两种内核简介

JupyterLite 支持多种在浏览器中运行的 Jupyter 内核，sphinx-demo 展示了两种最主流的选择：

| 特性 | Pyodide 内核 | Xeus Python 内核 |
|------|-------------|-----------------|
| 包名 | `jupyterlite-pyodide-kernel` | `jupyterlite-xeus` |
| Python 实现 | CPython 编译为 WebAssembly | Xeus 框架 + emscripten-forge 包 |
| 默认内核名 | `"python"` | `"XPython"` |
| 包安装时机 | 运行时（浏览器端） | 构建时（CI/本地构建阶段） |
| 包安装方式 | `piplite.install()` | `environment.yml` 预编译 |
| 支持的包 | PyPI 上的纯 Python 包 + Pyodide 预置包 | emscripten-forge 仓库的预编译包 |
| C 扩展支持 | Pyodide 预置的科学计算包 | emscripten-forge 编译的 WASM 包 |

## 关键差异详解

### 差异 1：包管理方式

**Pyodide**：在 Notebook 中运行时安装

```python
import piplite
await piplite.install("sympy")
import sympy
```

用户首次运行需要包的代码单元时，piplite 会从 PyPI（或自定义 wheelhouse）下载包并安装到浏览器中。优点是灵活——用户可以即时安装需要的包；缺点是首次安装需要等待下载，且只支持纯 Python 包和 Pyodide 已移植的包。

**Xeus**：在构建 JupyterLite 时预安装

```yaml
# environment.yml
name: xeus-python-kernel
channels:
  - https://repo.mamba.pm/emscripten-forge
  - conda-forge
dependencies:
  - numpy
  - scipy
  - matplotlib
  - sympy
  - ipycanvas
```

`jupyterlite-xeus` 在构建时（`jupyter lite build`）使用 micromamba 解析依赖并下载预编译的 WASM 包，将它们打包到站点中。用户打开 Notebook 时所有包已就绪，无需等待安装。

### 差异 2：conf.py 配置差异

两个内核的 conf.py 95% 相同，差异仅在以下位置：

| 配置项 | Pyodide | Xeus |
|--------|---------|------|
| `requirements.txt` | `jupyterlite-pyodide-kernel` | `jupyterlite-xeus` |
| `jupyter-lite.json` → `defaultKernelName` | `"python"` | `"XPython"` |
| `jupyter-lite.json` → `appName` | 含 `(Pyodide)` | 含 `(Xeus)` |
| `html_theme_options` → `switcher.version_match` | `"pyodide"` | `"xeus"` |
| `html_context` → `doc_path` | `"pyodide-kernel-example/..."` | `"xeus-kernel-example/..."` |
| `environment.yml` | 不需要 | 需要，定义预装包 |
| CI 构建 | 无需额外工具 | 需要 micromamba 求解依赖 |

### 差异 3：CI/CD 构建需求

Pyodide 内核的 CI 构建只需要标准 Python 环境。Xeus 内核的构建额外需要 micromamba（conda-forge 的包管理器），因为它需要在构建阶段求解 WASM 包依赖。这也是 demo 的 CI 工作流中 Xeus 构建步骤有条件地安装 micromamba 的原因。

## 如何选择

### 选择 Pyodide 的场景

- 你的文档示例主要使用 Python 标准库或 Pyodide 预置包（numpy, pandas, matplotlib, scipy, scikit-learn 等已包含）
- 希望示例可以动态安装包（`piplite.install`）
- 希望构建过程简单，不需要额外的 conda 工具
- 文档读者可能需要尝试不同的包

### 选择 Xeus 的场景

- 你需要 Pyodide 不支持的包（如 ipycanvas、某些 C 扩展包）
- 希望用户打开 Notebook 时所有包已就绪，零等待
- 需要更接近真实 conda 环境的体验
- 构建阶段可以接受更长的构建时间和 micromamba 依赖

### 两个都要？

sphinx-demo 采用的方案是构建两个独立站点，通过版本切换器让用户选择。这适合大型项目或教程网站。对于简单项目，选择一个内核即可。

## 配置步骤对比

### Pyodide 配置步骤

1. `pip install jupyterlite-pyodide-kernel`
2. conf.py 中 `defaultKernelName` 设为 `"python"`
3. 无需额外配置文件
4. Notebook 中用 `piplite` 安装额外包

### Xeus 配置步骤

1. `pip install jupyterlite-xeus`
2. 创建 `environment.yml` 列出依赖包
3. conf.py 中 `defaultKernelName` 设为 `"XPython"`
4. CI 中需安装 micromamba

完整示例见 [/examples/02-pyodide-setup.md](../examples/02-pyodide-setup.md) 和 [/examples/03-xeus-setup.md](../examples/03-xeus-setup.md)。

## 相关内容

- [03-sphinx-conf](03-sphinx-conf.md)
- [09-ci-deployment](09-ci-deployment.md)
- [/examples/02-pyodide-setup.md](../examples/02-pyodide-setup.md)
- [/examples/03-xeus-setup.md](../examples/03-xeus-setup.md)
