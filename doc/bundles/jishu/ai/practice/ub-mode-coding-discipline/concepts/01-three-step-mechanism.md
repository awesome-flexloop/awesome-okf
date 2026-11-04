---
okf_version: "0.2"
type: Concept
title: "三步机制：First Make it Work → Then Make it Right → Practice"
description: "ub-mode 的主干结构——三大节共 24 组原则清单，以及博文「修好 → 检验 → 说明」三步与官方结构的对应关系"
tags: [ub-mode, agent-skill, tdd, clean-code, 三步机制, 工作流]
source: /references/article-source.md#F-014-F-023
status: draft
stale_after: 2027-01-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/vgwzE-3XGKN1VSjaIoZ_BA
  - id: skill-md
    url: https://raw.githubusercontent.com/unclebob/ub-mode/master/SKILL.md
  - id: github
    url: https://github.com/unclebob/ub-mode
---

# 三步机制：First Make it Work → Then Make it Right → Practice

## 主干：三节结构

ub-mode 的全部规则组织为三大节（F-021、F-022、F-023），这一结构在 skill 的 description 中即被声明为「每次改动遵循 First Make it Work → Then Make it Right → Follow Practice」（F-014）：

| 节 | 官方节名 | 原则数量 | 回答的问题 |
|----|---------|:-------:|-----------|
| 一 | **First Make it Work** | 8 组原则 + Architecture 5 条 | 先让代码**能跑**，且方向对 |
| 二 | **Then Make it Right** | 7 条 | 再让代码**变好**，且可度量 |
| 三 | **Practice** | 4 条 | 最后**说明并交付**改动 |

> **为什么这个顺序不可颠倒？** 它把「先跑通、再优化、最后交付」这一工程常识固化为强制次序。跨步优化（还没跑通就重构）与跳过度量（改完不检验）都被结构性地排除。

## 第一节：First Make it Work（先让它能跑）

含 8 组原则，另有一个 Architecture 子节含 5 条（F-021）：

| # | 原则 | 编号 |
|---|------|------|
| 1 | Laziness Protocol | F-021 |
| 2 | Foundational Thinking | F-021 |
| 3 | TDD（测试先行） | F-021 |
| 4 | Redesign From First Principles | F-021 |
| 5 | Attack the Premise | F-021 |
| 6 | Subtract Before You Add | F-021 |
| 7 | Outcome-Oriented Execution | F-021 |
| 8 | Build the Lever | F-021 |

**Architecture 子节（5 条）**（F-021）：

| # | 原则 | 编号 |
|---|------|------|
| 1 | Model the Domain | F-021 |
| 2 | Boundary Discipline | F-021 |
| 3 | Type System Discipline | F-021 |
| 4 | Make Operations Idempotent | F-021 |
| 5 | Separate Before Serializing Shared State | F-021 |

博文对第一步的表述是「**把 Bug 修好**：先写测试，再做最小改动」（F-016）——它与官方清单中的 **TDD** 与 **Subtract Before You Add / 最小改动** 取向直接对应。

> 说明：上表原则**名称本身**为官方源逐条目核验所得（F-021）；各条的具体展开文本以仓库 [`SKILL.md`](https://raw.githubusercontent.com/unclebob/ub-mode/master/SKILL.md) 原文为准，本教程不逐条转述其正文。

## 第二节：Then Make it Right（再让它变好）

含 7 条（F-022）：

| # | 原则 | 编号 |
|---|------|------|
| 1 | Fix Root Causes（修根因而非症状） | F-022 |
| 2 | Sequence work into verifiable units（拆成可验证单元） | F-022 |
| 3 | Test Behavior Not Implementation（测行为而非实现） | F-022 |
| 4 | Crapper | F-022 |
| 5 | Dryer | F-022 |
| 6 | Mutator | F-022 |
| 7 | Refactoring | F-022 |

其中 **Crapper / Dryer / Mutator** 三条同时是可打分检查工具的入口（阈值与用法见 [可打分的检查](02-scoreable-checks.md)）——这正是 ub-mode 区别于「泛泛命名式规则」的关键：**第二节的「变好」不靠感觉，而靠分数**。

博文对第二步的表述是「**修好还要检验**：用 Crapper 查复杂度、Dryer 查重复度、Mutator 做变异测试」（F-017）——与官方三条工具原则完全对应。

## 第三节：Practice（实践与交付）

含 4 条（F-023）：

| # | 原则 | 编号 |
|---|------|------|
| 1 | Keep a Log（记日志） | F-023 |
| 2 | Guard the Context Window（守护上下文窗口） | F-023 |
| 3 | Worktree Cleanup（清理工作树） | F-023 |
| 4 | Commit and Push（提交并推送） | F-023 |

博文对第三步的表述是「**说明修改了什么**：报告改了哪些文件、加了哪些测试、检查结果」（F-018）——对应官方 Practice 节的「Keep a Log」取向。

> ⚠️ **第三节是全文最需注脚的地方**：官方 `Commit and Push` 要求「Push to the main line at the end」，而博文明确表达「作者对此**不放心**」（F-033）——这是仅有的、被博文标注为保留意见的一节。详见 [边界与勘误](04-boundaries-and-gotchas.md)。

## 博文举例的两条具体规则

博文在阐述规则时举了两个例子（均为博文单源表述，F-019、F-020）：

- **登录参数入口检查一次**（F-019）——对应「边界/入口校验只做一次」的工程直觉；
- **重复逻辑集中维护**（F-020）——对应第二节的 Dryer（消除重复度）取向。

## 小结：三步机制怎么读

| 博文口径 | 官方结构 | 核心手段 |
|---------|---------|---------|
| ① 把 Bug 修好 | First Make it Work | 先写测试（TDD）+ 最小改动 |
| ② 修好还要检验 | Then Make it Right | Crapper / Dryer / Mutator 打分 |
| ③ 说明修改了什么 | Practice | 记录改动与检查结果 |

三步机制中「② 检验」所依赖的三（实为四）个工具与阈值，是下一篇 [可打分的检查](02-scoreable-checks.md) 的主题。

事实编号全集见 [博文与官方源事实清单](../references/article-source.md)，核验结论见 [P0 核验报告](../references/verification.md)。
