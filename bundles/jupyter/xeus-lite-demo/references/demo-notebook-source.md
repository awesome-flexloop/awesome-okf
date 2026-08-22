---
type: Reference
title: 示例 Notebook 信源
description: content/demo.ipynb 内容登记，展示 xeus-python 内核和 ipycanvas 的基础用法
tags: [notebook, demo, ipycanvas, xeus-python, reference]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: demo-ipynb
    resource: https://github.com/jupyterlite/xeus-lite-demo/blob/main/content/demo.ipynb
    title: xeus-lite-demo content/demo.ipynb
---

## 源文件路径

`content/demo.ipynb`

## Cell 结构

### Cell 0

- **类型**: code
- **语言**: python
- **源码**:

```python
import this
```

执行后显示 Python 之禅（The Zen of Python），验证 Python 内核正常工作。

### Cell 1

- **类型**: code
- **语言**: python
- **源码**:

```python
from math import pi

from ipycanvas import Canvas

canvas = Canvas(width=1600, height=1200, layout=dict(width="100%"))

canvas.fill_style = "#8ee05e"
canvas.fill_rect(0, 0, canvas.width, canvas.height)

canvas.fill_style = "#f5f533"
canvas.fill_circle(canvas.width / 2.0, canvas.height / 2.0, 500)

canvas.stroke_style = "black"
canvas.line_width = 30
canvas.stroke_circle(canvas.width / 2.0, canvas.height / 2.0, 500)

canvas.fill_style = "black"
canvas.fill_circle(canvas.width / 2.7, canvas.height / 3.0, 100)  # Right eye
canvas.stroke_arc(canvas.width / 2.0, canvas.height / 2.0, 400, 0, pi, False)  # Mouth
canvas.stroke_arc(
    canvas.width - canvas.width / 2.7, canvas.height / 2.7, 100, 0, pi, True
)  # Left eye

canvas
```

## 绘制效果说明

此 Cell 使用 ipycanvas 绘制一个笑脸表情：

1. **绿色背景**：1600×1200 的矩形，颜色 #8ee05e
2. **黄色脸**：居中的圆形，半径500，颜色 #f5f533
3. **黑色描边**：脸的轮廓线，宽度30像素
4. **黑色右眼**：圆形，半径100，位于 (width/2.7, height/3.0)
5. **嘴巴**：下半圆弧，半径400，使用 stroke_arc 从0到pi（下半圆）
6. **黑色左眼**：弧形（闭合眼），半径100，从0到pi逆时针方向
7. **显示 canvas**：最后一行输出 canvas 对象，Jupyter 自动渲染为图像

## API 使用清单

| API | 来源 | 用途 |
|-----|------|------|
| `Canvas(width, height, layout)` | ipycanvas | 创建画布控件 |
| `canvas.fill_style` | ipycanvas | 设置填充颜色 |
| `canvas.fill_rect(x, y, w, h)` | ipycanvas | 填充矩形 |
| `canvas.fill_circle(x, y, r)` | ipycanvas | 填充圆形 |
| `canvas.stroke_style` | ipycanvas | 设置描边颜色 |
| `canvas.line_width` | ipycanvas | 设置线条宽度 |
| `canvas.stroke_circle(x, y, r)` | ipycanvas | 描边圆形 |
| `canvas.stroke_arc(x, y, r, start, end, anticlockwise)` | ipycanvas | 描边弧线 |
| `math.pi` | Python stdlib | 圆周率常量 |
