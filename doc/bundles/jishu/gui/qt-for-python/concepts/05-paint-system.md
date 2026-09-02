---
type: Concept
title: Qt 绘图系统：QPainter / QPen / QBrush 与 paintEvent
description: Qt 2D 绘图三核心类、paintEvent 绘制时机、坐标系统，以及 QPalette 调色板对控件配色的作用
tags: [QPainter, QPen, QBrush, paintEvent, QPalette, 绘图]
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

# Qt 绘图系统：QPainter / QPen / QBrush 与 paintEvent

Qt 的绘图系统可以渲染**矢量图形、位图图像和轮廓字体文本**。在 Widgets 体系中，一切自定义绘制都从 `paintEvent` 开始。

## 三核心类

| 类 | 角色 | 比喻 |
|----|------|------|
| **QPainter** | 执行绘制动作的"画家"：画线、矩形、圆、文字、图片 | 握笔的手 |
| **QPen** | 控制轮廓：颜色、线宽、线型（实线/虚线）、端点样式 | 画笔的笔尖 |
| **QBrush** | 控制填充：填充色、渐变、图案（纹理） | 颜料桶 |

典型绘制流程（必须在 `paintEvent` 或 `QPicture` 记录上下文中进行）：

```python
def paintEvent(self, event):
    painter = QPainter(self)                 # 在本控件上绘制
    painter.setPen(QPen(Qt.red, 2, Qt.DashLine))   # 红色虚线轮廓
    painter.setBrush(QBrush(Qt.blue))        # 蓝色填充
    painter.drawRect(10, 10, 100, 60)        # 画矩形
    painter.drawText(20, 50, "Hello")        # 画文字
```

## paintEvent 与绘制时机

- 控件需要重绘时（首次显示、被遮挡后恢复、调用 `update()`），Qt 派发绘制事件，触发 `paintEvent`；
- **不要**在 `paintEvent` 外直接创建 `QPainter(self)` 绘制；需要刷新时调用 `self.update()` 请求重绘；
- 频繁绘制应配合 `QPainter` 的抗锯齿设置 `renderHint = QPainter.Antialiasing`。

## 坐标系统

- 默认以控件左上角为原点 `(0,0)`，x 向右、y 向下，单位为像素；
- `QPainter` 支持 `translate()`/`rotate()`/`scale()`/`save()`/`restore()` 做坐标变换（几何画板类应用的核心）；
- 高分屏由 Qt 的设备像素比（devicePixelRatio）机制处理，`QPixmap` 可 `setDevicePixelRatio` 保持清晰。

## QPalette 调色板

`QPalette` 集中管理控件各状态下的颜色角色：窗口背景（Window）、窗口文字（WindowText）、按钮（Button）、高亮（Highlight）等。可通过 `widget.setPalette(palette)` 或 `app.setPalette(palette)` 应用，是不用 QSS 时改配色的官方手段。

## 关键要点

1. 画**形状/文字**用 QPainter + QPen/QBrush；画**位图**用 drawPixmap/drawImage（图像类选型见 [四大图像类](06-image-classes.md)）。
2. 自定义控件绘制 = 重写 `paintEvent` + 数据变化时 `update()`。
3. 复杂场景（大量可交互图元、缩放旋转）不要手写 paintEvent，应使用 [Graphics View 框架](07-graphics-view.md)。

## 可运行示例

- [示例 20：Qt 绘图系统](../examples/20-616d329f88d8.md)：绘图系统官方文档译注
- [示例 01：Qt5 绘制图形](../examples/01-e77efbe99288.md)：基础图形绘制
- [示例 02：Qt5 绘制图像与鼠标绘图](../examples/02-00649c377907.md)：鼠标轨迹绘制（事件 + 绘图综合）
- [示例 04：QPalette for Python](../examples/04-8884f22d281d.md)：调色板用法

## 事实溯源

F-105（绘图系统官方核验），篇内事实见 [article-source](../references/article-source.md)。
