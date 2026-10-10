---
type: Concept
title: "排行榜数字如何解读"
description: "拆解 LIFT 的效率指标、delta 方向、重复试验与榜单快照日期，防止把相对变化误读为绝对排名。"
status: stable
stale_after: 2026-12-31
generated: { by: "reference_agent", at: 2026-10-10T11:38:56+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-10T11:38:56+08:00 }
sources:
  - id: leaderboard
    resource: "https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/docs/leaderboard.json"
  - id: leaderboard-script
    resource: "https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/scripts/build_leaderboard.py"
  - id: paper
    resource: "https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/docs/paper-neurips.md"
  - id: article-facts
    resource: "../references/article-source.md"
---

# 排行榜数字如何解读

LIFT 公布的效率维度包括 turns、tools、tokens 和 latency 等。排行榜按同一 runtime 的 Loaded 与 Base 汇总值计算相对变化：

```text
delta = (sum(Loaded) - sum(Base)) / sum(Base) * 100
```

该公式来自官方榜单构建脚本，聚合的是配对 Holdout task-repeats 的 Loaded 与 Base 结果（F-018、F-019）。对于这些数值越低越好的成本/时延指标，负 delta 表示 Loaded 条件下该项数值低于 Base（F-020）。这不是能力越低的意思，也不能单凭负 delta 推出整体 Agent 更优秀。

## 报告中的统计信息

官方排行榜 JSON 列出 11 个 runtime，并声明 `n_repeats=10` 和 95% confidence interval（F-009、F-010）。但每个 runtime 条目还列出 274–280 个 `paired_task_repeats`，这是任务重复配对数；不要把两个层级的数量混成一个样本数（F-029）。

点估计与区间的计算口径也不同：点估计先汇总配对 task-repeat 的 Loaded 与 Base 指标，再代入上方公式；脚本则先按每个 repeat 计算比例变化，以这些 repeat 级变化的均值和总体标准差（`ddof=0`）做正态近似，计算 `mean ± 1.96 × std / sqrt(n_repeats)`。当区间上界低于零时，脚本将该指标标记为显著下降（F-019、F-021）。这一区间不是对 274–280 个配对任务逐一计算的同一估计量，报告时应同时说明口径。

`turns` 字段映射到运行记录中的 `trials`，表示一个任务内 work Agent 与 Judge 的实际交互轮数，直到任务成功或达到上限；它不是普通聊天产品中的用户对话轮次（F-030）。

论文页面另报告 11 runtimes、14 scenes、84 tasks，同时将当前材料描述为 v1 preprint 和 partial cross-runtime sweep（F-011、F-012）。

这些数字回答的是“当前材料声称覆盖了什么”，不自动证明每个 runtime 都有相同完整度，也不把统计区间变成业务效果保证。跨 runtime 的绝对分数不宜直接比较，论文也明确提示了这一限制（F-023）。

## 快照时点不可省略

排行榜 JSON 的 `generated_at` 为 **2026-08-23 15:14:31 UTC**；微信公众号文章页面显示日期为 **2026-10-09**（F-004、F-008）。因此该 JSON 是早于文章约七周的数据快照，不能当成文章发布当天的最新成绩。项目仓库后续更新也不意味着这份 JSON 自动更新。

引用一条榜单结果时，至少同时记录：

- runtime、Base 与 Loaded 的原始值；
- 指标定义及 delta 方向；
- Holdout 任务范围、重复次数和区间；
- JSON 的生成时点与论文版本/覆盖状态。

若只展示经过排序的 delta，就隐藏了基线大小、样本覆盖和结果不确定性。可逐项回查[来源台账](../references/source-manifest.md)和[核验报告](../references/verification.md)。
