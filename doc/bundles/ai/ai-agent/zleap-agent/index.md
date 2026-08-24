---
okf_version: "0.2"
title: "ZLEAP Agent"
description: "Workspace-first TypeScript Agent框架 - Cordis架构的三级Fiber执行模型与多平台网关"
tags:
  - ai-agent
  - typescript
  - cordis
  - workspace
  - fiber
  - gateway
  - multi-agent
generated: true
status: active
stale_after: P3M
sources:
  - https://github.com/zleap/zleap-agent
related:
  - "[[ai-agent-fundamentals]]"
  - "[[cordis]]"
  - "[[hermes-agent]]"
  - "[[deepseek-harness]]"
---

# ZLEAP Agent

ZLEAP Agent 是基于Cordis服务化插件架构的TypeScript智能体框架，采用Workspace-first设计理念。核心是Run→Work→WorkStep三级Fiber执行模型与状态机，提供ConversationService对话服务、ChatEngine执行引擎、PostgreSQL+pgvector双引擎持久化记忆（A/B双线：agent_memory笔记+core事件图）、RRF多路融合排序召回，以及支持飞书/微信/Feishu CLI的Gateway多平台IM网关。

## 🧩 概念导航（Concepts）

### 核心运行时
- [fiber-lifecycle](concepts/fiber-lifecycle.md) — Fiber执行生命周期与状态机：Run→Work→WorkStep三级模型，三套状态枚举、事件总线与生命周期钩子
- [agent-orchestration](concepts/agent-orchestration.md) — Agent编排引擎：@zleap/agent的L2编排层，ConversationService、ChatEngine、Workspace管线、Turn Loop、记忆梦境整理
- [ai-abstraction](concepts/ai-abstraction.md) — AI抽象层：@zleap/ai的ProviderAdapter统一接口、双Provider实现（Anthropic/OpenAI兼容）、SSE流式解析、Embeddings向量化
- [host-runtime](concepts/host-runtime.md) — Host运行时与服务编排：@zleap/host的PostgreSQL四级回退、runServe主管、安装/升级生命周期、多实例防护

### 记忆与持久化
- [store-persistence](concepts/store-persistence.md) — 状态持久化存储与向量记忆引擎：PostgreSQL+pgvector双引擎，A/B双线记忆、RRF融合召回、抽取管线

### 网关与任务
- [gateway-server](concepts/gateway-server.md) — Gateway多平台网关与消息路由：PlatformAdapter统一接口、三平台适配（Feishu/WeChat/Feishu CLI）、权限模式与消息分片
- [tasks-scheduling](concepts/tasks-scheduling.md) — 任务调度系统：pg-boss队列实现cron定时任务、任务处理器注册、死信队列
- [avatar-persona](concepts/avatar-persona.md) — Avatar人格与输入组装系统：人格定义、提示词组装策略
- [subagent-delegation](concepts/subagent-delegation.md) — 子Agent委派模式：Workspace Handoff机制

### 交互界面
- [cli-interface](concepts/cli-interface.md) — CLI与桌面端（TUI + Tauri Desktop）：命令行交互与桌面应用集成

## 🎯 示例导航（Examples）

- [setup-zleap-agent](examples/setup-zleap-agent.md) — 安装配置Zleap Agent：pnpm安装、PostgreSQL+pgvector配置、模型连接、启动CLI和Web服务
- [create-custom-workspace](examples/create-custom-workspace.md) — 创建自定义Workspace：配置系统提示词、工具集、技能包和路由规则，实现子Agent委派
- [configure-gateway-channel](examples/configure-gateway-channel.md) — 配置网关渠道：飞书/微信/飞书CLI网关配置、认证凭据、权限模式、自定义平台接入
- [schedule-cron-task](examples/schedule-cron-task.md) — 定时任务调度：pg-boss队列cron任务注册、任务处理、死信队列管理

## 📚 参考导航（References）

- [zleap-agent-sources](references/zleap-agent-sources.md) — ZLEAP-Agent v0.3.3 TypeScript monorepo源码路径、12 packages目录结构与关键文件清单

## 🔗 关联 Bundle

- [cordis](../cordis/index.md) — Cordis服务框架，ZLEAP Agent的核心架构基础
- [hermes-agent](../hermes-agent/index.md) — Hermes Agent，Python版渐进式Agent框架对比参考
- [deepseek-harness](../deepseek-harness/index.md) — DeepSeek Harness，Cordis架构Python实现参考
- [ai-agent-fundamentals](../ai-agent-fundamentals/index.md) — AI Agent基础概念与跨项目模式

---

> **信任声明**：本文档基于 ZLEAP-Agent v0.3.3 源码逐模块分析，经 OKF 五阶段流程（R→I→E→V→C）生成。
> 
> **生成时间**：2026-08-23 | **下次审查**：2026-11-23 | **维护者**：OKF Wiki Bot
> 
> **内容统计**：10 个概念 + 4 个示例 + 1 个信源 = 15 个内容文档

```{toctree}
:hidden:

concepts/agent-orchestration
concepts/ai-abstraction
concepts/avatar-persona
concepts/cli-interface
concepts/fiber-lifecycle
concepts/gateway-server
concepts/host-runtime
concepts/store-persistence
concepts/subagent-delegation
concepts/tasks-scheduling
examples/configure-gateway-channel
examples/create-custom-workspace
examples/schedule-cron-task
examples/setup-zleap-agent
references/zleap-agent-sources
.spec/facts
```
