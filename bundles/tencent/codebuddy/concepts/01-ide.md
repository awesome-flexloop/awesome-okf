---
type: Concept
title: "CodeBuddy IDE"
description: "CodeBuddy IDE 是基于 VSCode 架构的产设研一体 AI 桌面端，以自然语言驱动从 PRD、设计原型到前后端代码与部署的全流程，集成腾讯云与 Supabase 生态。"
tags: [codebuddy, ide, vscode, product-design-dev, figma, cloudbase, supabase]
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
---

# CodeBuddy IDE

CodeBuddy IDE 是 CodeBuddy 产品矩阵中面向"产设研一体"场景的独立桌面端，定位为"全球首款 AI 驱动的集成产品、设计与开发全栈高级工程师"（F-001），标语为 "Where Design Meets Dev in Real-Time"（F-002）。它将产品经理、设计师、开发者三个角色的工作流整合到同一 AI 驱动环境中。

## 产品定位

与传统 IDE 聚焦代码编辑不同，CodeBuddy IDE 的核心主张是以自然语言为输入，驱动完整研发链路（F-003）：

```
自然语言 → PRD → 设计原型 → 前后端代码 → 部署
```

这意味着用户可以从一句产品描述出发，由 AI 依次完成需求文档、设计原型、代码实现直至上线部署，而无需在多个工具间切换。

## 四阶段开发流程

IDE 文档将开发流程划分为四个阶段（F-010 ~ F-013）：

### 产品阶段

- 需求分析
- PRD（产品需求文档）生成（F-010）

### 设计阶段

- 原型设计
- 草图转高保真
- 组件库支持（F-011）

### 研发阶段

- Figma 设计稿转代码（F-005, F-012）
- 智能代码补全
- 单元测试生成
- 代码审查（通过 `@workspace#Codebase` 引用整个代码库）（F-012）

### 部署阶段

- 沙箱环境部署
- 公开链接发布（F-013）

## 内置生态集成

IDE 深度预置了后端、部署、组件库与模型生态（F-014 ~ F-017）：

| 类别 | 集成服务 | 用途 |
|------|----------|------|
| 后端（BaaS） | Supabase、腾讯 CloudBase | 数据库与后端逻辑一键部署 |
| 部署 | CloudStudio、EdgeOne Pages | 应用托管与发布 |
| 组件库 | TDesign、MUI、Shadcn | 预置 UI 组件，支持自然语言修改 |
| 多模型 | 混元、DeepSeek | AI 能力底座 |

其中，腾讯云 CloudBase 与 Supabase 支持后端一键部署（F-004），Figma 设计稿可一键转为代码（F-005），预置组件库可通过自然语言直接修改（F-006）。

## 技术架构

CodeBuddy IDE 基于 VSCode 架构构建（F-008），这带来两个关键优势：

1. **插件生态兼容**：天然支持 VSCode 插件市场，可复用现有扩展。
2. **远程开发支持**：支持远程 SSH 开发（F-008），可连接远端服务器环境。

这一架构选择使 IDE 既能提供深度定制的产设研 AI 体验，又不脱离成熟的开发者生态。

## 平台支持

| 平台 | 版本要求 |
|------|----------|
| macOS | 11.0+（Apple Silicon 与 Intel 双架构） |
| Windows | 10+ x64 |
| Linux | .deb 包（ARM64 / x86_64） |

以上见 F-007。

## 高级功能

IDE 与插件、CLI 共享一套高级 AI 功能（F-018）：

- **Plan 模式**：规划优先的执行模式
- **Subagents**：子 Agent 委派
- **Skills**：可复用技能包
- **Hooks**：生命周期钩子
- **MCP**：Model Context Protocol 工具集成
- **模型配置**：多模型选择与参数配置
- **检查点**：状态回滚
- **记忆**：长期上下文记忆
- **规则**：自定义行为规则
- **智能提交**：AI 辅助代码提交

## 与插件形态的关系

CodeBuddy 同时提供 IDE 与插件两种形态（F-009）。插件兼容六大宿主 IDE（F-019 ~ F-024）：

| 宿主 IDE | 兼容版本 |
|----------|----------|
| VS Code | 1.82+ |
| IntelliJ IDEA / PyCharm 等 JetBrains IDE | 2022.2+ |
| Android Studio | Flamingo |
| 微信开发者工具 | 1.06+ |
| Xcode | 14.0+ |
| Visual Studio | 2022 |

选择 IDE 可获得最完整的产设研一体体验；选择插件则可在已有 IDE 中获得 CodeBuddy 的 AI 能力，二者共享同一套核心功能。

## 相关概念

- [产品矩阵总览](/concepts/00-product-matrix.md) — IDE 在三态一体中的定位
- [CLI](/concepts/02-cli.md) — 与 IDE 共享高级能力的终端形态
- [NPC 云端 AI 员工](/concepts/03-npc.md) — 基于 CodeBuddy 核心能力的云端延伸
- [Security 安全审计](/concepts/05-security.md) — 代码审查与安全审计的协同
- [IDE 工作流示例](/examples/ide-workflow.md) — 从自然语言到部署的实战流程
- [CLI 快速入门](/examples/quick-start-cli.md) — 三态一体中 CLI 的使用
