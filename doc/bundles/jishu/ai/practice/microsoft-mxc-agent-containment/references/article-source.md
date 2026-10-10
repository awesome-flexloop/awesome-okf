---
okf_version: "0.2"
type: Reference
title: "博文信源事实清单"
description: "腾讯科技《微软给Agent立规矩，Windows要管AI了》事实编号登记（F-001~F-032）"
tags: [微软, MXC, Agent安全, 执行隔离, 博文转化]
generated: { by: "blog-article-to-okf-bundle", at: "2026-10-10T09:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-10T09:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/5bHJopj6-WOIBWeR68iaVA
    title: 《微软给Agent立规矩，Windows要管AI了》（微信公众号"腾讯科技"，作者晓静，编辑徐青阳，2026-10-08）
  - id: official-mxc
    resource: https://blogs.windows.com/windowsdeveloper/2026/10/07/microsoft-execution-containers-policy-driven-containment-for-ai-agents/
    title: Microsoft Execution Containers: Policy-driven containment for AI agents（微软 Windows Developer Blog，2026-10-07）
  - id: official-hybrid
    resource: https://blogs.windows.com/windowsexperience/2026/10/07/building-windows-for-hybrid-intelligence/
    title: Building Windows for hybrid intelligence（Pavan Davuluri，Windows Experience Blog，2026-10-07）
  - id: anthropic
    resource: https://www.anthropic.com/engineering/how-we-contain-claude
    title: How we contain Claude across products（Anthropic，2026-05）
---

# 博文信源事实清单

> 本条为 bundle 内 F 编号**第二份登记**（第一份在 Spec 区 `.trae/specs/okf-wiki-ecosystem/microsoft-mxc-agent-containment-blog-okf-wiki/facts.md`）。V 阶段须机械比对两集合一致性。

## 博文客观事实（F-001 ~ F-025）

| F | 声明 | 性质 |
|---|------|------|
| F-001 | 北京时间 2026-10-08 微软宣布 MXC 在 Windows 11 正式开放 | 事件（⚠️时区口径，见勘误） |
| F-002 | MXC 可限制 Agent 访问的文件、网络等资源，运行中执行规则 | 能力 |
| F-003 | MXC 支持进程隔离、独立会话、WSL 容器、虚拟机、Windows 365 云端执行 | 能力 |
| F-004 | 首批支持：OpenAI Codex、GitHub Copilot、OpenClaw、OpenShell；Claude Code/Manus/Perplexity 计划接入；Meta Muse 推 Windows 原生应用 | 名单（⚠️勘误，见 F-027） |
| F-005 | Pavan Davuluri 为微软 Windows 与设备业务执行副总裁 | 身份 |
| F-006 | 官方文章称传统沙箱非专为 Agent 设计，隔离需求随提示与工具调用变化 | 事件 |
| F-007 | 微软将 MXC 方向概括为隔离/身份/可管理性三关键词 | 能力 |
| F-008 | 微软希望将 Agent 活动纳入 Microsoft Agent 365、Intune 管理体系 | 能力 |
| F-009 | Simon Willison 2025 年提出"致命三要素"（Lethal Trifecta） | 概念（单源） |
| F-010 | Anthropic 2026-05 《How we contain Claude》：Claude Code 用户约批准 93% 权限请求 | 数字 |
| F-011 | Anthropic 转向执行隔离（沙箱/虚拟机/文件系统边界/网络出口）；区分监督 vs 限制能做什么 | 能力 |
| F-012 | Anthropic 披露 Agent 可能绕过既有隔离设计 | 能力 |
| F-013 | Agent 安全需模型/应用/操作系统三层配合 | 作者观点 |
| F-014 | 10-07 名单：OpenAI Codex、GitHub Copilot、OpenClaw、Replit、OpenShell 已支持；Claude Code/Manus/Perplexity 计划接入 | 名单（⚠️勘误，见 F-027） |
| F-015 | 名单含竞争者有益于 MXC 成为执行基础设施 | 作者观点 |
| F-016 | 接入 Windows 隔离可降模型公司自建成本；控制权划分待观察 | 作者观点 |
| F-017 | 微软提出"混合智能"（Hybrid Intelligence）：Agent 在本地/云端模型间选择执行位置 | 概念 |
| F-018 | Copilot+ PC 每月本地执行超 2 万亿次推理；GitHub 测试本地/云端智能路由 | 数字（单源） |
| F-019 | Windows 承担 Agent 执行环境 + 本地 AI 计算平台 | 作者观点 |
| F-020 | 微软未必能成为所有 Agent 的权限管理者（云 Agent 可绕过本地） | 作者观点 |
| F-021 | MXC 可跨操作系统使用，Windows 集成更深入 | 能力 |
| F-022 | 苹果/Google 争夺 Agent 时代系统入口 | 作者观点 |
| F-023 | 类比应用商店：Agent 执行环境或成新平台控制点 | 作者观点 |
| F-024 | 限制过多则开发者转向浏览器/云电脑/其他方式 | 作者观点 |
| F-025 | Agent 接管操作后 Windows 界面重要性下降，但执行环境仍有价值 | 作者观点 |

## 核验补充事实（F-026 ~ F-032）

| F | 声明 | 来源 | 等级 |
|---|------|------|------|
| F-026 | 官方 MXC GA；作者 Logan Iyer（CVP Windows Platform + Developer） | 微软官方博客 2026-10-07 | ✅P0 |
| F-027 | 官方名单：已支持 Copilot/OpenClaw/Codex/Replit/LM Studio/Unsloth；OpenShell 已集成（凭证+OCSF 审计）；将支持 Claude Code/Box/Egnyte/Heidi Health/Hermes Agent/Manus/Perplexity/Raycast/Simular | 官方博客 | ✅P0 |
| F-028 | 四种隔离后端：Process（跨平台）/Session（仅Win11）/WSLc（仅Win11）/MicroVM（实验）；Windows 365 GA | 官方博客 | ✅P0 |
| F-029 | 三种运行模式：Enforcement/Learning/Permissive | 官方博客 | ✅P0 |
| F-030 | 政策五领域：Containment/Process/File system/Network/User interface | 官方博客 | ✅P0 |
| F-031 | Pavan Davuluri 确认为 EVP Windows + Devices | 官方博客 | ✅P1 |
| F-032 | Anthropic containment 方法确认；93% 被多源转述 | Anthropic 官方 + 第三方 | ✅P0 |

## 勘误摘要

1. **F-001 日期口径**：博文用北京时间（10-08），官方用美西/太平洋时间（10-07）。正文以官方口径为准。
2. **F-004/F-014 名单口径**：博文"首批"名单不完整；官方"已支持"另含 Replit、LM Studio、Unsloth AI，"即将支持"另含 Box、Egnyte、Heidi Health、Hermes Agent、Raycast、Simular；OpenShell 为"已集成"。正文以官方名单为准。
3. **F-007 归因**：三能力框架由官方 MXC 博客（Logan Iyer）提出；Pavan Davuluri 的《Building Windows for hybrid intelligence》为并行发布。全文见 [verification.md](verification.md)。