---
type: Example
title: "示例二：读状态、调参与观测（官方文档转述，本束未实测）"
description: "status / microskills / toolprune / config 的读法、六步全栈对齐、附录 H 活动计数的观测口径与 headless 边界"
tags: [状态观测, 调参, 未实测, config, 累积成本]
status: stable
stale_after: 2027-02-28
generated: { by: "reference_agent/seven-concepts-a", at: "2026-11-17T12:45:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-17T12:45:00+08:00" }
sources:
  - id: repo
    resource: https://github.com/microsoft/TokenEconomizer
  - id: ledger
    resource: ../references/parameter-ledger.md
  - id: facts
    resource: ../references/article-source.md
---

# 示例二：读状态、调参与观测

> **⚠️ 未实测声明**：本页是依据 `microsoft/TokenEconomizer` README 与论文附录 H 整理的**检查清单与读表口径**，本束未运行插件、未采集任何真实 status 输出。文中不出现本环境实测数字。

## 1. 四条命令各回答什么问题

| 命令 | 应回答的问题 | 观察什么 |
|---|---|---|
| `status` | 本仓学到了什么、做了什么、会话花了多少 | 三条机制的动作计数、会话成本 |
| `microskills` | 哪些事实已被注入、哪些仍在形成 | Candidate / Confirmed 的分界（F-058） |
| `toolprune` | 哪些工具被排除、依据是什么 | 被屏蔽工具清单与证据（F-061、F-102） |
| `config` | 当前全部生效设置 | 三个开关与九个阈值（F-096、F-097） |

命令前缀随 agent 变化；从终端 `~/.tokeneconomizer/bin/te <cmd>` 不消耗 model turn，在 agent 内敲会消耗一个（F-101）。

## 2. 读 `microskills` 时该问的三件事

1. 一条事实是 **Confirmed** 还是仍在 Candidate？论文要求 3 个「编辑文件互不重叠」的任务确认（F-053）。
2. 它是否被注入？need gate 要求在 ≥4 次触发上 need rate ≥0.4（F-054）。
3. 有没有事实被退休？附录 H 记录约 1/5 提议技能在流内被退休（F-059）——**看到退休是正常现象，不是故障**。

## 3. 读 `toolprune` 时该问的三件事

1. 核心工具（shell、读 / 写 / 编辑）是否仍在？它们按设计永不移除（F-060）。
2. 屏蔽证据是否满足插件阈值：10 个未调用 prompt 跨 ≥2 个 session，或跨 5 个 session 任意长度（F-097）。
3. deny list 是已生效还是仅提议？若设置文件不可安全修改，插件只提议并说明原因，`toolprune apply` 可重试（README）。

需要归还时 `toolprune restore`；归还的工具不会再被移除。另有 `toolprune=propose` 模式：只提议、不改动，直到显式 `apply`。

## 4. 六步「按论文全栈对齐」

> 对齐的是**机制开关**，不是数值参数。论文按 task 计、插件按 prompt/session 计，阈值不可逐项映射（[参数分账台账](../references/parameter-ledger.md)）。

| 步 | 动作 | 依据 |
|---|---|---|
| 1 | `config set microskills=on` | 默认 off（F-096） |
| 2 | 确认 `toolprune=on`、`loopguard=on` | F-096 |
| 3 | 明确接受「插件不会自行停止 turn」，headless 配外层超时 | F-100 |
| 4 | 观察至少 6 个任务再判断成本是否回落 | F-086 |
| 5 | `config` 存档本仓实际生效值 | F-101 |
| 6 | 标注「开关已对齐、数值口径未对齐」 | 台账第 2 节 |

调参形状（README 示例，Claude Code 形式）：

```text
/tokeneconomizer:config set microskills=on
/tokeneconomizer:config set microskills_propose_every=5
/tokeneconomizer:config set toolprune_evidence=20
/tokeneconomizer:config set loopguard_nudges=2
```

单次会话可用 `TE_DISABLE=1` 整体关闭，或 `TE_MICROSKILLS` / `TE_TOOLPRUNE` / `TE_LOOPGUARD` 单独关闭；`--global` 让设置作用于全部仓库。

## 5. 附录 H 活动计数的观测口径

论文表 6 / 表 7 给出组合变体每六仓库流的均值，可作为「机制是否真的在动」的定性参照（**不是本机期望值**）：

| 列 | Sonnet 5 / Combined | Opus 4.8 / Combined | 单位 |
|---|---|---|---|
| Proposed | 12.1 | 10.3 | skills / stream |
| Confirmed | 8.4 | 7.1 | skills / stream |
| Needed | 301 | 241 | tasks / stream |
| Retired | 2.6 | 2.2 | skills / stream |
| Masked | 14.8 | 14.5 | schemas / stream（流末时点值） |
| Re-audits | 3.1 | 4.3 | tasks / stream |
| Judged | 9.9 | 12.2 | consultations / stream |
| Redirects | 3.9 | 5.3 | redirects / stream |
| Aborts | 2.0 | 2.2 | terminations / stream |

三条读表纪律（论文表 7 明示）：

- `Needed` 单位是任务，会比 `Confirmed` 大 33–37 倍，**不可与技能数直接比较**；
- `Masked` 是流末仍屏蔽的 schema 数（时点值），`Re-audits` 是任务数（累计值），两者不可比；
- judge 被咨询 9.9–13.1 次而 redirect 只有 3.9–5.3 次，说明多数升级得到「仍在推进 / 不确定」结论——**judge 调用多不等于打断多**。

## 6. headless 的额外检查

`claude -p` / `codex exec` / `copilot -p` 等无人值守运行里，被标记的 turn 会一直跑到 agent 自身上限（F-100）。检查：

- [ ] 外层是否有任务级超时或中止机制；
- [ ] `codex exec` 不打印 hook 消息、Claude Code 的插件行只在详细 transcript（Ctrl+O）里，提示可能被模型改写或漏掉；
- [ ] 事后 `te status` 里的 redirects / still-stuck 计数是否纳入观测指标。

## 7. 什么时候判定「不划算」

若项目任务数少于 6 个、每个任务都在新仓库、或轨迹本身很短，经验复用的空间有限（F-086、F-071、F-091）。此时应关闭策略或整体不上，而不是把论文均值当目标去调参。完整判据见 [局限与落地判据](../concepts/09-limits-and-adoption.md)。
