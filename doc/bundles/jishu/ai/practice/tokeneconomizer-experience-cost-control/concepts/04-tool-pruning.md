---
type: Concept
title: "工具剪枝：按仓库证据收窄接口"
description: "核心工具保护、两条屏蔽路径、每 5 任务全目录复审、按 agent 的设置文件写入位置与插件默认阈值"
tags: [工具剪枝, 接口收窄, 可逆性, MCP, 插件配置]
status: stable
stale_after: 2027-02-28
generated: { by: "reference_agent/seven-concepts-rie", at: "2026-11-17T12:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-17T12:30:00+08:00" }
sources:
  - id: facts
    resource: ../references/article-source.md
  - id: project
    resource: https://tokeneconomizer.github.io
  - id: repo
    resource: https://github.com/microsoft/TokenEconomizer
---

# 工具剪枝：按仓库证据收窄接口

## 为什么这条最有效

每轮请求都会把**每个已加载工具的描述**重新发一遍（F-015）。剖析显示：23 个 schema 里 16 个从未被调用，没有任何仓库调用超过 7 个，3 个工具占全部调用的 98%（F-022 ~ F-025）。工具剪枝因此作用在**每一轮**、而不是只在某几轮——消融里它单独贡献的节省最大（F-087、F-088），项目页也把它解释为「因为它作用于每个 turn」。

## 论文实验里的四步

| 步骤 | 规则 | 事实编号 |
|---|---|---|
| 1. 保护核心 | shell 执行与文件读 / 写 / 编辑类工具始终保留 | F-060 |
| 2. 按证据屏蔽 | 工具连续 3 个任务未被调用，进入候选 | F-061 |
| 3. 按相关性评审 | LLM judge 结合任务描述判断该工具是否确实无关；评审时把指向 PR / issue / commit / 文件的链接屏蔽掉，避免 judge 靠链接猜答案 | F-061、F-062 |
| 4. 定期复审 | 每 5 个任务恢复完整工具目录；复审期间被调用过的工具此后不再屏蔽 | F-063 |

第 3 步的「屏蔽链接」是一个容易被略过、但很说明问题的细节：judge 要做的是判断**任务性质**是否需要这个工具，而不是顺着任务描述里的仓库链接去推断答案。第 4 步则给出误判的恢复通道——一个被错剪的工具，最多等一轮复审就会回来。

剪枝单位按 harness 而定：一般是单个 tool，Codex 上是 capability package（F-064）。

## 开源插件的落点

插件把 deny list 写进 **agent 自己的设置文件**，不同 harness 位置不同（F-102）：

| Agent | 剪枝能移除什么 | 写入位置 |
|---|---|---|
| Claude Code | 单个工具 | `.claude/settings.local.json` |
| Codex | capability packages | `.codex/config.toml` |
| Copilot CLI | 整个 MCP server | `.github/copilot/settings.local.json` |
| Pi / Cursor / Grok / opencode / Hermes / Antigravity / Droid | 尚不能移除（或 TUI 无持久化 per-tool 设置） | — |

几条工程约束（仓库 README）：

- 插件只添加自己的条目，**不碰用户手写的 deny 规则**；它创建的设置文件通过 `.git/info/exclude` 排除在版本控制之外。
- `toolprune restore` 只移除插件的条目，归还的工具不会再被剪掉。
- 若设置文件不安全可改（仓库提交了 `.codex/config.toml`、JSON 无效、符号链接指向仓库外），deny list 只作为**提议**保留，会话起始会说明原因，`toolprune apply` 可重试。
- `refresh-catalog` 会在不调用模型的前提下记录会话加载过的全部工具，让剪枝有完整目录可评估。
- 写入 deny list 前要求该仓库会话空闲 60 分钟（F-097 的 `toolprune_quiet_minutes`）：工具集变化会让会话把整段历史重新写进 prompt cache，空闲一小时后缓存本来也已过期。

## 默认阈值与论文阈值的差异

| 维度 | 论文实验 | 插件默认 |
|---|---|---|
| 屏蔽证据 | 连续 3 个任务未调用 + 逐任务 judge | 10 个 prompt 未调用且跨 ≥2 个 session，或跨 5 个 session 任意长度 |
| 恢复 | 每 5 个任务自动全目录复审 | 手动 `toolprune restore`；`toolprune=propose` 只提议不生效 |
| 单位 | 任务（task） | prompt / session |

事实编号 F-061、F-063、F-097。这一组差异是 [参数分账台账](../references/parameter-ledger.md) 里最容易被误读的部分：插件把「长会话权重更高」写进了规则（按 prompt 计数），并要求至少 2 个 session，避免**单个会话独自决定**剪掉一个工具。

## 三个反模式

1. **全局固定裁剪**：按「通用最常用工具」给所有仓库发同一套精简目录。F-024 显示各仓最多用到 7 个工具，但用到的**不是同一批**；F-025 的 98% 集中在 3 个工具，剩下的稀疏且各仓不均。
2. **剪完不给恢复通道**：一旦剪错，后续任务会持续失败且无法自愈。论文的每 5 任务复审 + 插件的 `restore` 都是为此存在（F-063、F-101）。
3. **把剪枝效果当免费收益**：deny list 变化会打断 prompt cache，插件因此加了空闲期门槛（F-097）。忽略缓存代价，账面节省会被重新写入的历史吃掉。

> **读法提示**：工具剪枝是三条元策略里最「像配置管理」的一条，也最容易被误当成一次性的静态优化。它的正确形态是**带证据、带复审、带手动恢复接口的持续策略**。
