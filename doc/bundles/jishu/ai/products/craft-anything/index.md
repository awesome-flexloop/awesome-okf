---
okf_version: "0.2"
type: bundle
title: "Craft Anything：看懂任意软件，让 AI 造出你自己的版本"
description: "纯 Rust 的开源净室（clean-room）引擎——Study→Build→Check→Ready 四步工作流、1440/768/390 三宽度可量化相似度检查（布局+SSIM 均值，最多 6 轮或达 90%）、314 个工具同时是 CLI 子命令与 MCP 工具，含安装实操（源自微信博文经官方一手核验 12✅/11⚠️/0❌）"
tags: [craft-anything, clean-room, rust, mcp, cli, likeness-check, ssim, alpha, 博文转化]
generated:
  by: seven-concepts-cmd+blog-article-to-okf-wiki
  at: "2026-11-04T09:45:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-11-04T09:45:00+08:00"
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/wB4MHVC4hOWPMobtVidniA"
    title: 刚刚开源，5300 人关注的 AI 复刻项目火了
    account: 熊叔
  - id: github-repo
    url: "https://github.com/storytold/craft-anything"
  - id: github-api
    url: "https://api.github.com/repos/storytold/craft-anything"
  - id: github-releases
    url: "https://api.github.com/repos/storytold/craft-anything/releases"
  - id: official-status
    url: "https://github.com/storytold/craft-anything/blob/main/STATUS.md"
---

# Craft Anything：看懂任意软件，让 AI 造出你自己的版本

> **类型**：技术教程/产品解析（含可照做 examples/，操作可复现性两问皆"是"，但未在本机实测）
> **信源**：微信公众号文章《刚刚开源，5300 人关注的 AI 复刻项目火了》（作者「熊叔」，2026-11-03）→ 2026-11-04 经 GitHub REST API、官方 README 与 STATUS.md、第三方报道逐项核验
> **核验结论**：P0/P1 共 23 项 —— **✅ 12 / ⚠️ 11 / ❌ 0**，无核心声明核验失败 → 状态 **stable**（勘误完整登记）
> **数据时点**：Star 等动态数字为 2026-11-04 GitHub API 快照；功能口径对齐 main 与 v0.3.0

## 本文概要

[Craft Anything](https://github.com/storytold/craft-anything) 是一个**纯 Rust 编写的开源净室（clean-room）引擎**，目标是"看懂任意网站、应用或游戏如何工作，然后让 AI 造出你自己的版本"（F-004/F-025）。它把"复刻一个界面/应用"从人工扒代码或让 AI 凭截图"凭感觉重画"，改造成一条**可度量的工程流水线**：**Study → Build → Check → Ready**（F-027）。

其关键设计有两处：一是**净室取向**——先理解行为、再独立实现，而非搬运原站资产；二是**可量化的相似度检查**——在 1440/768/390 px 三种宽度下比对，相似度取"布局"与"画面细节（SSIM）"的均值、跨页再平均，迭代最多 6 轮或达 90% 即停止（F-010~F-016 / F-037）。项目当前处于**早期 alpha**（v0.3.0，2026-11-02 发布），构建需安装并登录 Claude Code。

## 阅读路径

**先建立概念（约 10 分钟）**

1. [Craft Anything 是什么：项目身份与定位](concepts/00-what-is-craft-anything.md)——定位、归属、许可、热度（带时点）
2. [净室与深度两种模式](concepts/01-clean-room-and-deep-modes.md)——为什么默认净室、深度模式与工具白名单边界
3. [相似度检查机制](concepts/02-likeness-checking-method.md)——三宽度比对、SSIM 均值、6 轮 / 90% 收敛

**再看工具与运行**

4. [工具、四步工作流与运行时](concepts/03-tools-workflow-and-runtime.md)——CLI/MCP 双入口、项目目录结构、Claude Code 运行现状

**最后动手实操**

5. [安装与已知边界](concepts/04-install-and-known-limits.md) / [实操示例](examples/00-install-and-run.md)——环境准备、安装包形态、跑一遍 Study → Ready

## 核心事实速查

| 项 | 值 |
|----|-----|
| 仓库 / 归属 | [storytold/craft-anything](https://github.com/storytold/craft-anything)（组织 `storytold`） |
| 建仓 / 最新推送 | 2026-10-31T14:50:00Z / 2026-11-04T01:45:16Z（F-032） |
| 许可 | **Apache-2.0**（GitHub API `license.spdx_id`）；仓库页另标 "Apache-2.0, MIT licenses found"（F-030） |
| 语言 / 前置依赖 | 纯 Rust / **Rust 1.97+**（F-031/F-028） |
| 版本 / 阶段 | **v0.3.0**（2026-11-02 发布）/ **早期 alpha**（F-034/F-009） |
| 社区数据 | Star **8531**、Fork **1422**、Open Issues **149**、Watch 36（**2026-11-04 时点**，F-033） |
| 工作流 | Study → Build → Check → Ready（F-027） |
| 检查机制 | 1440/768/390 px 三宽度；相似度=布局与画面细节(SSIM)均值，跨页平均；最多 6 轮或达 90%（F-037） |
| 工具面 | 每个工具既是 **CLI 子命令**也是 **MCP 工具**（口径见下） |
| 运行时 | 构建需安装并登录 **Claude Code**（live runs 记录 2.1.316）（F-018/F-039） |

## ⚠️ 阅读前必知的三条口径勘误

1. **工具总数三源并存**：博文 **314**（F-017）；第三方 kitploit 亦称 314（F-041）；官方 STATUS.md 为 **300 个引擎工具（含 AI 与 setup 层共 320 个）**（F-036）。三者统计层不同，本包并列呈现，不合并为单一数字。
2. **「10 月 18 日跑通、96%、一分半」时间线存疑**：仓库建仓日为 **2026-10-31**（F-032），晚于所述日期 13 天；且博文另称净室**完整实跑**官方状态页"还没做过"（F-021）。两处口径互相张力，**不作事实断言**。
3. **归属口径**：博文称项目由 **ArtCraft 团队**开发（F-003）；GitHub 归属组织为 **`storytold`**（F-024）。二者并列呈现，不合并为同一实体。

## 采用提示与已知边界

- **Apache-2.0 宽松许可**：可自由使用、修改、商用；仓库页另标 "MIT licenses found"，商用前建议做 License 复核（许可为官方标注，非法律意见）。
- **早期 alpha**：v0.3.0 距建仓仅两日，功能与命令可能快速变化；**构建需安装并登录 Claude Code**，Codex 适配器尚未在真实安装中验证（F-019）。
- **博文为第三方资讯号单篇介绍**：产品能力与机制经官方一手交叉核验；"深度模式""工具白名单强制""人机审批卡片""连拍三次"等为**博文单源**，正文均显式标注。
- **数字时效**：Star/版本为 2026-11-04 核验快照，`stale_after: 2026-12-31`，到期前复核。

## 信源与可信度

- 事实清单（F-001~F-043，含公开性预检）：[references/article-source.md](references/article-source.md)
- P0 核验报告与勘误四张清单：[references/verification.md](references/verification.md)
- 参考层导航：[references/index.md](references/index.md)

## 主题关联

- [rea](../rea/index.md)：统一 MCP 契约的本地逆向编排器——同属"把外部工具接进统一契约"的编排层思路
- [octop](../octop/index.md)：自托管多 Agent 平台——MCP 工具面与 Agent 编排的相邻话题
- [orca-ade](../orca-ade/index.md)：多 Agent 桌面工作台——同为"桌面端 Agent 工作流"形态
- [mobile-use](../mobile-use/index.md)：多智能体移动自动化——同为"让 Agent 操作既有软件"的自动化取向

```{toctree}
:maxdepth: 2
:hidden:

concepts/index
examples/index
references/index
log
```
