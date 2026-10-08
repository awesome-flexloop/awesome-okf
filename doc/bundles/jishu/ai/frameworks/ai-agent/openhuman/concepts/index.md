# 概念文档（Concepts）

本目录收录 OpenHuman 知识包的概念文档，按"产品事实 → 核心机制 → 运行时设计 → 格局取舍"四层递进。

## 篇目导航

| 文档 | 核心内容 |
|------|---------|
| [00-what-is-openhuman](00-what-is-openhuman.md) | 定位（开源 agent harness）、双时点热度对照、时间线、GPL-3.0 与技术栈、四种官方安装路径与三步走 |
| [01-memory-tree-and-tokenjuice](01-memory-tree-and-tokenjuice.md) | Memory Tree 官方管线（分块/三树/作业队列/leaf 状态机/SQLite+Obsidian/20 分钟）、10 亿 token 勘误、TokenJuice 七阶段压缩与博文测算边界 |
| [02-runtime-and-agent-design](02-runtime-and-agent-design.md) | 检查点图编排与 Split Brain、Subconscious、吉祥物、四平台会议 Agent、本地隐私真实边界、Signal E2E + x402 |
| [03-landscape-and-tradeoffs](03-landscape-and-tradeoffs.md) | 博文/官方两套竞品表（含 Hermes Agent）、Early Beta 五类短板、数字口径速查、作者观点分层、主题关联 |

```{toctree}
:hidden:
:maxdepth: 2

00-what-is-openhuman
01-memory-tree-and-tokenjuice
02-runtime-and-agent-design
03-landscape-and-tradeoffs
```
