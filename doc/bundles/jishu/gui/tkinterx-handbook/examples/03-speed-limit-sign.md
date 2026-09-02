---
type: Example
title: "示例：用 CanvasMeta 模拟电子限速标志"
description: "手册 F-TXH-05 完整可运行示例：黄绿点阵背景 + 红色限速 90 圆环，综合 create_text/create_circle/create_square"
tags: [tkinter, tkinterx, gui, canvas, speed-limit, example, create_circle, create_square]
generated: { by: "blog-article-to-okf-wiki/trae", at: "2026-09-02T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T18:00:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: tkinterx-handbook-jianshu
    resource: /references/sources.md
---

# 示例：用 CanvasMeta 模拟电子限速标志

手册 F-TXH-05《tkinterx 模拟电子限速》给出的完整示例：在灰色画布上铺满黄绿色小正方形模拟电子屏点阵，中央用红色粗圆环与楷体"90"文字模拟限速标志。[^F-TXH-05]

## 完整代码

```python
from tkinter import Tk, Label, ttk
from tkinterx.graph.canvas import CanvasMeta

W, H = 1920, 1080
x, y = [900, 500]
fill = 'red'  # 限速标志的颜色
text = '90'  # 限速标志
spacing = 20 # 正方形边界
r = 420  # 圆环半径
root = Tk()
root.geometry(f'{W}x{H}')
self = CanvasMeta(root, bg='gray')
self.create_text([x, y], text=text, font='楷体 500', fill=fill)
self.create_circle([x, y], r, width=80, color='red')
row = int(W/spacing)
column = int(H/spacing)
for i in range(row):
    for j in range(column):
        self.create_square([i*spacing, j*spacing], spacing, width=2, color='yellowgreen')
self.grid(sticky='nesw')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.mainloop()
```

## 参数解读

| 参数 | 值 | 作用 |
|------|-----|------|
| `W, H` | 1920, 1080 | 窗口初始分辨率 |
| `x, y` | [900, 500] | 限速标志中心坐标 |
| `fill` / `text` | `'red'` / `'90'` | 数字文字颜色与限速数值 |
| `spacing` | 20 | 点阵小正方形边长与步长（像素） |
| `r` | 420 | 限速圆环半径 |

绘图顺序：

1. `create_text([x, y], text=text, font='楷体 500', fill=fill)` 先写中心数字（字号 500 的楷体）；
2. `create_circle([x, y], r, width=80, color='red')` 再画 80 像素粗的红色圆环；
3. 双重循环按 `spacing` 步长铺满 `yellowgreen` 小正方形作为电子屏点阵背景（`row = W/spacing = 96` 行、`column = H/spacing = 54` 列）；
4. `grid(sticky='nesw')` + 行列 `weight=1` 让画布随窗口缩放。

## 运行方式

将代码保存为 `speed_limit.py`，执行：

```bash
python speed_limit.py
```

运行效果：

![模拟电子限速 90 的运行效果：灰底黄绿点阵与红色圆环](../../../../../_static/bundles/jishu/gui/tkinterx-handbook/images/9fe81ca6c0f7-1114626-c09d9b2bf4cfa6d0.webp)

## 可调实验

- 修改 `text` 与 `fill` 可模拟不同限速值（如 `'120'`、`'blue'`）；
- 调小 `spacing`（如 10）点阵更密，调大则更稀疏；
- 把 `color='yellowgreen'` 换成 `color_dict` 中的其他颜色名（见[颜色工具与抠图工具](../concepts/06-tools-colors-matting.md)）可改变点阵配色。

## 延伸阅读

- [规则图形与批量阵列](../concepts/03-graph-shapes.md) 第 1、6 节 — create_point/create_circle/create_square 接口与本例详解
- [CanvasMeta：统一的 2D 画图接口](../concepts/02-canvas-meta.md)
- [快速上手：安装与第一个程序](01-getting-started.md)
- [《tkinterx 手册》信源登记](../references/sources.md)

[^F-TXH-05]: 简书《tkinterx 模拟电子限速》，见[信源登记](../references/sources.md)。