---
type: Concept
title: AI Agent 框架导论
description: 什么是 AI Agent 框架、核心架构范式、本教程覆盖的 12 个开源项目全景与学习路径
tags: [ai-agent, introduction, agent-frameworks, overview]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T01:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T02:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: src-register
    resource: /references/ai-agent-sources.md
---

# AI Agent 框架导论

## 什么是 AI Agent 框架

AI Agent 框架是构建、部署和管理大语言模型（LLM）驱动的自主智能体的软件基础设施。与传统的"请求-响应"式 API 调用不同，AI Agent 具备**感知-思考-行动**的循环能力：接收环境输入、进行推理决策、调用工具执行动作、观察结果并继续迭代，直到任务完成。

一个完整的 AI Agent 框架通常包含以下核心子系统：

1. **Agent 运行时（Runtime）**：驱动 think-act-observe 循环的执行引擎
2. **工具系统（Tool System）**：让 Agent 能够调用外部能力（搜索、代码执行、文件操作等）
3. **记忆系统（Memory）**：管理对话历史、知识库和长期偏好
4. **模型抽象层（Provider Abstraction）**：统一接入不同 LLM 提供商的接口
5. **上下文管理（Context Management）**：在有限的上下文窗口内高效管理信息
6. **编排机制（Orchestration）**：多 Agent 协作、任务分解、工作流管理
7. **技能/插件系统（Skills/Plugins）**：可复用的能力扩展机制
8. **通信协议（Protocols）**：Agent 与宿主环境、其他 Agent 之间的通信标准

## 为什么阅读 Agent 框架源码

阅读生产级 Agent 框架的源码可以带来以下收获：

- **理解 Agent 循环的工程实现**：ReAct/Function Calling 在实际代码中如何组织？工具调用授权、错误恢复、中断处理等非功能需求如何实现？
- **掌握架构模式**：从工具注册表、插件系统到多 Agent 编排，这些框架沉淀了可复用的架构模式
- **跨语言对比学习**：Python（hermes/veadk）和 TypeScript（Zleap/Cordis/dsh）生态各自的设计取舍
- **理解协议标准**：MCP、ACP 等新兴 Agent 互操作协议的实际实现
- **从 Persona 到 Runtime 的完整栈**：从 280+ 角色定义（agency-agents）到 C++/Rust 终端嵌入（intelligent-terminal），覆盖 Agent 技术栈的全部层次

## 本教程覆盖的 12 个开源项目

本知识包系统分析了 `external/libs/models/ai/` 目录下的 12 个项目，横跨 Python、TypeScript、C++/Rust、Rust 四种语言生态：

### 完整运行时框架

| 项目 | 语言 | 核心特色 | 架构复杂度 |
|------|------|---------|-----------|
| **hermes-agent** | Python | 75+ 参数可配置 Agent、工具集注册表、MoA 多代理、多平台传输 | ★★★★★ |
| **veadk-python** | Python | Agent/Runner 分层、长短记忆分离、运行时委托（adk/codex/piagent） | ★★★★☆ |
| **Zleap-Agent** | TypeScript | Workspace-first 上下文隔离、9 状态机、Hook 系统、pgvector RRF 记忆 | ★★★★★ |
| **deepseek-harness** | TypeScript | "一切皆插件"Cordis 架构、Capability Seam 模式、ACP 支持 | ★★★★★ |

### 元框架与基础设施

| 项目 | 语言 | 核心特色 |
|------|------|---------|
| **Cordis** | TypeScript | 时空可组合性元框架：Context 原型链 + Fiber 生命周期 + 5 种事件模式 |
| **intelligent-terminal** | C++/Rust | Windows Terminal 原生 Agent 集成：ACP 协议 + COM 服务器 + OSC 事件总线 |
| **Second-Me** | Python/TS | 三层记忆 HMM（L0→L1→L2）+ LoRA 个性化 + 去中心化 Agent 网络 |

### 技能与 Persona 生态

| 项目 | 类型 | 核心特色 |
|------|------|---------|
| **agency-agents** | Markdown 集合 | 280+ 专业 Agent persona，18 个部门，多工具适配脚本 |
| **anthropics/skills** | MD+Python | Anthropic 官方 Skills 参考实现，文档技能含 OOXML schema 验证 |
| **book-to-skill** | Python | "编译时知识蒸馏"：将书籍编译为分层 Skill，节省 24–51× token |
| **i-have-adhd** | MD+Shell | 认知科学驱动的输出风格技能，10 条规则 + Hook 自动激活 |

## 核心架构范式对比

通过横向对比 12 个项目，我们可以识别出 AI Agent 框架的三种主流架构范式：

### 范式一：单体可配置 Agent（hermes-agent 风格）

一个高度参数化的 `AIAgent` 类通过 75+ 构造参数控制所有行为——工具集选择、模型配置、执行模式（并发/顺序/分段）、授权策略、平台传输。工具通过全局注册表（`ToolRegistry` 单例）注册，工具集通过 `TOOLSETS` 字典组合（支持 `includes` 嵌套）。多代理通过 MoA（Mixture of Agents）实现 reference fan-out → aggregator 两阶段推理。

**适合场景**：快速部署、单 Agent 应用、需要精细控制工具组合。

### 范式二：插件化一切（Cordis/deepseek-harness 风格）

所有功能通过插件系统组合。Cordis 提供 Context 原型链继承（extend/isolate/intercept）、Fiber 生命周期管理（PENDING→LOADING→ACTIVE→DISPOSED）、5 种事件分发模式。每个能力遵循 Service Definition（接口）+ Service Provider（实现）+ Consumer（使用者）三角色的"能力缝"（Capability Seam）模式。配置通过 `cordis.yml` 声明式组合，支持 group 分组和 isolate 隔离。

**适合场景**：企业级可扩展平台、需要热更新/动态加载、复杂功能组合。

### 范式三：工作区隔离流水线（Zleap-Agent 风格）

Agent 不直接面对所有工具和记忆，而是按 Workspace 隔离上下文。`AgentRuntime.run()` 按 `spaces[]` 数组顺序依次执行，每个 Workspace 有独立的 handler、可用工具集和记忆访问权限，上一个 Workspace 的 Artifact 作为下一个的输入。运行时状态机覆盖 Run/Work/Step 三级生命周期，9 个 Hook 点提供观测和扩展能力。

**适合场景**：复杂任务分解、多步骤流水线、需要强安全隔离的场景。

## 学习路径

本教程按以下路径组织，建议按顺序阅读：

### 基础概念（先读这些）

1. [Agent 核心循环](01-agent-loop.md) — think-act-observe 循环的工程实现、执行模式、错误恢复
2. [工具系统](02-tool-system.md) — 工具注册、函数调用、授权门控、并发执行
3. [记忆架构](03-memory-architecture.md) — 短期/长期/分层记忆、向量检索、身份建模

### 进阶架构

4. [多智能体编排](04-multi-agent.md) — MoA、Workspace 流水线、子代理委派
5. [模型 Provider 抽象](05-provider-abstraction.md) — 多模型适配、模型注册表、能力声明
6. [上下文管理](06-context-management.md) — 窗口预算、压缩策略、分层加载

### 扩展与生态

7. [技能与 Persona 系统](07-skill-persona.md) — SKILL.md 标准、persona 定义、知识编译
8. [插件化架构模式](08-plugin-architecture.md) — 注册表、Cordis Fiber、能力缝、副作用管理
9. [Agent 通信协议](09-agent-protocols.md) — MCP、ACP、传输层抽象

### 深度示例

- [hermes-agent 架构深度走读](/examples/hermes-agent-deep-dive.md)
- [Cordis 插件系统深度解析](/examples/cordis-plugin-system.md)
- [Second-Me 分层记忆模型解析](/examples/second-me-memory-model.md)
- [Intelligent Terminal ACP 集成模式](/examples/intelligent-terminal-acp.md)

## 前置知识

阅读本教程需要以下基础：

- **Python 或 TypeScript**：至少能阅读其中一种语言的代码；核心概念文档使用双语言对比示例
- **LLM 基础概念**：理解 Token、上下文窗口、Function Calling、System Prompt 等基本概念
- **基本的软件架构知识**：理解注册表模式、策略模式、依赖注入等常见设计模式

不需要的知识：

- 编译器设计或形式语言理论
- 深度学习模型训练细节
- 特定云平台的部署经验

## 相关概念

- [信源登记簿](/references/ai-agent-sources.md) — 12 个项目的源码路径、关键文件和版本信息
- [Agent 核心循环](01-agent-loop.md) — 第一步：理解 Agent 是如何"思考"的
