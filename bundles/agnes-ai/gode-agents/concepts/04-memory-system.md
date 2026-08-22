---
type: Concept
title: 记忆系统：步骤序列
description: AgentMemory的MemoryStep序列设计、ActionStep/PlanningStep消息序列化
tags: [记忆, Memory, 步骤序列]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: F-084
    resource: /references/memory-api.md
    title: Memory API 参考
---

# 记忆系统：步骤序列

## 概述

GodeAgents 的记忆设计与大多数 Agent 框架不同：**记忆不是键值存储，也不是向量数据库，而是一个 MemoryStep 的时序列表**。Agent 的全部记忆就是从任务开始到结束的每一个步骤的有序记录。每个步骤是一个不可变的数据类实例，知道如何将自己序列化为发给 LLM 的消息列表（通过 `to_messages()` 方法）。这种 append-only 的设计确保了零信息损失、可审计可回放、实现极简。

> 事实溯源：F-084、F-092~F-096

## 核心概念

### 记忆即序列

传统 Agent 框架的记忆通常分层管理：短期记忆（最近 N 轮）、长期记忆（向量检索）、工作记忆（当前变量）。GodeAgents 选择了更朴素的路线：**把所有交互步骤按顺序存下来**，每一步 LLM 看到什么输入、产生了什么输出、调用了什么工具、得到了什么观察，全部记录在案。LLM 的上下文窗口本身就是"遗忘机制"——步骤太多超出窗口时自然截断。

### 每个Step自序列化

核心设计原则：**每个 MemoryStep 自己决定如何呈现为 LLM 消息**。通过 `to_messages(summary_mode=False)` 方法，每个步骤类型输出自己对应的消息序列，外部不需要 if-else 判断步骤类型。

### 消息序列即对话历史

发给 LLM 的消息列表就是记忆序列化的结果。一次完整执行的消息序列结构为：

```
[SystemPrompt] → [Task] → [PlanningStep(可选)] → [ActionStep1] → [ActionStep2] → ... → [FinalAnswer]
```

每个 ActionStep 内部又包含：模型输出(assistant) → 工具调用(tool-call) → 观察(user/tool-response) → 错误(tool-response)。

## API 要点

### MemoryStep 类层次

```
MemoryStep（基类：定义dict()和to_messages()）
├── SystemPromptStep    — 系统提示词
├── TaskStep            — 用户任务+图片
├── ActionStep          — 完整一步推理记录（核心）
├── PlanningStep        — 规划输出
└── FinalAnswerStep     — 最终答案
```

> 事实溯源：F-084~F-091

### MemoryStep 基类

```python
class MemoryStep:
    def dict(self) -> dict: ...        # 序列化为字典
    def to_messages(self, **kwargs) -> List[Dict[str, Any]]: ...  # 抽象方法，子类实现
```

### SystemPromptStep

```python
@dataclass
class SystemPromptStep(MemoryStep):
    system_prompt: str
```

- 始终位于记忆序列的第一个位置
- `to_messages()` 正常模式返回 1 条 system 角色消息；`summary_mode=True` 时返回空列表

### TaskStep

```python
@dataclass
class TaskStep(MemoryStep):
    task: str
    task_images: list | None = None
```

- 记录用户提交的任务文本和可选图片
- `to_messages()` 返回 1 条 user 角色消息，内容以 `"New task:\n"` 开头
- 每次 `agent.run(task)` 追加新的 TaskStep（`reset=False` 时），实现多轮对话

### ActionStep（核心步骤类型）

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

**字段详解**：

| 字段 | 说明 |
|------|------|
| `model_input_messages` | 发给模型的输入消息列表（完整对话历史） |
| `model_output_message` | 模型返回的 `ChatMessage` 对象（结构化） |
| `model_output` | 模型输出的原始文本 |
| `tool_calls` | 工具调用列表（`ToolCall` 对象列表） |
| `observations` | 工具/代码执行的观察结果文本 |
| `observations_images` | 观察结果中的图像列表 |
| `action_output` | 行动的输出值（代码执行返回值等） |
| `error` | 执行过程中的错误（`AgentError` 子类实例） |
| `step_number` | 步骤编号（从1开始） |
| `start_time`/`end_time`/`duration` | 执行时间戳和耗时 |

**to_messages() 输出顺序**：
1. 模型输入消息（可选，仅调试时显示）
2. 模型输出 → assistant 角色
3. 工具调用信息 → tool-call 角色
4. 观察图像 → user 角色（每张一条）
5. 观察文本 → tool-response 角色
6. 错误信息 → tool-response 角色（如有错误）

> 事实溯源：F-087~F-088

### ToolCall 数据类

```python
@dataclass
class ToolCall:
    name: str        # 工具名
    arguments: Any   # 参数字典
    id: str          # 调用ID（uuid4自动生成）
```

`dict()` 方法转换为 OpenAI function calling 标准格式：
```python
{"id": "call_xxx", "type": "function", "function": {"name": "web_search", "arguments": '{"query": "..."}'}}
```

> 事实溯源：F-082

### PlanningStep

```python
@dataclass
class PlanningStep(MemoryStep):
    model_input_messages: List[Message]
    model_output_message: ChatMessage
    plan: str
```

**双消息设计**：
1. assistant 消息：包含 LLM 生成的计划内容
2. user 消息：内容为 `"Now proceed and carry out this plan."`——强制角色切换，防止 LLM 只规划不行动

**summary_mode 下返回空列表**：当 Agent 作为被管理 Agent 时，规划细节不需要传递给父 Agent，实现"轻量遗忘"。

> 事实溯源：F-089~F-090

### FinalAnswerStep

```python
@dataclass
class FinalAnswerStep(MemoryStep):
    final_answer: Any
```

标记任务完成，包含最终答案值。答案经过 `handle_agent_output_types()` 转换为适当的 `AgentType` 子类（`AgentText`/`AgentImage`/`AgentAudio`）。

> 事实溯源：F-091

### AgentMemory 记忆管理器

```python
class AgentMemory:
    system_prompt: SystemPromptStep
    steps: List[Union[TaskStep, ActionStep, PlanningStep]]
```

**核心方法**：

| 方法 | 说明 |
|------|------|
| `reset()` | 清空 `steps` 列表，保留 `system_prompt` |
| `get_succinct_steps()` | 返回不含 `model_input_messages` 的精简步骤字典列表 |
| `get_full_steps()` | 返回包含所有字段的完整步骤字典列表 |
| `replay(logger, detailed=False)` | 使用 AgentLogger 格式化输出执行历史 |

> 事实溯源：F-092~F-096

### ChatMessage 数据类

```python
@dataclass
class ChatMessage:
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[ChatMessageToolCall]] = None
    raw: Optional[Any] = None
    usage_logs: Optional[Any] = None
```

`MessageRole` 枚举值：`USER`、`ASSISTANT`、`SYSTEM`、`TOOL_CALL`、`TOOL_RESPONSE`。

> 事实溯源：F-061~F-062

## 代码示例

### 检查记忆步骤

```python
from codified_smolagents import CodeAgent, HfApiModel

model = HfApiModel()
agent = CodeAgent(tools=[], model=model, additional_authorized_imports=['math'])

result = agent.run("计算 2**10 + 3**5")

# 查看记忆步骤
print(f"系统提示词存在: {agent.memory.system_prompt is not None}")
print(f"总步骤数: {len(agent.memory.steps)}")

for i, step in enumerate(agent.memory.steps):
    step_type = type(step).__name__
    if hasattr(step, 'step_number') and step.step_number:
        print(f"  #{step.step_number}: {step_type}")
    else:
        print(f"  : {step_type}")
```

### 消息序列可视化

```python
from codified_smolagents import CodeAgent, HfApiModel

model = HfApiModel()
agent = CodeAgent(tools=[], model=model)
agent.run("2**10等于多少？", max_steps=3)

# 将记忆序列化为消息
messages = agent.write_memory_to_messages()
for i, msg in enumerate(messages):
    role = msg.get('role', 'unknown')
    content = str(msg.get('content', ''))[:80]
    print(f"消息[{i}] role={role}: {content}...")
```

### 使用 replay() 回放执行过程

```python
from codified_smolagents import CodeAgent, HfApiModel

model = HfApiModel()
agent = CodeAgent(tools=[], model=model, additional_authorized_imports=['math'])
agent.run("计算斐波那契数列前10项的和")

# 美观地回放执行过程
agent.memory.replay(agent.logger, detailed=False)
```

### 获取精简/完整步骤

```python
from codified_smolagents import CodeAgent, HfApiModel
import json

model = HfApiModel()
agent = CodeAgent(tools=[], model=model)
agent.run("2+2等于多少？")

# 精简步骤（不含model_input_messages，适合存储/序列化）
succinct = agent.memory.get_succinct_steps()
print(f"精简步骤数: {len(succinct)}")

# 完整步骤（包含所有字段，适合深度调试）
full = agent.memory.get_full_steps()
print(f"完整步骤数: {len(full)}")
```

### summary_mode 的效果对比

```python
from codified_smolagents import CodeAgent, HfApiModel

model = HfApiModel()
agent = CodeAgent(tools=[], model=model, planning_interval=2)
agent.run("计算 1+1，然后把结果乘以2")

# 正常模式：包含SystemPrompt和PlanningStep
normal_msgs = agent.write_memory_to_messages(summary_mode=False)
# 摘要模式：跳过SystemPrompt和PlanningStep
summary_msgs = agent.write_memory_to_messages(summary_mode=True)

print(f"正常模式消息数: {len(normal_msgs)}")
print(f"摘要模式消息数: {len(summary_msgs)}")
```

> 事实溯源：F-023、F-084~F-096

## 常见问题/注意事项

### 没有自动压缩/截断机制

GodeAgents 的记忆**没有自动摘要、没有滑动窗口、没有向量检索**。这是有意为之的设计：
- 框架保持简单，不引入复杂的记忆管理策略
- 当步骤太多时，会直接超出 LLM 的上下文窗口限制
- 对于大多数任务（10-30步），这种设计完全够用
- 如果需要处理超长任务，可通过 `planning_interval` 定期让 LLM 自己总结进展，或在应用层自定义 `write_memory_to_messages`

### summary_mode 是唯一的"压缩"机制

`summary_mode=True` 做两件事：
1. 跳过 `SystemPromptStep` 的消息输出
2. 跳过 `PlanningStep` 的消息输出

这在多智能体协作场景中有用——子 Agent 的内部规划细节不需要传递给父 Agent。

### 步骤不可变（append-only）

一旦步骤被追加到 `memory.steps`，就不应该修改。所有字段记录了执行时的真实状态，修改历史步骤会破坏可审计性。如果需要"纠正"记忆，应该追加新步骤而非修改旧步骤。

### reset() 只清空步骤不清空系统提示

`memory.reset()` 将 `steps` 列表清空，但 `system_prompt` 保留。这是因为系统提示词定义了 Agent 的行为模式，在 Agent 生命周期内不应改变。

### ActionStep 的 model_input_messages 是最大的字段

`model_input_messages` 包含了当前步发给模型的完整对话历史，是每个 ActionStep 中体积最大的字段。`get_succinct_steps()` 排除了此字段以减小序列化体积，适合存储和日志场景。`get_full_steps()` 包含此字段，适合深度调试。

### 多轮对话依赖记忆保留

连续调用 `agent.run(task)` 不传 `reset=True` 时，新的 TaskStep 追加到现有步骤序列中，Agent 可以引用之前的对话内容。传 `reset=True` 则清空历史开始新任务。

### ChatMessage 与 Message 类型的区别

- `ChatMessage`（models.py）：模型输入输出的结构化消息，包含 `role`、`content`、`tool_calls`、`raw`、`usage_logs`
- `Message`（memory.py）：TypedDict，包含 `role: MessageRole` 和 `content: str | list[dict]`，用于记忆序列化后的消息格式

## 相关链接

- [简介：编码式多智能体推理](/concepts/00-introduction.md) — 框架概述
- [快速开始](/concepts/01-getting-started.md) — 安装与第一个Agent
- [架构总览](/concepts/02-architecture-overview.md) — 模块依赖与组件关系
- [MultiStepAgent：核心推理循环](/concepts/03-multi-step-agent.md) — Agent如何在循环中使用记忆
- [Memory API 参考](/references/memory-api.md) — MemoryStep、AgentMemory、ToolCall完整API
- [Agents API 参考](/references/agents-api.md) — write_memory_to_messages()方法说明
- [Models API 参考](/references/models-api.md) — ChatMessage和MessageRole定义
