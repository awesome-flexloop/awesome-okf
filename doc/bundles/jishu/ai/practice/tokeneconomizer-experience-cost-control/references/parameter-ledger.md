---
type: Reference
title: "参数分账台账：论文实验配置 vs 开源插件默认值"
description: "逐项对照 arXiv:2610.22732 控制器配置表 4 与 microsoft/TokenEconomizer README Settings 表，标出同名异义、同义同值与行为差异"
tags: [参数对照, 口径分账, 复现, TokenEconomizer, 控制器配置]
status: stable
generated: { by: "reference_agent/seven-concepts-e", at: "2026-11-17T12:25:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-17T12:25:00+08:00" }
sources:
  - id: paper
    resource: https://arxiv.org/html/2610.22732v1
    title: "论文表 4 Controller configuration"
  - id: project
    resource: https://tokeneconomizer.github.io
    title: "项目页 Method / Step by step settings"
  - id: repo
    resource: https://github.com/microsoft/TokenEconomizer
    title: "仓库 README Settings 表"
---

# 参数分账台账

> **为什么单独一页**：论文与项目页用斜体字母描述**实验控制器**，仓库 README 用同名斜体字母描述**插件默认设置**。两处字母集合部分重叠，含义却不同。把两张表合并成一张，会得出「插件默认就是论文配置」的错误结论（核验报告 D-2、D-3）。本页按「冲突数字并存不合并抹平」的纪律，逐行分账。

## 1. 两套配置的性质

| 维度 | 论文实验控制器 | 开源插件 |
|---|---|---|
| 目的 | 在 277 个 SWE-Bench 任务上测量自适应成本控制的效果 | 在开发者日常仓库会话中运行 |
| 配置固定方式 | 主实验前在开发运行上定死，六个仓库、五个项目共用一套值，不逐环境调参（F-070、附录 C） | 每个机制可 `config set` 单独开关，支持 `--global` 与单会话环境变量 |
| 任务单元 | 每个任务一个独立会话 | 开发者真实会话，一个 turn 内可有多轮 |
| 数据位置 | 论文未描述持久化路径 | `~/.tokeneconomizer`（F-095） |

## 2. 逐项对照

| 符号 / 设置 | 论文实验配置（表 4 / 项目页） | 插件默认（README Settings） | 关系判定 |
|---|---|---|---|
| `k` | 工具连续 **3 个任务**未调用即进入剪枝候选 | `microskills_propose_every` = **3**（每隔几个 session 跑一次事实提议器） | ⚠️ **同名异义**：数值同为 3，一个管工具、一个管提议频率 |
| `p` | 成功轨迹轮数的 **90 分位**（预算分位数） | `toolprune_evidence` = **10**（工具须未经调用的 prompt 数） | ⚠️ **同名异义** |
| `T` | proposer cadence = 每 **5 个任务** | 无对应项；插件用 session 计数 | 单位不同（task vs session） |
| `n` | 确认阈值 = **3 次**「编辑文件互不重叠」的任务 | 博客写「several sessions have confirmed」；README 未给同名设置 | ⚠️ 近似但口径不同（论文要求编辑集不重叠） |
| `ρ` | need gate：≥4 次触发上 need rate **≥0.4** | README 未列 | 仅实验侧 |
| `γ` | 支持度衰减 **0.8 / task**（式 2） | README 未列 | 仅实验侧 |
| `λ` | 一次矛盾计 **5 次**确认（式 2） | README 未列 | 仅实验侧 |
| 剪枝移除条件 | 连续 3 个任务未调用 + 逐任务 LLM judge | 未调用达 **10 个 prompt** 且跨 **≥2 个 session**，或跨 **5 个 session** 任意长度 | ⚠️ 规则不同 |
| 剪枝恢复 | 每 **5 个任务**恢复全目录复审；复审中被调用者此后不再屏蔽 | `toolprune restore` 手动归还；`toolprune=propose` 先只提议 | ⚠️ 自动复审 vs 手动恢复 |
| `m` `s` `q` | 无对应项 | `toolprune_min_sessions`=2、`toolprune_sessions`=5、`toolprune_quiet_minutes`=60（写入 deny list 前需空闲 60 分钟） | 仅插件侧 |
| `β` | **1.25** × 成功轨迹轮数 90 分位（式 3） | README 未列 | 仅实验侧 |
| `c` | judge 判 stuck 的置信度 **0.7** | `loopguard.judge_confidence` = **0.7** | ✅ 同义同值 |
| `r` | Redirects **1, then stop** | `loopguard_nudges` = **1**（之后只提示开发者） | ⚠️ **值同、行为不同**：论文会 abort，插件从不自行停止 |
| `κ` / `b` | 强制停止倍数 **2.5**（严格停滞规则成立时） | `loopguard.backstop_mult` = **2.5** | ✅ 近似同义同值 |
| `e` | 无同名项；Web-Bench 用预注册 30 轮预算直到 5 个任务通过 | `loopguard.envelope_min_samples` = **5**（本仓需 5 个正常结束的 turn 才启用守卫） | ⚠️ 数值同为 5，语义不同 |
| micro-skills 开关 | 三条元策略**全开** | 默认 **off**（提议器会增加模型调用） | 🔴 **重大差异** |
| toolprune / loopguard 开关 | 全开 | 默认 **on / on** | ✅ 一致 |
| 循环干预终态 | judge 后仍循环则 **stop / abort**（附录 H 记录每流 1.4–2.2 次 abort） | 提示开发者如何停止，**不自行停止** | 🔴 **重大差异** |
| `droid_sidecall` | 无 | 默认 off | 仅插件侧 |

## 3. 三处最容易踩的坑

1. **照抄字母**：看到 README 的 `k=3` 就以为论文工具剪枝阈值是 3 个 prompt。论文是 3 个任务，插件是 10 个 prompt 跨 2 个 session。
2. **照抄默认就宣称复现**：插件默认关闭 micro-skills，而论文全栈三条全开（F-096、F-110）。开箱即用的插件不是论文实验配置。
3. **以为插件会替你刹车**：论文控制器会 abort，开源插件只给一行提示（F-100）。headless 运行时没人看提示，被标记的 turn 会一直跑到 agent 自身上限。

## 4. 按论文全栈对齐插件时的检查清单

| 步骤 | 动作 | 依据 |
|---|---|---|
| 1 | `config set microskills=on` | F-096 默认 off |
| 2 | 确认 `toolprune=on`、`loopguard=on` | F-096 |
| 3 | 明确接受「插件不会自行停止 turn」这一行为差异，改为人工或外层超时兜底 | F-100 |
| 4 | 用 `status` 观察至少 6 个任务后再判断成本是否回落 | F-086 第 6 个任务起回本 |
| 5 | 逐项记录本仓实际生效值：`config` | F-101 |
| 6 | 标注「对齐的是机制开关，不是数值参数」——两套阈值口径不可逐项映射 | 本页第 2 节 |

> 上述 6 步是**读文档得出的检查项**，不是本束实测结论。插件安装与运行在本环境未执行。
