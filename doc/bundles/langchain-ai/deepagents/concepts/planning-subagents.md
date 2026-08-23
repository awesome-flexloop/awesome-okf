---
type: concept
scope: deepagents
name: planning-subagents
version: "0.7.8"
source: https://github.com/langchain-ai/deepagents
description: Deep Agents 子代理架构——上下文隔离、三种形态、task 工具与状态传播机制
---

# 规划与子代理

子代理是 Deep Agents 解决"长任务上下文污染"和"专业能力隔离"的核心机制。主代理通过 `task` 工具将任务委派给子代理，子代理在隔离的上下文窗口中自主完成多步骤工作，返回一条简洁的最终报告。

## 为什么需要子代理

在长周期代理任务中，主代理的上下文窗口会被工具输出、中间结果、错误重试填满。子代理解决两个问题：

1. **上下文隔离**：子代理只看到父代理传入的任务描述，其工具输出和中间工作不污染父代理上下文。父代理只收到最终报告。
2. **专业聚焦**：不同子代理可以有不同的工具集、系统提示和模型，专注于狭窄领域。安全敏感工具可以隔离在有审批门控的子代理中。

## task 工具

`SubAgentMiddleware` 向代理暴露一个 `task` 工具，其输入模式为：

```python
class TaskToolSchema(BaseModel):
    description: str  # 详细任务描述，包含所有必要上下文和期望输出格式
    subagent_type: str  # 子代理类型名，必须是可用类型之一
```

工具描述模板包含所有可用子代理的名称和描述列表（`{available_agents}` 占位符在运行时替换），指导模型：

- 独立任务可并发启动多个代理（单条消息含多个工具调用）
- 每次调用无状态：代理只看到传入的提示，返回单一最终报告
- 代理的报告不直接展示给用户，主代理需自行转述摘要
- 告诉代理是创建内容、分析还是仅研究

## 三种子代理形态

### 1. 声明式 SubAgent

```python
class SubAgent(TypedDict):
    name: str           # 必填：唯一标识符
    description: str    # 必填：做什么，主代理据此决定何时委派
    system_prompt: str  # 必填：子代理指令
    tools: NotRequired[Sequence]       # 可选：不指定则继承主代理工具
    model: NotRequired[str | BaseChatModel]  # 可选：覆盖模型
    middleware: NotRequired[list]      # 可选：额外中间件
    interrupt_on: NotRequired[dict]    # 可选：人工审批配置
    skills: NotRequired[list[str]]     # 可选：技能源路径
    permissions: NotRequired[list]     # 可选：文件权限（不指定则继承）
    response_format: NotRequired       # 可选：结构化输出格式
```

`create_deep_agent()` 在构造时为每个声明式 `SubAgent` 编译独立的代理，自动配备基础中间件栈（FilesystemMiddleware → SummarizationMiddleware → PatchToolCallsMiddleware → SkillsMiddleware → Profile middleware → PromptCaching）。

### 2. 预编译 CompiledSubAgent

```python
class CompiledSubAgent(TypedDict):
    name: str
    description: str
    runnable: Runnable  # 预编译的 create_agent() 或自定义 LangGraph 图
```

适用于需要完全自定义图结构的场景。`runnable` 的状态模式必须包含 `messages` 键，以将结果传回主代理。

`CompiledSubAgent` 不继承父代理的 `state_schema`、`middleware` 或 `interrupt_on`——这些需在编译 runnable 时自行配置。

### 3. 异步 AsyncSubAgent

```python
class AsyncSubAgent(TypedDict):
    name: str
    description: str
    graph_id: str              # 远程服务器上的图名/助手 ID
    url: NotRequired[str]      # Agent Protocol 服务器 URL
    headers: NotRequired[dict] # 自定义认证头
```

通过 LangGraph SDK 在远程 Agent Protocol 服务器上启动后台运行，立即返回 task ID。主代理可监控进度、发送更新、取消任务。兼容 LangGraph Platform（托管）和自托管服务器。

异步子代理通过 `AsyncSubAgentMiddleware` 暴露一组工具（启动/检查/更新/取消/列出任务），而非通过同步的 `task` 工具。

## 默认通用子代理

如果调用者未提供名为 `"general-purpose"` 的子代理，`create_deep_agent()` 自动添加一个（除非 HarnessProfile 禁用）：

```python
GENERAL_PURPOSE_SUBAGENT: SubAgent = {
    "name": "general-purpose",
    "description": "General-purpose agent for researching complex questions, "
                   "searching for files and content, and executing multi-step tasks...",
    "system_prompt": DEFAULT_SUBAGENT_PROMPT,
}
```

通用子代理继承主代理的模型和工具，拥有自己的中间件栈。它适用于复杂的上下文密集型搜索任务——当搜索关键词或文件且不确定前几次能找到正确匹配时，用它执行搜索。

禁用方式：

```python
from deepagents import create_deep_agent, GeneralPurposeSubagentProfile

agent = create_deep_agent(
    model=...,
    # 不传入任何同步子代理
    # 通过 profile 禁用默认通用子代理
)
```

当没有同步子代理（未传入且默认禁用）时，`task` 工具不暴露。异步子代理不受影响。

## 状态隔离与传播

### 传递给子代理的状态

调用子代理时，父代理状态被过滤后传入：

- 排除 `_EXCLUDED_STATE_KEYS = {"messages", "todos", "structured_response"}`
- 排除中间件私有状态字段（通过 `private_state_keys`）
- `messages` 被替换为仅包含 `HumanMessage(content=description)` 的单元素列表

这意味着子代理看到的是一个全新的对话，只有任务描述作为输入。

### 从子代理返回的状态

子代理完成后，结果通过 `Command(update=...)` 返回：

1. 从结果状态中排除 `messages`、`todos`、`structured_response` 和私有键
2. 响应内容确定优先级：
   - 如有 `structured_response`，通过 `model_dump_json()`（Pydantic）、`dataclasses.asdict()`（dataclass）或 `json.dumps()` 序列化
   - 否则回溯最后一条非空 `AIMessage` 文本（跳过 Anthropic 偶尔发出的尾随空 `end_turn` 消息）
3. 响应作为 `ToolMessage` 注入父代理状态

### 结构化输出

子代理支持 `response_format` 参数，可返回结构化数据而非自由文本：

```python
from pydantic import BaseModel

class Findings(BaseModel):
    findings: str
    confidence: float

analyzer: SubAgent = {
    "name": "analyzer",
    "description": "Analyzes data and returns structured findings",
    "system_prompt": "Analyze the data and return your findings.",
    "model": "openai:gpt-5.5",
    "tools": [],
    "response_format": Findings,
}
```

父代理通过 `ToolMessage` 收到 JSON 序列化的结构化响应。

## 权限继承

子代理的文件权限规则：

- 声明式 `SubAgent` 不指定 `permissions` 时，继承父代理的权限规则
- 指定了 `permissions` 时，**完全替换**（非合并）父代理规则
- `CompiledSubAgent` 和 `AsyncSubAgent` 不继承父代理权限

权限规则按声明顺序求值，首匹配优先。`mode` 可为 `"allow"`、`"deny"`、`"interrupt"`。

## 安全设计模式

lca-deepagents 的 Sales Assistant 示例展示了一个关键安全模式：**受审批控制的工具应仅放在有门控的专业子代理上，绝不放在主代理上**。

原因：通用子代理继承主代理的工具集。如果主代理有 `add_customer` 工具，模型可以通过 `task` 委派给通用子代理来调用它，从而绕过主代理上的人工审批门控。将敏感工具仅放在配置了 `interrupt_on` 的专业子代理上，确保访问这些工具的唯一路径经过审批。

## 相关概念

- [总览](/langchain-ai/deepagents/concepts/overview) — Deep Agents 整体架构
- [Todo 与上下文管理](/langchain-ai/deepagents/concepts/todo-context) — 摘要压缩如何与子代理协作
- [中间件栈](/langchain-ai/deepagents/references/middleware-stack) — 子代理中间件的组装细节
- [lca-deepagents 示例](/langchain-ai/deepagents/examples/lca-variant) — 子代理安全模式的实际应用
