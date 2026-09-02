---
type: Example
title: "几何画板应用：Selector + GraphPainter"
description: "分步构建交互式几何画板：形状颜色选择面板、GraphMeta 画图面板、GraphPainter 完整窗体，含鼠标键盘操作说明"
tags: [tkinter, tkinterx, gui, painter, Selector, GraphMeta, GraphPainter, interactive]
generated: { by: "blog-article-to-okf-wiki/trae", at: "2026-09-02T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T18:00:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: tkinterx-handbook-jianshu
    resource: /references/sources.md
---

# 几何画板应用：Selector + GraphPainter

本示例按手册 F-TXH-01 的三个递进步骤，构建一个可用鼠标绘图、拖动、删除图形的几何画板。[^F-TXH-01]

## 第 1 步：选择面板 Selector

`tkinterx.graph.canvas_design.Selector` 提供图形形状与颜色的选择按钮：[^F-TXH-01]

```python
from tkinter import Tk
from tkinterx.graph.canvas_design import Selector
root = Tk()
select = Selector(root, background='skyblue')
select.grid()
root.mainloop()
```

运行后得到天蓝背景的选择面板：

![第 1 步效果：Selector 选择面板](../../../../../_static/bundles/jishu/gui/tkinterx-handbook/images/1a08da0a098f-1114626-be69fec8072a9aad.webp)

## 第 2 步：画图面板 GraphMeta

把 Selector 传给 `tkinterx.graph.painter.GraphMeta`，调用 `bind_drawing()` 绑定鼠标绘图事件：[^F-TXH-01]

```python
from tkinter import Tk
from tkinterx.graph.canvas_design import Selector
from tkinterx.graph.painter import GraphMeta

root = Tk()
selector = Selector(root, background='skyblue')
self = GraphMeta(root, selector)
self.bind_drawing()
selector.grid()
self.grid()
root.mainloop()
```

此时已可在下方画布上用鼠标作图，并通过选择器切换形状与颜色：

![第 2 步效果：Selector + GraphMeta 组合画板](../../../../../_static/bundles/jishu/gui/tkinterx-handbook/images/1a08da0a098f-1114626-cbece1b761d41e13.webp)

## 第 3 步：完整窗体 DrawingWindow

使用 `tkinterx.graph.painter.GraphPainter` 封装完整交互（`bind_drawing()` 绑定绘图、`bind_master()` 绑定主窗体快捷键），并将选择器与画板上下布局：[^F-TXH-01]

```python
from tkinter import Tk
from tkinterx.graph.canvas_design import Selector
from tkinterx.graph.painter import GraphPainter

class DrawingWindow(Tk):
    def __init__(self, **win_kw):
        super().__init__(**win_kw)
        self.selector = Selector(self, background='skyblue', width=350, height=90)
        self.painter = GraphPainter(self, self.selector, background='pink')
        self.painter.bind_drawing()
        self.painter.bind_master()

    def layout(self, row=0, column=0):
        self.selector.grid(row=row, column=column)
        self.painter.grid(row=row+1, column=column, sticky='nesw')

self = DrawingWindow()
self.layout(row=0, column=0)
self.mainloop()
```

运行效果：

![第 3 步效果：完整几何画板窗体](../../../../../_static/bundles/jishu/gui/tkinterx-handbook/images/1a08da0a098f-1114626-48876737c3b24ee8.webp)

## 交互操作速查

| 操作 | 效果 |
|------|------|
| 鼠标左键按下并拖动 | 在粉色画布上绘制选择器指定形状/颜色的图形（绘制中边框为加粗虚线，释放后变实线） |
| 鼠标左键点击图形后拖动 | 移动单个图形 |
| **Ctrl + a** | 选中画布全部图形，随后可整体拖动 |
| **F1** | 清空画布 |
| 鼠标悬停在图形上按 **Del** | 删除该图形 |
| 选中图形后按**方向键** | 按方向键方向微移图形 |
| 选择器按钮 | 切换画笔颜色与所画图形的形状（可自定义） |

内部通过实例变量 `record_bbox = [x0, y0, x1, y1]` 追踪鼠标位置：`(x0, y0)` 记录左键按下位置，`(x1, y1)` 记录鼠标实时位置；左键释放后 `(x0, y0)` 被置为 `['none']*2`。

## 延伸阅读

- [几何画板：Selector 选择器与 GraphPainter 画板](../concepts/05-geometry-painter.md) — 概念与事件模型详解
- [CanvasMeta：统一的 2D 画图接口](../concepts/02-canvas-meta.md) — 画板底层绘图接口
- [规则图形与批量阵列](../concepts/03-graph-shapes.md) — Selector 所在的 canvas_design 模块
- [《tkinterx 手册》信源登记](../references/sources.md)

[^F-TXH-01]: 简书《tkinter 的拓展包：tkinterx》，见[信源登记](../references/sources.md)。