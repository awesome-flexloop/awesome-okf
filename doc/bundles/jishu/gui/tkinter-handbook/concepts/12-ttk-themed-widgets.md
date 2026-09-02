---
type: Concept
title: "ttk 主题部件：18 种部件、标准选项与状态机制"
description: "tkinter.ttk 的行为/外观分离思想与不兼容点（fg/bg 等样式选项移至 ttk.Style）、18 种 ttk 部件清单（12 种已有 + Combobox/Notebook/Progressbar/Separator/Sizegrip/Treeview 6 种新增）、标准选项 class/cursor/takefocus/style、Label 选项 text/textvariable/underline/image/compound/width、九种状态标志与 identify/instate/state 方法"
tags: [tkinter, gui, ttk, themed-widgets, style, widget-states, combobox, notebook, treeview]
generated: { by: "blog-article-to-okf-wiki/trae", at: "2026-09-02T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T18:00:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: tkinter-handbook-jianshu
    resource: /references/sources.md
---

# ttk 主题部件：18 种部件、标准选项与状态机制

`tkinter.ttk` 模块提供对 Tk 8.5 中引入的 Tk 主题小部件集的访问。它的基本思想是：在可能的情况下，把实现小部件**行为**的代码与实现其**外观**的代码分开。直接好处是在各个平台上获得更贴近原生的外观；但替换小部件并不完全兼容——主要区别是 `'fg'`、`'bg'` 以及其他与样式相关的选项在 Ttk 小部件中**不再提供**，取而代之用 `ttk.Style` 类管理样式（Style 的 element/layout/configure 实战用法见[多窗口管理与跨窗口传值](10-windows.md)中 `EntryStyle.TEntry` 的例子）。[^F-THB-21]

## 18 种 ttk 部件

ttk 中有 18 种部件，其中 12 种已存在于经典 tkinter：`Button`、`Checkbutton`、`Entry`、`Frame`、`Label`、`LabelFrame`、`Menubutton`、`PanedWindow`、`Radiobutton`、`Scale`、`Scrollbar`、`Spinbox`；6 种是新增的：`Combobox`（下拉组合框）、`Notebook`（选项卡）、`Progressbar`（进度条）、`Separator`（分隔线）、`Sizegrip`（窗口大小拖放手柄）、`Treeview`（树/表视图）。它们全部是 `ttk.Widget` 的子类；`ttk.Widget` 定义了 Tk 主题部件支持的标准选项和方法，**不应被直接实例化**。[^F-THB-21]

## 标准选项

所有 ttk 小部件接受以下选项：[^F-THB-21]

| 选项 | 描述 |
| --- | --- |
| `class` | 指定窗口类。在查询选项数据库时使用该类、确定窗口默认绑定标签、选择控件默认布局和样式。**只读，只能在创建窗口时指定** |
| `cursor` | 鼠标光标；空字符串（默认）表示继承父控件光标 |
| `takefocus` | 键盘遍历（Tab）期间是否接受焦点：0 跳过、1 接收、空字符串由遍历脚本决定 |
| `style` | 指定自定义控件样式（如 `"EntryStyle.TEntry"`、`"Accent.TButton"`） |

**可滚动控件选项**：`xscrollcommand`（与水平滚动条通讯，通常设为滚动条的 `Scrollbar.set()` 方法，视图变化时滚动条随之更新）与 `yscrollcommand`（垂直方向同理）。

**Label 选项**（标签、按钮及其他按钮类小部件均支持）：

| 选项 | 描述 |
| --- | --- |
| `text` | 显示的文本字符串 |
| `textvariable` | 指定一个变量（如 `StringVar`），其值代替 `text` 显示 |
| `underline` | 要加下划线的字符索引（从 0 开始），用于助记符（Alt 快捷键）激活 |
| `image` | 显示的图像：列表首元素为默认图像名称，其余为 `Style.map()` 定义的 statespec/value 对，指定小部件处于特定状态时使用的图像；列表中所有图像应尺寸相同 |
| `compound` | 同时有文本和图像时两者的相对位置 |
| `width` | 大于零指定文本标签分配空间（字符宽度单位）；小于零指定最小宽度；零或未指定用自然宽度 |

`compound` 的有效值：`'text'`（只显示文本）、`'image'`（只显示图片）、`'top'/'bottom'/'left'/'right'`（图片分别位于文本的上/下/左/右）、`'none'`（默认：有图显示图，否则文本）。

> **宽度单位注意**：ttk 的文本类尺寸与经典 tkinter 一样以**文本单位**（默认字体中字符 "0" 的宽/高）度量，不是像素——这保证跨平台行为一致。

**兼容性选项**：`state` 可设置为 `'normal'` 或 `'disabled'` 控制 disabled 状态位；它是**只写**选项——设置会改变小部件状态，但查询请用 `Widget.state()` 方法，读取此选项不反映状态。

## 小部件状态机制

ttk 控件状态是独立状态标志的位图（bitmask），共 9 种标志：[^F-THB-21]

| Flag | 描述 |
| --- | --- |
| `active` | 鼠标光标在小部件上，按下鼠标按钮将引起动作 |
| `disabled` | 小部件在程序控制下被禁用 |
| `focus` | 小部件具有键盘焦点 |
| `pressed` | 小部件被按下 |
| `selected` | Checkbutton/Radiobutton 等的 "On"/"true"/"current" |
| `background` | Windows/Mac 的前后台窗口概念：后台窗口中的小部件置位，前台清除 |
| `readonly` | 小部件不应允许用户修改（如只读 Combobox/Entry） |
| `alternate` | 特定于小部件的备用显示格式 |
| `invalid` | 小部件的值无效（如 Entry 校验失败） |

**状态规范（statespec）** 是状态名称的序列，名称前可加 `!` 表示该位为 OFF。例如 `('pressed', '!disabled', 'active')` 表示"按下且未禁用且激活"。

三个状态相关方法：

- **`identify(x, y)`**：返回坐标 `(x, y)`（相对于小部件的像素坐标）处元素的名称；该点不在任何元素内则返回空字符串。用于样式调试与命中测试。
- **`instate(statespec, callback=None, *args, **kw)`**：测试小部件状态。未指定回调时：状态匹配 statespec 返回 `True`，否则 `False`；指定回调时：匹配则以 args 调用回调（常用于条件执行动作）。
- **`state(statespec=None)`**：修改或查询状态。指定 statespec 时按其设置状态，并返回一个新的 statespec 指示**哪些标志发生了变化**；不指定则返回当前启用的状态标志。statespec 通常是列表或元组。

```python
btn = ttk.Button(root, text="OK")
print(btn.state())                 # () —— 查询当前状态
btn.state(('disabled',))           # 禁用按钮
print(btn.instate(('disabled',)))  # True
btn.state(('!disabled',))          # 取消禁用
```

> 新增的 `Progressbar`、`Combobox` 等部件的实例方法与 Canvas 手绘进度条的区别见[画布交互综合示例](../examples/03-canvas-interactions.md)；跨窗口场景中 ttk 按钮与 Style 的组合用法见[多窗口管理与跨窗口传值](10-windows.md)。

[^F-THB-21]: 简书《tkinter.ttk.Widget 简介》（内容译自 Python 官方文档 tkinter.ttk），见[信源登记](../references/sources.md)。
