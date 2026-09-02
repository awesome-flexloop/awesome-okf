---
type: Example
title: 实战杂例：Canvas 动画、图元拖拽与 StringVar 传值
description: 三个无图杂例：①100 个随机游走彩色点的动画（每点独立 tag、Canvas.move 按 tag 平移、threading+Queue 承载动作、after 自递归驱动帧循环、daemon 线程、Queue.get(False) 非阻塞取动作）；②Canvas 图元拖拽（tag_bind 绑 token 类图元、_drag_data 记录被拖项与上次坐标、find_closest 命中检测、B1-Motion 按 delta 增量 move）；③两个 StringVar 间传值（write_var trace w 回调把 Entry 内容拷给 read_var 驱动 Label，按钮读取打印）
tags: [tkinter, Canvas, 动画, after, threading, Queue, Canvas.move, tag_bind, find_closest, 拖拽, StringVar, trace, 实战集]
generated: { by: "blog-article-to-okf-wiki", at: "2026-09-03T00:50:00+08:00" }
verified: { by: "process:bundle-self-check", at: "2026-09-03T00:50:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: F-TGD-32
    resource: /references/sources.md
    title: 简书《tkinter 的几个例子》
  - id: F-TGD-31
    resource: /references/sources.md
    title: 简书《tkinter 的 不同 StringVar 之间传递值》
---

# 实战杂例：Canvas 动画、图元拖拽与 StringVar 传值

> 对应信源：F-TGD-32《tkinter 的几个例子》（例 1 动画、例 2 拖拽，改自社区代码）与 F-TGD-31《不同 StringVar 之间传递值》。本篇无截图，均为可直接运行的代码模式。

## 1 动画：100 个随机游走的彩色点（F-TGD-32 例 1）

每个 `Point` 在画布上是一个退化椭圆（点），带两个 tag：专属 tag `runner<id>` 与公共 tag `runner`。动画驱动采用**生产者-消费者**：后台 daemon 线程每 0.25s 从 `Queue` 非阻塞取一个动作执行；动作本身用 `window.after(150, random_movement)` 自递归注册下一帧，所有点按随机 delta 调 `Canvas.move(tag, dx, dy)` 平移：

```python
from tkinter import Canvas, mainloop, Tk
import numpy as np
import random
import traceback
import threading
import time
from queue import Queue

class Point:
    def __init__(self, the_canvas, uID):
        self.uID = uID
        self.location = np.ones((2)) * 200
        self.color = "#" + "".join(
            [random.choice('0123456789ABCDEF') for j in range(6)])
        self.the_canvas = the_canvas
        the_canvas.create_oval(
            200, 200, 200, 200, fill=self.color, outline=self.color,
            width=6, tags=('runner' + str(uID), 'runner'))

    def move(self):
        delta = (np.random.random((2)) - .5) * 20
        self.the_canvas.move('runner' + str(self.uID), delta[0], delta[1])

def queue_func():
    while True:
        time.sleep(.25)
        try:
            next_action = the_queue.get(False)   # 非阻塞取动作
            next_action()
        except Exception:
            print(traceback.format_exc())

the_queue = Queue()
the_thread = threading.Thread(target=queue_func)
the_thread.daemon = True                        # 主线程退出时自动结束
the_thread.start()

window = Tk()
window.geometry('400x400')
the_canvas = Canvas(window, width=400, height=400, background='black')
the_canvas.grid(row=0, column=0)

points = {i: Point(the_canvas, i) for i in range(100)}

def random_movement():
    for point in points.values():
        point.move()
    window.after(150, random_movement)          # 自递归注册下一帧

the_queue.put(random_movement)
mainloop()
```

要点：

- **动画帧循环**：tkinter 主线程内用 `after(ms, cb)` 链式自递归是标准做法，绝不能在主线程里 `time.sleep` 阻塞 UI；
- **跨线程更新 UI**：本例把"动作"放进 Queue、由消费线程取出执行——更稳妥的现代写法是让后台线程只 `queue.put`，主线程用 `after` 轮询队列并在主线程执行画布操作（Tk 非线程安全，跨线程直接调控件可能随机崩溃）；
- **tag 即批量句柄**：按 `runner<id>` 移动单个点、按 `runner` 可一次性操作全部点。

## 2 拖拽：Canvas 图元拖动（F-TGD-32 例 2）

拖拽三件套：按下时 `<ButtonPress-1>` 用 `find_closest(x, y)` 命中最上层图元并记录起点；拖动时 `<B1-Motion>` 计算鼠标位移 delta，`canvas.move(item, dx, dy)` 增量平移并刷新记录；释放时 `<ButtonRelease-1>` 清空拖拽状态。三个事件都绑在 `"token"` tag 上，所有带该 tag 的图元自动可拖：

```python
import tkinter as tk

TOKENWIDTH = 10

class Example(tk.Frame):
    '''Illustrate how to drag items on a Tkinter canvas'''

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(width=400, height=400, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self._drag_data = {"x": 0, "y": 0, "item": None}
        self._create_token((100, 100), "red")
        self._create_token((200, 100), "black")
        self.canvas.tag_bind("token", "<ButtonPress-1>", self.on_token_press)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self.on_token_release)
        self.canvas.tag_bind("token", "<B1-Motion>", self.on_token_motion)

    def _create_token(self, coord, color):
        (x, y) = coord
        self.canvas.create_oval(x-25, y-25, x+25, y+25,
                                outline="blue", fill=color,
                                tags="token", width=TOKENWIDTH)

    def on_token_press(self, event):
        '''开始拖拽：记录被拖项与起点'''
        self._drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self.canvas.update_idletasks()

    def on_token_release(self, event):
        '''结束拖拽：清空状态'''
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0
        self.canvas.update_idletasks()

    def on_token_motion(self, event):
        '''拖拽中：按鼠标位移增量移动图元'''
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        self.canvas.move(self._drag_data["item"], delta_x, delta_y)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self.canvas.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    Example(root).pack(fill="both", expand=True)
    root.mainloop()
```

要点：拖拽用**增量 move**（本次坐标 − 上次坐标）而非绝对坐标，图元不会跳变；`find_closest` 返回 id 元组取 `[0]`；`update_idletasks` 强制即时刷新，避免拖动残影。

## 3 两个 StringVar 之间传值（F-TGD-31）

`write_var` 绑定 Entry，`trace("w", callbackW)` 在其每次被写入时把值拷给 `read_var`；Label 绑定 `read_var` 自动刷新——变量链路 `Entry → write_var →(trace)→ read_var → Label`，按钮只负责读取打印：

```python
from tkinter import Tk, StringVar, ttk

class App(Tk):
    def __init__(self):
        super().__init__()
        self.read_var = StringVar()
        self.write_var = StringVar()
        entry = ttk.Entry(self, textvariable=self.write_var)
        entry.pack(pady=5, padx=10)
        self.write_var.trace("w", self.callbackW)

        lab = ttk.Label(self, textvariable=self.read_var)
        self.read_var.set("输入显示")
        lab.pack(pady=5, padx=10)

        ttk.Button(self, text="读取", command=self.hit).pack(pady=5)

    def callbackW(self, *args):
        self.read_var.set(self.write_var.get())

    def hit(self):
        print("读取数据:", self.read_var.get())

root = App()
root.mainloop()
```

要点：`trace("w", cb)` 是 tkinter 变量联动的核心机制——回调签名 `(*args)`，由 Tk 传入内部参数；多级变量串联可实现"写一处、显多处"的单向数据流。更多联动模式见 [事件绑定与变量联动](../concepts/07-events-and-variables.md)。

## 4 要点回顾

- **动画**：`after` 链驱动帧循环；后台线程只放任务、主线程执行 UI 更新；daemon 线程随主程序退出。
- **拖拽**：press 记项记坐标 → motion 增量 move 并刷新坐标 → release 清状态；绑 tag 而非绑单个 id。
- **变量传值**：StringVar + trace 构成单向数据流，控件只绑定变量、不互相直接读写。

> 相关概念：[Canvas 画布](../concepts/09-canvas.md)、[事件绑定与变量联动](../concepts/07-events-and-variables.md)。相关实战：[Canvas 例子集](06-canvas-examples.md)、[图形操作案例](03-graphics-ops.md)。