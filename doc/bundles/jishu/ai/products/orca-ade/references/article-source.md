---
okf_version: "0.2"
type: Reference
title: 博文事实清单——《GitHub 6.7万 Star，一个多 Agent 协作、手机远程指挥的开源神器！》
description: 极客之家 2026-09-14 推文的 F 编号事实登记（双份登记之 bundle 份，与 spec facts.md 编号集合一致）
tags: [orca, 事实登记, 微信博文, multi-agent, ade, worktree]
generated:
  by: trae-solo-agent
  at: "2026-09-20T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-20T00:00:00+08:00"
status: stable
stale_after: "2026-11-30"
sources:
  - id: article-source
    url: /references/article-source.md
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
    url: https://ycombinator.com/companies/stably-ai-orca
  - id: appstore-orca
    url: https://apps.apple.com/us/app/orca-ide/id6766130217
---

# 博文事实清单（article-source）

> 本文件是 F 编号事实的 **bundle 侧登记**，与 spec `.trae/specs/okf-wiki-ecosystem/orca-ade-okf-wiki/facts.md` 构成**双份登记**，两侧编号集合必须一致且连续（F-001 ~ F-103，无跳号）。V 阶段以正则比对两侧编号集合是否相等。
> **编号分段**：F-001~F-060 = 博文事实（极客之家原文口径）；F-061~F-103 = 核验阶段补充事实（官方/第三方一手来源）。
> **信源距离层级**取值：`官方发布` / `作者一手实测` / `官方文档` / `第三方综述` / `厂商自宣` / `作者观点`。
> **P 级**：P0 = 厂商/产品自宣类必核验数字（星标、具名数量、免费与账号口径）；P1 = 一般事实；P2 = 观点/自述类单源。

## A. 博文元信息

| 项目 | 内容 |
|---|---|
| 标题 | 《GitHub 6.7万 Star，一个多 Agent 协作、手机远程指挥的开源神器！》 |
| 公众号 | 极客之家 |
| 发布时间 | 2026-09-14 14:05 |
| 正文字数 | 约 2635 字 |
| 文章 URL | https://mp.weixin.qq.com/s/8JIFdIzUwyLF6j1ysOrkzg |
| 体裁 | 第三方媒体开源项目产品介绍（含作者 macOS 侧轻量实测） |
| 采集/核验日 | 2026-09-20 |
| 主线实体 | Orca（Stably AI 出品的 AI 编程 Agent 编排桌面工具）；bundle 命名 `orca-ade` 用于规避 Homebrew `orca`（plotly 图表工具）同名混淆 |

## B. 博文事实（F-001~F-060）

| 编号 | 事实陈述 | 信源层级 | P 级 | 核验结论 |
|---|---|---|---|---|
| F-001 | 项目名 Orca，是一个管理 AI 编程 Agent 的开源工具 | 第三方综述 | P1 | ✅ |
| F-002 | 文章称 Orca 在 GitHub 已有 6.7 万 Star，且仍在增长 | 厂商自宣 | **P0** | ⚠️ 核验日实测 66,453（≈6.6 万） |
| F-003 | Orca 由 Stably AI 开源 | 第三方综述 | P1 | ✅ |
| F-004 | Stably AI 是 YC 孵化出来的公司 | 第三方综述 | P1 | ✅ YC 页标注 Batch Winter 2022 |
| F-005 | 官方定位称 ADE（Agent Development Environment，智能体开发环境） | 第三方综述 | **P0** | ⚠️ "ADE" 缩写证实，全称无官方出处 |
| F-006 | 传统 IDE 里 AI 只是插件；Orca 中干活主力是 Agent，人主要管派任务和看进度 | 作者观点 | P2 | 观点，不核验 |
| F-007 | Orca 自身不含任何模型 | 官方文档 | P1 | ✅ |
| F-008 | 不需要注册 Orca 账号 | 官方文档 | **P0** | ⚠️ 口径矛盾，见 F-078/F-079 |
| F-009 | 本地已登录好的命令行 Agent 可直接接续使用 | 官方文档 | P1 | ✅ |
| F-010 | 官方列表具名 Agent 已排近三十种 | 厂商自宣 | **P0** | ⚠️ 官方三处口径不一，见 F-065/F-066 |
| F-011 | 具名 Agent 含 Claude Code、Codex、OpenCode、Grok、Cursor CLI、GitHub Copilot CLI | 官方文档 | P1 | ✅ 六个全部命中 |
| F-012 | 国产 Agent 支持 Kimi、Qwen Code、MiMo Code | 官方文档 | P1 | ⚠️ 前两个证实；MiMo Code 仅在 README 徽章行，官方 docs 表未列 |
| F-013 | 官方说法：只要 Agent 能在终端里跑，就能放进 Orca 里跑 | 官方文档 | P1 | ✅ "Works with any CLI agent" |
| F-014 | 核心功能为并行 Worktree：多个 Agent 同时干活 | 官方文档 | P1 | ✅ |
| F-015 | 同一个需求可同时派给好几个 Agent | 官方文档 | P1 | ✅ |
| F-016 | 每个 Agent 分到一个独立 git worktree（独立目录 + 独立分支） | 官方文档 | P1 | ✅ |
| F-017 | 各 Agent 改文件互不干扰 | 官方文档 | P1 | ✅ "isolated git worktree" |
| F-018 | 跑完在一个界面并排看 diff，挑一份最满意的合并，其余直接丢弃 | 官方文档 | P1 | ✅ |
| F-019 | 以前做同样的事需手动开多个终端、自建 worktree、人工记窗口与任务对应关系 | 作者观点 | P2 | 观点，不核验 |
| F-020 | 内置终端为 WebGL 渲染 | 官方文档 | P1 | ✅（同行另有 xterm.js 口径，见 F-085） |
| F-021 | 终端支持无限分屏 | 官方文档 | P1 | ✅ "infinite splits" |
| F-022 | 终端回滚记录在重启之后还在 | 官方文档 | P1 | ✅ "scrollback that survives restarts" |
| F-023 | 同时跑多个 Agent 时，所有输出平铺在一个窗口里 | 官方文档 | P1 | ✅ |
| F-024 | 某个 Agent 干完了会有通知，不用一直盯屏 | 官方文档 | P1 | ✅ |
| F-025 | 内置一个 Chromium 浏览器，提供 Design Mode | 官方文档 | P1 | ✅ |
| F-026 | Design Mode 下点击页面元素，该元素的 HTML、CSS 和截图一起发给 Agent | 官方文档 | P1 | ✅（文档另加 computed styles 与 source map） |
| F-027 | Diff 批注：可在 diff 视图某一行直接写评论，写完一起发回让 Agent 继续改 | 官方文档 | P1 | ✅ |
| F-028 | 该流程与人工 review 代码差不多 | 作者观点 | P2 | 观点，不核验 |
| F-029 | GitHub 和 Linear 集成：PR、Issue、项目看板可在 Orca 内直接看 | 官方文档 | P1 | ✅ |
| F-030 | 看到要做哪个任务，可一键从该任务开出新 worktree | 官方文档 | P1 | ✅ "open a worktree from any task" |
| F-031 | SSH 远程 Worktree：可把 Agent 放到远程服务器上跑 | 官方文档 | P1 | ✅ |
| F-032 | 远程场景下文件编辑、git、终端能力都是完整的 | 官方文档 | P1 | ✅ |
| F-033 | 断线自动重连 | 官方文档 | P1 | ✅ "auto-reconnect" |
| F-034 | 带端口转发 | 官方文档 | P1 | ✅ Ports tab 一键转发 |
| F-035 | iOS 和 Android 都有配套 App | 官方文档 | P1 | ✅ |
| F-036 | 与桌面端配对后，Agent 跑完手机会收到通知 | 官方文档 | P1 | ✅ |
| F-037 | 人不在电脑前也能发后续指令 | 官方文档 | P1 | ✅ "send follow-ups from anywhere" |
| F-038 | 状态栏直接显示 Claude 和 Codex 的用量与限流重置时间 | 官方文档 | P1 | ✅ |
| F-039 | 多个账号之间一键切换，不用重新登录 | 官方文档 | P1 | ✅ "hot-swap accounts" |
| F-040 | Orca 自己还带一条命令行（Orca CLI） | 官方文档 | P1 | ✅ |
| F-041 | CLI 可脚本化建 worktree、打快照、点界面等操作 | 官方文档 | P1 | ✅ `orca worktree create` / `orca snapshot` / `orca click` |
| F-042 | Agent 反过来也能驱动 Orca，可把整个流程接进自动化 | 官方文档 | P1 | ✅ "Agents drive Orca too" |
| F-043 | macOS 安装命令为 `brew install --cask stablyai/orca/orca` | 作者一手实测 | **P0** | ✅ 逐字证实，见 F-070 |
| F-044 | Windows 和 Linux 去官网 onorca.dev 或 GitHub Releases 下安装包 | 第三方综述 | **P0** | ⚠️ **域名拼写错误**：官网为 `onorca.dev`（非 `onnorca.dev`），见 F-069 |
| F-045 | Windows 安装包是 exe | 第三方综述 | P1 | ✅ `orca-windows-setup.exe` |
| F-046 | Linux 安装包是 AppImage | 第三方综述 | P1 | ✅ 另有 .deb/.rpm |
| F-047 | 安装后流程：打开 → 添加本地代码仓库 → 新建 worktree → 终端选 Agent → 说一句要做什么 | 作者一手实测 | P1 | ✅ 与官方 first-session 文档一致 |
| F-048 | 想对比方案时同一需求多开几个 worktree，一个 worktree 派一个 Agent | 官方文档 | P1 | ✅ |
| F-049 | Orca 自己不卖模型，也不收费 | 官方文档 | **P0** | ✅ "Free and open source"，无 pricing 页 |
| F-050 | 用的是已有 Agent 订阅，各 Agent 额度该怎么算还怎么算 | 官方文档 | P1 | ✅ "your own subscription" |
| F-051 | 同时派五个 Agent 出去，token 消耗也是五份 | 作者观点 | P2 | 观点（成本推断），与官方"自带订阅"口径自洽 |
| F-052 | 手机端 iOS 走 App Store 或 TestFlight | 官方文档 | P1 | ✅ |
| F-053 | Android 在官网下 APK | 官方文档 | P1 | ⚠️ 证实但有坑：无 Google Play 官方条目，且官方两处版本号不一致，见 F-095/F-096 |
| F-054 | 装好后跟桌面端配对就能用 | 官方文档 | P1 | ✅ "Pairing is one-time" |
| F-055 | 作者观点：Orca 能火是因为单个 Agent 已够用，真正耗人的是同时开几个之后多出来的杂事 | 作者观点 | P2 | 观点，不核验 |
| F-056 | 作者观点：平时只用一个 Agent、一次只干一件事的用户，Orca 偏重，可先观望 | 作者观点 | P2 | 观点，不核验 |
| F-057 | 作者观点：已在同时用两三个 AI 编程工具、被窗口和分支搞头疼的用户适合 | 作者观点 | P2 | 观点，不核验 |
| F-058 | 开源地址 `https://github.com/stablyai/orca` | 官方发布 | P1 | ✅ 仓库真实存在 |
| F-059 | 文章标题称 "GitHub 6.7万 Star" | 厂商自宣 | **P0** | ⚠️ 同 F-002 |
| F-060 | 文章标题称 "多 Agent 协作、手机远程指挥" | 第三方综述 | P1 | ✅ 与功能描述一致 |

## C. 核验补充事实（F-061~F-103）

> 以下 43 条为核验阶段采集的一手事实，本身即核验产出，故「P 级」栏记 `—`，「核验结论」栏记该事实的核验状态（⚠️ 表示口径不一或需附加说明，而非核验失败）。

| 编号 | 事实陈述 | 信源层级 | P 级 | 核验结论 |
|---|---|---|---|---|
| F-061 | GitHub API：`stablyai/orca` 存在，`stargazers_count` = 66,453（核验日 2026-09-20） | 官方发布 | — | ✅ 实测 |
| F-062 | 仓库 License 为 MIT License | 官方发布 | — | ✅ |
| F-063 | 仓库主语言 TypeScript，创建于 2026-03-17 | 官方发布 | — | ✅ |
| F-064 | 仓库描述："Orca is the ADE for working with a fleet of parallel agents…" | 官方发布 | — | ✅ |
| F-065 | README 徽章行 "Works with any CLI agent"，具名 Agent 29 个 | 官方发布 | — | ✅ |
| F-066 | 官方 `docs/agents/supported` 表 35 行；官网首页口径 27 个——与 README 29 个三处不一致 | 官方文档 | — | ⚠️ 三处口径不一 |
| F-067 | 最新正式版 v1.4.205（2026-09-17） | 官方发布 | — | ✅ |
| F-068 | Release 资产：`orca-macos-arm64.dmg`、`orca-macos-x64.dmg`、`orca-windows-setup.exe`、`orca-linux.AppImage`、`orca-linux-arm64.AppImage`、`.deb`、`.rpm`（macOS 无 zip 安装包） | 官方发布 | — | ✅ |
| F-069 | **官网真实域名为 `onorca.dev`**（仓库 homepage 字段为 `https://onOrca.dev`；`onnorca.dev` 无法获取内容） | 官方发布 | — | ✅ 核实域名；博文拼写有误（E-1） |
| F-070 | Homebrew tap `stablyai/homebrew-orca` 的 `Casks/orca.rb`：`cask "orca"`、`version "1.4.205"`、`desc "IDE for orchestrating AI coding agents across terminals and worktrees"`、`homepage "https://onorca.dev/"` | 官方发布 | — | ✅ |
| F-071 | **同名混淆**：Homebrew 官方仓库 `homebrew/cask` 的 cask `orca` 是 plotly 的图表工具（v1.3.1，2026-09-01 因 fails_gatekeeper_check 被 disabled），与 Stably 版无关；Stably 版必须用全限定名 `stablyai/orca/orca` | 第三方综述 | — | ⚠️ 同名混淆风险 |
| F-072 | YC 公司页 "Stably AI (Orca)"：Batch **Winter 2022**，Active，旧金山，Team 25 | 第三方综述 | — | ✅ |
| F-073 | 创始人 Jinjing Liang（CEO）、Neil Parker；公司主营 Stably（AI 测试平台 stably.ai） | 第三方综述 | — | ✅ |
| F-074 | 官方标语 "Ship 100x with the agent IDE"；官方 docs 首页自称 "a desktop IDE"；官网另有 "An ADE is built for you and your agents" | 官方发布 | — | ✅ |
| F-075 | 官方 docs："**Not a model.** Orca runs agents you already use — bring your own Claude, Codex, or OpenCode subscription." | 官方文档 | — | ✅ |
| F-076 | 官方 docs：Orca 会以正确的工作目录启动 agent CLI，并转发你的订阅凭据 | 官方文档 | — | ✅ |
| F-077 | 首次启动提供导入 `~/.claude`、`~/.codex` | 官方文档 | — | ✅ |
| F-078 | 官方 telemetry 文档称 "**Orca has no account system**" | 官方文档 | — | ⚠️ 与 F-079 矛盾 |
| F-079 | 官方 mobile 文档要求 "signed into the same Orca account"，"sign-in is required for **Relay only**" | 官方文档 | — | ⚠️ 与 F-078 矛盾 |
| F-080 | 官网 "Free and open source."；`/pricing` 返回 404，全站无计费页 | 官方发布 | — | ✅ |
| F-081 | 官方："Orca does **not** sell managed VPS hosting"；"your provider account, images, and billing stay yours" | 官方文档 | — | ✅ |
| F-082 | 官方 worktrees 文档："Fan one prompt across five agents, each in its own isolated git worktree — compare the results and merge the winner." | 官方文档 | — | ✅ |
| F-083 | 官方 first-session 文档："Three branches. Three diffs. Same prompt." | 官方文档 | — | ✅ |
| F-084 | 官方 terminal 文档："Ghostty-class terminals with **WebGL rendering**, **infinite splits**, and **scrollback that survives restarts**" | 官方文档 | — | ✅ |
| F-085 | 同一 terminal 文档另称其是 "the same **xterm.js-based** terminal VS Code uses"——与 WebGL 口径并存 | 官方文档 | — | ⚠️ 两口径并存 |
| F-086 | 官方 notifications 文档：agent 从 working 转为 idle 时触发系统通知 + 声音 + chip | 官方文档 | — | ✅ |
| F-087 | 官方 design-mode 文档："Click any UI element in a real **Chromium** window to send its **HTML, CSS, and a cropped screenshot** straight into your agent's prompt." | 官方文档 | — | ✅ |
| F-088 | 官方 annotate 文档："**Drop comments on any diff line and ship them back to the agent**" | 官方文档 | — | ✅ |
| F-089 | 官方："**GitHub & Linear, Native** — Browse PRs, issues, and project boards in-app — **open a worktree from any task**" | 官方文档 | — | ✅ |
| F-090 | 官方 SSH 文档："**auto-reconnect and port forwarding included**"；"Orca reconnects and re-attaches"；侧栏 Ports tab 一键转发 | 官方文档 | — | ✅ |
| F-091 | 官方 mobile 文档："iOS and Android apps…get notified when an agent finishes and **send follow-ups from anywhere**"；"**Pairing is one-time**" | 官方文档 | — | ✅ |
| F-092 | 官方 usage-tracking 文档："See **Claude and Codex usage and rate-limit resets**, and **hot-swap accounts without re-logging in**"；状态栏呈现，5 小时/日/周重置，80% 警告 chip | 官方文档 | — | ✅ |
| F-093 | 官网 `/download` 同时提供 App Store 与 Android APK；README 另给 TestFlight 链接 | 官方发布 | — | ✅ |
| F-094 | App Store 条目 **"Orca IDE"**，副题 "Manage Coding Agents Remotely"，免费，iPhone/iPad，6 个评分 5.0，开发者栏显示 **Lovecast LLC** | 第三方综述 | — | ✅（主体归属未获官方说明） |
| F-095 | Android **仅走 GitHub Releases APK**；核验日未发现 Google Play 官方条目（Play 上的 "Orca: Boat GPS…" 为航海 App，无关） | 官方发布 | — | ⚠️ 无 Google Play 官方条目 |
| F-096 | 官方两处 Android 版本口径不一致：官网 `/download` 写 "APK 0.0.48"，README 链接为 `mobile-android-v0.0.50` | 官方发布 | — | ⚠️ 版本号不一致 |
| F-097 | 官方 CLI 文档：命令为 `orca`（随桌面端附带）；含 worktree/terminal/file/browser 命令族，`orca worktree create`、`orca snapshot`、`orca click`、`orca fill`；另有 `orca serve`（无头 Linux） | 官方文档 | — | ✅ |
| F-098 | 官方安装页另提供 Arch 的 `yay -S stably-orca-bin` | 官方文档 | — | ✅ |
| F-099 | 第三方星标统计：gstars.dev 于 2026-09-17 显示 70.5K；stably.ai 官网页面显示 71.4k | 第三方综述 / 厂商自宣 | — | ⚠️ 与核验日 API 值 66,453 不一致（时点不同） |
| F-100 | 第三方（Hacker News）用户评价："I've been impressed with orca"、"largely enjoying it" | 第三方综述 | — | ✅ |
| F-101 | 第三方分析：agent fleet management 能否成为独立品类是更难的战略问题；并指出 README 未含采用数据、star 数或独立基准，发布声明为公司自述 | 第三方综述 | — | ✅ |
| F-102 | 第三方对支持 Agent 数量的口径不一：多数写 "30+"，亦有 "25+" | 第三方综述 | — | ⚠️ 第三方口径不一 |
| F-103 | 无官方 quickstart 页（`/docs/quickstart` 404）；官方入门页为 `/docs/first-session`，安装页为 `/docs/install` | 官方发布 | — | ✅ |

## D. 观点分层

以下 7 条为**博文作者观点**，标注 P2 单源，**不得作为事实引用**：

| 编号 | 观点内容 | 属性 |
|---|---|---|
| F-006 | 传统 IDE 里 AI 只是插件；Orca 中干活主力是 Agent，人主要管派任务和看进度 | 范式判断 |
| F-019 | 以前做同样的事需手动开多个终端、自建 worktree、人工记窗口与任务对应关系 | 体验陈述 |
| F-028 | Design Mode + diff 批注流程与人工 review 代码差不多 | 类比评价 |
| F-051 | 同时派五个 Agent 出去，token 消耗也是五份 | 成本推断（与官方"自带订阅"口径自洽，但无实测数据） |
| F-055 | Orca 能火是因为单个 Agent 已够用，真正耗人的是同时开几个之后多出来的杂事 | 归因判断 |
| F-056 | 平时只用一个 Agent、一次只干一件事的用户，Orca 偏重，可先观望 | 适用性建议 |
| F-057 | 已在同时用两三个 AI 编程工具、被窗口和分支搞头疼的用户适合 | 适用性建议 |

**引用规则**：①正文引用上述条目必须显式标注"作者观点"；②推断与归因（F-051、F-055）不得固化为知识条目或量化结论；③适用性建议（F-056/F-057）与官方定位不冲突但无官方背书，仅作读者选型参考；④其余 F-001~F-060 中标注 P1 的条目均已由官方文档逐条证实，可作为事实引用，但引用时应保留 F 编号以便溯源。

## E. 勘误索引

博文口径与权威口径的偏差共 7 条，完整对照表、证据与影响面见 [verification.md](verification.md#三勘误表)。

| # | 一句话索引 | 性质 |
|---|---|---|
| E-1 | 博文写官网为 `onnorca.dev`，实为 **`onorca.dev`**（多打一个 n） | **博文硬错误** |
| E-2 | 博文"不需要注册 Orca 账号"为绝对口径；官方桌面端称 "no account system"，但移动端配对/Relay 要求登录同一 Orca 账号，官方文档自相矛盾 | 核心声明部分失真 |
| E-3 | 博文"6.7 万 Star"；核验日 66,453（≈6.6 万），第三方统计 70.5K–71.4K（时点不同） | 时点口径 |
| E-4 | 博文"ADE = Agent Development Environment"；官方仅使用缩写 ADE（或 agent IDE / desktop IDE），全称无官方出处 | 表述外推 |
| E-5 | 博文"将近三十种"Agent；官方三处口径 29 / 27 / 35，第三方 25+~30+ | 数字口径不稳定 |
| E-6 | 博文 Android "在官网下 APK"方向正确；需补：无 Google Play 官方条目，官网（0.0.48）与 README（0.0.50）版本号不一致 | 补充而非纠正 |
| E-7 | 博文未提安装包形态；macOS 实为 `.dmg`（无 zip 安装包）、Windows `.exe`、Linux `.AppImage`（另有 .deb/.rpm） | 补充 |