---
type: Reference
title: "P0 事实核验报告"
generated: { by: "blog-article-to-okf-wiki", at: "2026-09-02T12:00:00+08:00" }
---

# 核验报告

> 核验日期：2026-09-02
> 核验方式：WebSearch + WebFetch 访问 Qt 官方文档（doc.qt.io）与 Riverbank 官方文档（riverbankcomputing.com）交叉验证
> 核验人：OKF Wiki Bot

## 总结

| 项 | 结果 |
|----|------|
| P0 声明数 | 8 |
| ✅ 通过 | **8** |
| ⚠️ 部分通过（含勘误） | 0（勘误 1 项已在 qt-for-python 束记录，本束源文无版本号硬错误） |
| ❌ 失败 | 0 |
| 时效性补充 | 2 |

**结论**：文集为《PyQt5快速开发与实战》学习笔记并重组 zetcode 公开教程，控件类名、机制描述与 PyQt5/Qt5 官方文档一致，未发现虚构 API。全部 36 篇文章真实存在、可公开访问（含 2 篇作者自标注的代码片段/未完稿短文，已在事实登记中标注），178 张截图全部本地化且引用零缺失。

## 逐项核验

### 1. PyQt5 身份与许可证 — ✅ 通过

- Riverbank 官方介绍页（https://www.riverbankcomputing.com/static/Docs/PyQt5/introduction.html）："PyQt5 is dual licensed... under the Riverbank Commercial License and the GNU General Public License (GPL)"
- 与文集《架构简介》"PyQt5 是对 Digia Qt5 的 Python 绑定（Riverbank）"表述一致
- 对应事实：F-109

### 2. QApplication 单例与事件循环 — ✅ 通过

- 官方 QApplication 文档（https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QApplication.html）："there is precisely one QApplication object"
- 与文集《创建简单窗口》"You need one (and only one) QApplication instance per application"一致；exec_() 为 PySide2/PyQt5 + Python2 时代写法
- 对应事实：F-110

### 3. 信号槽与工具链命名 — ✅ 通过

- PyQt5 使用 pyqtSignal/pyqtSlot；pyuic5 转 .ui、pyrcc5 转 .qrc（Riverbank 介绍页工具清单）
- 与文集《Button 的简单例子》《vscode 计算器》（Qt Designer 模板对应 QMainWindow/QDialog/QWidget）一致
- 对应事实：F-111、F-112

### 4. 事件驱动模型 — ✅ 通过

- 官方事件文档（https://doc.qt.io/qtforpython-6/overviews/eventsandfilters.html）：应用进入主事件循环后监听分发事件
- 与文集《多线程》中"调用 exec_() 进入主循环"、耗时操作阻塞主线程导致卡顿的描述一致
- 对应事实：F-113

### 5. QWebEngineView 替代 QWebView — ✅ 通过（源文表述准确）

- 官方（https://doc.qt.io/qtforpython-6.5/overviews/qtwebengine-overview.html）：Qt WebKit "has been deprecated in Qt 5.5"，WebEngine 于 Qt 5.4 引入、Qt6 中 WebKit 彻底移除
- 源文《网页交互》表述："PyQt5 使用 QWebEngineView 控件来展示 HTML 页面，对老版本中的 QWebView 类不再进行维护，因 QWebEngineView 使用 Chromium 内核"——方向与事实准确，未给版本号故无硬错误
- 对应事实：F-114

### 6. QSS 样式表机制 — ✅ 通过

- Qt 样式表参考（https://doc.qt.io/qt-6/stylesheet-reference.html）：QSS 语法参考 CSS，支持选择器、子控件（::subcontrol）、伪状态（:pseudo-state）
- 与文集《QSS的UI美化》"QSS 大量参考了 CSS 的内容，但 QSS 的功能比 CSS 要弱得多"一致
- 对应事实：F-115

### 7. 多线程 QTimer/QThread — ✅ 通过

- Qt 线程文档（https://doc.qt.io/qt-6/thread-basics.html）：GUI 主线程阻塞会导致界面冻结，工作线程用 QThread
- 与文集《多线程》三种方法（QTimer/QThread/事件处理）一致
- 对应事实：F-116

### 8. Item View、拖放、国际化、绘图三核心 — ✅ 通过

- Model/View（https://doc.qt.io/qt-6/model-view-programming.html）：QListView/QTableView/QTreeView + 便利类 QListWidget/QTableWidget/QTreeWidget，与《表格与树》一致（F-117）
- 拖放（https://doc.qt.io/qt-6/dnd.html）：QDrag + QMimeData 基于 MIME，与《拖曳与剪贴板》一致（F-118）
- 国际化（https://doc.qt.io/qt-6/linguist-translators.html）：lupdate/Linguist/lrelease 工具链，与《PyQt5 国际化》一致（F-119）
- 绘图系统（https://doc.qt.io/qt-6/paintsystem.html）：QPainter/QPen/QBrush 三核心，与《窗口绘图类控件 QPainter》一致（F-120）

## 源文保真核验

| 检查项 | 结果 |
|--------|------|
| 文章数与文集章节数一致 | ✅ 36/36（shakespeare/v2 API 全文落盘） |
| 未完稿/片段型文章 | ✅ 已如实标注：《橡皮筋组件（待更）》作者自标"待更"；《2020-07-03》为描述符练习代码片段；《PyQt5 & NetworkX》为探索性代码片段 |
| 代码块保留 | ✅ fenced code block 保留语言标注 |
| 截图本地化 | ✅ 178 张图片全部复制至 _static/bundles/jishu/gui/pyqt5-gui/images/，Markdown 引用 0 缺失 |
| 外链处理 | ✅ links.jianshu.com 跳转解包、相对路径补全 |

## 时效性说明

- 文集成文于 2020 年（PyQt5/Qt5 时代），当前 PyQt6/Qt6 下控件类名、布局、信号槽、QSS、QThread、QWebEngine 等机制基本不变（F-121）
- 迁移注意：pyuic5/pyrcc5 → pyuic6/pyrcc6；exec_() → exec()；打包 PyInstaller 流程不变（F-122）
