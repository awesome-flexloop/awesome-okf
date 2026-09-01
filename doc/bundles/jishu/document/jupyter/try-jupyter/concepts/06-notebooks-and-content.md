---
type: Concept
title: "Notebook内容与示例数据"
description: "详解content/目录结构、7个演示notebook的内容覆盖（Intro/Lorenz/C++/R/SQLite）、8个示例数据文件（GeoJSON/音频/图表/FASTA/CSV/图片）及其对应的JupyterLab扩展查看器。"
tags: [notebooks, content, data-files, examples, geojson, fasta, ipywidgets, bqplot]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: content-dir
    resource: "../../../../../external/libs/jupyter/try-jupyter/content"
    title: "try-jupyter/content/ 目录"
  - id: pyproject
    resource: "/references/pyproject-source.md"
    title: "pyproject.toml信源"
  - id: readme
    resource: "../../../../../external/libs/jupyter/try-jupyter/README.md"
    title: "README.md"
---

# Notebook内容与示例数据

`content/` 目录是用户在JupyterLite中可访问的所有内容（notebook和数据文件），由 `jupyter_lite_config.json` 的 `LiteBuildConfig.contents` 配置指定打包到站点中。

## 目录结构

```
content/
├── notebooks/           # Jupyter notebook演示文件
│   ├── Intro.ipynb              # 入门介绍
│   ├── Lorenz.ipynb             # 洛伦兹吸引子（科学计算演示）
│   ├── cpp.ipynb                # C++基础
│   ├── cpp-third-party-libs.ipynb  # C++第三方库
│   ├── cpp-tiny-ray-tracer.ipynb   # C++光线追踪器
│   ├── r.ipynb                  # R语言演示
│   └── sqlite.ipynb             # SQLite演示
└── data/                # 示例数据文件
    ├── Museums_in_DC.geojson    # 华盛顿特区博物馆GeoJSON数据
    ├── audio.wav                # 音频示例
    ├── bar.vl.json              # Vega-Lite条形图规范
    ├── fasta-example.fasta      # FASTA序列文件
    ├── iris.csv                 # Iris数据集
    ├── marie.png                # 示例图片（居里夫人）
    └── matplotlib.png           # Matplotlib示例图
```

## Notebook详解

7个notebook覆盖了JupyterLite支持的所有内核和主要使用场景。

### 1. Intro.ipynb — 入门介绍

- **内核**：Python（Pyodide/Xeus-Python）
- **用途**：新用户的第一个notebook，介绍JupyterLite的基本概念和功能
- **内容**：
  - JupyterLab界面导览
  - 基本的Python代码执行
  - Markdown和富文本展示
  - 交互式Widget演示
- **已知警告**：`"Matplotlib is building the font cache; this may take a moment."`（Matplotlib首次加载字体会有缓存构建提示）
- **入口**：README推荐从此notebook开始体验

### 2. Lorenz.ipynb — 洛伦兹吸引子

- **内核**：Python
- **用途**：科学计算和可视化演示
- **内容**：
  - 洛伦兹吸引子（混沌理论经典模型）的数值计算
  - 使用Matplotlib/SciPy进行3D可视化
  - 展示NumPy+SciPy+Matplotlib在浏览器端的完整科学计算能力
- **已知警告**：Matplotlib字体缓存提示（与Intro相同）

### 3. cpp.ipynb — C++基础

- **内核**：C++23（xeus-cpp）
- **用途**：C++内核入门演示
- **内容**：
  - C++基本语法在Jupyter中的使用
  - 变量、函数、类等基础概念
  - 即时编译执行（xeus-cpp基于Clang实现C++ JIT）
- **已知警告**：`"some error"`（占位符，可能对应C++内核的某个已知非致命输出）

### 4. cpp-third-party-libs.ipynb — C++第三方库

- **内核**：C++23（xeus-cpp）
- **用途**：演示C++内核中使用第三方数值计算库
- **内容**：
  - xtensor（C++张量运算库，类似NumPy）
  - xsimd（SIMD向量化）
  - symengine（符号计算）
  - xtensor-blas（BLAS线性代数绑定）
- **已知警告**：无

### 5. cpp-tiny-ray-tracer.ipynb — C++光线追踪器

- **内核**：C++23（xeus-cpp）
- **用途**：高性能C++计算演示
- **内容**：
  - 一个小型光线追踪渲染器的完整实现
  - 展示浏览器中C++的计算性能
  - 生成渲染图像并在notebook中显示
- **已知警告**：无

### 6. r.ipynb — R语言演示

- **内核**：R（xeus-r）
- **用途**：R语言内核演示
- **内容**：
  - R基本语法和数据结构
  - ggplot2数据可视化
  - 统计分析示例
- **已知警告**：`"Attaching package:"`（R加载包时的标准消息）

### 7. sqlite.ipynb — SQLite演示

- **内核**：SQLite（xeus-sqlite）
- **用途**：SQLite内核演示
- **内容**：
  - 直接在notebook中执行SQL查询
  - 数据库创建、表操作、数据查询
  - 展示浏览器端SQL数据库能力
- **已知警告**：`"Error: no such table: players"`（预期错误，用于演示查询不存在表时的错误处理）

## 示例数据文件详解

### 地理数据：Museums_in_DC.geojson

- **格式**：GeoJSON（地理JSON数据格式）
- **内容**：华盛顿特区博物馆的地理位置数据
- **查看器**：`jupyterlab-geojson` 扩展提供可视化地理数据查看
- **用途**：配合ipyleaflet在地图上标注博物馆位置

### 音频：audio.wav

- **格式**：WAV音频
- **用途**：在notebook中演示音频播放功能
- **对应kernel**：Python内核，使用IPython的Audio组件

### 图表规范：bar.vl.json

- **格式**：Vega-Lite JSON规范
- **内容**：条形图的Vega-Lite声明式定义
- **用途**：演示声明式可视化
- **相关库**：可与bqplot/plotly等库配合使用

### 序列数据：fasta-example.fasta

- **格式**：FASTA（生物信息学序列格式）
- **内容**：DNA/蛋白质序列示例
- **查看器**：`jupyterlab-fasta` 扩展提供FASTA文件格式化显示
- **用途**：展示JupyterLab在生物信息学领域的应用

### 数据集：iris.csv

- **格式**：CSV（逗号分隔值）
- **内容**：经典Iris（鸢尾花）数据集
- **用途**：Python/R中进行数据分析和机器学习入门的标准数据集
- **相关库**：pandas读取、matplotlib/seaborn可视化

### 图片：marie.png

- **格式**：PNG图片
- **内容**：玛丽·居里（Marie Curie）的照片
- **用途**：notebook中图片显示演示

### 图片：matplotlib.png

- **格式**：PNG图片
- **内容**：Matplotlib生成的示例图
- **用途**：可视化输出示例

## 文件查看器扩展对应关系

| 文件类型 | 扩展包 | 功能 |
|---------|--------|------|
| `.geojson` | jupyterlab-geojson | 地理数据交互式地图查看 |
| `.fasta` | jupyterlab-fasta | 生物序列格式化显示 |
| `.csv` | JupyterLab内置 | 表格视图 |
| `.png/.jpg` | JupyterLab内置 | 图片显示 |
| `.wav` | JupyterLab内置 | 音频播放 |
| `.json` (Vega-Lite) | JupyterLab内置/第三方 | 图表渲染 |

## Notebook编辑注意事项

README中特别说明了notebook编辑方式：

> The notebooks in this repository are written with JupyterLite kernels, so if you edit them locally, you will likely over-write the kernel information with your local kernels. As such, the easiest way to make edits is via the Try Jupyter Page.

### 推荐编辑方式

1. 访问 https://jupyter.org/try-jupyter
2. 在线打开并修改notebook
3. 通过 File → Download 下载修改后的.ipynb文件
4. 替换仓库中的对应文件

### 本地编辑风险

如果使用本地Jupyter编辑notebook：
- 本地Jupyter的内核信息（kernel spec）会写入.ipynb文件的metadata
- 这会覆盖JupyterLite内核信息，导致在线站点中notebook可能无法正确关联内核
- 提交前需要检查并清理kernel metadata

## 添加新Notebook

要添加新的演示notebook：

1. **在线创建**（推荐）：在Try Jupyter站点中创建新notebook，使用目标内核
2. **下载放置**：下载后放入 `content/notebooks/` 目录
3. **测试执行**：构建站点后，确保notebook能在对应内核中正常执行
4. **注册已知警告**（如有必要）：在 `ui-tests/utils.py` 的 `KNOWN_WARNINGS_BY_NOTEBOOK` 中添加可忽略的警告
5. **构建测试**：运行 `pixi run test` 验证notebook执行无错误

## URL参数打开Notebook

项目依赖 `jupyterlab-open-url-parameter≥0.3.0` 扩展，支持通过URL参数直接打开notebook：

```
https://jupyter.org/try-jupyter/lab/index.html?path=notebooks/Intro.ipynb
```

URL格式：`/lab/index.html?path=notebooks/{NotebookName}.ipynb`

测试文件中使用的URL构造方式：
```python
from urllib.parse import quote
relative_path = notebook_path.relative_to(notebook_path.parent.parent)
notebook_url = f"{base_url}/lab/index.html?path={quote(str(relative_path))}"
```

这也是CI测试能够自动遍历所有notebook的基础。

## 相关概念

- [架构总览](02-architecture-overview.md)
- [内核生态](04-kernel-ecosystem.md)
- [构建管线](05-build-pipeline.md)
- [UI测试框架](07-ui-testing.md)
