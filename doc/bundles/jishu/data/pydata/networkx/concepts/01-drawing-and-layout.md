---
type: Concept
title: NetworkX 绘制与布局
description: 用 nx.draw 绘制无向/有向路径图，并通过 pos 字典控制布局、node_color/node_size/node_shape 控制节点样式与标签透明度
tags: [networkx, draw, layout, node-style, concept]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-5b8489e1e4a8
    resource: /references/source-02.md
    title: 信源登记：NetworkX 画出简单路径（F-114~F-119）
---

# NetworkX 绘制与布局

本文基于 2020 年前后教程（简书《NetworkX 画出简单路径》）。NetworkX 的「画图」能力委托 matplotlib 渲染——`nx.draw` 系列函数本质是生成布局并把图交给 matplotlib 绘制。

## 一、绘制一条简单路径

`nx.path_graph(n)` 创建 n 个节点依次相连的路径图（F-114）：

```python
import networkx as nx

G = nx.path_graph(4)
nx.draw(G)
```

有向图路径用 `create_using=nx.DiGraph()`（F-115）：

```python
G = nx.path_graph(4, create_using=nx.DiGraph())
nx.draw(G)
```

## 二、布局：pos 字典

布局由 `pos` 字典控制，键为节点、值为坐标元组。水平布局把所有节点放在 y=0 直线上（F-116）：

```python
G = nx.path_graph(4)
pos = {node: (node, 0) for node in G}
nx.draw(G, pos=pos)
```

竖直布局把所有节点放在 x=0 直线上（F-117）：

```python
G = nx.path_graph(4)
pos = {node: (0, node) for node in G}
nx.draw(G, pos=pos)
```

## 三、修改节点样式

除位置外，颜色、大小、形状均可任意设置（F-118）：

```python
G = nx.path_graph(4)
pos = {node: (node, 0) for node in G}
ncolor = ['r', 'b', 'k', 'g']   # 节点颜色
nsize = [600, 400, 200, 100]    # 节点大小
nshape = '>'                    # 节点形状
nx.draw(G, pos=pos, node_color=ncolor, node_shape=nshape, node_size=nsize)
```

## 四、标签与透明度

`with_labels=True` 显示默认标签，`font_color` 设置标签字体颜色（F-119）：

```python
G = nx.path_graph(4)
pos = {node: (node, 0) for node in G}
ncolor = 'g'
nsize = 500
nshape = 'o'
nx.draw(G, pos=pos, node_color=ncolor,
        with_labels=True,        # 显示标签
        font_color='w',          # 设置标签字体颜色
        node_shape=nshape, node_size=nsize)
```

`alpha=0.4` 设置节点透明度（F-119）：

```python
G = nx.path_graph(4)
pos = {node: (node, 0) for node in G}
ncolor = 'r'
nsize = 500
nshape = 'o'
nx.draw(G, pos=pos, node_color=ncolor,
        with_labels=True,        # 显示标签
        font_color='k',
        alpha=0.4,               # 设置透明度
        node_shape=nshape, node_size=nsize)
```

## 现状

本文基于 2020 年前后教程（对应 networkx 2.x 时代）。`nx.draw` 的核心参数在 networkx 3.x 中仍受支持：

- `pos`、`node_color`、`node_shape`、`node_size`、`with_labels`、`font_color`、`alpha` 等参数签名在 3.x 的 `nx.draw` 中保持兼容，本教程代码可直接运行。
- 注意 `nx.draw` 依赖 matplotlib 渲染；若仅需布局坐标（不绘图），可改用 `nx.spring_layout`、`nx.circular_layout` 等布局函数生成 `pos` 字典。
- 运行示例前需安装 `networkx` 与 `matplotlib` 两个包。

## 相关概念

- /concepts/00-nodes-and-edges.md — 节点与边及属性
- /concepts/02-directed-graph-and-dag.md — 有向图与 DAG（DiGraph 绘制）
- /examples/01-draw-simple-path.md — 简单路径绘制完整示例
