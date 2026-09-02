---
okf_version: "0.2"
---

# NetworkX 网络分析与绘图知识库

本知识包是 [NetworkX](https://networkx.org)（Python 生态最常用的网络/图分析库）的入门知识包，基于 2020 年前后简书连载《matplotlib & pillow & networkx 手册(停止维护)》中 3 篇 NetworkX 相关文章生成，覆盖节点与边、图的绘制与布局、以及用有向无环图（DAG）绘制神经网络结构三部分内容。所有内容均溯源至编号事实（spec:jianshu-blogs-to-okf-wiki 的 facts.md，F-106~F-197），遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 入门基础（concepts/）

* [节点与边](concepts/00-nodes-and-edges.md) — 节点/边/图三级属性的添加与访问：`add_node`/`add_edge`/`add_edges_from`、`G.graph`、`G.nodes.data()` 等。
* [绘制与布局](concepts/01-drawing-and-layout.md) — 用 `nx.path_graph` 绘制无向/有向路径；`pos` 字典控制布局；`node_color`/`node_size`/`node_shape` 控制节点样式、标签与透明度。
* [有向图与 DAG](concepts/02-directed-graph-and-dag.md) — 用 `nx.DiGraph` 表示有向无环图并绘制神经网络；DAGMeta 基类按层计算节点位置；SlowlyDAG 整体绘制与 DAG 分步高效绘制。

## 实战示例（examples/）

* [画出神经网络（DAG）](examples/00-draw-neural-network.md) — 完整可运行的 DAG 神经网络绘制：DAGMeta 按层布局、SlowlyDAG 用 `nx.draw` 整体绘制、DAG 用 `draw_networkx_*` 分步渲染。
* [画出简单路径](examples/01-draw-simple-path.md) — 完整可运行的简单路径绘制：无向/有向路径、水平/竖直布局、节点样式定制、标签与透明度。

## 信源登记簿（references/）

* [信源索引](references/index.md) — 3 篇简书文章信源登记概览。
* [source-01](references/source-01.md) — 《NetworkX 中的节点与边》（F-192~F-197，2020 年前后）。
* [source-02](references/source-02.md) — 《NetworkX 画出简单路径》（F-114~F-119，2020 年前后）。
* [source-03](references/source-03.md) — 《2 使用 NetworkX 画神经网络》（F-106~F-113，2020 年前后）。

## 学习路径建议

1. **入门**：concepts/00-nodes-and-edges.md → concepts/01-drawing-and-layout.md → 运行 examples/01-draw-simple-path.md
2. **进阶**：concepts/02-directed-graph-and-dag.md → 运行 examples/00-draw-neural-network.md
3. **溯源**：阅读 references/source-01~03.md，结合编号事实核对 API 用法

## 信任与生命周期说明

* **status 判定依据**：全部内容文档均 `status: stable`，基于 2020 年前后教程，引用编号事实 F-106~F-197。
* **stale_after 解释**：统一设置为 `2026-12-31`。教程对应 networkx 2.x 时代，核心 API（节点/边属性、`nx.draw`、`DiGraph`、`draw_networkx_*`）在 3.x 中保持兼容；该日期作为对旧教程时效性的保守重新评估节点。
* **核验链路**：`generated.at` 与 `verified.at` 均记录为 2026-09-02T00:00:00Z（spec:jianshu-blogs-to-okf-wiki 生成、process:seven-concepts-v 核验）；概念/示例文档均给出「现状」标注过时 API。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
