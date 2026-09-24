---
okf_version: "0.2"
type: reference
title: references 索引
description: qbs-book-to-skill bundle 参考信源——博文事实清单与 P0 核验报告
tags: [qbs, references, index]
---

# references/ 索引

本目录存放博文原文的事实采集与 P0 权威核验记录，是 bundle 内全部具体声明的出处。

## 文档列表

| 文档 | 说明 |
|------|------|
| [article-source.md](article-source.md) | 博文原文事实清单（F-001 至 F-056，含 R 阶段核验补充事实） |
| [verification.md](verification.md) | P0 权威核验报告（7 项 P0、3 则勘误、勘误四张清单过筛记录） |

## 使用约定

- 正文所有数字、术语、命令、组织与人物背景均以 F 编号回指本目录，禁止出现 F 编号之外的编造。
- 三则勘误在正文一律呈现**核实后的正确值**，源文口径留档于 [verification.md](verification.md)：
  - F-047（Time Craters 计量口径）
  - F-048（切换成本数字）
  - F-054（Jake Knapp 任职范围）

```{toctree}
:hidden:
:maxdepth: 2

article-source
verification
```