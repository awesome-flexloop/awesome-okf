---
type: Index
title: 实践示例索引
description: JupyterLite Demo 实践示例目录，包含7篇可动手操作的使用场景教程
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
---

# JupyterLite Demo 实践示例

本目录包含 JupyterLite 的实战示例文档，每个示例对应一个可动手操作的使用场景。

## 示例列表

### 入门示例

| 示例 | 说明 |
|------|------|
| [01-从零部署到 GitHub Pages](01-first-deployment.md) | 从空仓库开始，10分钟完成第一个站点部署 |
| [02-Python 内核基础使用](02-python-basics.md) | 变量、display、magics、网络请求等基础操作 |

### 数据与可视化

| 示例 | 说明 |
|------|------|
| [03-数据可视化实战](03-data-visualization.md) | Matplotlib/Altair/Plotly 三大库绘图 |
| [04-交互式控件与图表](04-interactive-widgets.md) | ipywidgets 控件 + bqplot 响应式图表 |
| [05-交互式地图可视化](05-interactive-maps.md) | folium 简单地图 + ipyleaflet 联动地图 |

### 创意与进阶

| 示例 | 说明 |
|------|------|
| [06-创意编程与物理模拟](06-creative-coding.md) | p5.js 创意草图 + ipycanvas 动画 + pyb2d 物理引擎 |
| [07-构建自定义 Demo 站点](07-custom-demo-site.md) | 定制主题/扩展/语言包的完整流程 |

## 前置条件

- 大部分示例使用 **Python (Pyodide)** 内核
- 创意编程示例使用 **p5.js** 内核
- 示例中的 `%pip install` 命令在浏览器中执行，无需本地安装
