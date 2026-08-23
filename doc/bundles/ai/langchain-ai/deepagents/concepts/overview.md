---
type: concept
scope: deepagents
name: overview
version: "0.7.8"
source: https://github.com/langchain-ai/deepagents
description: Deep Agents 总览——opinionated agent harness 的定位、三层架构与核心特性
---

# Deep Agents 总览

## 它是什么

**Deep Agents** 是一个开源的"batteries-included"（开箱即用）代理框架——一个有主见的（opinionated）代理，可直接运行。你可以扩展、覆盖或替换其中任何零件，而无需 fork。

它不是一个新的代理运行时，而是构建在 LangChain `create_agent()` 之上的组装层，后者又运行在 LangGraph 运行时之上。

## 三层架构

理解 Deep Agents 的关键是理解它在技术栈中的位置：

```
┌─────────────────────────────────────────────────────┐
│  Deep Agents                                        │
│  opinionated harness: defaults, middleware,         │
│  backends, profiles                                 │
├─────────────────────────────────────────────────────┤
│  LangChain                                          │
│  agent abstraction: model + tools + middleware      │
│  → agent loop                                       │
├─────────────────────────────────────────────────────┤
│  LangGraph                                          │
│  runtime: state, checkpoints, streaming, interrupts │
└─────────────────────────────────────────────────────┘
```

- **LangGraph** 是运行时。它将代理作为图执行：步骤通过转换连接，每个步骤可读写共享状态。LangGraph 负责在步骤间传递状态、暴露流式 API、保存检查点、通过 interrupt 暂停/恢复运行。
- **LangChain 的 `create_agent()`** 是 LangGraph 之上的代理抽象。调用者用模型、工具和中间件描述代理，LangChain 构建调用模型、执行工具、重复直到完成的循环。
- **Deep Agents** 是 `create_agent()` 之上的有主见的 harness。它不引入新运行时，而是组装长运行代理最常需要的默认中间件栈、后端、子代理、技能、内存和 profiles。

选择 Deep Agents 而非裸 `create_agent()` 的原因不是它是不同类型的运行时，而是它打包了长运行代理默认需要的零件。

## 四大设计原则

### 1. Opinionated（有主见）

默认值为长周期、多步骤工作调优。内置工具集（文件操作、shell、任务委派）、默认中间件顺序、自动添加的通用子代理——这些决策都基于实际代理使用经验。

### 2. Extensible（可扩展）

无需 fork 即可覆盖或替换任何零件：

- 通过 `middleware=` 参数插入自定义中间件，按名称匹配可替换默认中间件
- 通过 `tools=` 添加自定义工具（加法式，不移除内置工具）
- 通过 `HarnessProfile` 调整工具可见性、提示、中间件
- 通过 `BackendProtocol` 实现自定义存储后端
- 任何 LangGraph `CompiledStateGraph` 可作为 `CompiledSubAgent` 传入

### 3. Model-agnostic（模型无关）

支持任何支持 tool calling 的 LLM：

- 前沿 API（OpenAI、Anthropic、Google）
- 通过 Baseten、Fireworks 等提供商托管的开放权重模型
- 通过 Ollama、vLLM、llama.cpp 的自托管模型
- 任何 LangChain chat model

模型通过 `provider:model` 字符串（如 `"openai:gpt-5.5"`）或预初始化的 `BaseChatModel` 实例指定。

### 4. Production-ready（生产就绪）

构建在 LangGraph 之上，提供：

- 流式输出
- 持久化检查点
- 中断/恢复（人工在环）
- LangSmith 追踪和评估
- 多种部署选项

## 核心特性

### 子代理（Sub-agents）

将任务委派给拥有隔离上下文窗口的代理。子代理只看到父代理传入的任务描述，返回一条最终报告。支持三种形态：声明式 `SubAgent`、预编译 `CompiledSubAgent`、远程 `AsyncSubAgent`。

详见 [规划与子代理](/ai/langchain-ai/deepagents/concepts/planning-subagents)。

### 文件系统（Filesystem）

通过可插拔后端读取、写入、编辑、搜索文件。支持本地磁盘、内存状态、沙箱、LangGraph Store 等后端。`execute` 工具在沙箱后端上运行 shell 命令。

### 上下文管理（Context Management）

- 自动摘要压缩：当 token 使用量超过阈值时，用 LLM 摘要旧消息
- 工具输出卸载：大的工具结果写入后端磁盘，释放上下文窗口
- 历史持久化：卸载的消息以 Markdown 存储，媒体文件单独保存

### Shell 访问

在选择的沙箱中运行命令。安全边界在沙箱层——非沙箱后端不暴露 `execute` 工具。

### 持久化内存

可插拔的状态和存储后端，用于跨会话记忆。`MemoryMiddleware` 从 AGENTS.md 文件加载项目上下文并注入系统提示。

### 人工在环（Human-in-the-loop）

在工具执行前批准、编辑或拒绝工具调用。通过 `interrupt_on` 配置和 `FilesystemPermission` 的 `interrupt` 模式实现。

### 技能（Skills）

代理可按需加载的可复用行为。每个技能是一个包含 `SKILL.md`（YAML frontmatter + Markdown 指令）的目录，支持渐进式披露。

### 工具（Tools）

自带自定义函数或任何 MCP 服务器。内置工具与用户工具通过中间件合并。

## 快速开始

```bash
uv add deepagents
```

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[my_custom_tool],
    system_prompt="You are a research assistant.",
)
result = agent.invoke({"messages": "Research LangGraph and write a summary"})
```

代理可以规划、读写文件、管理自己的上下文。添加自定义工具、切换模型、自定义提示、配置子代理等。

## monorepo 组成

Deep Agents 仓库是一个 monorepo，包含多个包：

| 包 | 路径 | 用途 |
|---|---|---|
| `deepagents` | `libs/deepagents/` | 核心 SDK（本 bundle 主要描述对象） |
| `deepagents-acp` | `libs/acp/` | ACP 协议连接器（Zed 等编辑器） |
| `deepagents-cli` | `libs/cli/` | 部署工具（init/deploy/agents/mcp-servers） |
| `deepagents-code` | `libs/code/` | 终端编码代理（`dcode`） |

## 何时使用

- **用 Deep Agents**：需要完整 harness——规划、上下文管理、委派——开箱即用
- **用 LangChain `create_agent()`**：需要更轻量的 harness，不需要捆绑的中间件
- **直接用 LangGraph**：代理循环本身不是正确形状，需要自定义图

三层可以组合：任何 LangGraph `CompiledStateGraph` 都可以作为子代理传入 Deep Agent。

## 相关概念

- [规划与子代理](/ai/langchain-ai/deepagents/concepts/planning-subagents) — 子代理架构详解
- [Todo 与上下文管理](/ai/langchain-ai/deepagents/concepts/todo-context) — 摘要、技能、内存
- [ACP 协议](/ai/langchain-ai/deepagents/concepts/acp-protocol) — 编辑器集成
- [核心 API](/ai/langchain-ai/deepagents/references/api) — API 参考
