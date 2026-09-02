---
type: Concept
title: PySide2 与 PyQt5：两套 Python 绑定的差异与选型
description: PySide2（官方，LGPL）与 PyQt5（Riverbank，GPL/商业）在许可证、API 命名（Signal/slot 装饰器、uic/rcc 工具）上的差异
tags: [PySide2, PyQt5, 许可证, 选型, Signal]
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

# PySide2 与 PyQt5：两套 Python 绑定的差异与选型

Qt 的 Python 绑定有两套主流实现，API 高度相似但细节不同，选型直接影响项目合规性。

## 身份与许可证（P0 差异）

| 维度 | PySide2 / PySide6 | PyQt5 / PyQt6 |
|------|-------------------|----------------|
| 维护方 | **Qt 官方**（The Qt Company） | **Riverbank Computing**（第三方） |
| 许可证 | **LGPL v3** / GPL v2 / 商业 | **GPL v3** / Riverbank 商业许可证（**无 LGPL**） |
| 对应 Qt 版本 | PySide2↔Qt5，PySide6↔Qt6 | PyQt5↔Qt5，PyQt6↔Qt6 |
| 闭源商用 | LGPL 下动态链接可闭源分发 | 必须购买商业授权或开源（GPL 传染性） |

> 核验来源：Qt 官网与 Riverbank 官方介绍页（F-100、F-101）。

## API 命名差异

| 用途 | PySide2（Qt for Python） | PyQt5 |
|------|--------------------------|-------|
| 定义信号 | `QtCore.Signal(...)` | `QtCore.pyqtSignal(...)` |
| 定义槽 | `QtCore.Slot(...)` | `QtCore.pyqtSlot(...)` |
| .ui 文件转 Python | `pyside2-uic main.ui -o ui_main.py` | `pyuic5 main.ui -o ui_main.py` |
| .qrc 资源转 Python | `pyside2-rcc res.qrc -o rc_res.py` | `pyrcc5 res.qrc -o rc_res.py` |
| 进入事件循环 | `app.exec_()`（Qt6 推荐 `exec()`） | 相同 |

> Qt6 世代工具名相应变为 `pyside6-uic` / `pyuic6` 等（F-102）。

## 迁移建议

1. 新写代码时把信号/槽导入集中在一处，便于整体替换：
   ```python
   # PySide2 写法
   from PySide2.QtCore import Signal, Slot
   # PyQt5 写法
   from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot
   ```
   统一别名后，业务代码几乎可零改动切换。
2. 许可证敏感的闭源商业项目：优先 PySide（LGPL）。
3. 教学/历史项目：PyQt5 中文教程存量更多；本知识包的 pyqt5-gui 束即 PyQt5 体系。

## 可运行示例

- [示例 32：PySide2 与 PyQt5 的区别](../examples/32-296a4646a87a.md)：逐项 API 对照
- [示例 33：PySide2 与 PyQt5 学习资源](../examples/33-2e32587c4b4c.md)：资源清单
- [示例 08：PyQt5 学习资源（未分类）](../examples/08-09f6b4f5432b.md)

## 事实溯源

F-100、F-101、F-102（官方文档核验），详见 [verification](../references/verification.md) 第 1~3 项。
