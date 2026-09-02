# 实战示例索引

本束共 **12** 篇可复现实战/示例文档，由文集 34 篇博文中的完整项目与代码片段聚类而成（登录窗口、画图工具、计算器、文本编辑器、Matplotlib 嵌入等），代码、截图与原文效果均保留，信源见各篇文首与 [信源登记](../references/sources.md)。

| # | 实战文档 | 内容 |
|---|---------|------|
| 1 | [登录/注册窗口](01-login-window.md) | grid 布局表单、Entry/Button 回调、页面切换思路 |
| 2 | [自定义画图工具](02-drawing-tool.md) | Canvas 鼠标绘图、颜色/粗细选择、菜单与清屏 |
| 3 | [图形操作案例（graph-tensor 像素建模）](03-graphics-ops.md) | 像素级图形生成、Canvas 批量绘制与坐标计算 |
| 4 | [标注工具的标签模板（teach.md 解析器）](04-annotation-template.md) | Markdown 模板解析、标签数据结构与界面生成 |
| 5 | [tkinter 小例子 18 则](05-mini-examples.md) | 窗口/部件/布局/事件的最小可运行片段集 |
| 6 | [tkinter Canvas 例子 6 则](06-canvas-examples.md) | 基本图元、tag 操作、事件命中测试 |
| 7 | [多功能文本编辑器（Notebook Editor）](07-text-editor.md) | Notebook 多标签页、Text 编辑、菜单与文件操作 |
| 8 | [鼠标选择图形颜色与形状](08-color-shape-selector.md) | colorchooser、Canvas 图元拾取与属性修改 |
| 9 | [极简复杂算式计算器](09-calculator.md) | 按钮网格、表达式求值、StringVar 显示联动 |
| 10 | [Canvas 动画、图元拖拽与 StringVar 传值](10-misc-animation-drag.md) | after 定时动画、鼠标拖拽图元、跨部件变量传值 |
| 11 | [tkinter 嵌入 Matplotlib 绘图](11-embed-matplotlib.md) | FigureCanvasTkAgg 后端嵌入、工具栏与事件 |
| 12 | [Canvas 图形透明度](12-canvas-transparency.md) | stipple 位图透明与 PIL 合成透明两种方案 |

建议顺序：**1 → 5**（跑通入门片段）→ **9/8/2**（交互项目）→ **6/10/12**（Canvas 深入）→ **7/4/11**（综合应用）。

```{toctree}
:maxdepth: 1

01-login-window
02-drawing-tool
03-graphics-ops
04-annotation-template
05-mini-examples
06-canvas-examples
07-text-editor
08-color-shape-selector
09-calculator
10-misc-animation-drag
11-embed-matplotlib
12-canvas-transparency
```