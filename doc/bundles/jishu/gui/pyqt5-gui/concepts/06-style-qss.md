---
type: Concept
title: 窗口风格、QSS 样式表、窗口背景与不规则窗口
description: QStyle 原生风格切换；QSS（Qt Style Sheets）选择器/子控件/伪状态机制与 QDarkStyleSheet；QPalette 背景；paintEvent 异形窗口与 GIF
tags: [QSS, Qt Style Sheets, QStyle, QPalette, 窗口背景, 不规则窗口, QDarkStyleSheet]
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

# 窗口风格、QSS 样式表、窗口背景与不规则窗口

## 窗口风格（QStyle）

Qt 内置各平台原生风格，可全局或单控件设置：

```python
QStyleFactory.keys()              # 当前平台支持的风格列表
app.setStyle("Fusion")            # 全局风格
widget.setStyle(QStyleFactory.create("Windows"))
```

配合窗口标志 `setWindowFlags()` 可做**无边框窗口**（自行实现拖动/关闭按钮）：先 `QApplication.desktop()` 获取桌面控件与可用屏幕尺寸，再 `setWindowFlags(Qt.FramelessWindowHint)`。

## QSS：Qt Style Sheets

QSS 是用来自定义控件外观的机制，**大量参考 CSS 但功能弱于 CSS**（选择器更少、可用属性更少、并非所有属性都适用于所有控件，F-115）。价值在于**美化与代码分离，便于维护**。

```css
/* 选择器：控件类 #对象名 :伪状态 */
QPushButton#okButton:hover {
    background-color: #4CAF50;
    color: white;
    border-radius: 4px;
}
QLineEdit { border: 1px solid #ccc; padding: 4px; }
```

- **选择器类型**：类型选择器（`QPushButton`）、ID 选择器（`#okButton`，对应 `setObjectName()`）、类选择器、后代选择器、属性选择器；
- **子控件**（subcontrol）：`::up-button`、`::drop-down` 等控制控件内部部件；
- **伪状态**（pseudo-state）：`:hover`、`:checked`、`:disabled`、`:focus`；
- 加载方式：`widget.setStyleSheet(open("style.qss").read())`，或 `app.setStyleSheet()` 全局生效；
- 第三方主题 **QDarkStyleSheet**：`app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())` 一键暗色主题。

## 窗口背景三法

1. **QSS**：`setStyleSheet("background-image: url(bg.png);")`（标签/按钮背景图片同理）；
2. **QPalette**：`palette.setBrush(QPalette.Window, QBrush(QPixmap(...)))`；
3. **paintEvent**：重绘事件里 `painter.drawPixmap(...)`，最灵活。

## 不规则窗口与动画

- 用遮罩实现异形窗口：`widget.setMask(QBitmap(pixmap.mask()))`，点击透明区域不响应；
- 异形窗口动画：定时器/QPropertyAnimation 改变遮罩或几何；
- 加载 GIF：`QMovie("loading.gif")` + `label.setMovie(movie)` + `movie.start()`。

## 可运行示例

- [示例 16：窗口风格](../examples/16-91ac6e3e5cb0.md)
- [示例 15：QSS 的 UI 美化](../examples/15-b66d8273f9d1.md)：语法/选择器/伪状态/QDarkStyleSheet
- [示例 14：设置窗口背景](../examples/14-74595874ad73.md) · [示例 12：设置样式](../examples/12-d23aafed50e6.md)
- [示例 13：不规则窗口的显示](../examples/13-77ab74717607.md)：QWidget 绘图函数表、动画、GIF

## 事实溯源

F-115（QSS 官方核验）；篇内事实 F-034 ~ F-048。
