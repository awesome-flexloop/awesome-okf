---
type: Concept
title: "验证就是跑起来改动"
description: "把端到端运行固化为 verify skill 的工程做法：四类宿主入口、冒烟基座的投资方式、feature map 复用与可迁移模式"
tags: [verify-skill, smoke-test, e2e, cdp, simulator, feature-map]
status: stable
sources:
  - id: blog
    resource: https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/
---

# 验证就是跑起来改动

## 现象与根因

原文给了一条优先级判断：**端到端把应用跑起来比测试更重要**（F-033）。理由在 [三类测试](01-three-test-types.md) 已埋下——单测全绿仍可能破坏功能，而真实运行能给出「整个功能到底能不能用」的二元答案。作者类比：你不会没在模拟器里试过就发布 iOS 改动，对 Claude 也应如此。

根因是「理解缺口」：写代码的 Agent 与写单测的 Agent 共享同一份不完整的任务理解，于是两者可以一起错；只有真实运行系统不共享这份理解，才构成独立判据（F-017、F-015）。

## 四类宿主入口

原文按改动类型给出四种「手和眼」（F-034）：

| 改动类型 | 让 Agent 使用的入口 |
|---|---|
| Web 前端 | Claude Chrome 扩展 |
| 移动端 | iOS / Android MCP |
| 桌面端 | computer use |
| 后端服务 | 在本地把服务跑起来 |

E2E 场景再用 skill 通过 CDP、模拟器或 API harness 启动、驱动、检查应用（F-018）。

## 核心做法：把启动方式固化成 `verify` skill

这是全文最具操作性的一条（F-035—F-038）：

1. 建一个名为 `verify` 的 skill，写清「如何启动模拟器 / 如何把应用跑起来」；
2. 放在仓库的 `.claude/skills/` 下，**尽量靠近相关代码**，需要几个就建几个；
3. Claude 知道在提交改动前调用 `verify` skill；
4. 持续投资让它**快且可靠**：让 Claude 自己迭代它、对它做压力测试——它是 smoke test harness，必须「rock solid」；
5. 原文称 Anthropic 几乎所有改动都用这种方式端到端测试（F-038）。

注意第 4 步的性质：这个 skill 本身也是被验证的对象。[门禁治理](04-gate-governance.md) 里「定期审查审查者」是同一逻辑的团队级版本。

## 影响与建议

- **影响**：有了冒烟基座，Agent 会像人一样边跑边抓真实错误，迭代速度和错误发现率都上升（F-038 语境）。
- **建议**：feature map 同时充当 Agent 的向导与评分 rubric（F-019），从用户视角写清路径、快捷键、选择器、预期结果——它把「完成条件」变成 Agent 可读的文本，正是 [验证循环四要素](00-verification-loops.md) 第 1 步的落地物。
- **可迁移模式**：触发场景＝任意有可运行产物的仓库；核心步骤＝选宿主入口 → 写 `verify` skill → 强制提交前调用 → 反复压测 skill 本身 → 用 feature map 定义完成条件；反模式＝只在 CI 里跑单测就宣称「已验证」、把慢启动的冒烟流程塞进每轮循环、skill 写好后再不维护。
- **迁移验证**：换到非 Claude Code 的 Agent 时，只要「提交前强制可运行的冒烟入口 + 完成条件文本化」两件事还在，模式即成立。

## 与其他概念的关系

- 本页解决「信号从哪里来」；[团队验证流水线](03-team-pipeline.md) 解决「谁写、放在哪、何时触发」；
- 两篇可照做的配方见 [搭建 verify skill](../examples/00-verify-skill-blueprint.md)。

> 事实编号与来源层级见 [博文事实清单](../references/article-source.md)；本页涉及 F-015、F-017—F-019、F-033—F-038。
