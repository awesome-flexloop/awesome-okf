---
type: Reference
title: 信源登记：matplotlib 之形状与路径 patches 和 path（简书 d52132ab9ccc）
description: 简书文章《matplotlib 之形状与路径：patches和path》信源登记：URL、标题、时点与 F-184~F-191 事实清单
tags: [matplotlib, patches, path, source, jianshu]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-d52132ab9ccc
    url: https://www.jianshu.com/p/d52132ab9ccc
    title: matplotlib 之形状与路径：patches和path（水之心，2020 年前后）
---

# 信源登记：matplotlib 之形状与路径（patches 和 path）

本文登记简书文章《matplotlib 之形状与路径：patches和path》的信源信息与编号事实，供本束示例文档溯源使用。

## 文章信息

| 项目 | 内容 |
|------|------|
| 标题 | matplotlib 之形状与路径：patches和path |
| URL | https://www.jianshu.com/p/d52132ab9ccc |
| 作者 | 水之心 |
| 时点 | 2020 年前后（发布于 2020-06-05，最后编辑 2020-06-13） |
| 所属连载 | matplotlib & pillow & networkx 手册（停止维护），nb/46194813 |
| 原始出处 | 转载自 qinqianshan.com《matplotlib高级教程之形状与路径——patches和path》 |

## 事实清单（F-184 ~ F-191）

- **F-184**：形状指 `matplotlib.patches` 包中的对象（如箭头、正方形、椭圆），路径指 `matplotlib.path` 中实现的功能。
- **F-185**：`patches.Ellipse((xcenter, ycenter), width, height, angle=angle, linewidth=2, fill=False, zorder=2)` 创建椭圆；`patches.Arc` 等价，因为 `Arc` 继承自 `Ellipse` 类。
- **F-186**：`plt` 只实现了 `Rectangle`、`Circle`、`Polygon` 三个常用图形，更复杂的图形使用 `patches` 模块。
- **F-187**：用 `ax.add_patch(e1)` 添加单个 patch，或用 `PatchCollection(patches)` 构造集合后 `ax.add_collection(collection)` 添加集合。
- **F-188**：形状示例创建 `mpatches.Circle`、`mpatches.Rectangle`、`mpatches.Wedge`、`mpatches.RegularPolygon`、`mpatches.Ellipse`、`mpatches.Arrow`、`mpatches.PathPatch`、`mpatches.FancyBboxPatch`、`mlines.Line2D` 等对象，其中 `mpatches.Wedge(grid[2], 0.1, 30, 270, ec="none")`。
- **F-189**：路径代码用 `Path(verts, codes)` 创建路径对象，示例 codes 为 `[Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]`，通过 `patches.PathPatch(path, facecolor='orange', lw=2)` 与 `ax.add_patch(patch)` 绘制。
- **F-190**：`Path` 类定义 `Path(vertices, codes=None, _interpolation_steps=1, closed=False, readonly=False)`；codes 含义：`MOVETO` 移动钢笔到给定顶点（起始点）、`LINETO` 绘制直线到给定顶点、`CURVE3` 二次贝塞尔曲线、`CURVE4` 三次贝塞尔曲线、`CLOSEPOLY` 绘制线段到当前折线起始点、`STOP` 为整个路径末尾标记。
- **F-191**：条形图路径代码用 `np.random.seed(19680801)` 固定随机数种子、`np.histogram(data, 100)` 计算直方图，构造条形图顶点与 codes 后通过 `patches.PathPatch(barpath, facecolor='green', edgecolor='yellow', alpha=0.5)` 绘制。

## 文档引用

- 本束示例 [patches-and-path](../examples/patches-and-path.md) 引用本文信源。
