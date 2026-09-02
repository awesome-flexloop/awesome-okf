# 示例索引（Examples）

本目录包含 NetworkX 绘图的完整可运行示例，全部基于 2020 年前后教程（简书连载《matplotlib & pillow & networkx 手册》）。

## 示例列表

| 文档 | 覆盖内容 |
|------|---------|
| [画出神经网络（DAG）](00-draw-neural-network.md) | DAGMeta 基类按层布局；SlowlyDAG 用 `nx.draw` 整体绘制；DAG 用 `draw_networkx_nodes/edges/labels` 分步高效渲染（F-106~F-113） |
| [画出简单路径](01-draw-simple-path.md) | `nx.path_graph` 无向/有向路径；pos 水平/竖直布局；node_color/node_size/node_shape 节点样式；标签字体与透明度（F-114~F-119） |

## 运行环境

- Python 3.10+
- NetworkX（教程为 2.x 时代，3.x 兼容）
- Matplotlib（`nx.draw` 依赖其渲染）
- NumPy（仅 DAG 示例的 `pairs` 属性需要）

```{toctree}
:hidden:
:maxdepth: 7

00-draw-neural-network
01-draw-simple-path
```
