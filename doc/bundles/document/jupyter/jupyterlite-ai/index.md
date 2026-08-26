---
type: OKF
title: "JupyterLite AI 教程"
description: "JupyterLite AI (jupyterlite-ai) 是 JupyterLab/Notebook/JupyterLite 的浏览器端 AI 扩展，基于 Vercel AI SDK 实现，支持多提供商、工具调用、MCP 协议和自定义 Persona。"
tags: [jupyterlite-ai, jupyter, ai, jupyterlab, llm, agent, mcp, notebook]
okf_version: "0.2"
version: "0.19.0"
source: https://github.com/jupyterlite/ai
source_version: "0.19.0"
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-04-21T00:00:00+08:00" }
status: stable
stale_after: 2026-10-21
---

# JupyterLite AI

> JupyterLab / Notebook 7 / JupyterLite 的 AI 编程助手扩展

JupyterLite AI 是一个浏览器端的 AI 扩展，将大语言模型深度集成到 Jupyter 生态中。它支持多家 AI 提供商，内置工具调用能力，允许 AI 操作 Notebook、执行命令、获取网页内容，并通过 MCP 协议扩展自定义工具。

![JupyterLite AI Architecture](https://raw.githubusercontent.com/jupyterlite/ai/main/docs/source/_static/architecture.svg)

## ✨ 核心特性

- 🔌 **多提供商支持** — OpenAI、Anthropic、Google、Mistral 及任意 OpenAI 兼容服务（Ollama、vLLM 等）
- 🛠️ **工具调用** — AI 可执行 JupyterLab 命令、操作 Notebook、获取网页内容、搜索网络
- 🤖 **Agent 引擎** — 基于 Vercel AI SDK `ToolLoopAgent` 的多轮工具调用循环
- 🔐 **安全密钥管理** — API Key 通过 `jupyter-secrets-manager` 安全存储
- 🧩 **MCP 协议** — 支持 Model Context Protocol，接入外部工具服务器
- 🎭 **Persona 系统** — 自定义 AI 人设、系统提示词和行为模式
- 🌐 **JupyterLite 兼容** — 纯浏览器环境运行，无需 Python 后端服务器
- ⚡ **流式输出** — AI 回复实时流式显示
- 🔧 **可扩展架构** — 通过 Lumino Token DI 系统支持自定义工具和提供商

## 📦 包结构

JupyterLite AI 是一个 TypeScript monorepo，包含三个核心包：

| 包 | npm 包名 | 职责 |
|---|---------|------|
| Agent 核心 | `@jupyternaut/agent` | AI Agent 引擎、工具/提供商/技能注册表、MCP 管理 |
| Persona 编排 | `@jupyternaut/persona` | AI 人设系统、角色定义、技能加载 |
| JupyterLab 扩展 | `@jupyterlite/ai` | JupyterLab 集成、聊天 UI、设置面板、Notebook 工具 |

Python 包通过 `hatch-jupyter-builder` 构建，将前端扩展打包为可 pip 安装的 Jupyter 扩展。

## 📚 文档导航

### 入门指南

| 文档 | 说明 |
|------|------|
| [快速开始：安装与首次对话](/examples/01-quick-start.md) | 安装、配置、第一次 AI 对话 |
| [配置 AI 模型提供商](/examples/02-configure-provider.md) | 配置 OpenAI/Anthropic/Google/本地模型 |

### 核心概念

按顺序阅读以深入理解架构：

| 序号 | 概念文档 | 说明 |
|------|---------|------|
| 0 | [介绍与定位](/concepts/00-introduction.md) | 项目是什么、解决什么问题 |
| 1 | [架构总览](/concepts/01-architecture-overview.md) | 三层架构、核心数据流、模块关系 |
| 2 | [Token 与 DI 系统](/concepts/02-token-di-system.md) | Lumino Token 依赖注入机制 |
| 3 | [Provider 模型提供商系统](/concepts/03-provider-system.md) | 多 LLM 提供商注册与切换机制 |
| 4 | [Tool 工具系统](/concepts/04-tool-system.md) | 工具注册、发现、调用与审批 |
| 5 | [Agent 引擎](/concepts/05-agent-engine.md) | ToolLoop 循环、消息处理、流式响应 |
| 6 | [Skill 技能系统](/concepts/06-skill-system.md) | 技能加载、管理与 Persona 关联 |
| 7 | [设置与配置系统](/concepts/07-settings-and-config.md) | 配置 schema、密钥存储、设置 UI |
| 8 | [MCP 集成](/concepts/08-mcp-integration.md) | Model Context Protocol 服务器管理 |
| 9 | [Chat UI 交互](/concepts/09-chat-ui.md) | 聊天面板、消息渲染、用户交互 |
| 10 | [代码补全系统](/concepts/10-code-completion.md) | AI 行内补全、FIM 模式、Notebook 上下文感知 |

### 实践示例

| 示例 | 难度 | 说明 |
|------|------|------|
| [AI 对话技巧](/examples/03-chat-with-ai.md) | ⭐ | 提示词技巧、多轮对话策略 |
| [使用内置工具](/examples/04-use-builtin-tools.md) | ⭐⭐ | 命令执行、浏览器获取、Web搜索 |
| [AI 操作 Notebook](/examples/05-notebook-operations.md) | ⭐⭐ | 代码生成、单元格操作、数据分析 |
| [配置自定义 MCP 服务器](/examples/06-custom-mcp-servers.md) | ⭐⭐⭐ | 接入外部工具和数据源 |
| [自定义 AI 人设](/examples/07-custom-persona.md) | ⭐⭐⭐ | Persona 定义、系统提示词编写 |
| [JupyterLite 部署配置](/examples/08-jupyterlite-deployment.md) | ⭐⭐⭐ | 纯浏览器环境部署 |
| [开发自定义工具](/examples/09-develop-custom-tool.md) | ⭐⭐⭐⭐ | 扩展 AI 工具能力 |
| [开发自定义提供商](/examples/10-develop-custom-provider.md) | ⭐⭐⭐⭐ | 接入新的 LLM 服务 |

### API 参考

| 参考文档 | 说明 |
|---------|------|
| [源码结构索引](/references/source-code.md) | 目录树与核心文件说明 |
| [Token 与接口 API](/references/tokens-api.md) | 核心 Token、接口定义与契约 |
| [内置工具参考](/references/built-in-tools.md) | 所有内置工具的参数与用法 |
| [内置提供商参考](/references/built-in-providers.md) | 内置 LLM 提供商的配置与能力 |
| [插件架构参考](/references/plugin-architecture.md) | JupyterLab 插件系统与扩展点 |

## 🚀 快速安装

```bash
# pip 安装
pip install jupyterlite-ai

# 或 conda
conda install -c conda-forge jupyterlite-ai

# 启动 JupyterLab
jupyter lab
```

启动后，在左侧边栏点击 AI Chat 图标即可开始使用。

## 🔧 技术栈

- **前端框架**：JupyterLab 4.x / Lumino
- **AI SDK**：Vercel AI SDK (`ai` 包)
- **语言**：TypeScript
- **构建工具**：Webpack / Jupyter Builder
- **Python 构建**：Hatchling + hatch-jupyter-builder
- **密钥管理**：jupyter-secrets-manager
- **Schema 校验**：Zod
- **Monorepo 管理**：npm workspaces

## 🔗 相关链接

- [GitHub 仓库](https://github.com/jupyterlite/ai)
- [官方文档](https://jupyterlite-ai.readthedocs.io/)
- [JupyterLite 官网](https://jupyterlite.readthedocs.io/)
- [Vercel AI SDK 文档](https://sdk.vercel.ai/docs)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## 📄 许可证

BSD 3-Clause License

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
