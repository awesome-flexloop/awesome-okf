---
type: Concept
title: PyQt5 架构、环境搭建与打包分发
description: PyQt5 作为 Qt5 的第三方 Python 绑定的定位；pip 安装、VSCode 开发环境、Qt Designer 可视化设计与 PyInstaller 打包 exe 的完整工作流
tags: [PyQt5, 架构, 环境搭建, Qt Designer, PyInstaller, 打包]
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

# PyQt5 架构、环境搭建与打包分发

## PyQt5 是什么

**PyQt5** 是 Riverbank Computing 出品的、对 Digia **Qt5** C++ 库的 Python 绑定（F-109）。它把 Qt 的全部模块（QtCore/QtGui/QtWidgets 等）暴露给 Python，让开发者用 Python 编写原生跨平台桌面 GUI。

- 许可证：**GPL v3 或 Riverbank 商业许可证双授权**，无 LGPL（闭源商用需购买授权）；
- 与官方绑定 PySide2 的 API 差异详见 qt-for-python 束《PySide2 与 PyQt5 差异》概念。

## 环境搭建（Windows + Anaconda/venv）

```bash
pip install pyqt5           # 运行库
pip install pyqt5-tools     # 附带 Qt Designer、pyuic5/pyrcc5 等工具
```

验证安装：

```python
from PyQt5.QtWidgets import QApplication, QLabel
import sys
app = QApplication(sys.argv)
QLabel("Hello PyQt5").show()
sys.exit(app.exec_())
```

## Qt Designer 可视化工作流

1. 启动 **Qt Designer**，新建窗口时选择模板：
   - **Main Window** → 代码中继承 `QMainWindow`（带菜单栏/状态栏/工具栏）；
   - **Dialog** → 继承 `QDialog`（对话框）；
   - **Widget** → 继承 `QWidget`（通用控件/嵌入式）。
2. 拖拽控件、设置属性，保存为 `xxx.ui`（XML）；
3. 转换为 Python：`pyuic5 xxx.ui -o ui_xxx.py`，业务代码中 `from ui_xxx import Ui_MainWindow` 并多继承组合；
4. 资源文件（图标/图片）用 `.qrc` 描述，`pyrcc5 xxx.qrc -o rc_xxx.py`。

> 推荐模式：**ui_*.py 只做界面、不手改**（重新生成会覆盖）；业务逻辑写在单独的子类里。

## 打包为 exe（PyInstaller）

```bash
pip install pyinstaller
pyinstaller -F -w -i app.ico main.py
# -F 单文件；-w 不显示控制台窗口；-i 指定图标
```

注意：`-w` 模式下 print 输出不可见，调试阶段先用控制台模式；`.qrc` 资源已被 pyrcc5 编入 .py，无需额外打包；数据文件用 `--add-data` 携带。

## 可运行示例

- [示例 34：架构简介](../examples/34-1c12f82e0fd1.md)：PyQt5/Qt 架构综述
- [示例 36：0.1 使用 vscode 从零开始学习 PyQt5](../examples/36-c37c5b1c9a5e.md)：安装、环境、.gitignore 模板（阅读 1.5w+）
- [示例 35：0.2 使用 vscode 借助 PyQt5 设计计算器](../examples/35-6118e29e3051.md)：Designer + 逻辑 + 打包全流程实战
- [示例 11：PyQt5 学习资源](../examples/11-9e3bde8b2df5.md)：官方文档与教程链接

## 事实溯源

F-109、F-111、F-112、F-122（官方文档核验），见 [article-source](../references/article-source.md)。
