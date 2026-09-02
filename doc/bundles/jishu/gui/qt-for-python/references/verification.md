---
type: Reference
title: "P0 事实核验报告"
generated: { by: "blog-article-to-okf-wiki", at: "2026-09-02T12:00:00+08:00" }
---

# 核验报告

> 核验日期：2026-09-02
> 核验方式：WebSearch + WebFetch 访问 Qt 官方文档（doc.qt.io、www.qt.io）与 Riverbank 官方文档（riverbankcomputing.com）交叉验证
> 核验人：OKF Wiki Bot

## 总结

| 项 | 结果 |
|----|------|
| P0 声明数 | 10 |
| ✅ 通过 | **9** |
| ⚠️ 部分通过（含勘误） | 1 |
| ❌ 失败 | 0 |
| 时效性补充 | 3 |

**结论**：文集内容为 Qt for Python（PySide2）官方文档的中文翻译/学习笔记，文中 API、机制类声明与 Qt 官方文档一致，未发现虚构 API 或杜撰链接。唯一勘误为知识包草稿自身的 WebKit 弃用版本号（5.6 → 官方为 5.5），源文未给出具体版本号，不存在源文硬错误。全部 33 篇文章真实存在、可公开访问，103 张截图全部本地化且引用零缺失。

## 逐项核验

### 1. Qt for Python 官方绑定身份与许可证 — ✅ 通过

- Qt 官网（https://www.qt.io/qt-for-python）原文："Qt for Python offers the official Python bindings for Qt"
- Qt 6 文档许可证原文：Qt Quick 自 Qt 5.4 起以 GNU LGPL v3 或 GNU GPL v2 免费许可证 + 商业许可证提供（https://doc.qt.io/qt-6/qtquick-index.html）
- PySide2 对应 Qt5、PySide6 对应 Qt6 的命名关系在当前最新版（Qt 6.11）仍成立
- 对应事实：F-100

### 2. PyQt5 为 Riverbank 第三方绑定、GPL/商业双授权 — ✅ 通过

- Riverbank 官方介绍页（https://www.riverbankcomputing.com/static/Docs/PyQt5/introduction.html）原文："PyQt5 is dual licensed on all platforms under the Riverbank Commercial License and the GNU General Public License (GPL)"
- 无 LGPL 选项，与 PySide 的许可证差异是选型关键事实；PyQt6 延续同一模式
- 对应事实：F-101

### 3. 信号槽与 uic/rcc 工具命名差异 — ✅ 通过

- Qt for Python 官方信号槽文档使用 QtCore.Signal() / QtCore.Slot()（https://doc.qt.io/qtforpython-6/overviews/signalsandslots.html）
- 官方工具页列出 pyside2-uic、pyside2-rcc（https://doc.qt.io/qtforpython-6/tools/index.html）；Riverbank 介绍页列出 pyuic5、pyrcc5
- 与文集《PySide2 与 Pyqt5 的区别》《Qt signal 和 slot》内容一致
- 对应事实：F-102

### 4. 元对象系统三要素 — ✅ 通过

- Qt 6 官方文档（https://doc.qt.io/qt-6/metaobjects.html）原文："The meta-object system is based on three things: 1. The QObject class... 2. The Q_OBJECT macro... 3. The Meta-Object Compiler (moc)..."
- 与文集《Qt：The Meta-Object System》翻译内容一致；Python 绑定由绑定层自动处理 moc
- 对应事实：F-103

### 5. 事件处理机制 — ✅ 通过

- 官方事件与过滤器文档（https://doc.qt.io/qtforpython-6/overviews/eventsandfilters.html）：可重写 mousePressEvent() 等事件处理器、installEventFilter()/eventFilter() 事件过滤器
- QCoreApplication 文档：sendEvent() 立即同步处理，postEvent() 投递队列由主事件循环下次分发
- 与文集《Qt 事件》《Qt 事件管理》内容一致
- 对应事实：F-104

### 6. QPixmap/QImage/QPicture/QBitmap 四类分工 — ✅ 通过

- Qt 6 绘图系统文档（https://doc.qt.io/qt-6/paintsystem.html）：QPixmap 为屏幕显示优化（平台/后端相关）；QImage 为 I/O 与像素级访问设计、平台无关；QPicture 平台无关地序列化/重放 QPainter 命令；QBitmap 为 1-bit depth 单色 QPixmap
- 与文集《QT 三大绘图类》《Qt 之 QImage/QPicture/QBitmap/QPixmap》《Qt 绘图系统》系列笔记一致
- 时效补充：Qt6 中 QPixmap 渲染后端改为 QRhi，类分工定位不变
- 对应事实：F-105

### 7. Graphics View 框架三核心类 — ✅ 通过

- 官方文档（https://doc.qt.io/qt-6/graphicsview.html）原文："Graphics View provides a surface for managing and interacting with a large number of custom-made 2D graphical items, and a view widget for visualizing the items, with support for zooming and rotation"
- QGraphicsScene/QGraphicsView/QGraphicsItem（含 QGraphicsPixmapItem、QGraphicsItemGroup）类名与文集案例一致
- 时效补充：Qt6 中 Graphics View 保留维护（Qt Quick 为新推场景图路线，Widgets 侧未弃用）
- 对应事实：F-106

### 8. Qt 资源系统 .qrc → rcc → :/ 前缀 — ✅ 通过

- 官方资源文档（https://doc.qt.io/qt-6/resources.html）原文：".qrc file is an XML document that enumerates local files... It serves as input to rcc"；"copy.png will be available in the resource system as :/images/copy.png or qrc:/images/copy.png"
- 与文集《Qt 资源体系(qrc rcc)》一致
- 对应事实：F-107

### 9. WebKit 弃用与 WebEngine 替代 — ⚠️ 通过（含版本号勘误）

- Qt for Python 6.5 WebEngine 概览（https://doc.qt.io/qtforpython-6.5/overviews/qtwebengine-overview.html）原文："Qt WebEngine supersedes the Qt WebKit module... has been deprecated in Qt 5.5"
- Qt 5.4 发行说明（https://doc.qt.io/qt-5.12/whatsnew54.html）：WebEngine 于 Qt 5.4 作为新模块引入，同期宣布 WebKit 将被替代；Qt6 中 QtWebKit/QtWebKitWidgets 彻底移除
- **勘误记录**：知识包草稿曾写"Qt 5.6 弃用"，官方为 **Qt 5.5**；源文（pyqt5-gui 束《网页交互》）仅表述"老版本 QWebView 类不再维护"，未给版本号，无源文错误
- 对应事实：F-108

### 10. QML/Qt Quick 关系、QApplication 单例、事件循环 — ✅ 通过

- Qt Quick 文档（https://doc.qt.io/qt-6/qtquick-index.html）：Qt Qml 模块提供 QML 引擎与语言基础设施，Qt Quick 提供 QML 构建 UI 的基础类型
- QApplication 文档（https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QApplication.html）："For any GUI application using Qt, there is precisely one QApplication object"
- 移植指南：exec_() 因 Python 2 中 exec 为关键字而存在，Python 3 起规范写法为 exec()（exec_ 保留兼容别名）
- 对应事实：F-109

## 源文保真核验

| 检查项 | 结果 |
|--------|------|
| 文章数与文集章节数一致 | ✅ 33/33（shakespeare/v2 API 全文落盘，content_len 均 > 0） |
| 代码块保留 | ✅ 转换后 fenced code block 保留语言标注（python/qml/ini 等） |
| 截图本地化 | ✅ 103 张图片全部复制至 _static/bundles/jishu/gui/qt-for-python/images/，Markdown 引用 0 缺失 |
| 数学公式图 | ✅ math.jianshu.com 渲染图按 alt 文本还原为行内文字（坐标类表达式） |
| 外链处理 | ✅ links.jianshu.com 跳转链接已解包为目标 URL，简书相对路径已补全 |
| 作者身份 | ✅ 简书作者"水之心"，GitHub xinetzone/xinet 仓库真实存在且与文中 xinet/run_qt.py 描述吻合（F-110） |

## 时效性说明

- 文集成文于 2020 年（PySide2 5.11~5.15 / Qt5 时代），当前主流为 PySide6/PyQt6 + Qt 6.11
- 核心机制（信号槽、事件、元对象、绘图系统、Graphics View、资源系统、QML）在 Qt6 中保持稳定，类名与 API 格局不变
- 迁移注意：工具名 pyside2-* → pyside6-*；app.exec_() → app.exec()；QtWebKit 模块在 Qt6 已移除（F-110）
