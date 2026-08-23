---
title: 核心 SDK 与三层架构
type: concept
bundle: /datawhale/deepagents
related:
  - /datawhale/deepagents/concepts/monorepo-architecture
  - /datawhale/deepagents/concepts/code-module
  - /datawhale/deepagents/concepts/acp-protocol
sources:
  - https://github.com/datawhalechina/deepagents/blob/main/libs/ARCHITECTURE.md
  - https://github.com/datawhalechina/deepagents/blob/main/libs/deepagents/README.md
  - https://github.com/datawhalechina/deepagents/blob/main/libs/deepagents/deepagents/graph.py
  - https://github.com/datawhalechina/deepagents/blob/main/openwiki/architecture/overview.md
---

# 核心 SDK 与三层架构

Deep Agents 核心 SDK（`deepagents` 包，位于 `libs/deepagents/`）是整个项目的地基。它的核心设计哲学是**不重新发明运行时**，而是在 LangChain 和 LangGraph 之上提供有主见的默认组装。

## 三层栈

```text
Deep Agents      有主见的框架：默认值、中间件、后端、配置文件
LangChain        Agent 抽象：model + tools + middleware → agent loop
LangGraph        运行时：状态、检查点、流式、中断
```

- **LangGraph** 是运行时层，将 Agent 作为图执行，管理状态、检查点、流式 API 和中断/恢复。
- **LangChain 的 `create_agent()`** 是 Agent 抽象层，调用者用 model、tools、middleware 描述 Agent，LangChain 构建调用模型、执行工具、循环直到完成的循环。
- **Deep Agents** 是 `create_agent()` 之上的有主见框架，通过 `create_deep_agent()` 组装默认中间件栈并配置后端、子 Agent、技能、记忆和配置文件。

## create_deep_agent() 组装点

`create_deep_agent()` 位于 `libs/deepagents/deepagents/graph.py`，是 SDK 的唯一公共组装入口。构造阶段执行六步：

1. 解析请求的聊天模型及适用的提供商/框架配置文件
2. 解析文件系统、技能、记忆和 `execute` 行为使用的后端
3. 组装主 Agent 中间件栈
4. 构建默认通用子 Agent 和调用者提供的子 Agent
5. 组合系统提示（调用者指令 + SDK 默认值 + 配置文件文本）
6. 调用 LangChain 的 `create_agent(...)` 生成可运行的 Agent 图

## 中间件栈

中间件是 Deep Agents 注入行为的核心机制。与工具（只能在模型选择后被动执行）不同，中间件可以在模型调用前后、工具执行前后介入，能够：

- 从当前模型请求中添加或移除工具
- 将文件系统、记忆、技能、子 Agent、人在回路指令注入最终系统提示
- 在上下文增长时摘要/压缩或卸载消息历史
- 在图状态中存储类型化值供后续中间件或工具使用
- 在内置文件系统工具运行前强制执行文件系统权限

### 栈顺序

1. **基础脚手架中间件**：创建规划、文件系统访问、子 Agent 委派、摘要、请求清理能力
2. **调用者中间件**：应用添加自定义行为的位置
3. **配置文件和尾部中间件**：提供商特定行为、工具排除、提示缓存、记忆注入、人工审批

### 核心中间件模块

| 模块 | 职责 |
|------|------|
| `middleware/subagents.py` | 子 Agent 中间件和嵌套 `create_agent` 使用 |
| `middleware/filesystem.py` | 文件系统操作中间件 |
| `middleware/skills.py` | 可按需加载的可复用行为 |
| `middleware/memory.py` | 跨会话记忆 |
| `middleware/permissions.py` | 文件系统路径级权限策略 |
| `middleware/summarization.py` | 长线程摘要/压缩 |
| `middleware/async_subagents.py` | 异步子 Agent 支持 |

## 后端系统

后端位于 `libs/deepagents/deepagents/backends/`，决定文件、记忆和 Shell 执行的位置：

| 后端 | 用途 |
|------|------|
| `state` | 默认线程级状态后端 |
| `filesystem` | 文件系统持久化 |
| `store` | 跨线程存储后端 |
| `composite` | 组合多个后端 |
| `local_shell` | 本地 Shell 执行 |
| `sandbox` | 沙箱执行 |
| `langsmith` | LangSmith 沙箱集成 |
| `context_hub` | ContextHub 后端 |

如果后端无法执行 Shell 命令，SDK 会从模型请求中移除 `execute` 工具并省略 Shell 特定提示文本，而不是在调用后才拒绝。

## 配置文件（Profiles）

配置文件位于 `libs/deepagents/deepagents/profiles/`，分为两类：

- **Provider profiles**（`profiles/provider/`）：提供商特定行为，包括 nvidia、openai、openrouter
- **Harness profiles**（`profiles/harness/`）：模型特定框架调优，包括 anthropic haiku/opus/sonnet、nvidia nemotron、openai codex

配置文件通过 `deepagents.provider_profiles` 和 `deepagents.harness_profiles` entry-point groups 插件化注册，支持外部扩展。

## 状态与持久化

- `DeepAgentState` 扩展 LangChain 的 `AgentState`，`messages` 字段使用 `DeltaChannel` reducer 保持检查点线性增长
- 图状态和检查点由 LangGraph 管理（对话状态、消息历史、中断、可恢复性）
- 文件系统和记忆持久化由 Deep Agents 后端路由
- 中间件可通过 `state_schema` 贡献额外的类型化状态字段，私有中间件字段被追踪以防止意外泄露到子 Agent

## 工具可见性分层

模型可见的工具是多层协作的结果：

1. 内置中间件贡献标准工具（todo 管理、文件系统、子 Agent 委派）
2. 调用者 `tools=` 添加到该集合
3. 解析后的后端决定 Shell 执行是否可用
4. 框架配置文件可通过 `excluded_tools` 隐藏工具
5. 文件系统权限在调用时对内置工具强制执行路径级策略

## 安全模型

Deep Agents 遵循"信任 LLM"模型：Agent 可以做其工具允许的任何事。边界应在工具/沙箱层面强制执行，而非期望模型自我监督。权限不是可见性机制——模型可能仍看到一个调用后会被拒绝或中断的工具。

## 与其他概念的关系

- [Monorepo 架构](/ai/datawhale/deepagents/concepts/monorepo-architecture) 描述了 SDK 包在仓库中的位置。
- [Code终端编码Agent](/ai/datawhale/deepagents/concepts/code-module) 在 SDK 之上构建编码特定的中间件/工具/审批栈。
- [ACP协议集成](/ai/datawhale/deepagents/concepts/acp-protocol) 将编译后的 Agent 图适配为 ACP 服务器。
