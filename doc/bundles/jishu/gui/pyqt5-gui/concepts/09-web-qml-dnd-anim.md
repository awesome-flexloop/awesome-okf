---
type: Concept
title: 网页嵌入、QML、拖放剪贴板与属性动画
description: QWebEngineView（Chromium）嵌入网页与 JS 交互；QML 声明式界面加载；基于 MIME 的拖放与 QClipboard；QPropertyAnimation 属性动画
tags: [QWebEngineView, QML, 拖放, QDrag, QMimeData, QClipboard, QPropertyAnimation, 动画]
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

# 网页嵌入、QML、拖放剪贴板与属性动画

## 网页交互：QWebEngineView

PyQt5 使用 **QWebEngineView**（QtWebEngineWidgets 模块）展示 HTML 页面。老版本基于 WebKit 的 `QWebView` 已不再维护——**WebKit 自 Qt 5.5 弃用，Qt6 彻底移除**；WebEngine 基于 **Chromium 内核**，网页兼容性与体验显著更好（F-114）。

```python
from PyQt5.QtWebEngineWidgets import QWebEngineView
view = QWebEngineView()
view.setUrl(QUrl("https://doc.qt.io"))           # 外部网页
view.setHtml("<h1>Hello</h1>")                   # 直接嵌入 HTML
view.page().runJavaScript("alert('hi')")         # 调用 JS
```

Python ↔ JS 双向通信：`runJavaScript()` 调 JS；JS 侧通过 `QWebChannel` 注册的 Python 对象回调槽函数（文集演示了按钮触发 `complete_name` 槽回填表单）。本地 HTML/资源用 `setUrl(QUrl.fromLocalFile(...))`。

## QML 快速开发

QML 是声明式语言，用层级对象 + 属性绑定描述界面，适合动画丰富的现代 GUI。PyQt5 中可用 `QQmlApplicationEngine` 加载 `.qml` 文件运行（与 Qt Quick 控件配合）。

## 拖曳与剪贴板（基于 MIME）

桌面应用中复制/移动对象可通过**拖放（Drag and Drop）**完成：

- **QDrag** 发起拖放操作；
- **QMimeData** 承载数据并与 **MIME 类型**关联（文本 `text/plain`、URL、图片、自定义类型）；
- 控件需 `setAcceptDrops(True)`，重写 `dragEnterEvent`（判断是否接受）、`dropEvent`（取数据）；
- **QClipboard**：`QApplication.clipboard()`，`setText()`/`text()`/`setPixmap()` 操作剪贴板，与复制粘贴逻辑同源。

## 属性动画 QPropertyAnimation

对 Qt 属性做插值动画：

```python
anim = QPropertyAnimation(self.window(), b"geometry")
anim.setDuration(10000)
anim.setStartValue(QRect(0, 0, 100, 30))
anim.setKeyValueAt(0.5, QRect(240, 240, 100, 30))   # 关键帧
anim.setEndValue(QRect(480, 0, 100, 30))
anim.setEasingCurve(QEasingCurve.OutBounce)          # 缓动曲线
anim.start()
```

任何定义了 Qt 属性（pyqtProperty）的对象都可动画化：位置、大小、透明度、颜色等。

## 可运行示例

- [示例 17：网页交互](../examples/17-8cf81ca7d4c8.md)：外部/本地网页、嵌入 HTML、按钮调 JS
- [示例 09：PyQt5 与 QML](../examples/09-26d61806958b.md)
- [示例 21：拖曳与剪贴板](../examples/21-7824a0617393.md)：QDrag/QMimeData/QClipboard
- [示例 10：动画的例子](../examples/10-c6a767ea03f6.md)：QPropertyAnimation 关键帧与缓动
- [示例 08：Button 的简单例子](../examples/08-00e7c13bbefc.md)：信号槽入门（Greetings）

## 事实溯源

F-114（WebKit 弃用版本官方核验）、F-118（拖放 MIME 官方核验）；篇内事实 F-022 ~ F-024、F-049 ~ F-051、F-061 ~ F-063。
