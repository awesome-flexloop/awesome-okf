---
okf_version: "0.2"
type: bundle
title: Orca ADE——让多个 AI 编程 Agent 并行开工、手机远程指挥的开源桌面工作台
description: Stably AI 开源桌面 ADE 教程（极客之家博文核验转化）——并行 git worktree 多 Agent 编排、Design Mode、diff 批注、SSH 远程与移动端指挥、Orca CLI，含三平台安装实操与七项勘误
tags: [orca, ade, agent-fleet, worktree, 多agent协作, 远程指挥, stably-ai, 开源工具, 核验转化]
generated:
  by: trae-solo-agent
  at: "2026-09-20T17:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-20T17:30:00+08:00"
status: stable
stale_after: "2026-11-30"
sources:
  - id: article-source
    resource: /references/article-source.md
  - id: blog
    url: https://mp.weixin.qq.com/s/8JIFdIzUwyLF6j1ysOrkzg
  - id: github-orca
    url: https://github.com/stablyai/orca
  - id: github-api-orca
    url: https://api.github.com/repos/stablyai/orca
  - id: orca-site
    url: https://onorca.dev/
  - id: homebrew-orca
    url: https://github.com/stablyai/homebrew-orca
  - id: yc-stably
    url: https://www.ycombinator.com/companies/stably-ai-orca
  - id: appstore-orca
    url: https://apps.apple.com/us/app/orca-ide/id6766130217
---

# Orca ADE——让多个 AI 编程 Agent 并行开工、手机远程指挥的开源桌面工作台

> **类型**：开源工具教程（第三方媒体产品介绍博文 + 作者 macOS 侧轻量实测，经官方仓库/官网/Homebrew tap/YC 页核验转化）
> **信源**：微信公众号「极客之家」2026-09-14 14:05 推文《GitHub 6.7万 Star，一个多 Agent 协作、手机远程指挥的开源神器！》（约 2635 字）+ GitHub 仓库与 API / 官网 `onorca.dev` / Homebrew tap / YC 公司页（核验日 2026-09-20）
> **P0 核验**：8 条 P0 声明（去重 7 项）→ ✅ 2 / ⚠️ 6 / ❌ 0；核心声明（产品存在、功能、开源免费、安装命令）全部证实，`status: stable`；六项 ⚠️ 为口径类偏差（域名拼写、星标时点、ADE 全称、Agent 数量口径、账号口径矛盾、Android 版本），已在正文按"博文口径 / 核验口径"双标注，详见 [verification.md](references/verification.md)

## 本文概要

Orca 是 **Stably AI（YC W22）开源（MIT）的桌面 ADE（Agent Development Environment，官方仅用缩写）**，解决的问题不是"再做一个 AI IDE"，而是**把多个 CLI 编程 Agent 的并行作业搬进一个可视化工作台**：一条需求可同时扇出给多个 Agent，每个 Agent 拿到独立的 git worktree（独立目录 + 独立分支），改文件互不干扰；跑完在一个界面并排看 diff，挑最满意的一份合并、其余丢弃。周边配套包括内置 Chromium 的 Design Mode（点页面元素把 HTML/CSS/截图发回 Agent）、diff 行级批注、GitHub/Linear 任务直开 worktree、SSH 远程 worktree、iOS/Android 配套 App 远程指挥，以及可脚本化的 Orca CLI。

> ⚠️ **三条先读提示**：
> 1. **域名勘误（博文硬错误）**：博文写的官网 `onnorca.dev` **多打了一个 n**，正确域名为 **`onorca.dev`**（证据见 [verification.md](references/verification.md) 勘误 E-1 与 [article-source.md](references/article-source.md) F-069）；
> 2. **账号口径矛盾**：博文称"不需要注册 Orca 账号"，桌面端官方确实声明无账号体系，但**移动端配对/Relay 明确要求登录 Orca 账号**，官方文档自相矛盾（E-2）——"免账号"只对纯桌面用法成立；
> 3. **时效**：核验日（2026-09-20）最新桌面正式版为 **v1.4.205**，星标实测 **66,453**（博文"6.7 万"及第三方 70.5K–71.4K 均为不同时点口径），`stale_after` 设为 2026-11-30。

## 文档结构

### concepts/ — 概念解析

| 文档 | 主题 |
|------|------|
| [00-orca-overview.md](concepts/00-orca-overview.md) | 一句话定位与 ADE 口径边界、厂商 Stably AI（YC W22）、MIT 开源免费与"免账号"双口径、星标与版本的三方数字、支持平台与分发形态 |
| [01-fleet-worktree-mechanism.md](concepts/01-fleet-worktree-mechanism.md) | 一 prompt 扇出多 Agent 的主回路、独立 git worktree 隔离与择优合并、终端分屏与完成通知、Design Mode/diff 批注/任务直开 worktree、SSH 远程、移动端与 Orca CLI |
| [02-ecosystem-and-fit.md](concepts/02-ecosystem-and-fit.md) | 支持 Agent 清单的三处官方口径差异、成本真相（五 Agent 即五份 token）、适用/不适用决策表、同分组生态位对比与"agent fleet management 是否成立为品类"的第三方质疑 |

### examples/ — 实操示例

> 本目录是 **基于官方文档与官方仓库逐字核验重组的实操指引，不是博文作者的实测记录**：博文仅声明 macOS 侧跑过一行安装命令，未给版本号、未展示任何命令输出；本包制作中未在任何平台真机执行，读者执行前请以官方最新文档为准。

| 文档 | 主题 |
|------|------|
| [00-install-and-first-session.md](examples/00-install-and-first-session.md) | 前置认知（Orca 不含模型、用已有订阅）、macOS/Windows/Linux 安装资产与命令、Homebrew 同名 cask 消歧、首启导入 `~/.claude` 与 `~/.codex`、首个 worktree 链路、可用性检查表与常见坑 |
| [01-parallel-worktrees-and-cli.md](examples/01-parallel-worktrees-and-cli.md) | 并行 worktree 扇出与 diff 择一合并、终端/通知/Design Mode/diff 批注配套交互、Orca CLI 命令表（`orca worktree create`/`snapshot`/`click`/`fill`/`serve`）、SSH 远程 worktree、移动端配对、用量面板与并行 token 成本提示 |

### references/ — 信源登记

| 文档 | 说明 |
|------|------|
| [article-source.md](references/article-source.md) | F-001~F-103 事实清单（双份登记之 bundle 份：博文事实 60 条 + 核验补充 43 条），逐条标注信源距离层级与 P 级 |
| [verification.md](references/verification.md) | P0 核验报告：8 项 P0（2✅/6⚠️/0❌）、批 A/B/C 三路核验记录、勘误七项（E-1 域名硬错误 / E-2 账号口径矛盾 / E-5 Agent 数量三口径）、核验方法与未覆盖边界 |

## 主题关联

- [EchoBird 百灵鸟 AI Agent 桌面管理工具](../echobird/index.md)：同为 AI Agent 桌面管理工具，Echobird 走"模型枢纽 + 本地 LLM + 代理"（管"接哪个模型"），Orca 走"Agent 舰队 + worktree 编排"（管"开几路 Agent"）
- [LoopX 长程 Agent 控制面](../loopx/index.md)：同公众号同体裁转化；LoopX 是本地状态内核/控制面（治理"跨天跑、不空烧"），Orca 是交互式桌面工作台（承载"并行扇出、择优合并"）——治理层 × 工作台层互补
- [Codex Agent 工作流实践](../codex-agent-workflow-practices/index.md)：Codex CLI 并行 session 降本实践——Orca 是承载这类工作流的工具形态，二者是方法论与工具的关系
- [ToDesk AI 跨设备 AI 助手](../todesk-ai/index.md)：跨设备远程指挥的另一种形态，可对照 Orca 移动端"通知 + 追发指令"的生态位
- [planning-with-files 像 Manus 一样工作](../planning-with-files/index.md)：3-File Pattern 文件系统外存——与 Orca 的"worktree 即隔离工作区"同属把 Agent 状态外化到文件系统的路线
- [上下文优化 Context Optimization](../context-optimization/index.md)：Token 成本优化全景——Orca"五 Agent 五份 token"的成本结构是该主题下的并行化代价案例

## 已知边界

- **版本强时效**：核验日桌面正式版 **v1.4.205**；移动端版本两处官方口径不一致（官网 `/download` 写 APK 0.0.48，README 链向 `mobile-android-v0.0.50`，E-6），`stale_after`（2026-11-30）前须复核
- **星标时点口径**：博文"6.7 万"为发文时点（2026-09-14）表述；核验日（09-20）GitHub API 实测 66,453（≈6.6 万）；第三方统计 gstars.dev 70.5K（09-17）、stably.ai 官网 71.4k——三者时点与口径不同，正文按三方并列呈现
- **Agent 具名数量三口径**：官方 README 29 / 官网 27 / 官方 docs 表 35 行（E-5），博文"将近三十种"落在区间内但无唯一权威值，引用时须注明口径
- **ADE 全称无官方出处**："Agent Development Environment"为第三方与社区外推，官方仅使用缩写 ADE 或 "agent IDE"/"desktop IDE"（E-4）
- **账号口径矛盾**：官方"no account system"（桌面端反馈模板口径）与移动端"sign-in required"并存，未获官方澄清（E-2、未覆盖边界⑤）
- **未真机实测**：examples 中所有命令经官方文档逐字核验，但**本包制作中未在任何平台执行**；文中引号内容为官方文档原文措辞而非实测输出
- **未覆盖项**：博文发布日星标时点快照无法还原；官网 FAQ 折叠块为 JS 手风琴未取到正文；App Store 主体 "Lovecast LLC" 与 Stably AI 的法律实体对应关系无官方说明；Orca 建仓（2026-03）与 YC W22 批次的时序关系未获官方解释
- **观点分层**：F-055~F-057（"能火是因为……""偏重，可先观望"等）与 F-006/F-019/F-028/F-051 为博文作者观点（P2 单源），正文已显式标注，不作为事实引用
- **第三方质疑保留**：F-101 指出 README 未含采用数据、star 数或独立基准，发布声明为公司自述，"agent fleet management 能否成为独立品类"仍是开放战略问题——本包记录该质疑而不作结论

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```