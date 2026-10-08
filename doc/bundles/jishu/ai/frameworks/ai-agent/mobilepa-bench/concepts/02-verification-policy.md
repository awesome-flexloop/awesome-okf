---
type: Concept
title: "固定验证策略与六类 checker"
description: "评测器为每任务分配固定验证策略的四种成功形态，站点案例暴露的六类 checker 字面量与维度分布，replay demo 的 tool_acc/task_db_acc 双场景与保密边界。"
tags: [MobilePA-Bench, 验证策略, checker, 证据制判分, replay]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: mobilepa-facts
    resource: /references/facts.md
    title: MobilePA-Bench 与网站事实台账
  - id: mobilepa-sources
    resource: /references/source-registry.md
    title: 信源登记
---

# 固定验证策略与六类 checker

> **事实基础**：本文所有数据与引文均标注 F 编号，完整事实清单见本束 `references/facts.md` A 部分。

MobilePA-Bench 的判分**不是统一的 LLM 评审**，而是"证据制"：评测器为每个任务分配**固定验证策略（fixed verification policy）**，按任务性质选择从精确参数比对到行为评审的不同 checker（F-007）。本篇梳理四种成功形态、站点公开案例暴露的六类 checker 字面量及其维度分布，以及交互式 replay 演示呈现的判分口径。

## 1. 固定验证策略：四种成功形态

README Overview 原文（F-007）：评测器为每个任务分配固定验证策略，成功可要求以下四种形态之一：

| 形态 | 字面 | 考察点 |
|---|---|---|
| 精确工具调用 | an exact tool call | 工具名与参数完全正确 |
| 目标状态迁移 | a target state transition | 环境最终状态达到目标 |
| 规定动作顺序 | a prescribed action order | 执行顺序符合要求 |
| 有效协作模式 | a valid collaboration pattern | 与子代理/用户的协作行为有效 |

环境的角色（F-007）：执行每个动作、更新状态并返回观察或**运行时错误**——失败模式包括工具依赖、权限边界、冲突请求、运行时错误与不完整用户上下文（F-003）。

## 2. 六类 checker 字面量与维度分布

站点公开案例数据（`case_studies_data.js`）中出现的 checker 字面量共六类（F-021）：

```text
Strict tool + arguments      Behavior judge             Final DB state
DB state + retrieval         Behavior judge + retrieval  Skill routing + execution
```

各维度的分布（F-021、F-032）：

| 维度 | checker 分布 | 说明 |
|---|---|---|
| Tool Use | 3 个案例分别对应**三种**不同 checker | Tool Use 案例覆盖 Strict tool + arguments 等（F-021） |
| Memory | DB state + retrieval / Behavior judge + retrieval | 状态比对与检索证据组合（F-021） |
| Skills | 3 个案例**均为** Skill routing + execution | 考"是否先加载了正确的可复用技能"（F-032） |
| Sub-agent | 3 个案例**均为** Behavior judge | 协作行为交由评审（F-032） |

两点反常识：

- 并非"越有状态越用数据库比对"——**Sub-agent 维度统一交由 Behavior judge（LLM 评审），而 Tool Use 反而最"硬"**（Strict tool + arguments）（F-021）。
- Tool Use 维度的 BTU-622（Conflict intent，F-022）中，模型的最优行为是识别冲突后**反问用户**而非强行执行——"多执行动作"反而错。

## 3. replay demo：tool_acc 与 task_db_acc 双场景

交互式 replay 演示（`replay_demo_data.js` 的 `window.MobilePAReplayScenarios`）展示两种 policy（F-023）：

| 场景 id | tab 名 | policy | policyLabel | 示例 | 校验要点 |
|---|---|---|---|---|---|
| tool | "Exact Tool Call" | `tool_acc` | "Exact tool + arguments" | manage_alarm 创建 7:30 Morning run 闹钟 | checks 列 Tool name / Argument fields / Grounded values |
| state | "Stateful Completion" | `task_db_acc` | "Final environment state" | 杭州周六行程计划 | capabilities 标注 basic/memory/skills 三维 |

Demo 区三栏分别为 **Interaction（User & Agent）、Execution trace（Planner & Environment）、Fixed policy（Evidence Checker）**（F-023）——即把"对话—执行轨迹—判分依据"三段证据同屏呈现。

## 4. 公开与保密边界

Demo 区底部注明（F-023）：

```text
Illustrative public examples; hidden evaluation tasks and ground truth remain private.
```

即站点上的案例与 replay 演示仅是**展示型公开样例**，hidden 评测任务与 ground truth 保持私有（F-023，与 F-009 的 Hidden-test integrity 特性一致）。这决定了本基准的复现形态：无法下载任务集本地跑分，只能提交 endpoint 参与托管私有评测（F-008/F-009）。

## 5. 解读纪律

- 解读任一维度分数前，先问"该维度用什么 checker"：**Behavior judge 类分数的方差属性与确定性 checker（如 Strict tool + arguments、Final DB state）不同**，跨维度比较时应注意这一差异（F-021）。
- 案例 id（BTU-xxx / MEM-xxx）与 subtype（Ordered execution / Conflict intent / Memory update 等）是引用具体考题时的锚点（F-022）。

## 相关概念

- [00-benchmark-overview.md](00-benchmark-overview.md)——评测器建模与四种成功形态的出处
- [01-capability-dimensions.md](01-capability-dimensions.md)——各维度代表案例（BTU-204/BTU-622/MEM-0043 等）
- [03-leaderboard-analysis.md](03-leaderboard-analysis.md)——分数如何按维度加权汇总
- [../mobile-world/index.md](../../mobile-world/index.md)——同生态在线评测环境（环境实测式判分的对照形态）
