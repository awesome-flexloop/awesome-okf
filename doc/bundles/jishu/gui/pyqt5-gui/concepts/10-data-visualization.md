---
type: Concept
title: 数据可视化工具实战与学习资源
description: 以 USGS 实时地震数据为例的数据可视化工具构建路径，以及 PyQt5/Qt for Python 官方学习资源索引
tags: [数据可视化, USGS, CSV, matplotlib, 学习资源]
generated: { by: "blog-article-to-okf-wiki", at: "2026-09-02T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T12:00:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: jianshu-gui-article-source
    resource: /references/article-source.md
    title: 简书文集事实登记（F-001 ~ F-123）
  - id: pyqt5-official-docs
    resource: https://www.riverbankcomputing.com/static/Docs/PyQt5/
    title: PyQt5 官方文档
---

# 数据可视化工具实战与学习资源

## 数据可视化工具教程

官方 **Data Visualization Tool Tutorial** 以美国地质调查局（USGS）实时地震数据为例构建桌面可视化工具：

- 数据源：`earthquake.usgs.gov` 提供的 `all_day.csv`（全球当日地震记录，含经纬度、震级、深度、时间等字段）；
- 技术路径：Qt 网络请求/本地 CSV 读取 → `QAbstractTableModel` 承载表格数据 → QTableView 展示 → 配合 matplotlib（FigureCanvasQTAgg 嵌入）或 Qt 绘图做散点/柱状可视化；
- 教学价值：串联 Model/View、网络、文件 I/O 与绘图，是"控件学会之后做什么"的综合范例。

> 文集该篇为参考教程型笔记，建议配合官方教程原文与本束 [Model/View 概念](04-containers-itemviews.md)、[绘图概念](07-painting-canvas.md) 一起实践。

## 权威学习资源（按可信度排序）

1. **Qt Documentation**：https://doc.qt.io/ 与 Qt for Python：https://doc.qt.io/qtforpython —— P0 一手资料；
2. **PyQt5 官方主页/文档**：https://www.riverbankcomputing.com/static/Docs/PyQt5/ —— 绑定差异权威来源；
3. **Python 官方 wiki 的 PyQt 条目** 与 zetcode PyQt5 教程（http://zetcode.com/gui/pyqt5/）——本束系统化学习笔记的主要参考结构；
4. 拖放专项教程、图标资源站（控件图标）等见示例 11 的完整链接清单。

## 可运行示例

- [示例 06：PyQt5 数据可视化](../examples/06-a24a4dfdd544.md)：USGS all_day.csv 数据可视化工具
- [示例 11：PyQt5 学习资源](../examples/11-9e3bde8b2df5.md)：官方文档/教程/图标资源链接索引

## 事实溯源

篇内事实 F-016 ~ F-018、F-031 ~ F-033；资源链接以官方站点为准（F-121 时效性说明）。
