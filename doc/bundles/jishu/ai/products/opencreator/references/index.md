---
okf_version: "0.2"
type: references-index
title: "OpenCreator 参考层目录"
description: "信源登记、事实清单、P0 核验报告与知识地图"
tags: [opencreator, references, index]
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/oecbF0OUAKYSZfbI6WsKfA"
    title: "1.2万 Star 爆火，来看看这款顶级的一站式 Agent 创作神器"
    account: AI开源无界
  - id: github-repo
    url: "https://github.com/krillinai/OpenCreator"
    title: "OpenCreator (formerly KrillinAI) README"
---

# OpenCreator 参考层目录

> 本 bundle 的溯源层：逐条事实、P0 核验、信源登记与知识地图。

## 参考文档

1. [信源登记（source-manifest）](source-manifest.md)——账号归属、公开性预检、访问时点。
2. [事实清单（facts）](facts.md)——F-001~F-055，区分 page_fact 与 author_claim。
3. [P0 核验报告（verification）](verification.md)——24 项 P0 核验：18✅ / 5⚠️ / 1❌(数值存疑)。
4. [知识地图（knowledge-map）](knowledge-map.md)——事实层 / 机制层 / 迁移层三层。

```{toctree}
:maxdepth: 2

source-manifest
facts
verification
knowledge-map
```