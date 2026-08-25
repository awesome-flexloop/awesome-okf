---
title: Deep Agents
type: index
bundle: deepagents
description: |
  Deep Agents 是一个开源的、有主见的 Agent 框架，基于 LangChain 和 LangGraph 构建，
  提供开箱即用的长周期多步骤 Agent 能力，包括子 Agent、文件系统、上下文管理、Shell 访问、
  持久化记忆、人在回路、技能和 MCP 工具支持。本知识包涵盖其 monorepo 架构、核心 SDK、
  终端编码 Agent（dcode）、部署 CLI、ACP 协议集成、评估套件和 Talon 运行时宿主。
sources:
  - https://github.com/datawhalechina/deepagents
concepts:
  - name: monorepo架构
    path: /datawhale/deepagents/concepts/monorepo-architecture
    description: 独立版本化的多包 monorepo 结构、uv 依赖管理、Make 任务体系与跨包 fan-out 机制
  - name: 核心SDK与三层架构
    path: /datawhale/deepagents/concepts/core-sdk
    description: create_deep_agent 组装点、中间件栈、后端系统、配置文件与 LangChain/LangGraph 三层栈
  - name: ACP协议集成
    path: /datawhale/deepagents/concepts/acp-protocol
    description: Agent Client Protocol 适配器，将 Deep Agent 嵌入 Zed 等编辑器，支持会话持久化和动态模型切换
  - name: CLI部署工具
    path: /datawhale/deepagents/concepts/cli-toolchain
    description: deepagents-cli 部署工具链，包含 init/deploy/agents/mcp-servers 子命令与项目脚手架
  - name: Code终端编码Agent
    path: /datawhale/deepagents/concepts/code-module
    description: dcode 终端编码 Agent，Textual TUI、客户端/服务器架构、技能系统、沙箱与审批机制
  - name: Evals评估套件
    path: /datawhale/deepagents/concepts/evals-suite
    description: deepagents-evals 端到端行为评估，Harbor 沙箱基准、试验聚合、雷达图与 CI 集成
  - name: Talon运行时宿主
    path: /datawhale/deepagents/concepts/talon-runtime
    description: 实验性本地长运行 Agent 宿主，通道适配器（WhatsApp/Telegram）、cron 调度器与 MCP 工具加载
references:
  - name: 根 AGENTS.md
    path: /datawhale/deepagents/references/root-agents
    description: 仓库全局开发规范、PR 约定、搜索路由与 OpenWiki 说明
  - name: 根 README.md
    path: /datawhale/deepagents/references/root-readme
    description: 项目概览、核心特性、快速开始与 FAQ
  - name: libs/README.md
    path: /datawhale/deepagents/references/libs-readme
    description: Monorepo 包清单与各包 PyPI 信息
  - name: libs/ARCHITECTURE.md
    path: /datawhale/deepagents/references/libs-architecture
    description: 三层架构、构造与执行流程、中间件栈、工具表面与状态持久化
  - name: libs/DEVELOPMENT.md
    path: /datawhale/deepagents/references/libs-development
    description: 仓库布局、环境设置、命令参考、测试规范与基准测试
  - name: libs/acp/README.md
    path: /datawhale/deepagents/references/acp-readme
    description: ACP 集成指南、Zed 配置、自定义 Agent 与模型切换
  - name: libs/cli/README.md
    path: /datawhale/deepagents/references/cli-readme
    description: 部署 CLI 安装与使用、项目布局、MCP 服务器管理
  - name: libs/code/README.md
    path: /datawhale/deepagents/references/code-readme
    description: dcode 快速安装、功能特性与安全模型
  - name: libs/code/AGENTS.md
    path: /datawhale/deepagents/references/code-agents
    description: Code 包开发规范，Textual TUI 工程、斜杠命令、模型提供商配置
  - name: libs/code/ARCHITECTURE.md
    path: /datawhale/deepagents/references/code-architecture
    description: Code 包客户端/服务器架构、请求流程与设计权衡
  - name: libs/evals/README.md
    path: /datawhale/deepagents/references/evals-readme
    description: 评估套件概览、结果链接与贡献指南
  - name: libs/evals/AGENTS.md
    path: /datawhale/deepagents/references/evals-agents
    description: 评估 CLI 参考、子命令、退出码、试验摘要 schema 与 Harbor 集成
  - name: libs/talon/README.md
    path: /datawhale/deepagents/references/talon-readme
    description: Talon 运行时宿主快速开始、通道配置、MCP 工具与安全说明
examples:
  - name: 创建并调用 Deep Agent
    path: /datawhale/deepagents/examples/create-deep-agent
    description: 使用 create_deep_agent 构建带自定义工具的 Agent 并调用
  - name: ACP 自定义 Agent 服务器
    path: /datawhale/deepagents/examples/acp-custom-agent
    description: 通过 AgentServerACP 将自定义 Deep Agent 暴露为 ACP 服务器
  - name: dcode 一键安装与启动
    path: /datawhale/deepagents/examples/dcode-quickstart
    description: 通过 curl 安装 dcode 并启动终端编码 Agent
  - name: CLI 部署 Agent 项目
    path: /datawhale/deepagents/examples/cli-deploy-agent
    description: 使用 deepagents-cli 脚手架、注册 MCP 服务器并部署托管 Agent
  - name: 运行评估试验
    path: /datawhale/deepagents/examples/run-evals
    description: 使用 deepagents-evals 运行单次和多次试验评估
  - name: Talon 启动 Telegram Agent
    path: /datawhale/deepagents/examples/talon-telegram
    description: 配置并启动 Talon Telegram 通道 Agent
---

# Deep Agents 知识包

Deep Agents 是一个开源的 Agent 框架（agent harness），构建在 LangChain 和 LangGraph 之上，为长周期、多步骤的 Agent 工作提供开箱即用的默认配置。本知识包系统梳理了 Deep Agents 项目的 monorepo 架构、核心 SDK 设计、各功能模块职责及其相互关系。

## 快速导航

- **架构入门**：阅读[三层架构](/ai/datawhale/deepagents/concepts/core-sdk)理解 Deep Agents、LangChain、LangGraph 的分层关系。
- **包结构**：阅读[monorepo架构](/ai/datawhale/deepagents/concepts/monorepo-architecture)了解七个独立版本化包的职责边界。
- **终端产品**：阅读[Code终端编码Agent](/ai/datawhale/deepagents/concepts/code-module)了解 `dcode` 的客户端/服务器设计。
- **评估体系**：阅读[Evals评估套件](/ai/datawhale/deepagents/concepts/evals-suite)了解真实 LLM 评估与 Harbor 集成。

## 项目概要

| 维度 | 说明 |
|------|------|
| 仓库 | https://github.com/datawhalechina/deepagents |
| 语言 | Python（另有 JS/TS 版本 deepagents.js） |
| 包管理 | uv（禁止 pip/poetry/conda） |
| 任务运行 | Make（每包独立 Makefile） |
| 许可证 | MIT |
| 核心包数 | 7 个 libs 包 + 5 个 partner 子包 |
| 核心 SDK 版本 | 0.7.8 |
| dcode 版本 | 0.1.59 |

```{toctree}
:hidden:

concepts/acp-protocol
concepts/cli-toolchain
concepts/code-module
concepts/core-sdk
concepts/evals-suite
concepts/monorepo-architecture
concepts/talon-runtime
examples/acp-custom-agent
examples/cli-deploy-agent
examples/create-deep-agent
examples/dcode-quickstart
examples/run-evals
examples/talon-telegram
references/acp-readme
references/cli-readme
references/code-agents
references/code-architecture
references/code-readme
references/evals-agents
references/evals-readme
references/libs-architecture
references/libs-development
references/libs-readme
references/root-agents
references/root-readme
references/talon-readme
spec/facts
spec/insights
log
```
