---
type: Reference
title: JupyterLite Demo 依赖配置信源
description: requirements.txt 中所有依赖包的版本、分类、用途登记
tags: [requirements, dependencies, jupyterlite, pip, packages, kernels]
source_type: pip-requirements
source_path: requirements.txt
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: requirements
    resource: https://github.com/jupyterlite/demo/blob/main/requirements.txt
    title: requirements.txt
---

## 核心模块（必选）

| 包名 | 版本约束 | 用途 |
|------|----------|------|
| jupyterlite-core | ==0.8.0 | JupyterLite 核心框架 |
| jupyterlab | ~=4.6.0 | JupyterLab 前端 UI |
| notebook | ~=7.6.0 | Notebook 7 界面 |

## 内核（可选，Demo 全部预装）

| 包名 | 版本 | 语言 | 用途 |
|------|------|------|------|
| jupyterlite-pyodide-kernel | ==0.8.0 | Python (WASM) | CPython 编译为 WebAssembly，支持科学计算栈 |
| jupyterlite-javascript-kernel | ==0.3.0 | JavaScript | 浏览器原生 JS 执行内核 |
| jupyterlite-p5-kernel | ==0.3.0 | JavaScript (p5js) | p5.js 创意编程内核 |

## 语言包（可选）

| 包名 | 用途 |
|------|------|
| jupyterlab-language-pack-fr-FR | 法语界面语言包 |
| jupyterlab-language-pack-zh-CN | 中文界面语言包 |

## 文件渲染扩展（可选）

| 包名 | 版本约束 | 渲染格式 |
|------|----------|----------|
| jupyterlab-fasta | >=3.3.0,<4 | FASTA 生物序列格式 |
| jupyterlab-geojson | >=3.4.0,<4 | GeoJSON 地理数据格式 |

## 主题扩展（可选）

| 包名 | 用途 |
|------|------|
| jupyterlab-night | JupyterLab 暗色主题 |
| jupyterlab_miami_nights | Miami Nights 配色主题 |

## ipywidgets 生态（可选）

| 包名 | 版本约束 | 用途 |
|------|----------|------|
| ipywidgets | >=8.1.3,<9 | 交互式控件基础库 |
| ipyevents | >=2.0.1 | 鼠标/键盘事件支持 |
| ipympl | >=0.8.2 | Matplotlib 交互式后端（%matplotlib widget） |
| ipycanvas | >=0.9.1 | Canvas 绘图控件（RoughCanvas/MultiCanvas） |
| ipyleaflet | 无约束 | 交互式地图控件 |

## 绘图库（可选）

| 包名 | 版本约束 | 类型 |
|------|----------|------|
| plotly | >=6,<7 | 交互式可视化（plotly.js） |
| bqplot | 无约束 | Jupyter 原生交互式图表（基于 d3.js） |

## 禁用扩展

以下扩展在站点配置中被显式禁用：

| 扩展 ID | 原因 |
|---------|------|
| @jupyterlab/drawio-extension | drawio 图表编辑扩展（Demo 不需要） |
| jupyterlab-kernel-spy | 内核监控间谍扩展 |
| jupyterlab-tour | 引导式教程（有已知 bug，见 issue #82） |

## 注意事项

- Xeus Python 内核不在此 Demo 中提供，见 jupyterlite/xeus-python-demo 仓库
- 所有 Pyodide 示例笔记本中的第三方库（altair、pandas、numpy、folium 等）不预装，通过笔记本内 `%pip install` 动态安装
- 版本锁定使用 `==` 精确锁定核心组件，`~=` 兼容锁定 JupyterLab/Notebook，可选扩展使用 `>=` 范围
