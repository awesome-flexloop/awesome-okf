---
type: Reference
title: "GPT-6 Sol 与 GPT-6 Luna 官方核验报告"
description: "核验价格、模型定位、DeepSeek 对照口径和文章中的 benchmark/成效数字边界。"
tags: [gpt-6, verification, pricing, benchmark]
generated: { by: "reference_agent/trae", at: "2026-09-23T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T12:00:00+08:00" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/1190GW6WFZIzZ8YkDD44eg?from=industrynews&color_scheme=light#rd
  - id: openai
    resource: https://openai.com/index/introducing-gpt-6-sol-and-luna/
  - id: deepseek-pricing
    resource: https://api-docs.deepseek.com/quick_start/pricing
  - id: deepseek-release
    resource: https://deepseek.com/en/news/deepseek-v4-1-flash/
  - id: azure
    resource: https://azure.microsoft.com/en-us/blog/gpt-6-astra-sol-and-luna-for-production-agents-in-microsoft-foundry/
---

# GPT-6 Sol 与 GPT-6 Luna 官方核验报告

## 核验结论

| 核验项 | 结果 | 事实编号 |
|---|---|---|
| Sol/Luna 已发布 | ✅ OpenAI 官方发布页确认 | F-003 |
| API 价格 `$2/$10`、`$0.10/$0.50` | ✅ OpenAI 官方发布页确认 | F-004—F-006 |
| Sol/Luna 的任务分工 | ✅ OpenAI 与 Microsoft Foundry 资料口径一致 | F-007、F-008 |
| DeepSeek V4.1 Flash 为 1M 上下文并支持峰谷/缓存定价 | ✅ DeepSeek 官方资料确认 | F-009—F-011 |
| GPT-6 缓存读取 90% 折扣 | ⚠️ 官方发布口径；实际账单需按工作负载验证 | F-019 |
| benchmark 分数与竞品成本比例 | ⚠️ 厂商自述/文章转述，未独立复算 | F-013—F-016 |
| 内部错误率与研究人员 token 消耗 | ⚠️ 厂商内部统计，外部不可复核 | F-017、F-018 |
| Three.js 与视觉质量评价 | ⚠️ 实测样本，不代表总体能力 | F-024 |

## 勘误与口径

1. 文章把 DeepSeek V4.1 Flash 的价格换算成“人民币每百万 token”进行直观对比；正式选型应直接使用官方价表，并同时记录币种、峰谷时段、缓存状态和输入/输出方向。
2. 文章中的“低 60%—96%”“约 1% 成本”“错误减半”等数字未在本次核验中获得独立复算，不进入正文的确定性结论。
3. benchmark 的分数必须连同模型版本、推理强度、提示词、工具和评测日期保存；不同配置之间不可直接横比。

## 审查记录

- G1：事实、厂商声明、第三方实测和作者观点已分层。
- G2：洞察围绕价格、任务成本和选型边界组织。
- G3：抽取的任务成本评估模式可迁移到其他模型/Agent 平台。
- G4：本任务为知识包生成，无代码行动项；索引与 toctree 作为交付验收项。
