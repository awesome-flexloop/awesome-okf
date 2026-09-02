---
type: Reference
title: 信源登记：NetworkX 中的节点与边（简书 f687c1aecfcc）
description: 简书文章《NetworkX 中的节点与边》信源登记：URL、标题、时点与 F-192~F-197 事实清单
tags: [networkx, nodes, edges, source, jianshu]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-f687c1aecfcc
    url: https://www.jianshu.com/p/f687c1aecfcc
    title: NetworkX 中的节点与边（水之心，2020 年前后）
---

# 信源登记：NetworkX 中的节点与边

本文登记简书文章《NetworkX 中的节点与边》的信源信息与编号事实，供本束概念与示例文档溯源使用。

## 文章信息

| 项目 | 内容 |
|------|------|
| 标题 | NetworkX 中的节点与边 |
| URL | https://www.jianshu.com/p/f687c1aecfcc |
| 作者 | 水之心 |
| 时点 | 2020 年前后（发布于 2020-06-05） |
| 所属连载 | matplotlib & pillow & networkx 手册（停止维护），nb/46194813 |

## 事实清单（F-192 ~ F-197）

- **F-192**：节点可以是任何可哈希的 Python 对象（`None` 除外）；边可以是使用 `G.add_edge(n1, n2, object=x)` 创建联系的任何对象 x。
- **F-193**：`convert_node_labels_to_integers()` 函数可得到整数标签的图。
- **F-194**：创建空图 `G = nx.Graph()`，调用 `G.add_edge(1, 2, length=10)`、`G.add_edge(1, 3, weight=20)`、`G.add_edge(2, 3, capacity=15)` 为边添加属性，并用 `nx.draw(G)` 画图。
- **F-195**：`G[1][3]['color'] = 'red'` 等价于 `G[1][3].update({'color': 'red'})`；`G.add_edges_from([(3, 4), (4, 5)], color='red')`、`G.add_edges_from([(1, 2, {'color': 'blue'}), (2, 3, {'weight': 8})])`、`G.edges[3, 4]['weight'] = 4.2` 等边属性操作。
- **F-196**：`G = nx.Graph(day='Friday')` 创建带属性的图，`G.graph` 显示为 `{'day': 'Friday'}`；也可用 `G.graph['day'] = 'Friday'` 添加属性。
- **F-197**：`G.add_node(1, time='5pm')`、`G.add_nodes_from([3], time='2pm')`、`G.nodes[1]['room'] = 714` 等节点属性操作，`G.nodes.data()` 返回 `NodeDataView`。

## 文档引用

- 本束概念 [节点与边](../concepts/00-nodes-and-edges.md) 引用本文信源。
