---
type: Reference
title: JupyterLite AI 源码参考
description: jupyterlite-ai v0.19.0 源码结构与核心文件索引
tags: [jupyterlite-ai, source, reference]
generated: { by: "ai:trae-claude", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: repo
    resource: https://github.com/jupyterlite/ai
    title: jupyterlite/ai GitHub Repository
---

# JupyterLite AI 源码结构参考

## 项目概览

jupyterlite-ai 是 JupyterLab/Notebook 7/JupyterLite 的浏览器端 AI 扩展，提供代码补全和聊天功能。版本 v0.19.0，采用 TypeScript monorepo + Python 包结构。

## 目录结构

```
jupyterlite-ai/
├── packages/                    # TypeScript 包（monorepo workspaces）
│   ├── agent/                   # @jupyternaut/agent - AI 代理核心
│   │   ├── src/
│   │   │   ├── agent.ts         # AgentManager 核心实现
│   │   │   ├── tokens.ts        # Lumino Token 与接口定义
│   │   │   ├── providers/       # AI 模型提供者
│   │   │   │   ├── built-in-providers.ts  # 内置5个Provider
│   │   │   │   ├── provider-registry.ts   # Provider 注册表
│   │   │   │   ├── provider-tools.ts      # Provider 托管工具
│   │   │   │   ├── models.ts              # 模型创建工厂
│   │   │   │   └── model-info.ts          # 模型元数据
│   │   │   ├── tools/           # AI 工具
│   │   │   │   ├── tool-registry.ts       # 工具注册表
│   │   │   │   ├── commands.ts           # 命令发现/执行工具
│   │   │   │   ├── web.ts                # 浏览器抓取工具
│   │   │   │   └── skills.ts             # 技能发现/加载工具
│   │   │   └── skills/          # AI 技能系统
│   │   │       ├── index.ts
│   │   │       ├── skill-registry.ts
│   │   │       ├── skill-loader.ts
│   │   │       ├── parse-skill.ts
│   │   │       └── types.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── persona/                 # @jupyternaut/persona - Persona 编排层
│   │   ├── src/
│   │   │   ├── index.ts         # JupyterLab 插件注册入口
│   │   │   ├── persona.ts       # Persona 处理核心
│   │   │   ├── persona-registry.ts
│   │   │   ├── diff-manager.ts  # Diff 管理
│   │   │   ├── tokens.ts
│   │   │   ├── models/
│   │   │   │   └── settings-model.ts   # AI 设置模型
│   │   │   ├── widgets/
│   │   │   │   ├── ai-settings.tsx     # 设置面板
│   │   │   │   └── provider-config-dialog.tsx
│   │   │   ├── completion/
│   │   │   │   └── completion-provider.ts  # 代码补全
│   │   │   ├── components/
│   │   │   └── chat-commands/
│   │   └── package.json
│   └── ai/                      # @jupyterlite/ai - Chat UI 层
│       ├── src/
│       │   ├── index.ts         # JupyterLab 插件注册入口
│       │   ├── tokens.ts
│       │   ├── chat-model.ts    # 聊天模型
│       │   ├── chat-model-handler.ts
│       │   ├── chat-commands/
│       │   ├── components/
│       │   └── widgets/
│       │       └── main-area-chat.ts
│       └── package.json
├── python/                      # Python 包
│   ├── jupyterlite-ai/          # 主扩展包
│   │   └── pyproject.toml
│   └── jupyternaut-persona/     # Persona 扩展包
│       └── pyproject.toml
├── docs/                        # 官方文档（Jupyter Book）
├── ui-tests/                    # Playwright E2E 测试
└── demo/                        # JupyterLite 演示配置
```

## 核心文件职责

| 文件 | 核心类/接口 | 职责 |
|------|-----------|------|
| `agent.ts` | `AgentManager`, `AgentManagerFactory` | AI 代理执行循环、Tool Loop、MCP 集成 |
| `tokens.ts` | `IToolRegistry`, `IProviderRegistry`, `ISkillRegistry`, `IAgentManager`, `IAISettingsModel`, `IDiffManager` | 全局 Token 与接口契约 |
| `provider-registry.ts` | `ProviderRegistry` | 注册/创建 AI 模型提供者 |
| `built-in-providers.ts` | `anthropicProvider`, `googleProvider`, `mistralProvider`, `openaiProvider`, `genericProvider` | 5个内置 Provider 定义 |
| `tool-registry.ts` | `ToolRegistry` | 工具注册/获取/移除 |
| `commands.ts` | `createDiscoverCommandsTool`, `createExecuteCommandTool` | JupyterLab 命令工具 |
| `web.ts` | `createBrowserFetchTool` | 浏览器原生 URL 抓取工具 |
| `skills.ts` | `createDiscoverSkillsTool`, `createLoadSkillTool` | 技能发现与加载工具 |
| `skill-registry.ts` | `SkillRegistry` | 技能注册/列表/获取 |
| `persona/index.ts` | 默认导出插件数组 | Persona 编排层 JupyterLab 插件 |
| `ai/index.ts` | 默认导出插件数组 | Chat UI 层 JupyterLab 插件 |

## 关键依赖

| 包名 | 用途 |
|------|------|
| `ai` (Vercel AI SDK) | 核心 LLM 交互：`generateText`, `streamText`, `ToolLoopAgent`, `tool` |
| `@ai-sdk/anthropic` | Anthropic Claude 模型支持 |
| `@ai-sdk/google` | Google Gemini 模型支持 |
| `@ai-sdk/mistral` | Mistral AI 模型支持 |
| `@ai-sdk/openai` | OpenAI 模型支持 |
| `@ai-sdk/openai-compatible` | 通用 OpenAI 兼容接口（Ollama/LiteLLM） |
| `@ai-sdk/mcp` | MCP (Model Context Protocol) 客户端 |
| `@lumino/coreutils` | Lumino 核心工具：Token, PromiseDelegate, UUID |
| `@lumino/signaling` | 信号系统：Signal, ISignal |
| `@jupyterlab/application` | JupyterLab 应用：JupyterFrontEnd, JupyterFrontEndPlugin |
| `@jupyter/chat` | Jupyter Chat 组件：ChatWidget, MultiChatPanel, IChatModel |
| `jupyter-mcp-manager` | MCP 服务器管理：IMcpManager |
| `jupyter-secrets-manager` | 密钥管理：ISecretsManager, SecretsManager |
| `zod` | 工具输入 Schema 验证 |
