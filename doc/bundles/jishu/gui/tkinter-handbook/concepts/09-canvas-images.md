---
type: Concept
title: "画布图片：PhotoImage 格式限制、引用持有坑与背景图铺底"
description: "tkinter.PhotoImage 仅支持 PGM/PPM/GIF/PNG（JPG 需 PIL.ImageTk.PhotoImage）、mainloop 期间必须持有 PhotoImage 引用否则被垃圾回收导致图片不显示（实例属性持有解法）、create_image(anchor='nw') 铺背景图与 grid weight 随窗口缩放"
tags: [tkinter, gui, canvas, photoimage, pil, pillow, background-image, garbage-collection]
generated: { by: "blog-article-to-okf-wiki/trae", at: "2026-09-02T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T18:00:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: tkinter-handbook-jianshu
    resource: /references/sources.md
---

# 画布图片：PhotoImage 格式限制、引用持有坑与背景图铺底

## 坑一：PhotoImage 支持的图片格式很少

`tkinter.PhotoImage` 仅支持 **PGM、PPM、GIF、PNG** 四种格式；要在 Canvas（或 Label）上显示 JPG 等其他格式，需使用 PIL/Pillow 的 `PIL.ImageTk.PhotoImage` 载入：[^F-THB-07]

```python
from tkinter import Tk, Canvas
from PIL import ImageTk

name = 'images/car.jpg'
window = Tk()
canvas = Canvas(window, bg='pink')
img = ImageTk.PhotoImage(file=name)
canvas.create_image(120, 120, image=img)
canvas.pack()
window.mainloop()
```

## 坑二：PhotoImage 必须在 mainloop 期间持有引用

把创建 `ImageTk.PhotoImage` 的代码放进函数中，会出现"图片不显示"的现象：[^F-THB-07]

```python
def set_image(canvas, name):
    img = ImageTk.PhotoImage(file=name)
    canvas.create_image(300, 300, image=img)
    return img
```

原因是 `set_image(canvas, name)` 调用结束返回后，局部变量 `img` 立刻被垃圾回收，Tk 侧图片数据随之释放。**所有 PhotoImage 在 mainloop 期间必须有引用指向它们**：可以把 img 定义为全局变量，也可以把函数返回的 img 保存起来。更简单的办法是直接挂实例引用：

```python
def set_image(canvas, name):
    canvas.img = ImageTk.PhotoImage(file=name)   # 直接添加实例引用
    x = canvas.create_image(300, 300, image=canvas.img)
```

Label 载入图片同理（`Label(root, image=image)` 中的 image 也需持有），见[入门综合示例](../examples/01-getting-started.md)。

## 背景图铺底与随窗口缩放

付费文章《Python 设置 Canvas 背景图片且支持全屏显示》[^F-THB-12]的免费试读部分，给出了用实例变量显式持有 PhotoImage 的封装写法，并以 `create_image(..., anchor='nw')` 把图片从画布左上角铺底，配合 grid 的 `columnconfigure/rowconfigure(weight=1)` 让画布随窗口拉伸：

```python
from tkinter import Tk, Canvas
from PIL import ImageTk

class CanvasMeta(Canvas):
    def __init__(self, master, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.photo = None          # 显式引用 PhotoImage，防止被销毁

    def set_photo(self, photo):
        '''设置背景图'''
        # 使用实例变量引用避免 PhotoImage 被销毁
        self.photo = ImageTk.PhotoImage(file=photo)
```

绑定鼠标事件可查看画布坐标：

```python
class Graph(CanvasMeta):
    def __init__(self, master, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.bind('<1>', self.print_xy)

    def print_xy(self, event):
        print(event.x, event.y)
```

铺背景图并让画布跟随窗口缩放：

```python
def run(name):
    root = Tk()
    self = Graph(root, bg='pink')
    self.set_photo(name)
    self.create_image(0, 0, image=self.photo, anchor='nw')
    self.grid(sticky='nsew')
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()

if __name__ == "__main__":
    name = 'images/car.jpg'
    run(name)
```

要点：`anchor='nw'` 使图片左上角对齐画布原点 `(0, 0)`（默认 anchor='center' 会把图片中心放在该点）；`grid(sticky='nsew')` + 行列 weight=1 使画布占满并跟随窗口大小变化。

![全屏显示图片的目标效果](../../../../../_static/bundles/jishu/gui/tkinter-handbook/images/2e20fd55375b-1114626-b77ea99563ac683f.webp)

![初设背景图：图片以 nw 锚点铺在粉色画布上](../../../../../_static/bundles/jishu/gui/tkinter-handbook/images/2e20fd55375b-1114626-6208108088c3feef.webp)

> **试读边界声明**：F-THB-12 为简书付费文章（定价 1000 简书币），本次抓取仅获免费试读部分。原文止于"下面我们添加图片全屏显示，随着窗口大小的改变而变"一句，**图片随窗口缩放而缩放（重绘/重采样）的实现代码不在试读范围内**，本知识包不臆造该部分；需要图片级缩放可参考[画布拖曳与缩放](11-canvas-interactions.md)中基于 PIL 重采样的 tile 重绘方案。

[^F-THB-07]: 简书《tkinter 中 Canvas 创建图片的坑》，见[信源登记](../references/sources.md)。
[^F-THB-12]: 简书《Python 设置 Canvas 背景图片且支持全屏显示》（付费文章，仅获免费试读），见[信源登记](../references/sources.md)。
