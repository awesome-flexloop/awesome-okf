---
okf_version: "0.2"
type: bundle
title: "WorkBuddy 全媒体内容系统"
description: "商业分析/战略资讯：从一篇个人实战文章抽取内容流水线、中台、经验飞轮和一鱼多吃模型。非操作教程。"
tags: [WorkBuddy, AI商业化, 自媒体, 内容系统, 一人公司, 经验飞轮]
generated: { by: "reference_agent/blog-article-to-okf-wiki", at: "2026-09-20T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20T00:00:00Z" }
status: flagged
stale_after: "2026-12-31"
sources:
  - id: article
    resource: "/references/article-source.md"
  - id: verification
    resource: "/references/verification.md"
  - id: blog
    url: "https://mp.weixin.qq.com/s/8sPIOE2fyGPfzYP6T7Ziaw"
---

# WorkBuddy 全媒体内容系统

> **⚠️ flagged：** 本包是对作者个人实战叙述的结构化学习，不是 WorkBuddy 官方教程。日更数量、经营履历、成本、胜率和变现结果均未由独立证据确认。

这是一个**商业分析/战略资讯知识包，非操作教程**。文章的可迁移价值在于把内容业务拆成三层：

- **流水线**：将写作拆成工序，围绕关键路径分配模型质量；
- **中台**：集中管理目标、选题、排期、数据、客户和经验；
- **飞轮**：把爆款拆解和平台数据回流到下一轮生产。

## 阅读路径

1. [三层系统：流水线、中台与飞轮](concepts/00-system-architecture.md)
2. [内容流水线与模型路由](concepts/01-content-pipeline-and-model-routing.md)
3. [经验飞轮与一鱼多吃](concepts/02-closed-loop-and-multiplication.md)
4. [边界、评价与反模式](concepts/03-boundaries-and-evaluation.md)
5. [原文事实清单](references/article-source.md) → [核验报告](references/verification.md)

## 已知边界

- 原文未提供 WorkBuddy 版本、安装、配置、接口、输入输出或运行日志，因此不设置 `examples/`。
- “17 道工序”“11 个模块”“8 个分身”是作者对其系统的描述，不等于产品默认功能。
- “成本几乎为零”“胜率更高”“八处变现”等属于作者观点或自述，不构成收益承诺。
- 模型、平台接口和政策具有时效性，建议在 `stale_after` 前复核。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
