---
okf_version: "0.2"
type: group
title: "🖥️ GUI 桌面开发"
description: "Qt/PyQt Python 桌面 GUI 开发知识包分组——Qt for Python（PySide2）官方机制与 PyQt5 系统化实战"
total_bundles: 2
completed_bundles: 2
groups: "GUI桌面开发"
---

# 🖥️ GUI 桌面开发

> 本分组收录 Qt 技术栈 Python 桌面 GUI 开发知识包，来源为简书作者 **水之心**（xinetzone）两套公开学习文集（共 69 篇，2020 年），经 blog-article-to-okf-wiki 七阶段流程整理：事实登记 F-001 ~ F-234，P0 事实经 Qt/Riverbank 官方文档交叉核验，281 张原文截图完整本地化。

![Qt/PyQt Python 桌面 GUI 开发知识地图：等距视角的应用窗口由按钮、滑块、表格、画布对话框等控件积木拼成，绿色信号槽连线贯穿其间，Python 蛇环绕窗框，齿轮与计时器寓意多线程](/_static/bundles/jishu/gui/images/gui-group-hero.jpg)

## 知识包清单

| 知识包 | 定位 | 内容 |
|--------|------|------|
| [qt-for-python](qt-for-python/index.md) | **官方机制与原理**（PySide2 官方文档译注） | 33 篇：Qt 架构、元对象/信号槽/事件、绘图系统、四大图像类、Graphics View、资源系统、QML；8 篇概念 + 103 张截图 |
| [pyqt5-gui](pyqt5-gui/index.md) | **系统化实战**（《PyQt5快速开发与实战》笔记） | 36 篇：环境/Designer/打包、控件与布局、容器与 Model/View、对话框与国际化、QSS、绘图实战、多线程、WebEngine/QML/动画、数据可视化；10 篇概念 + 178 张截图 |

## 两束关系

- **qt-for-python** 回答"Qt 机制是什么、为什么"——官方文档视角，偏原理；
- **pyqt5-gui** 回答"桌面应用怎么一步步做出来"——控件手册 + 实战视角，偏工程；
- 两束共享同一套 Qt 底层机制（信号槽、事件、绘图），概念文档互相交叉引用，可对照阅读。

## 知识地图

```mermaid
flowchart TB
    G["🖥️ GUI 桌面开发分组"]
    A["qt-for-python<br/>官方机制与原理"]
    B["pyqt5-gui<br/>系统化实战"]
    G --> A
    G --> B
    A --> A1["Qt 架构与模块体系"]
    A --> A2["元对象系统<br/>信号槽与事件"]
    A --> A3["绘图系统<br/>QPainter 与四大图像类"]
    A --> A4["Graphics View 框架"]
    A --> A5["资源系统与 QML"]
    B --> B1["环境搭建与 Designer"]
    B --> B2["控件布局与容器"]
    B --> B3["对话框与国际化"]
    B --> B4["QSS 样式与美化"]
    B --> B5["绘图实战与多线程"]
    B --> B6["WebEngine/QML/动画/可视化"]
    A2 -. 共享底层机制 .-> B5
    A3 -. 共享底层机制 .-> B5
```

```{toctree}
:maxdepth: 1

qt-for-python/index
pyqt5-gui/index
```
