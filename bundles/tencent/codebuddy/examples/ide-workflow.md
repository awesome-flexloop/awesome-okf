---
type: Example
title: "IDE 产设研工作流"
description: "使用 CodeBuddy IDE 完成从自然语言需求到 PRD、Figma 设计转码、前后端实现、CloudBase/Supabase 部署与代码审查的全流程实战指南。"
tags: [codebuddy, ide, example, workflow, prd, figma, cloudbase, supabase, deployment]
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

# IDE 产设研工作流

本示例演示如何使用 CodeBuddy IDE 完成一次从自然语言需求到上线部署的完整产设研工作流。CodeBuddy IDE 定位为"全球首款 AI 驱动的集成产品、设计与开发全栈高级工程师"（F-001），以自然语言驱动全流程开发（F-003）。

## 工作流总览

```
自然语言需求 → PRD → 设计原型 → Figma转码 → 前后端代码 → 沙箱部署 → 公开链接
                                                          ↓
                                                    代码审查/单测
```

对应 IDE 文档定义的四个阶段（F-010 ~ F-013）：

1. **产品阶段**：需求分析与 PRD 生成
2. **设计阶段**：原型设计与草图转高保真
3. **研发阶段**：Figma 转码、智能补全、单测生成、代码审查
4. **部署阶段**：沙箱部署与公开链接发布

## 1. 产品阶段：从需求到 PRD

在 CodeBuddy IDE 中，用自然语言描述产品想法：

```
帮我设计一个团队任务管理工具，支持看板视图、任务分配、截止日期提醒
```

IDE 进入产品阶段（F-010），自动完成：

- **需求分析**：拆解核心功能点
- **PRD 生成**：输出产品需求文档

生成的 PRD 包含功能列表、用户故事、数据模型等，可作为后续设计与开发的依据。

## 2. 设计阶段：原型与组件库

### 生成设计原型

基于 PRD，IDE 进入设计阶段（F-011）：

- 生成产品原型
- 支持草图转高保真设计

### 使用预置组件库

IDE 预置组件库（F-006, F-016），支持三大组件体系：

| 组件库 | 适用场景 |
|--------|----------|
| TDesign | 腾讯设计体系，适合企业级应用 |
| MUI | Material Design，适合通用 Web 应用 |
| Shadcn | 现代可定制组件，适合精品项目 |

可通过自然语言直接修改组件（F-006）：

```
把看板卡片改成圆角阴影样式，状态标签用绿色表示已完成
```

### Figma 设计稿转代码

如果设计师已在 Figma 中完成设计，IDE 支持 Figma 设计稿一键转代码（F-005, F-012）：

1. 在 IDE 中关联 Figma 设计稿
2. 触发转码
3. 生成对应前端代码（含组件与样式）

## 3. 研发阶段：编码与质量保障

### 智能补全与前后端代码

IDE 根据设计稿与 PRD 生成前后端代码（F-003），并提供智能代码补全（F-012）。后端可集成（F-004, F-014）：

- **腾讯 CloudBase**（BaaS）
- **Supabase**

二者均支持一键部署后端，无需手动搭建服务器。

### 单元测试生成

IDE 可自动生成单元测试（F-012），为代码提供质量保障。

### 代码审查

IDE 支持代码审查，通过 `@workspace#Codebase` 引用整个代码库进行上下文感知的审查（F-012）：

```
@workspace#Codebase 审查看板模块的代码，检查状态管理是否有竞态问题
```

审查覆盖逻辑正确性、潜在 Bug、最佳实践等。

### 高级功能辅助

研发阶段可使用 IDE 的高级功能（F-018）：

- **Plan 模式**：先规划再执行，适合复杂重构
- **Subagents**：委派子任务给独立 Agent
- **MCP**：接入外部工具与数据源
- **检查点**：在关键节点创建检查点，支持回滚
- **智能提交**：AI 辅助生成规范的提交信息

## 4. 部署阶段：从沙箱到公开链接

### 沙箱部署

开发完成后，IDE 支持沙箱部署（F-013），在隔离环境中验证应用运行情况。

部署生态集成（F-015）：

| 平台 | 用途 |
|------|------|
| CloudStudio | 云端开发环境与部署 |
| EdgeOne Pages | 静态站点与前端应用发布 |

后端通过 CloudBase 或 Supabase 一键部署（F-004）。

### 公开链接发布

验证通过后，发布为公开链接（F-013），应用正式上线。

## 5. 平台与环境

### 桌面平台支持

CodeBuddy IDE 支持以下平台（F-007）：

| 平台 | 版本要求 |
|------|----------|
| macOS | 11.0+（Apple Silicon / Intel） |
| Windows | 10+ x64 |
| Linux | .deb（ARM64 / x86_64） |

### 远程开发

IDE 基于 VSCode 架构（F-008），支持：

- **插件市场**：安装 VSCode 生态扩展
- **远程 SSH 开发**：连接远端服务器进行开发

## 6. 多模型支持

IDE 内置多模型支持（F-017）：

- **混元**：腾讯自研大模型
- **DeepSeek**：深度求索模型

可通过模型配置（F-018）在不同模型间切换，根据任务需求选择合适的模型。

## 7. 完整流程回顾

以团队任务管理工具为例，完整流程如下：

| 步骤 | 阶段 | 输入 | 产出 |
|------|------|------|------|
| 1 | 产品 | 自然语言需求 | PRD 文档 |
| 2 | 设计 | PRD / Figma 稿 | 高保真原型 / 转码代码 |
| 3 | 研发 | 设计稿 + PRD | 前后端代码 + 单测 |
| 4 | 审查 | 代码 | 审查报告与修复 |
| 5 | 部署 | 完成代码 | 沙箱预览 |
| 6 | 发布 | 沙箱验证 | 公开链接 |

整个流程在同一个 IDE 中完成，无需在 PRD 工具、设计工具、编辑器、部署平台之间反复切换（F-002, F-003）。

## 与插件/CLI 形态的协同

CodeBuddy 提供三种形态（F-009）：

- **IDE**：本示例使用的形态，产设研一体体验最完整
- **插件**：团队成员可在 VS Code/JetBrains/Xcode 等宿主中使用同一套 AI 能力（F-019 ~ F-024）
- **CLI**：可用于服务器端构建、CI 环境中的自动化任务（F-026）

三种形态共享 Plan 模式、Subagents、Skills、Hooks、MCP、记忆等高级功能（F-018），项目上下文通过 CodeBuddy.md 等机制共享。

## 相关概念

- [CodeBuddy IDE](/concepts/01-ide.md) — IDE 能力与架构详解
- [产品矩阵总览](/concepts/00-product-matrix.md) — 三态一体与生态产品
- [CLI](/concepts/02-cli.md) — 终端形态与跨形态能力共享
- [NPC 云端 AI 员工](/concepts/03-npc.md) — 从需求到 PR 的云端自主交付
- [Security 安全审计](/concepts/05-security.md) — 代码审查后的深度安全审计
- [CLI 快速入门](/examples/quick-start-cli.md) — 终端工具使用实战
