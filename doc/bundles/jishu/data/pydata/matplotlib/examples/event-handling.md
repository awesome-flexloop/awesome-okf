---
type: Example
title: Matplotlib 事件处理
description: 基于 2020 年前后教程的 matplotlib 事件处理实战：mpl_connect 事件回调、事件属性、可拖拽矩形、鼠标进出与对象拾取
tags: [matplotlib, event-handling, mpl_connect, picker, interactive, example]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-9048dc53e33a
    resource: /references/source-18.md
    title: 信源登记：Matplotlib 事件处理（F-162~F-169）
---

# Matplotlib 事件处理

本文基于 2020 年前后教程（简书《Matplotlib 事件处理》）。matplotlib 通过事件回调实现与图形的交互（如平移、缩放、拖拽、拾取）。事件处理 API 是「GUI 中立」的——它基于 GTK 模型（matplotlib 支持的第一个用户界面），但不需要针对 wxpython、tkinter、qt4、gtk、macosx 等不同界面工具包分别写代码（F-162）。

## 一、事件连接

要接收事件，需编写一个回调函数，然后通过画布（`FigureCanvasBase`）的 `mpl_connect()` 连接到事件管理器。示例：打印鼠标点击的位置与按钮（F-163）：

```python
import numpy as np
from matplotlib import pyplot as plt

fig, ax = plt.subplots()
ax.plot(np.random.rand(10))

def onclick(event):
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))

cid = fig.canvas.mpl_connect('button_press_event', onclick)
```

`mpl_connect()` 返回一个连接 id（整数）。断开回调时调用：

```python
fig.canvas.mpl_disconnect(cid)
```

注意：画布仅保留回调的弱引用。若回调是类实例的方法，须保留对该实例的引用，否则实例被垃圾回收后回调会消失（F-163）。

## 二、可连接的事件名

以下事件均可通过 `mpl_connect()` 连接（F-164）：

| 事件名 | 事件类 | 说明 |
|--------|--------|------|
| 'button_press_event' / 'button_release_event' | `MouseEvent` | 鼠标按下 / 释放 |
| 'motion_notify_event' | `MouseEvent` | 鼠标移动 |
| 'scroll_event' | `MouseEvent` | 鼠标滚轮 |
| 'key_press_event' / 'key_release_event' | `KeyEvent` | 按键按下 / 释放 |
| 'pick_event' | `PickEvent` | 画布中对象被选中 |
| 'draw_event' | `DrawEvent` | 画布重绘（屏幕更新前） |
| 'resize_event' | `ResizeEvent` | 画布尺寸变化 |
| 'close_event' | `CloseEvent` | 图形被关闭 |
| 'figure_enter_event' / 'figure_leave_event' | `LocationEvent` | 鼠标进入 / 离开图形 |
| 'axes_enter_event' / 'axes_leave_event' | `LocationEvent` | 鼠标进入 / 离开坐标区 |

## 三、事件属性

所有 matplotlib 事件继承自 `matplotlib.backend_bases.Event`，储存 `name`（事件名称）、`canvas`（生成事件的 FigureCanvas 实例）、`guiEvent`（触发 matplotlib 事件的 GUI 事件）三个属性（F-165）。

`KeyEvent` 与 `MouseEvent` 都派生自 `LocationEvent`，具有以下属性（F-166）：

| 属性 | 描述 |
|------|------|
| `x` / `y` | 位置，距画布左端 / 底端的像素 |
| `inaxes` | 鼠标经过的 `Axes` 实例（若经过轴域） |
| `xdata` / `ydata` | 鼠标坐标（数据坐标） |

`MouseEvent` 额外有 `button`（按下的按钮，`None`、`1`、`2`、`3`、`'up'`、`'down'`，其中 `'up'`、`'down'` 用于滚动事件）与 `key` 属性（F-166）。

## 四、练习：可拖拽的矩形

连接 'button_press_event'、'button_release_event'、'motion_notify_event' 三个事件，按下时用 `Rectangle.contains()` 检测命中，移动时更新矩形位置，释放时重置状态（F-167）：

```python
import numpy as np
import matplotlib.pyplot as plt

class DraggableRectangle:
    def __init__(self, rect):
        self.rect = rect
        self.press = None

    def connect(self):
        'connect to all the events we need'
        self.cidpress = self.rect.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.rect.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = self.rect.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)

    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        if event.inaxes != self.rect.axes:
            return
        contains, attrd = self.rect.contains(event)
        if not contains:
            return
        print('event contains', self.rect.xy)
        x0, y0 = self.rect.xy
        self.press = x0, y0, event.xdata, event.ydata

    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if self.press is None:
            return
        if event.inaxes != self.rect.axes:
            return
        x0, y0, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.rect.set_x(x0 + dx)
        self.rect.set_y(y0 + dy)
        self.rect.figure.canvas.draw()

    def on_release(self, event):
        'on release we reset the press data'
        self.press = None
        self.rect.figure.canvas.draw()

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.rect.figure.canvas.mpl_disconnect(self.cidpress)
        self.rect.figure.canvas.mpl_disconnect(self.cidrelease)
        self.rect.figure.canvas.mpl_disconnect(self.cidmotion)

fig = plt.figure()
ax = fig.add_subplot(111)
rects = ax.bar(range(10), 20 * np.random.rand(10))
drs = []
for rect in rects:
    dr = DraggableRectangle(rect)
    dr.connect()
    drs.append(dr)

plt.show()
```

## 五、鼠标进入和离开

连接图形 / 轴域的进入 / 离开事件，改变鼠标所在轴域与图形的背景颜色（F-168）：

```python
import matplotlib.pyplot as plt

def enter_axes(event):
    print('enter_axes', event.inaxes)
    event.inaxes.patch.set_facecolor('yellow')
    event.canvas.draw()

def leave_axes(event):
    print('leave_axes', event.inaxes)
    event.inaxes.patch.set_facecolor('white')
    event.canvas.draw()

def enter_figure(event):
    print('enter_figure', event.canvas.figure)
    event.canvas.figure.patch.set_facecolor('red')
    event.canvas.draw()

def leave_figure(event):
    print('leave_figure', event.canvas.figure)
    event.canvas.figure.patch.set_facecolor('grey')
    event.canvas.draw()

fig1 = plt.figure()
fig1.suptitle('mouse hover over figure or axes to trigger events')
ax1 = fig1.add_subplot(211)
ax2 = fig1.add_subplot(212)

fig1.canvas.mpl_connect('figure_enter_event', enter_figure)
fig1.canvas.mpl_connect('figure_leave_event', leave_figure)
fig1.canvas.mpl_connect('axes_enter_event', enter_axes)
fig1.canvas.mpl_connect('axes_leave_event', leave_axes)

plt.show()
```

## 六、对象拾取（picker）

通过设置 Artist 的 `picker` 属性启用对象拾取。`picker` 有多种含义（F-169）：

| 取值 | 含义 |
|------|------|
| `None` | 禁用选择（默认） |
| `True` | 启用选择，鼠标移到该 artist 上方时触发事件 |
| float | 解释为点的 epsilon 容差，数据在鼠标事件 epsilon 内则触发 |
| function | 用户函数，签名 `hit, props = picker(artist, mouseevent)`，用于测试是否命中 |

启用拾取后，连接到画布的 `pick_event` 即可获得回调。`PickEvent` 永远有两个属性：`mouseevent`（生成拾取事件的鼠标事件）与 `artist`（被拾取的 Artist）。`Line2D` 等 artist 还可附加元数据，如拾取容差内数据点的索引（`event.ind`）。示例（F-169）：

```python
import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title('click on points')

line, = ax.plot(np.random.rand(100), 'o', picker=5)  # 5 points tolerance

def onpick(event):
    thisline = event.artist
    xdata = thisline.get_xdata()
    ydata = thisline.get_ydata()
    ind = event.ind
    points = tuple(zip(xdata[ind], ydata[ind]))
    print('onpick points:', points)

fig.canvas.mpl_connect('pick_event', onpick)

plt.show()
```

## 现状

本文基于 2020 年前后的教程（对应 matplotlib 2.x 时代）。事件处理核心 API 在本教程写成后保持稳定：

- `mpl_connect()` / `mpl_disconnect()`、上表所列事件名、`LocationEvent`/`MouseEvent` 属性（`x`/`y`/`inaxes`/`xdata`/`ydata`/`button`）、`picker` 机制在现行 matplotlib 3.x 中仍然可用，本教程代码基本可直接运行。
- 原文列举的交互后端含 `qt4`；在现行 matplotlib 中 Qt 后端已演进为 Qt5/Qt6，Tk 等其他后端仍受支持。运行交互示例前请确认当前环境已配置交互式后端（如 `%matplotlib` / `plt.switch_backend`）。
- 实际运行时若出现 `DeprecationWarning` 或默认参数变化，以所安装 matplotlib 版本的官方文档为准。

## 相关概念

- /concepts/01-artist-hierarchy.md — Artist 体系与事件系统（`Event`/`PickEvent` 类族）
- /concepts/02-backend-system.md — 交互后端与 `FigureCanvasBase`
- /concepts/03-pyplot-state-machine.md — pyplot 状态机与 Figure/Axes 管理
- /examples/basic-plotting.md — 基础绑图（事件处理的绘图基础）
