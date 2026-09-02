---
type: Concept
title: Qt 架构与 Qt for Python 模块体系
description: Qt 模块划分（QtCore/QtGui/QtWidgets/QtQml/QtQuick）、QApplication 单例与事件循环、Qt for Python 官方绑定的定位
tags: [Qt, 架构, QApplication, 事件循环, PySide]
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

# Qt 架构与 Qt for Python 模块体系

## Qt for Python 是什么

**Qt for Python** 是 Qt 官方提供的 Python 绑定项目（官网原文："Qt for Python offers the official Python bindings for Qt"），核心产物是 **PySide2**（对应 Qt5）与 **PySide6**（对应 Qt6）。它让开发者可以用 Python 调用 Qt 的全部能力，同时保留 Qt 的跨平台特性与原生性能。

许可证为 GNU LGPL v3 / GNU GPL v2 / 商业许可证三重授权（F-100）。

## 模块体系

Qt 按功能划分为多个模块，Python 中以子包形式导入：

| 模块 | 职责 | 典型类 |
|------|------|--------|
| **QtCore** | 非 GUI 核心机制：对象模型、信号槽、事件循环、定时器、线程、文件 I/O | `QObject`、`QCoreApplication`、`QTimer`、`QThread` |
| **QtGui** | 绘图、字体、颜色、图像、2D 图形基础设施 | `QPainter`、`QPixmap`、`QImage`、`QPalette` |
| **QtWidgets** | 传统 Widgets 风格 UI 控件集 | `QApplication`、`QWidget`、`QMainWindow`、`QPushButton` |
| **QtQml / QtQuick** | QML 引擎与声明式 UI 框架（Qt Quick） | `QmlEngine`、QML 类型系统 |
| **QtWebEngineWidgets** | 基于 Chromium 的网页嵌入 | `QWebEngineView` |

> 记忆法：**Core 管机制，Gui 管画笔，Widgets 管控件，Qml/Quick 管声明式界面**。

## 应用骨架：QApplication 与事件循环

任何 Qt GUI 应用有且仅有一个 `QApplication` 实例（官方原文："there is precisely one QApplication object"，F-109），最小骨架为：

```python
import sys
from PySide2.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)   # 1. 全局应用对象（唯一）
label = QLabel("Hello Qt")     # 2. 创建控件
label.show()                   # 3. 显示窗口
sys.exit(app.exec_())          # 4. 进入主事件循环（Qt6 推荐 app.exec()）
```

- `exec_()` 因 Python 2 中 `exec` 是关键字而加下划线；Python 3 / Qt6 起规范写法是 `app.exec()`。
- 事件循环内：事件被放入队列 → 主循环取出 → 分发给目标控件的事件处理器（如 `mousePressEvent`）→ 可能触发信号 → 信号驱动槽函数完成业务逻辑。

## 关键要点

1. 选型：商业闭源项目优先评估 PySide（LGPL），GPL 兼容项目 PyQt/PySide 均可（详见 [双绑定差异](03-pyside-vs-pyqt.md)）。
2. 导入约定：`from PySide2.QtWidgets import ...`（PyQt5 为 `from PyQt5.QtWidgets import ...`，API 高度一致）。
3. 界面技术路线二选一：**Widgets**（成熟、类多、适合传统桌面应用）或 **Qt Quick/QML**（声明式、动画与触摸场景强）。

## 可运行示例

- [示例 31：Qt5 开发入门](../examples/31-55c84ecaf4c0.md)：最小应用骨架
- [示例 11：Qt 简介](../examples/11-200d660116a6.md) · [示例 10：Qt 概述](../examples/10-52ae86ce104f.md)
- [示例 09：GUI 开发资源库](../examples/09-770d0c2e9df8.md) · [示例 33：PySide2 与 PyQt5 学习资源](../examples/33-2e32587c4b4c.md)

## 事实溯源

F-100、F-109（QApplication 单例、许可证，官方文档核验）；篇内事实见 [article-source](../references/article-source.md)。
