---
type: Concept
title: "插件与论文的分账：装上之后会得到什么"
description: "稳定 / 实验性支持矩阵、安装命令族、默认开关、常用命令、复现路径与「未实测」声明"
tags: [插件, 安装, 支持矩阵, 默认配置, 复现, 未实测]
status: stable
stale_after: 2027-02-28
generated: { by: "reference_agent/seven-concepts-rie", at: "2026-11-17T12:35:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-17T12:35:00+08:00" }
sources:
  - id: facts
    resource: ../references/article-source.md
  - id: repo
    resource: https://github.com/microsoft/TokenEconomizer
  - id: ledger
    resource: ../references/parameter-ledger.md
---

# 插件与论文的分账：装上之后会得到什么

> **⚠️ 未实测声明**：本页所有命令逐字转述自 `microsoft/TokenEconomizer` README，本束**未安装、未运行、未验证**任何一条。命令与受测版本区间随仓库更新会变，动手前请回读 README。可执行的检查清单见 [安装与验证示例](../examples/01-install-and-verify.md)。

## 两个不同的东西

| 维度 | 论文里的 TokenEconomizer | 开源插件 |
|---|---|---|
| 身份 | 实验用的外部控制器 | 可安装到日常 agent 的插件 |
| 目标 | 在 277 任务上测自适应成本控制 | 在开发者常驻仓库里省 token |
| 三条元策略 | 全开 | 默认开两条（micro-skills 关） |
| 卡住的 turn | 可 abort | 只提示，不自行停止 |
| 论文结果 | 18.4–30.9% | **README 不承诺任何降幅** |

事实编号 F-041、F-096、F-100、F-110。**把插件 README 里的数字当成「装上去就省 30%」的承诺是本束最想防住的误读。**

## 支持矩阵

| 类别 | Agent | 备注 |
|---|---|---|
| 稳定 | Claude Code、Codex、GitHub Copilot CLI、Pi | F-092 |
| 实验性 | opencode、Cursor Agent、Grok Build、Hermes Agent、Antigravity CLI、Factory Droid | F-093 |

能力并不齐整：Pi 只加载四个工具，所以工具剪枝什么都不移除；Grok Build 只有微技能与循环守卫，且学到的 fact 随会话**第一次工具调用**才到达模型；Antigravity CLI 只支持「不调用模型的微技能事实」；Factory Droid 的 TUI 没有持久化 per-tool 设置，工具剪枝不可用；Cursor Agent 仅 macOS / Linux（Windows 上 hook 走 PowerShell，插件启动器是 POSIX 脚本）。这些限制在 README 里逐条列出。

论文侧只测了 3 种 harness，§6 明确未覆盖 Pi 等精简 harness（F-107）——这是「实验覆盖」与「插件支持」的范围差异，不是矛盾。

## 前置条件与安装命令族

- Python 3.10+ 在 `PATH` 上；agent 以任意支持的方式登录；插件**不需要自己的 API key、不处理凭据**（F-094）。
- 学到的内容留在本机 `~/.tokeneconomizer`（F-095）。
- Claude Code / Codex / Copilot CLI / opencode 从 clone 目录运行插件，**clone 要留在原处**；marketplace 路径必须是绝对路径（Copilot CLI 会把 `./TokenEconomizer` 当成 GitHub 仓库名）。

三个主流 agent 的安装形状（README 原文转述）：

```sh
git clone https://github.com/microsoft/TokenEconomizer.git
# Claude Code
claude plugin marketplace add "$PWD/TokenEconomizer"
claude plugin install tokeneconomizer@tokeneconomizer
# Codex
codex plugin marketplace add "$PWD/TokenEconomizer"
codex plugin add tokeneconomizer@tokeneconomizer
# Copilot CLI
copilot plugin marketplace add "$PWD/TokenEconomizer"
copilot plugin install tokeneconomizer@tokeneconomizer
```

随后在目标仓库里启动 agent、信任该文件夹；Claude Code 与 Copilot CLI 运行 `/tokeneconomizer:status`，Codex 因 hooks 到下次会话才生效需先 `/exit` 再用 `$tokeneconomizer:status` 确认。Claude Code 与 Copilot CLI 每台机器（以及每次 agent 更新后）还要跑一次 `/tokeneconomizer:toolprune refresh-catalog`。Pi 用 `pi install git:github.com/microsoft/TokenEconomizer` 与 `/te status`。

## 默认开关与常用命令

| 机制 | 默认 | 说明 |
|---|---|---|
| `toolprune` | on | 默认开启 |
| `loopguard` | on | 默认开启；仅在 turn 出现循环迹象时才调用模型 |
| `microskills` | **off** | 提议器增加模型调用，收益取决于仓库与工作（F-096） |

| 命令 | 作用 |
|---|---|
| `status` | 本仓学到了什么、做了什么、会话花了多少 |
| `microskills` | 已注入的事实与仍在形成的事实 |
| `toolprune` | 被排除的工具与证据（部分 agent 不可用） |
| `toolprune restore` | 归还工具，此后不再移除 |
| `config` | 列出全部生效设置 |
| `config set microskills=on` | 打开一个机制；`--global` 作用于全部仓库 |

命令前缀随 agent 变化：Claude Code / Copilot CLI 用 `/tokeneconomizer:<cmd>`，Codex 用 `$tokeneconomizer:<cmd>`，Pi 用 `/te <cmd>`，其余从终端用 `~/.tokeneconomizer/bin/te --host <name> <cmd>`。**在 agent 内敲一次命令消耗一个 model turn，从终端敲不消耗。**

单次会话可用环境变量调整：`TE_DISABLE=1` 整体关闭，`TE_LOOPGUARD=off`、`TE_MICROSKILLS`、`TE_TOOLPRUNE` 单独关闭。

## 失败与降级行为

- 每个动作以一行公告；**任一部件失败，会话按未安装插件的方式继续**（F-098）。
- fact proposer 与 judge / redirect 的模型调用走用户自己的 agent 与同一登录或套餐，成本计入报告（F-099）。
- deny list 只加自己的条目、不碰用户手写规则；设置文件被 `.git/info/exclude` 排除。

## 想按论文全栈对齐

打开 `microskills=on`，确认另两条为 on，并明确接受「插件不会自行停止 turn」这一行为差异。但要注意：**对齐的是机制开关，不是数值参数**——论文按 task 计，插件按 prompt / session 计，两套阈值不可逐项映射。逐行对照见 [参数分账台账](../references/parameter-ledger.md)，六步检查清单在该页第 4 节。

## 复现论文结果

`experiments/` 提供论文结果背后的 harness、launcher 与任务集，README 说「每个结果一条命令」；它与已安装插件只共享 `tokeneconomizer/` 包，**不是插件的一部分**（F-104）。包仅用标准库，测试用 `python -m pytest tests`（F-105）。本束未运行这些命令，因此不声称任何复现结论。
