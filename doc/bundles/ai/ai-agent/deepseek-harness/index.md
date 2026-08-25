---
okf_version: "0.2"
title: "DeepSeek Harness"
description: "DeepSeek官方Agent SDK - R1推理模型优化的Cordis插件化智能体框架"
tags:
  - ai-agent
  - deepseek
  - python
  - cordis
  - react
  - reasoning
  - mcp
generated: true
status: active
stale_after: P3M
sources:
  - https://github.com/deepseek-ai/DeepSeek-Harness
related:
  - "[[ai-agent-fundamentals]]"
  - "[[cordis]]"
  - "[[hermes-agent]]"
  - "[[veadk-python]]"
---

# DeepSeek Harness

DeepSeek Harness 是深度求索（DeepSeek）官方推出的智能体框架，基于Cordis插件架构构建，专为DeepSeek R1推理模型和V3通用模型优化。核心采用ReactLoopAgent状态机与Inbox消息队列设计，提供类型安全的defineTool工具定义、四级瀑布执行管道、Code Mode、SubagentProvider多后端子Agent、MCP客户端桥接（stdio/HTTP双传输），以及ACP JSON-RPC over stdio服务端能力。

## 🧩 概念导航（Concepts）

### 核心运行时
- [agent-runtime-loop](concepts/agent-runtime-loop.md) — Agent运行时主循环：ReactLoopAgent状态机、Inbox消息队列、Turn-Step执行循环
- [llm-abstraction-layer](concepts/llm-abstraction-layer.md) — LLM抽象层：LlmRuntime服务、LlmAdapter适配器、ContentBlock/StreamChunk统一词汇、BlockAssembler流式组装
- [cordis-plugin-architecture](concepts/cordis-plugin-architecture.md) — Cordis插件核心架构：Context/Service/Plugin/Fiber体系、声明合并、依赖注入、瀑布事件、Bundle组合

### 工具与子Agent
- [tool-and-subagent](concepts/tool-and-subagent.md) — 工具系统与子Agent：defineTool类型安全定义、四级瀑布管道、Code Mode、SubagentProvider多后端
- [skill-system](concepts/skill-system.md) — Skill技能系统：技能注册、加载与执行机制
- [filesystem-and-shell](concepts/filesystem-and-shell.md) — 文件系统与Shell工具：文件读写、命令执行、沙箱安全

### 协议与集成
- [mcp-protocol-integration](concepts/mcp-protocol-integration.md) — MCP协议集成：Model Context Protocol工具/资源/Prompt、stdio/HTTP双传输、工具命名空间
- [acp-agent-protocol](concepts/acp-agent-protocol.md) — ACP Agent通信协议：JSON-RPC over stdio、session生命周期、权限决策与优雅关闭
- [session-and-context](concepts/session-and-context.md) — 会话与上下文管理：会话状态、上下文窗口管理、消息历史
- [web-client](concepts/web-client.md) — Web客户端架构：Web UI与HTTP API服务端设计

## 🎯 示例导航（Examples）

- [build-agent-loop](examples/build-agent-loop.md) — 构建Agent主循环：ReactLoopAgent状态机、消息发送、状态监控和事件处理
- [define-custom-tool](examples/define-custom-tool.md) — 定义自定义工具：defineTool类型安全工具定义、参数Schema、输出投影、并发安全
- [connect-mcp-server](examples/connect-mcp-server.md) — 连接MCP服务器：stdio/HTTP连接外部MCP服务器并使用其工具
- [create-cordis-plugin](examples/create-cordis-plugin.md) — 创建Cordis插件：Service定义、配置Schema、依赖注入和声明合并

## 📚 参考导航（References）

- [deepseek-harness-sources](references/deepseek-harness-sources.md) — DeepSeek Harness 0.1.0-rc.5 源码路径、版本信息、Cordis插件架构、关键文件清单

## 🔗 关联 Bundle

- [cordis](../cordis/index.md) — Cordis服务框架，DeepSeek Harness的插件架构基础
- [hermes-agent](../hermes-agent/index.md) — Hermes Agent，Python版渐进式多Agent框架参考
- [veadk-python](../veadk-python/index.md) — VEADK Python，另一Python Agent SDK对比参考
- [ai-agent-fundamentals](../ai-agent-fundamentals/index.md) — AI Agent基础概念与跨项目模式
- [zleap-agent](../zleap-agent/index.md) — ZLEAP Agent，Cordis架构TypeScript实现参考

---

> **信任声明**：本文档基于 DeepSeek Harness 0.1.0-rc.5 源码逐模块分析，经 OKF 五阶段流程（R→I→E→V→C）生成。
> 
> **生成时间**：2026-08-23 | **下次审查**：2026-11-23 | **维护者**：OKF Wiki Bot
> 
> **内容统计**：10 个概念 + 4 个示例 + 1 个信源 = 15 个内容文档

```{toctree}
:hidden:

concepts/acp-agent-protocol
concepts/agent-runtime-loop
concepts/cordis-plugin-architecture
concepts/filesystem-and-shell
concepts/llm-abstraction-layer
concepts/mcp-protocol-integration
concepts/session-and-context
concepts/skill-system
concepts/tool-and-subagent
concepts/web-client
examples/build-agent-loop
examples/connect-mcp-server
examples/create-cordis-plugin
examples/define-custom-tool
references/deepseek-harness-sources
```
