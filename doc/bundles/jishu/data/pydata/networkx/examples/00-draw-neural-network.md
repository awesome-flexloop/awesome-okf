---
type: Example
title: 画出神经网络（DAG）完整示例
description: 基于 2020 年前后教程的神经网络 DAG 绘制完整示例：DAGMeta 基类按层布局，SlowlyDAG 用 nx.draw 整体绘制，DAG 用 draw_networkx_* 分步高效渲染
tags: [networkx, dag, neural-network, digraph, draw_networkx, example]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-3f4f28183885
    resource: /references/source-03.md
    title: 信源登记：使用 NetworkX 画神经网络（F-106~F-113）
---

# 画出神经网络（DAG）完整示例

本文基于 2020 年前后教程（简书《2 使用 NetworkX 画神经网络》）。神经网络是有向无环图（DAG），因此用 NetworkX 的有向图包（`nx.DiGraph`）处理（F-106）。本示例给出两种完整可运行的绘制方案。

## 一、DAGMeta 基类

先定义一个 DAG 的基类，它负责按层计算节点位置。`DAGMeta.__init__` 接收每层节点数 `layer_sizes` 与所在矩形区域 `bbox`（默认 `(.1, .1, .9, .9)`，F-107），并据此计算横向/纵向间距（F-108）：

```python
from matplotlib import pyplot as plt
import networkx as nx

class DAGMeta:
    def __init__(self, layer_sizes, bbox=(.1, .1, .9, .9)):
        '''
        bbox: DAG 所在矩形区域
        layer_sizes: DAG 每层的节点数
        '''
        self.bbox = bbox
        self.layer_sizes = layer_sizes

    @property
    def w(self):
        '''DAG 的画布宽度'''
        return self.bbox[2] - self.bbox[0]

    @property
    def h(self):
        '''DAG 的画布高度'''
        return self.bbox[3] - self.bbox[1]

    @property
    def x_center(self):
        '''DAG 的画布水平中心'''
        return (self.bbox[2] + self.bbox[0]) / 2

    @property
    def y_center(self):
        '''DAG 的画布竖直中心'''
        return (self.bbox[3] + self.bbox[1]) / 2

    def __len__(self):
        '''DAG 的层数'''
        return len(self.layer_sizes)

    @property
    def x_spacing(self):
        '''DAG 水平方向的留白间隙'''
        return self.w / (len(self) - 1)

    @property
    def y_spacing(self):
        '''DAG 竖直方向的留白间隙'''
        return self.h / max(self.layer_sizes)
```

## 二、方案一：SlowlyDAG（nx.draw 整体绘制）

`SlowlyDAG` 用循环把每层节点加入 `nx.DiGraph()`，通过 `G.add_node(node_count, pos=(...))` 为节点附带位置属性，层间节点两两连边（F-109）：

```python
class SlowlyDAG(DAGMeta):
    def plot(self):
        import random
        G = nx.DiGraph()
        node_count = 0
        for i, v in enumerate(self.layer_sizes):
            layer_top = self.y_spacing * (v - 1) / 2. + self.y_center
            for j in range(v):
                G.add_node(node_count, pos=(self.bbox[0] + i * self.x_spacing,
                                            layer_top - j * self.y_spacing))
                node_count += 1

        for x, (left_nodes, right_nodes) in enumerate(zip(self.layer_sizes[:-1],
                                                          self.layer_sizes[1:])):
            for i in range(left_nodes):
                for j in range(right_nodes):
                    G.add_edge(i + sum(self.layer_sizes[:x]),
                               j + sum(self.layer_sizes[:x + 1]))

        pos = nx.get_node_attributes(G, 'pos')   # 把每个节点中的位置 pos 信息导出来
        nx.draw(G, pos,
                node_color=range(node_count),
                with_labels=True,
                node_size=500,
                edge_color=[random.random() for i in range(len(G.edges))],
                width=2,
                font_color='black',
                cmap=plt.cm.Paired,   # matplotlib 的调色板
                edge_cmap=plt.cm.Blues)
        plt.show()
```

调用实例（F-113 的前半部分）：

```python
bbox = .1, .1, .9, .9          # 网络所在矩形区域
layer_sizes = [4, 7, 5, 2]     # 网络每层的节点数
self = SlowlyDAG(layer_sizes, bbox)
self.plot()
```

## 三、方案二：DAG（draw_networkx_* 分步高效绘制）

`SlowlyDAG` 虽能画出 DAG 但速度较慢，可用 NetworkX 内置函数分步绘制。`DAG` 类构造函数执行 `self._dag = nx.DiGraph(name=name)`（F-111），`layout_nodes` 为每层每个节点添加带 LaTeX 风格名称（`$x^{m}_{n}$`）的节点与位置（F-111、F-112）：

```python
import numpy as np

class DAG(DAGMeta):
    def __init__(self, layer_sizes, bbox=(.1, .1, .9, .9), name='DAG'):
        super().__init__(layer_sizes, bbox)
        self._dag = nx.DiGraph(name=name)   # 可通过 self.name 获取名称

    def node_position(self, m, n):
        '''节点的位置
        m: DAG 的层序号
        n: DAG 该层的节点序号
        '''
        x = self.bbox[0] + m * self.x_spacing
        layer_top = self.y_spacing * (self.layer_sizes[m] - 1) / 2. + self.y_center
        y = layer_top - n * self.y_spacing
        return x, y

    def layout_nodes(self):
        for m, layer in enumerate(self.layer_sizes):
            for n in range(layer):
                self._dag.add_node(f"$x^{m}_{n}$", pos=self.node_position(m, n))

    @property
    def pairs(self):
        sizes = self.layer_sizes.copy()
        edgelist = []
        n_layer = 0
        for size in sizes[1:]:
            x, y = np.meshgrid(np.arange(sizes[0]), np.arange(sizes[1]))
            paris = np.stack([x.flatten(), y.flatten()], axis=1)
            edgelist.extend([f"$x^{n_layer}_{i}$", f"$x^{n_layer+1}_{j}$"]
                            for i, j in paris)
            del sizes[0]
            n_layer += 1
        return edgelist

    def plot(self):
        self.layout_nodes()
        pos = nx.get_node_attributes(self._dag, 'pos')
        nodes = nx.draw_networkx_nodes(self._dag, pos, node_size=500, alpha=0.7)
        nx.draw_networkx_edges(self._dag, pos,
                               edgelist=self.pairs,
                               width=2, alpha=0.3, edge_color='g')
        nx.draw_networkx_labels(self._dag, pos, font_size=14)
```

调用实例（F-113）：

```python
bbox = .1, .1, .9, .9          # 网络所在矩形区域
layer_sizes = [5, 7, 5, 3, 2]  # 网络每层的节点数
self = DAG(layer_sizes, bbox)
self.plot()
plt.axis('off')
plt.show()
```

## 运行要点

- 两个方案都依赖 `networkx` 与 `matplotlib`（方案二还需 `numpy`），请先安装这三个包。
- 方案一 `nx.draw(..., node_color=range(node_count), cmap=plt.cm.Paired)` 用整数序列直接着色并配合调色板；`edge_color` 用随机数并配 `edge_cmap=plt.cm.Blues`（F-110）。
- 方案二通过 `pairs` 属性用 `np.meshgrid` 生成相邻两层节点全连接的有向边列表，配合 `nx.draw_networkx_edges(..., edgelist=self.pairs)` 渲染（F-112）。
- 原文完整代码托管于 github.com/xinetzone/draw_dag（F-106 引言处注明）。

## 现状

本文基于 2020 年前后教程（对应 networkx 2.x 时代）：

- `nx.DiGraph`、`nx.get_node_attributes`、`nx.draw_networkx_nodes` / `draw_networkx_edges` / `draw_networkx_labels` 在 networkx 3.x 中保持可用，DAG 分层布局思路（按层计算 x/y 间距）依然适用。
- 原文 `SlowlyDAG` 中把整数序列直接当 `node_color` 的用法，在现行 matplotlib 中可能需要配合 `vmin`/`vmax` 或显式颜色映射才能正确着色——如遇颜色异常，请按所安装 matplotlib 版本的 `scatter`/`draw` 颜色规范调整。
- 层标识用 LaTeX 风格节点名（`$x^{m}_{n}$`），该命名手法不依赖版本，仍可直接使用。

## 相关概念

- /concepts/02-directed-graph-and-dag.md — 有向图与 DAG（含完整代码讲解）
- /concepts/01-drawing-and-layout.md — 绘制与布局（nx.draw 基础）
- /examples/01-draw-simple-path.md — 简单路径绘制示例
