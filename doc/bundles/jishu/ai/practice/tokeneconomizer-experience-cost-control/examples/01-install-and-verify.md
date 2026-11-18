---
type: Example
title: "示例一：安装与验证（官方文档转述，本束未实测）"
description: "四种稳定 agent 的安装命令族、信任与 hooks 生效步骤、status 验证、refresh-catalog 与常见坑"
tags: [安装, 验证, 未实测, Claude Code, Codex, Copilot CLI, Pi]
status: stable
stale_after: 2027-02-28
generated: { by: "reference_agent/seven-concepts-a", at: "2026-11-17T12:45:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-17T12:45:00+08:00" }
sources:
  - id: repo
    resource: https://github.com/microsoft/TokenEconomizer
  - id: facts
    resource: ../references/article-source.md
---

# 示例一：安装与验证

> **⚠️ 未实测声明**：以下命令逐字转述自 `microsoft/TokenEconomizer` README（采集日 2026-11-17）。本束**未安装、未运行、未验证**任何一步。命令与版本区间随仓库更新会变，动手前请回读 README 的 Install / Supported versions 两节。本示例是「读文档得到的检查清单」，不是运行记录。

## 0. 前置检查

| 检查项 | 要求 | 依据 |
|---|---|---|
| Python | 3.10+ 且在 `PATH` 上 | F-094 |
| agent 登录 | 任意该 agent 支持的方式 | F-094 |
| API key | 插件**不需要**自己的 key，不处理凭据 | F-094 |
| clone 位置 | 留给 Claude Code / Codex / Copilot CLI / opencode 从本地运行，不要装完就删 | README Install |
| marketplace 路径 | 必须绝对路径；Copilot CLI 会把 `./TokenEconomizer` 当成 GitHub 仓库名 | README Install |
| 版本 | 落在 [术语表版本快照](../references/glossary.md) 的受测区间内 | F-103 |

## 1. 安装（三选一，均在打算保留 clone 的目录执行）

```sh
git clone https://github.com/microsoft/TokenEconomizer.git

# Claude Code
claude plugin marketplace add "$PWD/TokenEconomizer"
claude plugin install tokeneconomizer@tokeneconomizer

# Codex
codex plugin marketplace add "$PWD/TokenEconomizer"
codex plugin add tokeneconomizer@tokeneconomizer

# GitHub Copilot CLI
copilot plugin marketplace add "$PWD/TokenEconomizer"
copilot plugin install tokeneconomizer@tokeneconomizer
```

Pi 的路径不同：`pi install git:github.com/microsoft/TokenEconomizer`。

## 2. 信任与首次验证

| Agent | 首次动作 | 状态命令 | 额外一次 |
|---|---|---|---|
| Claude Code | 启动 `claude` → 选「Yes, I trust this folder」→ 允许脚本 | `/tokeneconomizer:status` | `/tokeneconomizer:toolprune refresh-catalog` |
| Codex | 启动 `codex` → Trust and continue → Hooks need review 选 Trust all and continue；**hooks 下次会话才生效**，先 `/exit` 再启动 | `$tokeneconomizer:status` | — |
| Copilot CLI | 启动 `copilot` → Yes, and remember this folder → 允许脚本 | `/tokeneconomizer:status` | `/tokeneconomizer:toolprune refresh-catalog` |
| Pi | 启动 `pi` | `/te status` | — |

`refresh-catalog` 不调用模型，作用是记录会话加载过的全部工具，让工具剪枝有完整目录可评估。README 说明「每台机器一次，agent 更新后再跑一次」。

状态命令成功时会打印一段简短状态块；在 agent 内敲一次命令消耗一个 model turn，从终端 `~/.tokeneconomizer/bin/te <cmd>` 敲则不消耗（F-101）。

## 3. 「默认 ≠ 论文全栈」检查（最容易被跳过的一步）

装完不等于拿到论文效果。逐项确认：

| # | 检查 | 期望 | 依据 |
|---|---|---|---|
| 1 | `config` 打印 `microskills` | 默认 **off** | F-096 |
| 2 | `config` 打印 `toolprune` / `loopguard` | 默认 on | F-096 |
| 3 | 是否接受「插件不会自行停止 turn」 | headless 需外层超时 | F-100 |
| 4 | 是否打算按论文全栈对齐 | 若需，`config set microskills=on` | [参数台账第 4 节](../references/parameter-ledger.md) |
| 5 | 是否记录基线成本与质量 | 启用前先记 | [落地检查表](../concepts/09-limits-and-adoption.md) |

**不要**把 README 的 `k=3` 当成论文确认阈值，也不要把 18.4–30.9% 当作安装后的承诺（F-079、F-109）。

## 4. 常见坑（README 明示）

- Codex 0.141.0 之前完全不运行插件 hooks；hooks 改动必须重启会话才生效。
- Cursor Agent 实验性支持仅 macOS / Linux：Windows 上 hook 走 PowerShell，而插件启动器是 POSIX shell 脚本。
- Grok Build 的 learned facts 随会话**第一次工具调用**到达模型，不在会话起始；且没有工具剪枝。
- Antigravity CLI 只支持不调用模型的微技能事实，命令需从终端跑（Windows 用 `<plugin>\scripts\te.cmd --host antigravity status`）。
- Factory Droid 的 hooks 在启动时快照，安装后必须开新会话；TUI 无持久化 per-tool 设置，工具剪枝不可用。
- Hermes Agent 要 `ln -s` 链接而不是 `hermes plugins install`（后者会漏启动器并在安全扫描时拒绝整个仓库）。

## 5. 验收口径

本示例的「完成」定义为：**能打印出状态块，并能用 `config` 说清本仓三条机制各自的开关**。它不包含「成本下降了多少」——那需要至少 6 个任务的累积曲线（F-086）与成对的质量指标，属于 [示例二](02-status-and-tuning.md) 的观测范围。
