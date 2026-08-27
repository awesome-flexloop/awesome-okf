---
okf_version: "0.2"
title: "AI Agent 架构基础"
description: "AI Agent 框架跨项目架构模式对比知识库 - 12个开源项目源码深度分析，提炼8大核心架构模式"
tags:
  - ai-agent
  - fundamentals
  - architecture
  - patterns
  - cross-project
generated: 2026-08-23T02:00:00+08:00
status: stable
stale_after: P1Y
sources:
  - external/libs/models/ai/
related:
  - "[[hermes-agent]]"
  - "[[veadk-python]]"
  - "[[zleap-agent]]"
  - "[[deepseek-harness]]"
  - "[[intelligent-terminal]]"
  - "[[cordis]]"
  - "[[second-me]]"
  - "[[agency-agents]]"
  - "[[agency-agents-app]]"
  - "[[anthropics-skills]]"
  - "[[book-to-skill]]"
  - "[[i-have-adhd]]"
---

# AI Agent 架构基础

本知识包系统分析了 **12 个 AI Agent 开源项目**的源码（Python/TypeScript/C++/Rust 多语言生态），提炼出 AI Agent 框架的**8 大跨项目架构模式**。每个模式文档对比 4-5 个框架的实现差异，帮助读者建立系统性认知。

> 📖 **阅读建议**：如果你是 AI Agent 框架初学者，建议先阅读 [agent-core-loop-pattern](concepts/agent-core-loop-pattern.md) 建立核心循环概念，再按兴趣深入各项目 bundle。如果你要做框架选型，直接看 [choose-framework](examples/choose-framework.md) 示例。

## 项目覆盖一览

| 层级 | 项目 | 语言 | 核心特色 |
|------|------|------|---------|
| **Tier 1** | [hermes-agent](../hermes-agent/index.md) | Python | Nous Research 多Provider/平台/工具Agent框架，802个py文件 |
| **Tier 1** | [veadk-python](../veadk-python/index.md) | Python | 火山引擎 VeADK，基于 google-adk 的企业级 Agent SDK |
| **Tier 1** | [zleap-agent](../zleap-agent/index.md) | TS/Rust | 12包monorepo，Fiber状态机+Workspace OS+Tauri桌面端 |
| **Tier 1** | [deepseek-harness](../deepseek-harness/index.md) | TypeScript | 50+包Cordis插件架构，MCP/ACP双协议，Event-Sourcing会话 |
| **Tier 1** | [intelligent-terminal](../intelligent-terminal/index.md) | C++/Rust | Windows Terminal Agent集成，双进程架构，COM+JSON-RPC |
| **Tier 2** | [cordis](../cordis/index.md) | TypeScript | 元框架，DI+Fiber生命周期+5种事件模式，9个包 |
| **Tier 2** | [second-me](../second-me/index.md) | Python/TS | 三层记忆HMM（L0→L1→L2），LoRA个性化数字分身 |
| **Tier 3** | [agency-agents](../agency-agents/index.md) | Markdown | 270+ Persona角色库，17部门分类，NEXUS编排 |
| **Tier 3** | [agency-agents-app](../agency-agents-app/index.md) | Rust/Svelte | Tauri 2桌面应用，35个后端命令，Svelte 5 Runes |
| **Tier 3** | [anthropics-skills](../anthropics-skills/index.md) | Python/MD | Anthropic官方Skills规范，SKILL.md格式+渐进式加载 |
| **Tier 3** | [book-to-skill](../book-to-skill/index.md) | Python | 知识编译系统，7种格式解析器，四层产出流水线 |
| **Tier 3** | [i-have-adhd](../i-have-adhd/index.md) | Shell/MD | ADHD认知适配技能，10条输出规则，10+平台集成 |

## 🧩 核心概念（Concepts）

| 概念文档 | 核心问题 | 对比项目 |
|---------|---------|---------|
| [agent-core-loop-pattern](concepts/agent-core-loop-pattern.md) | Agent 如何"思考-行动-观察"？不同循环模式有何差异？ | hermes/deepseek/zleap/veadk |
| [provider-adapter-pattern](concepts/provider-adapter-pattern.md) | 如何统一接入不同LLM？适配器模式如何设计？ | hermes/zleap/veadk/deepseek |
| [plugin-architecture-patterns](concepts/plugin-architecture-patterns.md) | 插件系统的复杂度阶梯：注册表→Cordis→Capability Seam | cordis/hermes/deepseek |
| [multi-agent-orchestration](concepts/multi-agent-orchestration.md) | 多Agent如何协作？Gateway/MoA/Workspace/Subagent对比 | hermes/zleap/veadk/agency-agents |
| [memory-architecture-patterns](concepts/memory-architecture-patterns.md) | 记忆如何分层？短期/长期/HMM三层模型对比 | hermes/veadk/zleap/second-me |
| [mcp-acp-protocols](concepts/mcp-acp-protocols.md) | MCP和ACP协议有何区别？传输层如何抽象？ | hermes/deepseek/intelligent-terminal |
| [tool-system-design](concepts/tool-system-design.md) | 工具有哪些注册模式？执行生命周期如何设计？ | hermes/cordis/zleap/deepseek/intelligent |
| [prompt-architecture](concepts/prompt-architecture.md) | Prompt如何分层组织？Token预算如何分配？ | hermes/zleap/deepseek/veadk/second-me |

## 🎯 实战示例（Examples）

| 示例 | 场景 |
|------|------|
| [compare-agent-loops](examples/compare-agent-loops.md) | 4大框架Agent核心循环代码级对比，理解实现差异 |
| [choose-framework](examples/choose-framework.md) | 框架选型决策指南：企业级/桌面端/嵌入式/个人AI/协议层 |
| [build-agent-from-scratch](examples/build-agent-from-scratch.md) | 60行Python实现最小Think-Act-Observe循环 |

## 📚 参考信源（References）

| 信源 | 内容 |
|------|------|
| [cross-project-sources](references/cross-project-sources.md) | 12个项目源码位置+事实采集文件索引（865条零推测事实） |

## 学习路径

```
入门路径：
  agent-core-loop-pattern → build-agent-from-scratch → choose-framework
    ↓
进阶路径（按方向选择）：
  ├─ 框架开发：plugin-architecture-patterns → provider-adapter-pattern → cordis bundle
  ├─ 多Agent系统：multi-agent-orchestration → hermes/zleap bundle
  ├─ 记忆系统：memory-architecture-patterns → second-me bundle
  └─ 协议集成：mcp-acp-protocols → intelligent-terminal bundle
```

```{toctree}
:hidden:
:maxdepth: 7

concepts/agent-core-loop-pattern
concepts/mcp-acp-protocols
concepts/memory-architecture-patterns
concepts/multi-agent-orchestration
concepts/plugin-architecture-patterns
concepts/prompt-architecture
concepts/provider-adapter-pattern
concepts/tool-system-design
examples/build-agent-from-scratch
examples/choose-framework
examples/compare-agent-loops
references/cross-project-sources
```
