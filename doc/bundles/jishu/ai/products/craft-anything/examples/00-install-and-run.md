---
okf_version: "0.2"
type: Example
title: "实操：安装 Craft Anything 并跑一遍 Study → Ready"
description: "Craft Anything 的可照做上手流程——环境准备（Rust 1.97+ 与 Claude Code 登录）、获取安装包、初始化项目目录、走完 Study/Build/Check/Ready 四步、以 CLI 与 MCP 两种入口调用工具"
tags: [craft-anything, install, quickstart, cli, mcp, workflow]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-11-04T09:42:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-04T09:42:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/wB4MHVC4hOWPMobtVidniA"
  - id: github-repo
    url: "https://github.com/storytold/craft-anything"
  - id: github-releases
    url: "https://api.github.com/repos/storytold/craft-anything/releases"
  - id: official-status
    url: "https://github.com/storytold/craft-anything/blob/main/STATUS.md"
---

# 实操：安装 Craft Anything 并跑一遍 Study → Ready

> **可复现性说明**：本示例的输入（命令/依赖）、过程（步骤）、输出（可观察信号）明确，理论上可由独立执行者复现。**未在本机（Windows，未配置 Rust 1.97+ 与 Claude Code 登录态）实际运行**；命令与目录结构来自官方 README / STATUS.md 口径核对（见 [verification.md](../references/verification.md)），执行时以官方文档当前命令为准。
>
> **前置认知**：项目处于**早期 alpha**（v0.3.0，2026-11-02 发布），功能与命令可能快速变化。参见 [04 · 安装与已知边界](../concepts/04-install-and-known-limits.md)。

## 步骤 1 · 环境准备

两件事必须先满足：

| 依赖 | 要求 | 依据 |
|------|------|------|
| Rust 工具链 | **Rust 1.97+** | F-028 |
| AI 施工队运行时 | **安装并登录 Claude Code**（当前 live runs 使用 **2.1.316**） | F-018 / F-039 |

> Codex 适配器尚未在真实安装中验证（F-019），当前建议走 Claude Code 路径。

## 步骤 2 · 获取安装包

按平台选择分发形态（博文口径，F-023；部分已由 releases 资产核验，F-035）：

| 平台 | 形态 |
|------|------|
| Windows | `.msi` 安装包 / 便携版 |
| macOS | `.dmg` |
| Linux | AppImage / `.deb` / Flatpak |
| 浏览器 | WASM 查看器 |

已从 v0.3.0 releases 资产抓取到的样例包括：Linux `aarch64` AppImage（含 `.zsync`）、`.deb`、`.flatpak`、`.pkg.tar.zst`、`.rpm`、`.tar.gz`，以及 FreeBSD `aarch64` / `x86_64` `.tar.gz`。

> ⚠️ 上述为抓取样例，**未穷尽全部平台资产**。Windows/macOS/WASM 资产请在 [releases 页](https://github.com/storytold/craft-anything/releases) 现场核对。

## 步骤 3 · 初始化项目目录

官方 README 给出的工作目录组织（F-029）：

| 路径 | 作用 |
|------|------|
| `craft.json` | 项目清单/配置 |
| `capture/` | 对目标软件的采集产物 |
| `app/` | 你构建出的应用 |
| `checks/` | 相似度检查产物 |
| `investigation.cany` | 探查结果文件 |
| `inbox/` | 待处理输入/暂存 |

> "作用"列据命名与官方 README 上下文说明，非官方逐字段定义；精确语义以官方文档为准。

## 步骤 4 · Study（学习目标软件）

系统性地观察目标网站/应用/游戏如何工作：采集、结构化、行为探测（F-027）。

- **模式决定观察深度**：默认**净室（Clean room）**——只观察外部行为、不搬运原资产；如需更深入探查可切换**深度（Deep）**模式（后者仅博文单源，见 [01 · 两种模式](../concepts/01-clean-room-and-deep-modes.md)）。
- **工具受白名单约束**：过程中能被调用的工具受强制白名单限制（F-006，仅博文单源）。

## 步骤 5 · Build（让 AI 构建你的版本）

依据 Study 的观察结果，由 Claude Code 驱动 AI 重建你自己实现的版本（F-027）。

- CLI 入口示例：`craft-anything-cli rebuild`（F-029）。
- 官方口径：builder turns 单次最长可运行 **24 小时**（F-038）——适合长任务挂机重建。

## 步骤 6 · Check（量化比对）

用可量化相似度判定"像不像"（F-010~F-016 / F-037）：

1. 在 **1440 / 768 / 390 px** 三种宽度下比对；
2. 单页相似度 = **布局相似度**与**画面细节（SSIM）相似度**的**均值**；
3. 多页场景**跨页再平均**；
4. 迭代**最多 6 轮**，或任一网站达 **90%** 即停止。

> 原站自身会变动的部分（轮播/时间/推荐位）博文称用"连拍三次"剔除（F-013，仅博文单源）。详见 [02 · 相似度检查机制](../concepts/02-likeness-checking-method.md)。

## 步骤 7 · Ready（交付）

收敛到阈值（90% 或 6 轮用尽）后交付（F-027）。

## 入口选择：CLI 还是 MCP？

同一套工具**既是 CLI 子命令，也是 MCP 工具**（F-017），两种用法：

- **命令行**——适合脚本化、人工审阅、CI 式重复执行；
- **MCP（Model Context Protocol）**——把工具注册给 AI Agent，让 Agent 在对话/编排中直接调用。

> 工具总数**三源并存**（博文 314 / 第三方 314 / 官方 STATUS.md 300 引擎·320 含层），统计层不同，使用前见 [04 · 口径提醒](../concepts/04-install-and-known-limits.md)。

## 预期可观察信号与常见坑

| 观察点 | 预期 | 备注 |
|--------|------|------|
| 版本 | v0.3.0 起（2026-11-02） | 迭代快，`stale_after` 前复核（F-034） |
| 构建是否启动 | 需 Claude Code 已登录 | 未登录则构建步骤不可用（F-018） |
| Check 输出 | 三宽度相似度数值 + 迭代轮次 | 达到 90% 或 6 轮结束（F-037） |
| 净室**完整实跑** | 官方状态页曾写"还没做过" | 与博文"10-18 跑通一次"口径存在张力（F-021/F-022），不作事实断言 |
| 工具数 | 视统计层不同 | 300 / 314 / 320 三口径并存（F-036/F-041） |

## 阅读下一篇

- [概念 · 安装与已知边界](../concepts/04-install-and-known-limits.md)
- [P0 权威核验报告](../references/verification.md)
