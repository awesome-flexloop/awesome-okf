---
type: Example
title: Chaos Game 分形三角形
description: 基于 2020 年前后教程的 Chaos Game 分形三角形绘制：随机游走取中点迭代十万次，用 matplotlib 散点渲染
tags: [matplotlib, fractal, chaos-game, scatter, random, example]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-0099313fce96
    resource: /references/source-20.md
    title: 信源登记：画分形图的一个例子（F-101~F-105）
---

# Chaos Game 分形三角形

本文基于 2020 年前后教程（简书《画分形图的一个例子》）。Chaos Game（混沌游戏）是一种用随机过程生成分形的经典方法：从一个随机点出发，反复随机选择三角形的一个顶点并取中点，迭代大量次数后，点的分布会形成谢尔宾斯基三角形（Sierpinski triangle）式的分形图案。

## 一、完整代码

代码导入 `random`、`numpy` 与 `matplotlib.pyplot` 三个模块（F-101）。先设置三角形顶点坐标 `x = [1, 1.5, 2]`、`y = [1, 1+np.sqrt(.75), 1]`（等边三角形的三个顶点，F-102）：

```python
import random
import numpy as np
from matplotlib import pyplot as plt

# set point coordinates
x = [1, 1.5, 2]
y = [1, 1+np.sqrt(.75), 1]
ry = 1
rx = np.random.rand(1,) + 1
start = [ry, rx]
a, b, c = zip(x, y)  # set list of vertices for random choice
direction = [a, b, c]

def rand_dir(dirc):
    return np.array(random.choice(dirc))

def next_point(array, array2):
    return (array + array2) * .5
```

`next_point(array, array2)` 返回两点坐标的中点 `(array + array2) * .5`（F-103）。

接下来创建画布并绘制三角形顶点与初始随机点（F-104）：

```python
plt.figure(figsize=(10, 10))   # plot triangle
plt.scatter(x, y)              # plot initial random point
plt.scatter(rx, ry)
```

迭代 `n = 100000` 次：每次用 `random.choice(dirc)` 从顶点列表随机取一个顶点，计算新点（当前点与所选顶点的中点），并用 `plt.scatter(start[0], start[1], s=5)` 绘制；最后保存与展示（F-105）：

```python
n = 100000
for i in range(n):
    tri = rand_dir(direction)
    start = next_point(tri, start)
    point = plt.scatter(start[0], start[1], s=5)

plt.savefig('ChaosGameTriangle' + str(n) + '.png')
plt.show()
```

## 二、运行要点

- `next_point` 每步把当前点拉向随机顶点一半距离；初始点位置不影响最终分形形态，只影响收敛速度。
- 点尺寸 `s=5`、画布 `figsize=(10, 10)` 是原文设置，可直接复现。
- 保存文件名带迭代次数（`ChaosGameTriangle100000.png`）。

## 现状

本文基于 2020 年前后教程。核心算法与 API 均未过时：

- `random.choice`、`plt.scatter`、`plt.savefig`、`plt.show` 在现行 matplotlib 3.x 中仍可用，代码可直接运行。
- 性能提示：循环内逐点调用 `plt.scatter` 绘制 10 万点会较慢（原文即如此）。若需更快的渲染，可在循环内只累积坐标、循环结束后一次性 `plt.scatter(rxs, rys, s=5)` 批量绘制——这是性能优化建议，非原文内容。

## 相关概念

- /concepts/03-pyplot-state-machine.md — pyplot 状态机（figure/scatter/savefig/show）
- /concepts/01-artist-hierarchy.md — Artist 体系（散点归属 Axes）
- /examples/basic-plotting.md — 基础绑图（scatter 散点图基础）
