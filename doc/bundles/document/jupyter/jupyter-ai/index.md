---
okf_version: "0.2"
type: Bundle
title: jupyter-ai OKF Wiki
description: Jupyter AI 开源 AI 助手扩展的完整知识文档，涵盖架构、协议、Persona 系统、MCP 工具、扩展开发和配置
sources:
  - { id: jupyter-ai-docs, resource: "https://jupyter-ai.readthedocs.io/en/stable/", title: "Jupyter AI 官方文档" }
  - { id: jupyter-ai-org, resource: "https://jupyter.org/ai", title: "Jupyter AI 官方主页" }
  - { id: jupyter-ai-github, resource: "https://github.com/jupyterlab/jupyter-ai", title: "Jupyter AI GitHub 仓库" }
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T12:00:00+08:00" }
updated: { by: "doc-update", at: "2026-08-22T12:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:30:00+08:00" }
status: active
stale_after: 2027-08-22
---

# jupyter-ai

Jupyter AI 是将 AI Agent 连接到 JupyterLab 计算笔记本的官方开源扩展，基于 ACP（Agent Client Protocol）和 MCP（Model Context Protocol）双开放协议，支持 Claude、Codex、GitHub Copilot、Goose、Kiro、Mistral Vibe、OpenCode、Jupyternaut 等多种 AI Agent。

**版本**：3.1.3  
**Python 要求**：>=3.9  
**许可证**：BSD-3-Clause  
**仓库**：https://github.com/jupyterlab/jupyter-ai  
**文档**：https://jupyter-ai.readthedocs.io/

## 核心特性

- **多 Agent 支持**：同时支持 Claude、Codex、Copilot、Goose、Kiro、Jupyternaut 等前沿 AI Agent
- **Notebook 深度集成**：AI 可读写、编辑、运行 Notebook 单元格，直接操作 JupyterLab
- **实时协作**：基于 Yjs CRDT，多用户共享聊天会话，实时查看 Agent 编辑
- **安全护栏**：Agent 写入文件、运行命令、使用工具前默认请求用户审批
- **开放协议**：基于 ACP 和 MCP 开放标准，避免厂商锁定
- **可扩展架构**：元包架构 + Entry Points 插件系统，支持自定义 Persona 和工具
- **双交互模式**：聊天面板（复杂多轮对话）+ Magic Commands（单元格内快速问答）

## 文档索引

### 概念文档（Concepts）

| 文档 | 说明 |
|---|---|
| [Jupyter AI 简介](concepts/00-introduction.md) | 核心能力、设计理念、支持的 Agent 一览、v3 架构变革 |
| [安装与配置](concepts/01-installation-and-setup.md) | 安装方式、Agent 安装、ACP 适配器、首次启动 |
| [聊天界面](concepts/02-chat-interface.md) | 聊天创建、Persona 选择、附件、代码工具栏、权限控制 |
| [元包架构](concepts/03-metapackage-architecture.md) | v3 元包设计、子包职责划分、版本管理、文档聚合 |
| [ACP 与 MCP 双协议](concepts/04-protocols-acp-mcp.md) | Agent Client Protocol 和 Model Context Protocol 的分工与协作 |
| [AI Persona 系统](concepts/05-ai-personas.md) | Persona 概念、内置 Persona、@提及规则、自定义开发 |
| [聊天文件与持久化](concepts/06-chat-files-and-persistence.md) | .chat 文件格式、Yjs CRDT 实时协作、对话记忆管理 |
| [MCP 工具与 Notebook 交互](concepts/07-mcp-tools-and-notebooks.md) | 16个内置 MCP 工具、Notebook 操作、权限护栏机制 |
| [自定义 MCP 服务器](concepts/08-custom-mcp-servers.md) | mcp_settings.json 配置、stdio/HTTP 服务器、第三方工具集成 |
| [Entry Points API](concepts/09-entry-points-api.md) | Persona/工具/命令注册机制、插件开发指南 |
| [Magic Commands](concepts/10-magic-commands.md) | %ai/%%ai 单元格魔法命令、变量引用、对话上下文管理 |
| [配置系统](concepts/11-configuration-system.md) | Traitlets 配置、命令行参数、API Key、模型提供商配置 |
| [版本与升级](concepts/12-versioning-and-upgrades.md) | SemVer、版本上限策略、升级注意事项、子包兼容性 |

### API 参考（References）

| 文档 | 说明 |
|---|---|
| [参考文档索引](references/index.md) | 所有参考文档入口 |
| [元包源码参考](references/metapackage-source.md) | 元包结构、pyproject.toml 解析、子包依赖关系 |
| [Persona API 参考](references/persona-api.md) | BasePersona、PersonaDefaults、响应方法 API |
| [MCP 配置与工具参考](references/mcp-config-reference.md) | mcp_settings.json 规范、16个内置工具清单 |
| [配置参考](references/config-reference.md) | AiExtension/AiMagics 配置项完整列表 |
| [Entry Points 参考](references/entry-points-reference.md) | 4个 entry point group 的完整注册规范 |

### 示例（Examples）

| 文档 | 说明 |
|---|---|
| [示例索引](examples/index.md) | 所有示例入口 |
| [首次聊天快速上手](examples/first-chat.md) | 安装配置、创建第一个聊天、数据分析全流程 |
| [Notebook AI 辅助工作流](examples/notebook-ai-assistant.md) | 数据加载→探索→清洗→可视化→调试→文档的完整 AI 辅助流程 |
| [Magic Commands 使用](examples/magic-commands-usage.md) | %ai/%%ai 命令的实用场景和技巧 |
| [配置自定义 MCP 服务器](examples/custom-mcp-server.md) | 文件系统、GitHub、数据库等 MCP 服务器配置 |
| [创建自定义 Persona](examples/custom-persona.md) | 从零开发自定义 AI Persona 并注册到 Jupyter AI |

## 快速开始

```bash
# 1. 安装 Jupyter AI 和 Jupyternaut
pip install 'jupyter-ai[jupyternaut]'

# 2. 设置 API Key
export OPENAI_API_KEY="sk-your-key"

# 3. 启动 JupyterLab
jupyter lab

# 4. 点击左侧聊天图标 → + New Chat → 选择 Jupyternaut → 开始对话
```

## 架构总览

```
┌─────────────────────────────────────────────────────────┐
│                    JupyterLab 前端                       │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ 聊天面板  │  │ Notebook 视图 │  │ 文件浏览器/启动器 │  │
│  └────┬─────┘  └──────┬───────┘  └────────┬──────────┘  │
├───────┼───────────────┼───────────────────┼─────────────┤
│       │        Python 后端               │             │
│  ┌────┴──────────────┴───────────────────┴──────────┐   │
│  │              jupyter-ai 元包（路由器）            │   │
│  │  ┌─────────────┐  ┌──────────────────────────┐   │   │
│  │  │ Router      │→│ Persona Manager          │   │   │
│  │  └──────┬──────┘  └─────┬────────┬───────────┘   │   │
│  │         │               │        │                │   │
│  │  ┌──────┴──────┐  ┌────┴───┐ ┌─┴────────────┐   │   │
│  │  │ ACP Client  │  │Jupyter-│ │ 自定义        │   │   │
│  │  │ (外部Agent) │  │naut    │ │ Persona      │   │   │
│  │  └──────┬──────┘  └────┬───┘ └──────────────┘   │   │
│  └─────────┼──────────────┼────────────────────────┘   │
│            │              │                            │
│  ┌─────────┴──────────────┴────────────────────────┐   │
│  │           MCP 工具层（jupyter_server_mcp）       │   │
│  │  ┌──────────┐ ┌──────────┐ ┌─────────────────┐  │   │
│  │  │ Notebook │ │ Jupyter- │ │ 自定义 MCP 服务器│  │   │
│  │  │ 工具(13) │ │ Lab工具  │ │ (mcp_settings)  │  │   │
│  │  └──────────┘ └──────────┘ └─────────────────┘  │   │
│  └─────────────────────────────────────────────────┘   │
│            │                                           │
│  ┌─────────┴────────────────────────────────────────┐  │
│  │         基础层（jupyterlab-chat + Yjs CRDT）      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

```{toctree}
:hidden:

examples/index
references/index
concepts/00-introduction
concepts/01-installation-and-setup
concepts/02-chat-interface
concepts/03-metapackage-architecture
concepts/04-protocols-acp-mcp
concepts/05-ai-personas
concepts/06-chat-files-and-persistence
concepts/07-mcp-tools-and-notebooks
concepts/08-custom-mcp-servers
concepts/09-entry-points-api
concepts/10-magic-commands
concepts/11-configuration-system
concepts/12-versioning-and-upgrades
facts
insights
log
```
