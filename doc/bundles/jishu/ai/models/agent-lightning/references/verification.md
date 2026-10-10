---
okf_version: "0.2"
type: Reference
title: "Agent Lightning v1.0 博文 P0 核验报告"
description: "对 AINLP 博文《微软开源 Agent Lightning v1.0》的 P0 权威核验记录——10 项关键声明官方核验全通过，无源文硬错误，F-046 硬件型号标注单源待复核。"
tags: [agent-lightning, 核验, P0, harnessed-agentic-rl]
generated: { by: "reference_agent/deepseek-v4", at: "2026-10-10" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-10" }
status: stable
stale_after: 2026-12-31
sources:
  - id: official-blog
    url: "https://www.microsoft.com/en-us/research/blog/agent-lightning-v1-0-a-3500-line-lightweight-agentic-rl-framework-for-training-agents-with-real-harnesses/"
  - id: arxiv
    url: "https://arxiv.org/abs/2608.17528"
  - id: github
    url: "https://github.com/microsoft/agent-lightning"
---

# Agent Lightning v1.0 博文 P0 核验报告

> 核验方法：对博文中可验证的关键声明（成败数字、时间线、术语、发布事实）逐项对微软官方来源交叉核验。**未发现源文硬错误**（勘误为零）；F-046 硬件型号未直接核到官方原句，标注单源待复核。

## P0 核验结论表

| F 编号 | 核验对象 | 权威来源 | 结论 |
|--------|---------|---------|------|
| F-001 | Agent Lightning v1.0 由微软开源 | 微软官方博客 / GitHub | ✅ 通过 |
| F-008 | v1.0 将训练接到现成 harness 的模型接口 | 官方博客 | ✅ 通过 |
| F-009 | 约 6,000 个训练任务训练 Qwen3.5-9B | 官方博客（"about 6,000 training samples"） | ✅ 通过 |
| F-010 | SWE-bench Verified Pass@1 41.8%→56.4% | 官方博客 + chatpaper + neoteo | ✅ 通过 |
| F-011 | 提升 14.6 个百分点 | 官方博客（"14.6 percentage point gain"） | ✅ 通过 |
| F-012 | 微软亚洲研究院 10 月 7 日博客 | 官方博客（Published October 7, 2026, Microsoft Research Asia） | ✅ 通过 |
| F-013 | v1.0 及技术报告 8 月公开 | 官方博客 + MIT 发布信息 | ✅ 通过 |
| F-014 | 称为 Harnessed Agentic RL | arXiv 2608.17528 副标题/正文 | ✅ 通过 |
| F-041 | Collocated Async RL 约 2 倍端到端加速 | 官方博客（"about a 2x end-to-end speedup over synchronous RL"） | ✅ 通过 |
| F-044 | 约 3,500 行代码 | 官方博客标题（"3,500-Line"） | ✅ 通过 |
| F-046 | 最小 Calc-X 用一张 A100、Qwen3.5 编码示例用四张 B200 | 官方文档未直接核到原句 | ⚠️ 仅博文单源，待复核 |

## 勘误四张清单

### ① 日期/版本表

| 项 | 博文口径 | 官方口径 | 结论 |
|----|---------|---------|------|
| 博客发布时间 | 10 月 7 日 | 2026-10-07 | ✅ 一致 |
| v1.0/报告公开时间 | 8 月 | 2026-08（MIT license 发布） | ✅ 一致 |
| 模型 | Qwen3.5-9B | Qwen3.5-9B | ✅ 一致 |

### ② 成效数字溯源表

| 项 | 博文数值 | 官方出处 | 结论 |
|----|---------|---------|------|
| SWE-bench Pass@1 | 41.8% → 56.4% | 官方博客 | ✅ 有出处 |
| 提升 | +14.6 pp | 官方博客 | ✅ 有出处 |
| 训练样本 | 约 6,000 | 官方博客 | ✅ 有出处 |
| 加速 | 约 2×（官方实验） | 官方博客 | ✅ 有出处（限官方实验口径） |
| 代码量 | 约 3,500 行 | 官方博客标题 | ✅ 有出处 |

### ③ 口径对照表

- "约 6,000 训练样本""约 2 倍加速""约 3,500 行"均带"约/官方实验"限定词，正文沿用该口径，未当作普适性能承诺。
- F-046 硬件型号（A100/B200）标注"博文所述/待复核"，因官方型号原句未直接核到。

### ④ 引文逐字核对表

- 博文为综述性转述，无直接引号引文；关键术语（Harnessed Agentic RL、Collocated Async RL、rollout、agent harness）与官方一致，无意译加引号问题。
- 报告来源为《Agent Lightning v1.0: Towards Harnessed Agentic RL》（arXiv 2608.17528，微软团队），身份清晰，无厂商赞助未披露问题。

## 信源距离与状态结论

- 信源距离：**第三方综述**（AINLP 转载，作者 NLPerNLPer 对微软官方开源的综述解读，非厂商自宣、非一手实测）。
- 成效数字非厂商自宣营销数据，全部能溯源到微软官方实验口径，无营销污染风险。
- 核心声明（F-001/F-010/F-041/F-044）全部官方核验通过，无 flagged 触发。
- **状态：stable**。

## 未核验项（仅博文单源）

- F-046 硬件型号（A100/B200）：标注"博文所述/待复核"，stale_after（2026-12-31）前建议复核。
- 多数机制类条目（F-016~F-043 中 P1/P2 项）为博文叙述，辅以官方概念核验，属单源范畴，正文引用时提示甄别。