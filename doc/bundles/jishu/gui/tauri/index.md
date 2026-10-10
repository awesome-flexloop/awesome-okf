---
okf_version: "0.2"
type: bundle
title: "Tauri 2.0 与 Electron 对比教程"
description: "基于公众号「前端之神」单篇公开文章的 OKF 教程——Tauri 2.0 架构、性能真相、升级点与选型决策，含 F 编号事实登记与 P0 核验"
tags: [Tauri, Electron, 桌面开发, 跨平台, WebView, Rust, 技术选型]
generated: { by: "process:wechat-public-okf", at: "2026-10-10T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-10T00:00:00+08:00" }
status: draft
stale_after: 2027-10-10
sources:
  - id: wechat-frontend-god-tauri-electron
    resource: "https://mp.weixin.qq.com/s/cvvU940cWXLA_qP8NCDkGg"
    title: "取代 Electron？Tauri 2.0 做到全平台适配、轻量化！（前端之神）"
  - id: tauri-20-release
    resource: "https://v2.tauri.app/blog/tauri-20/"
    title: "Tauri 2.0 Stable Release（Tauri 官方博客）"
  - id: electron-why
    resource: "https://www.electronjs.org/docs/latest/why-electron"
    title: "Why Electron（Electron 官方文档）"
---

# Tauri 2.0 与 Electron 对比教程

本知识包源自公众号「**前端之神**」的单篇公开技术评论文章《取代 Electron？Tauri 2.0 做到全平台适配、轻量化！》，经 **R→I→E** 工作流整理为可溯源的 OKF 教程，聚焦 **Tauri 2.0 vs Electron** 的架构本质、性能真相、升级点与选型决策。

## 内容概览

- **事实登记**：F-001 ~ F-018，区分页面事实 / 作者陈述 / 作者数据，见 [事实登记表](references/facts.md)
- **P0 核验**：8 项可独立核验技术事实全部通过官方来源核验；具体数值标注单源局限，见 [核验报告](references/verification.md)
- **知识地图**：事实层 / 机制层（执行者洞察）/ 迁移层，见 [知识地图](references/knowledge-map.md)

## 学习路径

1. [01 · 认识 Tauri 2.0 与 Electron](concepts/01-overview-tauri-electron.md)——两种方案的本质差异（推荐先读）
2. [02 · Tauri 架构与性能真相](concepts/02-architecture-performance.md)——系统 WebView + Rust 后端，性能数字如何读
3. [03 · Tauri 2.0 升级点](concepts/03-tauri2-upgrade.md)——相比 1.0 的四大升级
4. [04 · 选型决策指南](concepts/04-selection-guidance.md)——何时选 Tauri、何时选 Electron

## 目录导航

- **concepts/**：4 篇概念文档，见 [概念体系](concepts/index.md)
- **references/**：信源登记、事实登记、P0 核验、知识地图，见 [参考与核验](references/index.md)
- **[log.md](log.md)**：变更日志

## 信任与局限

- **单源局限**：全部内容源自单一公众号文章；核心架构事实经官方核验，具体性能数值未独立复测（见 [verification.md](references/verification.md)）。
- **时效性**：成文于 2026-10，Tauri/Electron 生态快速迭代，建议在 `2027-10-10` 前复核。
- **无 `examples/` 目录**：本文为选型引导（非可复现操作步骤），按两问门判定暂不设示例。

```{toctree}
:maxdepth: 1

concepts/index
references/index
log
```