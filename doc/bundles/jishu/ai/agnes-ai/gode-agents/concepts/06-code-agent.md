---
type: Concept
title: CodeAgent：代码执行范式
description: CodeAgent基于Python代码块执行的CodeAct范式、Python执行器集成、导入授权
tags: [智能体, CodeAgent, CodeAct, 代码执行]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:20:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: F-039
    resource: /references/agents-api.md
    title: Agents API 参考
  - id: F-110
    resource: /references/executor-api.md
    title: Executor API 参考
---

# CodeAgent：代码执行范式

## 概述

`CodeAgent` 是 GodeAgents 提供的另一种核心智能体类型，继承自 `MultiStepAgent`，实现了 **CodeAct**（Code as Action）范式——让 LLM 生成 Python 代码块作为"行动语言"，通过安全的 Python 执行器运行代码，将输出作为观察结果反馈给模型继续推理。

与 ToolCallingAgent 的 JSON function calling 不同，CodeAgent 不向模型传递 `tools_to_call_from`，而是将工具代码直接注入到 Python 执行器的命名空间中，模型可以在一个代码块内自由组合多个工具、使用变量、编写循环和条件逻辑，表达能力远强于单步单工具的 function calling 模式。

> 事实溯源：F-039~F-046、F-105~F-119

## 核心概念

### CodeAct 范式

CodeAct 的核心理念是：**代码是通用的行动语言**。与其让模型只能在预定义的工具中做选择（function calling），不如让模型编写 Python 代码——代码本身就是一种结构化、可执行、表达能力极强的"行动"。模型可以：
- 在一个代码块中调用多个工具
- 用变量存储中间结果
- 使用 for/while 循环处理列表数据
- 使用 if/else 做条件分支
- 直接进行数学计算和数据处理
- 调用任何授权的 Python 标准库模块

### 工具通过命名空间注入

CodeAgent **不使用** `tools_to_call_from` 参数。它通过 `create_python_executor()` 创建执行器，调用 `send_tools()` 将工具代码通过 `get_tools_definition_code(tools)` 生成代码字符串，在执行器的受限命名空间中 `exec()` 执行，使工具函数直接作为 Python 函数可用。模型在代码块中像调用普通函数一样调用工具。

### 安全沙箱执行

CodeAgent 通过 `PythonExecutor` 在受限环境中执行模型生成的代码，提供多层安全保障：
- **导入白名单**：只允许导入 `BASE_BUILTIN_MODULES`（Python标准库安全子集）和用户额外授权的模块
- **危险模块/函数黑名单**：`builtins`、`os`、`subprocess`、`socket` 等危险模块，以及 `eval`、`exec`、`compile`、`__import__` 等危险函数被禁止
- **AST 静态检查**：`_check_imports` AST 访问器在执行前解析代码，验证所有 import 语句的安全性
- **操作次数限制**：`MAX_OPERATIONS=10000000`、`MAX_WHILE_ITERATIONS=1000000` 防止无限循环
- **输出截断**：`DEFAULT_MAX_LEN_OUTPUT=50000` 防止输出过长

> 事实溯源：F-105~F-107、F-114

## API 要点

### 构造参数

CodeAgent 继承 MultiStepAgent 的所有参数，并添加以下特有参数：

```python
CodeAgent(
    tools: List[Tool],
    model: Model,
    prompt_templates: Optional[PromptTemplates] = None,
    planning_interval: Optional[int] = None,
    # CodeAgent特有参数
    additional_authorized_imports: Optional[List[str]] = None,
    executor_type: str = "local",
    executor_kwargs: Optional[Dict[str, Any]] = None,
    max_print_outputs_length: Optional[int] = None,
    **kwargs,
)
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `additional_authorized_imports` | `None` | 额外授权导入的 Python 模块列表，`"*"` 表示全部授权（有警告） |
| `executor_type` | `"local"` | 执行器类型：`"local"`、`"e2b"`、`"docker"` |
| `executor_kwargs` | `None` | 传递给执行器构造函数的额外参数 |
| `max_print_outputs_length` | `None` | print 输出的最大长度，None 时使用默认值 50000 |

> 事实溯源：F-040

### 导入授权机制

```python
authorized_imports = sorted(set(BASE_BUILTIN_MODULES) | set(additional_authorized_imports or []))
```

- `BASE_BUILTIN_MODULES` 是一组经过安全审查的 Python 标准库模块（math、json、datetime、collections、re、random 等）
- 用户通过 `additional_authorized_imports` 添加额外需要的模块
- 当 `additional_authorized_imports` 包含 `"*"` 时，框架输出警告（表示允许导入任意模块，存在安全风险）
- 导入安全通过 AST 静态检查在执行前验证

> 事实溯源：F-041、F-105~F-107

### 默认提示模板

CodeAgent 默认从 `code_agent.yaml` 读取提示模板，指示模型：
- 使用 ` ```py ` 代码块编写 Python 代码
- 工具在命名空间中作为函数直接可用
- 使用 `final_answer()` 函数返回最终答案
- 可以在代码中使用变量、循环、条件等 Python 特性

> 事实溯源：F-042

### create_python_executor()：执行器工厂

```python
def create_python_executor(self) -> PythonExecutor
```

根据 `executor_type` 创建不同的执行器：

| executor_type | 执行器类 | 说明 |
|---------------|----------|------|
| `"local"` | `LocalPythonExecutor` | 本地进程内执行（默认） |
| `"e2b"` | `E2BExecutor` | 通过 E2B Sandbox 云端执行 |
| `"docker"` | `DockerExecutor` | 通过 Docker 容器+Jupyter Kernel Gateway 执行 |
| 其他值 | — | 抛出 `ValueError` |

> 事实溯源：F-043

### initialize_system_prompt()

```python
def initialize_system_prompt(self) -> str
```

渲染 system_prompt 时传入三个模板变量（比 ToolCallingAgent 多了 `authorized_imports`）：
- `tools`：可用工具列表的描述
- `managed_agents`：被管理子 Agent 列表的描述
- `authorized_imports`：授权导入的模块列表

> 事实溯源：F-044

### step() 核心流程

```python
def step(self, memory_step: ActionStep) -> Union[None, Any]
```

step() 方法执行以下流程：

1. **调用模型**：将记忆序列化为消息列表，调用 `model(input_messages, stop_sequences=["<end_code>", "Observation:", "Calling tools:"])`
   - **注意**：不传 `tools_to_call_from`！模型不使用 function calling，而是输出代码块
   - `stop_sequences` 包含 `"<end_code>"` 确保模型在代码块结束处停止
2. **解析代码**：用 `parse_code_blobs()` 从模型输出中提取 ` ```py ` 代码块，再用 `fix_final_answer_code()` 修复 `final_answer` 变量赋值问题
3. **执行代码**：调用 `python_executor(code_action)`，返回三元组 `(output, execution_logs, is_final_answer)`
4. **判断终止**：若 `is_final_answer=True`，返回 `output` 作为 final_answer
5. **记录观察**：将 `execution_logs` 作为观察记录到 memory_step，返回 None 继续循环

> 事实溯源：F-045

### 执行器返回值

`python_executor(code)` 返回 `(output, execution_logs, is_final_answer)` 三元组：

| 返回值 | 类型 | 说明 |
|--------|------|------|
| `output` | Any | 代码执行的输出值（print 输出或 final_answer 参数） |
| `execution_logs` | str | 执行日志，包含 print 输出、错误信息等 |
| `is_final_answer` | bool | 是否调用了 `final_answer()` 函数（True 表示任务完成） |

执行器通过检测 `final_answer_pattern` 正则和 `FinalAnswerException` 异常来判断是否为最终答案。`state` 中的 `final_answer` 函数会抛出 `FinalAnswerException`，执行器捕获该异常并设置 `is_final_answer=True`。

> 事实溯源：F-111、F-115

### to_dict() 序列化

CodeAgent 的 `to_dict()` 方法在基类基础上追加四个特有字段：
- `authorized_imports`
- `executor_type`
- `executor_kwargs`
- `max_print_outputs_length`

> 事实溯源：F-046

### LocalPythonExecutor 关键机制

```python
class LocalPythonExecutor(PythonExecutor):
    def __init__(self, additional_imports=None, max_print_outputs_length=None):
        self.state = {
            "final_answer": _final_answer_function,  # 抛FinalAnswerException
            "__builtins__": restricted_builtins,     # 安全builtins子集
            "authorized_imports": authorized_imports,
        }
```

- **state 字典**：维护跨代码块的持久状态，变量定义在多个 step 间保留
- **send_tools()**：通过 `get_tools_definition_code(tools)` 生成工具定义代码并在命名空间 exec
- **send_variables()**：将 variables dict 更新到 state
- **run_code_raise_errors()**：核心执行方法——`ast.parse` 解析代码 → `_check_imports` 验证安全 → `compile` + `exec` 在受限命名空间执行

> 事实溯源：F-112~F-117、F-119

### 远程执行器

- **E2BExecutor**（`RemotePythonExecutor`）：使用 `e2b_code_interpreter.Sandbox` 在 E2B 云端沙箱执行，`send_variables` 使用 pickle+base64 序列化
- **DockerExecutor**（`RemotePythonExecutor`）：通过 Jupyter Kernel Gateway 在 Docker 容器中执行，WebSocket 通信

> 事实溯源：F-148~F-150

## 代码示例

### 基础 CodeAgent

```python
from codified_smolagents import CodeAgent, HfApiModel

model = HfApiModel()

# 最简CodeAgent：无需手动添加工具，Python内置能力即可处理计算任务
agent = CodeAgent(
    tools=[],  # 空工具列表，依靠代码执行能力
    model=model,
    additional_authorized_imports=['math'],
    max_steps=5,
)

result = agent.run("计算从1到100所有质数的和")
print(result)
```

### 带额外导入授权的 CodeAgent

```python
from codified_smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel

model = HfApiModel()

agent = CodeAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    # 授权额外模块导入
    additional_authorized_imports=['math', 'datetime', 'statistics', 'collections', 'json'],
    executor_type='local',  # 使用本地执行器（默认）
    max_print_outputs_length=10000,  # 限制print输出长度
    max_steps=15,
    planning_interval=3,
)

result = agent.run("""
搜索2024年全球GDP排名前5的国家，
然后用Python计算它们GDP的平均值和标准差
""")
print(result)
```

### 多工具代码组合

```python
from codified_smolagents import (
    CodeAgent,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    WikipediaSearchTool,
    HfApiModel,
)

model = HfApiModel()

agent = CodeAgent(
    tools=[
        DuckDuckGoSearchTool(),
        VisitWebpageTool(),
        WikipediaSearchTool(),
    ],
    model=model,
    additional_authorized_imports=['json', 're', 'collections'],
    max_steps=20,
)

# 在一个代码块中，模型可以：
# 1. 调用web_search搜索
# 2. 用visit_webpage获取页面内容
# 3. 用正则提取信息
# 4. 用collections统计
# 5. 最终final_answer()返回结果
result = agent.run("""
搜索"Python 3.12 release notes"，访问相关页面，
提取所有新特性名称，按类别统计数量，以JSON格式返回
""")
print(result)
```

### 使用 Docker 执行器

```python
from codified_smolagents import CodeAgent, HfApiModel

model = HfApiModel()

agent = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=['math', 'numpy'],
    executor_type='docker',  # 在Docker容器中隔离执行
    executor_kwargs={'image': 'python:3.12-slim'},  # Docker镜像配置
    max_steps=10,
)

result = agent.run("用numpy计算一个100x100随机矩阵的特征值")
print(result)
```

### 跨步骤状态保持

```python
from codified_smolagents import CodeAgent, HfApiModel

model = HfApiModel()

agent = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=['math'],
    max_steps=10,
)

# CodeAgent的执行器state在步骤间保持
# 模型可以在第一步定义变量，后续步骤直接引用
result = agent.run("""
第一步：计算 fibonacci(30) 并存储在变量result中
第二步：判断result是否为质数
第三步：返回最终判断结果
""")
print(result)
```

> 事实溯源：F-039~F-046、F-105~F-119

### step() 执行流程图

```mermaid
sequenceDiagram
    participant Loop as _run()循环
    participant Step as step()
    participant Mem as write_memory_to_messages()
    participant Model as Model
    participant Parser as parse_code_blobs()<br/>+fix_final_answer_code()
    participant Exec as python_executor
    participant State as 受限命名空间state

    Loop->>Step: step(memory_step)
    Step->>Mem: 序列化记忆为消息列表
    Mem-->>Step: input_messages
    Step->>Model: model(input_messages,<br/>stop_sequences=["<end_code>","Observation:","Calling tools:"])
    Note over Step,Model: 不传tools_to_call_from！
    Model-->>Step: ChatMessage(content=代码文本)
    Step->>Parser: 提取```py代码块+修复final_answer
    Parser-->>Step: code_action(Python代码)
    Step->>Exec: python_executor(code_action)
    Exec->>State: ast.parse + _check_imports(安全检查)
    Exec->>State: compile + exec(受限命名空间)
    State-->>Exec: 执行结果/FinalAnswerException
    Exec-->>Step: (output, execution_logs, is_final_answer)

    alt is_final_answer == True
        Step-->>Loop: 返回output(任务完成)
    else 继续执行
        Step->>Step: 记录execution_logs为observation
        Step-->>Loop: 返回None(继续循环)
    end
```

> 事实溯源：F-043~F-045、F-110~F-119

## 常见问题/注意事项

### CodeAgent 不使用 function calling

CodeAgent 调用模型时**不传** `tools_to_call_from` 参数。模型不输出结构化的 tool_calls，而是输出包含 Python 代码块的文本。这意味着 CodeAgent 可以使用不支持 function calling 的模型（只要模型能生成 Python 代码），但代码解析依赖 `parse_code_blobs()` 正确识别 ` ```py ` 代码块。

### final_answer() 函数机制

在 CodeAgent 中，`final_answer` 不是一个"工具调用"，而是执行器命名空间中的一个特殊函数。调用它会抛出 `FinalAnswerException`，执行器捕获该异常后设置 `is_final_answer=True`，将参数作为最终答案返回。`fix_final_answer_code()` 会修复模型偶尔输出 `final_answer = xxx` 而非 `final_answer(xxx)` 的情况。

### 工具命名空间注入方式

ToolCallingAgent 通过 `tools_to_call_from` 将工具 Schema 传给模型，模型选择工具并输出 JSON 参数；CodeAgent 通过 `get_tools_definition_code(tools)` 生成工具的 Python 定义代码，在执行器命名空间中 exec，工具函数直接可用。模型在代码中像调用普通函数一样调用工具，例如 `result = web_search("Python 3.12")`。

### "*" 导入授权的风险

设置 `additional_authorized_imports=["*"]` 会输出警告，因为它允许模型导入任意 Python 模块，包括 `os`、`subprocess` 等危险模块。仅在完全信任模型输出且在隔离环境（如 Docker/E2B）中执行时使用。

### add_base_tools 不包含 python_interpreter

CodeAgent 的 `add_base_tools=True` 加载 `TOOL_MAPPING` 中除 `python_interpreter` 外的工具。这是因为 CodeAgent 本身就通过执行器具备 Python 代码执行能力，不需要额外的 Python 解释器工具。

> 事实溯源：F-018

### 本地执行器安全边界

LocalPythonExecutor 在同一进程内执行代码，虽然有导入白名单、危险函数黑名单、AST 检查、操作数限制等多层防护，但不是绝对安全的沙箱。执行不可信模型生成的代码时，推荐使用 `executor_type="docker"` 或 `"e2b"` 实现进程级/容器级隔离。

### BASE_PYTHON_TOOLS 安全内置函数

执行器的 `__builtins__` 不是完整的 Python builtins，而是 `BASE_PYTHON_TOOLS` 安全子集，包含 `print`（重定向为 custom_print）、`isinstance`、`range`、`len`、`sum`、`max`、`min`、`enumerate`、`zip`、`sorted`、类型转换函数（`int`、`str`、`float`、`list`、`dict`、`set`、`tuple`、`bool`）、数学函数（`abs`、`round`、`divmod`）等安全函数。

> 事实溯源：F-108

### 三种执行器对比

| 特性 | local | e2b | docker |
|------|-------|-----|--------|
| 隔离级别 | 进程内（受限命名空间） | 云端沙箱 | Docker容器 |
| 启动速度 | 最快（即时） | 快（沙箱复用） | 较慢（容器启动） |
| 安全性 | 基础防护 | 强隔离 | 强隔离 |
| 依赖要求 | 无额外依赖 | 需要e2b账号+SDK | 需要Docker环境 |
| 网络访问 | 继承宿主网络 | 沙箱网络 | 容器网络策略 |
| 适用场景 | 开发调试、可信任务 | 生产环境、不可信代码 | 自托管生产环境 |

## 相关链接

- [MultiStepAgent：核心推理循环](03-multi-step-agent.md) — 父类的run循环和step抽象
- [ToolCallingAgent：函数调用范式](05-tool-calling-agent.md) — 另一种智能体范式（function calling）
- [内置工具详解](08-builtin-tools.md) — 默认工具在CodeAgent中的使用
- [Agents API 参考](../references/agents-api.md) — CodeAgent完整API
- [Executor API 参考](../references/executor-api.md) — PythonExecutor及子类完整API
