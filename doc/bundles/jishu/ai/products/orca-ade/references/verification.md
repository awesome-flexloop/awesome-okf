---
okf_version: "0.2"
type: Reference
title: P0 权威核验报告——Orca ADE 博文（2026-09-20 核验）
description: 8 项 P0 声明核验（2✅/6⚠️/0❌）、批 A/B/C 三路核验记录（覆盖 F-061~F-103 共 43 条）、勘误七项（E-1 域名拼写为博文硬错误）、核验方法与未覆盖边界
tags: [orca, P0核验, 勘误, 信源核验, 时效管理]
generated:
  by: trae-solo-agent
  at: "2026-09-20T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-20T17:30:00+08:00"
status: stable
stale_after: "2026-11-30"
sources:
  - id: article-source
    url: /references/article-source.md
  - id: blog
    url: https://mp.weixin.qq.com/s/8JIFdIzUwyLF6j1ysOrkzg
  - id: github-api-orca
    url: https://api.github.com/repos/stablyai/orca
  - id: github-orca
    url: https://github.com/stablyai/orca
  - id: orca-site
    url: https://onorca.dev/
  - id: homebrew-orca
    url: https://github.com/stablyai/homebrew-orca
  - id: yc-stably
    url: https://ycombinator.com/companies/stably-ai-orca
  - id: appstore-orca
    url: https://apps.apple.com/us/app/orca-ide/id6766130217
---

# P0 权威核验报告

## 一、核验概览

| 项目 | 值 |
|---|---|
| 核验日期 | **2026-09-20** |
| 核验对象 | 微信公众号「极客之家」2026-09-14 14:05 推文《GitHub 6.7万 Star，一个多 Agent 协作、手机远程指挥的开源神器！》（约 2635 字） |
| 信源距离 | **第三方媒体产品介绍 + 作者 macOS 侧轻量实测**（非厂商自宣，亦非代码级/真机级实测）；涉产品自宣数据（星标、具名 Agent 数量、免费与账号口径）一律按 P0 处理 |
| P0 声明数 | **8 条**（F-002、F-005、F-008、F-010、F-043、F-044、F-049、F-059）；去重后为 **7 项声明**——F-059 与 F-002 同指"标题星标口径"一事 |
| P0 结论分布 | **✅ 2 / ⚠️ 6 / ❌ 0** |
| P0 ✅ 项 | F-043（macOS 安装命令逐字证实）、F-049（免费开源、无 pricing 页） |
| P0 ⚠️ 项 | F-002、F-059（星标时点口径）、F-005（ADE 全称无官方出处）、F-008（账号口径矛盾）、F-010（具名 Agent 数量三处不一）、F-044（官网域名拼写错误） |
| 核验补充事实 | F-061~F-103 共 **43 条**，由批 A/B/C 三路核验**全量覆盖（43/43）** |
| 勘误 | **E-1 ~ E-7 共 7 条**，其中 **E-1 为博文硬错误**（域名拼写） |
| 总体结论 | 核心声明（产品与仓库真实存在、开源免费、并行 worktree、diff 择一、Design Mode、SSH 远程、移动端、安装链路）**全部证实**，无 ❌ → bundle `status: stable` |
| 复核建议 | `stale_after: 2026-11-30`：项目周级迭代（最新 v1.4.205 / 2026-09-17），到期前复核版本线、Agent 具名清单与移动端版本口径 |

## 二、P0 核验记录

核验分三路并行进行：批 A（GitHub 仓库事实）、批 B（官网与功能口径）、批 C（移动端与第三方交叉核验）。

### 批 A｜GitHub 仓库事实

| 项 | 结论 | 官方原文关键措辞或实测值 | 来源 URL |
|---|---|---|---|
| F-061 仓库存在性与 Star | ✅ | 仓库 `stablyai/orca` 存在，`stargazers_count` = **66,453**（核验日 2026-09-20） | https://api.github.com/repos/stablyai/orca |
| F-062 License | ✅ | `MIT License` | 同上 |
| F-063 主语言与建仓日 | ✅ | 主语言 TypeScript；`created_at` = 2026-03-17 | 同上 |
| F-064 仓库描述 | ✅ | "Orca is the ADE for working with a fleet of parallel agents…" | 同上 |
| F-065 README 徽章具名清单与数量 | ✅ | 徽章行 "Works with any CLI agent"，具名 Agent **29 个** | https://github.com/stablyai/orca |
| F-066 官方数量口径（三处） | ⚠️ | README **29** / 官网首页 **27** / `docs/agents/supported` 表 **35 行**——三处不一致 | https://onorca.dev/docs/agents/supported |
| F-067 最新版本 | ✅ | 最新正式版 **v1.4.205**（2026-09-17） | https://api.github.com/repos/stablyai/orca/releases/latest |
| F-068 Release 资产形态 | ✅ | `orca-macos-arm64.dmg`、`orca-macos-x64.dmg`、`orca-windows-setup.exe`、`orca-linux.AppImage`、`orca-linux-arm64.AppImage`、`.deb`、`.rpm`；**macOS 无 zip 安装包** | 同上 |
| F-097 Orca CLI | ✅ | 命令为 `orca`（随桌面端附带）；含 worktree/terminal/file/browser 命令族，`orca worktree create`、`orca snapshot`、`orca click`、`orca fill`；另有 `orca serve`（无头 Linux） | https://onorca.dev/docs/cli/overview |

### 批 B｜官网与功能口径

| 项 | 结论 | 官方原文关键措辞或实测值 | 来源 URL |
|---|---|---|---|
| F-069 域名与定位 | ✅ | 仓库 `homepage` 字段为 `https://onOrca.dev`；`onnorca.dev` 无法获取内容 → 官网真实域名为 **`onorca.dev`** | https://api.github.com/repos/stablyai/orca |
| F-074 官方定位口径 | ✅ | 标语 "Ship 100x with the agent IDE"；docs 首页自称 "a desktop IDE"；官网另有 "An ADE is built for you and your agents" | https://onorca.dev/ ／ https://onorca.dev/docs |
| F-075 不含模型 | ✅ | "**Not a model.** Orca runs agents you already use — bring your own Claude, Codex, or OpenCode subscription." | https://onorca.dev/docs |
| F-076 自带订阅与凭据转发 | ✅ | Orca 会以正确的工作目录启动 agent CLI，并转发你的订阅凭据 | https://onorca.dev/docs/first-session |
| F-077 首启导入本地 Agent 配置 | ✅ | 首次启动提供导入 `~/.claude`、`~/.codex` | 同上 |
| F-008 账号口径（对应 F-078/F-079） | ⚠️ | F-078 "**Orca has no account system**" vs F-079 "signed into the same Orca account"、"sign-in is required for **Relay only**"——**官方文档自相矛盾** | https://onorca.dev/docs/telemetry ／ https://onorca.dev/docs/mobile |
| F-080 免费与无计费页 | ✅ | 官网 "Free and open source."；`/pricing` 返回 **404**，全站无计费页 | https://onorca.dev |
| F-081 不卖托管资源 | ✅ | "Orca does **not** sell managed VPS hosting"；"your provider account, images, and billing stay yours" | https://onorca.dev/docs/ways-to-run |
| F-082 并行 worktree 机制 | ✅ | "Fan one prompt across five agents, each in its own isolated git worktree — compare the results and merge the winner." | https://onorca.dev/docs/model/worktrees |
| F-083 三分支三 diff 同 prompt | ✅ | "Three branches. Three diffs. Same prompt." | https://onorca.dev/docs/first-session |
| F-084 终端（WebGL 口径） | ✅ | "Ghostty-class terminals with **WebGL rendering**, **infinite splits**, and **scrollback that survives restarts**" | https://onorca.dev/docs/terminal |
| F-085 终端（xterm.js 口径） | ⚠️ | 同一文档另称其是 "the same **xterm.js-based** terminal VS Code uses"——与 WebGL 口径并存 | 同上 |
| F-086 通知触发时机 | ✅ | agent 从 working 转为 idle 时触发系统通知 + 声音 + chip | https://onorca.dev/docs/notifications |
| F-087 Design Mode | ✅ | "Click any UI element in a real **Chromium** window to send its **HTML, CSS, and a cropped screenshot** straight into your agent's prompt." | https://onorca.dev/docs/browser/design-mode |
| F-088 Diff 批注 | ✅ | "**Drop comments on any diff line and ship them back to the agent**" | https://onorca.dev/docs/review/annotate-ai-diff |
| F-089 GitHub / Linear 集成 | ✅ | "**GitHub & Linear, Native** — Browse PRs, issues, and project boards in-app — **open a worktree from any task**" | https://onorca.dev/docs/review/linear |
| F-090 SSH 远程 worktree | ✅ | "**auto-reconnect and port forwarding included**"；"Orca reconnects and re-attaches"；侧栏 Ports tab 一键转发 | https://onorca.dev/docs/ssh |
| F-092 用量与账号切换 | ✅ | "See **Claude and Codex usage and rate-limit resets**, and **hot-swap accounts without re-logging in**"；状态栏呈现，5 小时/日/周重置，80% 警告 chip | https://onorca.dev/docs/agents/usage-tracking |
| F-093 下载渠道 | ✅ | `/download` 同时提供 App Store 与 Android APK；README 另给 TestFlight 链接 | https://onorca.dev/download |
| F-098 Arch 安装方式 | ✅ | 官方安装页另提供 `yay -S stably-orca-bin` | https://onorca.dev/docs/install |
| F-103 入门页与安装页 | ✅ | 无官方 quickstart 页（`/docs/quickstart` 404）；官方入门页为 `/docs/first-session`，安装页为 `/docs/install` | https://onorca.dev |

### 批 C｜移动端与第三方交叉核验

| 项 | 结论 | 官方原文关键措辞或实测值 | 来源 URL |
|---|---|---|---|
| F-070 Homebrew tap 安装命令 | ✅ | `Casks/orca.rb`：`cask "orca"`、`version "1.4.205"`、`homepage "https://onorca.dev/"`、desc "IDE for orchestrating AI coding agents across terminals and worktrees" | https://github.com/stablyai/homebrew-orca |
| F-071 同名 cask 混淆 | ⚠️ | Homebrew 官方仓库 `homebrew/cask` 的 cask `orca` 是 plotly 的图表工具（v1.3.1，2026-09-01 因 fails_gatekeeper_check 被 disabled），与 Stably 版无关；Stably 版必须用全限定名 `stablyai/orca/orca` | https://formulae.brew.sh/api/cask/orca.json |
| F-072 YC 背景 | ✅ | YC 公司页 "Stably AI (Orca)"：Batch **Winter 2022**，Active，旧金山，Team 25 | https://ycombinator.com/companies/stably-ai-orca |
| F-073 创始人 | ✅ | Jinjing Liang（CEO）、Neil Parker；公司主营 Stably（AI 测试平台 stably.ai） | 同上 |
| F-094 App Store 条目 | ✅ | "**Orca IDE**"，副题 "Manage Coding Agents Remotely"，免费，iPhone/iPad，6 个评分 5.0，开发者栏显示 **Lovecast LLC** | https://apps.apple.com/us/app/orca-ide/id6766130217 |
| F-095 Android 渠道 | ⚠️ | **仅走 GitHub Releases APK**；核验日未发现 Google Play 官方条目（Play 上的 "Orca: Boat GPS…" 为航海 App，无关） | https://github.com/stablyai/orca/releases |
| F-096 Android 版本口径 | ⚠️ | 官方两处不一致：官网 `/download` 写 "APK 0.0.48"，README 链接为 `mobile-android-v0.0.50` | https://onorca.dev/download |
| F-091 移动端能力与配对 | ✅ | "iOS and Android apps…get notified when an agent finishes and **send follow-ups from anywhere**"；"**Pairing is one-time**" | https://onorca.dev/docs/mobile |
| F-099 第三方星标统计 | ⚠️ | gstars.dev 于 2026-09-17 显示 **70.5K**；stably.ai 官网页面显示 **71.4k**——与核验日 API 实测 66,453 不一致（时点不同） | gstars.dev ／ stably.ai |
| F-100 第三方用户评价 | ✅ | "I've been impressed with orca"、"largely enjoying it" | https://news.ycombinator.com/item?id=49742023 |
| F-101 第三方质疑 | ✅ | agent fleet management 能否成为独立品类是更难的战略问题；并指出 README 未含采用数据、star 数或独立基准，发布声明为公司自述 | aiinsiders.net |
| F-102 第三方数量口径 | ⚠️ | 第三方对支持 Agent 数量的口径不一：多数写 "30+"，亦有 "25+" | andrew.ooo ／ dev.to ／ qiita.com |

## 三、勘误表

| # | 博文口径 | 正确口径 | 证据（F 编号） | 影响面 |
|---|---|---|---|---|
| **E-1** | 官网 `onnorca.dev` | 官网 **`onorca.dev`**（博文多打一个 n） | F-069、F-070、F-072 | **硬错误**：照抄会把读者带到不存在的域名 |
| E-2 | "也不需要注册什么 Orca 账号"（绝对口径） | 桌面端官方宣称 "no account system"；但**移动端配对/Relay 明确要求登录同一 Orca 账号**，官方文档自相矛盾 | F-078、F-079 | 核心声明部分失真：桌面可用 ≠ 全功能免账号 |
| E-3 | "6.7 万 Star" | 核验日 **66,453**（≈6.6 万）；第三方统计 70.5K–71.4K（时点不同） | F-061、F-099 | 时点口径，量级成立 |
| E-4 | "官方给它的定位叫 ADE，Agent Development Environment" | 官方仅使用缩写 **ADE**、或 "agent IDE"/"desktop IDE"；**全称无官方出处**（仅第三方与 GitHub topic 佐证） | F-064、F-074 | 表述外推，需标注 |
| E-5 | 官方列表具名 Agent "已经排了将近三十种" | 官方三处口径不一：README **29** / 官网 **27** / docs 表 **35 行**；第三方 25+~30+ | F-065、F-066、F-102 | 数字口径不稳定 |
| E-6 | Android "在官网下 APK" | 方向正确，但需补充：**无 Google Play 官方条目**；官网（0.0.48）与 README（0.0.50）版本号不一致 | F-095、F-096 | 补充而非纠正 |
| E-7 | 未提安装包形态 | macOS 实为 **.dmg**（无 zip 安装包）、Windows 为 **.exe**、Linux 为 **.AppImage**（另有 .deb/.rpm） | F-068 | 补充 |

> **E-1 特别标注**：这是本次核验中唯一一处**博文硬错误**（可被读者直接照做并失败）——`onnorca.dev` 无法获取内容，正确域名为 `onorca.dev`（同时被仓库 `homepage` 字段与 Homebrew cask 的 `homepage` 双重佐证）。bundle 正文一律使用 `onorca.dev`，不得原样照搬博文拼写。
> **E-2 特别标注**：属**部分失真**而非纯错误。桌面端"无账号系统"与移动端"Relay 需登录"并存，官方文档未澄清；bundle 正文须以双口径呈现，不得简化为"完全免账号"。

## 四、核验方法与未覆盖边界

- **方法**：GitHub API（`/repos`、`/releases/latest`）+ 仓库 raw README + 官网 `onorca.dev`（首页、`/download`、`/docs` 各页）+ Homebrew tap 源码 + YC 公司页 + 第三方报道交叉印证
- **未覆盖**：
  1. 博文发布日（2026-09-14）的星标时点快照无法还原，仅能取核验日实测值（66,453）
  2. 官网 FAQ 折叠块为 JS 手风琴，正文未能取到
  3. App Store 主体 "Lovecast LLC" 与 Stably AI 的法律实体对应关系无官方说明
  4. Orca 项目 2026-03 建仓与 YC W22 批次的时序关系未获官方解释
  5. 官方"no account system"与移动端"sign-in required"的矛盾未获官方澄清
- **未真机实测**：examples 中的命令经官方文档逐字比对，但**本包制作中未在任何平台执行**——macOS/Windows/Linux 三平台安装命令、`orca` CLI 命令族与移动端配对流程均未在真机验证，命令正确性以官方文档逐字比对为准（非实测输出）。