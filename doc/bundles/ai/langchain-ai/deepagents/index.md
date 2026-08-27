---
type: bundle
okf_version: "0.2"
scope: deepagents
name: deepagents
version: "0.7.8"
source: https://github.com/langchain-ai/deepagents
description: Deep Agents——LangChain 开源的 batteries-included 代理框架，基于 LangGraph 运行时，提供子代理委派、文件系统、上下文管理、技能、内存、人工在环和 ACP 协议集成
---

# Deep Agents

**Deep Agents** 是 LangChain 开源的"batteries-included"（开箱即用）代理框架——一个有主见的（opinionated）代理 harness，可直接运行，也可扩展、覆盖或替换任何零件。它构建在 LangChain `create_agent()` 和 LangGraph 运行时之上，为长周期、多步骤代理任务打包了文件系统、子代理委派、上下文管理、技能、内存和人工在环等能力。

- **SDK 版本**：0.7.8
- **许可证**：MIT
- **Python 要求**：≥3.11,<4.0
- **核心依赖**：langchain ≥1.3.16、langchain-core ≥1.6.0、langchain-anthropic ≥1.6.1、langsmith ≥0.11.1
- **仓库**：[github.com/langchain-ai/deepagents](https://github.com/langchain-ai/deepagents)

## 核心特性

- **子代理委派**：通过 `task` 工具将任务委派给拥有隔离上下文窗口的代理，支持声明式 `SubAgent`、预编译 `CompiledSubAgent` 和远程 `AsyncSubAgent` 三种形态
- **可插拔文件系统**：统一的 `BackendProtocol` 接口，七种内置后端（State、Filesystem、Composite、Store、LocalShell、LangSmithSandbox、ContextHub），支持本地/沙箱/远程存储
- **上下文管理**：自动摘要压缩（token 阈值触发）、工具输出卸载到磁盘、`DeltaChannel` 将检查点增长从 O(N²) 降至 O(N)
- **Shell 访问**：沙箱后端支持 `execute` 工具运行 shell 命令，非沙箱后端自动隐藏
- **持久化内存**：`MemoryMiddleware` 从 AGENTS.md 文件加载项目上下文，启动时注入系统提示
- **技能系统**：Anthropic Agent Skills 模式，渐进式披露，支持 base → user → project → team 分层
- **人工在环**：`interrupt_on` 和 `FilesystemPermission` 的 interrupt 模式支持工具调用前的批准/编辑/拒绝
- **ACP 协议集成**：通过 `deepagents-acp` 包在 Zed 等 ACP 兼容编辑器中运行 Deep Agent
- **Profile 系统**：Harness Profile 和 Provider Profile 正交调优，为不同模型定制工具可见性、提示和中间件
- **模型无关**：支持任何支持 tool calling 的 LLM（OpenAI、Anthropic、Google、开放权重、本地模型）

## monorepo 组成

| 包 | PyPI 名 | 用途 |
|---|---|---|
| 核心 SDK | `deepagents` | 代理框架主体（本 bundle 描述对象） |
| ACP 连接器 | `deepagents-acp` | Agent Client Protocol 集成（Zed 等编辑器） |
| 部署 CLI | `deepagents-cli` | `init`/`deploy`/`agents`/`mcp-servers` 部署工具 |
| 终端编码代理 | `deepagents-code` | `dcode` 命令行编码代理 |

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

## 文档导航

### 核心概念

- 总览 — Deep Agents 是什么、三层架构定位、核心特性
- 规划与子代理 — 上下文隔离、三种子代理形态、task 工具、安全设计模式
- Todo 与上下文管理 — 摘要压缩、消息卸载、技能、内存、DeltaChannel
- ACP 协议 — Agent Client Protocol 集成、编辑器对接、会话管理

### API 与技术参考

- 核心 API — `create_deep_agent()`、`DeepAgentState`、公共导出
- 中间件栈 — 默认中间件顺序、自定义合并规则、必需脚手架
- 后端系统 — `BackendProtocol`、七种内置后端、沙箱协议
- Profile 机制 — Harness/Provider Profile、模型特化调优
- ACP 协议参考 — `AgentServerACP` API 详情
- lca-deepagents 变体 — LangChain Academy 课程材料仓库说明

### 使用示例

- lca-deepagents 教学变体 — Chinook Sales Assistant 综合示例

### 规格文档

- 事实清单 — 64条从源码验证的编号事实
- 深度洞察 — 5个架构设计洞察

## 变体说明

本 bundle 同时覆盖 [lca-deepagents](https://github.com/langchain-ai/lca-deepagents)——LangChain Academy 官方课程材料仓库。它不是 SDK 的分支，而是固定在 `deepagents==0.7.0` 的教学示例集合，包含5个模块的课程练习和 Chinook Sales Assistant 综合项目。详见 lca-deepagents 变体说明。

## 目录结构

```
langchain-ai/deepagents/
├── spec/
│   ├── facts.md           # 源码事实验证清单（64条）
│   └── insights.md        # 架构设计洞察（5篇）
├── concepts/              # 核心概念（4篇）
│   ├── overview.md
│   ├── planning-subagents.md
│   ├── todo-context.md
│   └── acp-protocol.md
├── references/            # API/技术参考（6篇）
│   ├── api.md
│   ├── middleware-stack.md
│   ├── backends.md
│   ├── profiles.md
│   ├── acp-protocol.md
│   └── lca-variant.md
├── examples/              # 使用示例（1篇）
│   └── lca-variant.md
├── log.md                 # 变更日志
└── index.md               # 本文件
```

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
