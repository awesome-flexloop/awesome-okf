---
type: Example
title: "布局管理器综合示例：Pack 三容器、Grid 计算器、Place 随机标签"
description: "三个可直接运行的布局练习程序：Pack 的 side/fill/expand 多 Frame 嵌套（含 fm2 不填充坑的修复对照）、Grid 行列排布 16 键计算器、Place 按像素坐标摆放随机色标签并用灰度公式自动选择前景色"
tags: [tkinter, gui, layout, pack, grid, place, calculator, frame]
generated: { by: "blog-article-to-okf-wiki/trae", at: "2026-09-02T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T18:00:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: tkinter-handbook-jianshu
    resource: /references/sources.md
---

# 布局管理器综合示例：Pack 三容器、Grid 计算器、Place 随机标签

本示例把[布局管理](../concepts/04-geometry-management.md)中的三个管理器各落为一个完整可运行程序，均保存为单个 `.py` 文件即可执行。[^F-THB-03]

## 示例 1：Pack 多容器布局

三个 Frame 演示 side/fill/expand 组合。**注意 fm2 的对比**：fm1、fm3 各自在 pack 时带了 `fill=BOTH, expand=YES`，所以子按钮的 fill 方向有效；fm2 若只写 `expand=YES` 不带 fill，自身不拉伸，内部按钮的 `fill=Y` 无从发挥（运行截图与机制解释见[布局管理](../concepts/04-geometry-management.md)）。

```python
from tkinter import *


class App:
    def __init__(self, master):
        self.master = master
        self.init_widgets()

    def init_widgets(self):
        # 第一个容器：放在最左，自身双向填充
        fm1 = Frame(self.master)
        fm1.pack(side=LEFT, fill=BOTH, expand=YES)
        # 按钮从顶部排列，水平方向填充
        Button(fm1, text='第一个').pack(side=TOP, fill=X, expand=YES)
        Button(fm1, text='第二个').pack(side=TOP, fill=X, expand=YES)
        Button(fm1, text='第三个').pack(side=TOP, fill=X, expand=YES)

        # 第二个容器：关键坑——必须 fill=BOTH，内部按钮才能垂直填充
        fm2 = Frame(self.master)
        fm2.pack(side=LEFT, padx=10, fill=BOTH, expand=YES)
        Button(fm2, text='第一个').pack(side=RIGHT, fill=Y, expand=YES)
        Button(fm2, text='第二个').pack(side=RIGHT, fill=Y, expand=YES)
        Button(fm2, text='第三个').pack(side=RIGHT, fill=Y, expand=YES)

        # 第三个容器：放在右边，自身双向填充
        fm3 = Frame(self.master)
        fm3.pack(side=RIGHT, padx=10, fill=BOTH, expand=YES)
        # 按钮从底部排列，垂直方向填充
        Button(fm3, text='第一个').pack(side=BOTTOM, fill=Y, expand=YES)
        Button(fm3, text='第二个').pack(side=BOTTOM, fill=Y, expand=YES)
        Button(fm3, text='第三个').pack(side=BOTTOM, fill=Y, expand=YES)


if __name__ == '__main__':
    root = Tk()
    root.title('Pack布局')
    App(root)
    root.mainloop()
```

**实验建议**：把 fm2 的 pack 改回 `fm2.pack(side=LEFT, padx=10, expand=YES)` 运行一次，观察 fm2 按钮不再随窗口拉伸——这是 Pack 最常见的"子组件 fill 无效"坑。

## 示例 2：Grid 计算器按键面板

Entry 用 pack 固定在顶部，16 个按键用 `row=i//4, column=i%4` 排入 Frame。多数规整界面 Grid 都比 Pack 直观——布局过程就是指定行列号，网格尺寸自动计算。

```python
from tkinter import *


class App:
    def __init__(self, master):
        self.master = master
        self.init_widgets()

    def init_widgets(self):
        # 输入框放顶部
        e = Entry(relief=SUNKEN, font=('Courier New', 24), width=25)
        e.pack(side=TOP, pady=10)
        p = Frame(self.master)
        p.pack(side=TOP)
        names = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                 '+', '-', '*', '/', '.', '=')
        for i in range(len(names)):
            b = Button(p, text=names[i], font=('Verdana', 20), width=6)
            b.grid(row=i // 4, column=i % 4)


if __name__ == '__main__':
    root = Tk()
    root.title("Grid布局")
    App(root)
    root.mainloop()
```

**延伸**：需要跨行/跨列时用 `columnspan`/`rowspan`；需要单元格内对齐方向时用 `sticky='nsew'`，并配合 `columnconfigure(index, weight=1)` / `rowconfigure(index, weight=1)` 让网格随窗口缩放（权重写法见[画布图片](../concepts/09-canvas-images.md)背景图示例）。

## 示例 3：Place 绝对坐标标签墙

Place 要求显式给出每个组件的位置。下例为 5 个标签随机生成背景色，用灰度公式 `0.299*R + 0.587*G + 0.114*B` 判断背景亮度，自动选白/黑前景色保证可读性，再用 `place(x=, y=, width=, height=)` 逐一定位：

```python
from tkinter import *
import random


class App:
    def __init__(self, master):
        self.master = master
        self.init_widgets()

    def init_widgets(self):
        books = ('Python 入门', 'Python 初级', 'Python 进阶',
                 'Python 高级', 'Python 核心')
        for i in range(len(books)):
            ct = [random.randrange(256) for _ in range(3)]
            grayness = int(round(0.299 * ct[0] + 0.587 * ct[1] + 0.114 * ct[2]))
            bg_color = "#%02x%02x%02x" % tuple(ct)
            lb = Label(root, text=books[i],
                       fg='White' if grayness < 125 else 'Black',
                       bg=bg_color)
            lb.place(x=20, y=36 + i * 36, width=180, height=30)


if __name__ == '__main__':
    root = Tk()
    root.title('Place 布局')
    # width x height + x_offset + y_offset
    root.geometry("250x250+30+30")
    App(root)
    root.mainloop()
```

**要点**：容器坐标系原点 (0, 0) 在左上角，X 轴向右、Y 轴向下；`relx/rely/relwidth/relheight` 提供以父容器为单位 1 的相对坐标（0.0–1.0），适合需要按比例摆放的场景；`bordermode="inside"/"outside"` 控制宽高是否计入边框。

[^F-THB-03]: 简书《tkinter 布局管理》，见[信源登记](../references/sources.md)。
