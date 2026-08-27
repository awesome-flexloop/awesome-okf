---
type: Concept
title: 架构概览
description: jupyterlite-ai 三层架构（Agent/Persona/Chat）详解，核心数据流与组件协作关系
tags: [jupyterlite-ai, architecture, layers]
generated: { by: "ai:trae-claude", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: source
    resource: /references/source-code.md
    title: JupyterLite AI 源码参考
  - id: plugins
    resource: /references/plugin-architecture.md
    title: JupyterLab 插件架构参考
---

# 架构概览

jupyterlite-ai 采用三层架构设计，每层职责明确，通过 Lumino Token 系统实现松耦合的依赖注入。

## 三层架构图

```
┌─────────────────────────────────────────────────────────────┐
│                  @jupyterlite/ai (Chat UI 层)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │MultiChat │ │ChatModel │ │Toolbar   │ │Chat Commands  │  │
│  │Panel     │ │Handler   │ │Factory   │ │(/clear,/skill)│  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘  │
├─────────────────────────────────────────────────────────────┤
│               @jupyternaut/persona (编排层)                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │Persona   │ │Settings  │ │Completion│ │Diff Manager   │  │
│  │Registry  │ │Panel     │ │Provider  │ │               │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘  │
│  注册所有核心服务为 JupyterLab 插件，管理生命周期和配置         │
├─────────────────────────────────────────────────────────────┤
│                @jupyternaut/agent (Agent 核心层)             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │AgentMgr  │ │Provider  │ │Tool      │ │Skill Registry │  │
│  │Factory   │ │Registry  │ │Registry  │ │               │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Vercel AI SDK ToolLoopAgent             │   │
│  │  generateText / streamText / tool calling loop      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         ↕ 通过 Lumino Token (IToolRegistry, IProviderRegistry, etc.) 注入
```

## Agent 核心层

`@jupyternaut/agent` 包是纯逻辑层，不依赖 JupyterLab UI，核心组件：

| 组件 | 类名 | 职责 |
|------|------|------|
| Agent 管理器 | `AgentManager` | 执行 AI 对话循环、处理工具调用、管理审批流程 |
| Agent 工厂 | `AgentManagerFactory` | 创建 Agent 实例、管理 MCP 连接、维护 Agent 池 |
| Provider 注册表 | `ProviderRegistry` | 注册/创建 LLM Provider（Anthropic/OpenAI 等） |
| Tool 注册表 | `ToolRegistry` | 注册/查找 AI 可调用的工具 |
| Skill 注册表 | `SkillRegistry` | 注册/加载 AI 技能包 |
| 内置工具工厂 | `createXxxTool()` | 创建 discover_commands、execute_command、browser_fetch 等工具 |
| 内置 Provider | `xxxProvider` 对象 | 5 个预定义 Provider 配置 |

Agent 层依赖 Vercel AI SDK 的 `ToolLoopAgent` 实现核心的「LLM 调用 → 工具执行 → 结果回传 → 继续生成」循环。

## Persona 编排层

`@jupyternaut/persona` 包是连接核心逻辑和 JupyterLab 的桥梁，通过 JupyterFrontEndPlugin 注册所有服务：

- 注册 5 个内置 Provider 到 IProviderRegistry
- 创建 ToolRegistry 并注册内置工具（discover_commands、execute_command、browser_fetch、discover_skills、load_skill）
- 创建 SkillRegistry 并从配置路径加载技能文件
- 使用 SecretsManager 签名创建 AgentManagerFactory（确保密钥安全访问）
- 提供设置面板（AISettingsWidget）配置 API Key、模型、参数
- 注册代码补全提供者（AICompletionProvider）
- 管理 Diff 显示（DiffManager）
- 通过 PersonaRegistry 将每个 Chat Model 映射到独立的 AgentManager 实例

## Chat UI 层

`@jupyterlite/ai` 包实现用户交互界面：

- **MultiChatPanel**：侧边栏多会话管理面板，支持新建/切换/重命名聊天
- **MainAreaChat**：主区域聊天 Widget，支持从侧边栏拖拽到主工作区
- **ChatModelHandler**：创建和管理 IAIChatModel 实例，桥接 @jupyter/chat 和 AgentManager
- **ChatWidget**：复用 @jupyter/chat 的聊天渲染组件
- **工具栏**：模型选择、工具选择、停止生成、清除对话、保存/恢复聊天
- **聊天命令**：/clear 清除对话、/skills 列出技能、@ 提及 Persona

## 核心数据流

用户发送消息的完整数据流：

```
用户输入
  → ChatModel (IAIChatModel)
    → AgentManager.generateResponse(message)
      → ProviderRegistry.createChatModel() 获取 LanguageModel
      → ToolLoopAgent.stream() (Vercel AI SDK)
        → LLM API 调用（流式）
        → 如果返回 tool calls：
          → 检查是否需要用户审批（commandsRequiringApproval）
          → 执行工具（execute_command / browser_fetch / MCP tools）
          → 工具结果回传 LLM，继续生成
      → 流式输出 message_chunk 事件
        → ChatModel 接收并渲染消息
          → ChatWidget 实时更新 UI
```

## MCP 集成数据流

MCP 服务器的工具通过独立通道集成：

```
jupyter-mcp-manager (IMcpManager)
  → AgentManagerFactory 监听 serversChanged 信号
  → @ai-sdk/mcp 的 createMCPClient 连接 MCP 服务器
  → 获取 MCP 服务器暴露的 tools
  → 通过 initializeAgent(mcpTools) 注入到所有 AgentManager
  → Agent 的 ToolLoopAgent 可以调用 MCP 工具
```

## 多会话隔离

每个聊天面板（ChatPanel）拥有独立的：
- `IAIChatModel`（消息历史、输入状态）
- 通过 PersonaRegistry 绑定独立的 `AgentManager`（对话上下文、token 计数）
- 共享的 ProviderRegistry、ToolRegistry、SkillRegistry 单例

这意味着不同聊天窗口可以使用不同的 Provider/模型，互不干扰。

## 扩展点架构

第三方扩展通过以下标准 JupyterLab 依赖注入方式扩展：

```typescript
const myPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:add-custom-provider',
  autoStart: true,
  requires: [IProviderRegistry],  // 或 IToolRegistry, ISkillRegistry
  activate: (app, registry) => {
    registry.registerProvider(myCustomProvider);
  }
};
```

## 相关概念

- [Token 依赖注入系统](02-token-di-system.md)
- [Provider 模型管理](03-provider-system.md)
- [Tool 工具系统](04-tool-system.md)
- [Agent 执行引擎](05-agent-engine.md)
- [插件架构参考](../references/plugin-architecture.md)
