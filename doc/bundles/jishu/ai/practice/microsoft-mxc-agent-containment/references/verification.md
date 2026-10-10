---
okf_version: "0.2"
type: Reference
title: "P0/P1 核验报告"
description: "微软 MXC 博文关键声明的 P0/P1 核验结论、权威来源与勘误（名单口径、日期口径、归因）"
tags: [微软, MXC, 核验, P0核验, 勘误]
generated: { by: "blog-article-to-okf-bundle", at: "2026-10-10T09:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-10T09:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/5bHJopj6-WOIBWeR68iaVA
    title: 《微软给Agent立规矩，Windows要管AI了》（腾讯科技，2026-10-08）
  - id: official-mxc
    resource: https://blogs.windows.com/windowsdeveloper/2026/10/07/microsoft-execution-containers-policy-driven-containment-for-ai-agents/
    title: 微软官方 MXC 博客（2026-10-07）
  - id: official-hybrid
    resource: https://blogs.windows.com/windowsexperience/2026/10/07/building-windows-for-hybrid-intelligence/
    title: Building Windows for hybrid intelligence（2026-10-07）
  - id: anthropic
    resource: https://www.anthropic.com/engineering/how-we-contain-claude
    title: How we contain Claude across products（2026-05）
---

# P0/P1 核验报告

> 信源距离预判：博文来自**腾讯科技**（头部科技媒体、第三方转述），虽非厂商自宣，但名称/名单/日期/成效数字仍按 P0 核验。主要核验对象为微软官方博客与 Anthropic 官方文章，均交叉比对成功。

## 核验结论总表

| # | 声明（F） | 核验结果 | 权威来源 |
|---|----------|---------|---------|
| 1 | MXC 在 Windows 11 正式开放（F-001） | ⚠️ 通过（时区口径差异） | 官方博客 10-07 GA |
| 2 | 三能力框架：隔离/身份/可管理性（F-007） | ✅ 通过 | 官方博客 Containment/Identity/Manageability |
| 3 | 首批支持名单（F-004/F-014） | ⚠️ 名单口径不合 | 官方博客（见勘误②） |
| 4 | Pavan Davuluri EVP Windows+Devices（F-005/F-031） | ✅ 通过 | Windows Experience Blog + C-Suite 名单 |
| 5 | Anthropic 93% 批准 + containment（F-010/F-032） | ✅ 通过 | Anthropic 官方 + 多源转述 |
| 6 | MXC 四种隔离后端（F-003/F-028） | ✅ 通过 | 官方博客 |
| 7 | MXC 三种运行模式（F-029） | ✅ 通过 | 官方博客 |
| 8 | MXC 政策五领域（F-030） | ✅ 通过 | 官方博客 |
| 9 | 跨平台/Windows 365（F-021/F-028） | ✅ 通过 | 官方博客 |
| 10 | Entra 区分 agent + Agent 365/Intune 管理（F-008） | ✅ 通过 | 官方博客 |
| 11 | 混合智能 + Copilot+ PC 2 万亿次/月（F-017/F-018） | ⚠️ 2万亿次/月单源 | 官方博客提及混合智能；2 万亿次待补独立源 |
| 12 | Simon Willison "致命三要素" 2025（F-009） | ⚠️ 单源 | 概念真实，2025 提出年份未见独立出处 |

## 勘误明细

### ① F-001 日期口径（时区差异，非错误）
- 博文：北京时间 **2026-10-08** 宣布 MXC 开放。
- 官方：微软 Windows Developer Blog 署名 **2026-10-07**（美西/太平洋时间）确认 MXC generally available，活动在旧金山。
- 处理：正文以官方 10-07 为准，注明博文按北京时间记 10-08。

### ② F-004 / F-014 名单口径（博文名单不完整）
- 博文"首批支持"：OpenAI Codex、GitHub Copilot、OpenClaw、OpenShell（F-004）；另一处：OpenAI Codex、GitHub Copilot、OpenClaw、Replit、OpenShell 已支持（F-014）。
- 官方 MXC 博客精确名单：
  - **已支持**：GitHub Copilot、OpenClaw、OpenAI Codex、Replit、LM Studio、Unsloth AI。
  - **已集成（单列，非首批发榜）**：NVIDIA OpenShell——并补充"凭证管理 + OCSF 审计（企业）"细节，博文未提。
  - **即将支持**：Anthropic Claude Code、Box、Egnyte、Heidi Health、Hermes Agent（Nous Research）、Manus、Perplexity、Raycast、Simular。
  - 博文提及的 Meta Muse 与官方微软名单呼应（Meta 方独立发布），未在微软官方名单中。
- 处理：正文以官方完整名单为准；"首批"表述替换为官方"已支持/已集成/即将支持"三分法；保留博文名单作为口径对照说明。

### ③ F-007 三能力框架归因
- 博文：将"隔离、身份、可管理性"概括归因为 Pavan Davuluri。
- 官方：三能力（Containment/Identity/Manageability）由微软 Windows Developer Blog 的 MXC 发布文（作者 **Logan Iyer**，CVP Windows Platform + Developer）提出；Pavan Davuluri 同日以 Windows Experience Blog 作者身份发布《Building Windows for hybrid intelligence》（EVP Windows + Devices，2026-10-07）。
- 处理：正文将三能力框架归因于微软平台战略（MXC 官方博客），并标注 Pavan Davuluri 为同日"混合智能"博文作者；不单一归因于 Pavan。

## 单源 / 未完全核验项

1. **Copilot+ PC 每月 2 万亿次本地推理（F-018）**：博文表述；官方 MXC 博客未直接给出该数字，未完成独立权威核验 → 正文标注"厂商/博文口径"。
2. **Simon Willison "致命三要素"2025 提出年份（F-009）**：概念真实且为公开安全讨论；具体提出年份未见独立出处 → 标注"作者/博文转述"。
3. **Microsoft Agent 365、Intune 的管理细节（F-008）**：官方博客确认 Entra 区分 agent 活动 + 扩展 Agent 365 到本地 + Intune 策略"即将支持"MXC 进程容器 → ✅ 基本通过，但管理细节为"coming soon"表述。

## 结论

核心声明（MXC 发布、三能力框架、四种隔离后端、三种运行模式、政策五领域、Anthropic 93%、官方支持名单）全部经微软/Anthropic 权威来源核验通过。博文准确性整体较高，主要瑕疵为**名单不完整**与**两处归因/时区口径**，本文已在正文以正确口径呈现并标注源文差异。本 bundle 状态为 **stable**。