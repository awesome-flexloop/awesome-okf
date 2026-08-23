---
type: Reference
title: Agents API 参考
description: codified-smolagents 智能体核心API参考，包含MultiStepAgent、ToolCallingAgent、CodeAgent类及相关类型定义与工具函数
tags: [Agent, MultiStepAgent, ToolCallingAgent, CodeAgent, ReAct, API参考]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T22:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T22:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: agents-source
    resource: ../../../../../../external/libs/models/AgnesAI/GodeAgents/Multi-Agent-Task/src/codified-smolagents/agents.py
    title: codified-smolagents/agents.py
---

# Agents API 参考

本文件记录 `agents.py` 模块中的所有公开类、类型定义和工具函数，基于源码零推测事实 F-006 ~ F-046。

## 概述

`agents.py` 是 codified-smolagents 的核心模块，实现了基于 ReAct（Reasoning + Acting）框架的多步智能体体系。核心类 `MultiStepAgent` 提供了智能体运行的主循环，`ToolCallingAgent` 和 `CodeAgent` 是两个具体子类，分别通过 JSON 工具调用和 Python 代码执行两种方式与环境交互。

> 事实溯源：F-013、F-032、F-039

## 模板工具函数

### get_variable_names

```python
def get_variable_names(self, template: str) -> Set[str]
```

从 Jinja2 模板字符串中提取所有 `{{ variable }}` 形式的变量名集合。使用正则表达式 `r"\{\{([^{}]+)\}\}"` 匹配。

**参数：**
- `template` (`str`): Jinja2 模板字符串

**返回：** `Set[str]` — 变量名集合

> 事实溯源：F-006

### populate_template

```python
def populate_template(template: str, variables: Dict[str, Any]) -> str
```

使用 Jinja2 的 `Template`（配置 `StrictUndefined`）渲染模板，将变量注入后返回渲染结果。渲染异常时抛出通用 `Exception`。

**参数：**
- `template` (`str`): Jinja2 模板字符串
- `variables` (`Dict[str, Any]`): 模板变量字典

**返回：** `str` — 渲染后的字符串

> 事实溯源：F-007

## Prompt 模板类型定义

### PlanningPromptTemplate

```python
class PlanningPromptTemplate(TypedDict):
    initial_facts: str
    initial_plan: str
    update_facts_pre_messages: str
    update_facts_post_messages: str
    update_plan_pre_messages: str
    update_plan_post_messages: str
```

规划步骤的提示词模板，包含初始事实收集、初始计划制定、事实更新前后消息、计划更新前后消息共6个字符串字段。

> 事实溯源：F-008

### ManagedAgentPromptTemplate

```python
class ManagedAgentPromptTemplate(TypedDict):
    task: str
    report: str
```

被管理智能体（Managed Agent）的提示词模板，包含任务分配和结果报告两个字符串字段。

> 事实溯源：F-009

### FinalAnswerPromptTemplate

```python
class FinalAnswerPromptTemplate(TypedDict):
    pre_messages: str
    post_messages: str
```

最终回答阶段的提示词模板，包含前置消息和后置消息两个字符串字段。

> 事实溯源：F-010

### PromptTemplates

```python
class PromptTemplates(TypedDict):
    system_prompt: str
    planning: PlanningPromptTemplate
    managed_agent: ManagedAgentPromptTemplate
    final_answer: FinalAnswerPromptTemplate
```

智能体完整的提示词模板集合，包含系统提示词、规划模板、被管理智能体模板和最终回答模板四个字段。

> 事实溯源：F-011

### EMPTY_PROMPT_TEMPLATES

```python
EMPTY_PROMPT_TEMPLATES: PromptTemplates
```

空提示词模板常量，所有字段值为空字符串，作为 `prompt_templates=None` 时的默认值。

> 事实溯源：F-012

## MultiStepAgent

```python
class MultiStepAgent
```

多步智能体基类，实现 ReAct 框架的核心循环：在目标未达成时，循环执行"行动（LLM生成）→观察（环境反馈）"的步骤。

> 事实溯源：F-013

### 构造函数

```python
def __init__(
    self,
    tools: List[Tool],
    model: Callable[[List[Dict[str, str]]], ChatMessage],
    prompt_templates: Optional[PromptTemplates] = None,
    max_steps: int = 20,
    add_base_tools: bool = False,
    verbosity_level: LogLevel = LogLevel.INFO,
    grammar: Optional[Dict[str, str]] = None,
    managed_agents: Optional[List] = None,
    step_callbacks: Optional[List[Callable]] = None,
    planning_interval: Optional[int] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    provide_run_summary: bool = False,
    final_answer_checks: Optional[List[Callable]] = None,
)
```

**参数：**
- `tools` (`List[Tool]`): 智能体可使用的工具列表
- `model` (`Callable`): 生成智能体行动的语言模型，接收消息列表返回 `ChatMessage`
- `prompt_templates` (`Optional[PromptTemplates]`): 提示词模板，默认为空模板
- `max_steps` (`int`, 默认 `20`): 最大执行步数
- `add_base_tools` (`bool`, 默认 `False`): 是否添加基础工具（web_search、visit_webpage、search_wikipedia）
- `verbosity_level` (`LogLevel`, 默认 `LogLevel.INFO`): 日志详细级别
- `grammar` (`Optional[Dict[str, str]]`): 用于解析LLM输出的语法规则
- `managed_agents` (`Optional[List]`): 可被调用的被管理智能体列表
- `step_callbacks` (`Optional[List[Callable]]`): 每步执行后的回调函数列表
- `planning_interval` (`Optional[int]`): 规划步骤执行间隔（步数）
- `name` (`Optional[str]`): 智能体名称（作为被管理智能体时必需）
- `description` (`Optional[str]`): 智能体描述（作为被管理智能体时必需）
- `provide_run_summary` (`bool`, 默认 `False`): 作为被管理智能体调用时是否提供运行摘要
- `final_answer_checks` (`Optional[List[Callable]]`): 最终回答验证函数列表

**初始化的实例属性：** `agent_name`、`model`、`prompt_templates`、`max_steps`、`step_number`（初始0）、`grammar`、`planning_interval`、`state`（初始空字典）、`name`、`description`、`provide_run_summary`、`final_answer_checks`、`managed_agents`（字典）、`tools`（字典，key为tool.name）、`system_prompt`、`memory`（`AgentMemory`实例）、`logger`（`AgentLogger`实例）、`monitor`（`Monitor`实例）、`step_callbacks`（列表，自动追加`monitor.update_metrics`）

> 事实溯源：F-014、F-015

### 核心方法

#### run

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

执行智能体任务。当 `stream=True` 时返回生成器逐步产出步骤；否则通过 `deque(..., maxlen=1)[0].final_answer` 返回最终答案。

**参数：**
- `task` (`str`): 要执行的任务描述
- `stream` (`bool`): 是否以流式方式运行
- `reset` (`bool`): 是否重置对话历史
- `images` (`Optional[List[PIL.Image.Image]]`): 输入图像列表
- `additional_args` (`Optional[Dict]`): 传递给智能体运行的额外变量
- `max_steps` (`Optional[int]`): 覆盖默认最大步数

> 事实溯源：F-020

#### step

```python
def step(self, memory_step: ActionStep) -> Union[None, Any]
```

执行一步 ReAct 循环的抽象方法，由子类实现。返回 `None` 表示步骤未结束，返回非 `None` 值表示最终答案。

> 事实溯源：F-022

#### write_memory_to_messages

```python
def write_memory_to_messages(
    self,
    summary_mode: Optional[bool] = False,
) -> List[Dict[str, str]]
```

将内存中的系统提示词和所有步骤依次转换为消息列表，用于输入给LLM。

**参数：**
- `summary_mode` (`Optional[bool]`): 摘要模式，为True时精简输出

**返回：** `List[Dict[str, str]]` — 消息列表

> 事实溯源：F-023

#### extract_action

```python
def extract_action(self, model_output: str, split_token: str) -> Tuple[str, str]
```

从LLM输出中按分隔符解析行动。取倒数第二个元素为推理过程（rationale），最后一个元素为行动（action）。分割失败时抛出 `AgentParsingError`。

**参数：**
- `model_output` (`str`): LLM输出文本
- `split_token` (`str`): 行动分隔符

**返回：** `Tuple[str, str]` — (rationale, action) 元组

> 事实溯源：F-024

#### provide_final_answer

```python
def provide_final_answer(self, task: str, images: Optional[list]) -> str
```

在达到最大步数后，基于交互日志生成最终回答。构造包含 `final_answer.pre_messages` 和 `final_answer.post_messages` 的消息列表调用模型。

**返回：** `str` — 最终回答文本

> 事实溯源：F-025

#### __call__

```python
def __call__(self, task: str, **kwargs)
```

使智能体可被作为被管理智能体调用。渲染 `managed_agent.task` 模板后调用 `run()`，再渲染 `managed_agent.report` 模板返回结果。若 `provide_run_summary=True` 则追加运行摘要。

> 事实溯源：F-026

#### save

```python
def save(self, output_dir: str | Path, relative_path: Optional[str] = None)
```

将智能体保存到输出目录，包括：递归保存被管理智能体、每个工具保存为 `tools/{tool_name}.py`、提示词模板序列化为 `prompts.yaml`、配置序列化为 `agent.json`、生成 `requirements.txt`、使用Jinja2模板生成 `app.py`。

> 事实溯源：F-027

#### to_dict

```python
def to_dict(self) -> dict[str, Any]
```

将智能体转换为字典表示，包含 `tools`、`model`、`managed_agents`、`prompt_templates`、`max_steps`、`verbosity_level`、`grammar`、`planning_interval`、`name`、`description`、`requirements` 字段。

> 事实溯源：F-028

#### from_hub

```python
@classmethod
def from_hub(
    cls,
    repo_id: str,
    token: Optional[str] = None,
    trust_remote_code: bool = False,
    **kwargs,
)
```

从 Hugging Face Hub 加载智能体（Space仓库）。要求 `trust_remote_code=True`。使用 `snapshot_download` 下载后调用 `from_folder()` 加载。

> 事实溯源：F-029

#### from_folder

```python
@classmethod
def from_folder(cls, folder: Union[str, Path], **kwargs)
```

从本地文件夹加载智能体。读取 `agent.json`，递归加载被管理智能体、工具（通过 `Tool.from_code`）、模型（动态导入），返回智能体实例。

> 事实溯源：F-030

#### push_to_hub

```python
def push_to_hub(
    self,
    repo_id: str,
    commit_message: str = "Upload agent",
    private: Optional[bool] = None,
    token: Optional[Union[bool, str]] = None,
    create_pr: bool = False,
) -> str
```

将智能体上传到 Hugging Face Hub（创建为Space仓库）。内部先 `save()` 到临时目录，再 `upload_folder` 上传。

> 事实溯源：F-031

#### interrupt

```python
def interrupt(self)
```

中断智能体执行，设置 `interrupt_switch = True`。

#### replay

```python
def replay(self, detailed: bool = False)
```

打印智能体执行步骤的美观回放。`detailed=True` 时显示每步内存详情（会显著增加日志长度）。

#### visualize

```python
def visualize(self)
```

使用 Rich 创建智能体结构的树形可视化。

### 内部方法

- `_validate_name(name)`: 验证名称为有效Python标识符且非保留字
- `_setup_managed_agents(managed_agents)`: 构建被管理智能体字典
- `_setup_tools(tools, add_base_tools)`: 构建工具字典，处理基础工具添加，确保 `final_answer` 工具存在
- `_validate_tools_and_managed_agents(tools, managed_agents)`: 检测工具和被管理智能体名称重复
- `_run(task, max_steps, images)`: 核心生成器方法，循环执行步骤
- `_create_action_step(step_start_time, images)`: 创建ActionStep实例
- `_execute_step(task, memory_step)`: 执行单步，调用子类的 `step()` 方法
- `_validate_final_answer(final_answer)`: 运行最终回答检查
- `_finalize_step(memory_step, step_start_time)`: 完成步骤，记录时间、执行回调
- `_handle_max_steps_reached(task, images, step_start_time)`: 达到最大步数时的处理
- `_create_planning_step(task, is_first_step, step)`: 创建规划步骤

> 事实溯源：F-016~F-019、F-021

## ToolCallingAgent

```python
class ToolCallingAgent(MultiStepAgent)
```

基于JSON工具调用的智能体，利用LLM原生的function calling能力，通过 `model.get_tool_call` 机制调用工具。

> 事实溯源：F-032

### 构造函数

```python
def __init__(
    self,
    tools: List[Tool],
    model: Callable[[List[Dict[str, str]]], ChatMessage],
    prompt_templates: Optional[PromptTemplates] = None,
    planning_interval: Optional[int] = None,
    **kwargs,
)
```

当 `prompt_templates=None` 时，从 `smolagents.prompts.toolcalling_agent.yaml` 加载默认模板。其余参数传递给父类。

> 事实溯源：F-033、F-034

### 核心方法

#### initialize_system_prompt

```python
def initialize_system_prompt(self) -> str
```

渲染系统提示词模板，传入变量 `tools` 和 `managed_agents`。

> 事实溯源：F-035

#### step

```python
def step(self, memory_step: ActionStep) -> Union[None, Any]
```

执行一步：
1. 将内存转换为消息列表
2. 调用模型，传入 `tools_to_call_from` 和停止序列 `["Observation:", "Calling tools:"]`
3. 从 `model_message.tool_calls[0]` 提取工具名、调用ID和参数
4. 若工具为 `final_answer`，返回最终答案；否则调用 `execute_tool_call()` 执行工具，返回 `None`

> 事实溯源：F-036

#### execute_tool_call

```python
def execute_tool_call(self, tool_name: str, arguments: Union[Dict[str, str], str]) -> Any
```

执行工具或被管理智能体调用。先在 `{**self.tools, **self.managed_agents}` 中查找，替换状态变量后调用。`TypeError` 抛出 `AgentToolCallError`，其他异常抛出 `AgentToolExecutionError`。

> 事实溯源：F-038

#### _substitute_state_variables

```python
def _substitute_state_variables(
    self, arguments: Union[Dict[str, str], str]
) -> Union[Dict[str, Any], str]
```

将参数中值为字符串且在 `self.state` 中存在的键替换为对应的状态值。

> 事实溯源：F-037

## CodeAgent

```python
class CodeAgent(MultiStepAgent)
```

基于代码执行的智能体，LLM生成Python代码块，经解析后在受控的Python执行器中运行。

> 事实溯源：F-039

### 构造函数

```python
def __init__(
    self,
    tools: List[Tool],
    model: Callable[[List[Dict[str, str]]], ChatMessage],
    prompt_templates: Optional[PromptTemplates] = None,
    grammar: Optional[Dict[str, str]] = None,
    additional_authorized_imports: Optional[List[str]] = None,
    planning_interval: Optional[int] = None,
    executor_type: str | None = "local",
    executor_kwargs: Optional[Dict[str, Any]] = None,
    max_print_outputs_length: Optional[int] = None,
    **kwargs,
)
```

**特有参数：**
- `additional_authorized_imports` (`Optional[List[str]]`): 额外授权的Python导入模块列表，与 `BASE_BUILTIN_MODULES` 合并；包含 `"*"` 时输出警告日志
- `executor_type` (`str | None`, 默认 `"local"`): 执行器类型，可选 `"local"`、`"e2b"`、`"docker"`
- `executor_kwargs` (`Optional[Dict[str, Any]]`): 传递给执行器构造函数的额外参数
- `max_print_outputs_length` (`Optional[int]`): print输出最大长度

当 `prompt_templates=None` 时，从 `smolagents.prompts.code_agent.yaml` 加载默认模板。初始化时创建Python执行器实例 `self.python_executor`。

> 事实溯源：F-040~F-042

### 核心方法

#### create_python_executor

```python
def create_python_executor(self) -> PythonExecutor
```

根据 `executor_type` 创建执行器：
- `"e2b"` → `E2BExecutor`
- `"docker"` → `DockerExecutor`
- `"local"` → `LocalPythonExecutor`
- 其他值抛出 `ValueError`

> 事实溯源：F-043

#### initialize_system_prompt

```python
def initialize_system_prompt(self) -> str
```

渲染系统提示词模板，传入变量 `tools`、`managed_agents`、`authorized_imports`。

> 事实溯源：F-044

#### step

```python
def step(self, memory_step: ActionStep) -> Union[None, Any]
```

执行一步：
1. 将内存转换为消息列表
2. 调用模型，传入停止序列 `["<end_code>", "Observation:", "Calling tools:"]`
3. 使用 `parse_code_blobs()` 提取代码块，`fix_final_answer_code()` 修复代码
4. 调用 `self.python_executor(code_action)` 执行代码
5. 返回 `(output, execution_logs, is_final_answer)` 三元组；`is_final_answer=True` 时返回output，否则返回None

> 事实溯源：F-045

#### to_dict

```python
def to_dict(self) -> dict[str, Any]
```

在父类结果基础上追加 `authorized_imports`、`executor_type`、`executor_kwargs`、`max_print_outputs_length` 四个字段。

> 事实溯源：F-046

## 相关概念

- [智能体架构概述](/concepts/agent-architecture.md) — MultiStepAgent的ReAct循环设计
- [工具调用智能体](/concepts/tool-calling-agent.md) — ToolCallingAgent的JSON工具调用机制
- [代码执行智能体](/concepts/code-agent.md) — CodeAgent的Python代码执行机制
- [提示词模板系统](/concepts/prompt-templates.md) — PromptTemplates和YAML提示词配置
- [模型API参考](/references/models-api.md) — Model基类和各实现类
- [工具API参考](/references/tools-api.md) — Tool基类和工具定义
- [内存API参考](/references/memory-api.md) — AgentMemory和MemoryStep体系
- [执行器API参考](/references/executor-api.md) — PythonExecutor和执行环境
