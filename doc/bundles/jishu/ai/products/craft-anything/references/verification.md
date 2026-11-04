---
okf_version: "0.2"
type: Reference
title: "Craft Anything 博文 P0 权威核验报告（verification）"
description: "对博文 P0/P1 声明的官方一手交叉核验：仓库元数据/日期/许可/检查机制/工具数/运行时，含勘误四张清单"
tags: [craft-anything, verification, p0-check, fact-check, errata]
generated: { by: "blog-article-to-okf-wiki:R/V", at: "2026-11-04T09:20:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/wB4MHVC4hOWPMobtVidniA"
  - id: github-api
    url: "https://api.github.com/repos/storytold/craft-anything"
  - id: github-releases
    url: "https://api.github.com/repos/storytold/craft-anything/releases"
  - id: official-status
    url: "https://github.com/storytold/craft-anything/blob/main/STATUS.md"
---

# P0 权威核验报告

> 核验时间：2026-11-04。信源：GitHub REST API（仓库元数据与 releases 时点快照）、官方仓库 README、官方 STATUS.md、第三方报道交叉（均为项目一手 / 可公开访问信源）。
> 博文信源距离：第三方资讯号单篇介绍文（作者「熊叔」）；其中产品能力与机制描述属**从业者一手介绍**，非厂商官方发布稿。
> **结论**：P0/P1 共 23 项 —— **✅ 12 / ⚠️ 11 / ❌ 0**，无核心声明核验失败 → bundle 状态 **stable**（勘误完整登记）。

## 核验总览

| 级别 | 数量 | 结论分布 |
|------|------|---------|
| P0（仓库存在性/语言/许可/日期/检查机制/工具数/运行时/时间线） | 15 | ✅ 9 / ⚠️ 6 / ❌ 0 |
| P1（模式/白名单/审批卡片/Codex 适配器/前置依赖/流程） | 8 | ✅ 3 / ⚠️ 5 / ❌ 0 |
| 合计 | 23 | **✅ 12 / ⚠️ 11 / ❌ 0** |

**总体评估**：博文事实准确度高——项目真实存在（`storytold/craft-anything`）、纯 Rust、许可 Apache-2.0（另标 MIT）、净室引擎定位、1440/768/390 三宽度比对与「布局+画面细节（SSIM）取均值、跨页再平均、最多 6 轮或达 90% 停止」的检查机制、v0.3.0（2026-11-02）发布、构建需 Claude Code，全部与官方一手材料一致。11 项 ⚠️ 集中在**动态数字时效**（Star 数）、**口径分层**（工具数 314/300/320）、**单源未证**（深度模式、白名单、审批卡片、10 月 18 日跑通），无一项构成核心声明造假。

## 勘误四张清单

### ① 日期/版本表

| 博文声明（F） | 官方核验 | 结论 |
|--------------|---------|------|
| "10 月 31 日建仓"（F-007） | `created_at=2026-10-31T14:50:00Z`（F-032） | ✅ 一致 |
| "11 月 2 日发 v0.3.0"（F-009） | release v0.3.0 `published_at=2026-11-02T17:58:25Z`（F-034） | ✅ 一致 |
| "官方记录过一次跑通在 **10 月 18 日**，96% 相似度、一分半"（F-022） | 仓库 `created_at=2026-10-31`，**晚于所述日期 13 天**（F-032）；公开信源无该次记录（F-021） | ⚠️ **时间线存疑**：公开信源无法证实；若属实应为开源前内部记录。正文标注"仅博文单源、与建仓时间先后关系存疑" |

### ② 成效数字溯源表

| 博文声明（F） | 官方核验 | 结论 |
|--------------|---------|------|
| 作者查看时"四千七百多颗星"（F-008） | 官方现值 Star **8531**（2026-11-04 快照，F-033） | ⚠️ **时效差异非造假**；正文呈现官方现值并标注博文口径 |
| 标题"5300 人关注"（F-002） | 官方 Star 8531 / Watch 36（F-033） | ⚠️ 成文时点口径；"关注"非 GitHub 原生指标，量级与 Star 一致 |
| "净室完整实跑……做到 96% 相似度、用了一分半"（F-022） | 博文自身又称官方状态页"净室完整实跑**还没做过**"（F-021） | ⚠️ **两处口径互相张力**：正文并列呈现，提示"完整实跑"与"一次记录跑通"非同一口径 |
| "**314** 个工具"（F-017） | STATUS.md：**300 引擎工具**（320 含 AI 与 setup 层）（F-036）；第三方 kitploit 亦称 314（F-041） | ⚠️ **口径差异**：三源并存，正文并列呈现并标注统计层差异 |

### ③ 口径对照表

| 博文声明（F） | 官方口径 | 结论 |
|--------------|----------|------|
| "**ArtCraft 团队**开发"（F-003） | GitHub 归属组织为 **`storytold`**（F-024） | ⚠️ 组织名 vs 团队名口径不同；正文并列，不合并为同一实体 |
| "纯 Rust"（F-003） | `language=Rust`（F-031） | ✅ 一致 |
| 博文未声明许可 | GitHub API `license.spdx_id=Apache-2.0`；仓库页另标 "Apache-2.0, MIT licenses found"（F-030/F-043） | ✅ 官方补充；双许可迹象 |
| "净室（默认）/ 深度模式"（F-005） | README 官方定位 "an open-source, **clean-room engine** in pure Rust"（F-025） | ⚠️ 净室 ✅；"深度模式"博文单源 |
| "314 个工具，每个既是 CLI 子命令也是 MCP 工具"（F-017） | README 口径 314（含 298 引擎）；STATUS.md 300 引擎 / 320 含 AI+setup 层（F-036） | ⚠️ **层级不同**：引擎层 vs 全部工具层，非同一统计范围 |
| "构建需安装登录 Claude Code"（F-018） | STATUS.md：live runs 使用 Claude Code **2.1.316**（F-039） | ✅ 一致（版本号官方细化） |

### ④ 引文逐字核对表

| 博文引用（F） | 官方原文核对 | 结论 |
|--------------|-------------|------|
| "看懂任意网站、应用或游戏如何工作，然后让 AI 造出你自己的版本"（F-004） | README："See how any website, app or game works, then have AI build your own version"（F-025） | ✅ 意译一致；博文为中文意译，**非官方原句**，引用时不宜加引号直引 |
| 前置依赖 Rust 1.97+（F-028，官方补充） | README 前置依赖声明 | ✅ |
| `craft-anything-cli rebuild`（F-029） | README 命令示例 | ✅ |

## 博文笔误登记（非事实错误，正文不沿用错误口径）

- 博文**自身已订正**一处截图清单笔误：390px 宽度下网页横向滚动，实际渲染宽度为 **412px**（F-014）——属作者自纠，非我方勘误。
- 未见其他笔误；博文未声明许可 / 版本号 / 工具数统计口径，属**信息省略**而非事实错误，已在正文用官方口径补齐。

## 核验方法与局限

1. **方法**：GitHub REST API 获取仓库不可伪造元数据（创建/推送时间、Star/Fork/Issues、`license.spdx_id`、语言、体积）；REST releases API 取 v0.3.0 发布时点与资产清单；WebFetch 拉取官方 README 与 STATUS.md 交叉比对定位、四步流程、前置依赖、命令、检查机制与运行时；第三方报道（kitploit / opennet.ru / madrobot.blog / gadgetpilipinas.net / eyerys.com）作旁证。
2. **局限**：① **未在本机实际安装或运行** Craft Anything（本机为 Windows，未配置 Rust 1.97+ 工具链与 Claude Code 登录态），安装包形态与 CLI 行为层以官方 README / releases 资产清单为准则；② releases 资产清单仅抓取到 Linux aarch64 与 FreeBSD 系列样例，**未穷尽全部平台资产**（Windows / macOS / WASM 资产存在性以博文为准，标注 ⚠️）；③ 博文配图内嵌文字未采集，以正文文字事实为准；④ "深度模式""工具白名单强制""人机审批卡片"等博文单源声明未获官方一手逐字确认，标注"仅博文单源"。
3. **复核安排**：`stale_after=2026-12-31` 前复核 Star / 版本演进（早期 alpha 迭代快）、工具数官方口径（300 / 314 / 320 收敛情况）、Windows / macOS / WASM 资产落地、以及"净室完整实跑"是否补做。

## 阅读下一篇

- 概念教程：[00 · Craft Anything 是什么](../concepts/00-what-is-craft-anything.md)
- 机制教程：[02 · 相似度检查机制](../concepts/02-likeness-checking-method.md)
