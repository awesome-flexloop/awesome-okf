---
type: Reference
title: "验证方法论核验与对抗审查报告"
description: "原站与全文镜像对读、官方文档交叉核验、勘误 E-0 至 E-4、四视角对抗审查、G1-G4 质量门记录与未获独立核验项"
tags: [verification, adversarial-review, provenance, errata, quality-gates]
route: chaptered-summary
generated: { by: "process:seven-concepts V", at: "2026-11-17T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-17T00:00:00+08:00" }
status: stable
stale_after: "2027-05-17"
sources:
  - id: blog
    resource: https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/
  - id: mirror
    resource: https://www.spke.com/en/ai/article/8773
  - id: cc-review-customize
    resource: https://code.claude.com/docs/en/code-review-customize
  - id: cc-hooks
    resource: https://code.claude.com/docs/en/hooks
  - id: cc-goal
    resource: https://code.claude.com/docs/en/goal
---

# 验证方法论核验与对抗审查报告

## 转化路线

`route: chaptered-summary`——**深度摘要加原创改写**，不逐字转录。原站为公开技术博客（有文本层、无访问控制），不属于扫描版版权材料；但为避免「把博文复述成官方规范」，仍显式登记路线：全包按「为什么验证 → 用什么测 → 怎么落地 → 怎么管住验证器」重组结构，英文原文仅以术语与短句形式保留，所有中文表述为重新组织。

## 信源分层

| 层 | 信源 | 本包用途 | 边界 |
|---|---|---|---|
| L1 主源 | claude.dev 原站博文（2026-11-16） | 全部事实与主张的来源 | 动态渲染，首轮抓取仅返回头部与部分段落 |
| L1' 补源 | 全文转载镜像（标注源发布时间 2026-11-16 20:00 UTC+8） | 补齐原站未返回的段落 | 非官方源；与原站重叠部分逐段比对一致 |
| L2 官方核验 | code.claude.com 的 code-review-customize、hooks、goal 三页 | 核验 `REVIEW.md`、Stop hook、`/goal` 机制 | 仅核验机制，未核验团队内部做法 |
| L3 转述 | 博文内链（《Solving code review at Anthropic》、fast-check/Hypothesis/proptest、CDP 等） | 作为术语与工具名登记 | 未逐页回源，不作硬事实 |

## 勘误与口径差异

### E-0 原站正文抓取不完整

原站首轮返回标题、副标题、作者、目录与引言，正文中出现多处 `[...]` 省略；第二次定向抓取补回 E2E 与结论段，团队流程中段仍缺。全文镜像补齐后，与原站已返回段落逐段比对，措辞一致。**处理**：以原站为权威，镜像仅补缺；差异段落在事实表中标 `双源一致`。

### E-1 `REVIEW.md` 从 base 分支读取带前提条件

博文表述为「Code Review reads the REVIEW.md file from the base or default branch, never from the pull request's changes」（F-049）。官方 `Customize Code Review` 文档给出的机制更细：需先把 `REVIEW.md` 提交并合并到仓库根，**再保护默认分支**；文档分别描述「受保护分支」与「未受保护的默认分支」下评审读取的行为，并写明包含文件「从同一 commit 读取，而非 PR 自身改动」。

**处理**：正文保留博文主张，同时补充「落地必须配分支保护」，不把简化表述写成无条件官方保证。

### E-2 `/goal` 的评估器不是验证本身

官方文档确认 `/goal` 每轮结束后由小模型判断条件是否满足，由「新模型」而非执行工作的模型决定完成；同时明确评估器**不执行命令、不独立读文件**，只判断会话中已呈现的证据。

**处理**：[团队验证流水线](../concepts/03-team-pipeline.md) 将 `/goal` 定位为「保证循环不提前停」，强调它不能替代真实检查；[搭建 verify skill](../examples/00-verify-skill-blueprint.md) 要求验证步骤产出可见证据。

### E-3 Code Review 服务与本地 `/code-review` 读不同文件

官方文档明确：Code Review **服务**读 `CLAUDE.md` 与 `REVIEW.md`；会话内运行的本地 `/code-review` **命令**只读 `CLAUDE.md`，不读 `REVIEW.md`。博文把「`REVIEW.md` 机制」与「commit gate 检查会话是否含 `/code-review`」并排叙述，读者易把两者当成同一套规则。

**处理**：正文分列两套工具，提示「希望两处都生效的规则写进 `CLAUDE.md`」。

### E-4 内部数字与阈值均为团队自述

约 90% 代码占比、成功率最多提升 10 个百分点、39 项清单、三轮失败阈值、3–10 项触发范围、两次拦截后放行，均出自博文，无独立复算或第三方数据。`10 MIN READ`、`2026-11-16` 为页面元信息。

**处理**：事实表标 `团队自述未复算` 或 `博文单源`；正文不把这些数字当作行业基线或推荐阈值。

## 四视角对抗审查（V）

| 视角 | 提出的问题 | 本包处置 |
|---|---|---|
| 魔鬼代言人 | 「验证循环 ⇒ 并行数十至数百个 Agent」是团队自述，缺少外部复现；90% 代码占比同样不可核验 | 四处核心结论均标 F 编号与来源层级；bundle 根「已知边界」首条即声明单一主源与内部数据未复算 |
| 新人 | 容易把 `/goal` 当成验证、把 `REVIEW.md` 当成无条件生效、把「生成测试」当成「建立循环」 | E-2、E-3 专列；[验证循环](../concepts/00-verification-loops.md) 反模式逐条点名；各概念页末尾给「反模式」清单 |
| 老板 | 39 项清单、三 agent 证伪、形式化 eval 的维护成本对小团队是否过重？ | [门禁治理](../concepts/04-gate-governance.md) 给出「到过拟合边界就停止调优」与 observe 三态，明确可分级采用；[可迁移模式总表](../concepts/05-misses-into-rules.md) 按触发场景给最小集 |
| 未来 | 规则只增不减会熵增；模型升级后「三轮」「3–10 项」等阈值可能失效 | E-4 标注阈值时效；[规则清理](../concepts/05-misses-into-rules.md) 单列一节；全包设 `stale_after: 2027-05-17` 并提示复核官方文档 |

> 审查中修正的一处：初稿把「`/goal` 每轮由独立模型判定」写成「独立执行了验证」，经官方文档核对后改为「判定条件不替代检查」，即 E-2。

## 质量门记录

| 门 | 判据 | 本包落点 | 结果 |
|---|---|---|---|
| G1 事实无因果词 | R 阶段只做客观陈述 | [博文事实清单](article-source.md) 71 条表格 | 通过 |
| G2 洞察四元组 | 现象 + 根因 + 影响 + 建议 | [验证循环](../concepts/00-verification-loops.md) 四节齐备，其余概念页均含「现象/根因或判据」与「建议」 | 通过 |
| G3 模式可迁移 | 触发场景 + 核心步骤 + 反模式 + 迁移验证 | 6 篇概念页均带四要素；[可迁移模式总表](../concepts/05-misses-into-rules.md) 汇总 6 个模式 | 通过 |
| G4 行动项原子化 | 单一职责、可独立验证 | 6 概念页 + 2 示例页各自独立主题；2 篇 examples 各带验收清单与预期输出 | 通过 |

**事实登记双份比对**：`F-001` 至 `F-071` 共 **71 条**，区间上界 ↔ 本页统计 ↔ 交叉引用三处一致、连续无跳号。

## 未获独立核验项

1. 全部团队内部数据与阈值（见 E-4）。
2. 全文镜像非官方源；其与原站重叠部分一致，但补齐段落未获官方第二源。
3. 博文内链的工具页、`claude.com` 相关文章与《Solving code review at Anthropic》的 eval 细节未逐页回源，仅按博文转述登记。
4. 两篇 `examples/` 为整理配方，本库环境未执行，不构成实测通过。
5. 官方文档仅核验机制存在性，未核验 Claude Code 团队是否按博文所述方式实际配置。
