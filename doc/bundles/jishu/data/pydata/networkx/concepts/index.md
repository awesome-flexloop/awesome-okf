# 概念索引（Concepts）

本目录包含 NetworkX 核心概念的系统性讲解，共 3 篇概念文档，建议按顺序阅读。

## 概念列表

| 序号 | 文档 | 核心内容 |
|------|------|---------|
| 00 | [节点与边](00-nodes-and-edges.md) | 节点/边/图三级属性的添加与访问；`add_node`/`add_edge`/`add_edges_from`、`G.graph`、`G.nodes.data()`（F-192~F-197） |
| 01 | [绘制与布局](01-drawing-and-layout.md) | `nx.path_graph` 无向/有向路径；pos 字典布局；node_color/node_size/node_shape 节点样式；标签与透明度（F-114~F-119） |
| 02 | [有向图与 DAG](02-directed-graph-and-dag.md) | `nx.DiGraph` 表示 DAG；DAGMeta 按层计算节点位置；SlowlyDAG 整体绘制与 DAG 分步绘制（F-106~F-113） |

## 阅读路径建议

```
00-nodes-and-edges（理解数据模型）
    ↓
01-drawing-and-layout（理解绘制与布局）
    ↓
02-directed-graph-and-dag（进阶：DAG 分层绘制）
    ↓
examples/00-draw-neural-network.md（动手实践）
```

## 概念依赖关系

```
00-nodes-and-edges
    └── 01-drawing-and-layout
          └── 02-directed-graph-and-dag
                └── examples/00-draw-neural-network.md
```

```{toctree}
:hidden:
:maxdepth: 7

00-nodes-and-edges
01-drawing-and-layout
02-directed-graph-and-dag
```
