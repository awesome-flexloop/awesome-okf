---
type: Reference
title: "LIFT 关键声明核验与对抗审查"
description: "记录关键数字、开源属性、领域定位及四视角审查结论，明确可证范围与未决项。"
status: stable
stale_after: 2026-12-31
generated: { by: "reference_agent", at: 2026-10-10T11:38:56+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-10T11:38:56+08:00 }
sources:
  - id: blog
    resource: "https://mp.weixin.qq.com/s/2I_eem6KwJ3hKeM9nyHSBg?from=industrynews&color_scheme=light#rd"
  - id: repo
    resource: "https://github.com/FeiZhuNiU-INFJA/LIFT"
  - id: leaderboard
    resource: "https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/docs/leaderboard.json"
  - id: leaderboard-script
    resource: "https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/scripts/build_leaderboard.py"
  - id: paper
    resource: "https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/docs/paper-neurips.md"
  - id: suite
    resource: "https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/assets/suite_requirement.md"
  - id: repo-snapshot
    resource: "https://github.com/FeiZhuNiU-INFJA/LIFT/tree/9d282e415c5e3b0f65b82c8758a013b269583d93"
  - id: se-bench
    resource: "https://arxiv.org/html/2602.04811v1"
  - id: evoagentbench
    resource: "https://arxiv.org/pdf/2607.05202"
  - id: github-api
    resource: "https://api.github.com/repos/FeiZhuNiU-INFJA/LIFT"
---

# 核验结论

## P0 核验表

| 声明 | 核验结果 | 证据与处理 |
|---|---|---|
| 文章把 LIFT 描述为开源项目 | **未能确认，核心声明待核** | GitHub API 返回 `license: null`，检查的仓库树未见 LICENSE 文件（F-026）。公开可读源码仓库不自动等于已授予开源许可证。Bundle 标记 `status: flagged`；正文只称“公开仓库中的评测框架”，不建议据此复用代码。 |
| Agent 自我进化此前几乎无人衡量 | **范围过宽，已收窄** | SE-Bench 与 EvoAgentBench 均有早于本文的公开预印本记录（F-024、F-025）。这些工作不代表与 LIFT 任务和指标相同；正文将贡献限定为 LIFT 所采用的 Loaded 对 Holdout Final Task 配对指标，不作“首次/唯一”判断。 |
| 排行榜反映文章发布时的最新结果 | **不成立为当前性表述** | JSON 的 `generated_at` 是 2026-08-23 15:14:31 UTC，早于文章页面日期 2026-10-09（F-004、F-008）。正文把它作为有日期的静态快照，不写成 10 月最新成绩。 |
| 排行榜包含 11 runtimes、10 repeats 和 95% CI | **官方材料支持，需区分统计层级** | JSON 列出 11 个 runtime，声明 `n_repeats=10` 和 95% CI；条目另显示 274–280 个 `paired_task_repeats`（F-009、F-010、F-029）。两类数字不可混作同一层样本数，数据仍属项目自有口径。 |
| 论文报告 11 runtimes、14 scenes、84 tasks，结果是完整最终评测 | **数字支持，结论需限定** | 官方论文页面列出这些覆盖数，同时自述 v1 preprint 与 partial cross-runtime sweep（F-011、F-012）。不可把部分扫描描述成最终全量结果。 |
| 负 delta 表示 Loaded 条件改善 | **公式方向支持，不能单独代表总体能力** | 脚本以配对 task-repeats 的 Loaded 与 Base 指标总和差除以 Base 总和计算聚合 delta（F-019、F-020、F-029）。对 turns/tools/tokens/latency 等“越低越好”的指标，负值表示该指标下降；不等同于跨 runtime 的绝对能力排名。 |
| 榜单 CI 与聚合 delta 是同一估计量，且显著标记证明普遍改善 | **不成立** | 点估计对配对任务观测求和后计算比例；CI 则按 repeat 级比例变化，以总体标准差（ddof=0）和正态近似计算 `mean ± 1.96 × std / sqrt(n_repeats)`。当 CI 上界低于零时脚本标记显著下降（F-019、F-021、F-029）。两者聚合层级不同；论文仍报告 partial sweep，统计标记不消除任务、Judge 或环境偏差。 |
| `turns` 是用户聊天轮次 | **与官方字段语义不符** | 构建脚本将 leaderboard 的 `turns` 映射到 `trials`；运行时代码把任务内 work Agent 与 Judge 的交互计为 turns，直到成功或达到上限（F-030）。教程已明确它不是普通聊天产品的用户对话轮次。 |
| Holdout 代表与 Warmup 完全不重叠的要求空间 | **不成立** | 官方 suite 文档称 Holdout 与 Warmup requirements 约有 75% 重合，其余为变体或矛盾要求（F-028）。正文已区分任务保留与要求域完全未见。 |
| LIFT 缩写只有一种官方展开 | **存在来源措辞差异** | 仓库描述使用 “Loaded Impact on Holdout Final Task”，论文标题使用 “Loaded Impact on Final Task”（F-007、F-027）。正文并列记录，不裁定唯一写法。 |
| 微信文章的 07:03 时间可换算为特定时区 | **页面证据不支持时区换算** | 页面显示 2026-10-09 07:03，但没有时区标记（F-004）；教程保留页面显示值并注明未注明时区，不作换算。 |
| 官方链接指向随时间变化的 `main`，难以复核当时源码 | **已固定源码快照** | 本次核验记录 GitHub API 在 2026-10-10 返回的 `main` 提交 SHA，并将 LIFT 文档和脚本链接固定到该提交（F-031）。GitHub 仓库描述和 license API 属采集时点元数据，仍按时间戳解释。 |
| 评测结果可外推到所有真实 Agent 使用场景 | **不支持** | 官方论文明确讨论 Judge 偏差和环境保真度，且提示绝对分数不宜跨 runtime 直接比较（F-022、F-023）。正文将结论限定于报告中的任务、Judge、runtime 和容器环境。 |

## 来源与可信度边界

- LIFT 的流程和统计细节以项目官方仓库为主要依据；论文、JSON 和脚本同属项目来源，不视为彼此独立的外部验证。
- 相关工作由各自的预印本记录证明其存在。此处不评价论文质量，也不声称它们与 LIFT 的实验协议等价。
- 未做独立运行复现、代码许可证法律意见或论文同行评审状态的外部确认。
- 若仓库新增许可证、排行榜重生成、论文发布新版本或基准增加复现实验，应重新核验并考虑撤销 `flagged` 状态。

## 四视角 V 审查

| 视角 | 攻击点 | 裁定 | 回归确认 |
|---|---|---|---|
| 魔鬼代言人 | “开源”可能只是仓库公开，未见许可证时读者可能误以为可自由复用。 | 采纳 | 根索引和来源台账明确许可证未确认；bundle 状态设为 `flagged`。 |
| 魔鬼代言人 | 10 次重复和 95% CI 容易掩盖排行榜数据比文章早约七周、论文仍为部分 sweep。 | 采纳 | 概念页与核验表同时展示生成日期、论文状态和适用限制。 |
| 新人 | Loaded、Holdout、delta 若不解释，读者可能把负值误解为性能下降。 | 采纳 | 概念页先定义 Base/Loaded/Holdout，再用公式解释符号方向。 |
| 业务负责人 | tokens 或 latency 下降不能直接推出用户体验、生产力或单位经济性改善。 | 采纳 | 结论页区分代理指标与业务结果，并要求报告原始值和任务边界。 |
| 未来视角 | LIFT 主分支、榜单和论文会继续变动，静态网页可能迅速过时。 | 采纳 | 设置 `stale_after: 2026-12-31`，并列出许可证、榜单、论文更新触发器。 |
| 方法审查 | 相关基准存在不意味着它们测量相同构念，直接对比会制造假冲突。 | 采纳 | 只用 SE-Bench/EvoAgentBench 限制“无人研究”说法，不做横向分数比较。 |
| 魔鬼代言人 | 把 10 次 repeats、274–280 个配对任务数和 CI 当作同一统计口径，会造成样本量与不确定性误读。 | 采纳 | 新增 F-029；排行榜教程与本表分别解释聚合 delta 和 repeat 级 CI 估计。 |
| 新人 | `turns` 容易被理解为用户与聊天机器人的对话轮次。 | 采纳 | 新增 F-030；排行榜教程说明字段映射到 `trials`，指任务内 work Agent/Judge 往返轮数。 |
| 魔鬼代言人 | 名为 Holdout 的集合可能令读者误以为 Warmup 与 Holdout 的要求完全隔离。 | 采纳 | 新增 F-028；协议页和边界页明确约 75% requirements 重合。 |
| 新人 | 仓库与论文对 LIFT 缩写展开不同，且文章页面时间没有时区。 | 采纳 | 新增 F-027；修正 F-004；首篇概念教程并列缩写版本，根索引不推测时区。 |
| 未来视角 | 引用 `main` 会随仓库更新而漂移，未来读者无法确认当时使用的源码。 | 采纳 | 新增 F-031；官方文档/脚本改用固定提交链接，动态仓库元数据保留采集时点。 |

十一项攻击均已落实到本报告、bundle 索引、概念页或事实台账；无未处理的 P0 内容错误。许可证状态仍未决，因此整体保持 `flagged`，不是对评测机制本身的否定。
