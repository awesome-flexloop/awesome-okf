# 实战示例

本目录包含 tkinter 手册知识包的 3 个综合示例文档，每个文档提供可直接保存运行的完整程序与逐步截图，对应概念文档中的 API 讲解。

* [01-快速上手：第一个窗口、Frame 容器与 Label/Button/Entry](01-getting-started.md) — Tk() 根窗口与 mainloop、geometry 语法、Frame 容器、Label 文本/颜色/图片（PhotoImage 引用持有坑）、文本单位宽高、Button 与 Entry；含 10 张逐步运行截图。
* [02-布局管理器综合示例：Pack 三容器、Grid 计算器、Place 随机标签](02-layout-managers.md) — side/fill/expand 多 Frame 嵌套与 fm2 不填充坑对照、16 键计算器 Grid 排布、place 绝对坐标标签墙与灰度前景色公式。
* [03-画布交互综合示例：Canvas 进度条、拖曳与滚轮缩放](03-canvas-interactions.md) — coords 重塑矩形进度条（sleep 阻塞版与 after 非阻塞改进版）、scan 拖曳、canvasx/canvasy 坐标转换、MouseWheel/Button-4/5 以鼠标为锚点缩放。

```{toctree}
:hidden:
:maxdepth: 7

01-getting-started
02-layout-managers
03-canvas-interactions
```
