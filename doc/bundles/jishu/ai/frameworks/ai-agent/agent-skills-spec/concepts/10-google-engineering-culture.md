---
type: Concept
title: Google 工程文化术语详解
description: 支撑 AI 编程技能设计的 8 个 Google 工程文化核心术语——Hyrum 定律、Beyonce 规则、Chesterton 栅栏、测试金字塔、左移、基于主干开发、DAMP 胜过 DRY、代码即负债。
tags: [google-engineering, hyrum-law, test-pyramid, shift-left, trunk-based-development, engineering-culture]
generated: { by: "process:learning-migration merge", at: "2026-09-02" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02" }
status: stable
stale_after: 2027-09-02
sources:
  - id: learning-google-culture
    resource: "SpecWeave docs/knowledge/learning/02-agent-engineering-methodology/02-prompt-coding/agent-skills-wiki/04-google-engineering-culture.md"
    title: Google 工程文化术语解释（腾讯云开发者社区 2026-07-08 文章转译）
---

# Google 工程文化术语详解

## Hyrum 定律（Hyrum's Law）

> **定义**：当 API 有足够多的用户时，你在合同中承诺什么都不重要：你所有可观察到的行为都会被某人依赖。
>
> **出处**：Google 工程师 Hyrum Wright 提出。

**工程意义**：

- 不要以为“这是内部实现细节用户不会依赖”——只要行为是可观察的，就一定会有人依赖
- 修改任何行为（即使是“bug”）都可能是破坏性变更
- 因此 API 设计要保守，一版本规则（不要同时支持多个版本的行为），明确什么是契约什么是实现细节

**在 Agent Skills 中的体现**：api-and-interface-design 技能专门强调契约优先设计和一版本规则。

## Beyonce 规则（Beyoncé Rule）

> **定义**：If you liked it, you should have put a test on it——如果你喜欢某个行为，你就应该给它写个测试。
>
> **出处**：化用 Beyoncé 歌曲《Single Ladies》歌词 “If you liked it then you shoulda put a ring on it”。

**工程意义**：

- 你不写测试覆盖的行为，下次重构时就会被不小心改掉
- 所有你期望保持的行为（包括边界条件、错误处理）都必须有测试保护
- 这是 TDD 和测试金字塔的哲学基础

**在 Agent Skills 中的体现**：test-driven-development 技能的核心原则之一。

## Chesterton 栅栏（Chesterton's Fence）

> **定义**：在你知道栅栏为什么建在那里之前，不要拆除它。改革者拆掉栅栏时应该能说明：当初建栅栏是为了解决什么问题？为什么现在那个问题不存在了？
>
> **出处**：G.K. Chesterton 的比喻。

**工程意义**：

- 看到“这代码写得真烂为什么不删掉”时，先搞清楚它当初为什么存在
- 你觉得“多余”的代码可能是在处理某个你没遇到过的边界 case
- 重构和简化必须建立在理解原有设计意图的基础上

**在 Agent Skills 中的体现**：code-simplification 技能的首要原则。

## 测试金字塔（Test Pyramid）

> **定义**：测试应该按比例分层：80% 单元测试（快、小、isolated），15% 集成测试（验证模块交互），5% 端到端测试（慢、贵、覆盖核心路径）。
>
> **出处**：Mike Cohn 提出，Google 工程实践广泛采用。

**工程意义**：

- 反模式：冰淇淋蛋筒（大量 E2E，少量单元测试）——测试慢、不稳定、难定位
- 单元测试给你快速反馈，集成测试给你模块信心，E2E 只覆盖最核心的用户旅程
- 80/15/5 是经验比例，不同项目可调整，但金字塔形状不能倒

**在 Agent Skills 中的体现**：test-driven-development 技能明确要求测试金字塔比例。

## 左移（Shift Left）

> **定义**：把质量保障、安全检查、测试等环节从开发流程的后期（发布前）移到前期（编码时、提交时、构建时）。问题发现得越早，修复成本越低。

**工程意义**：

- 需求阶段发现问题：成本 1x
- 编码阶段发现问题：成本 10x
- 测试阶段发现问题：成本 100x
- 生产环境发现问题：成本 1000x
- “越快越安全”不是省略步骤，而是把检查自动化到开发最早期，快速反馈

**在 Agent Skills 中的体现**：ci-cd-and-automation 技能的核心理念，质量门禁左移到每次提交。

## 基于主干开发（Trunk-Based Development）

> **定义**：所有开发者频繁向主干（trunk/main/master）提交小批量变更，不维护长期存在的特性分支。特性通过特性标志（feature flags）隐藏，未完成的代码合入主干但不暴露给用户。
>
> **对比**：与 Git Flow 等长生命周期分支模型相反。

**工程意义**：

- 避免“合并地狱”：分支存在几周后再合并，冲突堆积成山
- 小批量提交：每次变更约 100 行，容易评审，出问题容易回滚
- 持续集成：每个人每天都在最新代码上工作，及早发现集成问题
- 特性标志解耦“代码合入”和“功能发布”

**在 Agent Skills 中的体现**：git-workflow-and-versioning 技能的核心要求。

## DAMP 胜过 DRY（DAMP over DRY）

> **定义**：Descriptive And Meaningful Phrases（描述性且有意义的短语）胜过 Don't Repeat Yourself（不要重复自己）——在测试代码中，适当的重复比过度抽象更好，因为测试的首要目标是可读性和可理解性。

**工程意义**：

- 生产代码要 DRY：避免重复逻辑，抽公共函数
- 测试代码要 DAMP：每个测试用例应该能独立读懂，不需要跳转到辅助函数看 setup 了什么
- 测试读的频率远高于写的频率，测试的可读性直接决定了测试能不能作为“活文档”
- 不要为了“消除重复”把测试抽得面目全非，后人根本看不懂测的是什么

**在 Agent Skills 中的体现**：test-driven-development 技能中的测试设计原则。

## 代码即负债（Code as Liability）

> **定义**：代码不是资产，是负债。每一行代码都需要维护、调试、理解、移植——代码越多，维护成本越高，出 bug 的表面积越大。最好的代码是没有代码，最好的工程师是删代码的工程师。

**工程意义**：

- 新功能加代码是必要的，但旧功能下线时必须删代码（deprecation）
- 僵尸代码（永远不会执行的代码、被废弃但没删的代码）是纯粹的负债
- 简化代码、重构的本质是减少负债
- 不要“以防万一”留着代码——版本控制会记住历史，真需要再找回来

**在 Agent Skills 中的体现**：deprecation-and-migration 技能的核心思维，code-simplification 也体现了这一点。

## 相关概念

- [/concepts/09-osmani-agent-skills-practice.md](/concepts/09-osmani-agent-skills-practice.md) —— 这些术语在生产级技能库中的具体落位
- [/concepts/03-authoring-principles.md](/concepts/03-authoring-principles.md) —— 开放标准视角的创作原则
