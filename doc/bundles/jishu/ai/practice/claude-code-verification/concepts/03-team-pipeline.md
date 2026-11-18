---
type: Concept
title: "团队验证流水线"
description: "人在哪里介入、代码所有者写自己的检查、39 项清单按 diff 触发、单评审者多轮叠加、检查不可自改与便宜检查先行"
tags: [human-in-the-loop, review-md, reliability-checklist, diff-trigger, branch-protection, hooks, goal]
status: stable
sources:
  - id: blog
    resource: https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/
  - id: cc-review-customize
    resource: https://code.claude.com/docs/en/code-review-customize
  - id: cc-goal
    resource: https://code.claude.com/docs/en/goal
---

# 团队验证流水线

这一层回答的是治理问题：验证物由谁写、放在哪里、什么时候跑、谁有权改。原文的九条实践可归为四组。

## 一、人的介入点：失败即路由

没人能读每一个改动，于是团队把「失败」当作「需要人」的信号（F-039）：Claude 跑检查并尝试修复；**同一检查连续三轮仍失败，就停下来叫人**。这比「按改动大小决定是否人工审」更省人，且天然把人放在 Agent 反复搞不定的地方。

配套一条：代码所有者写自己的检查，并调优到「能报出 owner 会报的问题」（F-040）；检查拉入 reviewer 时**要说明为什么**，不让 reviewer 从 diff 反推（F-041）。这把「 tacit knowledge（只存在于人脑里的判据）」强制外化成了检查项。

## 二、按 diff 触发的可靠性清单

团队维护一份 **39 项**清单，每项含三件东西：可从 diff 读出的 **trigger**、对应的 **check**、以及背后的**事故或 PR**（F-042）。示例条目是 `--resume loads old transcripts`：当会话存储或消息类型变动时，检查新增字段能否安全加载——旧 transcript 里没有该字段（F-043）。

Claude 读 diff 后只查 trigger 匹配的项，通常 **3 到 10 项**（F-044）。设计要点是：没有人需要背下历史故障清单，历史故障被编码成 diff 可识别的模式。这与 [把漏检变成规则](05-misses-into-rules.md) 是同一个「事故 → 规则」闭环的静态侧。

## 三、评审的组织方式

| 实践 | 原文主张 | 依据 |
|---|---|---|
| 不堆叠评审者 | 加第二个更贵的 reviewer 往往不如调优主 reviewer | F-045 |
| 用 `REVIEW.md` 写明该代码该关注什么 | 把注意力写进文件而非靠模型猜 | F-046 |
| 一个评审者、多轮叠加 | 每轮带上前几轮上下文与历史失败，不从头全查；更便宜且找得更多 | F-047 |

第三条值得单独强调：多轮评审的价值来自**累积上下文**，不是重复劳动。若每轮都从零重查，轮次增加只带来成本。

## 四、检查不可自改，便宜检查先行

> **「如果改动能修改评判它的检查，这个检查就坏了。」**（F-048）

三条硬约束（F-049—F-051）：

1. **规则与改动隔离**：Code Review 从 base / default 分支读 `REVIEW.md`，绝不从 PR 的改动里读；门禁规则必须放在改动够不着的分支。
2. **评审只对 commit**：评审期间有人继续 push，评审结果就失效——过期 commit 上的「通过」没有意义。
3. **便宜检查先行**：开 PR 之前，Claude 先跑 tests、build、linter；否则本可自查的 bug 会消耗共享的评审与 CI 时间。可用结束时的 hook 或 `/goal` 强制。

### 官方文档补充（口径差异）

- **`REVIEW.md` 的分支前提**：官方文档要求先把 `REVIEW.md` 提交并合并到仓库根，**再保护默认分支**；并且明确区分「受保护分支」与「未受保护的默认分支」两种读取行为。因此博文「绝不从 PR 改动读」是有条件的结论，落地时必须配分支保护（见 [E-1](../references/verification.md)）。
- **服务与本地命令不是一回事**：Code Review 服务读 `CLAUDE.md` 与 `REVIEW.md`；会话内运行的 `/code-review` 命令只读 `CLAUDE.md`，**不读 `REVIEW.md`**（见 [E-3](../references/verification.md)）。
- **`/goal` 的评估器边界**：官方文档确认每轮结束后由一个小模型判断条件是否满足，由「新模型」而非干活的模型决定完成；但评估器**不执行命令、不独立读文件**，只判断会话里已呈现的证据（见 [E-2](../references/verification.md)）。所以 `/goal` 能保证循环不提前停，不能替代真实检查。
- **Stop hook**：官方文档的 `Stop` 事件在「Claude 完成响应」时触发，可作为确定性的每轮检查入口。

## 可迁移模式与反模式

- **触发场景**：多人/多 Agent 共用一个仓库，检查规则开始被频繁修改时。
- **核心步骤**：定义失败→人的路由阈值 → 所有者把判据写成检查并附理由 → 把历史事故编码为 diff trigger → 规则放受保护分支 → PR 前跑便宜检查 → 多轮评审复用上下文。
- **反模式**：让 PR 同时携带规则修改；评审期间继续 push；用更多 reviewer 掩盖主 reviewer 未调优；把 `/goal` 当作验证本身。
- **迁移验证**：换代码托管平台时，只要「规则文件与变更分支物理隔离」和「评审绑定到不可变 commit」两条仍成立，模式成立。

> 事实编号与来源层级见 [博文事实清单](../references/article-source.md)；本页涉及 F-039—F-051。
