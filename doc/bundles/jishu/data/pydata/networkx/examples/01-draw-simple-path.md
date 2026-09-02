---
type: Example
title: 画出简单路径完整示例
description: 基于 2020 年前后教程的简单路径绘制完整示例：nx.path_graph 创建无向/有向路径，pos 控制水平/竖直布局，node_color/node_size/node_shape 与标签、透明度样式定制
tags: [networkx, path-graph, draw, layout, node-style, example]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-5b8489e1e4a8
    resource: /references/source-02.md
    title: 信源登记：NetworkX 画出简单路径（F-114~F-119）
---

# 画出简单路径完整示例

本文基于 2020 年前后教程（简书《NetworkX 画出简单路径》）。用 `nx.path_graph` 很容易画出一条路径，本示例展示从创建到布局、样式定制的完整过程。

## 一、画出一条简单的路径

无向图路径用 `nx.path_graph(n)` 创建，直接 `nx.draw(G)` 绘制（F-114）：

```python
import networkx as nx

G = nx.path_graph(4)
nx.draw(G)
```

有向图路径只需加 `create_using=nx.DiGraph()`（F-115）：

```python
G = nx.path_graph(4, create_using=nx.DiGraph())
nx.draw(G)
```

## 二、修改布局：pos 字典

以下以无向图为例说明布局与样式修改。

水平布局把所有节点放在 y=0 直线上（F-116）：

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

## 三、修改节点的样式

节点的颜色、大小、形状都可以任意设置（F-118）：

```python
G = nx.path_graph(4)
pos = {node: (node, 0) for node in G}
ncolor = ['r', 'b', 'k', 'g']   # 节点颜色
nsize = [600, 400, 200, 100]    # 节点大小
nshape = '>'                    # 节点形状
nx.draw(G, pos=pos, node_color=ncolor, node_shape=nshape, node_size=nsize)
```

## 四、节点显示默认标签与字体颜色

`with_labels=True` 显示默认标签，`font_color='w'` 把标签字体改为白色（F-119）：

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

## 五、设置节点的透明度

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

## 运行要点

- 运行前需安装 `networkx` 与 `matplotlib` 两个包（`nx.draw` 依赖 matplotlib 渲染）。
- 单值（如 `ncolor = 'g'`、`nsize = 500`、`nshape = 'o'`）会对所有节点统一生效；列表（如 `ncolor = ['r','b','k','g']`）则按节点顺序逐点生效。

## 现状

本文基于 2020 年前后教程（对应 networkx 2.x 时代）：

- `nx.path_graph`、`nx.draw` 及其 `pos`、`node_color`、`node_size`、`node_shape`、`with_labels`、`font_color`、`alpha` 等参数在 networkx 3.x 中保持兼容，代码可直接运行。
- 若仅需布局坐标而不绘图，可改用 `nx.spring_layout`、`nx.circular_layout` 等布局函数生成 `pos` 字典。

## 相关概念

- /concepts/01-drawing-and-layout.md — 绘制与布局（nx.draw 基础）
- /concepts/00-nodes-and-edges.md — 节点与边及属性
- /examples/00-draw-neural-network.md — 画出神经网络（DAG）完整示例
