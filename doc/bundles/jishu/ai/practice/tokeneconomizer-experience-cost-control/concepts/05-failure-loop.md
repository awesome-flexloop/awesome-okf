---
type: Concept
title: "失败循环干预：先量出预算，再决定要不要打断"
description: "轮次预算 B_i、规则层监视、judge 置信度、redirect、backstop、各 agent 停止方式与 headless 边界"
tags: [失败循环, 轮次预算, judge, redirect, headless, 可逆性]
status: stable
stale_after: 2027-02-28
generated: { by: "reference_agent/seven-concepts-rie", at: "2026-11-17T12:35:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-17T12:35:00+08:00" }
sources:
  - id: facts
    resource: ../references/article-source.md
  - id: project
    resource: https://tokeneconomizer.github.io
  - id: repo
    resource: https://github.com/microsoft/TokenEconomizer
---

# 失败循环干预：先量出预算，再决定要不要打断

## 难点不是「发现失败」，而是「区分还在推进」

[成本剖析](01-cost-profiling.md) 给了两个反直觉数字：50 条成功轨迹里有 36 条同样重复了失败签名（F-029）；重复后发生的花费中超过一半来自最终成功的运行。所以「看到重复错误就停」会砍掉大量本来能成功的任务。Matplotlib 与 Sphinx 的失败 / 成功轮数差异也说明全局轮数上限不可靠（F-027）。

论文的解法是**先学会这个仓库「正常的一轮有多长」**，再把「异常」定义为相对该仓库自身分布的偏离。

## 四步机制

**第 1 步 · 学预算**（式 3，F-066）

```
B_i = β · Q_p( { |ξ_j| : j < i, y_j = 1 } )      p = 90, β = 1.25
```

取该仓库**已成功轨迹**轮数的 90 分位，乘 1.25 的余量。用成功轨迹而非全部轨迹，是为了不让失败的拖尾把预算本身拉高。

**第 2 步 · 便宜地监视**（F-067）：每次工具调用后用规则检查——重复失败签名、密集错误、是否跑过 Bᵢ。这一层**不调用模型**。

**第 3 步 · judge 与 redirect**（F-068）：疑似卡住时，LLM judge 读近期动作摘要；置信度 ≥ c = 0.7 判定 stuck，写入一条短 redirect（附「已经试过什么」的摘要），建议换一种做法。论文配置为 Redirects = 1, then stop（F-069）。

**第 4 步 · backstop**（F-069）：κ = 2.5，当「反复改动同一批文件 + 密集错误 + 重复失败」三个条件同时成立且 turn 跑过 κ·Bᵢ 时，不经 judge 强制重定向 / 停止。

附录 C 还给了一个边界例子：Web-Bench 每个流只有 20 或 21 个任务，成功轮数的分位数来不及预热，守卫改用**预注册 30 轮预算**，直到 5 个任务通过（F-070）。这是「同一套参数不能硬套不同任务流结构」的直接证据。安全基准则因每个任务都是新仓库而整体关闭 micro-skills，只留两条元策略（F-071）。

## 实际触发频率

附录 H 表 6（每六仓库流均值，F-072）：judge 被咨询 9.9–13.1 次，redirect 3.9–5.3 次，abort 1.4–2.2 次。论文的解释是：**大多数升级最终得到「仍在推进」或「不确定」的结论**，因此 judge 的调用远多于真正打断的次数。换句话说，这是一条「宁可多问一次，也不要误停」的策略。

## ⚠️ 论文控制器与开源插件的行为差异

这是本束最重要的一处落地差异（核验报告 D-3）：

| 维度 | 论文实验控制器 | 开源插件 |
|---|---|---|
| redirect 后仍卡住 | stop / abort（表 6 有 Aborts 列） | **只提示开发者如何停止，从不自行停止 turn**（F-100） |
| 提示形态 | 论文未描述 | 一行公告，例：`TokenEconomizer: this turn still looks stuck after a redirect (judge-stuck@0.82, 46 tool calls). Press Esc to interrupt it.` |
| 提示位置 | — | 交互模式下在 agent 回复 / 会话 / 通知里；headless 下在最终回复或 stdout/stderr |
| headless 后果 | 控制器自行终止 | 没人看提示时，被标记的 turn 会一直跑到 agent 自身上限 |

仓库 README 给出的停止方式：Claude Code 交互按 Esc、headless Ctrl+C；Codex 交互 Esc 后还需 `/stop` 结束已启动的命令；Copilot CLI 交互按两次 Esc；Pi / opencode 按 Esc 或 Ctrl+C。另有两个诚实的能力声明：Claude Code 只把插件自己的行显示在详细 transcript（Ctrl+O），所以插件会请模型在回复里复述这条提示，**模型可能改写或漏掉**；`codex exec` 不打印 hook 消息；Hermes Agent 同理靠模型复述。

> **给工程落地的结论**：如果跑的是 `claude -p` / `codex exec` 这类无人值守任务，不能指望插件替你刹车。需要外层超时或任务级中止策略，并把 `te status` 里的 redirect / still-stuck 计数作为观测指标。

## 插件侧的可配置项

| 设置 | 默认值 | 含义 |
|---|---|---|
| `loopguard.envelope_min_samples` | 5 | 本仓需 5 个「正常结束」的 turn 后才启用守卫（F-097） |
| `loopguard.judge_confidence` | 0.7 | judge 判定 stuck 的置信门槛，与论文同值 |
| `loopguard_nudges` | 1 | 每 turn 的 redirect 次数，之后只提示 |
| `loopguard.backstop_mult` | 2.5 | 相对通常长度的倍数 |
| `TE_LOOPGUARD=off` | — | 单次会话级关闭（同类还有 `TE_MICROSKILLS`、`TE_TOOLPRUNE`、`TE_DISABLE=1`） |

⚠️ `e = 5` 与论文的「Web-Bench 预注册到 5 个任务通过」数值相同但语义不同，见 [参数分账台账](../references/parameter-ledger.md)。

## 三个反模式

1. **用固定轮数上限**：F-027 的 Matplotlib 45 vs 20、Sphinx 36 vs 31 说明失败与成功的长度关系随仓库变化。
2. **把「重复」当作「卡住」**：F-029 显示多数成功轨迹也会重复失败签名。
3. **自动终止却不给恢复路径**：论文 §6 明确把「困难但有效的任务被误判为失败循环」列为可能的误判，并用「先 redirect 再 stop、放过不确定情形」限制损害（F-106）；插件更进一步把最终决定留给人（F-100）。
