---
type: Reference
title: "TokenEconomizer 术语表与版本快照"
description: "黑盒成本控制、三种元策略、成本口径与受测版本区间的术语对照"
tags: [术语表, 版本快照, 成本控制, 编码Agent]
status: stable
generated: { by: "reference_agent", at: "2026-11-17T12:25:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-17T12:25:00+08:00" }
sources:
  - id: paper
    resource: https://arxiv.org/html/2610.22732v1
  - id: repo
    resource: https://github.com/microsoft/TokenEconomizer
  - id: facts
    resource: ./article-source.md
---

# 术语表与版本快照

## 1. 核心术语

| 术语 | 英文 / 符号 | 本束采用的定义 | 事实编号 |
|---|---|---|---|
| 黑盒成本控制 | black-box cost control | 不改模型权重与 agent-loop 代码，只通过指令前缀、已加载工具、实时事件流三个既有接口施加控制 | F-041、F-042 |
| 元策略 | meta-strategy | 三条环境无关的过程：微技能注入、工具剪枝、失败循环干预 | F-040 |
| 策略 | policy | 元策略在某个环境中学到的具体决策（注入哪些事实、屏蔽哪些工具、何时干预） | F-040 |
| 固定策略 | fixed strategy | 在所有环境套用同一配置的降本手段，如 RTK、Serena、RepoMap | F-040、F-030 |
| 任务流 | task stream | 同一环境内按时间排序的任务序列 τ₁…τₙ | F-043 |
| 控制器状态 | Sᵢ | 由该仓库已完成任务轨迹蒸馏出的状态，供下一任务使用 | F-045 |
| 微技能 | micro-skill | 一行仓库专属事实 + 可执行 detectors，经证据门控后才注入起始上下文 | F-051、F-053 |
| detectors | detectors | 每条微技能附带的可执行检验，任务后判断确认 / 矛盾 / 是否需要，不调用模型 | F-052 |
| 支持度 | qᵢ(f) | 按 γ 衰减加权、矛盾按 λ 放大的证据分数，小于 0 即永久退休 | F-055、F-056 |
| 工具剪枝 | tool pruning | 屏蔽仓库历史表明不会用到的工具，始终保留 shell 与文件读写编辑类核心工具 | F-060、F-061 |
| 复审 | re-audit | 每 5 个任务恢复完整工具目录；期间被调用的工具此后不再屏蔽 | F-063 |
| 失败循环干预 | failure-loop intervention / loop guard | 规则层监视重复失败，judge 判定卡住后写入 redirect | F-067、F-068 |
| 轮次预算 | Bᵢ | 该仓库已成功轨迹轮数的 90 分位 × 1.25 | F-066 |
| redirect | redirect | 一条附「已尝试什么」摘要的短提示，建议换一种做法 | F-068 |
| 缓存感知成本 | cache-aware cost | 按未缓存输入 / 缓存输入 / 输出分别加权，并叠加控制器自身调用成本 | F-049 |
| Pass@1 | Pass@1 | SWE-Bench 官方 grader 下的单次通过率 | F-077 |
| 累积 Pass@2 | cumulative Pass@2 | Web-Bench 原基准推荐的质量指标 | F-077 |
| 锚点组 | — | 本知识库计数规则：目录直接含 concepts/examples/references 之一即计 1 束（见 log.md） | — |

## 2. 三条元策略的作用面

| 元策略 | 作用面 | 时机 | 是否调用模型 |
|---|---|---|---|
| 微技能注入 | 知识（指令前缀） | 任务之间 | 提议器调用；detectors 不调用 |
| 工具剪枝 | 接口（已加载工具集） | 每个任务之前 | judge 评审时调用 |
| 失败循环干预 | 控制（实时 rollout） | 轨迹运行期间 | 规则层不调用；judge 与 redirect 写入时调用 |

## 3. 版本快照（易过期信息）

> 以下取自仓库 README「Supported versions」，仅在采集日 2026-11-17 有效；README 明确写出「更新版本尚未测试」。

| Agent | 受测版本区间 | 备注 |
|---|---|---|
| Claude Code | 2.1.300 – 2.1.310 | 旧版不支持 |
| Codex | 0.153.1 – 0.164.0 | 0.141.0 之前完全不运行插件 hooks |
| GitHub Copilot CLI | 1.0.83 – 1.0.102 | 旧版不支持 |
| Pi | 1.2.0 – 1.3.0 | 0.99.x 需按路径加载扩展 |
| Cursor Agent（实验） | 3.24.9 / cursor-agent 2026.11.05 | 仅 macOS、Linux |
| Grok Build（实验） | 1.0.70 | — |
| opencode（实验） | 1.19.5 / 2.2.0 | 2.x 终端 UI 未测 |
| Hermes Agent（实验） | 0.22.5 | 仅经典 CLI 与一次性运行 |
| Antigravity CLI（实验） | agy 1.5.1 / 1.5.2 | Windows 11 / macOS / Linux |
| Factory Droid（实验） | 0.233.0 | 仅 macOS |

**论文侧版本口径**：§6 明确实验只覆盖三种广泛使用的编码 agent，未覆盖 Pi 等更精简 harness（F-107）；插件稳定支持列表含 Pi（F-092）。两者是「实验覆盖范围」与「插件支持范围」的差异，不是矛盾。

## 4. 易混写的三组数字

| 容易混 | 正确读法 |
|---|---|
| 18.4–30.9% 与 5.2–40.1% | 前者是五个组合的平均降本，后者是 30 个仓库×组合 cell 的降本区间 |
| 16.9–32.0% 与 18.4–30.9% | 前者是累积成本曲线终点的节省，后者是平均单任务降本 |
| 6.4–21.2% 与 6.4–19.6% | 前者是论文摘要把三类基准合并的区间；后者是博客对两个安全基准的合并区间。逐基准数字见表 2(b) |
