---
type: Concept
title: Jupyter AI 简介
description: Jupyter AI 是什么、核心能力、设计理念与支持的 AI Agent 一览
tags: [introduction, overview, jupyter-ai, agents, features]
sources:
  - id: readme
    resource: external/libs/jupyter/jupyter-ai/README.md
    title: README.md
  - id: docs-index
    resource: external/libs/jupyter/jupyter-ai/docs/source/index.md
    title: docs/source/index.md
  - id: agents-md
    resource: external/libs/jupyter/jupyter-ai/AGENTS.md
    title: AGENTS.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# Jupyter AI 简介

Jupyter AI 是一个将 AI Agent 连接到 JupyterLab 计算笔记本的开源扩展。它在 JupyterLab 中提供原生聊天界面，让你可以与前沿 AI Agent 协作，包括 Claude、Codex、GitHub Copilot、Goose、Kiro、Mistral Vibe、OpenCode 等。

## 核心定位

Jupyter AI 的核心价值在于**把 AI Agent 深度集成到 Notebook 工作流中**，而非简单的聊天窗口：

- **读写文件**：Agent 可以读取和修改工作区中的文件
- **运行终端命令**：Agent 可以执行 shell 命令（需用户审批）
- **操作 Notebook**：Agent 可以创建、读取、编辑、运行 Notebook 单元格
- **实时协作**：基于 Yjs CRDT，多用户可共享同一个聊天会话
- **开放协议**：基于 ACP 和 MCP 开放标准，避免厂商锁定

## 核心特性

| 特性 | 说明 |
|---|---|
| 💬 协作聊天 | 与 AI Persona 和其他用户在共享聊天中协作，拖拽附件共享上下文 |
| 🤖 前沿 Agent | 直接使用 Claude、Codex、Copilot、Goose、Kiro、Mistral Vibe 等 |
| ⚡ 实时 UI | 基于新的 RTC 后端，实时查看其他用户或 Agent 编辑文件 |
| 🛡️ 默认护栏 | Agent 在写入文件、运行命令或使用 MCP 工具前请求权限 |
| 📓 Notebook 工具 | AI Persona 可写入、调试和运行 Notebook |
| 🧩 灵活可扩展 | 构建自定义 AI Persona 或共享自定义 MCP 服务器 |

## 支持的 AI Agent

Jupyter AI 默认不内置任何 Agent，需要单独安装。以下是官方支持的 Agent 列表：

| Agent | 安装 | ACP 适配器 |
|---|---|---|
| Claude Code | 官方 CLI 安装 | `npm install -g @agentclientprotocol/claude-agent-acp` |
| Codex CLI | 官方 CLI 安装 | `npm install -g @zed-industries/codex-acp` |
| GitHub Copilot CLI | 官方 CLI 安装 | 内置支持 |
| Goose | 官方 CLI 安装 | 内置支持 |
| Kilo CLI | 官方 CLI 安装 | 内置支持 |
| Kiro CLI | 官方 CLI 安装 | 内置支持 |
| Mistral Vibe | `pip install mistral-vibe` 或 `uv tool install mistral-vibe` | 内置支持 |
| OpenCode | 官方 CLI 安装 | 内置支持 |
| Jupyternaut | `pip install 'jupyter-ai[jupyternaut]'` | 内置（直接模型调用） |

Jupyter AI 会**自动检测**环境中可用的 Agent，无需手动配置。

## 版本信息

- **当前版本**：3.1.3
- **Python 要求**：>=3.9
- **许可证**：BSD-3-Clause
- **仓库**：https://github.com/jupyterlab/jupyter-ai
- **文档**：https://jupyter-ai.readthedocs.io/

## v3 架构变革

Jupyter AI v3 进行了重大架构重构：[^agents-md]

- **从单体仓库（monorepo）变为元包（metapackage）**：v3 不再是单体仓库，而是由多个独立子包（通过 `submodules/manifest.json` 注册的 12 个 jupyter-ai-contrib 子包 + jupyterlab_chat 核心依赖）组合而成，每个子包位于独立仓库
- **元包本身几乎为空**：`jupyter-ai` 包只包含版本号、默认 MCP 工具注册、文档聚合基础设施
- **子包独立发版**：每个子包遵循 SemVer，元包通过版本上限（ceiling pin）控制兼容性
- **文档聚合**：用户文档存放在主仓库，贡献者/开发者文档存放在各子包仓库，通过 Sphinx 扩展自动聚合

## 设计原则

Jupyter AI 遵循以下设计原则：[^contributors]

1. **厂商中立**：不歧视任何 Agent 或模型提供商
2. **仅响应显式提示**：不监听文件、不自动发送提示，所有非确定性操作必须用户主动选择
3. **提示透明**：聊天界面和 Magic 命令使用的系统提示开源可见
4. **可追溯**：生成的 Notebook 和 Magic 输出均标注由 Jupyter AI 生成
5. **以人为中心**：聊天界面符合通用聊天应用习惯，设置界面最小化且易懂

## 相关概念

- [安装与配置](/concepts/01-installation-and-setup.md)
- [聊天界面](/concepts/02-chat-interface.md)
- [元包架构](/concepts/03-metapackage-architecture.md)
- [ACP 与 MCP 双协议](/concepts/04-protocols-acp-mcp.md)
