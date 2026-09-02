---
type: Example
title: Matplotlib 形状与路径（patches 与 path）
description: 基于 2020 年前后教程的 matplotlib 特殊图形绘制：patches 形状、PatchCollection 集合、Path 路径与 codes 顶点编码
tags: [matplotlib, patches, path, pathpatch, patchcollection, example]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-d52132ab9ccc
    resource: /references/source-19.md
    title: 信源登记：matplotlib 之形状与路径 patches 和 path（F-184~F-191）
---

# Matplotlib 形状与路径（patches 与 path）

本文基于 2020 年前后教程（简书《matplotlib 之形状与路径：patches和path》）。除常见线形图、条形图、扇形图外，matplotlib 还支持绘制特殊形状与路径：

- **形状（shape）**：指 `matplotlib.patches` 包中的对象（如箭头、正方形、椭圆），也称「块」（F-184）。
- **路径（path）**：一系列可能断开、可能已关闭的线和曲线段，指 `matplotlib.path` 中实现的功能（F-184）。

## 一、绘制形状的三步走

绘制任何 patch 都遵循「三步走」：①创建画图对象与子图；②创建对应的形状对象；③将形状添加到 Axes 中（核心步骤）。

第一步创建画布与子图：

```python
import numpy as np
from matplotlib import patches
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(211, aspect='auto')
```

第二步创建椭圆。`patches.Ellipse((xcenter, ycenter), width, height, angle=angle, linewidth=2, fill=False, zorder=2)`（F-185）：

```python
xcenter, ycenter = 1, 1
width, height = 0.8, 0.5
angle = -30  # 椭圆的旋转角度
ax.set_xbound(-1, 3)
ax.set_ybound(-1, 3)

e1 = patches.Ellipse((xcenter, ycenter), width, height,
                     angle=angle, linewidth=2, fill=False, zorder=2)
```

`patches.Arc` 与 `Ellipse` 等价，因为 `Arc` 继承自 `Ellipse` 类（F-185）。

第三步将形状加入图中。单个 patch 用 `ax.add_patch(e1)`；多个 patch 可先放入集合，再用 `PatchCollection(patches)` 构造集合后 `ax.add_collection(collection)`（F-187）：

```python
from matplotlib.collections import PatchCollection

e2 = patches.Arc((2, 2), width=3, height=2,
                 angle=angle, linewidth=2, fill=False, zorder=2)

patches_list = []
patches_list.append(e1)
patches_list.append(e2)

collection = PatchCollection(patches_list)
ax.add_collection(collection)

plt.show()
```

## 二、画出不同形状

`plt` 只实现了 `Rectangle`、`Circle`、`Polygon` 三个常用图形（可用 `plt.xxx()` 创建）；更复杂的图形使用 `patches` 模块（F-186）。以下示例在 3x3 网格中绘制多种形状与 `Line2D`（F-188）：

```python
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.path as mpath
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection

def label(xy, text):
    '''给每个 patch 设置标签说明'''
    y = xy[1] - 0.15
    plt.text(xy[0], y, text, ha="center", family='sans-serif', size=14)

fig, ax = plt.subplots()
grid = np.mgrid[0.2:0.8:3j, 0.2:0.8:3j].reshape(2, -1).T

patches = []
circle = mpatches.Circle(grid[0], 0.1, ec="none")
patches.append(circle)
label(grid[0], "Circle")

rect = mpatches.Rectangle(grid[1] - [0.025, 0.05], 0.05, 0.1, ec="none")
patches.append(rect)
label(grid[1], "Rectangle")

wedge = mpatches.Wedge(grid[2], 0.1, 30, 270, ec="none")
patches.append(wedge)
label(grid[2], "Wedge")

polygon = mpatches.RegularPolygon(grid[3], 5, 0.1)
patches.append(polygon)
label(grid[3], "Polygon")

ellipse = mpatches.Ellipse(grid[4], 0.2, 0.1)
patches.append(ellipse)
label(grid[4], "Ellipse")

arrow = mpatches.Arrow(grid[5, 0] - 0.05, grid[5, 1] - 0.05, 0.1, 0.1, width=0.1)
patches.append(arrow)
label(grid[5], "Arrow")

Path = mpath.Path
path_data = [
    (Path.MOVETO, [0.018, -0.11]),
    (Path.CURVE4, [-0.031, -0.051]),
    (Path.CURVE4, [-0.115, 0.073]),
    (Path.CURVE4, [-0.03, 0.073]),
    (Path.LINETO, [-0.011, 0.039]),
    (Path.CURVE4, [0.043, 0.121]),
    (Path.CURVE4, [0.075, -0.005]),
    (Path.CURVE4, [0.035, -0.027]),
    (Path.CLOSEPOLY, [0.018, -0.11])]
codes, verts = zip(*path_data)
path = mpath.Path(verts + grid[6], codes)
patch = mpatches.PathPatch(path)
patches.append(patch)
label(grid[6], "PathPatch")

fancybox = mpatches.FancyBboxPatch(
    grid[7] - [0.025, 0.05], 0.05, 0.1,
    boxstyle=mpatches.BoxStyle("Round", pad=0.02))
patches.append(fancybox)
label(grid[7], "FancyBboxPatch")

x, y = np.array([[-0.06, 0.0, 0.1], [0.05, -0.05, 0.05]])
line = mlines.Line2D(x + grid[8, 0], y + grid[8, 1], lw=5., alpha=0.3)
label(grid[8], "Line2D")

colors = np.linspace(0, 1, len(patches))
collection = PatchCollection(patches, cmap=plt.cm.hsv, alpha=0.3)
collection.set_array(np.array(colors))
ax.add_collection(collection)
ax.add_line(line)

plt.axis('equal')
plt.axis('off')
plt.tight_layout()
plt.show()
```

## 三、Path 路径：顶点与编码

路径绘制与普通 patch 大致相同，核心在于用 `Path(verts, codes)` 创建路径对象，再包装成 `PathPatch` 加入图中（F-189）。

以矩形路径为例，顶点按逆时针给出，并用 codes 指明连接方式：

```python
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

verts = [
    (0., 0.),  # 矩形左下角的坐标 (left, bottom)
    (0., 1.),  # 矩形左上角的坐标 (left, top)
    (1., 1.),  # 矩形右上角的坐标 (right, top)
    (1., 0.),  # 矩形右下角的坐标 (right, bottom)
    (0., 0.)]  # 封闭到起点

codes = [Path.MOVETO,
         Path.LINETO,
         Path.LINETO,
         Path.LINETO,
         Path.CLOSEPOLY]

path = Path(verts, codes)          # 创建一个 path 路径对象
fig = plt.figure()
ax = fig.add_subplot(111)
patch = patches.PathPatch(path, facecolor='orange', lw=2)  # 路径通过 PathPatch 实现
ax.add_patch(patch)
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
plt.show()
```

`Path` 类定义如下，需要传递两个必要参数（F-190）：

```python
class Path(vertices, codes=None, _interpolation_steps=1, closed=False, readonly=False)
```

`vertices` 是路径经过的关键点坐标序列；`codes` 指明点与点之间的连接方式。codes 取值含义（F-190）：

| codes | 含义 |
|-------|------|
| `MOVETO` | 拿起钢笔，移动到给定顶点（一般指「起始点」） |
| `LINETO` | 从当前位置绘制直线到给定顶点 |
| `CURVE3` | 用给定控制点绘制二次贝塞尔曲线到给定端点 |
| `CURVE4` | 用给定控制点绘制三次贝塞尔曲线到给定端点 |
| `CLOSEPOLY` | 绘制线段到当前折线的起始点 |
| `STOP` | 整个路径末尾的标记（当前不需要且被忽略） |

创建 `vertices` 和 `codes` 时，每个顶点与每个 codes 一一对应。

## 四、用 Path 绘制心形与条形统计图

### 心形路径

`(code, 顶点)` 成对给出，用 `zip(*path_data)` 拆成 codes 与 verts（F-189 同款手法）：

```python
path_data = [
    (Path.MOVETO, [0.018, -0.11]),   # 起点
    (Path.CURVE4, [-0.031, -0.051]),
    (Path.CURVE4, [-0.115, 0.073]),
    (Path.CURVE4, [-0.03, 0.073]),
    (Path.LINETO, [-0.011, 0.039]),
    (Path.CURVE4, [0.043, 0.121]),
    (Path.CURVE4, [0.075, -0.005]),
    (Path.CURVE4, [0.035, -0.027]),
    (Path.CLOSEPOLY, [0.018, -0.11])]  # 闭合到起点

codes, verts = zip(*path_data)
heartpath = Path(verts, codes)
patch = mpatches.PathPatch(heartpath)
ax.add_patch(patch)
```

### 条形图路径

`hist`、`bar` 等高层绘图函数本质也是通过路径实现。用 `np.random.seed(19680801)` 固定随机数种子、`np.histogram(data, 100)` 计算直方图，再构造每个条形四角的顶点（F-191）：

```python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path

fig = plt.figure()
ax = fig.add_subplot(111)
np.random.seed(19680801)               # 固定随机数种子
data = np.random.randn(1000)
n, bins = np.histogram(data, 100)

left = np.array(bins[:-1])
right = np.array(bins[1:])
bottom = np.zeros(len(left))
top = bottom + n
nrects = len(left)

nverts = nrects * (1 + 3 + 1)
verts = np.zeros((nverts, 2))
codes = np.ones(nverts, int) * path.Path.LINETO
codes[0::5] = path.Path.MOVETO
codes[4::5] = path.Path.CLOSEPOLY
verts[0::5, 0] = left
verts[0::5, 1] = bottom
verts[1::5, 0] = left
verts[1::5, 1] = top
verts[2::5, 0] = right
verts[2::5, 1] = top
verts[3::5, 0] = right
verts[3::5, 1] = bottom

barpath = path.Path(verts, codes)
patch = patches.PathPatch(barpath, facecolor='green', edgecolor='yellow', alpha=0.5)
ax.add_patch(patch)

ax.set_xlim(left[0], right[-1])
ax.set_ylim(bottom.min(), top.max())
plt.show()
```

## 现状

本文基于 2020 年前后教程（对应 matplotlib 2.x 时代）。形状与路径 API 高度稳定：

- `matplotlib.patches`（`Ellipse`/`Arc`/`Circle`/`Rectangle`/`Wedge`/`RegularPolygon`/`Arrow`/`FancyBboxPatch` 等）、`matplotlib.path.Path`、`PatchCollection`、`PathPatch` 在现行 matplotlib 3.x 中保持可用，本文代码基本可直接运行。
- 原文使用的 `fig.add_subplot(211, aspect='auto')` 与 `plt.axis('equal')`/`plt.tight_layout()` 用法在现行版本仍被支持。
- 更高级的路径操作（路径效果 `matplotlib.patheffects`、坐标变换 `matplotlib.transforms`）原文未展开，可查阅官方文档。

## 相关概念

- /concepts/01-artist-hierarchy.md — Artist 体系与 Patch（Rectangle/Polygon/Circle 等 Primitive）
- /concepts/03-pyplot-state-machine.md — pyplot 状态机与 Figure/Axes 管理
- /examples/basic-plotting.md — 基础绑图（与形状绘制的对比）
