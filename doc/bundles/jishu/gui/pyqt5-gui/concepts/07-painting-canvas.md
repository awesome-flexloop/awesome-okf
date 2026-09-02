---
type: Concept
title: QPainter 绘图控件与图形编辑工具实战
description: QPainter/QPen/QBrush 在控件上的绘图基础；labelme 式涂鸦画板、QRubberBand 橡皮筋选区、NetworkX 图谱嵌入的实战模式与参数集中管理
tags: [QPainter, QPen, QBrush, QRubberBand, 涂鸦画板, mouseMoveEvent, NetworkX, 图像编辑]
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

# QPainter 绘图控件与图形编辑工具实战

## 绘图基础

PyQt5 绘图系统能渲染**矢量图像、位图图像和轮廓字体文本**，核心三个类：**QPainter**（画家）、**QPen**（画笔，轮廓）、**QBrush**（画刷，填充）。显示本地图像用 `QPixmap`（图像呈现本质也是绘图）。详见 qt-for-python 束《Qt 绘图系统》概念。

## 鼠标交互式绘图模式

涂鸦/画板类应用的统一模式（重写鼠标事件 + 缓冲图层）：

1. 维护一个 `QPixmap` 作为画布缓冲（或 `QGraphicsScene`）；
2. `mousePressEvent`：记录起点，开始路径；
3. `mouseMoveEvent`：在缓冲上 `painter.drawLine(last, current)` 连线，`update()` 刷新；
4. `mouseReleaseEvent`：结束笔画；
5. `paintEvent`：把缓冲 `drawPixmap` 到控件。

多彩涂鸦：每笔随机/可选颜色（`QPen(QColor(...))`），可切换粗细。

## 借鉴 labelme 组织图像编辑工具

文集作者借鉴开源标注工具 [wkentaro/labelme](https://github.com/wkentaro/labelme) 的架构经验：

- 画布封装为独立 widget（`PrettyWidget`/Canvas 类），工具栏按钮切换模式（涂鸦/矩形/多边形）；
- **参数集中管理**：`utils/params.py` 统一存放画笔颜色、线宽、画布尺寸等配置，避免魔法数字散落；
- 橡皮筋选区：`QRubberBand` + `QRect/QSize/QPoint` 记录选择区域，配合 `QCheckBox` 等控制选项。

## NetworkX 图谱嵌入

把 NetworkX 的图布局（spring_layout 等）渲染到 QWidget：NetworkX 只负责算坐标，绘制交给 QPainter 或 matplotlib Figure 嵌入；文集提供了多按钮切换不同布局的探索性实现（代码片段型，见示例 01）。

## Python 描述符小技

封装图形属性时可用 Python 描述符：`__set__` 中 `isinstance(value, self.custom_type)` 判断，命中则 `custom_type(value)` 否则 `custom_type(*value)`，实现赋值时自动类型包装（示例 02，作者的语言基础练习）。

## 可运行示例

- [示例 22：窗口绘图类控件 QPainter](../examples/22-8d5614635b83.md)
- [示例 03：图形编辑工具之涂鸦](../examples/03-e4b9152524a1.md)：涂鸦简笔画、多彩画板、params.py 管理（15 段代码、3 图）
- [示例 04：橡皮筋组件（待更）](../examples/04-da2b6001733e.md)：QRubberBand + QRect/QPoint（作者标注未完稿）
- [示例 01：PyQt5 & NetworkX](../examples/01-31fe0eb4a8a6.md)：NetworkX 嵌入尝试（代码片段型）
- [示例 02：2020-07-03 描述符练习](../examples/02-cf0d9b7eff2c.md)：descriptor 类型转换

## 事实溯源

F-120（绘图三核心官方核验）；篇内事实 F-001 ~ F-009。
