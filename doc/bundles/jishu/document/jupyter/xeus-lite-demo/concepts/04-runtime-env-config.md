---
type: Concept
title: 运行时环境配置
description: environment.yml 文件的结构、channels 配置、依赖声明规则和常见内核配置示例
tags: [environment.yml, runtime, conda, emscripten-forge, dependencies, configuration]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: env-source
    resource: /references/environment-source.md
    title: 运行时环境配置信源
  - id: readme
    resource: /references/readme-source.md
    title: README 使用说明信源
---

## environment.yml 结构

`environment.yml` 定义浏览器内 WASM 运行时的 conda 包环境。它是一个标准的 conda 环境文件，但有特殊的 channels 配置。

```yaml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-python
  - ipycanvas
  # 添加更多包...
```

## 字段详解

### name

环境名称，默认为 `xeus-kernel`。这个值主要用于标识环境，不影响构建或运行。可以保留默认值或自定义。

### channels

channels 指定从哪里下载 conda 包。xeus-lite 的运行时环境**必须**配置两个通道：

| 通道 | URL | 作用 |
|------|-----|------|
| emscripten-forge-dev | `https://repo.prefix.dev/emscripten-forge-dev` | WASM 编译包，包含 xeus 内核和特化包 |
| conda-forge | `https://repo.prefix.dev/conda-forge` | 通用 conda-forge 包的 WASM 版本（通过 prefix.dev 镜像） |

**通道顺序很重要**：emscripten-forge-dev 必须排在前面，确保优先获取 WASM 特化版本。

> ⚠️ 不要使用标准的 `- conda-forge`（无 URL 前缀）。标准 conda-forge 提供的是 x86_64 Linux 包，不是 WASM 包。必须使用 prefix.dev 的 URL。

### dependencies

dependencies 列表声明需要预装到 JupyterLite 环境中的 conda 包。

## 内核选择

你需要至少安装一个内核。可选的 xeus 内核包括：

| 内核包名 | 语言 | 说明 |
|---------|------|------|
| `xeus-python` | Python | 默认 Python 内核（基于 CPython WASM） |
| `xeus-r` | R | R 语言内核 |
| `xeus-cpp` | C++ | C++ 交互式内核（基于 cling） |
| `xeus-lua` | Lua | Lua 语言内核 |
| `xeus-ruby` | Ruby | Ruby 语言内核 |

可以同时安装多个内核，用户在 Notebook 中可以切换。

## 常用包配置

### Python 科学计算

```yaml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-python
  - numpy
  - pandas
  - matplotlib
  - scipy
  - scikit-learn
  - ipycanvas
```

### R 统计分析

```yaml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-r
  - r-tidyverse
  - r-ggplot2
  - r-dplyr
```

> R 包在 conda 中以 `r-` 前缀命名。例如 `tidyverse` → `r-tidyverse`。

### C++ 交互式编程

```yaml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-cpp
```

### 多语言环境

```yaml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-python
  - xeus-r
  - numpy
  - matplotlib
```

## 可用包检查

并非所有 conda-forge 包都有 WASM 版本。要确认一个包是否可用，可以：

1. 访问 [prefix.dev](https://prefix.dev/channels/emscripten-forge-dev) 搜索包名
2. 查看包是否有 `emscripten-wasm32` 平台的构建
3. 或访问 [jupyterlite-xeus 文档](https://jupyterlite-xeus.readthedocs.io/en/latest/environment.html) 查看已知可用包列表

常见的已验证可用包包括：
- **数值计算**：numpy, scipy, pandas, sympy
- **可视化**：matplotlib, bokeh, plotly, ipycanvas, ipywidgets
- **机器学习**：scikit-learn
- **图像处理**：scikit-image, pillow
- **R 包**：r-tidyverse, r-ggplot2, r-dplyr（需检查具体版本）

## 配置后做什么

1. 编辑并提交 `environment.yml` 到 main 分支
2. 等待 GitHub Actions 完成构建（约3-5分钟）
3. 打开你的 JupyterLite 站点
4. 创建新 Notebook，选择对应的内核
5. 在 Notebook 中 `import` 你添加的包进行验证

## 注意事项

- 包越多，构建时间越长，站点加载越慢。只添加真正需要的包
- 版本不需要手动指定（如不写 `numpy=1.24`），构建系统会自动解析兼容版本
- 如果某个包安装后 Notebook 无法启动，检查该包是否有 WASM 版本
- 首次加载站点时，WASM 模块需要下载到浏览器，可能需要几秒到几十秒（取决于包数量和网速）

## 相关概念

- [双环境模型](02-dual-environment.md) — 理解两个环境文件的区别
- [构建环境配置](05-build-env-config.md) — 构建工具链配置
- [多语言内核支持](07-kernel-options.md) — 各内核详细说明
- [Python 科学计算环境](../examples/02-numpy-matplotlib.md) — NumPy/Matplotlib 配置示例
- [R 内核配置](../examples/03-r-kernel.md) — R 语言配置示例
