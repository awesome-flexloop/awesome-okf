---
type: Concept
title: ToolCallingAgent：函数调用范式
description: ToolCallingAgent基于JSON function calling的工具调用机制、step流程、状态变量替换
tags: [智能体, ToolCallingAgent, 工具调用, Function Calling]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:20:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: F-032
    resource: /references/agents-api.md
    title: Agents API 参考
---

# ToolCallingAgent：函数调用范式

## 概述

`ToolCallingAgent` 是 GodeAgents 提供的两种核心智能体类型之一，继承自 `MultiStepAgent`，实现了基于 LLM 原生 **function calling（函数调用）** API 的工具调用范式。它的核心思想是：将工具列表以 JSON Schema 格式传递给模型，由模型决定调用哪个工具、传入什么参数，框架负责解析模型返回的结构化工具调用并执行，将观察结果反馈给模型继续推理。

与 CodeAgent 使用 Python 代码块作为"行动语言"不同，ToolCallingAgent 的每一步只能调用一个工具，参数为 JSON 格式，更适合精确的工具参数控制场景。

> 事实溯源：F-032~F-038

## 核心概念

### Function Calling 范式

Function calling 是现代 LLM 的一项原生能力：模型不仅能生成文本，还能输出结构化的工具调用请求（包含工具名和 JSON 格式参数）。ToolCallingAgent 充分利用这一能力，通过 `tools_to_call_from` 参数将可用工具的 JSON Schema 传给模型，模型返回 `tool_calls` 结构，框架负责解析和执行。

### 单步单工具

ToolCallingAgent 的每一步（step）只解析 `model_message.tool_calls[0]`，即一次只调用一个工具。如果需要组合多个工具，模型需要在多步中依次调用——这保证了每一步的简单可追踪，但在复杂组合场景下可能不如 CodeAgent 灵活。

### 状态变量替换

`_substitute_state_variables()` 方法实现了一个轻量级的状态传递机制：当工具参数值是字符串，且该字符串恰好是 `self.state` 字典中的键时，自动将其替换为 state 中对应的值。这使得工具调用可以引用之前步骤中存储的数据。

## API 要点

### 构造参数

ToolCallingAgent 继承 MultiStepAgent 的所有参数，自身 `__init__` 签名为：

```python
ToolCallingAgent(
    tools: List[Tool],
    model: Model,
    prompt_templates: Optional[PromptTemplates] = None,
    planning_interval: Optional[int] = None,
    **kwargs,  # 传递给MultiStepAgent构造器
)
```

| 参数 | 说明 |
|------|------|
| `tools` | 工具列表，框架自动注入 `final_answer` |
| `model` | Model 子类实例，需支持 function calling |
| `prompt_templates` | 自定义提示模板，默认从 `toolcalling_agent.yaml` 读取 |
| `planning_interval` | 规划间隔步数 |
| `**kwargs` | 传递给 MultiStepAgent 的其他参数（max_steps、verbosity_level 等） |

> 事实溯源：F-033

### 默认提示模板

ToolCallingAgent 默认从 `toolcalling_agent.yaml` 读取提示模板。模板中指示模型使用 JSON 格式输出工具调用，而非 Python 代码块。

> 事实溯源：F-034

### initialize_system_prompt()

```python
def initialize_system_prompt(self) -> str
```

渲染 system_prompt 时传入两个模板变量：
- `tools`：可用工具列表的描述
- `managed_agents`：被管理子 Agent 列表的描述

> 事实溯源：F-035

### step() 核心流程

```python
def step(self, memory_step: ActionStep) -> Union[None, Any]
```

step() 方法执行以下流程：

1. **调用模型**：将记忆序列化为消息列表，调用 `model(messages, tools_to_call_from=list(self.tools.values()), stop_sequences=["Observation:", "Calling tools:"])`
2. **解析工具调用**：从返回的 `model_message.tool_calls[0]` 中提取 `tool_name`、`tool_call_id`、`tool_arguments`
3. **判断终止**：若工具是 `final_answer`，直接返回答案作为 final_answer
4. **执行工具**：调用 `execute_tool_call(tool_name, tool_arguments)` 执行工具
5. **记录观察**：将工具返回值作为观察结果记录到 memory_step，返回 None 继续循环

关键参数：
- `tools_to_call_from=list(self.tools.values())`：将所有工具转为 JSON Schema 传给模型
- `stop_sequences=["Observation:", "Calling tools:"]`：告诉模型在生成这些序列时停止，防止模型"编造"观察结果

> 事实溯源：F-036

### execute_tool_call()：工具执行与异常处理

```python
def execute_tool_call(self, tool_name: str, arguments: Union[Dict[str, str], str]) -> Any
```

执行流程：

1. **查找工具**：在合并字典 `{**self.tools, **self.managed_agents}` 中按名称查找工具或子 Agent
2. **替换状态变量**：调用 `_substitute_state_variables(arguments)` 替换 state 中的变量引用
3. **调用工具**：传入替换后的参数调用工具/子 Agent
4. **异常处理**：
   - `TypeError` → 抛出 `AgentToolCallError`（参数类型错误等调用层面问题）
   - 其他异常 → 抛出 `AgentToolExecutionError`（执行过程中的错误）

> 事实溯源：F-038

### _substitute_state_variables()：状态变量替换

```python
def _substitute_state_variables(self, arguments: Any) -> Any
```

递归遍历参数字典/列表，对每个值：
- 如果值是**字符串**且该字符串**恰好是** `self.state` 字典中的键 → 替换为 `self.state[键]` 的值
- 其他情况保持不变

这允许 Agent 在工具调用中通过字符串引用之前步骤存储在 state 中的数据，例如将上一步搜索结果的引用键作为参数传给下一步的工具。

> 事实溯源：F-037

### add_base_tools 行为

当 `add_base_tools=True` 时，ToolCallingAgent 添加 `TOOL_MAPPING` 中除 `python_interpreter` 外的所有默认工具（web_search、visit_webpage、search_wikipedia），同时 **保留** `python_interpreter` 工具——这是 ToolCallingAgent 与 CodeAgent 的区别之一：ToolCallingAgent 默认包含 Python 解释器工具，CodeAgent 则通过代码执行器内置 Python 能力。

> 事实溯源：F-018、F-125

## 代码示例

### 创建基础 ToolCallingAgent

```python
from codified_smolagents import ToolCallingAgent, DuckDuckGoSearchTool, HfApiModel

# 初始化模型（需支持function calling）
model = HfApiModel()

# 创建带搜索工具的ToolCallingAgent
agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    max_steps=10,
    verbosity_level=2,
)

# 运行任务
result = agent.run("Python 3.12 有哪些主要新特性？")
print(result)
```

### 多工具组合

```python
from codified_smolagents import (
    ToolCallingAgent,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    WikipediaSearchTool,
    HfApiModel,
)

model = HfApiModel()

# 组合搜索、网页访问和维基百科工具
agent = ToolCallingAgent(
    tools=[
        DuckDuckGoSearchTool(),
        VisitWebpageTool(),
        WikipediaSearchTool(),
    ],
    model=model,
    max_steps=15,
    planning_interval=3,
)

# Agent会自动选择合适的工具
result = agent.run("什么是Transformer架构？它的核心注意力机制是如何工作的？")
print(result)
```

### 使用 add_base_tools 加载默认工具

```python
from codified_smolagents import ToolCallingAgent, HfApiModel

model = HfApiModel()

# add_base_tools=True 自动加载web_search、visit_webpage、search_wikipedia、python_interpreter
agent = ToolCallingAgent(
    tools=[],  # 空列表，基础工具自动添加
    model=model,
    add_base_tools=True,
    max_steps=10,
)

result = agent.run("搜索Python 3.12的新特性，然后用Python解释器计算2的20次方")
print(result)
```

### 利用 state 传递状态变量

```python
from codified_smolagents import ToolCallingAgent, tool, HfApiModel

model = HfApiModel()

@tool
def store_value(key: str, value: str) -> str:
    """存储一个键值对到agent状态中。

    Args:
        key: 存储的键名
        value: 要存储的值

    Returns:
        存储确认信息
    """
    return f"已存储 {key}={value}"

@tool
def recall_value(key: str) -> str:
    """从agent状态中读取一个值。

    Args:
        key: 要读取的键名

    Returns:
        键对应的值
    """
    return f"读取 {key}"

agent = ToolCallingAgent(
    tools=[store_value, recall_value],
    model=model,
    max_steps=5,
)

# Agent可以通过state字典在工具间传递数据
# 当工具参数值恰好匹配state中的键时，_substitute_state_variables会自动替换
result = agent.run("先存储一个值my_key=hello，然后读取它")
print(result)
```

> 事实溯源：F-032~F-038、F-018

### step() 执行流程图

```mermaid
sequenceDiagram
    participant Loop as _run()循环
    participant Step as step()
    participant Mem as write_memory_to_messages()
    participant Model as Model
    participant Exec as execute_tool_call()
    participant Tool as Tool/ManagedAgent

    Loop->>Step: step(memory_step)
    Step->>Mem: 序列化记忆为消息列表
    Mem-->>Step: messages
    Step->>Model: model(messages, tools_to_call_from=tools.values(),<br/>stop_sequences=["Observation:", "Calling tools:"])
    Model-->>Step: ChatMessage(tool_calls=[...])
    Step->>Step: 解析tool_calls[0]:<br/>tool_name, tool_call_id, tool_arguments

    alt tool_name == "final_answer"
        Step-->>Loop: 返回final_answer(任务完成)
    else 普通工具
        Step->>Exec: execute_tool_call(tool_name, arguments)
        Exec->>Exec: _substitute_state_variables(arguments)
        Exec->>Tool: 在{**tools, **managed_agents}中查找并调用
        alt TypeError
            Tool-->>Exec: 抛出TypeError
            Exec-->>Step: 抛出AgentToolCallError
        else 其他异常
            Tool-->>Exec: 抛出异常
            Exec-->>Step: 抛出AgentToolExecutionError
        else 成功
            Tool-->>Exec: 返回observation
            Exec-->>Step: 返回observation
        end
        Step->>Step: 记录observation到memory_step
        Step-->>Loop: 返回None(继续循环)
    end
```

> 事实溯源：F-036~F-038

## 常见问题/注意事项

### 模型必须支持 function calling

ToolCallingAgent 依赖模型的原生 function calling 能力（通过 `tools_to_call_from` 参数传递工具 Schema）。使用不支持 function calling 的模型会导致无法正确解析工具调用，此时应考虑使用 CodeAgent 或通过 LiteLLMModel 等适配层。

### 每步只能调用一个工具

`tool_calls[0]` 的硬编码意味着每步只能执行一个工具调用。如果需要在一个"思考步"中并行调用多个工具（如同时搜索多个查询），ToolCallingAgent 无法原生支持，需要多步串行完成。CodeAgent 在这方面更灵活——一个代码块中可以调用任意数量的工具。

### stop_sequences 的作用

`stop_sequences=["Observation:", "Calling tools:"]` 是关键设计：
- `"Observation:"`：防止模型在生成工具调用后"自问自答"编造观察结果
- `"Calling tools:"`：确保模型在输出工具调用格式后停止，由框架填充实际观察

### 状态变量替换是精确匹配

`_substitute_state_variables` 只替换参数值**完全等于** state 键名的字符串。例如 state 中有 `{"result": "42"}`，工具参数 `{"x": "result"}` 会被替换为 `{"x": "42"}`，但 `{"x": "the result is"}` 不会被替换。这是设计上的简洁取舍，避免意外替换。

### python_interpreter 工具的特殊地位

与 CodeAgent 不同，ToolCallingAgent 在 `add_base_tools=True` 时保留 `python_interpreter` 工具。这意味着 ToolCallingAgent 可以像调用其他工具一样调用 Python 解释器执行计算，但每次执行是独立的（不像 CodeAgent 的执行器保持 state 连续性）。

### 与 CodeAgent 的选择指南

| 场景 | 推荐 |
|------|------|
| 需要精确控制工具参数（JSON格式） | ToolCallingAgent |
| 模型原生支持 function calling 且效果好 | ToolCallingAgent |
| 工具调用链简单（每步一个工具） | ToolCallingAgent |
| 需要在代码中组合多工具、变量、循环 | CodeAgent |
| 复杂数学计算/数据处理 | CodeAgent |
| 模型不支持 function calling | CodeAgent |

## 相关链接

- [MultiStepAgent：核心推理循环](/concepts/03-multi-step-agent.md) — 父类的run循环和step抽象
- [CodeAgent：代码执行范式](/concepts/06-code-agent.md) — 另一种智能体范式（CodeAct）
- [工具系统：@tool装饰器与Tool基类](/concepts/07-tool-system.md) — 如何开发自定义工具
- [内置工具详解](/concepts/08-builtin-tools.md) — 默认工具的功能与用法
- [Agents API 参考](/references/agents-api.md) — ToolCallingAgent完整API
- [Models API 参考](/references/models-api.md) — 模型function calling接口
