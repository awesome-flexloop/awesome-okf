# AI Agent 框架核心概念

本目录包含 AI Agent 框架的 10 个核心概念文档，从基础到进阶系统讲解 Agent 框架的架构设计。

## 基础概念（建议先读）

| 序号 | 文档 | 简介 |
|------|------|------|
| 0 | [AI Agent 框架导论](00-introduction.md) | 什么是 AI Agent 框架、核心子系统、12 个开源项目全景、学习路径 |
| 1 | [Agent 核心循环](01-agent-loop.md) | think-act-observe 循环的工程实现、三种执行模式、错误恢复、状态机设计 |
| 2 | [工具系统](02-tool-system.md) | 工具注册、函数调用、授权门控、ToolRegistry 单例、Capability Seam 三角色 |
| 3 | [记忆架构](03-memory-architecture.md) | 短期/长期/分层记忆、向量检索、Second-Me L0→L1→L2 三层身份建模 |

## 进阶架构

| 序号 | 文档 | 简介 |
|------|------|------|
| 4 | [多智能体编排](04-multi-agent.md) | MoA 两阶段推理、Workspace 流水线、子代理委派、去中心化 AI Space |
| 5 | [模型 Provider 抽象](05-provider-abstraction.md) | 适配器模式、ProviderRegistry 双注册表、能力声明、运行时委托 |
| 6 | [上下文管理](06-context-management.md) | 滑动窗口、语义压缩、Workspace 隔离、编译时知识蒸馏（24-51×token节省） |

## 扩展与生态

| 序号 | 文档 | 简介 |
|------|------|------|
| 7 | [技能与 Persona 系统](07-skill-persona.md) | SKILL.md 标准、280+ Persona 角色库、知识编译、认知适配风格技能 |
| 8 | [插件化架构模式](08-plugin-architecture.md) | 注册表→副作用→Cordis Fiber 生命周期、Context 原型链、5种事件模式、能力缝 |
| 9 | [Agent 通信协议](09-agent-protocols.md) | MCP 工具协议、ACP 客户端协议、传输层抽象、COM/OSC 原生集成 |
