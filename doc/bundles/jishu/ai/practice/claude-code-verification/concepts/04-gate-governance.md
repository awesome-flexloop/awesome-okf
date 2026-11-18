---
type: Concept
title: "门禁治理与评审者评测"
description: "commit 验证戳与 off/observe/enforce 三态门禁、误报兜底、评审者的三类指标与形式化 eval、分层召回率与重要性标签"
tags: [observe-mode, commit-gate, eval, recall, severity, overfitting]
status: stable
sources:
  - id: blog
    resource: https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/
  - id: code-review-post
    resource: https://claude.dev/blog/solving-code-review-at-anthropic/
---

# 门禁治理与评审者评测

## 新门禁先跑 observe 模式

团队给每个 commit 打上「**这次是怎么验证的**」戳，戳里甚至包含 `none`，以便直接查询「哪些 commit 完全没验证」（F-052）。在此之上建了一道 commit gate：会话中没有出现过 `/code-review` 或 `/verify` 就拦截提交，设 **off / observe / enforce** 三态（F-053）。

| 模式 | 行为 | 目的 |
|---|---|---|
| off | 不生效 | 初始状态 |
| observe | 记录「本会被拦下」的提交，不真的拦 | 人工复核误报，确保无人受影响（F-054） |
| enforce | 真正拦截；commit message 可写明未验证的理由 | 落地执行（F-055） |

一个容易被忽略但很务实的兜底：**同一会话内被拦两次后，下一次放行**，避免 Claude 卡死——原文直说「Claude Code isn't perfect」（F-056）。这体现了门禁设计的成熟之处：门禁本身也要有退出机制，否则它会变成比它要防的问题更严重的阻塞。

## 定期「审查审查者」

三个日常指标（F-057）：合并后被 revert 的改动数、maintainer 合并前拒绝的改动数、以及一个 **size-matched**（规模匹配）的「保持干净」改动子集。第三项是对照组——没有它，无法区分「查得严」与「只会乱报」。

形式化 eval 的做法来自团队此前的 code review 文章（F-058）：

1. 按历史事故与 revert 建样例集，把仓库**复现到评审发生时的状态**；
2. 每个样例给一句「bug 是什么」的答案 key；**只有正确描述该 bug 的 finding 才得分**；
3. 用「已合并且稳定」的改动作对照，防止过度标记；
4. tuning set 与固定 test set 分开，避免调参污染评估。

### 三个必须分开的召回率

原文最锋利的方法论主张在这里（F-059）：分别评估 **raw findings**、**post-verification**、**final review** 三阶段的召回率，才能看出系统是否**丢掉了它本已发现的 bug**。只给一个端到端总分，会把「发现对了但被后续环节筛掉」误算成「没发现」。这是验证链路可观测性的核心，也是 [验证循环](00-verification-loops.md) 在团队尺度上的对应物。

## 有效性之外还有「重要性」

技术正确不等于值得改（F-060）：人关心的是 must-fix / should-fix / nit。Code Review 用 **Important / Nit / Pre-existing** 三档标签承接，其中 `Pre-existing` 明确表示「不该让作者为原本就存在的 bug 负责」（F-061）。

最后是调优的停止条件（F-062）：**把 recall 调到「再往上就是对 eval 过拟合、而不是真在抓 bug」为止**。这条把「指标越高越好」翻转为「指标高到开始脱离真实分布就该停」，是整套评测体系的自我约束。

## 结论层的四条治理律

原文收尾把验证层当作一个系统来对待（F-070）：

1. 放在被评判的改动**够不着的地方**；
2. 用**真正让你疼过的 bug** 给它评分；
3. 漏掉的东西写下来，让同类问题**不再发生第二次**；
4. 并且**修剪**这些教训，让它们始终值得跑。

第 4 条常被漏掉，却是 [把漏检变成规则](05-misses-into-rules.md) 的直接动机。

## 可迁移模式与反模式

- **触发场景**：准备上线新的自动检查/评审门禁，或已有门禁开始被抱怨「太吵」。
- **核心步骤**：打验证戳（含 `none`）→ observe 跑一段 → 复核误报 → enforce → 设卡死兜底 → 用带对照组的 eval 分层量召回 → 到过拟合边界停止调优。
- **反模式**：一上来就 enforce；只算端到端总分；没有对照组地追求高召回；门禁无退出机制。
- **迁移验证**：任何 CI/评审系统都可套用「三态上线 + 对照组 eval + 分层召回 + 停止条件」四步；缺对照组则无法区分严格与噪声。

> 事实编号与来源层级见 [博文事实清单](../references/article-source.md)；本页涉及 F-052—F-062、F-070。可照做的配方见 [observe 模式门禁落地](../examples/01-observe-mode-gate.md)。
