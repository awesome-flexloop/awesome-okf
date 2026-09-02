---
type: Concept
title: 对话框体系与 Qt Linguist 国际化
description: QDialog 自定义对话框、QMessageBox/QInputDialog/QFileDialog/QFontDialog/QColorDialog 标准对话框，以及 lupdate/Linguist/lrelease 翻译工作流
tags: [QDialog, QMessageBox, QFileDialog, QFontDialog, QColorDialog, Qt Linguist, 国际化, i18n]
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

# 对话框体系与 Qt Linguist 国际化

## 对话框是什么

对话框是人与程序之间的"对话"窗口：输入数据、修改设置、确认操作。分两类：

- **模态对话框**：`exec_()` 阻塞父窗口，关闭前必须先处理（设置页常用）；
- **非模态对话框**：`show()` 打开，不阻塞（查找面板常用）。

## 标准对话框（开箱即用）

| 类 | 用途 | 典型方法 |
|----|------|---------|
| QMessageBox | 消息/确认框 | `information()`/`warning()`/`question()`（返回点击的按钮） |
| QInputDialog | 单值输入 | `getText()`/`getInt()`/`getItem()` |
| QFileDialog | 文件选择 | `getOpenFileName()`/`getSaveFileName()`/`getExistingDirectory()` |
| QFontDialog | 选字体 | `getFont()` 返回 (QFont, ok) |
| QColorDialog | 选颜色 | `getColor()` 返回 QColor |

## 自定义对话框

继承 `QDialog`，放置输入控件 + 确定/取消按钮（`QDialogButtonBox`），用 `accept()`/`reject()` 返回，调用方按返回值取值：

```python
dlg = Form(self)
if dlg.exec_() == QDialog.Accepted:
    name = dlg.name_edit.text()
```

## Qt Linguist 国际化工作流

官方工具链三步（F-119）：

1. **lupdate**（Release manager）：扫描源码中 `tr("...")` 包裹的待翻译字符串，生成/更新 `.ts` 翻译文件；
2. **Qt Linguist**（翻译者）：打开 `.ts`，逐条填写译文；
3. **lrelease**：把 `.ts` 编译为二进制 `.qm`；程序运行时用 `QTranslator` 加载 `.qm` 并 `app.installTranslator()`，**可动态切换界面语言**。

```python
trans = QTranslator()
trans.load("zh_CN.qm")
app.installTranslator(trans)   # 所有 tr() 文本立即显示译文
```

> 要点：源码中所有面向用户的字符串都用 `self.tr("...")` 包裹，lupdate 才能提取。

## 可运行示例

- [示例 23：对话框类控件](../examples/23-66464e94a4d4.md)：全部标准对话框（12 张截图）
- [示例 07：自定义对话框](../examples/07-9070c2ef0c06.md)：Form(QDialog) 输入名字弹问候
- [示例 05：PyQt5 国际化](../examples/05-010bebde9577.md)：lupdate/Linguist/lrelease + 动态切换语言全流程

## 事实溯源

F-119（Linguist 官方核验）；篇内事实 F-013 ~ F-015、F-067 ~ F-069。
