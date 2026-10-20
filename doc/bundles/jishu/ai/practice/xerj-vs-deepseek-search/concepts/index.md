# Concepts 索引

本目录是 XERJ × DeepSeek Search/Fetch 对比知识包的概念文档，按「框架 → 决策轴 → 逐轴细化 → 落地」组织。

| 文档 | 一句话简介 |
|---|---|
| [00 对比框架与结论](00-comparison-frame.md) | 九个对照轴、三个根本差异，以及「不是竞品而是语料两端」这一核心结论与总表 |
| [01 语料归属](01-corpus-ownership.md) | 为什么「要检索的东西归谁」是第一决策轴；四类不可互换的问题；归属判定的三个问题与一个反直觉推论 |
| [02 上下文成本与接口契约](02-context-cost-and-contracts.md) | 「先摘要后全文」的两种实现（`_passage` + 投影 vs 三档摘要分层）、三个默认值陷阱、上下文预算的换算 |
| [03 失败语义与可诊断性](03-failure-semantics-and-boundaries.md) | 把错误码当契约读；XERJ 的边界编码进响应体 vs DeepSeek 的 404 五因合并；边界探测清单 |
| [04 成本曲线与选型](04-cost-model-and-selection.md) | 固定成本 vs 线性按次计费、深研型任务的量级测算、2026-11-01 计费切换、选型决策树与组合架构 |

```{toctree}
:maxdepth: 2

00-comparison-frame
01-corpus-ownership
02-context-cost-and-contracts
03-failure-semantics-and-boundaries
04-cost-model-and-selection
```
