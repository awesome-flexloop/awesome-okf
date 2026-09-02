---
type: Reference
title: 信源登记：NetworkX 画出简单路径（简书 5b8489e1e4a8）
description: 简书文章《NetworkX 画出简单路径》信源登记：URL、标题、时点与 F-114~F-119 事实清单（布局与样式）
tags: [networkx, path-graph, draw, layout, source, jianshu]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-5b8489e1e4a8
    url: https://www.jianshu.com/p/5b8489e1e4a8
    title: NetworkX 画出简单路径（水之心，2020 年前后）
---

# 信源登记：NetworkX 画出简单路径

本文登记简书文章《NetworkX 画出简单路径》的信源信息与编号事实，供本束概念与示例文档溯源使用。

## 文章信息

| 项目 | 内容 |
|------|------|
| 标题 | NetworkX 画出简单路径 |
| URL | https://www.jianshu.com/p/5b8489e1e4a8 |
| 作者 | 水之心 |
| 时点 | 2020 年前后（发布于 2020-06-06） |
| 所属连载 | matplotlib & pillow & networkx 手册（停止维护），nb/46194813 |

## 事实清单（F-114 ~ F-119）

- **F-114**：使用 `G = nx.path_graph(4)` 创建路径图，并用 `nx.draw(G)` 绘制无向图路径。
- **F-115**：使用 `G = nx.path_graph(4, create_using=nx.DiGraph())` 创建有向图路径。
- **F-116**：水平布局代码使用 `pos = {node:(node, 0) for node in G}` 设置节点位置。
- **F-117**：竖直布局代码使用 `pos = {node:(0, node) for node in G}` 设置节点位置。
- **F-118**：修改节点样式代码调用 `nx.draw(G, pos=pos, node_color=ncolor, node_shape=nshape, node_size=nsize)`，其中 `ncolor = ['r', 'b', 'k', 'g']`、`nsize = [600, 400, 200, 100]`、`nshape = '>'`。
- **F-119**：`nx.draw(..., with_labels=True, font_color='w')` 修改标签字体颜色，`alpha=0.4` 设置节点透明度。

## 文档引用

- 本束概念 [绘制与布局](../concepts/01-drawing-and-layout.md) 与示例 [画出简单路径](../examples/01-draw-simple-path.md) 引用本文信源。
