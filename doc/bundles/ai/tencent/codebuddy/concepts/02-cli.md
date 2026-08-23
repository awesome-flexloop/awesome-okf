---
type: Concept
title: "CodeBuddy CLI"
description: "CodeBuddy CLI 是终端原生 AI 编程工具，具备全仓百万级代码感知、MCP 双端、分层长期记忆与 Sub-agents，支持 50+ 编程语言与三大桌面平台。"
tags: [codebuddy, cli, terminal, mcp, subagents, memory, code-intelligence]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-02-23
sources:
  - id: cli-official
    resource: /references/cli.md
    title: CodeBuddy CLI 产品官网
  - id: docs-intro
    resource: /references/docs-intro.md
    title: CodeBuddy IDE 文档介绍
---

# CodeBuddy CLI

CodeBuddy CLI（又称 CodeBuddy Code）是 CodeBuddy 产品矩阵中的终端原生 AI 编程工具，定位为具备全仓百万级代码感知能力的命令行助手（F-026）。它面向偏好终端工作流、需要在服务器或 CI 环境中使用 AI 编程能力的开发者，同时提供企业级可定制架构。

## 安装与环境要求

通过 npm 全局安装（F-027）：

```bash
npm install -g @tencent-ai/codebuddy-code
```

环境要求：

- Node.js 22+
- Git

CLI 跨平台支持 macOS、Linux、Windows（F-036），覆盖 50+ 编程语言（F-036）。

> 注：IDE 文档页标注的 Node.js 要求为 18.0+（F-025），CLI 官网要求为 22+（F-027），使用 CLI 时应以 22+ 为准。

## 核心能力

### 全仓代码感知

CLI 具备全仓百万级代码感知能力（F-026），提供高级代码智能（F-029）：

- 全代码库分析
- 语义搜索

这使得 CLI 能够理解整个项目的结构与上下文，而非仅当前打开的文件，适合在大型代码库中进行跨文件重构与问题定位。

### 终端深度编码

CLI 支持终端深度编码（F-028），可直接在命令行中完成代码编写、修改与执行。

### 多模态输入

支持图片与截图输入，通过 Ctrl+V 粘贴图片（F-031），可用于 UI 还原、错误截图分析等场景。

## 项目手册：CODEBUDDY.md

CLI 提供 `/init` 命令，用于生成 CODEBUDDY.md 项目手册（F-030）。该文件是项目上下文的载体，记录项目结构、约定与规则，供 AI 在后续会话中理解项目。

CODEBUDDY.md 同时是分层长期记忆的基础（见下文）。

## 分层长期记忆

CLI 的长期记忆基于 CodeBuddy.md 分三层继承（F-033）：

| 层级 | 作用范围 | 典型用途 |
|------|----------|----------|
| 项目级 | 当前项目 | 项目结构、编码规范、技术栈 |
| 用户级 | 当前用户所有项目 | 个人编码偏好、常用工具 |
| 企业级 | 企业内所有项目 | 安全规范、合规要求、统一标准 |

这种分层模型使企业能在企业级统一下发规则底线，项目级在此基础上补充特定约定，用户级保存个人偏好，三层叠加生效。

## Sub-agents

CLI 支持 Sub-agents（子 Agent），每个子 Agent 具备（F-034）：

- **独立上下文**：不与父 Agent 共享上下文窗口，避免上下文膨胀
- **专属提示词**：针对特定任务定制 system prompt
- **独立工具权限**：按最小权限原则配置可访问工具

Sub-agents 适合将复杂任务拆解为并行子任务，每个子 Agent 专注单一职责，提升复杂任务的完成质量。

## MCP 双端能力

CLI 同时具备 MCP（Model Context Protocol）客户端与服务器能力（F-032）：

- **作为客户端**：连接外部 MCP 服务器，获取额外工具与资源
- **作为服务器**：向其他 Agent 或工具暴露 CLI 自身的能力

这使 CLI 既能消费外部工具生态，也能作为工具被集成到更大的 Agent 工作流中。

## 高度自定义

CLI 支持两方面自定义（F-035）：

- **分层配置**：与记忆层级对应的配置体系
- **CLI 参数**：通过命令行参数覆盖默认行为

## 故障排查

`/doctor` 命令用于环境与配置故障排查（F-037），可检查 Node.js 版本、Git 可用性、配置完整性等。

## 计费

CLI 按 Token 消耗计费（F-038）。

## 与 IDE 形态的关系

CLI 与 IDE、插件共享同一套高级 AI 功能（F-018），包括 Plan 模式、Subagents、Skills、Hooks、MCP、模型配置、检查点、记忆、规则、智能提交。区别在于交互载体：

- IDE 提供完整图形界面与产设研一体链路
- CLI 提供纯终端交互，适合自动化与服务器环境
- 三者通过 CodeBuddy.md 等机制共享项目上下文

## 相关概念

- [产品矩阵总览](/concepts/00-product-matrix.md) — CLI 在三态一体中的定位
- [CodeBuddy IDE](/concepts/01-ide.md) — 与 CLI 共享高级能力的桌面端
- [NPC 云端 AI 员工](/concepts/03-npc.md) — 云端 Agent 与本地 CLI Sub-agents 的对比
- [CLI 快速入门](/examples/quick-start-cli.md) — 安装、初始化与常用命令实战
- [IDE 工作流示例](/examples/ide-workflow.md) — 跨形态协同的工作流
