---
type: Concept
title: "CodeBuddy 产品矩阵总览"
description: "CodeBuddy 产品矩阵由 IDE、插件、CLI 三种形态与 NPC、WorkBuddy、Security 三大延伸产品构成，覆盖本地编码、云端交付、办公协同与安全审计全场景。"
tags: [codebuddy, product-matrix, overview, ide, cli, npc, workbuddy, security]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-02-23
sources:
  - id: ide-official
    resource: /references/ide.md
    title: CodeBuddy IDE 产品官网
  - id: docs-intro
    resource: /references/docs-intro.md
    title: CodeBuddy IDE 文档介绍
  - id: cli-official
    resource: /references/cli.md
    title: CodeBuddy CLI 产品官网
  - id: npc-official
    resource: /references/npc.md
    title: CodeBuddy NPC 产品官网
  - id: workbuddy-official
    resource: /references/workbuddy.md
    title: WorkBuddy 在线 AI 助手
  - id: security-official
    resource: /references/security.md
    title: CodeBuddy Security 安全审计平台
---

# CodeBuddy 产品矩阵总览

CodeBuddy 是腾讯推出的 AI 编程产品矩阵，以"AI 驱动全栈研发"为核心，从本地开发工具延伸到云端自主 Agent、在线办公助手与代码安全审计，形成覆盖软件研发生命周期的产品体系。本概念页梳理矩阵中六大产品的定位、关系与适用场景。

## 矩阵构成

CodeBuddy 产品矩阵可分为两层：**核心研发层**（三种形态共享同一 AI 引擎）与**场景延伸层**（面向云端交付、办公协同、安全审计的独立产品）。

### 核心研发层：三态一体

CodeBuddy 以三种形态交付同一套 AI 编程能力（F-009）：

| 形态 | 定位 | 典型用户 |
|------|------|----------|
| [IDE](01-ide.md) | 产设研一体的独立桌面端 | 需要从 PRD 到部署全流程的团队 |
| 插件 | 即插即用于 VS Code/JetBrains/Xcode 等主流 IDE | 已有固定 IDE 工作流的开发者 |
| [CLI/Code](02-cli.md) | 终端命令行工具 | 偏好终端、服务器/无头场景开发者 |

三种形态共享 Plan 模式、Subagents、Skills、Hooks、MCP、记忆、规则、智能提交等高级功能（F-018），学习成本可跨形态迁移。IDE 基于 VSCode 架构（F-008），插件兼容六大宿主 IDE（F-019 ~ F-024），CLI 通过 npm 包 `@tencent-ai/codebuddy-code` 分发（F-025, F-027）。

### 场景延伸层

| 产品 | 定位 | 核心场景 |
|------|------|----------|
| [NPC](03-npc.md) | 云端 AI 员工（Cloud Agent） | 目标驱动的自主需求交付、多 Agent 协同 |
| [WorkBuddy](04-workbuddy.md) | 在线 AI 助手 Web 应用 | 日常办公与代码开发的对话式协同 |
| [Security](05-security.md) | AI 代码安全审计平台 | 漏洞发现、PoC 验证、自动修复 |

## 产品关系

```
┌─────────────────────────────────────────────────────────┐
│                    CodeBuddy AI 引擎                      │
│   Plan · Subagents · Skills · Hooks · MCP · 记忆 · 规则   │
└──────────┬──────────────────┬──────────────────┬────────┘
           │                  │                  │
     ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
     │    IDE     │      │   插件     │      │    CLI    │
     │ 产设研一体  │      │ 主流 IDE   │      │  终端原生  │
     └───────────┘      └───────────┘      └───────────┘
           │                  │                  │
           └──────────┬───────┴──────────┬───────┘
                      │                  │
              ┌───────▼───────┐  ┌───────▼───────┐
              │     NPC       │  │  WorkBuddy    │
              │  云端 AI 员工  │  │  在线助手     │
              └───────────────┘  └───────────────┘
                      │
              ┌───────▼───────┐
              │   Security    │
              │  安全审计平台  │
              └───────────────┘
```

- **NPC 基于 CodeBuddy 打造**（F-039），将本地 AI 能力部署到 CNB 云端，实现自主交付。
- **WorkBuddy 顶部导航**直接链接 IDE、插件、CLI（F-059），表明它是 CodeBuddy 生态的在线入口之一。
- **Security** 可与研发流程协同：NPC 自主修复构建报错（F-047），Security 提供漏洞修复补丁（F-068），两者共同构成质量与安全闭环。

## 适用场景选择

| 场景 | 推荐产品 |
|------|----------|
| 从想法到 MVP 的快速验证 | IDE（自然语言→PRD→设计→代码→部署） |
| 在现有 IDE 中获得 AI 辅助 | 对应宿主的 CodeBuddy 插件 |
| 服务器端、CI 环境、终端偏好 | CLI |
| 指派独立需求让 AI 自主完成 PR | NPC |
| 办公文档、数据分析、日常开发问答 | WorkBuddy |
| 代码漏洞审计与自动修复 | Security |

## 计费模式

矩阵中多款产品采用 Token 消耗计费：

- CLI 按 Token 消耗计费（F-038）。
- NPC 按量收取 Agent 执行 Token 消耗（F-051）。
- Security 通过腾讯云购买入口开通（F-079）。
- WorkBuddy 当前处于公测阶段（F-060）。

## 跨产品能力复用

CodeBuddy 矩阵的核心优势在于能力的跨产品复用：

1. **Skills 与规则**在 IDE、插件、CLI 间共享（F-018），NPC 也支持 Skill 定制（F-049）。
2. **MCP**在 CLI 中同时支持客户端与服务器（F-032），可作为工具被其他产品调用。
3. **CodeBuddy.md 项目手册**由 CLI `/init` 生成（F-030），作为跨形态共享的项目上下文载体。
4. **多模型支持**覆盖混元与 DeepSeek（F-017），为矩阵各产品提供统一模型底座。

## 相关概念

- [CodeBuddy IDE](01-ide.md) — 产设研一体的桌面端，全流程开发链路
- [CLI](02-cli.md) — 终端原生工具，分层记忆与 Sub-agents
- [NPC 云端 AI 员工](03-npc.md) — 目标驱动的云端自主 Agent
- [WorkBuddy 在线助手](04-workbuddy.md) — 办公与开发双场景对话式助手
- [Security 安全审计](05-security.md) — 六步安全闭环与对抗性 AI 审查
- [CLI 快速入门](../examples/quick-start-cli.md) — 体验三态一体中的 CLI 形态
- [IDE 工作流](../examples/ide-workflow.md) — 从自然语言到部署的实战流程
