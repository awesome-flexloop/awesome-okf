---
type: Concept
title: Qt 资源系统（qrc/rcc）与 QML 声明式界面
description: .qrc 资源文件经 rcc 编译后以 :/ 前缀访问的机制，以及 QML 语言与 Qt Quick 声明式 UI 开发
tags: [qrc, rcc, 资源系统, QML, Qt Quick, 声明式UI]
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

# Qt 资源系统（qrc/rcc）与 QML 声明式界面

## Qt 资源系统

把图片、图标、翻译文件等资源**嵌入可执行文件**，避免部署时路径错乱：

1. 编写 `.qrc`（XML 格式）列出资源文件：
   ```xml
   <RCC>
     <qresource prefix="/images">
       <file>copy.png</file>
     </qresource>
   </RCC>
   ```
2. 用 **rcc** 工具编译进程序（Python 绑定为 `pyside2-rcc` / `pyrcc5`）；
3. 代码中用资源路径访问，前缀为 `:/` 或 `qrc:`：
   ```python
   icon = QIcon(":/images/copy.png")   # 等价 qrc:/images/copy.png
   ```

官方原文：".qrc file is an XML document that enumerates local files... It serves as input to rcc"（F-107）。

> Python 项目中也可绕过 rcc，在运行时注册资源目录；但文集推荐的标准做法仍是 rcc 生成 `rc_*.py` 后 `import`。

## QML 与 Qt Quick

**QML** 是一种声明式语言（declarative language），用层级化的对象结构 + 属性绑定描述界面；**Qt Quick** 是基于 QML 的 UI 框架（Qt Qml 模块提供引擎，Qt Quick 提供可视类型）。

```qml
import QtQuick 2.0
import QtQuick.Controls 2.0

Rectangle {
    width: 200; height: 100
    Button {
        text: "Click"
        anchors.centerIn: parent
        onClicked: console.log("hello")
    }
}
```

Python 侧加载 QML：

```python
from PySide2.QtWidgets import QApplication
from PySide2.QtQuickWidgets import QQuickWidget

app = QApplication([])
view = QQuickWidget()
view.setSource(QUrl.fromLocalFile("view.qml"))
view.show()
app.exec_()
```

## Widgets vs QML 如何选

| 维度 | Qt Widgets | QML / Qt Quick |
|------|-----------|----------------|
| 范式 | 命令式（代码构建控件树） | 声明式（描述"界面是什么"） |
| 强项 | 传统桌面表单、控件丰富、成熟稳定 | 动画流畅、触摸/移动端、自定义视觉 |
| 语言 | Python/C++ | QML + JavaScript，可与 Python 混合 |

## 可运行示例

- [示例 26：Qt 资源体系（qrc rcc）](../examples/26-81782dc6951e.md)
- [示例 06：QML 简单类型](../examples/06-5a74589ec4a8.md)
- [示例 07：QML 组件](../examples/07-880a2274fece.md)

## 事实溯源

F-107（资源系统）、QML/Qt Quick 关系核验见 [verification](../references/verification.md) 第 8、10 项。
