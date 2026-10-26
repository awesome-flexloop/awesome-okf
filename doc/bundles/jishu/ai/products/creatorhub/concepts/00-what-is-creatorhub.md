---
okf_version: "0.2"
type: Concept
title: "CreatorHub 是什么：项目身份与时间线"
description: "CreatorHub 的定位、仓库与作者、2026-07 创建与 v0.2.4 时间线、2,562 Star 快照、无 LICENSE 的许可状态，以及博文与官方口径的六项差异（事实层）"
tags: [creatorhub, project-profile, timeline, license, star-history, self-media]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-26T10:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-26T10:50:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/Y5AvYGtyj2t9xPJIXuSYBA
  - id: github-api
    url: https://api.github.com/repos/3441293738/creatorhub
  - id: official-readme
    url: https://raw.githubusercontent.com/3441293738/creatorhub/main/README.md
  - id: official-changelog
    url: https://raw.githubusercontent.com/3441293738/creatorhub/main/CHANGELOG.md
---

# CreatorHub 是什么：项目身份与时间线

> 事实层（What / When / Who）。本文只陈述可核验事实；架构机制见 [01](01-local-first-architecture.md)，能力边界见 [02](02-platform-capability-matrix.md)，许可与合规见 [04](04-boundaries-license-and-compliance.md)。

## 一句话定位

[CreatorHub](https://github.com/3441293738/creatorhub) 是一个用 **Python + FastAPI** 编写的**本地 Web 内容运营面板**：把抖音、小红书、快手、视频号的账号管理、作品/评论监控、关键词批量采集、内容下载、发布与跨平台转发、自动评论/回复和通知，收进一个本地运行、浏览器操作的界面（F-027、F-029、F-030）。

官方仓库的一句话描述是“多平台内容监控·采集·搬运 一个 Web 面板管起抖音 / 小红书 / 快手”（F-026），README 首行则写“支持抖音 / 小红书 / 快手 / 视频号”（F-027）。两处差异不是矛盾，而是**能力不对等**：视频号只支持本账号数据（F-045）。

## 项目身份

| 项 | 值 | 依据 |
|---|---|---|
| 仓库 | `3441293738/creatorhub`（个人账号，非组织仓库） | F-020 |
| 形态 | 本地 Web 面板 + Windows 安装版 | F-029、F-054 |
| 主语言 | Python | F-022 |
| 创建时间 | 2026-07-03 | F-020 |
| 默认分支 | `main` | F-020 |
| 最近推送 | 2026-10-26（仍在高频迭代） | F-020、F-028 |
| 许可 | **无 LICENSE，API license=null** | F-023 |
| 主页 | GitHub Pages 在线预览（脱敏示例数据） | F-025 |

> **“个人仓库”不是贬义，但要计入供应风险**：单维护者项目对平台页面改版、接口变更的响应速度取决于作者时间；Issue 14 个开放（F-021），使用前应评估“出问题能否自己改”。代码分层清晰（F-033），具备自维护可行性，但无 LICENSE 会限制二次分发（F-065）。

## 时间线

| 时间 | 事件 | 依据 |
|---|---|---|
| 2026-07-03 | 仓库创建 | F-020 |
| 2026-08-28 | 微信公众号「明见如是」发布推介博文（1.7k Star 口径） | F-002、F-061 |
| 2026-09-10 | v0.1.0 首个 Release | F-024 |
| 2026-09-14 | v0.2.0：Windows 安装版、后台更新检查、中文安装向导 | F-024、F-054、F-071 |
| 2026-09-18 / 09-20 | v0.2.2 / v0.2.3：秒级监控频率、多账号同主页监控、抖音粉丝/私信 API | F-071 |
| 2026-10-16 | v0.2.4：统一采集、小红书收藏夹、账号工作台、事件中心、Webhook 出站 | F-071 |
| 2026-10-26 | 本知识包核验快照：2,562 Star / 472 Fork / 14 Issue | F-021 |

> **关键时序**：源文发布时（08-28）项目还没有任何 Release，只能源码运行——所以源文说“不是双击就完事”在当时成立；09-14 的 v0.2.0 才改变部署体验（F-063）。读旧文必须对齐时间线，否则会把“已解决的门槛”当成现状。

## 社区热度（带时点）

2026-10-26 快照：**Star 2,562、Fork 472、开放 Issue 14**（F-021）。源文 08-28 口径为 1.7k（F-007），两者相差约 50%，属于三个多月增长的正常区间，但源文数字无法回溯逐字验证，本包统一采用官方现值并标注日期（F-061）。

Star 不适合作为质量结论：它反映传播，不反映四平台当前可用性、风控强度或维护承诺。判断可用性请看 [平台能力矩阵](02-platform-capability-matrix.md) 与 [核验报告](../references/verification.md)。

## 许可状态：必须单独说清

- 仓库根目录**没有 LICENSE 文件**，GitHub API `license` 字段为 `null`（F-023）。
- 法律默认：**版权保留（All rights reserved）**。公开可读、可克隆、可自行部署，不等于授予复制、修改、分发、商用许可（F-065）。
- 因此本包不使用“开源项目”作为事实陈述，统一写“公开仓库 / source-available”。“能自己部署”成立，“可自由二次分发”不成立。
- 需要二次开发或商用：联系作者取得书面授权；企业内部使用也应做许可审查。

## 源文与官方口径的六项差异

| # | 源文说法 | 官方事实 | 类型 |
|---|---|---|---|
| 1 | “开源项目”“开源，能自己部署” | 无 LICENSE，默认版权保留 | ❌ 核心勘误（F-065） |
| 2 | “Python + FastAPI + Playwright” | `patchright==1.61.2`（Playwright 兼容分支）+ Chrome CDP | ⚠️ 技术口径（F-062） |
| 3 | 标题“视频号全管了” | 视频号仅本账号数据，不支持他人作品监控/下载 | ❌ 能力夸大（F-064） |
| 4 | “不是双击就完事” | v0.2.0 起 Windows 安装版可双击安装 | ⚠️ 时效（F-063） |
| 5 | “统一发到多个平台” | 各平台分别发布 + 下载后跨平台转发 | ⚠️ 口径收窄（F-066） |
| 6 | “1.7k star” | 2026-10-26 为 2,562 | ⚠️ 动态数字（F-061） |

> 六项中两项为 ❌：许可与视频号能力。前者影响“能不能用/能不能分发”，后者影响“买了能不能干预期的事”，都属于采用决策的核心，因此 bundle 标记 `status: flagged`，而非 stable。

## 它解决的真实问题

源文列出的痛点很具体：一个作品四个后台各传一遍、评论散落四个 App、评论三天后才看到、播放量要逐个 App 刷新（F-004）。CreatorHub 的对应解法是：统一账号与任务面板、评论聚合、监控轮询、数据本地留存（F-029、F-037~F-039、F-047）。

这属于**运营工作流收敛**，不是“增长工具”：它不会让内容变好，也不保证流量；它把重复操作与信息收集集中，让人把时间放回选题与判断（F-019，作者观点）。

## 下一步

- 想知道“为什么能本地跑、账号怎么隔离”：[本地优先架构](01-local-first-architecture.md)
- 想知道“四个平台各能做什么、视频号到底缺什么”：[平台能力矩阵](02-platform-capability-matrix.md)
- 想直接安装上手：[Windows 安装版](../examples/00-windows-install.md) / [源码运行](../examples/01-source-run.md)
