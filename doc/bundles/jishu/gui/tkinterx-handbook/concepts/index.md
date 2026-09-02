# 概念文档

本目录包含 tkinterx 手册知识包的 6 个概念文档，按学习路径排列：从项目概览到核心画布接口、图形工具、窗体传值、几何画板，再到颜色与待更工具。

## 入门与核心

* [01-tkinterx 概览：安装与模块地图](01-overview.md) — 项目背景、pip 安装、PyPI 元信息核验、模块地图与设计理念。
* [02-CanvasMeta：统一的 2D 画图接口](02-canvas-meta.md) — create_graph 统一绘制直线/椭圆/矩形/弧/多边形、参数说明与 tags 规则。
* [03-规则图形、批量阵列与图形设计工具](03-graph-shapes.md) — create_point/create_circle/create_square、ParamDict、add_row/add_column、canvas_design 的 SimpleGraph/RegularGraph、彩色矩阵与电子限速综合应用。

## 窗体与交互

* [04-WindowMeta：可传递值的窗体](04-window-meta.md) — add_row 行数据、table 字典、create_widget/run 重载、ask_window 跨窗体传值。
* [05-几何画板：Selector 选择器与 GraphPainter 画板](05-geometry-painter.md) — Selector 选择面板、GraphMeta/GraphPainter 交互画板、DrawingWindow 组合窗体与鼠标键盘操作。

## 工具

* [06-颜色工具与抠图工具](06-tools-colors-matting.md) — show_colors 颜色表、140 余条 color_dict 完整字典、作者待更的抠图工具现状说明。

```{toctree}
:hidden:
:maxdepth: 7

01-overview
02-canvas-meta
03-graph-shapes
04-window-meta
05-geometry-painter
06-tools-colors-matting
```