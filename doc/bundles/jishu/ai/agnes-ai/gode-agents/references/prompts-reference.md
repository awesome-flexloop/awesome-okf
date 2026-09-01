---
type: reference
title: 提示词模板参考
description: Gode Agents 提示词模板系统API参考，包括PromptTemplates类型定义、Jinja2模板渲染、系统提示词、规划提示词、托管代理提示词和最终答案提示词。
tags:
  - prompts
  - templates
  - jinja2
  - system-prompt
  - planning
generated: true
status: current
stale_after: 2026-03-01
sources:
  - F-091
  - F-092
  - F-093
  - F-094
  - F-095
  - F-096
  - F-097
  - F-098
  - F-099
  - F-100
  - F-101
  - F-102
  - F-103
  - F-104
  - F-105
  - F-106
  - F-107
  - F-108
  - F-109
  - F-110
  - F-147
  - F-148
  - F-149
  - F-150
  - F-151
  - F-152
  - F-153
  - F-154
  - F-155
---

# 提示词模板参考

本文档描述 Gode Agents 的提示词模板系统，包括类型定义、模板渲染函数、默认提示词结构和Jinja2变量。

## 概述

Gode Agents 使用基于 Jinja2 的提示词模板系统，通过 `PromptTemplates` 类型定义四类提示词：系统提示词、规划提示词、托管代理提示词和最终答案提示词。`ToolCallingAgent` 和 `CodeAgent` 分别从 `toolcalling_agent.yaml` 和 `code_agent.yaml` 加载默认提示词模板。

## 提示词模板类型

### PlanningPromptTemplate

规划步骤的提示词模板类型（F-091~F-109）。

```python
class PlanningPromptTemplate(TypedDict):
    """规划步骤提示词模板"""
    initial_facts: str
    initial_plan: str
    update_facts_pre_messages: str
    update_facts_post_messages: str
    update_plan_pre_messages: str
    update_plan_post_messages: str
```

**字段说明**：
- `initial_facts`: 初始事实调查提示词
- `initial_plan`: 初始计划提示词
- `update_facts_pre_messages`: 更新事实前置消息
- `update_facts_post_messages`: 更新事实后置消息
- `update_plan_pre_messages`: 更新计划前置消息
- `update_plan_post_messages`: 更新计划后置消息

### ManagedAgentPromptTemplate

托管代理的提示词模板类型（F-112~F-122）。

```python
class ManagedAgentPromptTemplate(TypedDict):
    """托管代理提示词模板"""
    task: str
    report: str
```

**字段说明**：
- `task`: 任务分配提示词模板
- `report`: 结果报告提示词模板

### FinalAnswerPromptTemplate

最终答案的提示词模板类型（F-125~F-135）。

```python
class FinalAnswerPromptTemplate(TypedDict):
    """最终答案提示词模板"""
    pre_messages: str
    post_messages: str
```

**字段说明**：
- `pre_messages`: 最终答案生成前置消息
- `post_messages`: 最终答案生成后置消息

### PromptTemplates

完整的代理提示词模板集合（F-138~F-152）。

```python
class PromptTemplates(TypedDict):
    """代理提示词模板集合"""
    system_prompt: str
    planning: PlanningPromptTemplate
    managed_agent: ManagedAgentPromptTemplate
    final_answer: FinalAnswerPromptTemplate
```

**字段说明**：
- `system_prompt`: 系统提示词，定义代理角色、能力、工具列表和行为规则
- `planning`: 规划步骤提示词模板
- `managed_agent`: 托管代理调用提示词模板
- `final_answer`: 最终答案生成提示词模板

## 空提示词模板

`EMPTY_PROMPT_TEMPLATES` 提供空的默认模板（F-155~F-167）：

```python
EMPTY_PROMPT_TEMPLATES = PromptTemplates(
    system_prompt="",
    planning=PlanningPromptTemplate(
        initial_facts="",
        initial_plan="",
        update_facts_pre_messages="",
        update_facts_post_messages="",
        update_plan_pre_messages="",
        update_plan_post_messages="",
    ),
    managed_agent=ManagedAgentPromptTemplate(task="", report=""),
    final_answer=FinalAnswerPromptTemplate(pre_messages="", post_messages=""),
)
```

## 模板渲染函数

### populate_template

使用 Jinja2 渲染提示词模板（F-078~F-088）。

```python
def populate_template(compiled_template: str, variables: dict) -> str:
    """
    使用 Jinja2 渲染模板。

    Args:
        compiled_template: Jinja2 模板字符串
        variables: 模板变量字典

    Returns:
        渲染后的字符串

    Raises:
        Exception: 模板渲染错误
    """
```

**使用示例**：
```python
system_prompt = populate_template(
    self.prompt_templates["system_prompt"],
    variables={"tools": self.tools, "managed_agents": self.managed_agents},
)
```

## 系统提示词

系统提示词定义代理的角色、能力、工作流程、示例、工具列表和行为规则。

### ToolCallingAgent 系统提示词结构

`ToolCallingAgent` 的系统提示词采用伪代码风格定义（F-147~F-154）：

```yaml
system_prompt: |-
  agent = {
    'role': 'expert_assistant',
    'capability': 'solve_any_task',
    'method': 'tool_calls',
    'tools': 'available'
  }
  cycle = {
    'Action': {
      'format': 'json',
      'fields': ['name', 'arguments'],
      'output': 'observation'
    },
    'Observation': {
      'type': 'string',
      'usage': 'next_action_input',
      'example': 'represent a file, like image_1.jpg'
    }
  }
  # ... 示例 ...
  # Tool List (Jinja2 循环)
  {%- for tool in tools.values() %}
  - {{ tool.name }}: {{ tool.description }}
      Takes inputs: {{tool.inputs}}
      Returns an output of type: {{tool.output_type}}
  {%- endfor %}
  # Team List (条件渲染)
  {%- if managed_agents and managed_agents.values() | list %}
  {%- for agent in managed_agents.values() %}
  - {{ agent.name }}: {{ agent.description }}
  {%- endfor %}
  {%- endif %}
  rules = [
    '1: ALWAYS provide tool call, else fail.',
    '2: Use correct tool args (values, not vars).',
    '3: Call tools ONLY when needed. Use final_answer if NO tool needed.',
    '4: NEVER repeat tool calls with same params.'
  ]
```

**关键特性**：
- 动作格式：JSON格式 `{"name": "...", "arguments": {...}}`
- 循环：Action → Observation → Action → ...
- 必须调用 `final_answer` 工具结束任务
- 支持图片/音频等文件类型输出（存储在 state 中）

### CodeAgent 系统提示词结构

`CodeAgent` 的系统提示词定义 Thought-Code-Observation 循环（F-148）：

```yaml
system_prompt: |-
  config = {
      'role': 'expert_assistant',
      'goal': 'solve_best',
      'method': 'step_plan',
      'tools': 'python_callable',
      'cycle': [Thought:, Code:, Observation:],
      'plan': {
          'Thought': ['Explain reasoning', 'List tools'],
          'Code': {
              'lang': 'python',
              'end': '<end_code>',
              'output': 'print'
          },
          'Observation': 'Report output',
          'Final': 'final_answer'
      }
  }
  # ... 示例 ...
  rules = [
      "1: Always write 'Thought:' and 'Code:' with ```py...```<end_code>",
      "2: Only use defined vars; no fake or notional ones",
      "3: Use tool(args...) directly, not dicts",
      "4: Avoid chaining tools with unknown outputs; use print() between",
      "5: Call tools only when needed; don't repeat same call",
      "6: Don't name vars like tools (e.g., 'search')",
      "7: Only import from: {{authorized_imports}}",
      "8: State (vars, imports) persists across blocks",
      "9: You must solve the task, not just suggest how"
  ]
```

**关键特性**：
- 代码格式：Markdown Python 代码块 ` ```py ... ```<end_code>`
- 循环：Thought → Code → Observation → ...
- 使用 `final_answer()` 函数返回结果
- Python 状态（变量、导入）跨代码块持久化
- 仅允许从 `authorized_imports` 列表导入

### initialize_system_prompt 方法

`MultiStepAgent` 子类实现此方法生成系统提示词（F-484~F-486, F-953~F-958）：

```python
class MultiStepAgent:
    def initialize_system_prompt(self):
        """在子类中实现"""
        pass

class ToolCallingAgent(MultiStepAgent):
    def initialize_system_prompt(self) -> str:
        system_prompt = populate_template(
            self.prompt_templates["system_prompt"],
            variables={"tools": self.tools, "managed_agents": self.managed_agents},
        )
        return system_prompt
```

## 规划提示词

规划提示词在 `planning_interval` 不为 None 时，每 N 步触发一次规划步骤。

### 初始计划提示词

`initial_plan` 模板用于首次规划（F-133~F-220）：

**结构**：
1. **Survey 部分**（事实调查）：
   - `# 1. Given`: 任务中给出的事实
   - `# 2. Lookup`: 需要查找的信息
   - `# 3. Derive`: 需要推导的信息

2. **Plan 部分**（计划函数）：
   - `def plan():` 定义高级逻辑步骤
   - 使用概念函数：`lookup()`, `convert_data()`, `translate()`, `final_answer()` 等

**Jinja2 变量**：
- `{{task}}`: 当前任务字符串
- `{{tools}}`: 工具字典（循环渲染工具列表）
- `{{managed_agents}}`: 托管代理字典（条件渲染）

**格式示例**：
```python
# Survey
# 1. Given
task = "..."
source_doc = "..."
# 2. Lookup
section = lookup_document(content=target)
# 3. Derive
result = process(input=section)
# Plan
def plan():
    section = lookup_document(content=target)
    result = process(input=section)
    final_answer(result)
```

### 更新计划提示词

`update_plan_pre_messages` 和 `update_plan_post_messages` 用于计划更新（F-221~F-354）：

**结构**：
1. **Survey Update 部分**：
   - `# 1. Given`: 原始任务中未变化的事实
   - `# 2. Learned`: 新获取或推导出的事实
   - `# 3. To Lookup`: 仍需查找的信息
   - `# 4. To Derive`: 仍需推导的信息

2. **Plan Update 部分**：
   - `def plan_update():` 定义更新后的计划步骤

**Jinja2 变量**：
- `{{task}}`: 原始任务
- `{{remaining_steps}}`: 剩余步骤数
- `{{tools}}`: 工具字典
- `{{managed_agents}}`: 托管代理字典

### _create_planning_step 方法

创建规划步骤的内部方法（F-412~F-471）：

```python
def _create_planning_step(self, task, is_first_step: bool, step: int) -> PlanningStep:
    """
    创建规划步骤。

    首次规划使用 initial_plan 模板，
    后续更新使用 update_plan_pre_messages + 历史消息 + update_plan_post_messages。
    """
```

## 托管代理提示词

托管代理提示词用于主代理调用子代理时的任务包装和结果包装。

### 任务提示词

`managed_agent.task` 模板用于包装子代理任务（F-355~F-371, F-412~F-428）：

**ToolCallingAgent 格式**：
```text
role = 'helper_agent'
name = '{{name}}'
task_source = 'manager'
task = '{{task}}'
# ... 其他伪代码指令 ...
### 1. Task outcome (short version):
### 2. Task outcome (extremely detailed version):
### 3. Additional context (if relevant):
```

**CodeAgent 格式**：
```text
role = 'helper_agent'
name = '{{name}}'
task_source = 'manager'
task = '{{task}}'
# ... 其他伪代码指令 ...
## 1.Task result (short version)
## 2.Task result (very detailed version)
## 3.Additional background (if relevant)
```

**Jinja2 变量**：
- `{{name}}`: 子代理名称
- `{{task}}`: 分配给子代理的任务

### 报告提示词

`managed_agent.report` 模板用于包装子代理返回结果（F-372~F-374, F-429~F-431）：

```text
final_answer =  {{final_answer}}
source_agent = {{name}}
```

**Jinja2 变量**：
- `{{name}}`: 子代理名称
- `{{final_answer}}`: 子代理返回的最终答案

### __call__ 方法

托管代理调用时使用提示词模板包装任务和结果（F-588~F-606）：

```python
def __call__(self, task: str, **kwargs):
    """托管代理调用入口：包装任务→执行→包装结果"""
    full_task = populate_template(
        self.prompt_templates["managed_agent"]["task"],
        variables=dict(name=self.name, task=task),
    )
    report = self.run(full_task, **kwargs)
    answer = populate_template(
        self.prompt_templates["managed_agent"]["report"],
        variables=dict(name=self.name, final_answer=report),
    )
    if self.provide_run_summary:
        # 附加运行摘要
        answer += "\n\nFor more detail, find below a summary of this agent's work:\n<summary_of_work>\n"
        for message in self.write_memory_to_messages(summary_mode=True):
            content = message["content"]
            answer += "\n" + truncate_content(str(content)) + "\n---"
        answer += "\n</summary_of_work>"
    return answer
```

## 最终答案提示词

最终答案提示词用于任务完成后从对话历史中提取最终答案。

### 提示词结构

`final_answer` 模板分为前置消息和后置消息（F-375~F-382, F-432~F-439）：

```yaml
final_answer:
  pre_messages: |-
    agent_failed = True
    your_task = provide answers
    agent_memory = <MEMORY_BELOW>
  post_messages: |-
    from_above = True
    answer_for = {{task}}
```

### provide_final_answer 方法

使用最终答案提示词生成最终答案（F-531~F-573）：

```python
def provide_final_answer(self, task: str, images: Optional[list["PIL.Image.Image"]]) -> str:
    """
    基于交互日志提供任务的最终答案。

    构建消息序列：
    1. System消息：pre_messages
    2. 历史消息（不含原始system prompt）
    3. User消息：post_messages（含{{task}}变量）

    Args:
        task: 要执行的任务
        images: 可选的图片对象列表

    Returns:
        最终答案字符串
    """
    messages = [
        {
            "role": MessageRole.SYSTEM,
            "content": [
                {
                    "type": "text",
                    "text": self.prompt_templates["final_answer"]["pre_messages"],
                }
            ],
        }
    ]
    if images:
        messages[0]["content"].append({"type": "image"})
    messages += self.write_memory_to_messages()[1:]  # 跳过system prompt
    messages += [
        {
            "role": MessageRole.USER,
            "content": [
                {
                    "type": "text",
                    "text": populate_template(
                        self.prompt_templates["final_answer"]["post_messages"],
                        variables={"task": task}
                    ),
                }
            ],
        }
    ]
    try:
        chat_message: ChatMessage = self.model(messages)
        return chat_message.content
    except Exception as e:
        return f"Error in generating final LLM output:\n{e}"
```

## 默认提示词文件

### 加载方式

`ToolCallingAgent` 和 `CodeAgent` 在构造函数中从 YAML 文件加载默认提示词（F-942~F-944, F-1160~F-1162）：

```python
class ToolCallingAgent(MultiStepAgent):
    def __init__(self, ..., prompt_templates=None, ...):
        prompt_templates = prompt_templates or yaml.safe_load(
            importlib.resources.files("smolagents.prompts")
                .joinpath("toolcalling_agent.yaml")
                .read_text(encoding='utf-8')
        )
        super().__init__(..., prompt_templates=prompt_templates, ...)

class CodeAgent(MultiStepAgent):
    def __init__(self, ..., prompt_templates=None, ...):
        prompt_templates = prompt_templates or yaml.safe_load(
            importlib.resources.files("smolagents.prompts")
                .joinpath("code_agent.yaml")
                .read_text(encoding='utf-8')
        )
        super().__init__(..., prompt_templates=prompt_templates, ...)
```

### 自定义提示词

用户可以通过 `prompt_templates` 参数传入自定义提示词：

```python
import yaml

# 从自定义YAML文件加载
with open("my_prompts.yaml", "r", encoding="utf-8") as f:
    custom_prompts = yaml.safe_load(f)

agent = CodeAgent(
    tools=[my_tool],
    model=my_model,
    prompt_templates=custom_prompts,
)
```

### 导出提示词

`save()` 方法会将当前使用的提示词模板导出为 `prompts.yaml`（F-641~F-653）：

```python
def save(self, output_dir: str | Path, relative_path: Optional[str] = None):
    # ...
    yaml_prompts = yaml.safe_dump(
        self.prompt_templates,
        default_style="|",  # 强制使用块字面量
        default_flow_style=False,
        width=float("inf"),
        sort_keys=False,
        allow_unicode=True,
        indent=2,
    )
    with open(os.path.join(output_dir, "prompts.yaml"), "w", encoding="utf-8") as f:
        f.write(yaml_prompts)
```

## Jinja2 模板变量

所有提示词模板中可用的 Jinja2 变量：

| 变量 | 类型 | 说明 | 使用位置 |
|------|------|------|----------|
| `tools` | `dict[str, Tool]` | 工具字典，键为工具名 | system_prompt, planning |
| `managed_agents` | `dict[str, MultiStepAgent]` | 托管代理字典 | system_prompt, planning |
| `task` | `str` | 当前任务字符串 | planning.initial_plan, planning.update_plan_pre_messages, final_answer.post_messages, managed_agent.task |
| `remaining_steps` | `int` | 剩余步骤数 | planning.update_plan_post_messages |
| `name` | `str` | 代理名称 | managed_agent.task, managed_agent.report |
| `final_answer` | `Any` | 子代理返回的最终答案 | managed_agent.report |
| `authorized_imports` | `list[str]` | 授权导入的Python模块列表 | CodeAgent system_prompt |

### Jinja2 语法支持

模板支持标准 Jinja2 语法：
- `{% for ... %}` / `{% endfor %}`: 循环
- `{% if ... %}` / `{% endif %}`: 条件
- `{{ variable }}`: 变量插值
- `{{ value | filter }}`: 过滤器（如 `repr`, `camelcase`）

## 提示词设计原则

### 伪代码风格

Gode Agents 的提示词采用伪代码（pseudocode）风格而非自然语言描述：
- 使用变量赋值（`key = 'value'`）
- 使用字典/列表结构（`rules = [...]`）
- 使用条件语句注释（`if not final_answer:`）
- 这种格式对LLM更结构化，减少歧义

### 示例驱动

系统提示词包含多个完整示例（Few-shot）：
- 简单工具调用示例
- 多步推理示例
- 错误恢复示例
- 计算示例

### 规则列表

系统提示词末尾有明确的编号规则列表：
- ToolCallingAgent: 4条核心规则
- CodeAgent: 9条核心规则（含导入限制、变量命名等）

## 相关概念

- MultiStepAgent 执行循环
- ToolCallingAgent JSON工具调用
- CodeAgent Python代码执行
- 规划步骤机制
- 托管代理系统
- AgentMemory 记忆系统
