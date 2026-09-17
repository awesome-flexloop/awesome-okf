---
okf_version: "0.2"
type: bundle
title: LoopX 长程 Agent 控制面——让 AI Agent 跨天跑、可复盘、不空烧
description: 国产开源 LoopX 状态内核教程（极客之家博文核验转化）——本地优先控制面、quota 计费闸门、人类门禁、dashboard、200h OpenViking 证据与安装实操
tags: [loopx, agent-control-plane, long-horizon, loop-engineering, quota, human-gate, codex, claude-code, cursor, deepseek-harness]
generated:
  by: trae-solo-agent
  at: "2026-09-16T20:40:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-16T21:10:00+08:00"
status: stable
stale_after: "2026-11-30"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/BzxrklBhyJBWjhupDtcgVQ
  - id: github-loopx
    url: https://github.com/huangruiteng/loopx
  - id: pypi-loopx
    url: https://pypi.org/project/loopx/
  - id: openviking
    url: https://github.com/volcengine/OpenViking
  - id: ts-migration-rfc
    url: https://github.com/huangruiteng/loopx/blob/main/docs/architecture/rfcs/typescript-control-plane-migration-v0.md
---

# LoopX 长程 Agent 控制面——让 AI Agent 跨天跑、可复盘、不空烧

> **类型**：开源工具教程（第三方推荐博文 + 一手轻量实测，经官方四源核验转化）
> **信源**：微信公众号「极客之家」2026-09-03 推文（作者丛林，2777 字）+ GitHub 仓库/PyPI/OpenViking/TS 迁移 RFC（核验日 2026-09-16）
> **P0 核验**：12 项声明 ✅ 10 / ⚠️ 2 / ❌ 0（两项均为版本时效口径：v0.4.x 滞后、纯 Python→TS 内核演进，正文双口径呈现）

## 本文概要

LoopX 是一个**开源、供应商中立、本地优先的长程 Agent 控制面（状态内核）**：Claude Code、Codex、Cursor 等宿主照常逐轮干活，LoopX 在其上持久管理目标（objective）、门禁（gates）、待办（todos）、证据（evidence）与配额（quota），解决长周期任务三大痛点——上下文丢失目标、该确认时不停、无进展时空烧 token。其代表证据是作者在火山引擎 OpenViking 仓库的 **169 个公开 PR、跨度 200+ 自然小时**的贡献序列，并明确标注"非连续运行、非无人值守"边界。

> ⚠️ **时效提示（先读）**：博文写于 0.5.4 时代（文中称 v0.4.x 已滞后）；核验时最新为 **1.0.5（2026-09-15）**，1.0 起内核迁移 TypeScript，**安装新增 Node.js 22.18+ 前置**。机制与命令在 1.0 保持不变。详见 [verification.md](references/verification.md)。

## 文档结构

### concepts/ — 概念解析

| 文档 | 主题 |
|------|------|
| [00-loopx-overview.md](concepts/00-loopx-overview.md) | 定位与分工、仓库热度（5818 star/Apache-2.0）、纯 Python→TS 内核的版本演进 |
| [01-control-plane-mechanism.md](concepts/01-control-plane-mechanism.md) | 状态五问、quota should-run 计费闸门、具体人类门禁、dashboard 工作台、多宿主接入表 |
| [02-evidence-and-fit.md](concepts/02-evidence-and-fit.md) | OpenViking 200h 公开序列与边界、证据四级分层、五类适用场景与适配三问 |

### examples/ — 实操示例

| 文档 | 主题 |
|------|------|
| [00-install-and-doctor.md](examples/00-install-and-doctor.md) | Python/Node 前置、安装三命令、重启宿主、doctor 通过判据、常见报错 |
| [01-connect-goal-dashboard.md](examples/01-connect-goal-dashboard.md) | connect/start-goal --guided/status/dashboard、宿主进环、每日巡检三命令、gitignore |

### references/ — 信源登记

| 文档 | 说明 |
|------|------|
| [article-source.md](references/article-source.md) | F-001~F-049 事实清单（博文 36 条 + 核验补充 13 条，双份登记） |
| [verification.md](references/verification.md) | 12 项 P0 核验记录、勘误两张表、核验方法与未覆盖边界 |

## 主题关联

- [Codex Agent 工作流实践](../codex-agent-workflow-practices/index.md)：Codex CLI 降本工作流实测——LoopX 提供跨轮治理层，二者是"运行时实践 × 长程控制面"互补
- [planning-with-files 像 Manus 一样工作](../planning-with-files/index.md)：3-File Pattern 文件系统外存——与 LoopX 本地状态内核同属"上下文工程/外存化"路线
- [上下文优化 Context Optimization](../context-optimization/index.md)：Token 成本优化全景——quota should-run 是治理侧的 token 节流机制
- [AI 工程方法论](../ai-engineering-methodology/index.md)：Harness 工程与 Agent 评测谱系——LoopX 的 loop engineering 是该谱系的产品化实例
- [Agent 平台散篇笔记](../agent-platform-notes/index.md)：多平台工具散篇聚合，可对照 LoopX 在同类产品中的位置

## 已知边界

- **版本强时效**：1.0（2026-09-06）刚发布且周级迭代；内核 TypeScript 迁移 RFC 状态仍为 Accepted/进行中，Node 要求与桌面端形态可能再变，stale_after（2026-11-30）前须复核
- **博文版本口径**："v0.4.x 阶段""纯 Python"为 0.4/0.5 时点口径，正文已按"博文时点 / 核验时点"双标注，引用请勿退回旧口径
- **未真机实测**：examples 命令经官方文档逐字比对但本包制作中未执行；200h 证据以公开 PR 序列存在性与官方边界声明为核验限，未逐一复核任务图
- **无遥测口径**：依据官方反馈模板声明（"contains no telemetry"），未做源码级审计
- **观点分层**：场景归纳、"大概率要火"等为博文作者观点（P2 单源），已在正文显式标注，不作为事实引用

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
