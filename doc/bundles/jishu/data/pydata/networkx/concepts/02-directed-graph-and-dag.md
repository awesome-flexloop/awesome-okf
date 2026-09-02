---
type: Concept
title: NetworkX 有向图与 DAG
description: 用 nx.DiGraph 表示有向无环图（DAG）并绘制神经网络结构；DAGMeta 基类按层计算节点位置，draw_networkx_nodes/edges/labels 分步渲染
tags: [networkx, digraph, dag, neural-network, draw_networkx, concept]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-3f4f28183885
    resource: /references/source-03.md
    title: 信源登记：使用 NetworkX 画神经网络（F-106~F-113）
---

# NetworkX 有向图与 DAG

本文基于 2020 年前后教程（简书《2 使用 NetworkX 画神经网络》）。神经网络是有向无环图（DAG），因此用 NetworkX 的有向图包（`nx.DiGraph`）处理（F-106）。

## 一、DAGMeta 基类：按层计算节点位置

`DAGMeta` 基类接收每层节点数 `layer_sizes` 与所在矩形区域 `bbox`，并据此计算横向/纵向间距（F-107、F-108）：

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

`x_spacing` 返回 `self.w/(len(self) - 1)`，`y_spacing` 返回 `self.h/max(self.layer_sizes)`（F-108）。

## 二、SlowlyDAG：用 DiGraph 构造并整体绘制

用循环把每层节点加入 `nx.DiGraph()`，通过 `G.add_node(node_count, pos=(...))` 为节点附带位置属性，层间节点两两连边（F-109）：

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

`SlowlyDAG.plot()` 调用 `nx.draw(G, pos, node_color=range(node_count), with_labels=True, node_size=500, edge_color=[random.random() for i in range(len(G.edges))], width=2, font_color='black', cmap=plt.cm.Paired, edge_cmap=plt.cm.Blues)`（F-110）。调用实例：

```python
bbox = .1, .1, .9, .9          # 网络所在矩形区域
layer_sizes = [4, 7, 5, 2]     # 网络每层的节点数
self = SlowlyDAG(layer_sizes, bbox)
self.plot()
```

## 三、DAG：用 draw_networkx_* 分步高效绘制

`SlowlyDAG` 虽能画出 DAG 但速度较慢，可用 NetworkX 内置函数分步绘制。`DAG` 类构造函数执行 `self._dag = nx.DiGraph(name=name)`，注释说明可通过 `self.name` 获取名称（F-111）：

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

`DAG.plot()` 调用 `nx.get_node_attributes(self._dag, 'pos')` 获取节点位置，并依次调用 `nx.draw_networkx_nodes`、`nx.draw_networkx_edges`、`nx.draw_networkx_labels` 绘制（F-112）。调用实例（F-113）：

```python
bbox = .1, .1, .9, .9          # 网络所在矩形区域
layer_sizes = [5, 7, 5, 3, 2]  # 网络每层的节点数
self = DAG(layer_sizes, bbox)
self.plot()
plt.axis('off')
plt.show()
```

## 现状

本文基于 2020 年前后教程（对应 networkx 2.x 时代）：

- `nx.DiGraph`、`nx.get_node_attributes`、`nx.draw_networkx_nodes` / `draw_networkx_edges` / `draw_networkx_labels` 在 networkx 3.x 中保持可用，DAG 分层布局思路（按层计算 x/y 间距）依然适用。
- 原文 `SlowlyDAG` 中 `nx.draw(G, pos, node_color=range(node_count), ...)` 这类把整数序列直接当 `node_color` 的用法，在现行 matplotlib 中可能需要配合 `vmin`/`vmax` 或显式颜色映射才能正确着色——如遇颜色异常，请按所安装 matplotlib 版本的 `scatter`/`draw` 颜色规范调整。
- 层标识用 LaTeX 风格节点名（`$x^{m}_{n}$`），该命名手法不依赖版本，仍可直接使用。

## 相关概念

- /concepts/00-nodes-and-edges.md — 节点与边及属性
- /concepts/01-drawing-and-layout.md — 绘制与布局（nx.draw 基础）
- /examples/00-draw-neural-network.md — 画出神经网络完整示例
