---
okf_version: "0.2"
title: "VEADK Python"
description: "火山引擎智能体开发套件 - 豆包大模型原生Agent SDK与全链路开发框架"
tags:
  - ai-agent
  - volcengine
  - bytedance
  - python
  - doubao
  - a2a
  - rag
generated: true
status: active
stale_after: P3M
sources:
  - https://github.com/volcengine/veadk-python
related:
  - "[[ai-agent-fundamentals]]"
  - "[[deepseek-harness]]"
  - "[[second-me]]"
  - "[[zleap-agent]]"
---

# VEADK Python

VEADK（Volcano Engine Agent Development Kit）Python 是火山引擎推出的智能体开发套件，与火山方舟（Ark）平台深度集成，豆包系列模型开箱即用。核心采用Agent/Runner双层架构，支持A2A（Agent-to-Agent）协议、A2UI（Agent-driven UI）声明式富组件、8种向量后端的RAG知识库、双层记忆系统、Sequential/Parallel/Loop/Supervisor组合Agent模式，以及Tunnel隧道安全桥接企业内网MCP服务。

## 🧩 概念导航（Concepts）

### 核心架构
- [agent-and-runner](concepts/agent-and-runner.md) — Agent类与Runner执行引擎：核心双层架构，Agent定义能力，Runner驱动会话执行
- [model-configuration](concepts/model-configuration.md) — 模型配置层：LiteLlm通用适配+ArkLlm火山原生Responses API双后端
- [tool-definition](concepts/tool-definition.md) — 工具定义与调用：15+内置工具延迟加载、MCP Router远程工具、自动挂载机制
- [memory-system](concepts/memory-system.md) — 记忆系统：ShortTermMemory会话级+LongTermMemory跨会话双层架构
- [knowledge-base](concepts/knowledge-base.md) — 知识库集成：KnowledgeBase统一抽象、8种向量后端、Profile分库、RAG自动工具挂载

### 多Agent与协议
- [composite-agents](concepts/composite-agents.md) — 组合Agent模式：Sequential/Parallel/Loop/Supervisor四种协作模式，AgentBuilder YAML构建
- [a2a-protocol](concepts/a2a-protocol.md) — Agent-to-Agent协议：基于Google a2a-sdk的Agent发现、远程调用、Agent Card元数据交换
- [a2ui-protocol](concepts/a2ui-protocol.md) — Agent-to-UI协议：声明式富UI组件输出、Catalog组件目录、JSON Schema验证
- [tunnel-networking](concepts/tunnel-networking.md) — 隧道与网络通信：WebSocket安全桥接企业内网MCP到云端，无需开放入站端口

### CLI与工具
- [cli-commands](concepts/cli-commands.md) — CLI命令系统：基于Click的15+子命令，覆盖初始化/调试/知识库/部署/评估/强化学习全生命周期

## 🎯 示例导航（Examples）

- [quickstart-agent](examples/quickstart-agent.md) — 快速创建Agent并运行：使用Agent+Runner配置模型，执行多轮对话和流式输出
- [add-knowledge-base](examples/add-knowledge-base.md) — 添加知识库实现RAG：支持Milvus/OpenSearch/VikingDB等向量后端，文档导入与检索增强
- [build-sequential-workflow](examples/build-sequential-workflow.md) — 构建顺序与并行工作流：Sequential/Parallel组合多Agent，output_key状态传递
- [expose-a2a-server](examples/expose-a2a-server.md) — 暴露A2A服务端：VeA2AServer通过FastAPI提供JSON-RPC接口，Agent Card配置

## 📚 参考导航（References）

- [veadk-python-sources](references/veadk-python-sources.md) — VEADK-Python 源码路径、版本信息、核心目录与关键文件清单

## 🔗 关联 Bundle

- [ai-agent-fundamentals](../ai-agent-fundamentals/index.md) — AI Agent 基础概念与跨项目模式
- [deepseek-harness](../deepseek-harness/index.md) — DeepSeek Harness，另一Python Agent SDK参考
- [zleap-agent](../zleap-agent/index.md) — ZLEAP Agent，TypeScript Agent框架架构对比
- [second-me](../second-me/index.md) — Second Me个人智能体，记忆与个性化参考
- [cordis](../cordis/index.md) — Cordis插件架构，服务编排设计参考

---

> **信任声明**：本文档基于 VEADK-Python 源码逐模块分析，经 OKF 五阶段流程（R→I→E→V→C）生成。
> 
> **生成时间**：2026-08-23 | **下次审查**：2026-11-23 | **维护者**：OKF Wiki Bot
> 
> **内容统计**：10 个概念 + 4 个示例 + 1 个信源 = 15 个内容文档

```{toctree}
:hidden:
:maxdepth: 7

concepts/a2a-protocol
concepts/a2ui-protocol
concepts/agent-and-runner
concepts/cli-commands
concepts/composite-agents
concepts/knowledge-base
concepts/memory-system
concepts/model-configuration
concepts/tool-definition
concepts/tunnel-networking
examples/add-knowledge-base
examples/build-sequential-workflow
examples/expose-a2a-server
examples/quickstart-agent
references/veadk-python-sources
```
