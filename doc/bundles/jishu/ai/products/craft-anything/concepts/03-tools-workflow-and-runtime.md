---
okf_version: "0.2"
type: Concept
title: "工具、四步工作流与运行时"
description: "Craft Anything 的工具面（每个工具既是 CLI 子命令也是 MCP 工具）、Study→Build→Check→Ready 四步工作流、项目文件夹结构，以及 Claude Code / Codex 运行时现状"
tags: [craft-anything, cli, mcp, workflow, claude-code, codex, runtime]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-11-04T09:36:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-04T09:36:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/wB4MHVC4hOWPMobtVidniA"
  - id: github-repo
    url: "https://github.com/storytold/craft-anything"
  - id: official-status
    url: "https://github.com/storytold/craft-anything/blob/main/STATUS.md"
---

# 工具、四步工作流与运行时

## 四步工作流：Study → Build → Check → Ready

官方 README 把整件事定义为四个阶段（F-027）：

| 阶段 | 做什么 | 关联 |
|------|--------|------|
| **Study** | 观察目标软件如何工作：采集、结构化、行为探测 | 净室模式下强调"理解行为"（见 [01](01-clean-room-and-deep-modes.md)） |
| **Build** | 依据观察结果，让 AI 构建你自己的版本 | 运行时需 Claude Code（见下） |
| **Check** | 用可量化相似度比对原站 | 见 [02 · 相似度检查机制](02-likeness-checking-method.md) |
| **Ready** | 收敛到阈值后交付 | 最多 6 轮或达 90%（F-037） |

## 工具面：一个工具，两种入口

博文称项目有 **314 个工具**，且**每个工具既是 CLI 子命令，也是 MCP 工具**（F-017）。

这一设计意味着同一套能力可以两条路调用：

- **命令行**——直接以 `craft-anything-cli` 子命令驱动，适合脚本化与人工审阅；
- **MCP（Model Context Protocol）**——作为工具暴露给 AI Agent，让 Agent 在对话/编排中直接调用。

> **口径勘误（重要）**：工具总数**三源并存**——博文 **314**（F-017）；第三方 kitploit 亦称 314 CLI/MCP inspection tools（F-041）；官方 STATUS.md 则称 **300 个引擎工具（含 AI 与 setup 层共 320 个）**（F-036）。三者统计层不同（引擎层 vs 全部工具层），本包并列呈现，不合并为单一数字（见 [verification.md](../references/verification.md) 勘误②③）。

## 项目文件夹结构

官方 README 给出工作目录的组织方式（F-029），核心文件/目录包括：

| 路径 | 作用（据命名与官方说明） |
|------|------------------------|
| `craft.json` | 项目清单/配置 |
| `capture/` | 对目标软件的采集产物 |
| `app/` | 你构建出的应用 |
| `checks/` | 检查（相似度比对）相关产物 |
| `investigation.cany` | 探查结果文件 |
| `inbox/` | 待处理输入/暂存 |

> 上表"作用"列为**据命名与官方 README 上下文的说明**，非官方逐字段定义；精确语义使用时以官方文档为准。

## 构建命令与前置依赖

- **前置依赖**：**Rust 1.97+**（F-028）。
- **构建命令示例**：`craft-anything-cli rebuild`（F-029）——重建流程的 CLI 入口。

## 运行时现状：Claude Code 是当前路径

- 博文称**构建需安装并登录 Claude Code**（F-018）。
- 官方 STATUS.md 记载：live runs 使用 **Claude Code 2.1.316**，在一台 Mac 上（2026-11-02）（F-039）。
- 关于 **Codex 适配器**：博文称其**尚未在真实安装中验证**（F-019）——与官方 README Status 段的"Partly there"取向一致。

> 即：当前可用的"AI 施工队"路径是 Claude Code；Codex 支持仍在过渡中，正式使用前建议以官方状态为准。

## 工程健康度（官方自述）

官方 STATUS.md 记载：**2026-10-23 的基线审计中 923 项测试通过**（F-040），workspace clippy / layers / fmt 与全历史 secret scan 均为干净状态。这为早期 alpha 阶段的工程质量提供了一个官方口径的旁证。

## 阅读下一篇

- [04 · 安装与已知边界](04-install-and-known-limits.md)：安装包形态与早期 alpha 的能力边界
- [实操示例 · 安装与重建](../examples/00-install-and-run.md)：从下载安装到发起重建的步骤清单
