# 概念体系索引

本束概念按"入门概念 → 基础部件 → 布局 → 高级部件 → 应用骨架 → 交互细节 → 两大核心部件 → 架构与样式"递进：

| # | 概念文档 | 覆盖内容 |
|---|---------|---------|
| 1 | [tkinter 基础概念：Widgets、几何管理与事件处理](01-introduction.md) | 三大基本概念、Tk/ttk 关系、mainloop 事件循环 |
| 2 | [第一个窗口与基础主题化 Widgets](02-basic-widgets.md) | Tk 窗口骨架、Label/Entry/Button/Checkbutton/Radiobutton/Frame、validate 输入验证、invoke |
| 3 | [几何管理器：grid、pack、place 与嵌套布局](03-geometry-managers.md) | grid 行列配置/sticky/跨格、pack 停靠、place 精确定位、Frame 嵌套与布局重组 |
| 4 | [高级主题化 Widgets](04-advanced-widgets.md) | Combobox/Listbox/Scrollbar/Scale/Spinbox/Progressbar、Treeview 表格树、Notebook 选项卡、PanedWindow |
| 5 | [菜单、多窗口与标准对话框](05-menus-windows-dialogs.md) | 菜单栏/弹出菜单、Toplevel 多窗口、messagebox/filedialog/colorchooser、Tix 标准对话框 |
| 6 | [友好界面设计与 ToolTip 提示](06-friendly-ui-tooltips.md) | 界面设计原则、ToolTip 自定义实现、tix.Balloon 气泡提示、焦点与键盘友好 |
| 7 | [事件绑定与变量联动](07-events-and-variables.md) | bind 事件序列/回调参数、鼠标键盘事件、StringVar 等 variable 双向联动、trace 监听 |
| 8 | [Text 多行文本部件](08-text-widget.md) | 索引/tag/mark 体系、富文本与样式、嵌入窗口与图片、记事本式编辑 |
| 9 | [Canvas 画布与 2D 绘图](09-canvas.md) | 线/矩形/椭圆/多边形/文本/图片、tag 分组操作、鼠标绘图与拖拽、坐标变换 |
| 10 | [界面样式、MVC 架构与参考资源](10-styles-mvc-resources.md) | ttk.Style 主题化、MVC 三层组织 GUI 代码、图标/图片资源管理、官方学习资源 |

学习路径：**1 → 2 → 3**（能写出表单窗口）→ **4 → 5**（做出完整应用骨架）→ **6 → 7**（打磨交互）→ **8/9**（按文本编辑或绘图方向深入）→ **10**（架构与样式收口）。

```{toctree}
:maxdepth: 1

01-introduction
02-basic-widgets
03-geometry-managers
04-advanced-widgets
05-menus-windows-dialogs
06-friendly-ui-tooltips
07-events-and-variables
08-text-widget
09-canvas
10-styles-mvc-resources
```