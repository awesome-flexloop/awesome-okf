---
type: Reference
title: 信源登记：使用 NetworkX 画神经网络（简书 3f4f28183885）
description: 简书文章《2 使用 NetworkX 画神经网络》信源登记：URL、标题、时点与 F-106~F-113 事实清单（DAG）
tags: [networkx, dag, neural-network, digraph, source, jianshu]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-3f4f28183885
    url: https://www.jianshu.com/p/3f4f28183885
    title: 2 使用 NetworkX 画神经网络（水之心，2020 年前后）
---

# 信源登记：使用 NetworkX 画神经网络

本文登记简书文章《2 使用 NetworkX 画神经网络》的信源信息与编号事实，供本束概念与示例文档溯源使用。

## 文章信息

| 项目 | 内容 |
|------|------|
| 标题 | 2 使用 NetworkX 画神经网络 |
| URL | https://www.jianshu.com/p/3f4f28183885 |
| 作者 | 水之心 |
| 时点 | 2020 年前后（发布于 2020-06-06） |
| 所属连载 | matplotlib & pillow & networkx 手册（停止维护），nb/46194813 |
| 完整代码 | github.com/xinetzone/draw_dag |

## 事实清单（F-106 ~ F-113）

- **F-106**：神经网络是有向无环图（DAG），文章使用 NetworkX 的有向图包处理。
- **F-107**：定义 `DAGMeta` 基类，其 `__init__(self, layer_sizes, bbox=(.1, .1, .9, .9))` 接收 `layer_sizes` 与 `bbox` 两个参数。
- **F-108**：`DAGMeta` 属性 `x_spacing` 返回 `self.w/(len(self) - 1)`，`y_spacing` 返回 `self.h/max(self.layer_sizes)`。
- **F-109**：`SlowlyDAG.plot()` 调用 `nx.DiGraph()` 创建有向图，并通过 `G.add_node(node_count, pos=(...))` 为节点添加位置属性。
- **F-110**：`SlowlyDAG.plot()` 调用 `nx.draw(G, pos, node_color=range(node_count), with_labels=True, node_size=500, edge_color=[random.random() for i in range(len(G.edges))], width=2, font_color='black', cmap=plt.cm.Paired, edge_cmap=plt.cm.Blues)`。
- **F-111**：`DAG` 类构造函数执行 `self._dag = nx.DiGraph(name=name)`，注释说明可通过 `self.name` 获取名称。
- **F-112**：`DAG.plot()` 调用 `nx.get_node_attributes(self._dag, 'pos')` 获取节点位置，并依次调用 `nx.draw_networkx_nodes`、`nx.draw_networkx_edges`、`nx.draw_networkx_labels` 绘制。
- **F-113**：调用实例 `self = DAG([5, 7, 5, 3, 2], bbox)`，其后调用 `plt.axis('off')` 与 `plt.show()`。

## 文档引用

- 本束概念 [有向图与 DAG](../concepts/02-directed-graph-and-dag.md) 与示例 [画出神经网络](../examples/00-draw-neural-network.md) 引用本文信源。
