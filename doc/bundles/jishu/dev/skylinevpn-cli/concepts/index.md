---
okf_version: "0.2"
type: Concept
title: "skylinevpn-cli 概念层索引"
description: "从定位、产品面、发行拓扑到信任模型的七篇概念文档导航"
---

# 概念层索引

> 先读 [00 定位](00-overview-and-positioning.md)：它决定你用哪条路线读后面六篇。

| 篇目 | 回答的问题 | 关键结论 |
|------|-----------|---------|
| [00 定位与全景](00-overview-and-positioning.md) | 这个仓库是什么？仓库里有什么？ | 公开的**发行仓**，不是产品源码仓 |
| [01 产品面](01-product-surface.md) | 命令怎么用？支持哪些平台？ | 四类命令 + 两种模式 + 安装/更新/卸载三段生命周期 |
| [02 发行拓扑](02-distribution-topology.md) | 三个 CI 束如何变成一个 Release？ | `dist/<tag>` 是唯一发布单元；`latest` 与 `tag` 双寻址 |
| [03 安装期校验链](03-installer-verification-chain.md) | 安装器在用户机器上做了什么？ | 架构检测 → 内嵌哈希校验 → 服务安装 → 语言 |
| [04 暂存管线](04-release-staging-pipeline.md) | `build_release.py` 凭什么可信？ | 命中数断言 + 自洽重写 + 递归泄漏扫描 |
| [05 身份与泄漏门](05-identity-and-leak-gates.md) | 谁可以发布？什么内容会被拦？ | 三层门禁；作者与平台提交者分离 |
| [06 信任模型与边界](06-trust-model-and-boundaries.md) | 这条链能证明什么？ | 有完整性，无签名，不抗发布方失陷 |

```{toctree}
:maxdepth: 1
:caption: 概念

00-overview-and-positioning
01-product-surface
02-distribution-topology
03-installer-verification-chain
04-release-staging-pipeline
05-identity-and-leak-gates
06-trust-model-and-boundaries
```
