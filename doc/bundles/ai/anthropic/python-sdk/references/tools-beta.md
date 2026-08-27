---
type: reference
title: "Anthropic Python SDK 工具系统与 Beta API 参考"
description: "Function Calling 工具定义、beta_tool 装饰器、ToolRunner 工具运行器、Beta 命名空间（Agents/Memory/Sessions/Skills/Environments/Vaults）的完整 API 参考。"
tags: [tools, function-calling, beta, agents, memory, sessions, skills]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-038~F-058
    resource: /python-sdk/references/tools-beta.md
    title: "Anthropic Python SDK 工具系统与 Beta API 参考"
---

# Anthropic Python SDK 工具系统与 Beta API 参考

本文档登记 Function Calling（函数调用）工具系统核心类、工具装饰器、ToolRunner 运行器，以及 Beta 命名空间下的实验性 API（Agents、Memory Stores、Sessions、Skills、Environments、Vaults 等）。

> ⚠️ **实验性 API 提示**：所有通过 `client.beta` 访问的 API 均为实验性功能，可能在未来版本中发生破坏性变更。使用时需添加对应的 `anthropic-beta` 请求头，SDK 会自动处理。

## Function Tools 核心类

工具系统定义在 `anthropic.lib.tools` 模块下。

### ToolError

**类路径**：`anthropic.lib.tools.ToolError`

工具执行错误异常类，继承自 `Exception`：

```python
class ToolError(Exception):
    content: BetaFunctionToolResultType
```

当工具执行失败时抛出，`content` 属性包含工具返回的错误结果内容。

### BetaBuiltinFunctionTool（抽象基类）

**类路径**：`anthropic.lib.tools.BetaBuiltinFunctionTool`

内置工具的抽象基类，定义了内置工具必须实现的接口：

| 方法 | 签名 | 说明 |
|------|------|------|
| `to_dict()` | `() -> dict` | 抽象方法，将工具转换为 API 请求所需的字典格式 |
| `call()` | `(input: object) -> object` | 抽象方法，执行工具逻辑 |

### BaseFunctionTool（泛型基类）

**类路径**：`anthropic.lib.tools.BaseFunctionTool[CallableT]`

函数工具的泛型基类，封装普通 Python 函数为可被 LLM 调用的工具：

| 属性 | 类型 | 说明 |
|------|------|------|
| `func` | `CallableT` | 原始 Python 函数 |
| `name` | `str` | 工具名称 |
| `description` | `str` | 工具描述（提供给 LLM） |
| `input_schema` | `dict` | JSON Schema 格式的输入参数定义 |
| `close` | `Callable[[], None] \| None` | 可选的清理函数 |

### BetaFunctionTool（同步函数工具）

**类路径**：`anthropic.lib.tools.BetaFunctionTool[FunctionT]`

继承自 `BaseFunctionTool[FunctionT]`，同步函数工具包装类：

```python
class BetaFunctionTool(BaseFunctionTool[FunctionT]):
    def call(self, input: object) -> object:
        ...
```

### BetaAsyncFunctionTool（异步函数工具）

**类路径**：`anthropic.lib.tools.BetaAsyncFunctionTool[AsyncFunctionT]`

继承自 `BaseFunctionTool[AsyncFunctionT]`，异步函数工具包装类：

```python
class BetaAsyncFunctionTool(BaseFunctionTool[AsyncFunctionT]):
    async def call(self, input: object) -> object:
        ...
```

### 工具类型别名

```python
BetaRunnableTool = Union[BetaFunctionTool[Any], BetaBuiltinFunctionTool]
```

可运行工具类型，可以是包装后的函数工具或内置工具。

## 工具装饰器

### @beta_tool

**类路径**：`anthropic.lib.tools.beta_tool`

同步函数工具装饰器，支持带参数和不带参数两种用法，将普通 Python 函数自动包装为 `BetaFunctionTool` 实例。

**用法示例**：

```python
from anthropic.lib.tools import beta_tool

# 不带参数
@beta_tool
def get_weather(location: str) -> str:
    """获取指定地点的天气"""
    return f"Weather in {location}: Sunny"

# 带参数（自定义名称/描述）
@beta_tool(name="fetch_weather", description="查询天气信息")
def get_weather(location: str, unit: str = "celsius") -> str:
    ...
```

### @beta_async_tool

**类路径**：`anthropic.lib.tools.beta_async_tool`

异步函数工具装饰器，将异步 Python 函数包装为 `BetaAsyncFunctionTool` 实例。

**用法示例**：

```python
from anthropic.lib.tools import beta_async_tool

@beta_async_tool
async def fetch_data(url: str) -> dict:
    """异步获取数据"""
    ...
```

## ToolRunner 工具运行器

### BaseToolRunner

**类路径**：`anthropic.lib.tools.BaseToolRunner[AnyFunctionToolT, ResponseFormatT]`

工具运行器泛型基类，负责自动处理多轮工具调用循环：

| 属性 | 类型 | 说明 |
|------|------|------|
| `_tools_by_name` | `dict[str, BetaRunnableTool]` | 工具名称到工具实例的映射 |
| `_params` | `dict` | API 请求参数 |
| `_options` | `RequestOptions \| None` | 请求选项 |
| `_max_iterations` | `int` | 最大工具调用轮次 |
| `_iteration_count` | `int` | 当前迭代计数 |

### 停止原因映射

`_STOP_REASON_STEPS` 字典定义了停止原因到下一步动作的映射：

| StopReason | 下一步动作 | 说明 |
|------------|-----------|------|
| `"tool_use"` | `"run_tools"` | 需要执行工具，继续循环 |
| `"end_turn"` | `"stop"` | 对话结束，停止循环 |
| `"max_tokens"` | `"stop"` | 达到 token 上限，停止循环 |

### 核心方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `append_messages()` | `(*messages: BetaMessageParam \| ParsedBetaMessage) -> None` | 向消息历史追加消息，支持 BetaMessageParam 或解析后的消息类型 |

## lib/tools 模块索引

`lib/tools/` 目录包含以下工具相关模块：

| 模块文件 | 说明 |
|---------|------|
| `_beta_functions.py` | BetaFunctionTool、BetaAsyncFunctionTool、beta_tool/beta_async_tool 装饰器、ToolError |
| `_beta_runner.py` | BaseToolRunner 工具运行器基类、停止原因映射逻辑 |
| `_beta_builtin_memory_tool.py` | 内置 Memory 工具实现 |
| `mcp.py` | MCP（Model Context Protocol）工具集成 |
| `agent_toolset.py` | Agent 工具集定义 |
| `_tool_dispatch.py` | 工具分发逻辑 |
| `_skills.py` | Skills（技能）工具集成 |
| `_memories.py` | Memories（记忆）工具集成 |
| `_file_store.py` | 文件存储工具集成 |

## Beta API 命名空间

### Beta 资源类

**类路径**：`anthropic.resources.beta.Beta`

`Beta` 类继承自 `SyncAPIResource`，定义在 `resources/beta/beta.py`，是所有实验性 API 的入口。通过 `client.beta` 懒加载访问。

### Beta 子资源属性

`Beta` 类通过 `@cached_property` 定义以下子资源属性：

| 属性 | 资源类 | 说明 |
|------|--------|------|
| `.agents` | `Agents` | Agents（智能体）管理资源 |
| `.sessions` | `Sessions` | Sessions（会话）资源 |
| `.memory_stores` | `MemoryStores` | Memory Stores（记忆存储）资源 |
| `.skills` | `Skills` | Skills（技能）资源 |
| `.environments` | `Environments` | Environments（环境）资源 |
| `.vaults` | `Vaults` | Vaults（保险库）资源 |
| `.deployments` | `Deployments` | Deployments（部署）资源 |
| `.dreams` | `Dreams` | Dreams 资源 |
| `.tunnels` | `Tunnels` | Tunnels（隧道）资源 |
| `.organization` | `Organization` | Organization（组织）资源 |
| `.webhooks` | `Webhooks` | Webhooks 资源 |
| `.user_profiles` | `UserProfiles` | 用户配置资源 |
| `.models` | `Models` | Beta 模型资源 |
| `.messages` | `Messages` | Beta 消息资源（含 batches） |
| `.files` | `Files` | Beta 文件资源 |

> 异步版本为 `AsyncBeta`，所有子资源均有对应的异步版本。

## Agents 资源

**类路径**：`anthropic.resources.beta.agents.Agents`

`Agents` 类继承自 `SyncAPIResource`，用于管理 Managed Agents（托管智能体）：

| 属性 | 说明 |
|------|------|
| `.versions` | Versions 子资源，管理 Agent 版本 |

### Agents.create 方法

```python
Agents.create(
    *,
    model: agent_create_params.Model,
    name: str,
    description: str | NotGiven = ...,
    mcp_servers: Iterable[McpServerParam] | NotGiven = ...,
    metadata: MetadataParam | NotGiven = ...,
    multiagent: MultiagentParam | NotGiven | None = ...,
    skills: Iterable[SkillParam] | NotGiven = ...,
    system: str | Iterable[SystemMessageParam] | NotGiven = ...,
    tools: Iterable[ToolParam] | NotGiven = ...,
    betas: Iterable[str] | NotGiven = ...,
    # + extra kwargs
) -> Agent
```

**必填参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `model` | `agent_create_params.Model` | Agent 使用的模型 |
| `name` | `str` | Agent 名称 |

**可选参数**：`description`、`mcp_servers`、`metadata`、`multiagent`、`skills`、`system`、`tools`、`betas`。

**请求细节**：
- HTTP 方法：`POST`
- 端点：`"/v1/agents?beta=true"`
- 自动添加请求头：`"anthropic-beta": "managed-agents-2026-04-01"`

## 其他 Beta 子资源概览

### Memory Stores

通过 `client.beta.memory_stores` 访问，包含以下子资源：
- `memories`：记忆条目管理
- `memory_versions`：记忆版本管理

### Sessions

通过 `client.beta.sessions` 访问，包含以下子资源：
- `threads`：会话线程
- `events`：会话事件
- `resources`：会话资源

### Skills

通过 `client.beta.skills` 访问，包含 `versions` 子资源用于技能版本管理。

### Environments / Vaults

通过 `client.beta.environments` 和 `client.beta.vaults` 访问，分别用于环境管理和安全存储。
