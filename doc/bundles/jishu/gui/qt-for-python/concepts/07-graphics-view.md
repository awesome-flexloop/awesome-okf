---
type: Concept
title: Graphics View 框架：Scene / View / Item
description: QGraphicsScene、QGraphicsView、QGraphicsItem 三核心协作，支持大量 2D 图元的管理、缩放旋转与交互，含图元组合与滚动区域
tags: [QGraphicsView, QGraphicsScene, QGraphicsItem, Graphics View, 图像浏览器]
generated: { by: "blog-article-to-okf-wiki", at: "2026-09-02T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T12:00:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: jianshu-qt-article-source
    resource: /references/article-source.md
    title: 简书文集事实登记（F-001 ~ F-111）
  - id: qt-official-docs
    resource: https://doc.qt.io/qtforpython-6/
    title: Qt for Python 官方文档
---

# Graphics View 框架：Scene / View / Item

当界面需要管理**大量可交互的 2D 图元**（绘图工具、地图、编辑器、图片浏览器）时，手写 `paintEvent` 不再合适。Qt 提供 **Graphics View 框架**，官方定义其为"管理和交互大量自定义 2D 图形项的表面，以及可视化这些项的视图控件，支持缩放和旋转"（F-106）。

## 三核心类

| 类 | 职责 |
|----|------|
| **QGraphicsScene** | 场景（"舞台"）：持有所有图元、负责事件分发、提供 `items()`/`addItem()`/碰撞检测 |
| **QGraphicsView** | 视图（"摄像机"）：显示场景的控件，支持滚动、缩放（`scale()`）、旋转（`rotate()`） |
| **QGraphicsItem** | 图元（"演员"）：场景中的可视对象，可重写 `paint()`/`boundingRect()`/鼠标事件 |

```python
scene = QGraphicsScene()
scene.addPixmap(QPixmap("image.jpg"))   # 便捷图元 QGraphicsPixmapItem
view = QGraphicsView(scene)             # 一个场景可挂多个视图
view.show()
```

## 常用内置图元

- `QGraphicsPixmapItem`：显示位图（图片浏览器、抠图工具的基础）；
- `QGraphicsRectItem` / `QGraphicsEllipseItem` / `QGraphicsLineItem` / `QGraphicsTextItem`：基本形状与文字；
- `QGraphicsItemGroup`：把多个图元**组合为一个整体**（统一移动/变换），`addToGroup()`/`removeFromGroup()`；
- `QGraphicsPathItem`：任意贝塞尔路径（涂鸦画板核心）。

## 交互与自定义图元

自定义图元继承 `QGraphicsItem`（或便利子类），实现：

- `boundingRect()`：声明图元外接矩形（Qt 据此判断重绘区域，必须准确）；
- `paint(painter, option, widget)`：绘制内容；
- `mousePressEvent()`/`mouseMoveEvent()`：图元级事件处理（坐标为**场景坐标**）。

典型应用模式：

- **几何画板**：矩形/圆形图元 + 鼠标拖拽调整控制点（见示例 03、17）；
- **抠图工具**：QGraphicsPixmapItem 底图 + 可移动选区图元（见示例 15）；
- **图片浏览器**：View 缩放/滚动 + 场景内多 PixmapItem（见示例 18）。

## 与 QScrollArea 的关系

`QScrollArea` 是普通 Widgets 体系的滚动容器（给任何控件加滚动条）；Graphics View 的 View **内置滚动支持**，无需再套 QScrollArea。文集示例 19 演示了 QScrollArea 的独立用法。

## 可运行示例

- [示例 05：QGraphicsView 案例](../examples/05-548ab27a94a2.md)
- [示例 14：QGraphicsItemGroup](../examples/14-8cef5a88e4cc.md)：图元组合
- [示例 16：QGraphicsPixmapItem](../examples/16-5e4c48aed744.md)：位图项
- [示例 17：设计可塑性的矩形框](../examples/17-b1b5f88afe26.md) · [示例 03：制作几何画板](../examples/03-1b742cafce94.md)
- [示例 15：创建抠图工具](../examples/15-ba17fab5f60c.md) · [示例 18：图片浏览器](../examples/18-262146cc6dda.md)
- [示例 19：QScrollArea](../examples/19-645545f47750.md)：滚动容器对照

## 事实溯源

F-106（Qt 6 Graphics View 官方文档核验），详见 [verification](../references/verification.md) 第 7 项。
