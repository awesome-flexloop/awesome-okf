---
type: Example
title: "快速上手：安装 tkinterx 与第一个画图程序"
description: "从 pip 安装到运行第一个 CanvasMeta 程序：画直线、椭圆、矩形、弧与多边形，并调用 show_colors 查看颜色表"
tags: [tkinter, tkinterx, gui, getting-started, install, canvas, colors]
generated: { by: "blog-article-to-okf-wiki/trae", at: "2026-09-02T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T18:00:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: tkinterx-handbook-jianshu
    resource: /references/sources.md
---

# 快速上手：安装 tkinterx 与第一个画图程序

本示例带你从零安装 tkinterx 并跑通第一个画布程序，对应手册 F-TXH-01 与 F-TXH-02 的入门内容。[^F-TXH-01][^F-TXH-02]

## 环境要求

- Python >= 3.7（PyPI 元数据要求，见[信源登记](../references/sources.md)）
- 支持 Windows 7/10 与 Linux；tkinter 为 Python 标准库自带（Windows 官方安装包默认包含；部分 Linux 发行版需安装 `python3-tk`）
- tkinterx 最新版本 0.0.9（2020-05-30 发布）

## 第 1 步：安装

```bash
pip install tkinterx
```

安装成功后即可 `import tkinterx`。

## 第 2 步：第一个画图程序

将手册中的 `test_Meta` 保存为 `hello_tkinterx.py`：[^F-TXH-01]

```python
from tkinter import Tk
from tkinterx.graph.canvas import CanvasMeta

root = Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
self = CanvasMeta(root)
kw = {
    'color': 'purple',
    'dash': 2,
    'width': 3,
}
self.create_graph('line', [20, 20, 100, 200], **kw)
self.create_graph('oval', [50, 80, 100, 200], fill='red', **kw)
self.create_graph('rectangle', [170, 80, 220, 200], fill='yellow', **kw)
self.create_graph('arc', [180, 100, 250, 260],
                  tags='test',
                  fill='lightblue', style='chord', **kw)
self.create_graph('polygon', [(270, 80), (220, 170), (230, 90)], fill='blue', **kw)
self.create_graph('polygon', ((70, 80), (20, 70), (30, 90)), fill='purple', **kw)
self.grid(row=0, column=0)
print((self.gettags(1)))
print((self.find_withtag('test')))
root.mainloop()
```

运行：

```bash
python hello_tkinterx.py
```

预期结果：弹出一个窗口，紫色虚线轮廓的直线、红填充椭圆、黄填充矩形、浅蓝弦形弧以及两个多边形依次画出；终端打印 id=1 图元的标签与绑定 `'test'` 标签的图元 id。截图见 [CanvasMeta：统一的 2D 画图接口](../concepts/02-canvas-meta.md)图 1。

## 第 3 步：查看常用颜色表

挑选颜色时无需记忆颜色名，直接调用 tkinterx 内置的颜色表：[^F-TXH-02]

```python
from tkinterx.tools.colors import show_colors
show_colors()
```

运行后弹出常用颜色表单窗口，截图与 140 余条颜色字典见 [颜色工具与抠图工具](../concepts/06-tools-colors-matting.md)。

## 常见问题

- **`ModuleNotFoundError: No module named 'tkinterx'`**：确认安装所用 pip 与运行所用 Python 为同一环境（`python -m pip install tkinterx`）。
- **Linux 下提示没有 tkinter**：安装系统包，如 Ubuntu/Debian 执行 `sudo apt install python3-tk`。
- **接口与本文不一致**：tkinterx 为 Pre-Alpha 早期项目，本知识包对应 2020 年 4-5 月博文的接口形态；若安装版本不同，以 GitHub 仓库 xinetzone/pychaos 源码为准（地址见[信源登记](../references/sources.md)）。

## 延伸阅读

- [CanvasMeta：统一的 2D 画图接口](../concepts/02-canvas-meta.md)
- [规则图形与批量阵列](../concepts/03-graph-shapes.md)
- [颜色工具与抠图工具](../concepts/06-tools-colors-matting.md)
- [《tkinterx 手册》信源登记](../references/sources.md)

[^F-TXH-01]: 简书《tkinter 的拓展包：tkinterx》，见[信源登记](../references/sources.md)。
[^F-TXH-02]: 简书《tkinter 界面常用颜色表单》，见[信源登记](../references/sources.md)。