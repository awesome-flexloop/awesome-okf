---
type: Concept
title: 监控与日志
description: AgentLogger日志系统、Monitor token计数、异常层次结构、工具函数
tags: [日志, 监控, AgentLogger, Monitor, 异常]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: F-126
    resource: /references/utils-api.md
    title: Utils API 参考
---

## 概述

GodeAgents 框架提供了完整的监控与日志体系，帮助开发者追踪 Agent 运行状态、诊断问题和统计资源消耗。核心组件包括：`AgentLogger`（基于 rich 的结构化日志系统）、`Monitor`（Token 用量计数器）、层次化的异常体系，以及一组实用的工具函数（代码块解析、内容截断、JSON 序列化、名称校验、工具验证等）。通过合理配置日志级别和使用监控工具，开发者可以清晰地观察 Agent 的每一步推理和执行过程。

> 事实溯源：F-126~F-152

## 核心概念

### LogLevel 四级日志控制

框架定义了四个日志级别，从静默到详细：

| 级别 | 值 | 说明 |
|------|----|------|
| `OFF` | 0 | 关闭所有日志输出 |
| `ERROR` | 1 | 仅输出错误信息 |
| `INFO` | 2 | 输出常规运行信息（默认级别） |
| `DEBUG` | 3 | 输出详细调试信息（含完整代码、消息内容等） |

日志级别是整数枚举，可以直接用数值比较进行过滤。

> 事实溯源：F-126

### AgentLogger：结构化日志系统

`AgentLogger` 是框架的核心日志类，内部使用 `rich.console.Console` 进行终端输出，提供多种格式化日志方法：

| 方法 | 用途 |
|------|------|
| `log(level, message, **kwargs)` | 基础日志输出 |
| `log_rule(title, **kwargs)` | 输出分隔线（带标题） |
| `log_task(task, **kwargs)` | 输出任务信息（格式化显示） |
| `log_markdown(content, **kwargs)` | 渲染并输出 Markdown 内容 |
| `log_code(code, language, **kwargs)` | 语法高亮输出代码块 |
| `log_error(exception, **kwargs)` | 格式化输出异常信息 |
| `visualize_agent_tree(agent, **kwargs)` | 可视化显示 Agent 层次结构树 |

这些方法为不同类型的信息提供了专门的格式化输出，使终端日志既美观又易读。

> 事实溯源：F-127

### Monitor：Token 用量监控

`Monitor` 类负责跟踪 Agent 运行过程中的 Token 消耗：

| 方法/属性 | 说明 |
|-----------|------|
| `last_input_token_count` | 最近一次模型调用的输入 Token 数 |
| `last_output_token_count` | 最近一次模型调用的输出 Token 数 |
| `update_metrics(step_log, agent)` | 根据步骤日志更新 Token 计数 |
| `__del__` | 析构时输出总 Token 使用量汇总 |

`Monitor` 在 Agent 运行时自动创建和更新，开发者可以通过 `agent.monitor` 访问。当 Monitor 对象被销毁时（通常是 Agent 运行结束），会自动输出累计的 Token 总消耗量。

> 事实溯源：F-128

### 异常层次结构

框架定义了以 `AgentError` 为基类的完整异常层次：

```
AgentError(Exception)           # Agent 异常基类
├── AgentParsingError           #   解析错误（模型输出解析失败）
├── AgentGenerationError        #   生成错误（模型调用/生成失败）
├── AgentExecutionError         #   执行错误（代码/工具执行失败）
├── AgentMaxStepsError          #   步骤超限（超过max_steps）
├── AgentToolCallError          #   工具调用错误（工具调用格式/参数错误）
└── AgentToolExecutionError     #   工具执行错误（工具内部运行异常）
```

这种分类使得开发者可以精确捕获和处理不同类型的错误：
- 解析错误通常意味着模型输出格式不符合预期
- 生成错误通常是 API 调用失败
- 执行错误是代码/工具运行时异常
- 步骤超限需要增大 max_steps 或优化任务
- 工具调用/执行错误帮助定位工具层面的问题

> 事实溯源：F-129

## API 要点

### AgentLogger 核心方法

```python
class AgentLogger:
    """基于rich Console的结构化日志器"""

    def __init__(self, level: int = LogLevel.INFO):
        """初始化日志器，指定日志级别"""
        ...

    def log(self, level: int, message: str, **kwargs):
        """输出指定级别的日志消息"""
        ...

    def log_rule(self, title: str = "", **kwargs):
        """输出水平分隔线，可选带标题"""
        ...

    def log_task(self, task: str, **kwargs):
        """格式化输出任务内容"""
        ...

    def log_markdown(self, content: str, **kwargs):
        """渲染Markdown并输出"""
        ...

    def log_code(self, code: str, language: str = "python", **kwargs):
        """语法高亮输出代码块"""
        ...

    def log_error(self, exception: Exception, **kwargs):
        """格式化输出异常信息和堆栈"""
        ...

    def visualize_agent_tree(self, agent, **kwargs):
        """可视化显示Agent及其managed_agents的树状结构"""
        ...
```

> 事实溯源：F-127

### 工具函数

```python
def parse_code_blobs(text: str) -> str:
    """从文本中提取```python代码块内容，用于解析CodeAgent的模型输出"""
    ...

def truncate_content(content: str, max_length: int = 5000) -> str:
    """截断超长内容，默认最大5000字符，防止日志/消息过长"""
    ...

def make_json_serializable(obj: Any) -> Any:
    """递归将对象转换为JSON可序列化格式（处理datetime/set/自定义对象等）"""
    ...

def is_valid_name(name: str) -> bool:
    """检查名称是否为有效的Python标识符且非保留字（用于工具/Agent命名校验）"""
    ...

def parse_json_blob(text: str) -> dict:
    """从文本中提取JSON对象，用于解析ToolCallingAgent的工具调用"""
    ...

def get_imports(code: str) -> List[str]:
    """从代码字符串中提取顶层import语句的模块名列表"""
    ...
```

> 事实溯源：F-131~F-139

### MethodChecker 与 validate_tool_attributes

```python
class MethodChecker(ast.NodeVisitor):
    """AST访问器，检查Tool方法（forward）中是否使用了未定义的名称"""
    ...

def validate_tool_attributes(cls, check_imports: bool = True) -> None:
    """
    用AST分析验证Tool子类的正确性：
    - 检查name/description/inputs/output_type是否定义
    - 检查forward方法签名
    - check_imports=True时检查方法中的import和未定义名称
    验证失败时抛出异常。
    """
    ...
```

`validate_tool_attributes` 在 Tool 实例化时自动调用，确保工具定义的正确性。`MethodChecker` 使用 AST 分析检查 forward 方法中引用的名称是否都有定义（包括参数、导入和内置函数），帮助在工具加载阶段发现潜在的 NameError。

> 事实溯源：F-151~F-152

## 代码示例

### 配置日志级别

```python
from codified_smolagents import CodeAgent, HfApiModel
from codified_smolagents.utils import LogLevel

model = HfApiModel()

# 默认级别 INFO：输出常规运行信息
agent = CodeAgent(tools=[], model=model, additional_authorized_imports=['math'], max_steps=3)
result = agent.run("计算 2**20")

# DEBUG 级别：输出详细调试信息（完整代码、消息历史等）
agent_debug = CodeAgent(
    tools=[], model=model,
    additional_authorized_imports=['math'],
    max_steps=3,
    verbosity_level=LogLevel.DEBUG,
)
result = agent_debug.run("计算 2**20")

# ERROR 级别：仅输出错误信息
agent_quiet = CodeAgent(
    tools=[], model=model,
    additional_authorized_imports=['math'],
    max_steps=3,
    verbosity_level=LogLevel.ERROR,
)
result = agent_quiet.run("计算 2**20")

# OFF 级别：静默模式，无任何输出
agent_silent = CodeAgent(
    tools=[], model=model,
    additional_authorized_imports=['math'],
    max_steps=3,
    verbosity_level=LogLevel.OFF,
)
result = agent_silent.run("计算 2**20")
```

### 直接使用 AgentLogger

```python
from codified_smolagents.utils import AgentLogger, LogLevel

# 创建日志器
logger = AgentLogger(level=LogLevel.DEBUG)

# 基础日志
logger.log(LogLevel.INFO, "Agent启动中...")
logger.log(LogLevel.DEBUG, "详细调试信息：变量x=42")
logger.log(LogLevel.ERROR, "发生错误！")

# 分隔线
logger.log_rule(title="步骤 1：思考")

# 输出代码（语法高亮）
code = """
import math
result = math.sqrt(16)
final_answer(result)
"""
logger.log_code(code, language="python")

# 输出Markdown
logger.log_markdown("""
## 执行结果

- 计算完成
- 结果: **4.0**
""")

# 输出任务
logger.log_task("计算从1到100的所有质数")
```

### 使用 Monitor 查看 Token 用量

```python
from codified_smolagents import CodeAgent, HfApiModel

model = HfApiModel()
agent = CodeAgent(tools=[], model=model, additional_authorized_imports=['math'], max_steps=5)

result = agent.run("计算1到100的和")

# 访问Monitor查看Token统计
monitor = agent.monitor
print(f"最近输入Token: {monitor.last_input_token_count}")
print(f"最近输出Token: {monitor.last_output_token_count}")

# 通过model也可以查看Token计数
print(f"模型Token统计: {model.get_token_counts()}")
# Monitor析构时会自动输出总Token用量
```

### 异常捕获与处理

```python
from codified_smolagents import CodeAgent, HfApiModel
from codified_smolagents.utils import (
    AgentError, AgentParsingError, AgentGenerationError,
    AgentExecutionError, AgentMaxStepsError,
    AgentToolCallError, AgentToolExecutionError,
)

model = HfApiModel()
agent = CodeAgent(tools=[], model=model, additional_authorized_imports=['math'], max_steps=3)

try:
    result = agent.run("一个非常复杂的任务，可能需要很多步骤")
except AgentMaxStepsError:
    print("错误：Agent执行步骤超过max_steps限制，请增加max_steps或简化任务")
except AgentParsingError as e:
    print(f"错误：模型输出解析失败 - {e}")
    print("可能原因：模型未按预期格式输出代码块")
except AgentExecutionError as e:
    print(f"错误：代码执行失败 - {e}")
    print("可能原因：生成的代码有语法错误或运行时异常")
except AgentGenerationError as e:
    print(f"错误：模型生成失败 - {e}")
    print("可能原因：API调用失败、网络问题或模型服务不可用")
except AgentToolCallError as e:
    print(f"错误：工具调用格式错误 - {e}")
except AgentToolExecutionError as e:
    print(f"错误：工具执行异常 - {e}")
except AgentError as e:
    print(f"Agent运行错误（通用）: {e}")
```

### 使用工具函数

````python
from codified_smolagents.utils import (
    parse_code_blobs, truncate_content, make_json_serializable,
    is_valid_name, parse_json_blob, get_imports,
)

# parse_code_blobs：从文本提取Python代码块
text = """我来帮你计算。
```py
import math
result = math.factorial(10)
print(result)
```
<end_code>"""
code = parse_code_blobs(text)
print(code)
# "import math\nresult = math.factorial(10)\nprint(result)"

# truncate_content：截断超长内容
long_text = "A" * 10000
truncated = truncate_content(long_text, max_length=100)
print(f"截断后长度: {len(truncated)}")  # 100
print(truncated.endswith("..."))  # True（或类似截断标记）

# make_json_serializable：递归转为JSON可序列化
import datetime
data = {
    "time": datetime.datetime(2026, 8, 22, 12, 0),
    "tags": {"python", "ai", "agent"},  # set
    "nested": {"value": float("inf")},
}
serializable = make_json_serializable(data)
import json
json_str = json.dumps(serializable)
print(json_str)

# is_valid_name：检查有效Python标识符
print(is_valid_name("my_tool"))      # True
print(is_valid_name("web_search"))   # True
print(is_valid_name("123abc"))       # False（数字开头）
print(is_valid_name("my-tool"))      # False（含连字符）
print(is_valid_name("class"))        # False（保留字）
print(is_valid_name("import"))       # False（保留字）

# parse_json_blob：从文本提取JSON
json_text = '思考中... {"name": "search", "arguments": {"query": "AI"}} 调用工具'
parsed = parse_json_blob(json_text)
print(parsed)  # {"name": "search", "arguments": {"query": "AI"}}

# get_imports：提取import语句
code = """
import os
import sys
from math import sqrt, pi
from collections import defaultdict
import numpy as np

x = sqrt(16)
"""
imports = get_imports(code)
print(imports)  # ['os', 'sys', 'math', 'collections', 'numpy']
````

### 工具验证

```python
from codified_smolagents import Tool
from codified_smolagents.utils import validate_tool_attributes

# 正确的工具定义
class GoodTool(Tool):
    name = "good_tool"
    description = "一个正确定义的工具"
    inputs = {
        "text": {
            "type": "string",
            "description": "输入文本",
        }
    }
    output_type = "string"

    def forward(self, text: str) -> str:
        return text.upper()

# 验证通过（不抛异常）
validate_tool_attributes(GoodTool)
print("GoodTool 验证通过")

# 错误的工具定义（缺少description）
class BadTool(Tool):
    name = "bad_tool"
    # 缺少 description
    inputs = {"x": {"type": "integer", "description": "数字"}}
    output_type = "integer"

    def forward(self, x: int) -> int:
        return x * 2

try:
    validate_tool_attributes(BadTool)
except Exception as e:
    print(f"BadTool 验证失败: {e}")
```

### 可视化 Agent 树

```python
from codified_smolagents import CodeAgent, ToolCallingAgent, HfApiModel, DuckDuckGoSearchTool

model = HfApiModel()

# 创建一个包含托管智能体的Agent
search_agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    max_steps=3,
    name="search_expert",
    description="专门进行网络搜索的智能体",
)

agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[search_agent],
    additional_authorized_imports=['math'],
    max_steps=5,
)

# 使用AgentLogger可视化Agent层次结构
from codified_smolagents.utils import AgentLogger, LogLevel
logger = AgentLogger(level=LogLevel.INFO)
logger.visualize_agent_tree(agent)
# 输出类似：
# CodeAgent
# └── search_expert (ToolCallingAgent)
```

> 事实溯源：F-126~F-152

## 注意事项

### verbosity_level 控制日志详细程度

Agent 构造时的 `verbosity_level` 参数接受 `LogLevel` 枚举值（0-3），控制运行过程中日志输出的详细程度。生产环境建议使用 `LogLevel.ERROR` 或 `LogLevel.OFF` 减少输出；开发调试时使用 `LogLevel.DEBUG` 查看完整的代码生成和执行细节。

### Monitor 在析构时输出汇总

`Monitor.__del__` 在对象被垃圾回收时自动输出总 Token 用量。在交互式环境（如 Jupyter）中，对象生命周期可能较长，汇总信息可能延迟输出。如果需要即时查看 Token 用量，通过 `model.get_token_counts()` 或 `monitor.last_input_token_count` / `monitor.last_output_token_count` 主动获取。

### parse_code_blobs 只提取 Python 代码块

`parse_code_blobs()` 专门提取 ` ```py ` 或 ` ```python ` 标记的代码块，不会提取其他语言的代码块（如 ` ```json `、` ```bash `）。如果模型输出了非 Python 代码块，该函数不会提取其内容。

### truncate_content 默认最大长度 5000

`truncate_content(content, max_length=5000)` 默认截断到 5000 字符，用于防止超长的工具输出或观察结果撑爆上下文窗口。在处理长文档时注意这一默认限制，必要时增大 `max_length` 参数。

### make_json_serializable 处理特殊浮点值

`make_json_serializable()` 能处理 `datetime`、`set`、`bytes` 等非 JSON 原生类型，也能处理 `float("inf")`、`float("-inf")`、`float("nan")` 等特殊浮点值（转换为字符串表示）。自定义类实例默认转换为其 `__dict__` 或字符串表示。

### is_valid_name 检查保留字

`is_valid_name()` 不仅检查是否为有效 Python 标识符（`str.isidentifier()`），还检查是否为 Python 保留字（`keyword.iskeyword()`）。工具名和 Agent 名必须通过此校验，否则会在初始化时被拒绝。

### validate_tool_attributes 在 Tool.__init__ 中自动调用

创建 Tool 实例时（无论是通过子类还是 `@tool` 装饰器），`validate_tool_attributes()` 会自动被调用验证工具定义。验证失败会抛出异常，阻止无效工具的创建。`@tool` 装饰器生成的工具一般能通过验证，手动定义 Tool 子类时需注意四要素完整性。

### AgentError 是所有框架异常的基类

捕获 `AgentError` 可以兜底处理所有框架抛出的异常。但建议尽量捕获更具体的子类（如 `AgentMaxStepsError`），以便针对不同错误类型采取不同的恢复策略。

## 相关链接

- [多步推理循环](/concepts/03-multi-step-agent.md) — Agent运行循环中的日志输出
- [CodeAgent：代码执行范式](/concepts/06-code-agent.md) — 代码执行错误与异常处理
- [ToolCallingAgent：函数调用范式](/concepts/05-tool-calling-agent.md) — 工具调用错误解析
- [Python 执行器与安全沙箱](/concepts/11-python-executor.md) — 执行错误与InterpreterError
- [Utils API 参考](/references/utils-api.md) — 日志/监控/工具函数完整API
