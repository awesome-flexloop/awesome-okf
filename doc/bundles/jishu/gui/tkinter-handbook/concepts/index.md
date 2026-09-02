# 概念文档

本目录包含 tkinter 手册知识包的 12 个概念文档，按学习路径排列：从 Tcl/Tk 关系与微件体系出发，经样式、布局、事件、变量调度等基础，再进入 Canvas 画布核心（参数、画图、图片、交互）与多窗口、ttk 主题部件等进阶主题。

## 基础篇

* [01-tkinter 入门：Tcl/Tk 关系、GUI 四任务与学习资源](01-introduction.md) — tkinter 是什么、Tcl/Tk 之上的薄面向对象层、GUI 四个基本编程任务、官方与社区资源。
* [02-微件体系与配置管理](02-widgets-and-configuration.md) — 完整微件清单、Misc/mixin 架构、cget/config/keys 配置三件套、name 路径标识。
* [03-样式：颜色、字体、边框与 tk_setPalette](03-styling.md) — 颜色名与 RGB 值、字体与文本格式化、relief 边框、全局配色方案。
* [04-布局管理：Pack、Grid 与 Place](04-geometry-management.md) — 三种几何管理器选项、多 Frame 嵌套坑、计算器 Grid 布局、Place 绝对/相对坐标。
* [05-事件与绑定](05-events-and-bindings.md) — 事件序列语法、Event 对象属性、四级绑定、WM_DELETE_WINDOW 协议。
* [06-变量追踪、对话框与事件循环调度](06-variables-dialogs-and-scheduling.md) — StringVar.trace 双向联动、Dialog 模态对话框、after/after_idle/update 调度、剪贴板。

## Canvas 画布篇

* [07-Canvas 核心机制：item handles、tags、选项与方法全集](07-canvas-core.md) — ID/tags 双标识、预定义 all/current、组件选项表、40+ 方法速查、highlightthickness 边框坑。
* [08-Canvas 画图函数分组：graph / image / text / window](08-canvas-shapes.md) — create_arc/line/oval/rectangle/polygon/bitmap/image/text/window、通用参数、stipple/dash/joinstyle。
* [09-画布图片：PhotoImage 格式限制、引用持有坑与背景图铺底](09-canvas-images.md) — PNG/GIF 与 PIL 补 JPG、mainloop 期间引用持有、anchor='nw' 铺底、付费试读边界声明。

## 进阶篇

* [10-多窗口管理：Toplevel、单子窗口与跨窗口传值](10-windows.md) — geometry 语法、Toplevel 多窗口、state() 探测单例、transient/wait_window 模态回传。
* [11-画布拖曳与缩放：scan、canvasx/canvasy、滚轮缩放与 dnd 拖放协议](11-canvas-interactions.md) — scan_mark/scan_dragto、MouseWheel/Button-4/5 事件、图片缩放三档方案、tkinter.dnd 七回调协议。
* [12-ttk 主题部件：18 种部件、标准选项与状态机制](12-ttk-themed-widgets.md) — 行为/外观分离、ttk.Style、Combobox/Notebook/Progressbar/Treeview 等 6 种新增部件、9 种状态标志与 identify/instate/state。

```{toctree}
:hidden:
:maxdepth: 7

01-introduction
02-widgets-and-configuration
03-styling
04-geometry-management
05-events-and-bindings
06-variables-dialogs-and-scheduling
07-canvas-core
08-canvas-shapes
09-canvas-images
10-windows
11-canvas-interactions
12-ttk-themed-widgets
```
