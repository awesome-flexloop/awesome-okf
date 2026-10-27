---
okf_version: "0.2"
type: bundle
id: gpt-61-sol
title: GPT-6.1 Sol 模型与任务评估教程
description: 从官方模型参考、发布评测、系统卡和 Asana 案例学习 Sol 的 API、缓存、电脑操作与任务选型；技术综述型教程，非已实测接入。
tags: [openai, gpt-6-1-sol, responses, computer-use, prompt-cache, model-evaluation]
generated: { by: "reference_agent/okf-wiki", at: "2026-10-27" }
status: draft
stale_after: 2026-11-27
source: https://developers.openai.com/api/docs/models/gpt-6.1-sol
sources:
  - id: model
    resource: https://developers.openai.com/api/docs/models/gpt-6.1-sol
  - id: launch
    resource: https://openai.com/zh-Hans-CN/index/introducing-gpt-6-1-sol/
  - id: asana
    resource: https://asana.com/inside-asana/cut-browsers-agent-cost
  - id: facts
    resource: references/source-inventory.md
---

# GPT-6.1 Sol 模型与任务评估教程

GPT-6.1 Sol 面向复杂编码、电脑操作和专业工作，官方强调以更低成本接近 Astra；API 名为 `gpt-6.1-sol`。[F-001、F-002] 官方评测与 Asana 案例提供了任务、档位和工作流的比较证据，不能替代真实业务验收。

**本束保持 draft。** 83 条编号项记录来源声明与采集观察，包含缓存计费/TTL 和限速档位的冲突；没有执行真实 Sol API 或电脑操作，系统卡后半、当前账户权益与独立 Sol 复测仍有缺口。所有成效数字均保留发布方与样本限定。

## 按问题阅读

| 读者问题 | 页面 |
|---|---|
| Sol 是什么，产品入口与模型有什么区别 | [定位与学习路径](concepts/00-overview.md) |
| 支持什么端点，如何迁移请求与状态 | [API 与迁移](concepts/01-api-and-migration.md) |
| 缓存能省什么，如何看长上下文和账单 | [价格与缓存](concepts/02-pricing-and-cache.md) |
| 电脑操作由谁执行，如何限制与验收 | [电脑操作与安全](concepts/03-computer-use-and-safety.md) |
| 官方跑分和 76 倍降本能说明什么 | [评测与 Asana 案例](concepts/04-benchmarks-and-case-study.md) |
| 如何设计自己的模型与工作流对照 | [3 条洞察与候选评估模式](concepts/05-insights-and-evaluation.md) |
| 数字来自哪里，哪些口径仍冲突 | [83 条编号台账](references/source-inventory.md) |
| 审查和校验是否完成 | [审查记录](references/adversarial-review.md)、[执行日志](log.md) |

## 方法论与证据边界

场景 4 知识沉淀，session `sc-20261027-gpt-61-sol`，链路 R→I→E→V；C 等用户明确授权，不自动提交或推送。事实集中在台账，3 条四元组洞察与“任务账单对拍”模式集中在评估页；模式为 L1-draft，跨域迁移是设计而非实测。

API 参考、发布文和系统卡属于同厂商证据；Asana 原文与 OpenAI 案例页属于同一次实验。DeepSWE 官网只核对基准方法，本次可见榜单没有取得 Sol6.1 条目，不能据此称第三方已复测。[F-081]

模型原生输入文本/图像、输出文本；工具生成图像不等于原生图像输出。[F-006、F-011、F-047] 一百万 token 容量不等于长上下文可靠性，缓存折扣不等于整任务成本降幅，completed 不等于业务保存成功。

采集日为 2026-10-27，复查截至 2026-11-27；遇接口、价格、产品权益或型号变化提前复查。存在参数文档冲突，故不设置伪装成已实测步骤的 `examples/`。本束按子项目自治规范放在 models 分类，不创建主仓治理资产。

## 关联学习

[GPT-6.1 Terra](../gpt-61-terra/index.md)侧重自然写作与视觉任务定位，不能把其权益声明直接套用 Sol。[VISTA 视觉原生 Harness](../vista-visual-harness/index.md)讨论观察和历史组织，可与本束 Asana 案例对读；[分块 KV Cache 相位敏感性](../phase-sensitive-kv-cache/index.md)讨论检索可靠性，本束讨论具体模型接口与任务评估。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
