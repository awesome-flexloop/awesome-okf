---
type: Example
title: 创意编程与物理模拟
description: 使用 p5.js 内核进行创意编程、使用 ipycanvas 实现 Canvas 动画、使用 pyb2d 进行物理引擎模拟
tags: [creative-coding, p5js, ipycanvas, pyb2d, animation, physics, game-of-life]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: notebook-catalog
    resource: /references/notebook-catalog.md
    title: 笔记本目录信源
---

## 概述

本文档演示 JupyterLite 中的创意编程能力：p5.js 内核的创意草图、ipycanvas 的 Canvas 动画、以及 pyb2d 物理引擎模拟。

## p5.js 创意编程

新建笔记本，选择 **p5.js** 内核。

### 第一个 p5 Sketch

定义变量：

```javascript
var n = 4;
var speed = 1;
```

setup() 函数创建画布：

```javascript
function setup() {
  createCanvas(innerWidth, innerHeight);
  rectMode(CENTER);
}
```

draw() 函数绘制动画：

```javascript
function draw() {
  background('#ddd');
  translate(innerWidth / 2, innerHeight / 2);
  for (let i = 0; i < n; i++) {
    push();
    rotate(frameCount * speed / 1000 * (i + 1));
    fill(i * 5, i * 100, i * 150);
    const s = 200 - i * 10;
    rect(0, 0, s, s);
    pop();
  }
}
```

渲染画布：

```javascript
%show
```

执行后看到旋转的彩色矩形动画。

### 实时调参

修改变量值后重新执行 `%show`，动画实时更新：

```javascript
speed = 3  // 加快旋转速度
n = 20     // 增加矩形数量
```

```javascript
%show
```

### 跟随鼠标的圆

```javascript
function setup() {
  createCanvas(400, 400);
}

function draw() {
  background(220);
  fill(255, 0, 0);
  ellipse(mouseX, mouseY, 50, 50);
}
```

```javascript
%show
```

## ipycanvas Canvas 绘图

ipycanvas 提供在 Python 中操作 Canvas 的能力，可以结合 numpy 实现高性能动画。选择 **Python (Pyodide)** 内核。

### 安装

```python
%pip install -q ipycanvas
```

### 康威生命游戏

这是 Demo 中 ipycanvas.ipynb 展示的经典示例：

```python
import asyncio
import numpy as np
from ipycanvas import RoughCanvas, hold_canvas
```

定义生命游戏迭代函数：

```python
def life_step(x):
    """康威生命游戏单步演化"""
    nbrs_count = sum(np.roll(np.roll(x, i, 0), j, 1)
                     for i in (-1, 0, 1) for j in (-1, 0, 1)
                     if (i != 0 or j != 0))
    return (nbrs_count == 3) | (x & (nbrs_count == 2))
```

定义绘制函数：

```python
def draw(x, canvas, color='black'):
    with hold_canvas(canvas):
        canvas.clear()
        canvas.fill_style = '#FFF0C9'
        canvas.rough_fill_style = 'solid'
        canvas.fill_rect(-10, -10, canvas.width + 10, canvas.height + 10)
        canvas.rough_fill_style = 'cross-hatch'
        canvas.fill_style = color
        canvas.stroke_style = color

        living_cells = np.where(x)
        rects_x = living_cells[1] * n_pixels
        rects_y = living_cells[0] * n_pixels
        canvas.fill_rects(rects_x, rects_y, n_pixels)
        canvas.stroke_rects(rects_x, rects_y, n_pixels)
```

初始化滑翔机枪图案：

```python
glider_gun = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
    [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
    [1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
]

x = np.zeros((50, 70), dtype=bool)
x[1:10, 1:37] = glider_gun
```

创建画布并运行动画：

```python
n_pixels = 15
canvas = RoughCanvas(width=x.shape[1]*n_pixels, height=x.shape[0]*n_pixels)
canvas.fill_style = '#FFF0C9'
canvas.rough_fill_style = 'solid'
canvas.fill_rect(0, 0, canvas.width, canvas.height)
canvas  # 显示画布
```

```python
draw(x, canvas, '#5770B3')

# 运行 300 代
for _ in range(300):
    x = life_step(x)
    draw(x, canvas, '#5770B3')
    await asyncio.sleep(0.1)
```

观看滑翔机枪发射滑翔机的经典生命游戏动画。

### ipycanvas 关键 API

| API | 用途 |
|-----|------|
| `Canvas(width, height)` | 基础画布 |
| `RoughCanvas(width, height)` | 手绘风格画布 |
| `hold_canvas(canvas)` | 批量绘制上下文管理器（减少重绘） |
| `fill_rect(x, y, w, h)` | 填充矩形 |
| `fill_rects(x_array, y_array, size)` | 批量填充矩形（高性能） |
| `fill_style`, `stroke_style` | 填充/描边颜色 |
| `rough_fill_style` | 手绘填充样式（solid/hachure/cross-hatch） |

## pyb2d 物理引擎

pyb2d 是 Box2D 物理引擎的 Python 绑定，在 Pyodide 中通过 `pyb2d-jupyterlite-backend` 包提供 Jupyter 异步 GUI 后端。Demo 的 `content/pyodide/pyb2d/` 目录包含多个物理模拟和游戏示例。

### 安装与初始化

pyb2d 示例使用 piplite 安装（注意：不是标准的 pip 包名）：

```python
import piplite
await piplite.install('pyb2d-jupyterlite-backend>=0.4.2')

from pyb2d_jupyterlite_backend.async_jupyter_gui import JupyterAsyncGui
import b2d  # pyb2d 以 b2d 名称导入
```

### 示例列表

| 笔记本 | 内容 |
|--------|------|
| 0_tutorial.ipynb | Box2D 基础教程（世界创建、刚体、关节、步进模拟） |
| color_mixing.ipynb | 颜色混合模拟 |
| gauss_machine.ipynb | 高斯机/统计物理演示 |
| newtons_cradle.ipynb | 牛顿摆模拟 |
| games/angry_shapes.ipynb | 愤怒的小鸟类弹射游戏 |
| games/billiard.ipynb | 台球碰撞模拟 |
| games/goo.ipynb | 粘粘世界类软物体游戏 |
| games/rocket.ipynb | 火箭发射模拟 |

### 基本使用模式

```python
# 1. 安装后端并导入
# 2. 创建物理世界（b2d.World）
# 3. 添加刚体和关节（world.create_body, world.create_joint）
# 4. 使用 JupyterAsyncGui 作为后端进行交互渲染
# 5. 在动画循环中 world.step() 推进物理模拟
```

## 相关概念

- [三大内核生态对比](/concepts/03-kernel-ecosystem.md)
- [Pyodide 生态库与 %pip 安装](/concepts/05-pyodide-libraries.md)
- [交互式控件实战](/examples/04-interactive-widgets.md)
- [自定义 Demo 站点实战](/examples/07-custom-demo-site.md)
