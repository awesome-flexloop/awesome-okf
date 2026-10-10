---
type: Concept
title: "有效范围与迁移边界"
description: "界定 LIFT 证据能支持的结论、与相关工作的关系、许可证状态和可迁移的配对评测做法。"
status: stable
stale_after: 2026-12-31
generated: { by: "reference_agent", at: 2026-10-10T11:38:56+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-10T11:38:56+08:00 }
sources:
  - id: paper
    resource: "https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/docs/paper-neurips.md"
  - id: se-bench
    resource: "https://arxiv.org/html/2602.04811v1"
  - id: evoagentbench
    resource: "https://arxiv.org/pdf/2607.05202"
  - id: github-api
    resource: "https://api.github.com/repos/FeiZhuNiU-INFJA/LIFT"
  - id: repo-snapshot
    resource: "https://github.com/FeiZhuNiU-INFJA/LIFT/tree/9d282e415c5e3b0f65b82c8758a013b269583d93"
  - id: article-facts
    resource: "../references/article-source.md"
---

# 有效范围与迁移边界

## 结果能支持什么

当 Holdout 划分、Base/Loaded 配对、任务要求、Judge 和运行环境均有清晰记录时，LIFT 结果可以描述：在这些特定条件下，加载某种演化状态后，若干任务指标相对基线发生了什么变化。官方 suite 还说明 Holdout requirements 与 Warmup requirements 约有 75% 重合（F-028），所以正向结果应限定为该任务集构造下的加载效应，不能直接等同于对完全新要求的泛化。任务质量、资源消耗与时延应分别阅读；LIFT 的效率指标下降不能单独证明 Agent 任务能力提高，更不能从 tokens 或 latency 下降直接推出人的生产力、用户满意度或单位经济性改善。

官方论文提出的限制包括 Judge 偏差、评测环境保真度，以及不同 runtime 的绝对分数不可直接用作跨 runtime 能力排名（F-022、F-023）。因此，报告应附上失败样例和评测边界，而不是只呈现聚合名次。

## 相关研究不是同一把尺

公开预印本中已有 SE-Bench（arXiv:2602.04811v1）和 EvoAgentBench（arXiv:2607.05202）等 Agent 自进化评测相关工作（F-024、F-025）。它们的存在足以让“此前无人衡量 Agent 自我进化”的说法显得过宽；但仅凭标题和摘要也不能断言它们与 LIFT 使用同一任务定义、统计协议或指标。

更谨慎的定位是：LIFT 关注加载演化状态对 Holdout 最终任务指标的影响。相关工作应按各自论文定义分别阅读，不能拼成一张未经口径对齐的排名表。

## 许可证与复用

文章称其为开源项目，但本次检查的 GitHub API 返回 `license: null`，仓库树未见 LICENSE 文件（F-026）。所以本包将其称为公开仓库中的评测框架，**不确认代码的开源许可证，也不提供可自由复制、修改或商用的法律结论**。若要运行或复用代码，应先核实仓库后续是否补充许可证及其适用范围。

## 可迁移做法：同题配对评测

以下是从 LIFT 设计抽象出的 **L1-draft**，不是官方通用标准，也未在其他项目独立验证：

1. 把“学习/演化阶段”与“最终测试阶段”分开，预先冻结测试集。
2. 对照条件与处理条件使用相同的 Holdout 任务和判分规则。
3. 记录加载状态的来源、版本和隔离方法。
4. 预先确定重复次数与主要指标，保留两种条件的原始结果。
5. 把效应量、区间、失败样例、Judge 与环境限制一起报告。

可将它用于比较检索知识、技能包、策略文件或规则集加载前后的系统表现，前提是任务与环境足够可比。**不要**把它用于跨产品绝对能力排名，也不要把训练题充当 Holdout、只报最好一次或把代理指标直接解释为业务成效。

## 复核触发器

当 LIFT 仓库新增许可证、排行榜生成时间更新、论文发布新版本、任务数量或评测协议变化时，重新核验本页及 bundle 的 `flagged` 状态。当前资料时点为 2026-10-10。
