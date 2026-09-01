---
type: Concept
title: MultiStepAgent：核心推理循环
description: MultiStepAgent基类的run循环、step抽象、记忆管理、规划机制
tags: [核心, 智能体, 循环, MultiStepAgent]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: F-013
    resource: /references/agents-api.md
    title: Agents API 参考
  - id: F-084
    resource: /references/memory-api.md
    title: Memory API 参考
---

# MultiStepAgent：核心推理循环

## 概述

`MultiStepAgent` 是 GodeAgents 框架的核心基类，定义了多步推理的通用框架。它无显式基类（继承 `object`），实现了 ReAct（Reasoning + Acting）范式的核心循环——在目标未达成时反复执行"思考→行动→观察"步骤，直到产出最终答案或达到步数上限。`ToolCallingAgent` 和 `CodeAgent` 都继承自它，子类只需实现一个抽象方法：`step()`。

理解了 `MultiStepAgent`，你就理解了框架 80% 的运行机制。

> 事实溯源：F-013、F-022、F-032、F-039

## 核心概念

### 模板方法模式

`MultiStepAgent` 是典型的**模板方法（Template Method）**设计模式：
- **基类**定义算法骨架：初始化记忆→进入循环→每步序列化记忆→调用模型→执行行动→记录结果→检查终止→返回答案
- **子类**只需实现 `step(memory_step)` 方法，定义"单步做什么"——ToolCallingAgent 解析 JSON 工具调用，CodeAgent 解析并执行 Python 代码

### 推理循环三阶段

1. **初始化**：创建 TaskStep，进入 `_run()` 生成器
2. **迭代**：循环调用 step()，每步可插入 PlanningStep，直到 final_answer 非 None 或步数超限
3. **终止**：创建 FinalAnswerStep，返回结果

### 规划机制

通过 `planning_interval` 参数控制：第1步和每隔 N 步创建 `PlanningStep`，让 LLM 先制定/更新计划再执行，帮助长任务保持方向。

## API 要点

### 构造参数

```python
MultiStepAgent(
    tools: List[Tool],                          # 工具列表（自动注入final_answer）
    model: Callable,                            # 模型实例（Model子类）
    prompt_templates: Optional[PromptTemplates] = None,  # 自定义提示模板
    max_steps: int = 20,                        # 最大步数
    add_base_tools: bool = False,               # 是否添加默认搜索工具
    verbosity_level: LogLevel = LogLevel.INFO,  # 日志级别（0=OFF,1=ERROR,2=INFO,3=DEBUG）
    grammar: Optional[Dict[str, str]] = None,   # 输出语法约束
    managed_agents: Optional[List] = None,      # 被管理的子Agent列表
    step_callbacks: Optional[List[Callable]] = None,  # 步骤回调函数
    planning_interval: Optional[int] = None,    # 规划间隔步数
    name: Optional[str] = None,                 # Agent名称（被管理时必填）
    description: Optional[str] = None,          # Agent描述（被管理时必填）
    provide_run_summary: bool = False,          # 作为被管理Agent时是否提供运行摘要
    final_answer_checks: Optional[List[Callable]] = None,  # 最终答案检查
)
```

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `agent_name` | str | Agent名称标识 |
| `model` | Callable | 模型实例 |
| `prompt_templates` | PromptTemplates | 提示模板集合 |
| `max_steps` | int | 最大步数 |
| `step_number` | int | 当前步数（初始0） |
| `state` | dict | 状态字典，用于跨步骤变量传递 |
| `tools` | dict | 工具字典，key为tool.name |
| `managed_agents` | dict | 被管理Agent字典，key为agent.name |
| `system_prompt` | str | 系统提示词 |
| `memory` | AgentMemory | 记忆实例（AgentMemory(system_prompt)） |
| `logger` | AgentLogger | 日志器（AgentLogger(level=verbosity_level)） |
| `monitor` | Monitor | 监控器（Monitor(model, logger)） |
| `step_callbacks` | list | 步骤回调列表 |
| `planning_interval` | int/None | 规划间隔 |
| `grammar` | dict/None | 语法约束 |

> 事实溯源：F-014~F-015

### 核心方法

#### run()：入口方法

```python
def run(
    self,
    task: str,
    stream: bool = False,
    reset: bool = False,
    images: Optional[List["PIL.Image.Image"]] = None,
    additional_args: Optional[Dict] = None,
    max_steps: Optional[int] = None,
)
```

- `stream=True`：返回 `self._run(...)` 生成器，逐步 yield ActionStep
- `stream=False`（默认）：使用 `deque(..., maxlen=1)[0].final_answer` 消费生成器，返回最终答案
- `reset=True`：调用 `memory.reset()` 清空历史步骤
- `images`：多模态图片输入列表
- `max_steps`：临时覆盖构造时的最大步数

> 事实溯源：F-020

#### _run()：核心生成器

`_run()` 是真正的推理循环引擎，是一个 Python 生成器。循环逻辑：

1. 创建 `TaskStep(task, task_images)` 追加到 `memory.steps`
2. `step_number = 0`，`final_answer = None`
3. while 循环：
   - `step_number += 1`
   - **规划检查**：若 `planning_interval` 非 None 且 (`step_number == 1` 或 `step_number % planning_interval == 0`)，创建 `PlanningStep` 让 LLM 制定计划
   - 创建 `ActionStep`，记录 `start_time`
   - 调用 `step(memory_step)`（子类实现）
   - 记录 `end_time`、`duration`
   - 执行所有 `step_callbacks`
   - 若 `final_answer` 非 None，跳出循环
   - 若 `step_number > max_steps`，调用 `provide_final_answer()` 兜底
   - yield 当前步骤
4. 创建 `FinalAnswerStep(final_answer)` 并 yield

> 事实溯源：F-021

#### step()：抽象方法

```python
def step(self, memory_step: ActionStep) -> Union[None, Any]
```

基类中方法体为 `pass`，子类必须实现。返回 `None` 表示继续循环，返回非 None 值表示任务完成（该值即 final_answer）。

- **ToolCallingAgent.step()**：调用 model 传入 `tools_to_call_from`，从 `tool_calls[0]` 解析工具名和参数；若工具是 `final_answer` 则返回答案，否则调用 `execute_tool_call()` 并返回 None
- **CodeAgent.step()**：调用 model（不传 tools_to_call_from），用 `parse_code_blobs()` 解析 Python 代码块，通过 `python_executor` 执行，返回 `(output, execution_logs, is_final_answer)` 三元组

> 事实溯源：F-022、F-036、F-045

#### write_memory_to_messages()：记忆序列化

```python
def write_memory_to_messages(self, summary_mode: bool = False) -> List[Dict[str, str]]
```

将 `self.memory.system_prompt` 和 `self.memory.steps` 依次调用 `to_messages(summary_mode=summary_mode)` 并扩展为消息列表返回。`summary_mode=True` 时 PlanningStep 返回空消息，减少 Token 消耗。

> 事实溯源：F-023

#### execute_tool_call()（ToolCallingAgent）：工具执行

```python
def execute_tool_call(self, tool_name: str, arguments: Union[Dict[str, str], str]) -> Any
```

在 `{**self.tools, **self.managed_agents}` 合并字典中查找工具/子Agent，通过 `_substitute_state_variables()` 替换 state 变量后调用。`TypeError` 抛出 `AgentToolCallError`，其他异常抛出 `AgentToolExecutionError`。

> 事实溯源：F-037~F-038

#### 持久化方法

| 方法 | 说明 |
|------|------|
| `save(output_dir)` | 保存到目录：tools/*.py、prompts.yaml、agent.json、requirements.txt、app.py |
| `to_dict()` | 序列化为字典（包含tools、model、managed_agents、prompt_templates、参数配置） |
| `from_hub(repo_id, trust_remote_code=True)` | 从 HuggingFace Hub 下载 Space 仓库并加载 |
| `from_folder(folder)` | 从本地文件夹加载（读取agent.json，递归加载tools/model/managed_agents） |
| `push_to_hub(repo_id)` | 打包上传到 HuggingFace Hub 作为 Space |

> 事实溯源：F-027~F-031

## 代码示例

### 创建并运行 ToolCallingAgent

```python
from codified_smolagents import ToolCallingAgent, DuckDuckGoSearchTool, HfApiModel

model = HfApiModel()
agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    max_steps=10,
    verbosity_level=2,  # INFO级别，显示思考过程
)
result = agent.run("Python 3.12 有哪些主要新特性？")
print(result)
```

### 创建带规划的 CodeAgent

```python
from codified_smolagents import CodeAgent, HfApiModel

model = HfApiModel()
agent = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=['math', 'datetime'],
    planning_interval=3,  # 每3步重新规划
    max_steps=30,
)
result = agent.run("计算从2024年1月1日到今天一共有多少天，然后判断这个数是否为质数")
print(result)
```

### 流式模式逐步获取步骤

```python
from codified_smolagents import CodeAgent, HfApiModel

model = HfApiModel()
agent = CodeAgent(tools=[], model=model)

# stream=True 返回生成器
for step in agent.run("计算 fibonacci(20) 的值", stream=True):
    step_type = type(step).__name__
    print(f"[{step_type}] step_number={step.step_number if hasattr(step, 'step_number') else 'N/A'}")
    if step_type == "FinalAnswerStep":
        print(f"最终答案: {step.final_answer}")
```

### 多轮对话（保留记忆）

```python
from codified_smolagents import CodeAgent, HfApiModel

model = HfApiModel()
agent = CodeAgent(tools=[], model=model, additional_authorized_imports=['math'])

# 第一轮
r1 = agent.run("计算 2**10")
print(r1)  # 1024

# 第二轮：不reset，保留上下文，Agent可以引用之前的结果
r2 = agent.run("把上面的结果再乘以2")
print(r2)  # 2048

# 全新任务：reset=True清空记忆
r3 = agent.run("计算 3**5", reset=True)
print(r3)  # 243
```

### 多智能体协作

```python
from codified_smolagents import CodeAgent, ToolCallingAgent, HfApiModel, DuckDuckGoSearchTool

model = HfApiModel()

# 子Agent：专门负责搜索
search_agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    name="search_agent",
    description="擅长搜索网络信息，当需要查找事实性信息时使用"
)

# 父Agent：可以委派搜索任务给子Agent
manager = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[search_agent],
    additional_authorized_imports=['math'],
)
result = manager.run("搜索GodeAgents框架的版本号，然后计算版本号中数字的乘积")
print(result)
```

> 事实溯源：F-014~F-021、F-032~F-046

## 常见问题/注意事项

### max_steps 默认20步可能不够

对于需要多次搜索、阅读网页、综合分析的复杂任务，20步可能不够。步数耗尽时 Agent 不会直接报错，而是调用 `provide_final_answer()` 基于已有信息做兜底总结。建议复杂调研任务设置 `max_steps=30~50`。

### planning_interval 建议值

- 太频繁（如1）：Agent 会不断"规划"而不"行动"，浪费 Token 和步数
- 太稀疏（如10）：失去方向校正效果
- 推荐值：3-5，既能定期校正方向，又不会过度规划

### step_callbacks 用于监控和调试

回调函数接收 `(step_log, agent)` 两个参数，每步完成后调用。框架自动追加 `monitor.update_metrics` 用于 Token 统计。可以自定义回调实现：
- 自定义日志格式
- 提前终止（在回调中抛出异常）
- 步骤数据收集和分析

### state 字典跨步骤传递

Agent 维护 `self.state = {}` 字典，`_substitute_state_variables()` 方法会在工具参数值是字符串且恰好是 state 中的键时自动替换。这使得工具调用可以引用之前步骤产生的数据。

### final_answer 工具自动注入

不需要手动添加 `FinalAnswerTool()`，框架在 `_setup_tools()` 中通过 `self.tools.setdefault("final_answer", FinalAnswerTool())` 确保其存在。

### 作为被管理Agent必须设置name和description

当一个 Agent 通过 `managed_agents` 参数被父Agent管理时，必须设置 `name`（有效Python标识符）和 `description`（描述能力）。父Agent通过 description 了解子Agent的能力，决定何时委派任务。

### 生命周期图

```mermaid
sequenceDiagram
    participant User as 用户
    participant Run as run()
    participant Loop as _run()生成器
    participant Step as step()(子类)
    participant Model as Model
    participant Tool as Tool/Executor
    participant Memory as AgentMemory

    User->>Run: agent.run(task)
    Run->>Memory: memory.reset() (如果reset=True)
    Run->>Memory: 创建TaskStep → steps.append
    Run->>Loop: 启动_run()生成器

    loop plan-act-observe循环
        Loop->>Loop: step_number++
        alt 第1步或planning_interval步
            Loop->>Model: 创建PlanningStep(制定计划)
            Model-->>Loop: 返回plan
            Loop->>Memory: PlanningStep → steps.append
        end
        Loop->>Loop: 创建ActionStep, 记录start_time
        Loop->>Step: step(memory_step)
        Step->>Memory: write_memory_to_messages()
        Memory-->>Step: 返回消息列表
        Step->>Model: model(messages, tools_to_call_from/stop_sequences)
        Model-->>Step: 返回ChatMessage
        alt ToolCallingAgent
            Step->>Tool: execute_tool_call(tool_name, args)
            Tool-->>Step: 返回observation
        else CodeAgent
            Step->>Tool: python_executor(code)
            Tool-->>Step: 返回(output, logs, is_final_answer)
        end
        Step->>Memory: ActionStep(记录模型输出/观察/错误) → steps.append
        Loop->>Loop: 执行step_callbacks
        Loop->>Loop: 检查final_answer或max_steps
    end

    Loop->>Memory: FinalAnswerStep → steps.append
    Loop-->>Run: yield FinalAnswerStep
    Run-->>User: 返回final_answer
```

> 事实溯源：F-020~F-026、F-036~F-038、F-045

## 相关链接

- [简介：编码式多智能体推理](00-introduction.md) — 框架概述
- [快速开始](01-getting-started.md) — 安装与第一个Agent
- [架构总览](02-architecture-overview.md) — 模块依赖与组件关系
- [记忆系统：步骤序列](04-memory-system.md) — AgentMemory与MemoryStep体系
- [Agents API 参考](../references/agents-api.md) — MultiStepAgent/ToolCallingAgent/CodeAgent完整API
- [Memory API 参考](../references/memory-api.md) — 记忆系统API
- [Models API 参考](../references/models-api.md) — 模型后端API
