---
type: Concept
title: ACP 与 MCP 双协议
description: Jupyter AI 的协议中心设计——Agent Client Protocol (ACP) 连接外部 Agent，Model Context Protocol (MCP) 提供工具访问
tags: [protocol, acp, mcp, agent, tools, standards, vendor-lock-in]
sources:
  - id: readme
    resource: external/libs/jupyter/jupyter-ai/README.md
    title: README.md
  - id: user-guide
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/index.md
    title: users/index.md
  - id: contributors
    resource: external/libs/jupyter/jupyter-ai/docs/source/contributors/index.md
    title: contributors/index.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# ACP 与 MCP 双协议

Jupyter AI 的核心设计理念是**协议中心（protocol-centric）**——它不是硬编码支持特定 AI 服务商，而是基于两个开放标准协议构建：**ACP（Agent Client Protocol）** 和 **MCP（Model Context Protocol）**。这种设计避免了厂商锁定，让任何兼容这两个协议的 Agent 和工具都可以即插即用。

## 为什么需要双协议

理解两个协议的分工是理解 Jupyter AI 扩展性的关键：

| 协议 | 解决的问题 | 角色 |
|---|---|---|
| **ACP** | Jupyter AI 如何与外部 AI Agent 通信 | Agent 连接协议 |
| **MCP** | AI Agent 如何访问 Jupyter 环境的能力（文件、Notebook、命令） | 工具访问协议 |

简单说：**ACP 负责"接 Agent"，MCP 负责"给 Agent 工具"**。

## ACP：Agent Client Protocol

[Agent Client Protocol](https://agentclientprotocol.com)（ACP）是一个开放协议，定义了 AI Agent 与宿主应用（这里是 JupyterLab）之间的通信标准。

### ACP 在 Jupyter AI 中的作用

- **连接外部 Agent**：Claude Code、Codex CLI、Goose、Kiro 等 Agent 通过 ACP 协议连接到 Jupyter AI
- **能力协商**：Agent 启动后向 Jupyter AI 报告自己支持的模型、模式、权限设置
- **流式通信**：Agent 的回复通过 ACP 流式传回聊天界面
- **双向交互**：工具调用请求、权限审批、配置变更都通过 ACP 传递

### ACP Persona 工作流

```
Jupyter AI（ACP Client）          外部 Agent（ACP Server）
       │                                │
       │──── 启动/连接 ───────────────→│
       │                                │
       │←─── 报告能力（模型/模式/权限）──│
       │                                │
       │──── 用户消息 ────────────────→│
       │                                │
       │←─── 流式内容块 ───────────────│
       │←─── 工具调用请求 ─────────────│
       │                                │
       │──── 权限询问 → 用户            │
       │──── 审批结果 ────────────────→│
       │                                │
       │←─── 工具结果/继续流式回复 ─────│
       │                                │
```

### ACP 适配器

部分 Agent 需要额外安装 ACP 适配器包才能被 Jupyter AI 识别：

- Claude Code：`@agentclientprotocol/claude-agent-acp`（npm）
- Codex：`@zed-industries/codex-acp`（npm）

这些适配器作为 Agent CLI 和 Jupyter AI 之间的 ACP 桥梁。

### 直接模型 Persona vs ACP Persona

并非所有 Persona 都通过 ACP 连接。Jupyternaut 是一个**直接模型 Persona**——它不经过 ACP 跳转，而是直接通过 LiteLLM 调用模型 API，但仍然使用相同的 Jupyter MCP 工具：

```
直接模型 Persona（Jupyternaut）:
  用户消息 → Persona → LiteLLM → LLM API
                         ↓
                    MCP 工具调用（需权限）

ACP Persona（Claude/Codex/...）:
  用户消息 → Persona → ACP Client → 外部 Agent
                                    ↓
                              MCP 工具调用（需权限）
```

## MCP：Model Context Protocol

[Model Context Protocol](https://modelcontextprotocol.io)（MCP）是一个开放协议，定义了 AI 模型如何访问外部工具、资源和提示。Jupyter AI 通过 `jupyter_server_mcp` 包实现了 Jupyter 环境的 MCP 服务器。

### MCP 在 Jupyter AI 中的作用

- **暴露 Notebook 工具**：读取/编辑/创建/运行 Notebook 单元格
- **暴露 JupyterLab 操作**：打开文件、运行命令
- **连接自定义工具**：通过 `.jupyter/mcp_settings.json` 添加第三方 MCP 服务器
- **权限护栏**：所有 MCP 工具调用都经过权限审批流程

### 协议角色

Jupyter AI 在一个会话中可同时扮演多个 MCP 角色：

| 角色 | 说明 |
|---|---|
| **MCP Server** | Jupyter Server 通过 `jupyter_server_mcp` 暴露内置 Notebook/JupyterLab 工具 |
| **MCP Client 配置提供者** | Jupyter AI 读取 `mcp_settings.json` 并将自定义 MCP 服务器配置传递给 Agent |
| **MCP 桥接** | ACP Agent 通过 Jupyter AI 间接访问所有配置的 MCP 服务器 |

### 内置 MCP 工具

Jupyter AI 默认注册了 16 个 MCP 工具（分为 Notebook 工具集和 JupyterLab 工具集），详见 [MCP 配置与工具参考](/references/mcp-config-reference.md)。

### 自定义 MCP 服务器

用户可以通过工作区 `.jupyter/mcp_settings.json` 添加额外的 MCP 服务器：

- **Stdio 服务器**：本地进程方式（如文件系统工具、GitHub 工具）
- **HTTP 服务器**：远程 HTTP 方式（如企业内部工具服务）

配置后重启 JupyterLab，所有 ACP Agent 都能自动使用这些工具。详见 [自定义 MCP 服务器](/concepts/08-custom-mcp-servers.md)。

## 协议协作流程

一个典型的消息处理流程涉及两个协议的协作：

```
1. 用户发送消息 "帮我修复 Notebook 中第3个单元格的错误"
       │
       ▼
2. Router 将消息路由到选中的 Persona
       │
       ├── ACP Persona: Jupyter AI(ACP Client) → 外部 Agent
       └── 直接模型 Persona: Persona → LiteLLM → LLM
       │
       ▼
3. Agent/模型决定需要读取 Notebook（工具调用）
       │
       ▼
4. MCP 工具调用请求 → 权限审批（用户确认）
       │
       ▼
5. 工具执行（read_cell），结果返回给 Agent
       │
       ▼
6. Agent 分析错误，决定编辑单元格（第二个工具调用）
       │
       ▼
7. MCP 工具调用请求 → 权限审批
       │
       ▼
8. 工具执行（edit_cell），Notebook 更新
       │
       ▼
9. Agent 通过 ACP/直接回复流式返回结果到聊天面板
```

## 为什么选择开放协议

基于开放协议而非专有 API 有几个关键优势：

1. **避免厂商锁定**：可以自由切换 Agent 提供商，不被绑定到特定服务商
2. **生态兼容**：任何支持 ACP 的 Agent 和支持 MCP 的工具都可以直接使用
3. **安全透明**：协议是开放的，工具调用和权限流程可审计
4. **可扩展性**：开发者可以添加自定义 MCP 服务器扩展 Agent 能力，无需修改 Jupyter AI 核心代码

## 相关概念

- [元包架构](/concepts/03-metapackage-architecture.md)
- [AI Persona 系统](/concepts/05-ai-personas.md)
- [MCP 工具与 Notebook 交互](/concepts/07-mcp-tools-and-notebooks.md)
- [自定义 MCP 服务器](/concepts/08-custom-mcp-servers.md)
- [MCP 配置与工具参考](/references/mcp-config-reference.md)
