---
type: Reference
title: 信源登记：画分形图的一个例子（简书 0099313fce96）
description: 简书文章《画分形图的一个例子》信源登记：URL、标题、时点与 F-101~F-105 事实清单（Chaos Game 分形三角形）
tags: [matplotlib, fractal, chaos-game, source, jianshu]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-0099313fce96
    url: https://www.jianshu.com/p/0099313fce96
    title: 画分形图的一个例子（水之心，2020 年前后）
---

# 信源登记：画分形图的一个例子

本文登记简书文章《画分形图的一个例子》的信源信息与编号事实，供本束示例文档溯源使用。

## 文章信息

| 项目 | 内容 |
|------|------|
| 标题 | 画分形图的一个例子 |
| URL | https://www.jianshu.com/p/0099313fce96 |
| 作者 | 水之心 |
| 时点 | 2020 年前后（发布于 2020-08-31） |
| 所属连载 | matplotlib & pillow & networkx 手册（停止维护），nb/46194813 |

## 事实清单（F-101 ~ F-105）

- **F-101**：代码导入 `random`、`numpy` 与 `matplotlib.pyplot` 三个模块。
- **F-102**：设置三角形顶点坐标 `x = [1, 1.5, 2]`、`y = [1, 1+np.sqrt(.75), 1]`。
- **F-103**：定义函数 `next_point(array, array2)`，函数体返回 `(array + array2) * .5`。
- **F-104**：调用 `plt.figure(figsize=(10, 10))` 创建画布，用 `plt.scatter(x, y)` 与 `plt.scatter(rx, ry)` 绘制三角形顶点与初始随机点。
- **F-105**：设置循环次数 `n = 100000`，循环内每次用 `random.choice(dirc)` 从顶点列表随机取一个顶点并计算新点，用 `plt.scatter(start[0], start[1], s=5)` 绘制，最后调用 `plt.savefig('ChaosGameTriangle'+str(n)+'.png')` 与 `plt.show()`。

## 文档引用

- 本束示例 [fractal](../examples/fractal.md) 引用本文信源。
