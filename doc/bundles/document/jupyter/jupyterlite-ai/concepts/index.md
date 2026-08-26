# JupyterLite AI 核心概念

本目录包含 JupyterLite AI 的核心架构概念文档，按推荐阅读顺序排列。

## 阅读路径

建议按序号顺序阅读，从整体到局部逐步深入理解：

```
00 介绍与定位 → 01 架构总览 → 02 Token/DI系统 → 03 Provider系统 → 04 Tool系统
→ 05 Agent引擎 → 06 Skill系统 → 07 配置系统 → 08 MCP集成 → 09 Chat UI → 10 代码补全
```

## 概念文档索引

| 序号 | 文档 | 难度 | 核心内容 |
|------|------|------|---------|
| 00 | [介绍与定位](00-introduction.md) | ⭐ 入门 | 项目是什么、解决什么问题、与 jupyter-ai 的区别、适用场景 |
| 01 | [架构总览](01-architecture-overview.md) | ⭐ 入门 | 三层架构（Agent/Persona/UI）、核心数据流、包依赖关系 |
| 02 | [Token 与 DI 系统](02-token-di-system.md) | ⭐⭐ 进阶 | Lumino Token 机制、6大核心 Token、依赖注入、插件契约 |
| 03 | [Provider 模型提供商系统](03-provider-system.md) | ⭐⭐ 进阶 | IProviderRegistry、多提供商注册、模型配置、Vercel AI SDK 适配 |
| 04 | [Tool 工具系统](04-tool-system.md) | ⭐⭐ 进阶 | IToolRegistry、工具注册/发现/调用、审批机制、内置工具 |
| 05 | [Agent 引擎](05-agent-engine.md) | ⭐⭐⭐ 高级 | AgentManager、ToolLoop 循环、消息处理、流式响应、MCP 集成 |
| 06 | [Skill 技能系统](06-skill-system.md) | ⭐⭐⭐ 高级 | ISkillRegistry、技能加载、与 Persona 关联、技能生命周期 |
| 07 | [设置与配置系统](07-settings-and-config.md) | ⭐⭐ 进阶 | 配置 Schema、密钥管理（SecretsManager）、设置面板、序列化 |
| 08 | [MCP 集成](08-mcp-integration.md) | ⭐⭐⭐ 高级 | MCP 管理器、服务器连接、工具桥接、传输协议（stdio/SSE） |
| 09 | [Chat UI 交互](09-chat-ui.md) | ⭐⭐ 进阶 | 聊天面板、消息渲染、输入处理、代码操作、命令面板集成 |
| 10 | [代码补全系统](10-code-completion.md) | ⭐⭐ 进阶 | AI 行内补全、IInlineCompletionProvider、FIM 模式、Notebook 上下文感知、Tab 补全 |

## 概念关系图

```
┌─────────────────────────────────────────────────┐
│                  Chat UI (09)                    │
│         聊天面板 / 消息渲染 / 用户交互            │
└────────────────────┬────────────────────────────┘
                     │ 用户消息/工具结果
                     ▼
┌─────────────────────────────────────────────────┐
│              Agent 引擎 (05)                     │
│    ToolLoop 循环 / 消息处理 / 流式响应           │
├──────────┬──────────┬──────────┬────────────────┤
│ Provider │  Tool    │  Skill   │  MCP           │
│  (03)    │  (04)    │  (06)    │  (08)          │
├──────────┴──────────┴──────────┴────────────────┤
│           Token / DI 系统 (02)                   │
│      服务注册 / 依赖注入 / 插件契约              │
├─────────────────────────────────────────────────┤
│          设置与配置系统 (07)                     │
│   配置 Schema / 密钥管理 / 持久化                │
├─────────────────────────────────────────────────┤
│           代码补全系统 (10)                      │
│   IInlineCompletionProvider / FIM / 上下文感知  │
└─────────────────────────────────────────────────┘
```

## 前置知识

阅读概念文档前，建议了解：
- JupyterLab 扩展开发基础（Lumino 插件系统）
- TypeScript 基础
- LLM 工具调用（Function Calling）概念
- 基本的 AI Agent 工作原理

## 相关资源

- [API 参考](/references/index.md) — 接口定义、源码索引、工具/提供商参考
- [实践示例](/examples/index.md) — 从安装到开发的操作指南
- [官方文档](https://jupyterlite-ai.readthedocs.io/)

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-architecture-overview
02-token-di-system
03-provider-system
04-tool-system
05-agent-engine
06-skill-system
07-settings-and-config
08-mcp-integration
09-chat-ui
10-code-completion
```
