---
type: Concept
title: 第一个窗口、QLabel、布局管理与文本框
description: QApplication 骨架与提示/图标/消息框；QLabel 文本与对齐；绝对布局 vs 布局管理器（QHBoxLayout/QVBoxLayout/QGridLayout）；QLineEdit/QTextEdit
tags: [QApplication, QMainWindow, QLabel, 布局, QHBoxLayout, QLineEdit, QTextEdit]
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

# 第一个窗口、QLabel、布局管理与文本框

## 应用骨架

每个应用需要且**仅有一个** `QApplication` 实例（F-110）：

```python
import sys
from PyQt5.QtWidgets import QApplication, QWidget

app = QApplication(sys.argv)   # sys.argv 允许命令行参数；不用可传 []
w = QWidget()
w.show()
sys.exit(app.exec_())          # 进入主事件循环
```

常见窗口装饰：`setWindowTitle()`、`setWindowIcon(QIcon(...))`、`setToolTip("提示")`（悬停提示）、`QMessageBox.information(...)`（消息框）、`move()`/`resize()` 定位与居中。

## QLabel 标签

`QLabel` 显示文本或图片：`setText()`、`setPixmap()`、`setAlignment(Qt.AlignCenter)`、`setFont(QFont(...))`。还支持**富文本/HTML 方式设置文本**（文集原话："This HTML approach will be valid too"），可直接放 `<b>`、`<a href>` 等标签。

## 布局管理

管理控件位置与嵌套关系有两种方式：

| 方式 | 特点 | 评价 |
|------|------|------|
| **绝对布局** `move(x,y)` | 像素硬编码 | 控件不随窗口缩放自适应，多语言/多平台易错位，不推荐 |
| **布局管理器** | 自动计算位置尺寸 | ✅ 推荐，窗口缩放自动重排 |

三种基础布局：`QHBoxLayout`（水平）、`QVBoxLayout`（垂直）、`QGridLayout`（网格）；可嵌套组合成全局布局：

```python
layout = QVBoxLayout()
layout.addWidget(btn1)
layout.addWidget(btn2)
layout.addLayout(sub_hbox)   # 嵌套子布局
self.setLayout(layout)       # 应用到窗口
```

配合 `addSpacing()`/`addStretch()` 控制间距与弹性空白。

## 文本框类控件

- **QLineEdit**：**单行**文本输入——密码模式 `setEchoMode(QLineEdit.Password)`、占位提示 `setPlaceholderText()`、校验器 `setValidator()`、`textChanged` 信号；
- **QTextEdit**：**多行**富文本编辑——支持 HTML、`append()` 追加、`toPlainText()` 取值；
- 仅展示多行只读文本可用 `QLabel`（设 `setWordWrap(True)`）。

## 可运行示例

- [示例 33：创建简单窗口](../examples/33-c561524202ef.md)：tooltip、图标、关闭、消息框、窗口居中（17 段代码）
- [示例 32：QLabel](../examples/32-0ac7994021b5.md)：字体、对齐、HTML 进阶用法
- [示例 31：布局管理](../examples/31-04a3d116bcb4.md)：绝对布局对比、嵌套布局、动态布局
- [示例 30：文本框类控件](../examples/30-b3654650e61e.md)：QLineEdit/QTextEdit

## 事实溯源

篇内事实 F-097 ~ F-108，见 [article-source](../references/article-source.md)。
