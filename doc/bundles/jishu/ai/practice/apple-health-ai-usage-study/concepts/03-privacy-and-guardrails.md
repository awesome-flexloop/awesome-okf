---
type: concept
title: 03 · 隐私架构、安全护栏与非诊断边界
description: 不训练模型、可选 HealthKit 与问卷、安全措施、令人担忧问题的转介护栏、非诊断声明，以及媒体单源细节的降级处理
tags: [apple, health-ai, privacy, healthkit, guardrails, safety, non-diagnostic]
generated:
  by: workbuddy/seven-concepts-cmd
  at: "2026-11-17T12:30:00+08:00"
status: stable
stale_after: 2027-05-17
sources:
  - id: apple-newsroom-2026-11-15
    resource: https://www.apple.com/newsroom/2026/11/apple-launches-research-study-to-explore-the-use-of-ai-for-health/
    title: Apple Newsroom 官方公告（2026-11-15 UPDATE）
  - id: macrumors-2026-11-16
    resource: https://www.macrumors.com/2026/11/16/apple-seeks-200000-people-for-ai-health-study/
    title: MacRumors 报道（媒体单源细节的唯一直接出处）
---

# 03 · 隐私架构、安全护栏与非诊断边界

健康数据是最敏感的一类个人信息。官方稿在这一段给出的承诺密度最高，也最需要逐句区分「官方写了」与「媒体补了」。

## 官方一手承诺（可直接引用）

| # | 官方表述 | 事实编号 |
|---|----------|----------|
| 1 | 研究从设计之初即含隐私保护、透明性与临床护栏（privacy protections, transparency, and clinical guardrails） | F-029 |
| 2 | **研究数据不会用于训练 AI 模型** | F-030 |
| 3 | 参与者保留是否分享任何 HealthKit 指标或问卷回答的控制权 | F-031 |
| 4 | Apple 已实施安全措施，保护其持有的研究数据及参与者信息的机密性 | F-032 |
| 5 | 研究 App 设安全护栏，用于检测某些令人担忧的问题，并在需要时建议参与者向医疗服务者或其他资源跟进 | F-033 |
| 6 | 研究 App 不用于诊断或治疗任何状况，不替代医疗专业人员的建议；健康问题应咨询医生或临床人员 | F-034 |

第 1～4 项构成**数据侧**边界，第 5～6 项构成**能力侧**边界。两者合起来才是完整的风险隔离：既限制数据怎么用，也限制回答能被当成什么。

## 媒体单源细节（本束降级处理）

以下两条在多篇报道中流传，但**未出现在 Apple 官方稿**中，本束只在事实清单登记，不写入任何结论性表述：

| 媒体说法 | 出处链 | 本束处置 |
|----------|--------|----------|
| 问题在送达 OpenEvidence 前经去标识化处理 | MacRumors（S4）直接报道 | 登记为 F-035，标「媒体单源、官方未证实」 |
| OpenEvidence 在 24 小时内删除问答数据 | MacRumors（S4）；另有报道称该细节源自 CNET、经 9to5Mac 转引（S5） | 登记为 F-036，标「媒体单源 + 二手转引」 |

> ⚠️ **教学要点**：「多家媒体都写」不等于「官方确认」。当多家报道共享同一原始出处时，它们仍只算**一个独立信源**。判读练习见 [examples/01](../examples/01-claim-verification-drill.md)。

另有媒体给出研究时长约 12 个月、基线/月度问卷、独立审查委员会（IRB）监督、KFF 调查引用等细节（S9）。这些同样未见于官方稿与官方研究网站，本束列入 [未披露项登记](../references/verification.md)，不用于支撑任何结论。

## 保守写法与开放问题

官方稿没有公开：触发护栏的具体问题清单、介于「常规」与「紧急」之间的问题如何处理、端到端数据流向、留存期限、撤回机制、是否有补偿（S8 亦指出这几项缺失）。研究类 App 的这些细节通常写在知情同意文件里，读者若参与应以 App 内官方文件为准——**本束不替官方补答案**。

## 与本知识库惯例的呼应

这套「官方承诺 / 媒体单源 / 未披露项」三分法，与同组 [u2flash-free-month](../../u2flash-free-month/index.md) 处理「厂商自述」的方式同源：核心声明经一手核验，非核心但流传广的说法保留口径并显式降低强度，不给它结论地位。
