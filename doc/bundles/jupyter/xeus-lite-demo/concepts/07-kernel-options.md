---
type: Concept
title: 多语言内核支持
description: xeus-python、xeus-r、xeus-cpp 等内核的配置方法、适用场景和注意事项
tags: [kernel, xeus-python, xeus-r, xeus-cpp, multi-language, wasm]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README 使用说明信源
  - id: env-source
    resource: /references/environment-source.md
    title: 运行时环境配置信源
---

## 支持的内核

xeus-lite 通过 emscripten-forge 支持多种编程语言内核。每个内核都是独立的 conda 包，在 `environment.yml` 中声明即可使用。

## xeus-python（Python 内核）

**包名**：`xeus-python`

这是默认的 Python 内核，基于 CPython 编译为 WASM。

### 配置

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
```

### 适用场景
- 数据分析、科学计算
- 教学（Python 入门、数据科学课程）
- 快速原型验证
- 可视化（matplotlib、bokeh、plotly）

### 常用配套包
- **数值计算**：numpy, scipy, pandas, sympy
- **机器学习**：scikit-learn
- **可视化**：matplotlib, seaborn, bokeh, plotly, ipycanvas, ipywidgets
- **图像处理**：scikit-image, pillow
- **网络请求**：在 WASM 环境中网络请求受限（跨域、同步限制）

### 注意事项
- xeus-python 是 CPython 的 WASM 编译版本，不是 Pyodide，两者有差异
- 某些需要 C 扩展或系统调用的包可能不可用
- 文件系统是内存文件系统（基于 IndexedDB），刷新页面后数据可能丢失
- 默认演示 Notebook 使用 ipycanvas 绘制笑脸，验证内核和图形功能正常

## xeus-r（R 内核）

**包名**：`xeus-r`

R 语言内核，基于 R 解释器编译为 WASM。

### 配置

```yaml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-r
  - r-tidyverse
```

### 适用场景
- 统计分析
- 数据可视化（ggplot2）
- 统计学教学
- R 语言课程

### R 包命名规则

conda 中的 R 包以 `r-` 为前缀，包名中的点号和下划线通常转为连字符：

| CRAN 包名 | conda 包名 |
|----------|-----------|
| tidyverse | r-tidyverse |
| ggplot2 | r-ggplot2 |
| dplyr | r-dplyr |
| tidyr | r-tidyr |
| coursekata | r-coursekata（README示例） |

### 注意事项
- R 包的 WASM 可用性不如 Python 包广泛
- 包含复杂 C/Fortran 依赖的包可能未被编译
- 建议先从 `r-tidyverse` 开始，它包含了最常用的数据科学包

## xeus-cpp（C++ 内核）

**包名**：`xeus-cpp`

C++ 交互式内核，基于 cling C++ 解释器编译为 WASM。

### 配置

```yaml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-cpp
```

### 适用场景
- C++ 教学
- 算法演示
- C++ 代码快速验证
- 数值计算（Eigen 等库如果可用）

### 使用特点
- 支持交互式 C++（无需 main 函数）
- 变量和函数在 cell 间持久化
- 支持标准 C++17/20 特性
- 编译错误即时反馈

### 注意事项
- C++ 内核的 WASM 包体积较大
- 标准库支持取决于 WASM 编译配置
- 第三方 C++ 库的可用性有限
- 编译执行比 Python/R 慢（即时编译）

## xeus-lua（Lua 内核）

**包名**：`xeus-lua`

Lua 语言内核，适合嵌入式脚本和轻量编程场景。

```yaml
dependencies:
  - xeus-lua
```

## 多内核共存

可以同时安装多个内核，用户在创建 Notebook 时选择：

```yaml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-python
  - xeus-r
  - numpy
  - pandas
  - matplotlib
  - r-tidyverse
```

在 JupyterLite 中，用户可以通过 Kernel → Change Kernel 菜单切换语言。

## 内核选择指南

| 需求 | 推荐内核 | 理由 |
|------|---------|------|
| 通用数据科学 | xeus-python | 包生态最丰富，社区支持最好 |
| 统计教学/研究 | xeus-r | R 语言统计功能强大，tidyverse 生态完善 |
| C++ 教学/算法 | xeus-cpp | 交互式 C++，即时反馈 |
| 轻量脚本 | xeus-lua | Lua 轻量快速 |
| 教学环境 | 多内核并存 | 让学生根据课程选择语言 |

## 内核切换界面

部署完成后，在 JupyterLite 中切换内核：
1. 打开或创建 Notebook
2. 点击菜单栏的 **Kernel** → **Change Kernel**
3. 选择可用的内核（如 XPython、XR、XCpp）
4. 等待内核启动（首次加载可能需要几秒）

## 验证内核是否工作

部署后，创建一个新 Notebook，选择对应内核，运行简单代码验证：

**Python**:
```python
import sys
print(sys.version)
import numpy as np
print(np.__version__)
```

**R**:
```r
R.version.string
x <- c(1, 2, 3, 4, 5)
mean(x)
```

**C++**:
```cpp
#include <iostream>
std::cout << "Hello, xeus-cpp!" << std::endl;
```

## 相关概念

- [运行时环境配置](04-runtime-env-config.md) — environment.yml 配置详解
- [Python 科学计算环境](/examples/02-numpy-matplotlib.md) — NumPy/Matplotlib 配置示例
- [R 内核配置](/examples/03-r-kernel.md) — R 语言配置示例
- [C++ 内核配置](/examples/04-cpp-kernel.md) — C++ 内核配置示例
