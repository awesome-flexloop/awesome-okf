---
type: Concept
title: "Agent-Autoloop 是什么：从一篇开源公告读起"
description: "发布事实、项目定位、设计来源与版本边界——理解这套「确定性内核 + 万物皆插件」Agent 自动化中台的起点"
tags: ["项目定位", "开源公告", "设计来源", "阅读路线"]
status: stable
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/T9_acg247gxzUNL4j5zrCw
    title: "开源我这折腾了1年的「Agent自动化系统」（2026-11-04）"
  - id: official-readme
    resource: https://github.com/KKKKhazix/agent-autoloop/blob/main/README.md
    title: "Agent Autoloop 官方 README"
  - id: official-install
    resource: https://github.com/KKKKhazix/agent-autoloop/blob/main/INSTALL.md
    title: "Agent Autoloop 官方 INSTALL"
---

# Agent-Autoloop 是什么

> Fact index：本篇声明对应 [信源与事实登记](../references/article-source.md) 的 F-001~F-009、F-043、F-044、F-045、F-065。

## 一句话定位

**Agent-Autoloop** 是一个极轻量的 Agent 自动化中台：把任务调度做成一个零外部依赖的**内核**，把事件来源、Agent、通知通道，甚至代码上线流水线全部拆成可插拔的**插件**，让命令行 Agent 在后台自己接活、自己跟进到底，平时不打扰人，遇到拿不准的事才发卡片找人拍板（F-043）。

它的名字直白——作者的命名说明是「就是这么简单、直白、不绕弯子」；仓库地址为 `https://github.com/KKKKhazix/agent-autoloop`（F-003），采用 MIT 许可证（F-065）。

## 发布时序

| 时点 | 事件 | 事实 |
|------|------|------|
| 2026-11-02 前后（「周一」） | 前篇《折腾了整整1年，毫无保留地分享一下我这套Agent自动化系统。》发布 | F-002 |
| 2026-11-04 08:19 | 公众号「数字生命卡兹克」发布开源公告，标注原创 | F-001 |
| 中间两天 | 作者自述收到反馈后「花了两天时间重写」，重新梳理架构、抽象解耦 | F-005 |
| 2026-11-06 | 本知识包以官方 `README.md` / `INSTALL.md`（`main` 分支快照）核验 | 见 [P0 核验报告](../references/verification.md) |

作者自述周一没有开源的两个理由是「没到能称为基建架构的地步」与「没想到对这么多人有用」（F-004）——这是作者叙事，官方仓库无对应记载，按单源处理。

## 它解决什么问题

官方 README 给出的痛点是：平时用 Claude Code、Codex 这类命令行 Agent，大多是「人守着终端用」——输一句话、盯着它跑、等它问下一步；一旦关掉窗口或人走开，事情就断了（F-043）。

Autoloop 的三个设计取舍（均来自官方 README）：

1. **一台电脑、一条命令就能跑**：装在 Mac 或 Linux 上，不用买云服务器，也不用开放公网端口。
2. **一行配置接新 Agent**：不需要 SDK，也不需要改 Agent 源码；能接收提示词并打印最后一条回复的命令行工具都能接（F-053）。
3. **没有后台界面**：需要拍板时把卡片推到飞书、钉钉、企微、Slack、Discord 或桌面通知；想看全局进展，敲一行命令（F-036、F-052）。

> 为什么「没有后台界面」反而值得写进定位？这决定了整套系统的交互模型：状态查询靠 CLI，人工介入靠通道插件，而不是常驻一个 Web 控制台。理解这一点，后面五步流程里的「批奏折」分支才不显得奇怪。

## 设计来源：两个可交叉引用的同组知识包

博文将重构的设计来源表述为两处（F-006）：

- **Pi 极简内核与 Extensions 设计** → 对应本分组的 [pi-agent-harness](../../pi-agent-harness/index.md) 与 [pi-cli](../../pi-cli/index.md)。
- **DeepSeek Harness「一切皆插件」架构理念** → 对应本分组的 [deepseek-harness](../../deepseek-harness/index.md) 与 [deepseek-harness-0-2](../../deepseek-harness-0-2/index.md)。

> 引文边界：「一切皆插件」是作者对 DSH 设计思想的概括表述，官方 README 中没有这一短语；本教程按转述处理，不作为 DSH 官方定位引用（见 [P0 核验报告](../references/verification.md) 勘误四张清单之④）。

作者把重构目标表述为「极其轻量、快速、安全，但同时也是可扩展性极佳」（F-007，作者观点）。这句主观判断不宜当作验收标准；可核验的对应物是内核的四条禁令与四个机制，见 [01 内核与五步流程](01-kernel-and-loop.md) 与 [02 内核四机制](02-four-mechanisms.md)。

## 版本、平台与许可证边界

| 项 | 官方口径 | 事实 |
|----|---------|------|
| 版本 | 作者自述「还只是 1.0.0 版本」，可能有不完善与 BUG；安装取最新 Release（通过全部检查的版本） | F-008、F-046 |
| 平台 | macOS / Linux；**Windows 版待定**，作者称 11 月 7、8 日回家后开发并做兼容性测试，进度见 issue #17；WSL2 可跑但有多项限制 | F-044、F-045 |
| 依赖 | Node.js 24 或更新、Git、curl，以及一个已登录的命令行 Agent；不需要 GitHub 账号 | F-044 |
| 许可证 | MIT | F-065 |

> ⚠️ 博文「电脑上装个 Node 就能跑」（F-013）没有区分平台与版本。本篇以官方口径为准：Windows 用户在 WSL2 之外没有官方支持路径，且 WSL2 有 systemd、桌面通知、用量上报等具体限制（见 [安装与首次试跑](../examples/01-install-and-first-run.md)）。

## 阅读路线

| 读者意图 | 建议路径 |
|---------|---------|
| 想先搞清楚「它在干什么」 | 本篇 → [01 内核与五步流程](01-kernel-and-loop.md) |
| 关心长流程、断电恢复、Prompt 注入 | [02 内核四机制](02-four-mechanisms.md) |
| 关心怎么接自己的 Agent / 通道 / CI | [03 插件生态](03-plugin-ecosystem.md) → [插件接入与交付演练](../examples/03-plugins-and-delivery.md) |
| 想直接上手 | [安装与首次试跑](../examples/01-install-and-first-run.md) → [规则与回执](../examples/02-rules-and-receipts.md) |
| 想核对某个数字或说法 | [信源与事实登记](../references/article-source.md) → [P0 核验报告](../references/verification.md) |

## 本教程的三条阅读纪律

1. **事实、作者观点、教程解读三层分离**：带 F 编号的是登记事实；「作者观点 / 作者自述」会显式标注；由本教程做的类比与推断一律写成「可以理解为」并说明依据。
2. **数字取官方口径**：性能与规模数字以官方 README 的实测表为准（F-061），博文的口语化近似只在口径对照时出现（F-013、F-014）。
3. **示例未在本机实测**：`examples/` 中的命令与配置来自官方文档，可照做，但本知识包生成过程中未安装运行该项目；且官方已标注多项「未测 / 未逐个跑过」，请按 [P0 核验报告的分档](../references/verification.md) 判断。
