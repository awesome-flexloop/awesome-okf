---
okf_version: "0.2"
title: "Hermes Agent"
description: "渐进式披露多Agent框架 - 从简单对话到团队协作的可扩展AI Agent平台"
tags:
  - ai-agent
  - multi-agent
  - cordis
  - mcp
  - acp
  - gateway
  - python
generated: true
status: active
stale_after: P3M
sources:
  - https://github.com/NousResearch/hermes-agent
related:
  - "[[ai-agent-fundamentals]]"
  - "[[cordis]]"
  - "[[zleap-agent]]"
  - "[[agency-agents]]"
---

# Hermes Agent

Hermes Agent 是一个渐进式披露（Progressive Disclosure）的多Agent框架，设计理念是"随你成长"——新用户可立即开始简单对话，高级用户可解锁自定义Agent、技能、工具、团队协作、TUI/Web UI、网关接入以及22+消息平台集成。核心基于Cordis服务编排，支持ACP（Agent Client Protocol）和MCP（Model Context Protocol），内置约100个工具、8种记忆插件、34+模型提供商。

## 🧩 概念导航（Concepts）

### 核心架构
- [agent-core-loop](concepts/agent-core-loop.md) — Agent 核心思考-行动-观察循环：AIAgent类的Think-Act-Observe循环实现
- [tool-registry](concepts/tool-registry.md) — 工具注册表与调用机制：ToolRegistry单例管理约100个内置工具，支持11类工具集
- [provider-abstraction](concepts/provider-abstraction.md) — Provider抽象层与模型适配：ProviderProfile+ProviderTransport双层抽象，支持34+模型提供商
- [memory-subsystem](concepts/memory-subsystem.md) — 记忆子系统：MemoryManager编排器+8个记忆插件（mem0/honcho/byterover等）

### 协议与网关
- [mcp-protocol](concepts/mcp-protocol.md) — MCP协议集成：stdio/SSE/HTTP传输、服务器懒加载、工具动态注册、安全过滤
- [acp-adapter](concepts/acp-adapter.md) — ACP适配器：HermesACPAgent服务器、SessionManager、stdio传输，为Zed/Codex等编辑器提供接入
- [gateway-multi-agent](concepts/gateway-multi-agent.md) — Gateway多Agent编排：GatewayRunner主控制器、多平台适配器、会话路由、LRU缓存
- [platform-plugin](concepts/platform-plugin.md) — 平台插件系统与消息渠道：统一接入22+消息平台（Telegram/Discord/Slack/飞书/企业微信/WhatsApp等）

### 任务与交互
- [cron-scheduler](concepts/cron-scheduler.md) — 定时任务调度：cron表达式解析、作业存储、文件锁并发控制、Agent/纯脚本双模式
- [cli-app-entry](concepts/cli-app-entry.md) — CLI入口与应用管理：argparse子命令体系、TUI/CLI聊天、会话管理、Desktop桌面应用与Bootstrap安装器

## 🎯 示例导航（Examples）

- [create-simple-agent](examples/create-simple-agent.md) — 创建简单Agent并对话：使用AIAgent初始化实例，配置Provider，通过chat()进行多轮对话
- [register-custom-tool](examples/register-custom-tool.md) — 注册自定义工具：通过ToolRegistry注册自定义工具，定义Function Schema和handler
- [use-mcp-server](examples/use-mcp-server.md) — 连接MCP服务器：配置stdio/SSE/HTTP三种传输，自动发现远程工具并注册
- [setup-gateway-multi-agent](examples/setup-gateway-multi-agent.md) — 搭建Gateway多Agent系统：配置多平台适配器、会话隔离、流式分发

## 📚 参考导航（References）

- [hermes-agent-sources](references/hermes-agent-sources.md) — Hermes Agent v0.20.0 源码路径、版本信息、核心目录与关键文件清单

## 🔗 关联 Bundle

- [ai-agent-fundamentals](../ai-agent-fundamentals/index.md) — AI Agent 基础概念与跨项目模式
- [cordis](../cordis/index.md) — Cordis 服务框架，Hermes Agent 的核心编排引擎
- [zleap-agent](../zleap-agent/index.md) — ZLEAP Agent，TypeScript 版 Cordis Agent 框架参考
- [agency-agents](../agency-agents/index.md) — Agency Agents，多Agent角色专业化协作方案
- [deepseek-harness](../deepseek-harness/index.md) — DeepSeek Harness，同样基于Cordis的Python Agent框架
- [anthropics-skills](../anthropics-skills/index.md) — Anthropic Skills，技能定义与安全实践参考

---

> **信任声明**：本文档基于 Hermes Agent v0.20.0 源码逐模块分析，经 OKF 五阶段流程（R→I→E→V→C）生成。
> 
> **生成时间**：2026-08-23 | **下次审查**：2026-11-23 | **维护者**：OKF Wiki Bot
> 
> **内容统计**：10 个概念 + 4 个示例 + 1 个信源 = 15 个内容文档

```{toctree}
:maxdepth: 7

concepts/acp-adapter
concepts/agent-core-loop
concepts/cli-app-entry
concepts/cron-scheduler
concepts/gateway-multi-agent
concepts/mcp-protocol
concepts/memory-subsystem
concepts/platform-plugin
concepts/provider-abstraction
concepts/tool-registry
examples/create-simple-agent
examples/register-custom-tool
examples/setup-gateway-multi-agent
examples/use-mcp-server
references/hermes-agent-sources
```
