---
type: Concept
title: 提示词模板系统
description: YAML提示模板结构、Jinja2变量渲染、planning/managed_agent/final_answer子模板
tags: [提示词, 模板, Jinja2, YAML, PromptTemplates]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: F-008
    resource: /references/prompts-reference.md
    title: Prompts 参考
  - id: F-035
    resource: /references/agents-api.md
    title: Agents API 参考
---

# 提示词模板系统

## 概述

提示词模板系统（Prompt Templates）是 GodeAgents 框架中管理 Agent 与 LLM 交互提示词的核心机制。框架采用 YAML 文件定义结构化模板，通过 Jinja2 模板引擎进行变量渲染，将系统提示、规划提示、托管智能体提示和最终答案提示组织为层次化的 `PromptTemplates` 结构。内置的 `code_agent.yaml` 和 `toolcalling_agent.yaml` 分别为 CodeAgent 和 ToolCallingAgent 提供了经过调优的默认提示词，同时开发者可以通过自定义模板精细控制 Agent 的行为。

> 事实溯源：F-006~F-012、F-025、F-035、F-044、F-153~F-155

## 核心概念

### PromptTemplates 四层结构

`PromptTemplates` 是一个 TypedDict，包含四个顶层字段，每个字段对应 Agent 运行中不同阶段的提示词：

| 字段 | 类型 | 用途 |
|------|------|------|
| `system_prompt` | `str` | 系统提示，定义 Agent 的角色、能力和行为规范 |
| `planning` | `PlanningPromptTemplate` | 规划阶段提示（事实收集+计划制定+更新） |
| `managed_agent` | `ManagedAgentPromptTemplate` | 托管智能体调用提示（任务分配+报告接收） |
| `final_answer` | `FinalAnswerPromptTemplate` | 最终答案输出提示 |

> 事实溯源：F-011

### 三个子模板结构

**PlanningPromptTemplate（六段式）**

规划模板包含六个字符串字段，对应 ReAct 风格规划的六个阶段：

| 字段 | 用途 |
|------|------|
| `initial_facts` | 初始事实记录提示 |
| `initial_plan` | 初始计划制定提示 |
| `update_facts_pre_messages` | 更新事实前的引导消息 |
| `update_facts_post_messages` | 更新事实后的确认消息 |
| `update_plan_pre_messages` | 更新计划前的引导消息 |
| `update_plan_post_messages` | 更新计划后的确认消息 |

这种六段式设计使得 Agent 在每一步执行后都能回顾事实、更新计划，保持对任务全局的认知。

**ManagedAgentPromptTemplate（两段式）**

| 字段 | 用途 |
|------|------|
| `task` | 分配给托管智能体的任务模板 |
| `report` | 接收托管智能体报告的模板 |

**FinalAnswerPromptTemplate（两段式）**

| 字段 | 用途 |
|------|------|
| `pre_messages` | 输出最终答案前的引导消息 |
| `post_messages` | 输出最终答案后的收尾消息 |

> 事实溯源：F-008~F-010

### Jinja2 模板渲染

框架使用 Jinja2 模板引擎渲染提示词模板，所有模板变量使用 `{{ variable_name }}` 语法标记：

- **`populate_template(template, variables)`**：使用 `jinja2.Template(StrictUndefined)` 渲染模板，`StrictUndefined` 模式下引用未定义变量会抛出错误，防止因变量名拼写错误导致提示词残缺
- **`get_variable_names(template)`**：使用正则 `r"\{\{([^{}]+)\}\}"` 提取模板中所有变量名，用于在渲染前验证所需变量是否齐全

> 事实溯源：F-006~F-007

### code_agent.yaml vs toolcalling_agent.yaml

两个内置 YAML 模板文件结构相同（都有 system_prompt/planning/managed_agent/final_answer 四个顶层键），但 system_prompt 的内容不同：

| 模板文件 | system_prompt 指令 | 输出格式 |
|----------|-------------------|----------|
| `code_agent.yaml` | 指示 LLM 使用 ` ```py ` 代码块执行操作，通过 `final_answer()` 返回答案，`<end_code>` 标记代码结束 | Python 代码块 |
| `toolcalling_agent.yaml` | 指示 LLM 使用 JSON 格式 `tool_calls` 调用工具 | JSON 工具调用 |

> 事实溯源：F-153~F-155

### system_prompt 渲染变量

不同 Agent 类型在渲染 system_prompt 时传入的变量不同：

| Agent 类型 | 渲染变量 |
|-----------|----------|
| `ToolCallingAgent` | `tools`, `managed_agents` |
| `CodeAgent` | `tools`, `managed_agents`, `authorized_imports` |

CodeAgent 额外需要 `authorized_imports` 变量来告知模型可安全使用的 Python 模块列表。

> 事实溯源：F-035、F-044

### EMPTY_PROMPT_TEMPLATES

`EMPTY_PROMPT_TEMPLATES` 是一个常量，所有字段均为空字符串。当需要完全自定义提示词、不使用任何默认模板内容时，可以以此为起点构建。

> 事实溯源：F-012

## API 要点

### TypedDict 定义

```python
from typing import TypedDict

class PlanningPromptTemplate(TypedDict):
    initial_facts: str
    initial_plan: str
    update_facts_pre_messages: str
    update_facts_post_messages: str
    update_plan_pre_messages: str
    update_plan_post_messages: str

class ManagedAgentPromptTemplate(TypedDict):
    task: str
    report: str

class FinalAnswerPromptTemplate(TypedDict):
    pre_messages: str
    post_messages: str

class PromptTemplates(TypedDict):
    system_prompt: str
    planning: PlanningPromptTemplate
    managed_agent: ManagedAgentPromptTemplate
    final_answer: FinalAnswerPromptTemplate
```

> 事实溯源：F-008~F-011

### 模板工具函数

```python
def get_variable_names(template: str) -> List[str]:
    """
    用正则 r"\\{\\{([^{}]+)\\}\\}" 提取Jinja2模板中的变量名。
    返回变量名字符串列表（去重）。
    用于在渲染前检查所需变量是否齐全。
    """
    ...

def populate_template(template: str, variables: dict) -> str:
    """
    用 jinja2.Template(StrictUndefined) 渲染模板。
    StrictUndefined模式：引用未定义变量时抛出UndefinedError，
    防止因变量缺失导致提示词残缺。
    返回渲染后的字符串。
    """
    ...
```

> 事实溯源：F-006~F-007

### provide_final_answer 流程

```python
def provide_final_answer(self, task: str, **kwargs):
    """
    构造包含 final_answer.pre_messages 和 final_answer.post_messages
    的消息列表，调用模型生成最终答案。
    """
    ...
```

当 Agent 决定输出最终答案时，框架会：
1. 将 `final_answer.pre_messages` 渲染后插入消息列表
2. 调用模型生成答案
3. 将 `final_answer.post_messages` 渲染后追加到消息中

> 事实溯源：F-025

### YAML 模板文件结构

```yaml
# code_agent.yaml 示例结构
system_prompt: |
  You are an expert Python agent. You write code to solve tasks.
  Use ```py code blocks for all actions.
  Call final_answer() to return your final answer.
  Mark the end of your code with <end_code>.
  Available imports: {{ authorized_imports }}
  Available tools:
  {{ tools }}
  Managed agents:
  {{ managed_agents }}

planning:
  initial_facts: |
    ...
  initial_plan: |
    ...
  update_facts_pre_messages: |
    ...
  update_facts_post_messages: |
    ...
  update_plan_pre_messages: |
    ...
  update_plan_post_messages: |
    ...

managed_agent:
  task: |
    ...
  report: |
    ...

final_answer:
  pre_messages: |
    ...
  post_messages: |
    ...
```

> 事实溯源：F-153~F-155

## 代码示例

### 自定义 system_prompt

```python
from codified_smolagents import CodeAgent, HfApiModel, PromptTemplates

model = HfApiModel()

# 使用自定义system_prompt，其他部分使用默认模板
custom_templates = {
    "system_prompt": """你是一个专业的Python数据分析师。
你擅长使用pandas、numpy和matplotlib处理和分析数据。
所有操作通过Python代码执行，使用```py代码块。
当得出最终结论时，调用final_answer()返回结果。

可用工具：
{{ tools }}

托管智能体：
{{ managed_agents }}

授权导入：
{{ authorized_imports }}

请以清晰、专业的方式完成任务。"""
}

agent = CodeAgent(
    tools=[],
    model=model,
    prompt_templates=custom_templates,
    additional_authorized_imports=['pandas', 'numpy', 'math'],
    max_steps=5,
)

result = agent.run("计算1到100的平方和，并判断是否为质数")
print(result)
```

### 使用 Jinja2 变量渲染

```python
from codified_smolagents import populate_template, get_variable_names

# 定义模板
template = """你是一个{{ role }}。
你的任务是{{ task_description }}。
你可以使用以下工具：{% for tool in tools %}- {{ tool }}{% endfor %}
注意事项：{{ constraint }}"""

# 提取模板变量名
variables = get_variable_names(template)
print(f"模板需要的变量: {variables}")
# ['role', 'task_description', 'tools', 'constraint']

# 渲染模板
rendered = populate_template(template, {
    "role": "代码助手",
    "task_description": "计算数学问题",
    "tools": ["calculator", "text_stats"],
    "constraint": "答案必须准确，步骤清晰",
})
print(rendered)
```

### 构建完整的自定义 PromptTemplates

```python
from codified_smolagents import (
    CodeAgent, HfApiModel, PromptTemplates,
    PlanningPromptTemplate, ManagedAgentPromptTemplate, FinalAnswerPromptTemplate,
)

model = HfApiModel()

# 完全自定义提示模板
custom_templates: PromptTemplates = {
    "system_prompt": """你是一个严谨的研究助手。
每次行动前，你需要先思考，然后执行代码验证假设。
使用```py代码块编写Python代码，用<end_code>标记结束。
得出结论后调用final_answer(结论)返回。

授权导入: {{ authorized_imports }}
工具: {{ tools }}
托管智能体: {{ managed_agents }}""",

    "planning": {
        "initial_facts": """首先，列出完成任务"{{ task }}"需要了解的已知事实：""",
        "initial_plan": """基于以上事实，制定逐步执行计划：""",
        "update_facts_pre_messages": """根据最新执行结果，更新已知事实：""",
        "update_facts_post_messages": """事实已更新。""",
        "update_plan_pre_messages": """根据新的事实，调整执行计划：""",
        "update_plan_post_messages": """计划已更新，继续执行。""",
    },

    "managed_agent": {
        "task": """请调用 {{ agent_name }} 完成以下任务：{{ task }}
请详细描述你需要它做什么。""",
        "report": """{{ agent_name }} 返回了以下结果：{{ report }}
请根据此结果继续你的任务。""",
    },

    "final_answer": {
        "pre_messages": """你已经收集到足够的信息。请给出最终答案。""",
        "post_messages": """答案已提供。""",
    },
}

agent = CodeAgent(
    tools=[],
    model=model,
    prompt_templates=custom_templates,
    additional_authorized_imports=['math'],
    max_steps=5,
)

result = agent.run("验证哥德巴赫猜想在100以内偶数上是否成立")
print(result)
```

### 从 EMPTY_PROMPT_TEMPLATES 开始构建

```python
from codified_smolagents import CodeAgent, HfApiModel
from codified_smolagents.prompts import EMPTY_PROMPT_TEMPLATES

# 从空模板开始（所有字段为空字符串）
templates = dict(EMPTY_PROMPT_TEMPLATES)

# 仅设置system_prompt，其他部分保持为空
templates["system_prompt"] = """Solve the task using Python code in ```py blocks.
Call final_answer() with your result.
Imports allowed: {{ authorized_imports }}
Tools: {{ tools }}"""

model = HfApiModel()
agent = CodeAgent(
    tools=[],
    model=model,
    prompt_templates=templates,
    additional_authorized_imports=['math', 'statistics'],
    max_steps=3,
)
result = agent.run("What is the standard deviation of [1,2,3,4,5,6,7,8,9,10]?")
print(result)
```

### ToolCallingAgent 使用自定义提示词

```python
from codified_smolagents import ToolCallingAgent, HfApiModel, DuckDuckGoSearchTool

model = HfApiModel()

# ToolCallingAgent的system_prompt不需要authorized_imports变量
# 因为它通过JSON tool_calls调用工具，而非生成代码
custom_templates = {
    "system_prompt": """你是一个网络搜索助手。
你可以使用提供的工具搜索最新信息。
以JSON格式输出tool_calls来调用工具。
当你有足够信息回答用户问题时，直接回答。

可用工具：
{{ tools }}

托管智能体：
{{ managed_agents }}""",
}

agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    prompt_templates=custom_templates,
    max_steps=5,
)

result = agent.run("2026年图灵奖得主是谁？")
print(result)
```

### 检查模板变量

```python
from codified_smolagents import get_variable_names

# 检查CodeAgent默认system_prompt需要哪些变量
code_agent_prompt = """
Available imports: {{ authorized_imports }}
Tools: {{ tools }}
Managed agents: {{ managed_agents }}
Task: {{ task }}
"""
vars_needed = get_variable_names(code_agent_prompt)
print(f"CodeAgent system_prompt需要变量: {vars_needed}")
# ['authorized_imports', 'tools', 'managed_agents', 'task']

# 检查ToolCallingAgent默认system_prompt
toolcalling_prompt = """
Tools: {{ tools }}
Managed agents: {{ managed_agents }}
"""
vars_needed2 = get_variable_names(toolcalling_prompt)
print(f"ToolCallingAgent system_prompt需要变量: {vars_needed2}")
# ['tools', 'managed_agents']
```

> 事实溯源：F-006~F-012、F-025、F-035、F-044、F-153~F-155

## 注意事项

### CodeAgent 模板必须包含 authorized_imports 变量

`CodeAgent.initialize_system_prompt()` 在渲染 system_prompt 时传入 `authorized_imports` 变量。如果自定义模板中引用了 `{{ authorized_imports }}`，必须确保该变量在渲染时可用；如果不引用该变量，则可以省略，但建议保留以便模型知道哪些模块可用。

### StrictUndefined 模式下变量名错误会抛异常

`populate_template()` 使用 `jinja2.Template(StrictUndefined)`，这意味着模板中引用的任何变量如果不在传入的 variables 字典中，都会抛出 `jinja2.UndefinedError`。这是有意设计的——防止因变量名拼写错误导致生成残缺的提示词。在自定义模板前，建议使用 `get_variable_names()` 检查所需变量。

### 规划模板六段式不要随意删除

PlanningPromptTemplate 的六个字段在规划流程的不同阶段被分别渲染和使用，删除任一字段可能导致运行时 KeyError。如果不需要某个阶段，可以将其设为空字符串，但不应删除键。

### code_agent.yaml 的代码块标记至关重要

`code_agent.yaml` 的 system_prompt 中指示 LLM 使用 ` ```py ` 代码块和 `<end_code>` 结束标记。框架依赖这些标记通过 `parse_code_blobs()` 从模型输出中提取代码。如果自定义 system_prompt 移除了这些指示，模型可能不以正确格式输出代码，导致解析失败。

### toolcalling_agent.yaml 的 JSON 格式指示同样关键

`toolcalling_agent.yaml` 的 system_prompt 指示 LLM 使用 JSON 格式输出 tool_calls。框架通过 `parse_json_blob()` 解析这些调用。修改此提示时务必保留 JSON 格式的指令，否则工具调用会解析失败。

### final_answer 模板影响答案质量

`final_answer.pre_messages` 和 `final_answer.post_messages` 控制最终答案的生成引导。好的 pre_messages 可以引导模型给出更完整、结构化的答案，而不只是简单地调用 final_answer() 返回。

### YAML 文件中的 | 保留换行符

在 YAML 模板文件中，多行字符串应使用 `|`（literal block scalar）而非 `>`（folding block scalar），以保留提示词中的换行格式，这对代码块和列表格式尤为重要。

## 相关链接

- [CodeAgent：代码执行范式](/concepts/06-code-agent.md) — CodeAgent如何使用system_prompt
- [ToolCallingAgent：函数调用范式](/concepts/05-tool-calling-agent.md) — ToolCallingAgent的提示词差异
- [多步推理循环](/concepts/03-multi-step-agent.md) — 规划模板在多步循环中的使用
- [高级特性](/concepts/14-advanced-features.md) — Managed Agents的task/report模板
- [Prompts 参考](/references/prompts-reference.md) — 默认模板完整内容
