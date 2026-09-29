---
okf_version: "0.2"
type: Concept
title: "OpenHuman 是什么：本地优先的个人 Agent Harness"
description: "OpenHuman（TinyHumans）定位——开源 agent harness 而非聊天机器人、stateless 命题、仓库元数据与发布时间线、GPL-3.0/Rust/Tauri 技术栈、四种官方安装路径与三步走"
tags: [OpenHuman, TinyHumans, Agent Harness, 个人AI助手, Tauri, Rust, GPL-3.0, 安装]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-16T20:30:00+08:00" }
verified: { by: "process:blog-article-to-okf-wiki-v", at: "2026-09-16T20:30:00+08:00" }
status: stable
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/pdH1ZB3yPfDdA7Ay72hjGQ
    title: 开源先驱博文（2026-07-28）
  - id: github
    url: https://github.com/tinyhumansai/openhuman
    title: OpenHuman GitHub 仓库（2026-09-16 实测）
---

# OpenHuman 是什么：本地优先的个人 Agent Harness

> **数字口径提示**：本文热度数字均标注时点。博文口径为 2026-07-28，权威核验口径为 2026-09-16 GitHub 实测，两者相差 7 周且项目处于周级发版期，请勿混用。

## 一、一句话定位

OpenHuman（开发商 TinyHumans AI）是一个安装在个人电脑上的**开源 Agent Harness**——GitHub About 原文为 "OpenHuman is an open source **agent harness** with local-first memory, agent orchestration, and workflows"（F-043）。它不是网站聊天框，而是 Windows/macOS/Linux 桌面应用（F-037）：把你已有的工具（邮箱、日历、代码仓库、文档、聊天）通过 OAuth 接进来，在本地持续构建关于"你是谁"的记忆，再驱动 Agent 回答与执行（F-009/F-010）。

博文用一句话概括它要解决的命题（F-008，博文转述引文，本次核验未在官方 README 逐字定位，引用以博文为准）：

> "Every model in the world shares the same fundamental limitation: they are stateless."
> 世界上所有模型都有同一个根本缺陷：它们没有状态。

博文据此给出的归纳是：OpenHuman 不是又一个聊天机器人，而是"持续运转、知道你是谁、能自己干活的个人数字分身"（F-010，作者归纳）。

## 二、仓库元数据与热度（双时点对照）

| 指标 | 博文口径（2026-07-28） | 权威核验（2026-09-16） |
|------|----------------------|----------------------|
| Star | 7,800+（F-006，历史值无法回溯） | **39,814（39.8k）**（F-044） |
| Commit | 3,926 次（F-005，历史值无法回溯） | **20,551 次**（F-047） |
| Fork | — | 3,922（F-044） |
| Contributors | — | 183（F-044） |
| 最新版本 | v0.63.3，"六十多个版本"（F-005） | release 最新 v0.63.12；**release 共 56 个 / tag 共 106 个**（F-046） |
| Trending | 发布一周内连续 9 天第一（F-004） | README 自认该表述，时间锚点为"发布后一周内"（F-048） |

> ⚠️ 博文标题中的 3,926 commits / 7,800 Star 两个历史数字均**无法经官方渠道回溯证实**；第三方 AI 生成知识库曾称项目 5 月中已达 27k+ stars（F-064，弱源不采），与博文口径数量级冲突。引用热度时请使用 2026-09-16 实测值并标注时点。"六十多个版本"与 56 个 releases 的口径不符（F-046）。

时间线（F-043/F-046/F-060）：仓库创建 2026-02-18 → 最早 GitHub Release v0.49.32（2026-03-31）→ 发布后一周内连续 9 天 GitHub Trending 全站第一 → 2026-07-28 博文中版本 v0.63.3 → 2026-08-07 最新 release v0.63.12（tag 已推进到 v0.63.21+）。项目目前挂官方 **Early Beta** 徽章："Under active development. Expect rough edges."

## 三、许可证与技术栈（以官方为准）

- **许可证 GPL-3.0**（F-045，GitHub 侧栏与 API 双重确认；博文 F-007 准确）
- **技术栈**：Tauri 桌面壳（`crates/openhuman-app`）+ Rust workspace（贡献指南要求 Rust 1.96.1，Rust 占比 58.6%）+ TypeScript 前端（37.9%）+ SQLite 本地存储；构建链 Node.js 24+ / pnpm / Cargo（F-029/F-057）
- **模型**：可用自有 provider key 接入托管模型，也可跑**全本地 Ollama**，三者可混用（F-057）。博文技术栈表中的 "React"、具名 "Claude/GPT/Gemini" 未见于官方 README，官方以"your own provider key"泛指托管模型；安全项中博文列出的 "ChaCha20-Poly1305" 亦未在 README 出现（F-056），Signal Protocol 端到端加密则获官方明确（见 [02-runtime-and-agent-design](02-runtime-and-agent-design.md)）
- 博文导语所称"内置完整 Linux 沙箱"在官方 README 与 GitBook 公开功能页均未见（F-062，单源存疑，不作为本包事实）

## 四、获取与安装（命令经官方核验）

博文给出的安装命令全部经 GitHub 实测存在（F-030/F-058）：

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.sh | bash
# Windows（PowerShell 7+）
irm https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.ps1 | iex
# macOS Homebrew（命令见于官方 INSTALL.md，该页另列 Debian/Ubuntu .deb 与 AUR）
brew install --cask openhuman
```

`scripts/install.sh`（21,787 字节）与 `install.ps1`（9,013 字节）HTTP 200 真实可取；也可直接从 [GitHub Releases](https://github.com/tinyhumansai/openhuman/releases/latest) 下载安装包。

源码构建（F-032，与官方 pnpm/Node 工具链一致）：

```bash
git clone https://github.com/tinyhumansai/openhuman.git
cd openhuman
git submodule update --init --recursive
pnpm install
pnpm dev                                # Web UI 开发模式
pnpm --filter openhuman-app dev:app     # 桌面应用开发模式
```

安装后的"三步走"（F-031，博文口径，与官方 Guide 的四检查点一致）：① 登录产品后逐个 OAuth 授权核心服务（博文建议邮箱+日历+GitHub+文档共 3-5 个；注意登录产品不等于自动获得邮箱权限，每个连接器独立授权）；② 等待约 20 分钟完成首个 ingest 周期（博文称 5-10 分钟，官方文档口径为约 20 分钟一个周期）；③ 再开始提问，让回答落在已同步的记忆上。

> **硬件口径**：官方 Guide 的基线是 **4GB+ RAM**（Getting Started 口径），大型邮箱/代码库叠加本地模型建议 16GB+，并建议快速 SSD（F-059）；博文建议 8GB+ 并称 4GB 下吉祥物动画卡顿（F-035），属更保守的体验口径。

## 相关文档

- 记忆与成本机制：[01-memory-tree-and-tokenjuice](01-memory-tree-and-tokenjuice.md)
- Agent 运行时与设计：[02-runtime-and-agent-design](02-runtime-and-agent-design.md)
- 竞品格局与取舍：[03-landscape-and-tradeoffs](03-landscape-and-tradeoffs.md)
- 事实清单：[references/article-source](../references/article-source.md)
