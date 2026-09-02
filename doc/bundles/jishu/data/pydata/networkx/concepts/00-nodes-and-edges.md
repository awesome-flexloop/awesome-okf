---
type: Concept
title: NetworkX 节点与边
description: NetworkX 图的节点与边可以是任意可哈希对象与任意关联对象；本文介绍图/边/节点三级属性的添加与访问方式
tags: [networkx, graph, nodes, edges, attributes, concept]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-f687c1aecfcc
    resource: /references/source-01.md
    title: 信源登记：NetworkX 中的节点与边（F-192~F-197）
---

# NetworkX 节点与边

本文基于 2020 年前后教程（简书《NetworkX 中的节点与边》）。NetworkX 对节点与边可容纳的对象类型不做限定：节点可以是任何可哈希的 Python 对象（`None` 除外）；边可以使用 `G.add_edge(n1, n2, object=x)` 创建与任意对象 x 的联系（F-192）。例如 n1、n2 可以是蛋白质对象，x 可以是记录其相互作用的文献 XML 记录。

若需要更传统的整数标签图，可用 `convert_node_labels_to_integers()` 函数转换（F-193）。

## 一、为边添加属性

创建空图并逐条添加带属性的边（F-194）：

```python
import networkx as nx
from matplotlib import pyplot as plt

G = nx.Graph()                 # 创建空图
G.add_edge(1, 2, length=10)    # 为边 (1,2) 添加属性 length = 10
G.add_edge(1, 3, weight=20)    # 为边 (1,3) 添加属性 weight = 20
G.add_edge(2, 3, capacity=15)  # 为边 (2,3) 添加属性 capacity = 15
nx.draw(G)                     # 画出图
```

为已有边添加新属性（F-195）：

```python
G[1][3]['color'] = 'red'       # 等价于 G[1][3].update({'color': 'red'})
```

更多边属性操作（F-195）：

```python
G.add_edge(1, 2, weight=4.7)
G.add_edges_from([(3, 4), (4, 5)], color='red')
G.add_edges_from([(1, 2, {'color': 'blue'}), (2, 3, {'weight': 8})])
G[1][2]['weight'] = 4.7
G.edges[3, 4]['weight'] = 4.2
```

## 二、为图添加属性

在构造时直接传入属性，或通过 `G.graph` 字典添加（F-196）：

```python
G = nx.Graph(day='Friday')
G.graph                      # {'day': 'Friday'}
```

也可先建空图再添加：

```python
G = nx.Graph()
G.graph['day'] = 'Friday'
G.graph                      # {'day': 'Friday'}
```

## 三、为节点添加属性

节点的属性通过 `add_node` / `add_nodes_from` 附带，或直接经 `G.nodes[1]` 字典写入（F-197）：

```python
G.add_node(1, time='5pm')
G.add_nodes_from([3], time='2pm')
G.nodes[1]                   # {'time': '5pm'}
G.nodes[1]['room'] = 714
G.nodes.data()               # NodeDataView({1: {'time': '5pm', 'room': 714}, 3: {'time': '2pm'}})
```

`G.nodes.data()` 返回 `NodeDataView`，可直接查看全部节点的属性字典（F-197）。

## 现状

本文基于 2020 年前后教程（对应 networkx 2.x 时代）。以上节点/边/图三级属性 API 在 networkx 3.x 中保持稳定：

- `add_edge`/`add_edges_from`/`add_node`/`add_nodes_from`、`G.graph`、`G.nodes.data()`、`G.edges[...]` 赋值与 `G[...][...]['attr']` 索引在 3.x 中均可直接使用。
- `convert_node_labels_to_integers()` 在 2.x 起位于 `networkx.relabel` 子模块（`nx.relabel.convert_node_labels_to_integers`），导入路径以所安装版本为准。

## 相关概念

- /concepts/01-drawing-and-layout.md — 图的绘制与布局
- /concepts/02-directed-graph-and-dag.md — 有向图与 DAG
- /examples/01-draw-simple-path.md — 简单路径绘制示例
