---
okf_version: "0.2"
type: bundle
title: Plotly.py 知识包
description: Plotly.py 开源交互式可视化库的源码学习文档，涵盖图对象模型、Figure 数据结构、Plotly Express 高级 API、渲染与 IO 系统
tags:
  - plotly
  - python
  - 可视化
  - 数据科学
  - 交互式图表
generated:
  by: reference_agent/trae-glm
  at: 2026-08-22T15:00:00Z
verified:
  by: "process:seven-concepts-v"
  at: 2026-08-22T15:30:00Z
status: stable
stale_after: 2027-12-31
sources:
  - plotly/basedatatypes.py
  - plotly/graph_objs/
  - plotly/express/
  - plotly/io/
  - plotly/_subplots.py
  - plotly/figure_factory/
  - plotly/colors/
  - plotly/tools.py
---

# Plotly.py 知识包

Plotly.py 是 Python 生态中最流行的交互式可视化库之一，基于 plotly.js 渲染引擎，提供声明式 API 支持 40+ 种图表类型。本知识包从源码层面解析 plotly.py 的核心架构和使用方法。

## 包信息

| 字段 | 值 |
|------|-----|
| 包名 | plotly |
| 版本获取方式 | `importlib.metadata.version("plotly")` |
| 许可证 | MIT |
| 源码路径 | `d:\spaces\SpecWeave\external\libs\python\plotly.py\plotly\` |
| 渲染引擎 | plotly.js（前端 JavaScript 库） |
| 核心依赖 | numpy, narwhals, packaging |

## 文档结构

```
plotly/
├── index.md                        ← 本文件（知识包入口）
├── concepts/                       ← 概念文档
│   ├── index.md                    ← 概念索引
│   ├── 00-introduction.md          ← Plotly.py 简介
│   ├── 01-figure-model.md          ← Figure 数据模型
│   ├── 02-plotly-express.md        ← Plotly Express 高级 API
│   └── 03-rendering-io.md          ← 渲染与 IO
├── references/                     ← 深度参考
│   ├── index.md                    ← 信源登记簿
│   └── graph-obj-model.md          ← 图对象模型源码解析
└── examples/                       ← 代码示例
    ├── index.md                    ← 示例索引
    └── interactive-charts.md       ← 基础交互式图表示例
```

## 快速导航

### 入门阅读

1. [Plotly.py 简介](concepts/00-introduction.md) — 了解 plotly.py 是什么、核心特性和生态
2. [Figure 数据模型](concepts/01-figure-model.md) — 理解 Figure/data/layout 三层结构
3. [Plotly Express](concepts/02-plotly-express.md) — 学习高效绘图 API
4. [渲染与 IO](concepts/03-rendering-io.md) — 掌握图表显示和导出

### 深入源码

- [图对象模型](references/graph-obj-model.md) — 从源码解析 BaseFigure/BasePlotlyType/BaseTraceType 类层级、动态属性访问、代码生成机制

### 动手实践

- [基础交互式图表](examples/interactive-charts.md) — 散点图/折线图/柱状图/饼图/热力图/3D表面图/子图的完整代码

## 核心模块速览

| 模块 | 路径 | 功能 |
|------|------|------|
| graph_objects | `plotly/graph_objects/` | 图对象层级（Figure/Layout/Scatter/Bar/...） |
| express | `plotly/express/` | 高级快速绘图 API（scatter/line/bar/...） |
| io | `plotly/io/` | 渲染器、JSON/HTML 序列化、模板、静态导出 |
| basedatatypes | `plotly/basedatatypes.py` | 基类体系（BaseFigure/BasePlotlyType/BaseTraceType/BaseLayoutType） |
| subplots | `plotly/_subplots.py` | make_subplots() 子图创建工具 |
| figure_factory | `plotly/figure_factory/` | 特殊图表工厂（甘特图/等高线/树状图等） |
| colors | `plotly/colors/` | 颜色比例尺与颜色转换工具 |
| tools | `plotly/tools.py` | mpl_to_plotly、FigureFactory 等工具 |

## 版本兼容性说明

- 本文档基于当前源码生成，版本通过 `importlib.metadata` 动态获取
- `plotly.graph_objects` 是推荐的 PEP8 命名，`plotly.graph_objs` 为旧命名兼容入口
- Plotly 6.x 要求 Jupyter Notebook >= 7、JupyterLab >= 3
- 静态图片导出需要安装 kaleido 包：`pip install kaleido`
- Plotly Express 依赖 numpy 和 narwhals（DataFrame 抽象层）
