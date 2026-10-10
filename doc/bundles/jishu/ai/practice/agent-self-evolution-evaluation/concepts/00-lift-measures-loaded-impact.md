---
type: Concept
title: "LIFT 衡量的是什么"
description: "从 Agent 自我进化的宽泛说法收敛到 LIFT 的具体测量对象：加载演化产物后，Holdout 最终任务指标如何变化。"
status: stable
stale_after: 2026-12-31
generated: { by: "reference_agent", at: 2026-10-10T11:38:56+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-10T11:38:56+08:00 }
sources:
  - id: blog
    resource: "https://mp.weixin.qq.com/s/2I_eem6KwJ3hKeM9nyHSBg?from=industrynews&color_scheme=light#rd"
  - id: repo
    resource: "https://github.com/FeiZhuNiU-INFJA/LIFT"
  - id: benchmark
    resource: "https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/docs/benchmark-intro.md"
  - id: article-facts
    resource: "../references/article-source.md"
---

# LIFT 衡量的是什么

“Agent 会不会越用越聪明”是一个宽问题。LIFT 把它收窄为一个可测问题：在相同的 Holdout 最终任务上，Agent 加载此前演化产生的状态后，任务表现或资源消耗相对未加载状态发生了什么变化。仓库描述将 LIFT 展开为 “Loaded Impact on Holdout Final Task”；论文标题则使用 “Loaded Impact on Final Task”，省略 Holdout 一词（F-007、F-027）。引用缩写时应保留这一来源差异，而不要把某个版本说成唯一官方写法。

这一区分很重要。LIFT 的 delta 表示**加载产物带来的相对变化**，并非 Agent 的绝对能力分数。不同 runtime 的绝对分数也不应被直接排成一个能力榜（F-019、F-020、F-023）。

## 术语

| 术语 | 本包中的含义 |
|---|---|
| Warmup | 用于 Agent 学习或产生可加载状态的阶段。 |
| Holdout | 与 Warmup 分开的最终评测任务集。 |
| Base | 未加载该次演化产物的对照条件。 |
| Loaded | 加载演化产物后执行同一 Holdout 任务的条件。 |
| Delta | Loaded 相对 Base 的指标变化；对低值更好的效率指标，负值表示数值下降。 |

这些定义描述 LIFT 的评测语境，不意味着所有 Agent 自我改进系统都采用相同术语或机制。术语与流程依据官方基准文档登记，见[事实索引](../references/article-source.md)。

## 适合回答的问题

LIFT 可以帮助研究者检查：某种演化状态在给定 Holdout 任务、runtime、Judge 和环境中，是否改变了最终任务指标。它本身不能单独回答“哪个 Agent 最聪明”“用户生产力是否提高”或“对所有真实场景是否有效”。

文章将领域中统一衡量方式不足作为背景主张（F-005）。已有 SE-Bench 与 EvoAgentBench 等相关研究，因此更稳妥的表述是：LIFT 提供了一种特定的加载效应测量设计，而不是该方向此前无人研究（F-024、F-025）。

## 延伸阅读

- [配对 Holdout 协议](01-paired-holdout-protocol.md)
- [排行榜数字如何解读](02-reading-leaderboard.md)
- [有效范围与迁移边界](03-limitations-and-transfer.md)
