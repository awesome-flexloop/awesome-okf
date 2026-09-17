---
okf_version: "0.2"
type: Concept
title: LoopX 是什么——长程 Agent 的本地状态内核与控制面
description: LoopX 定位、与宿主 Agent 的分工、热度与许可、实现形态从纯 Python 到 TypeScript 内核的版本演进（含博文口径勘误）
tags: [loopx, control-plane, local-first, 状态内核, 版本演进]
generated:
  by: trae-solo-agent
  at: "2026-09-16T20:40:00+08:00"
status: stable
stale_after: "2026-11-30"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/BzxrklBhyJBWjhupDtcgVQ
  - id: github-loopx
    url: https://github.com/huangruiteng/loopx
  - id: pypi-loopx
    url: https://pypi.org/project/loopx/
  - id: ts-migration-rfc
    url: https://github.com/huangruiteng/loopx/blob/main/docs/architecture/rfcs/typescript-control-plane-migration-v0.md
---

# LoopX 是什么——长程 Agent 的本地状态内核与控制面

## 一句话定位

LoopX 是一个**开源、供应商中立、本地优先（local-first）的长程 Agent 控制面**：它不替代 Claude Code、Codex、Cursor 等 AI 编程工具，而是运行在它们之上，专门管理"跨轮次、跨天"的状态——目标是什么、卡在哪里、下一轮该谁做、每轮留下了什么证据、预算还剩多少（F-006、F-007）。

官方中文定位原句为："**把会干活的 Agent，接成可管理、可复盘、可持续改进的数字员工**"（F-009，PyPI/GitHub 项目描述逐字一致）；英文表述为 "The open, provider-neutral, stateful control plane for long-horizon agents"。

## 宿主负责干活，LoopX 负责治理

博文给出的分工类比与官方 README 的架构图一致：

- **宿主（harness）**：Codex、Claude Code、Cursor 等，在各自会话里执行"一轮"有界工作；
- **LoopX**：在宿主之上持有持久控制状态 `objective + gates + todos + scope + evidence + quota`，决定下一轮该不该动、问什么、交给谁。

官方特别声明它**不是又一个 Agent 框架，也不是供应商绑定的编排运行时**（"It is not another agent framework or a provider-specific orchestration runtime"）。这也是本知识包归入 ai 生态直挂束、而非 ai-agent 框架源码组的原因。

## 仓库热度与基本盘（核验时点 2026-09-13）

| 指标 | 值 | 出处 |
|---|---|---|
| 仓库 | github.com/huangruiteng/loopx（F-035） | 博文 + 官方 |
| Star / Fork | **5818 / 530**（F-037） | GitHub API 实测；博文 09-03 称"5000 多"，量级一致 ✅ |
| 许可 | Apache-2.0（F-037） | GitHub API |
| 创建时间 | 2026-05-31（F-037） | GitHub API——博文"开源不久"的表述成立 |
| 语言分布 | GitHub 统计主语言为 Python（F-037），但 1.0 起内核含 TypeScript（见下） | GitHub API + RFC |
| 社区面 | Discord、GitHub Discussions、Trendshift 上榜徽章 | README |

> **热度数字时效**：5818 为 2026-09-13 快照，star 处于快速增长期，引用时须带时点。

## 实现形态与版本演进（重要勘误，双口径阅读）

博文称 LoopX "纯 Python 写的"、项目"还在 v0.4.x 阶段"（F-008、F-033）。经 PyPI 时间线与官方 RFC 核验，需按两个时点理解：

**博文口径（2026-09-03 发文，作者安装体验更早）**

- 0.4.x/0.5.x 的 PyPI 包为**纯 Python 分发、零强制运行时依赖**（至今 1.0.5 的 `requires_dist` 仍无强制 runtime 依赖，deepseek-harness 仅为 optional extra）（F-038）；
- 但"v0.4.x 阶段"在发文当天已不准确：**0.5.0 于 2026-08-19 发布**，09-03 最新为 0.5.4（F-039，勘误①）。

**核验时口径（2026-09-16，最新 1.0.5）**

- **TypeScript 控制面迁移 RFC 已于 2026-08-15 获 Accepted**（早于博文 19 天），采用增量替换式迁移、不维护两套语义实现，核验时处于 transaction-payoff 阶段（F-041，勘误②）；
- **1.0 起**（1.0.0 发布于 2026-09-06，距博文 3 天）官方要求 **Python 3.11+ 且 Node.js 22.18.0+**（推荐 24 LTS）：Node 运行"托管的、空闲即退出的 TypeScript Effect 内核"，LoopX 负责自动启停（F-040）；
- 1.0 同步推出 **Personal Agent Workspace**（个人 Agent 工作台）：目标、注意力、会话、任务、文件、调度、恢复在同一本地工作区持久化，并提供浏览器/PWA 工作台与原生桌面预览版（F-049）。

版本线速览（PyPI upload 时间，F-038）：

```
0.4.8 (08-16) → 0.4.9/0.5.0 (08-19) → 0.5.4 (09-02)
→ 1.0.0 (09-06) → 1.0.5 (09-15)   # 核验时最新
```

> 阅读建议：博文中的安装与机制描述整体仍然成立（命令在 1.0 未变），但**安装前需额外准备 Node.js 22.18+**；"纯 Python"应理解为 0.4/0.5 时代的历史形态。

## 本地优先边界

"Local first"是项目徽章级承诺（F-010）：目标、范围、证据等状态写入项目本地的 `.loopx/`、`.codex/goals/`、`.local/` 等目录（官方要求将其加入 gitignore，F-046），不走云服务；浏览器/桌面界面只是状态的"投影"，**LoopX 状态文件本身才是权威来源**（"LoopX state—not the browser—remains authoritative"）。无遥测口径见 [01 机制篇](01-control-plane-mechanism.md) 与核验报告 F-047。

## 延伸阅读

- [01 控制面工作机制](01-control-plane-mechanism.md)——状态内核五问、quota 闸门、人类门禁、工作台与多宿主
- [02 200 小时证据与适用边界](02-evidence-and-fit.md)——OpenViking 公开序列、适用/不适用场景
- [verification.md](../references/verification.md)——两条勘误的完整核验记录
