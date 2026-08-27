---
type: Concept
title: "演示能力维度与多内核支持"
description: "系统了解 jupyterlab-demo 覆盖的 JupyterLab 核心能力维度：多文件格式查看器、多语言内核、交互控件与可视化，理解每个演示文件对应哪个能力"
tags: [capabilities, file-viewers, kernels, widgets, visualization, multilingual]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:25:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: narrative, resource: "/references/narrative-source.md", title: "Narrative演示脚本信源" }
  - { id: binder, resource: "/references/binder-config-source.md", title: "Binder配置信源" }
---

# 演示能力维度与多内核支持

jupyterlab-demo 的素材选择不是随意的——每个数据文件、每个 Notebook 都经过精心挑选，用于展示 JupyterLab 的某个特定能力。本章节系统梳理 demo 覆盖的能力维度，帮助你理解"为什么选这些文件"。

## 能力维度总览

jupyterlab-demo 覆盖了 JupyterLab 的六大核心能力维度：

```
┌─────────────────────────────────────────────────────┐
│              JupyterLab 核心能力维度                  │
├─────────────┬─────────────┬─────────────────────────┤
│  基础交互    │  文件查看器  │  多语言内核              │
│  Launcher   │  CSV/表格   │  Python (ipykernel)     │
│  拖拽布局    │  图片查看    │  Python (xeus-python)   │
│  命令面板    │  GeoJSON    │  R (irkernel)           │
│  查找替换    │  Vega-Lite  │  C++ (xeus-cling)       │
│  单文档模式  │  FASTA      │  Julia (可选)           │
├─────────────┼─────────────┼─────────────────────────┤
│  交互可视化  │  协作与扩展  │  文档与输出              │
│  ipywidgets │  实时协作    │  Markdown+Python混编    │
│  bqplot     │  插件架构    │  nbconvert转换          │
│  altair     │  JupyterHub │  打印输出               │
│  matplotlib │  扩展管理器  │  离线Notebook           │
└─────────────┴─────────────┴─────────────────────────┘
```

## 维度一：基础交互能力

这是 JupyterLab 作为 IDE 的基础功能，demo 通过操作演示而非特定文件展示：

| 能力 | 演示方式 | 演示脚本位置 |
|------|---------|-------------|
| Launcher 启动器 | 点击 + 按钮创建 Notebook/Console/Editor/Terminal | jupyterlab.md §1 |
| Notebook 单元格操作 | 折叠输入/输出、拖放单元格重排序 | jupyterlab.md §1 |
| 文件浏览器 | 文件操作、右键菜单、拖放文件 | jupyterlab.md §1 |
| 运行面板 | 查看和管理运行中的 Kernel/终端 | jupyterlab.md §1 |
| 命令面板 | 模糊搜索命令（演示搜索"new"） | jupyterlab.md §1 |
| Dock Panel 布局 | 将活动面板拖拽排列为任意布局 | jupyterlab.md §1 |
| 标签页与单文档模式 | 标签切换、Shift+Cmd+Enter 专注模式 | QConAI.md |
| 查找替换 | Notebook 和文本文件中的查找替换 | jupyterlab.md §5 |
| 状态栏 | 底部状态栏信息、扩展可添加状态 | jupyterlab.md §6 |
| 终端 | 完整终端支持（可运行 vi/emacs） | QConAI.md |

### 拖放功能演示

build.py 特意创建了两个空文件用于演示拖放：
- `move_this_file.txt`：一个空文本文件（被拖拽对象）
- `move_it_here/`：一个空目录（拖拽目标位置）

演示者可以在文件浏览器中直观展示 JupyterLab 的拖放能力。

## 维度二：文件查看器（File Handlers）

JupyterLab 的文件处理器是其扩展性的核心体现——每种文件格式都有专门的查看器，demo 覆盖了6种格式：

### CSV/表格查看器（DataGrid）

| 文件 | 大小 | 用途 |
|------|------|------|
| `data/iris.csv` | 小（~4KB） | 基础表格展示、排序 |
| `TCGA_Data/c2.cp.v3.0.symbols_edit.csv` → `smaller.csv` | 中 | 中等数据滚动浏览 |
| `big.csv`（Urban Data Challenge） | **200MB / 120万行** | 大数据高性能滚动 |

DataGrid 是基于 Lumino 的高性能 Canvas 表格组件，演示重点是：
- 200MB CSV 文件浏览器加载缓慢/无法打开，但 JupyterLab DataGrid 可以流畅滚动
- 支持排序、多列布局
- 万亿行/列的理论性能（Chris Colbert 的实现）

### 图片查看器

| 文件 | 来源 |
|------|------|
| `hubble.jpg` | NASA/ESA 哈勃望远镜拍摄的交互星系 AM 0500-620 |

支持缩放、全屏查看。

### GeoJSON 地图查看器

| 文件 | 来源 |
|------|------|
| `data/Museums_in_DC.geojson` | 华盛顿 DC 开放数据（OpenData DC），CC-BY 4.0 |

使用 jupyterlab-geojson 扩展渲染交互式地图，展示华盛顿 DC 的博物馆分布。

### Vega-Lite 可视化查看器

| 文件 | 来源 |
|------|------|
| `vega.vl.json` | Altair 示例（`bar.vl.json` 重命名） |

Vega-Lite 是声明式可视化语法，JupyterLab 可以直接渲染 .vl.json 文件为交互式图表。多视图同步演示：用 JSON 编辑器修改 Vega 配置，图表查看器实时更新。

### FASTA 生物序列查看器

| 文件 | 来源 |
|------|------|
| 无直接文件，通过 Fasta.ipynb 展示 | jupyterlab-fasta 扩展 |

FASTA 格式用于存储生物序列（DNA/RNA/蛋白质）。jupyterlab-fasta 扩展提供序列可视化和多序列比对查看。演示重点：这是一个第三方扩展，仅用几十行代码就为 JupyterLab 添加了全新文件类型支持。

### 其他格式

| 格式 | 查看器 | 备注 |
|------|--------|------|
| PDF | 内置 PDF 查看器 | jupyterlab-slides.pdf |
| JSON | JSON 编辑器（带语法高亮） | japan_meteorological_agency_*.json |
| Markdown | 实时渲染预览 | markdown_python.md, jupyterlab.md |
| 视频/音频 | HTML5 播放器 | jupiter.mp4 (CC0), rocket.wav (CC0) |
| Vega/Vega-Lite | 交互式图表 | bar.vl.json |

## 维度三：多语言内核

Jupyter 的核心优势之一是语言无关的架构——同一界面可以运行多种编程语言的内核（Kernel）。

### Python 内核

| 内核包 | 实现语言 | 特点 |
|--------|---------|------|
| `ipykernel` | Python (wrapper) | 官方 Python 内核，最成熟稳定 |
| `xeus-python` | C++ | 替代实现，基于 Xeus 框架，支持调试协议 |

demo 默认使用 ipykernel，environment.yml 同时安装 xeus-python 展示多内核选择。

### R 内核

| 包 | 用途 |
|----|------|
| `r-irkernel` | R 语言内核 |
| `r-ggplot2` | R 绘图库 |

`notebooks/R.ipynb` 展示在 JupyterLab 中运行 R 代码和 ggplot2 可视化。CI 中会执行此 Notebook 验证 R 内核可用。

### C++ 内核（已注释）

```yaml
# - xeus-cling
# - xtensor
# - xtensor-blas
# - xwidgets
# - xleaflet
```

C++ 内核（xeus-cling，基于 Cling C++ 解释器）在 environment.yml 中被注释掉，原因可能是构建时间过长或不稳定。`notebooks/Cpp.ipynb` 保留用于手动环境。

### Julia 内核（构建后删除）

`notebooks/Julia.ipynb` 存在于源目录中，但 postBuild 脚本主动删除它：

```bash
rm demo/notebooks/Julia.ipynb
```

因为 environment.yml 中没有安装 Julia 内核，保留会导致用户打开时找不到内核报错。这是一个**防御性设计**：宁可删除不支持的内容，也不让用户遇到错误。

## 维度四：交互可视化与控件

| 库 | 文件 | 演示内容 |
|----|------|---------|
| `ipywidgets` | 基础交互控件 | 滑块、按钮、下拉菜单等基础控件 |
| `bqplot` | notebooks/bqplot.ipynb | 基于 D3.js 的交互式2D可视化 |
| `altair` | Vega-Lite生态 | 声明式统计可视化 |
| `matplotlib` | notebooks/Lorenz.ipynb | 3D 洛伦兹吸引子绘图 |
| `ipyleaflet` | （环境安装） | 交互式地图控件 |

bqplot 示例特别值得注意：演示脚本（QConAI.md）提到可以右键将 Widget 输出"拉出"为独立视图，形成 dashboard 原型。

## 维度五：实时协作与扩展

| 能力 | 配置/扩展 | 说明 |
|------|----------|------|
| 实时协作 | `c.LabApp.collaborative = True` | jupyter-collaboration 包提供 RTC（实时协作） |
| JupyterHub | 内置核心扩展 | 多用户认证与管理 |
| 离线Notebook | jupyter-offlinenotebook | 无网络时使用Notebook |
| 扩展管理器 | 左侧面板内置 | 搜索、安装、管理扩展 |

### 插件架构的核心理念

演示脚本反复强调一个信息：**Everything is a plugin**（一切皆插件）。

JupyterLab 中你看到的一切——文件浏览器、Notebook、Console、Terminal、编辑器、状态栏——都是以扩展（npm 包）形式实现的。第三方开发者编写的扩展与 JupyterLab 内置功能享有完全平等的地位。

这意味着：
- 你可以替换内置的任何组件
- 你可以添加新的文件查看器、新的命令、新的面板
- 扩展开发只需 npm 包 + 元数据，无需核心团队审批

FASTA 查看器就是一个案例：有人在 SciPy 会议上说需要FASTA支持，开发者用几十行代码几小时就做出了原型扩展。

## 维度六：文档混编与输出

| 能力 | 演示文件 | 说明 |
|------|---------|------|
| Markdown+Python | markdown_python.md | 在 Markdown 文件中绑定 Kernel，选中代码块 Shift+Enter 执行 |
| Notebook 输出新视图 | bqplot 输出 | 右键输出 → "Create New View for Output" → 独立面板 |
| nbconvert 转换 | CI 中使用 | Notebook → HTML/PDF/Markdown/脚本 |
| 打印 | 状态栏 | 扩展可自定义打印布局 |

Markdown+Python 混编是 JupyterLab 独有的工作流：你可以在一个 Markdown 文档中写教程/说明文字，嵌入可执行的 Python 代码块，绑定一个 Console 来逐步执行代码——这比 Notebook 更适合"文档驱动"的编程和教学场景。

## 演示流程设计逻辑

演示脚本（jupyterlab.md）的章节顺序遵循一个学习路径：

1. **从 Launcher 开始**（认识入口）→ 2. **Notebook基础**（熟悉界面）→ 3. **左侧面板**（管理文件）→ 4. **Markdown+Console**（跨工具协作）→ 5. **布局排列**（自由组织）→ 6. **文件查看器**（多种格式）→ 7. **实用功能**（查找/状态栏/打印）→ 8. **多用户**（JupyterHub）→ 9. **扩展架构**（开放平台）

这个顺序从简单到复杂，从使用到开发，让观众逐步理解 JupyterLab 不仅是一个 Notebook 界面，而是一个完整的、可扩展的、面向交互式计算的 IDE 平台。

## 相关概念

- [项目定位与设计理念](00-introduction.md)
- [Notebook 示例解析](05-notebook-examples.md)
- [数据文件与多格式查看器](06-data-files.md)
- [插件架构与扩展生态](08-extension-demo.md)
