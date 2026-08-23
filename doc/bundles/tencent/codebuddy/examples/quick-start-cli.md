---
type: Example
title: "CLI 快速入门"
description: "从零开始使用 CodeBuddy CLI：环境准备、全局安装、/init 初始化项目手册、/doctor 诊断、常用命令与 MCP/Sub-agents 配置实战。"
tags: [codebuddy, cli, example, quick-start, installation, init, doctor, mcp, subagents]
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

# CLI 快速入门

本示例演示如何从零开始安装、配置并使用 CodeBuddy CLI，覆盖环境准备、项目初始化、故障诊断与核心功能使用。

## 1. 环境准备

CodeBuddy CLI 要求以下环境（F-027）：

- **Node.js** 22 或更高版本
- **Git**

检查当前版本：

```bash
node --version
git --version
```

若 Node.js 版本低于 22，请先升级。可通过 nvm（Node Version Manager）管理多版本：

```bash
nvm install 22
nvm use 22
```

> 注：IDE 文档页标注 Node.js 18.0+ 即可（F-025），但 CLI 官网明确要求 22+（F-027），使用 CLI 时以 22+ 为准。

## 2. 全局安装

通过 npm 全局安装 CodeBuddy CLI（F-025, F-027）：

```bash
npm install -g @tencent-ai/codebuddy-code
```

安装完成后验证：

```bash
codebuddy --version
```

CLI 支持 macOS、Linux、Windows 三大平台，覆盖 50+ 编程语言（F-036）。

## 3. 健康检查

首次使用前，运行 `/doctor` 命令进行环境与配置故障排查（F-037）：

```bash
codebuddy
```

进入 CLI 交互界面后输入：

```
/doctor
```

`/doctor` 会检查以下内容：

- Node.js 与 Git 版本是否满足要求
- 配置文件完整性
- 网络连通性
- 认证状态

根据诊断结果修复问题后再继续。

## 4. 初始化项目手册

进入项目目录，使用 `/init` 命令生成 CODEBUDDY.md 项目手册（F-030）：

```bash
cd your-project
codebuddy
```

在交互界面中输入：

```
/init
```

CLI 会分析项目结构并生成 `CODEBUDDY.md` 文件。该文件是项目级长期记忆的载体（F-033），记录项目结构、技术栈、编码规范等信息，使 AI 在后续会话中能快速理解项目上下文。

### CODEBUDDY.md 分层记忆

CLI 的长期记忆分三层（F-033）：

| 层级 | 位置/范围 | 用途 |
|------|-----------|------|
| 项目级 | 当前项目的 CODEBUDDY.md | 项目特定约定 |
| 用户级 | 当前用户全局 | 个人偏好 |
| 企业级 | 企业统一下发 | 安全与合规底线 |

`/init` 生成的是项目级手册，三层叠加生效。

## 5. 开始编码

初始化完成后，直接在 CLI 中用自然语言描述任务：

```
> 分析 src/ 目录下的代码结构，找出可以重构的重复逻辑
```

CLI 具备全仓百万级代码感知能力（F-026），会进行全代码库分析与语义搜索（F-029），而非仅查看单个文件。

### 粘贴截图

CLI 支持图片与截图输入（F-031）。在交互界面中直接按 Ctrl+V 粘贴剪贴板中的截图，可用于：

- UI 设计稿还原
- 错误截图分析
- 架构图解读

## 6. 使用 Sub-agents

对于复杂任务，可使用 Sub-agents 进行任务委派（F-034）。每个子 Agent 具备：

- 独立上下文窗口（避免主对话上下文膨胀）
- 专属提示词（针对子任务定制）
- 独立工具权限（最小权限原则）

在对话中描述需要委派的任务，CLI 会自动调度子 Agent：

```
> 请分别审查 auth/ 和 payment/ 两个模块的安全性，给出独立报告
```

此任务可并行委派给两个专注于不同模块的子 Agent（F-044 描述了并行能力，本地 CLI 的 Sub-agents 是其本地形态）。

## 7. 配置 MCP

CLI 同时具备 MCP 客户端与服务器能力（F-032）。

### 作为 MCP 客户端

在配置中添加 MCP 服务器连接，即可使用外部工具。MCP 配置使 CLI 能访问数据库、API、文件系统等外部资源。

### 作为 MCP 服务器

CLI 也可启动为 MCP 服务器，向其他 Agent 或工具暴露自身的代码分析与编辑能力：

```bash
codebuddy mcp-server
```

（此命令形式参考 CodeBuddy 生态的 MCP 服务器能力，F-032。）

## 8. 自定义配置

CLI 支持分层配置与 CLI 参数两种自定义方式（F-035）：

- **分层配置**：项目级、用户级、企业级配置叠加
- **CLI 参数**：启动时通过命令行参数临时覆盖默认行为

## 9. 常用命令速查

| 命令/操作 | 说明 | 事实 ID |
|-----------|------|---------|
| `npm install -g @tencent-ai/codebuddy-code` | 全局安装 | F-027 |
| `/init` | 生成 CODEBUDDY.md 项目手册 | F-030 |
| `/doctor` | 环境与配置故障排查 | F-037 |
| `Ctrl+V` | 粘贴图片/截图 | F-031 |
| 自然语言对话 | 全代码库分析与语义搜索 | F-029 |

## 10. 计费说明

CLI 按 Token 消耗计费（F-038）。全代码库分析、多 Sub-agents 并行等操作会消耗更多 Token，建议在复杂任务前评估成本。

## 下一步

- 阅读 [CLI 概念文档](/concepts/02-cli.md) 深入了解分层记忆与 Sub-agents 架构
- 阅读 [IDE 工作流示例](/examples/ide-workflow.md) 了解产设研一体的完整流程
- 阅读 [NPC 概念](/concepts/03-npc.md) 了解云端自主 Agent 如何基于同样的核心能力交付完整 PR

## 相关概念

- [CLI](/concepts/02-cli.md) — CLI 架构与分层记忆详解
- [CodeBuddy IDE](/concepts/01-ide.md) — 与 CLI 共享高级能力的桌面端
- [产品矩阵总览](/concepts/00-product-matrix.md) — CLI 在三态一体中的定位
- [NPC 云端 AI 员工](/concepts/03-npc.md) — 本地 Sub-agents 的云端延伸
- [IDE 工作流示例](/examples/ide-workflow.md) — 产设研一体工作流实战
