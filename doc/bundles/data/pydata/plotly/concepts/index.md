# 概念索引

本目录包含 Plotly.py 核心概念的系统性讲解文档，按学习顺序排列。

## 文档列表

| 序号 | 文档 | 说明 |
|------|------|------|
| 00 | [Plotly.py 简介](00-introduction.md) | 交互式可视化库概览、MIT 许可证、声明式 API、plotly.js 渲染、Plotly Express、FigureWidget、Dash 集成 |
| 01 | [Figure 数据模型](01-figure-model.md) | Figure 顶层容器、data(traces) + layout、graph_objects 层级结构、魔术方法动态属性访问、JSON 序列化 |
| 02 | [Plotly Express](02-plotly-express.md) | px 模块高级 API、_chart_types.py 图表工厂函数、facet/marginal/animation 参数、长表宽表输入、_core.py 核心逻辑 |
| 03 | [渲染与 IO](03-rendering-io.md) | renderers 框架（notebook/browser/svg/png）、io 模块、offline 模式、to_json/to_html/fig.show() 流程、模板机制 |

## 推荐阅读顺序

```
00-introduction → 01-figure-model → 02-plotly-express → 03-rendering-io
       ↓                                                        ↓
  references/graph-obj-model.md                    examples/interactive-charts.md
```

1. 先读 **00-introduction** 了解 Plotly.py 是什么
2. 再读 **01-figure-model** 理解核心数据结构
3. 然后读 **02-plotly-express** 学习高效绘图
4. 最后读 **03-rendering-io** 掌握输出与部署
5. 需要深入源码细节时参考 **references/** 目录
6. 需要可运行代码时参考 **examples/** 目录

```{toctree}
:hidden:

00-introduction
01-figure-model
02-plotly-express
03-rendering-io
```
