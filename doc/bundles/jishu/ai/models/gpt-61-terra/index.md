---
okf_version: "0.2"
type: bundle
title: GPT-6.1 Terra 模型能力与任务选型教程
description: 从 Tibo Day 22 原帖与官方发布资料学习 Terra 的自然写作、视觉电脑操作、API 和成本边界；技术综述型教程，非已实测操作教程。
tags: [openai, gpt-6-1-terra, computer-use, visual-reasoning, writing, model-selection, token-cost]
generated: { by: "reference_agent/okf-wiki", at: "2026-10-27" }
status: draft
stale_after: 2026-11-27
source: https://x.com/thsottiaux/status/2114800277677092936
sources:
  - id: tibo
    resource: https://x.com/thsottiaux/status/2114800277677092936
  - id: launch
    resource: https://openai.com/index/introducing-gpt-6-1-terra/
  - id: model
    resource: https://developers.openai.com/api/docs/models/gpt-6.1-terra
  - id: facts
    resource: references/article-source.md
---

# GPT-6.1 Terra 模型能力与任务选型教程

GPT-6.1 Terra 的官方定位结合视觉推理、电脑操作和自然写作；API 名称为 `gpt-6.1-terra`。[F-008、F-013] Tibo 的 Day 22 原帖强调表达与请求理解，并给出相较 Sol 的“2X more usage”说法。[F-003、F-005]

**本束为技术综述型学习教程，保持 draft。** 价格与接口声明已回源核对，但“2X”的精确权益规则、独立成效实验与系统卡细项仍未取得。官方自报评测不等于本束复测。[F-011、F-045]

## 快速导航

| 读者问题 | 阅读位置 |
|---|---|
| Terra 适合什么任务，能否替代强模型 | [发布定位](concepts/00-positioning.md) |
| 支持什么模态、端点和工具 | [能力与 API 边界](concepts/01-capabilities.md) |
| 2X、降价与限速有什么区别 | [价格与额度](concepts/02-economics.md) |
| 如何解读分数并设计自己的试验 | [任务评估](concepts/03-task-evaluation.md) |
| 能提炼哪些可迁移方法 | [候选选型模式](concepts/04-selection-pattern.md) |
| 每条事实的来源与核验状态 | [45 条编号事实](references/article-source.md)、[核验记录](references/verification.md) |

## 证据与使用边界

- 采集日为 2026-10-27；X 页面时间没有时区，官网出版时间未取得。[F-006]
- 原帖、官方发布文与模型参考属于同厂商相关证据，不能计为三个独立实验。
- 本束不提供真实套餐可用次数、不承诺吞吐翻倍，不把内部评测错误率作为业务错误率。
- Computer use 是工具能力；原生模态仍为文本和图像输入、文本输出，音视频不支持。[F-018、F-024]
- 本次未调用真实 API、未操作测试桌面，也未转写引用视频。没有可复现且已实测的源文步骤，因此不设 `examples/`。
- 采用子项目轻量规范，F 编号只在信源台账维护一次，避免双份事实漂移；不创建主仓规划资产、不自动提交。
- 价格、接口、用量政策在 2026-11-27 前复核；安全系统卡取得后再补独立核验记录。

## 主题关联

[VISTA 视觉原生 Harness](../vista-visual-harness/index.md)讨论视觉 Agent 的观测和记忆组织，本束讨论具体模型的发布声明与任务选型；[分块 KV Cache 相位敏感性](../phase-sensitive-kv-cache/index.md)讨论长上下文检索可靠性，本束不把上下文容量上限当作检索质量保证。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
