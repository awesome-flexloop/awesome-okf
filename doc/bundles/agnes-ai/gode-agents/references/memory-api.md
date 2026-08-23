---
type: Reference
title: Memory API 参考
description: codified-smolagents 内存管理与数据类型API参考，包含AgentMemory、MemoryStep体系、ToolCall、AgentType类型系统
tags: [Memory, AgentMemory, MemoryStep, ToolCall, AgentType, AgentImage, API参考]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T22:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T22:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: memory-source
    resource: ../../../../../../external/libs/models/AgnesAI/GodeAgents/Multi-Agent-Task/src/codified-smolagents/memory.py
    title: codified-smolagents/memory.py
  - id: agent-types-source
    resource: ../../../../../../external/libs/models/AgnesAI/GodeAgents/Multi-Agent-Task/src/codified-smolagents/agent_types.py
    title: codified-smolagents/agent_types.py
---

# Memory API 参考

本文件记录 `memory.py` 和 `agent_types.py` 模块中的内存管理体系和数据类型，基于源码零推测事实 F-082 ~ F-104。

## 概述

内存系统记录智能体执行过程中的完整交互历史，采用步骤（MemoryStep）序列的形式组织。每一步包含模型输入输出、工具调用、观察结果、错误信息等。系统还定义了AgentText、AgentImage、AgentAudio等多模态数据类型，用于统一处理不同类型的智能体输入输出。

> 事实溯源：F-084、F-092、F-097

## 基础类型定义

### Message

```python
class Message(TypedDict):
    role: MessageRole
    content: str | list[dict]
```

消息类型字典，用于LLM交互的消息格式。`role` 使用MessageRole枚举值，`content` 为纯文本字符串或多模态内容列表（含type字段的字典列表）。

> 事实溯源：F-083

### ToolCall

```python
@dataclass
class ToolCall:
    name: str
    arguments: Any
    id: str
```

工具调用记录数据类。

**字段：**
- `name` (`str`): 工具名称
- `arguments` (`Any`): 工具调用参数（通常为字典）
- `id` (`str`): 工具调用唯一标识符

**方法：**
- `dict() -> dict`: 转换为OpenAI格式的function call字典：`{"id": ..., "type": "function", "function": {"name": ..., "arguments": ...}}`，arguments通过`make_json_serializable`递归序列化

> 事实溯源：F-082

## MemoryStep 基类

```python
@dataclass
class MemoryStep
```

所有内存步骤的基类。

**方法：**
- `dict() -> dict`: 使用`asdict()`转换为字典（子类可重写以自定义序列化）
- `to_messages(**kwargs) -> List[Dict[str, Any]]`: 抽象方法，将步骤转换为消息列表，子类必须实现

> 事实溯源：F-084

## MemoryStep 子类

### SystemPromptStep

```python
@dataclass
class SystemPromptStep(MemoryStep):
    system_prompt: str
```

系统提示词步骤。

**to_messages行为：**
- 非摘要模式：返回1条system角色消息，内容为system_prompt
- 摘要模式（summary_mode=True）：返回空列表

> 事实溯源：F-085

### TaskStep

```python
@dataclass
class TaskStep(MemoryStep):
    task: str
    task_images: list | None = None
```

任务步骤，记录用户提交的任务。

**字段：**
- `task` (`str`): 任务描述文本
- `task_images` (`list | None`): 任务附带的图像列表

**to_messages行为：** 返回1条user角色消息，内容以"New task:\n"开头，包含任务文本和可选图像。

> 事实溯源：F-086

### ActionStep

```python
@dataclass
class ActionStep(MemoryStep):
    model_input_messages: List[Message] | None = None
    tool_calls: List[ToolCall] | None = None
    start_time: float | None = None
    end_time: float | None = None
    step_number: int | None = None
    error: AgentError | None = None
    duration: float | None = None
    model_output_message: ChatMessage = None
    model_output: str | None = None
    observations: str | None = None
    observations_images: List["PIL.Image.Image"] | None = None
    action_output: Any = None
```

行动步骤，记录每一步ReAct循环的完整信息。这是最核心的步骤类型。

**字段：**
- `model_input_messages`: 发送给模型的输入消息
- `tool_calls`: 工具调用列表
- `start_time` / `end_time`: 步骤开始/结束时间戳
- `step_number`: 步骤编号
- `error`: 执行过程中的错误
- `duration`: 步骤执行时长（秒）
- `model_output_message`: 模型返回的ChatMessage对象
- `model_output`: 模型输出文本
- `observations`: 工具执行观察结果文本
- `observations_images`: 观察结果中的图像
- `action_output`: 行动输出结果

**to_messages输出顺序：**
1. （可选，show_model_input_messages=True时）模型输入消息（system角色）
2. （非摘要模式）模型输出（assistant角色）
3. 工具调用信息（tool-call角色），格式为"Calling tools:\n[{tool_call_dict}, ...]"
4. 观察图像（user角色），每个图像一条消息
5. 观察文本（tool-response角色），格式为"Observation:\n{observations}"
6. 错误信息（tool-response角色），包含错误消息和重试提示

> 事实溯源：F-087、F-088

### PlanningStep

```python
@dataclass
class PlanningStep(MemoryStep):
    model_input_messages: List[Message]
    model_output_message: ChatMessage
    plan: str
```

规划步骤，记录智能体的规划过程。

**字段：**
- `model_input_messages`: 规划输入消息
- `model_output_message`: 模型返回的规划响应
- `plan` (`str`): 生成的计划文本

**to_messages行为：**
- 非摘要模式：返回2条消息
  1. assistant角色：计划内容
  2. user角色："Now proceed and carry out this plan."（强制角色切换，防止模型续写计划）
- 摘要模式：返回空列表

> 事实溯源：F-089、F-090

### FinalAnswerStep

```python
@dataclass
class FinalAnswerStep(MemoryStep):
    final_answer: Any
```

最终回答步骤，标记任务完成。

**字段：**
- `final_answer` (`Any`): 最终答案值（经`handle_agent_output_types`转换为AgentType）

> 事实溯源：F-091

## AgentMemory

```python
class AgentMemory
```

智能体内存管理器，维护系统提示词和步骤序列。

> 事实溯源：F-092

### 构造函数

```python
def __init__(self, system_prompt: str)
```

初始化内存。创建SystemPromptStep实例，steps列表初始为空。

**属性：**
- `system_prompt` (`SystemPromptStep`): 系统提示词步骤
- `steps` (`List[Union[TaskStep, ActionStep, PlanningStep]]`): 执行步骤序列

### 核心方法

#### reset

```python
def reset(self)
```

清空步骤列表（steps重置为空列表），不重置system_prompt。

> 事实溯源：F-093

#### get_succinct_steps

```python
def get_succinct_steps(self) -> list[dict]
```

返回精简步骤列表，排除 `model_input_messages` 字段以减小体积。

> 事实溯源：F-094

#### get_full_steps

```python
def get_full_steps(self) -> list[dict]
```

返回完整步骤列表（包含model_input_messages）。

> 事实溯源：F-095

#### replay

```python
def replay(self, logger: AgentLogger, detailed: bool = False)
```

使用logger美观地回放智能体执行步骤。`detailed=True`时额外显示每步的模型输入消息（会显著增加日志长度，仅用于调试）。

> 事实溯源：F-096

## AgentType 类型系统

### AgentType

```python
class AgentType
```

智能体数据类型基类，用于统一处理不同模态的输入输出。

**构造函数：**
```python
def __init__(self, value)
```
存储原始值为 `self._value`。

**方法：**
- `to_raw(self)`: 返回原始值（如PIL.Image.Image）
- `to_string(self) -> str`: 转换为字符串表示（子类实现，默认抛出NotImplementedError）

> 事实溯源：F-097~F-099

### AgentText

```python
class AgentText(AgentType)
```

文本数据类型。`to_string()` 直接返回字符串值。

> 事实溯源：F-100

### AgentImage

```python
class AgentImage(AgentType, PIL.Image.Image)
```

图像数据类型，支持多种输入格式：PIL.Image.Image、字节数据、文件路径、张量。

**方法：**
- `to_string(self) -> str`: 返回图像文件路径（自动保存为PNG临时文件）
- `save_to_file(self, path, format="png")`: 保存图像到文件
- `to_raw(self)`: 返回原始PIL图像对象

> 事实溯源：F-101

### AgentAudio

```python
class AgentAudio(AgentType)
```

音频数据类型，支持音频路径和音频数据输入。

**方法：**
- `to_string(self) -> str`: 返回音频文件路径（自动保存为文件）
- `save_to_file(self, path)`: 保存音频到文件

> 事实溯源：F-102

### 类型处理函数

#### handle_agent_input_types

```python
def handle_agent_input_types(tool_name, arguments, state)
```

处理工具输入中的AgentImage/AgentAudio类型，将它们转换为文件路径。

> 事实溯源：F-103

#### handle_agent_output_types

```python
def handle_agent_output_types(output, observations_images=None)
```

将工具输出转换为适当的AgentType子类实例（AgentText、AgentImage、AgentAudio）。

> 事实溯源：F-104

## 相关概念

- [智能体内存系统](/concepts/memory-system.md) — 步骤序列与消息转换机制
- [智能体执行循环](/concepts/agent-execution-loop.md) — ReAct循环中ActionStep的生命周期
- [多模态数据处理](/concepts/multimodal-types.md) — AgentType类型系统与多模态支持
- [智能体API参考](/references/agents-api.md) — MultiStepAgent如何使用AgentMemory
- [工具API参考](/references/tools-api.md) — 工具调用与AgentType的关系
