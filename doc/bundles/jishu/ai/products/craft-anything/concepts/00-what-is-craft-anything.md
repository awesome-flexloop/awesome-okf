---
okf_version: "0.2"
type: Concept
title: "Craft Anything 是什么：项目身份与定位"
description: "Craft Anything 的身份、归属、许可、热度（带时点）与要解决的问题——一个纯 Rust 的开源净室引擎，看懂任意软件如何工作再让 AI 造出你自己的版本"
tags: [craft-anything, overview, clean-room, rust, open-source]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-11-04T09:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-04T09:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/wB4MHVC4hOWPMobtVidniA"
  - id: github-api
    url: "https://api.github.com/repos/storytold/craft-anything"
  - id: official-status
    url: "https://github.com/storytold/craft-anything/blob/main/STATUS.md"
---

# Craft Anything 是什么：项目身份与定位

## 一句话定位

[Craft Anything](https://github.com/storytold/craft-anything) 是一个**纯 Rust 编写的开源净室（clean-room）引擎**，目标是：**看懂任意网站、应用或游戏如何工作，然后让 AI 造出你自己的版本**（F-004/F-025）。

官方 README 原句：

> See how any website, app or game works, then have AI build your own version; an open-source, clean-room engine in pure Rust.（F-025）

官方 About 补充："Craft Anything: understand how any software works, and craft your own."（F-026）

## 核心事实速查

| 项 | 值 |
|----|-----|
| 仓库 / 归属 | [storytold/craft-anything](https://github.com/storytold/craft-anything)（组织 `storytold`） |
| 建仓 / 最新推送 | 2026-10-31T14:50:00Z / 2026-11-04T01:45:16Z（F-032） |
| 许可 | **Apache-2.0**（GitHub API `license.spdx_id`）；仓库页另标 "Apache-2.0, MIT licenses found"（F-030） |
| 语言 / 前置依赖 | Rust / **Rust 1.97+**（F-031/F-028） |
| 最新版本 | **v0.3.0**，发布于 2026-11-02T17:58:25Z；项目处于**早期 alpha**（F-034/F-009） |
| 社区数据 | Star **8531**、Fork **1422**、Open Issues **149**、Watch 36（**2026-11-04 时点**，F-033） |
| 工作流 | Study → Build → Check → Ready 四步（F-027） |
| 检查机制 | 1440/768/390 px 三宽度比对；相似度 = 布局与画面细节（SSIM）均值，跨页再平均；最多 6 轮或达 90% 停止（F-037） |
| 运行时 | 构建需安装并登录 Claude Code（live runs 记录为 2.1.316）（F-018/F-039） |

## 它要解决的问题

传统"复刻一个界面 / 应用"的路径要么靠人工扒设计与代码，要么让 AI 凭截图"凭感觉"重画——前者慢，后者不可验证。Craft Anything 把这件事拆成可度量的工程流程：

1. **Study（学习）**——系统性地观察目标软件：抓取、结构化、探测其行为（F-027）。
2. **Build（构建）**——让 AI 依据观察结果重建你自己的版本（F-027）。
3. **Check（检查）**——用**可量化的相似度**把重建结果与原站逐宽度、逐页比对（见 [02 · 相似度检查机制](02-likeness-checking-method.md)）。
4. **Ready（就绪）**——收敛到既定阈值后交付（F-027）。

其中的"净室（clean-room）"取向是关键设计约束：**先理解行为、再独立实现**，而不是复制粘贴原站资产——这既是法律上更稳妥的路径，也是"让 AI 真的学会"的前提（F-025）。

## 归属与口径提示

- 博文称项目由 **ArtCraft 团队**开发（F-003）；GitHub 上的**归属组织为 `storytold`**（F-024）。二者口径不同，本知识包并列呈现，不合并为同一实体（详见 [verification.md](../references/verification.md) 勘误③）。
- 博文称"刚刚开源""5300 人关注"（F-002），作者查看时约"四千七百多颗星"（F-008）——均为**成文时点**口径；官方现值 Star 为 8531（2026-11-04 快照，F-033）。动态数字引用须带时点。

## 阅读下一篇

- [01 · 净室与深度两种模式](01-clean-room-and-deep-modes.md)：默认净室模式与深度模式的差别、工具白名单约束。
- [02 · 相似度检查机制](02-likeness-checking-method.md)：三宽度比对、SSIM 均值、6 轮 / 90% 收敛规则。
- [03 · 工具、四步工作流与运行时](03-tools-workflow-and-runtime.md)：工具即 CLI 子命令又是 MCP 工具、Claude Code 运行时、项目文件夹结构。
- [04 · 安装与已知边界](04-install-and-known-limits.md)：安装包形态、前置依赖与早期 alpha 的能力边界。
