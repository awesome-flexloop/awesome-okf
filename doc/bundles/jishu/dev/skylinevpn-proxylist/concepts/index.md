---
okf_version: "0.2"
type: Concept
title: "skylinevpn-proxylist 概念层索引"
description: "从仓库定位、规则格式、上游消化、归约算法到发布通道与风险边界的六篇概念文档导航"
---

# 概念层索引

> 先读 [00 定位与全景](00-overview-and-positioning.md)：它说明「一份数据文件为什么需要一个仓库」，并决定你用哪条路线读后面五篇。

| 篇目 | 回答的问题 | 关键结论 |
|------|-----------|---------|
| [00 定位与全景](00-overview-and-positioning.md) | 这个仓库是什么？为什么只有 7 个文件？ | **单文件数据产品仓**：产物是 `proxy.list`，代码只是编译器 |
| [01 规则文件格式](01-rule-file-format.md) | 三节各是什么？条目怎么解释？ | 后缀 / 精确 / 正则三节，语义只由 `merge.py` 定义 |
| [02 上游消化](02-upstream-digestion-pipeline.md) | gfwlist 怎么变成三节？ | base64 解码 → AutoProxy 语法降维 → 丢弃 `@@` 例外 |
| [03 归约算法](03-reduction-algorithm.md) | 为什么不只是去重？ | 父后缀吸收子域；本地清单作为叠加层参与并集 |
| [04 发布通道](04-release-channel-and-fixed-url.md) | 下载地址为什么永远不变？ | 日期 tag + `latest` 别名 + Release 资产双通道 |
| [05 风险与边界](05-boundaries-and-risk-model.md) | 这套流水线能保证什么？ | 只有流程一致性；无签名、无摘要、无内容量下界 |

```{toctree}
:maxdepth: 1
:caption: 概念

00-overview-and-positioning
01-rule-file-format
02-upstream-digestion-pipeline
03-reduction-algorithm
04-release-channel-and-fixed-url
05-boundaries-and-risk-model
```
