# 概念体系索引

本束概念文档按"术语 → 架构 → 机制 → 专项能力"递进组织：

| # | 概念文档 | 覆盖内容 |
|---|---------|---------|
| 1 | [GUI 与 GUI toolkit 核心术语](01-gui-terminology.md) | 窗口/控件/布局/事件循环、GUI 工具包角色 |
| 2 | [Qt 架构与 Qt for Python 模块体系](02-qt-architecture.md) | QtCore/QtGui/QtWidgets/QtQml、QApplication 单例 |
| 3 | [PySide2 与 PyQt5 差异与选型](03-pyside-vs-pyqt.md) | 许可证（LGPL vs GPL）、Signal/pyqtSignal、uic/rcc 工具 |
| 4 | [元对象系统、信号槽与事件](04-meta-signal-slot-event.md) | QObject/Q_OBJECT/moc、信号连接、事件过滤器 |
| 5 | [Qt 绘图系统](05-paint-system.md) | QPainter/QPen/QBrush、paintEvent、QPalette |
| 6 | [四大图像类](06-image-classes.md) | QPixmap/QImage/QPicture/QBitmap 分工与选型 |
| 7 | [Graphics View 框架](07-graphics-view.md) | Scene/View/Item、图元组合、缩放交互 |
| 8 | [资源系统与 QML](08-resources-and-qml.md) | .qrc/rcc、:/ 资源前缀、QML/Qt Quick 声明式 UI |

学习路径：**1 → 2 → 3 → 4**（建立全局观）→ **5 → 6 → 7**（绘图与图形方向深入）→ **8**（资源与 QML 扩展）。

```{toctree}
:maxdepth: 1

01-gui-terminology
02-qt-architecture
03-pyside-vs-pyqt
04-meta-signal-slot-event
05-paint-system
06-image-classes
07-graphics-view
08-resources-and-qml
```
