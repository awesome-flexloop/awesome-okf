---
type: concept
title: "Beta: Agents、Memory与Skills"
description: "详解 Anthropic Python SDK Beta API 命名空间，包括 Agents 托管智能体、Memory Stores 跨会话记忆、Sessions 持久化会话、Skills 可复用技能、Environments 沙箱环境、Vaults 凭证管理、MCP 协议支持与 Agent Toolset 工具集。"
tags: [beta, agents, memory, sessions, skills, mcp, environments, vaults, experimental]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: experimental
stale_after: 2026-11-27
sources:
  - id: F-049~F-058
    resource: /python-sdk/references/tools-beta.md
    title: "Anthropic Python SDK 工具系统与 Beta API 参考"
---

# Beta: Agents、Memory与Skills

Anthropic Python SDK 将所有实验性功能统一放在 `client.beta` 命名空间下，通过版本化的 `anthropic-beta` 请求头控制 API 访问。Beta 层正在快速演进，从基础的 Tool Use（工具调用）扩展到完整的智能体（Agents）生态，包括托管智能体、长期记忆、持久化会话、可复用技能、沙箱执行环境、凭证保险库、MCP 协议支持等高级能力。这些功能代表了 Anthropic 构建生产级 AI 智能体平台的方向。

> ⚠️ **重要提示**：所有 Beta API 均为实验性功能，可能在未来版本中发生破坏性变更（包括参数调整、端点变化、甚至功能移除）。生产环境使用请锁定 SDK 版本，并密切关注 Anthropic 官方更新日志。

**本文适合谁**：正在构建复杂 AI 智能体应用的开发者、希望利用 Anthropic 托管能力减少自建基础设施的工程师、探索下一代 AI Agent 架构的技术负责人。

## Beta API 访问机制

Beta API 通过 `client.beta` 懒加载属性访问，这是一个 `Beta` 类实例（继承自 `SyncAPIResource`），定义在 `resources/beta/beta.py`。

### 版本化 Header 控制

每个 Beta 功能对应一个特定的版本日期字符串，SDK 在调用对应 API 时会自动添加 `anthropic-beta` 请求头：

```python
from anthropic import Anthropic

client = Anthropic()

# 访问 Beta API - SDK 自动添加对应的 anthropic-beta 头
agent = client.beta.agents.create(
    model="claude-3-5-sonnet-latest",
    name="my-assistant",
)
# 自动添加: "anthropic-beta": "managed-agents-2026-04-01"
```

这种设计允许 Anthropic 并行迭代多个 Beta 功能，不同功能有独立的版本周期，不会相互影响。

### Beta 子资源索引

`client.beta` 通过 `@cached_property` 提供以下子资源入口：

| Beta 子资源 | 属性路径 | 说明 |
|------------|---------|------|
| Agents | `client.beta.agents` | 托管智能体管理（创建、版本、配置） |
| Sessions | `client.beta.sessions` | 持久化会话管理 |
| Memory Stores | `client.beta.memory_stores` | 长期记忆存储 |
| Skills | `client.beta.skills` / `client.skills` | 可复用技能 |
| Environments | `client.beta.environments` | 沙箱执行环境 |
| Vaults | `client.beta.vaults` | 凭证安全存储 |
| Messages | `client.beta.messages` | Beta 版消息 API（含 batches 等） |
| Models | `client.beta.models` | Beta 模型管理 |
| Files | `client.beta.files` | Beta 文件管理 |
| Deployments | `client.beta.deployments` | 部署管理 |
| Webhooks | `client.beta.webhooks` | Webhook 配置 |
| Organization | `client.beta.organization` | 组织管理 |
| User Profiles | `client.beta.user_profiles` | 用户配置 |
| Dreams | `client.beta.dreams` | Dreams 功能 |
| Tunnels | `client.beta.tunnels` | 隧道功能 |

所有 Beta 子资源均有对应的异步版本（`async_client.beta.*`），API 完全对称。

## Agents：托管智能体

Agents 是 Anthropic 提供的**托管智能体（Managed Agents）**服务，允许你在 Anthropic 平台上定义、版本化和运行可复用的智能体配置。Agent 本质上是一组预定义的指令（system prompt）、工具集合、模型配置和技能的组合，可以被多次调用而无需每次重复配置。

### Agent 的核心概念

一个 Agent 包含以下要素：
- **模型（model）**：Agent 使用的 Claude 模型
- **名称（name）**：Agent 的唯一名称
- **系统指令（system）**：Agent 的人设/行为指令
- **工具（tools）**：Agent 可调用的工具集合
- **技能（skills）**：Agent 可使用的可复用技能
- **MCP 服务器（mcp_servers）**：Agent 可连接的 MCP 服务器
- **元数据（metadata）**：自定义标签
- **多智能体配置（multiagent）**：多智能体协作配置

### Agents API 核心方法

```python
from anthropic import Anthropic

client = Anthropic()

# 1. 创建 Agent
agent = client.beta.agents.create(
    model="claude-3-5-sonnet-latest",  # 必填
    name="customer-support-agent",     # 必填
    description="A helpful customer support agent",
    system="You are a friendly customer support agent. Be concise and helpful.",
    tools=[...],                       # 工具定义
    skills=[...],                      # 技能引用
    metadata={"department": "support"},
)

# 2. 获取 Agent 详情
retrieved_agent = client.beta.agents.retrieve(agent.id)

# 3. 更新 Agent
updated_agent = client.beta.agents.update(
    agent.id,
    description="Updated description",
)

# 4. 列出所有 Agents
agents_page = client.beta.agents.list(limit=20)
for a in agents_page:
    print(a.id, a.name)

# 5. Agent 版本管理
versions = client.beta.agents.versions.list(agent.id)
specific_version = client.beta.agents.versions.retrieve(agent.id, version_id="v1")
```

### Agents.create 端点细节

- HTTP 方法：`POST`
- 端点：`"/v1/agents?beta=true"`
- 自动添加请求头：`"anthropic-beta": "managed-agents-2026-04-01"`
- 必填参数：`model` 和 `name`
- 可选参数：`description`、`mcp_servers`、`metadata`、`multiagent`、`skills`、`system`、`tools`、`betas`

Agent 版本化允许你迭代更新 Agent 配置而不影响已使用旧版本的生产工作负载。

## Memory Stores：跨会话记忆

Memory Stores 提供了**长期记忆（Long-term Memory）**能力，允许 Agent 在多个会话之间持久化存储信息，解决了普通对话"聊完就忘"的问题。记忆存储可以理解为 Agent 的"知识库"或"长期记忆库"。

### 记忆存储的核心概念

- **Memory Store（记忆库）**：一个命名的记忆容器，可以关联到 Agent
- **Memory（记忆条目）**：存储在记忆库中的单条信息
- **记忆工具（Memory Tool）**：内置工具，允许 Claude 在对话中自主读写记忆

### Memory Stores API 核心方法

```python
from anthropic import Anthropic

client = Anthropic()

# 1. 创建记忆库
store = client.beta.memory_stores.create(
    name="user-preferences",
    description="Stores user preferences and past interactions",
)

# 2. 获取记忆库
retrieved_store = client.beta.memory_stores.retrieve(store.id)

# 3. 更新记忆库
updated_store = client.beta.memory_stores.update(
    store.id,
    name="user-preferences-v2",
)

# 4. 列出所有记忆库
stores = client.beta.memory_stores.list()

# 5. 管理记忆条目
memories = client.beta.memory_stores.memories.list(store.id)

# 6. 记忆版本管理
memory_versions = client.beta.memory_stores.memory_versions.list(store.id, memory.id)
```

### 内置 Memory 工具

SDK 在 `lib/tools/_beta_builtin_memory_tool.py` 中提供了内置的 Memory 工具实现。当 Agent 配置了记忆库后，Claude 可以自主决定何时存取记忆：

```python
# 伪代码展示概念
# Claude 在对话中自动调用记忆工具：
# 1. 对话开始时检索相关记忆
# 2. 对话中发现重要信息时自动保存到记忆
# 3. 记忆冲突时自动更新或保留多版本
```

这种设计让记忆管理对开发者透明——你只需要创建记忆库并关联到 Agent，Claude 会自主管理记忆的读写。

## Sessions：持久化会话

Sessions 提供了**持久化对话上下文**能力，与无状态的 `messages.create` 不同，Session 会在服务端保存完整的对话历史，支持多轮交互中断和恢复。

### Session 的核心概念

- **Session（会话）**：一个持久化的对话容器
- **Thread（线程）**：Session 内的对话线程
- **Event（事件）**：Session 中发生的事件（消息、工具调用等）

### Sessions API 核心方法

```python
from anthropic import Anthropic

client = Anthropic()

# Session 管理
session = client.beta.sessions.create(...)
retrieved_session = client.beta.sessions.retrieve(session.id)

# Thread 管理
thread = client.beta.sessions.threads.create(session.id, ...)
messages = client.beta.sessions.threads.messages.list(thread.id)

# Event 管理
events = client.beta.sessions.events.list(session.id)
```

Sessions 适合构建需要长时间运行、可能跨多次用户访问的对话场景，例如：
- 客服对话：用户关闭页面后再次打开可以继续之前的对话
- 多步任务：一个任务分多次完成，中间可以暂停
- 协作场景：多个用户或 Agent 共享同一个会话上下文

## Skills：可复用技能

Skills（技能）是可复用的能力单元，类似于"工具包"或"插件"，可以被多个 Agent 引用。Skill 将一组相关的工具、指令和配置打包成一个可版本化的单元。

### Skills API 核心方法

```python
from anthropic import Anthropic

client = Anthropic()

# Skills 同时在 client.skills 和 client.beta.skills 可用
skill = client.skills.create(
    name="web-search",
    description="Search the web for real-time information",
    # ... 技能配置
)

# 获取技能
retrieved_skill = client.skills.retrieve(skill.id)

# 列出技能
skills = client.skills.list()

# 技能版本管理
versions = client.skills.versions.list(skill.id)
specific_version = client.skills.versions.retrieve(skill.id, "v1")
```

SDK 在 `lib/tools/_skills.py` 中提供了 Skills 工具集成逻辑。创建 Agent 时，可以通过 `skills` 参数引用一个或多个技能，Agent 将自动获得这些技能提供的能力。

## Environments：沙箱执行环境

Environments 提供了**隔离的沙箱执行环境**，允许 Agent 在安全的环境中执行代码、运行命令、操作文件，而不会影响宿主系统。这是构建能够"动手做事"的 Agent 的基础设施。

### Environments 概念

- **环境（Environment）**：一个隔离的沙箱容器
- **Work（工作单元）**：在环境中执行的代码或命令

```python
from anthropic import Anthropic

client = Anthropic()

# 创建执行环境
env = client.beta.environments.create(
    # 环境配置：语言、依赖、资源限制等
)

# 在环境中执行代码（通过 work 子资源）
result = client.beta.environments.work.create(
    env.id,
    code="print('Hello from sandbox!')",
    language="python",
)
```

沙箱环境的典型用例：
- **代码执行**：Agent 编写并运行代码，验证结果
- **数据处理**：在沙箱中处理上传的数据文件
- **命令执行**：安全地运行 shell 命令
- **多步工作流**：在同一个环境中执行多步操作，保留文件系统状态

## Vaults：凭证管理

Vaults（保险库）提供了**安全的凭证存储和管理**能力，允许 Agent 安全地使用 API Key、密码、令牌等敏感信息，而无需将这些信息硬编码在工具定义或消息中。

```python
from anthropic import Anthropic

client = Anthropic()

# Vault 管理
vault = client.beta.vaults.create(
    name="my-secrets",
)

# 存储和检索凭证（凭证值在传输和存储中都加密）
# client.beta.vaults.secrets.create(...)
```

Vaults 解决了 Agent 使用外部工具时的凭证安全问题：
- 凭证加密存储，Anthropic 也无法明文查看
- Agent 调用工具时自动注入凭证，开发者无需在代码中处理
- 支持凭证轮换和访问审计
- 细粒度的权限控制：哪些 Agent 可以访问哪些凭证

## MCP 支持：Model Context Protocol

SDK 在 `lib/tools/mcp.py` 中提供了对 **MCP（Model Context Protocol）** 的支持。MCP 是一个开放协议，允许 AI 模型以标准化方式连接外部数据源和工具。

### MCP 的价值

MCP 类似于"AI 世界的 USB-C"，提供了统一的工具/数据源接入标准：
- 不需要为每个工具写定制化集成代码
- MCP 服务器可以用任何语言实现
- 支持动态发现工具能力
- 一个 MCP 服务器可以被多个 Agent/应用复用

在 Agents API 中，通过 `mcp_servers` 参数配置 Agent 可以连接的 MCP 服务器。

## Agent Toolset：2026-08-01 版浏览器/计算机工具集

SDK 在 `lib/tools/agent_toolset.py` 中定义了 Agent 工具集，包括：

- **Browser 工具**：允许 Agent 控制网页浏览器，进行网页导航、点击、输入、截图等操作
- **Computer 工具**：允许 Agent 控制计算机桌面，进行鼠标点击、键盘输入、屏幕截图等 GUI 操作

这组工具对应 `anthropic-beta` 头版本 `2026-08-01`，代表了 Anthropic 在 Computer Use（计算机使用）方向的持续演进——从早期的屏幕截图+简单操作，进化到完整的浏览器和桌面自动化能力。

```python
# 概念示例：使用 computer use 工具
# agent = client.beta.agents.create(
#     model="claude-3-5-sonnet-latest",
#     name="desktop-assistant",
#     tools=[{"type": "computer_20260801", ...}],  # 2026-08-01 版 computer 工具
# )
```

## Beta API 使用注意事项

### 1. 版本锁定

由于 Beta API 可能变更，生产环境使用时请锁定 SDK 版本：

```bash
# requirements.txt
anthropic==0.xx.x  # 锁定具体版本，不要使用 >= 或 ~=
```

### 2. 错误处理

Beta API 可能返回新的错误类型或状态码，建议捕获更宽泛的异常并做好降级：

```python
from anthropic import Anthropic, APIStatusError, AnthropicError

client = Anthropic()

try:
    agent = client.beta.agents.create(...)
except APIStatusError as e:
    if e.status_code == 404:
        # Beta 端点可能在版本更新时变化
        print("Beta endpoint not available, may have been updated")
    else:
        print(f"Beta API error {e.status_code}: {e.message}")
except AnthropicError as e:
    print(f"SDK error: {e}")
```

### 3. 功能开关

某些 Beta 功能可能需要单独申请白名单或开启账户设置，如果遇到权限错误（403），请检查 Anthropic 控制台的 Beta 功能访问权限。

### 4. 成本考量

托管 Agents、Memory Stores、Environments 等高级功能可能有额外的计费项（不仅是 token 费用），使用前请了解定价模型。

## 从 Tool Use 到完整 Agent 平台

回顾 SDK 的能力演进路径，可以清晰看到 Anthropic 的 Agent 平台路线图：

1. **Tool Use（基础工具调用）**：`@beta_tool` 装饰器 + ToolRunner，在客户端代码中运行工具
2. **MCP（标准化工具协议）**：统一的外部工具接入标准
3. **Skills（可复用技能包）**：工具+指令的版本化打包
4. **Memory（长期记忆）**：跨会话状态持久化
5. **Sessions（持久化会话）**：对话状态服务端管理
6. **Environments（沙箱执行）**：安全的代码运行环境
7. **Vaults（凭证管理）**：安全的密钥管理
8. **Agents（托管智能体）**：将以上所有能力组合成可复用、可版本化的托管实体

这代表了从"无状态 API 调用"到"有状态、有记忆、能行动、可托管的智能体平台"的演进。

## 相关概念

- [工具调用（Function Calling）](04-tool-use.md) — Beta Agents 能力的基础，理解 @beta_tool 装饰器和 ToolRunner
- [多云后端部署](07-multi-cloud.md) — Bedrock/Vertex 多云客户端同样支持 Beta API
- [中间件、扩展与错误处理](09-middleware-extended.md) — Beta API 调用同样需要完善的错误处理和中间件
- [Anthropic Python SDK 工具系统与 Beta API 参考](../references/tools-beta.md) — Beta 资源类和方法的完整 API 手册
