---
okf_version: "0.2"
type: Example
title: 实操 1——三平台安装 Orca 与首个会话
description: macOS/Windows/Linux 三平台官方安装资产与命令、Homebrew 同名 cask 消歧、首启导入 ~/.claude 与 ~/.codex 凭据、添加仓库→建 worktree→选 Agent 的完整链路，附可用性检查表与常见坑
tags: [orca, ade, 安装, homebrew, dmg, appimage, worktree, first-session]
generated:
  by: trae-solo-agent
  at: "2026-09-20T20:40:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-20T21:10:00+08:00"
status: stable
stale_after: "2026-12-20"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/8JIFdIzUwyLF6j1ysOrkzg
  - id: github-orca
    url: https://github.com/stablyai/orca
  - id: docs-install
    url: https://onorca.dev/docs/install
  - id: docs-first-session
    url: https://onorca.dev/docs/first-session
---

# 实操 1：三平台安装 Orca 与首个会话

> **实操来源说明（必读）**：本篇命令与安装资产均来自**官方文档与官方仓库的逐字核验**（核验日 2026-09-20，对应最新正式版 **v1.4.205**，F-067）；**本知识包制作过程中未在任何平台真机执行**。博文作者只声明 macOS 侧跑过一行安装命令（F-043），**未给版本号、未展示任何命令输出**，Windows/Linux 步骤为博文转述（F-044~F-046）。因此本篇不是"博文作者实测记录"，而是"官方口径重组的实操指引"——执行前请以官方最新文档为准（安装页 `/docs/install`、入门页 `/docs/first-session`，F-103）。

## 0. 前置认知（装之前必须清楚）

- Orca **自身不含任何模型**（F-007）。官方文档原文："**Not a model.** Orca runs agents you already use — bring your own Claude, Codex, or OpenCode subscription."（F-075，官方文档描述，非实测输出）
- 它跑的是**你已有的 CLI Agent 订阅**：各 Agent 额度该怎么算还怎么算（F-050）；Orca 自己不卖模型、也不收费（F-049）。
- 需要一个**本地已经登录好的命令行 Agent**：官方称"只要 Agent 能在终端里跑，就能放进 Orca 里跑"（F-013）；Orca 会以正确的工作目录启动 agent CLI，并转发你的订阅凭据（F-076）。

## 1. 下载入口

| 入口 | 地址 | 出处 |
|---|---|---|
| 官网 | `onorca.dev`（下载页 `/download`） | F-069、F-093 |
| GitHub Releases | `https://github.com/stablyai/orca/releases` | F-058、F-068 |

> ⚠️ **勘误提醒（E-1，博文硬错误）**：博文把官网写成 `onnorca.dev`（多打一个 n）——该域名无法获取内容，照抄会打不开。**正确域名为 `onorca.dev`**（F-069；仓库 `homepage` 字段与 Homebrew cask 的 `homepage` 均为 `https://onorca.dev/`，F-070）。

官方入门资料的实际位置（F-103）：安装页 `/docs/install`、首会话页 `/docs/first-session`；**`/docs/quickstart` 为 404**，不要按其他工具的惯例去找 quickstart。

v1.4.205 的 Release 资产命名（F-068）：

```text
orca-macos-arm64.dmg
orca-macos-x64.dmg
orca-windows-setup.exe
orca-linux.AppImage
orca-linux-arm64.AppImage
（另有 .deb /.rpm）
```

注意：**macOS 只有 `.dmg`，没有 zip 安装包**（E-7）。

## 2. macOS 安装

```bash
brew install --cask stablyai/orca/orca
```

这是博文作者**唯一声明亲自跑过**的一行命令（F-043，作者一手实测，P0），已由官方 Homebrew tap 源码逐字证实（F-070）；博文口径也确认 macOS 实为 `.dmg` 形态（F-068）。

> 🚨 **同名混淆坑（必须用全限定名）**：Homebrew 官方仓库 `homebrew/cask` 里也有一个名为 `orca` 的 cask，那是 **plotly 的图表工具**（v1.3.1，2026-09-01 因 `fails_gatekeeper_check` 被 disabled），与 Stably 的 Orca 毫无关系（F-071）。写成裸名 `orca` 会装到错误的东西上——**务必用全限定名 `stablyai/orca/orca`**。这也是本知识包束名取 `orca-ade`（而非常见的 `orca`）的同一消歧理由。

Tap 元数据（F-070，逐字）：cask 名 `orca`、`version "1.4.205"`、`desc "IDE for orchestrating AI coding agents across terminals and worktrees"`、`homepage "https://onorca.dev/"`。

不愿用 Homebrew 时，直接从 Releases 下 `orca-macos-arm64.dmg` / `orca-macos-x64.dmg`（F-068）。

## 3. Windows 安装

博文口径（**转述，非实测**，F-045）：下载 `orca-windows-setup.exe`，运行安装程序。官方 Release 资产名逐字一致（F-068）。

> 说明：官方登记可用的 Windows 分发形态即 `.exe` 安装包；**官方文档未提供 winget / scoop / Chocolatey 等命令行安装方式**，本篇不编造此类命令。

## 4. Linux 安装

官方 Release 提供 `orca-linux.AppImage` 与 `orca-linux-arm64.AppImage`，另有 `.deb` 与 `.rpm`（F-046、F-068）。

Arch 系另有官方安装页给出的 AUR 形式（F-098）：

```bash
yay -S stably-orca-bin
```

> 说明：AppImage 的赋权与运行方式、`.deb`/`.rpm` 的安装命令，官方文档在本包核验范围内未登记，故不列出；请以官方安装页 `/docs/install` 为准（F-103）。

## 5. 首次会话链路（安装后第一件事）

官方 first-session 的步骤链与博文描述一致（F-047）：

1. **启动 Orca**；
2. **导入本地 Agent 凭据**——官方首启提供导入 `~/.claude`、`~/.codex`（F-077）；
3. **添加本地代码仓库**；
4. **新建 worktree**（独立目录 + 独立分支，F-016）；
5. **在终端选择要用哪个 Agent**（F-047）——Orca 以正确的工作目录启动该 agent CLI 并转发你的订阅凭据（F-076）；
6. **说一句话描述要做什么**（F-047）。

官方 first-session 文档对"一次开多个 worktree"的概括原文（F-083，官方文档描述，非实测输出）："**Three branches. Three diffs. Same prompt.**"

想看多开后的对比与择优，见 [实操 2](01-parallel-worktrees-and-cli.md)；机制层解释见 [概念 01](/concepts/01-fleet-worktree-mechanism.md)。

## 6. 安装后如何确认可用（检查表）

> ⚠️ **官方未提供独立诊断命令**：对照同为"装完要自检"的场景（如 LoopX 的 `loopx doctor`），Orca 官方 CLI 文档登记的 `orca` 命令面为 worktree/terminal/file/browser 四个命令族（F-097），**未见等价 doctor/诊断子命令**——不要按其他工具的习惯去找，也不要相信任何"ora doctor"式命令的教程。

| 检查项 | 判据 | 出处 |
|---|---|---|
| 应用可启动 | 能启动桌面端并进入主界面 | F-047（官方入门链路） |
| 凭据已接续 | 首启可导入 `~/.claude` / `~/.codex` | F-077 |
| 仓库可添加 | 能添加本地代码仓库 | F-047 |
| worktree 可建 | 能新建 worktree（独立目录 + 独立分支） | F-016、F-047 |
| Agent 可选 | 终端内可选到本地已安装并已登录的 CLI Agent | F-013、F-047 |
| 命令行可用 | 系统中存在 `orca` 命令（随桌面端附带） | F-097 |
| 桌面免账号 | 官方 telemetry 文档称 "Orca has no account system" | F-078 |

## 7. 常见坑（安装阶段高发）

| 坑 | 说明 | 出处 |
|---|---|---|
| 域名拼错 | 博文写 `onnorca.dev`；正确为 **`onorca.dev`** | E-1、F-069 |
| Homebrew 同名 cask | 裸名 `orca` 是 plotly 的图表工具；必须写 `stablyai/orca/orca` | F-071 |
| 以为 Orca 自带模型/额度 | Orca 不含模型，用的是你自己已有的 Agent 订阅，额度按各 Agent 供应商计费 | F-007、F-050 |
| 以为"全功能免账号" | 桌面端官方宣称无账号系统；**移动端配对 / Relay 明确要求登录同一 Orca 账号**，官方文档自相矛盾（详见 [实操 2](01-parallel-worktrees-and-cli.md)） | F-078、F-079、E-2 |
| 找 quickstart 页 | `/docs/quickstart` 为 404；入门页是 `/docs/first-session` | F-103 |
| 找 doctor 命令 | 官方未见独立诊断命令 | F-097 |
| 找 macOS zip 包 | macOS 只有 `.dmg` | F-068、E-7 |

## 8. 与相邻知识包的对照

- 同为「极客之家」同体裁转化的 [LoopX 束](../../loopx/index.md)：LoopX 是长程 Agent 控制面（有 `doctor` 自检、pip 安装），Orca 是 Agent 舰队的桌面编排环境（GUI 分发、无独立诊断命令）——两者解决的不是同一层问题。
- [EchoBird 束](../../echobird/index.md)：同为 AI Agent 桌面管理工具，可对照桌面端形态差异。

下一篇：[并行 worktree 扇出、Orca CLI 与远程移动端](01-parallel-worktrees-and-cli.md)。