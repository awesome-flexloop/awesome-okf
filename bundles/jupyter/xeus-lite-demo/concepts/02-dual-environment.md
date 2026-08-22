---
type: Concept
title: 双环境模型
description: xeus-lite 中构建环境（build-environment.yml）与运行时环境（environment.yml）的区别、各自职责和配置规则
tags: [dual-environment, build-environment, runtime-environment, conda, wasm, architecture]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: env-source
    resource: /references/environment-source.md
    title: 运行时环境配置信源
  - id: build-env
    resource: /references/build-env-source.md
    title: 构建环境配置信源
---

## 为什么需要两个环境文件

xeus-lite-demo 包含两个 conda 环境配置文件，这是初学者最容易混淆的地方。理解它们的区别是掌握 xeus-lite 配置的关键。

**核心原因**：构建 JupyterLite 站点的机器（Linux CI）和运行 JupyterLite 的环境（用户浏览器）是完全不同的计算平台——一个是 x86_64 Linux，另一个是 WebAssembly 浏览器虚拟机。它们需要不同架构的包。

## 两个环境文件对比

| 属性 | `environment.yml` | `.github/build-environment.yml` |
|------|-------------------|--------------------------------|
| **作用** | 定义浏览器内运行时的包 | 定义 CI 构建机上的工具 |
| **运行位置** | 用户浏览器（WASM） | GitHub Actions（Linux x86_64） |
| **conda 通道** | prefix.dev 的 emscripten-forge-dev + conda-forge | 标准 conda-forge |
| **包架构** | WebAssembly (emscripten-wasm32) | Linux x86_64 |
| **包含内容** | 语言内核、用户库（numpy等） | jupyterlite CLI、构建插件 |
| **何时生效** | 用户打开 Notebook 时 | `jupyter lite build` 时 |
| **修改后效果** | 改变 Notebook 中可用的包 | 改变构建过程（加插件等） |
| **示例包** | xeus-python, numpy, matplotlib, ipycanvas | jupyterlite-core, jupyterlite-xeus, notebook |

## 构建环境详解

构建环境（`.github/build-environment.yml`）安装在 GitHub Actions 的 Ubuntu 虚拟机上，用于执行 `jupyter lite build` 命令。

```yaml
name: build-env
channels:
  - conda-forge
dependencies:
  - python
  - pip
  - jupyter_server
  - jupyterlite-core >=0.7      # JupyterLite CLI 构建工具
  - jupyterlite-xeus >=4.3      # xeus 内核集成插件
  - notebook >=7.5              # Notebook 7 前端
```

**何时修改构建环境**：
- 需要添加 JupyterLite 插件（如 jupyterlite-terminal、jupyterlite-p5-kernel 等）
- 需要升级 jupyterlite-core 或 jupyterlite-xeus 版本
- 需要添加构建时需要的 Python 工具

**何时不需要修改构建环境**：
- 用户需要新的 Python/R 包（如 pandas、scikit-learn）→ 修改 environment.yml
- 需要添加新的 Notebook → 放入 content/ 目录

## 运行时环境详解

运行时环境（`environment.yml`）定义用户浏览器中可用的包。这些包由 emscripten-forge 编译为 WASM，在构建时被下载并打包到静态站点中。

```yaml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev   # WASM 包通道
  - https://repo.prefix.dev/conda-forge            # WASM 通用包
dependencies:
  - xeus-python    # Python 内核
  - ipycanvas      # Canvas 绘图组件
```

**何时修改运行时环境**：
- 需要添加新的内核（xeus-r、xeus-cpp 等）
- 需要安装 Python 包（numpy、pandas、matplotlib、scipy 等）
- 需要安装 R 包（r-tidyverse、r-ggplot2 等，需加 `r-` 前缀）

**通道选择规则**：
- `emscripten-forge-dev` 通道包含 xeus 内核和 WASM 特化包
- `conda-forge` 通道（prefix.dev 镜像）包含通用 WASM 包
- 两个通道必须同时配置，顺序是 emscripten-forge-dev 在前

## 配置决策树

当你想"添加一个东西"时，用这个决策树判断应该修改哪个文件：

```
我要添加的是什么？
├─ Python/R/C++ 包（在 Notebook 中 import 的）
│  └─ ✅ 修改 environment.yml（运行时环境）
│     例：numpy, pandas, matplotlib, xeus-r, r-ggplot2
│
├─ JupyterLite 插件（扩展 UI 功能的）
│  └─ ✅ 修改 .github/build-environment.yml（构建环境）
│     例：jupyterlite-terminal, jupyterlite-p5-kernel
│
├─ Notebook 文件（.ipynb）
│  └─ ✅ 放入 content/ 目录
│
├─ 数据文件（CSV、图片等）
│  └─ ✅ 放入 content/ 目录
│
└─ 不确定？
   └─ 如果它是 "用户在 Notebook 里用的" → environment.yml
      如果它是 "构建/界面功能" → build-environment.yml
```

## 常见配置错误

### 错误1：把插件写进 environment.yml

```yaml
# ❌ 错误
dependencies:
  - jupyterlite-terminal  # 这是构建插件，不是运行时包！
```

**后果**：构建可能失败，或者插件不生效（因为它是 x86_64 包，不是 WASM 包）。

**正确做法**：写入 `.github/build-environment.yml`。

### 错误2：把用户包写进 build-environment.yml

```yaml
# ❌ 错误
dependencies:
  - numpy  # 这是用户运行时包，不应该在构建环境中
```

**后果**：numpy 安装在 CI 机器上，但不会被打包到静态站点中，Notebook 中 `import numpy` 会报错。

**正确做法**：写入 `environment.yml`。

### 错误3：遗漏或错误配置 channels

```yaml
# ❌ 错误：缺少 emscripten-forge-dev 通道
channels:
  - conda-forge
dependencies:
  - xeus-python  # 找不到 WASM 版本！
```

**后果**：构建时无法找到 xeus-python 的 WASM 版本，可能下载到错误架构的包。

**正确做法**：必须同时包含两个 prefix.dev 通道，且 emscripten-forge-dev 在前。

## 相关概念

- [运行时环境配置](04-runtime-env-config.md) — environment.yml 详细配置方法
- [构建环境配置](05-build-env-config.md) — build-environment.yml 详细配置方法
- [多语言内核支持](07-kernel-options.md) — 配置 Python/R/C++ 内核
- [添加 JupyterLite 插件](/examples/05-add-jupyterlite-plugins.md) — 插件安装示例
