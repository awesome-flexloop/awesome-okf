---
type: Concept
title: "事件序列、Event 对象与四级绑定"
description: "tkinter 事件说明符 <modifier-type-detail> 语法、鼠标/键盘/窗口事件速查、Event 对象属性表、bind/bind_class/bind_all 四级绑定与匹配顺序、WM_DELETE_WINDOW 协议与 destroy 事件捕获"
tags: [tkinter, gui, event, binding, callback, protocol, wm-delete-window]
generated: { by: "blog-article-to-okf-wiki/trae", at: "2026-09-02T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T18:00:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: tkinter-handbook-jianshu
    resource: /references/sources.md
---

# 事件序列、Event 对象与四级绑定

## 事件说明符语法

tkinter 使用 `<modifier-type-detail>` 序列描述事件，分为三个字段：[^F-THB-02]

- **type**：事件说明符中最重要的部分，指定要绑定的事件类型。可以是 `Button`、`Key` 之类的用户操作，也可以是 `Enter`、`Configure` 等窗口管理器事件。
- **modifier** 与 **detail**：提供附加信息，许多情况下可省略。

事件字符串有多种简写：匹配键盘键时可省去尖括号（空格和尖括号本身除外），直接按键名书写，例如 `a` 表示用户键入 "a"；注意 `1` 是键盘绑定（数字键 1），而 `<1>` 是鼠标按钮绑定。可打印字符大多可直接使用，例外是空格（`<space>`）和小于号（`<less>`）。[^F-THB-02]

## 常用事件速查

鼠标按钮约定：Button 1 是最左按钮，Button 2 是中键（如有），Button 3 是最右按钮。在微件上按下鼠标按钮时，tkinter 会自动"抓住"（grab）鼠标指针——即使指针移出当前微件，只要按住按钮，后续 Motion/Release 事件仍发送给该微件。指针当前位置（相对微件）由回调事件对象的 `x`、`y` 成员提供。`<Button-1>`、`<ButtonPress-1>` 与 `<1>` 三种写法等价。[^F-THB-02]

| 事件 | 描述 |
| --- | --- |
| `<B1-Motion>` | 按住鼠标 button 1 的同时移动鼠标（B2 中键、B3 右键同理） |
| `<ButtonRelease-1>` | Button 1 被释放 |
| `<Double-Button-1>` | 双击 Button 1 |
| `<Enter>` | 鼠标指针进入微件 |
| `<Leave>` | 鼠标指针离开微件 |
| `<FocusIn>` | 键盘焦点已移至此微件或其子级 |
| `<FocusOut>` | 键盘焦点从该微件移到另一个微件 |
| `<Return>` | 用户按下 Enter 键。几乎可绑定键盘上所有键：Cancel(Break)、BackSpace、Tab、Shift_L、Control_L、Alt_L、Pause、Caps_Lock、Escape、Prior(Page Up)、Next(Page Down)、End、Home、Left/Up/Right/Down、Print、Insert、Delete、F1–F12、Num_Lock、Scroll_Lock 等 |
| `<Key>` | 用户按下任意键；该键在事件对象的 **char** 成员中给出（特殊键为空字符串） |
| `a` | 用户键入 "a"（例外：空格 `<space>`、小于 `<less>`） |
| `<Shift-Up>` | 按住 Shift 同时按上箭头；`Alt`、`Shift`、`Control` 均可作前缀 |
| `<Configure>` | 微件改变大小（某些平台上还包括位置）；新尺寸在事件对象的 `width`、`height` 属性中 |

窗口与组件相关事件：[^F-THB-02]

| 事件 | 描述 |
| --- | --- |
| Activate | 组件由不可用变为可用时触发（针对 state 变值） |
| Deactivate | 组件由可用变为不可用时触发 |
| Configure | 组件大小发生变化时触发 |
| Destory | 组件销毁时触发 |
| FocusIn | 组件获取焦点时触发（对 Entry 和 Text 有效） |
| FocusOut | 组件失去焦点时触发 |
| Map | 组件由隐藏变为显示时触发 |
| UnMap | 组件由显示变为隐藏时触发 |
| Perproty | 窗口属性发生变化时触发 |

## Event 对象属性

| 属性 | 描述 |
| --- | --- |
| widget | 产生该事件的微件（有效的 tkinter 微件实例而非名字）；所有事件都会设置 |
| x, y | 当前鼠标位置（像素） |
| x_root, y_root | 当前鼠标位置相对屏幕左上角的坐标（像素） |
| char | 字符代码（仅键盘事件），字符串形式 |
| keysym | 键符号（仅键盘事件） |
| keycode | 键代码（仅键盘事件） |
| num | 按钮编号（仅鼠标按钮事件） |
| width, height | 微件的新尺寸（像素，仅 Configure 事件） |
| type | 事件类型 |

下例把 Canvas 的 `<Configure>` 绑定到 resize 回调，在窗口缩放时取得新尺寸：[^F-THB-02]

```python
from tkinter import *

class testApp3:
    def __init__(self, master):
        self.ma = master
        self.f = Frame(self.ma)
        self.f.pack(fill=BOTH, expand=YES)
        self.cv = Canvas(self.f, width=125, height=125, bg='red')
        self.cv.pack(fill=BOTH, expand=YES)
        self.b1 = Button(self.f, text='Hello', height=1, width=10,
                         padx=0, pady=1, command=self.howbig)
        self.b1.pack(side=BOTTOM, anchor=S, padx=4, pady=4)
        self.cv.bind('<Configure>', self.resize)

    def howbig(self):
        print(self.cv['width'], self.cv['height'])
        print(self.cvw, self.cvh)

    def resize(self, event):
        print('(%d, %d)' % (event.width, event.height))
        self.cvw, self.cvh = event.width - 4, event.height - 4

root = Tk()
app = testApp3(root)
root.mainloop()
```

## 四级绑定与匹配顺序

绑定可以在四个级别上创建：[^F-THB-02]

1. **微件实例**：使用 `bind`；
2. **微件所在的顶层窗口**（Toplevel 或 root）：同样使用 `bind`；
3. **微件类**：使用 `bind_class`（tkinter 自身用它提供标准绑定）；
4. **整个应用程序**：使用 `bind_all`（例如为 F1 键在应用任意位置提供帮助）。

同一事件存在多个/重叠绑定时：在每个级别上 tkinter 只选择"最匹配"的绑定——例如同时为 `<Key>` 和 `<Return>` 创建实例绑定，按 Enter 时只调用后者；但如果在顶层窗口上也绑定了 `<Return>`，则两个处理程序都会被调用。**调用顺序为：实例级别 → 顶层窗口级别 → 类级别（通常是标准绑定）→ 应用程序级别**。极端情况下单个事件最多可触发四个处理程序。

## 协议处理：WM_DELETE_WINDOW

除事件绑定外，tkinter 还支持协议处理程序（protocol handlers）——"协议"指应用程序与窗口管理器之间的交互。最常用的是 `WM_DELETE_WINDOW`，定义用户用窗口管理器显式关闭窗口（点关闭按钮）时的行为。用 `protocol` 方法安装处理程序（微件必须是 root 或 Toplevel）：[^F-THB-02]

```python
widget.protocol("WM_DELETE_WINDOW", handler)
```

安装自己的处理程序后，tkinter 不再自动关闭窗口：可以弹出消息框询问是否保存数据，或直接忽略请求。要在处理程序中关闭窗口，调用窗口的 `destroy` 方法：

```python
from tkinter import messagebox, Tk

def callback():
    if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
        root.destroy()

root = Tk()
root.protocol("WM_DELETE_WINDOW", callback)
root.mainloop()
```

注意：即使不在顶层窗口注册 `WM_DELETE_WINDOW` 处理程序，窗口本身仍会照常销毁；但自 Python 1.5.2 起 tkinter 不会销毁相应的微件实例层次结构，因此始终自己注册处理程序是好习惯：

```python
top = Toplevel(...)
# make sure widget instances are deleted
top.protocol("WM_DELETE_WINDOW", top.destroy)
```

[^F-THB-02]: 简书《tkinter 事件与绑定》（译介 effbot Tkinterbook "Events and Bindings"），见[信源登记](../references/sources.md)。
