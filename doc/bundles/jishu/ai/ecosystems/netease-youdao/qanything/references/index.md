# 信源与证据

QAnything 知识包的三篇证据文档，构成 R→I→E→V→C 生成链路的事实底座。

* [QAnything 源码事实清单](facts.md) — R 阶段事实采集：60 条零推测源码事实（F-qa-001~060），逐条溯源至 vendor 基线的 local_doc_qa、parent_retriever、vectorstore、model_config 等 20 余个核心源码文件。
* [QAnything 架构洞察](insights.md) — I 阶段架构洞察：基于 60 条事实提炼 5 条核心洞察（隐性召回契约、父子切分、多租户分区、服务化拆分、演进痕迹）并规划 concepts/ 知识地图。
* [QAnything 信源登记](sources.md) — 上游仓库、固定基线（v2.0.0-69-g615417a）、pin commit、AGPL-3.0 许可证与关键信源文件清单（R/I 阶段共用）。

```{toctree}
:hidden:
:maxdepth: 7

facts
insights
sources
```
