---
type: Reference
title: Utils API 参考
description: codified-smolagents 工具函数、监控、验证、CLI和UI模块API参考
tags: [Utils, AgentError, 监控, AgentLogger, Monitor, 工具验证, CLI, GradioUI, API参考]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T22:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T22:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: utils-source
    resource: ../../../../../../external/libs/models/AgnesAI/GodeAgents/Multi-Agent-Task/src/codified-smolagents/utils.py
    title: codified-smolagents/utils.py
  - id: monitoring-source
    resource: ../../../../../../external/libs/models/AgnesAI/GodeAgents/Multi-Agent-Task/src/codified-smolagents/monitoring.py
    title: codified-smolagents/monitoring.py
  - id: tool-validation-source
    resource: ../../../../../../external/libs/models/AgnesAI/GodeAgents/Multi-Agent-Task/src/codified-smolagents/tool_validation.py
    title: codified-smolagents/tool_validation.py
  - id: type-hints-source
    resource: ../../../../../../external/libs/models/AgnesAI/GodeAgents/Multi-Agent-Task/src/codified-smolagents/_function_type_hints_utils.py
    title: codified-smolagents/_function_type_hints_utils.py
  - id: cli-source
    resource: ../../../../../../external/libs/models/AgnesAI/GodeAgents/Multi-Agent-Task/src/codified-smolagents/cli.py
    title: codified-smolagents/cli.py
  - id: gradio-ui-source
    resource: ../../../../../../external/libs/models/AgnesAI/GodeAgents/Multi-Agent-Task/src/codified-smolagents/gradio_ui.py
    title: codified-smolagents/gradio_ui.py
---

# Utils API 参考

本文件记录工具函数、监控日志、工具验证、类型提示解析、命令行界面和Gradio UI模块，基于源码零推测事实 F-126 ~ F-147 和 F-139 ~ F-142。

## 概述

工具层提供全框架共用的基础能力：异常层次体系定义了所有智能体错误类型；内容处理函数支持代码块解析、JSON提取、内容截断、源码序列化；监控模块提供结构化日志和token使用统计；工具验证模块通过AST静态分析确保Tool子类正确性；CLI和Gradio UI提供了快速启动和交互界面。

> 事实溯源：F-129、F-126~F-128、F-151~F-152、F-143~F-147

## 异常层次体系（utils.py）

### AgentError

```python
class AgentError(Exception)
```

所有智能体相关异常的基类。

**构造函数：**
```python
def __init__(self, message, logger: "AgentLogger")
```
接收错误消息和日志器，自动通过logger.log_error记录错误。

**方法：**
- `dict() -> Dict[str, str]`: 返回`{"type": 类名, "message": 消息}`字典

> 事实溯源：F-129

### 异常子类

| 异常类 | 继承自 | 用途 |
|-------|--------|------|
| `AgentParsingError` | AgentError | LLM输出解析错误 |
| `AgentGenerationError` | AgentError | 模型生成错误（非模型本身错误，而是实现错误） |
| `AgentExecutionError` | AgentError | 代码/工具执行错误 |
| `AgentMaxStepsError` | AgentError | 达到最大步数错误 |
| `AgentToolCallError` | AgentExecutionError | 工具调用参数错误（TypeError） |
| `AgentToolExecutionError` | AgentExecutionError | 工具执行过程错误 |

> 事实溯源：F-129

## 内容处理工具函数

### parse_code_blobs

```python
def parse_code_blobs(text: str) -> str
```

从LLM输出中提取````py ... ````或````python ... ````代码块内容。支持多个代码块（以换行连接返回）。如果文本本身是有效Python代码（ast.parse成功），直接返回原文。无代码块时抛出ValueError并给出修复提示。

**参数：**
- `text` (`str`): LLM输出文本

**返回：** `str` — 提取的代码内容

> 事实溯源：F-131

### parse_json_blob

```python
def parse_json_blob(json_blob: str) -> Tuple[Dict[str, str], str]
```

从文本中提取JSON对象，返回解析后的字典和JSON之前的前缀文本。使用`json.loads(strict=False)`解析。

**返回：** `Tuple[Dict[str, str], str]` — (JSON数据, 前缀文本)

> 事实溯源：F-138

### truncate_content

```python
def truncate_content(content: str, max_length: int = 20000) -> str
```

截断超长内容，保留前后各一半，中间插入截断提示。默认最大长度20000字符。

**参数：**
- `content` (`str`): 待截断内容
- `max_length` (`int`, 默认`20000`): 最大字符数

> 事实溯源：F-132

### make_json_serializable

```python
def make_json_serializable(obj: Any) -> Any
```

递归将对象转换为JSON可序列化类型。处理None/基本类型/字符串（尝试解析JSON）/列表/元组/字典/自定义对象（转__dict__）/其他类型（转字符串）。

> 事实溯源：F-133

### escape_code_brackets

```python
def escape_code_brackets(text: str) -> str
```

转义代码段中的方括号，同时保留Rich样式标签（bold/red/green/blue/yellow等颜色和格式标签不转义）。

## 名称与源码工具

### is_valid_name

```python
def is_valid_name(name: str) -> bool
```

检查字符串是否为有效Python标识符且非保留关键字。

> 事实溯源：F-134

### get_source

```python
def get_source(obj) -> str
```

获取类或可调用对象的源代码。优先使用`inspect.getsource`，在动态环境（Jupyter/IPython）中回退到从IPython历史中查找。返回dedent后的源码。失败时抛出TypeError/OSError/ValueError。

> 事实溯源：F-136

### instance_to_source

```python
def instance_to_source(instance, base_cls=None) -> str
```

将实例转换为其类的源码代码字符串表示。包括类定义、docstring、类属性（自动推导import）、方法（仅包含与基类不同的方法）。用于Tool序列化保存。

### make_init_file

```python
def make_init_file(folder: str | Path)
```

创建目录（如不存在）并生成空的`__init__.py`文件。

> 事实溯源：F-135

### _is_package_available

```python
@lru_cache
def _is_package_available(package_name: str) -> bool
```

使用`importlib.metadata.version`检查包是否可用，结果带LRU缓存。

> 事实溯源：F-137

## 图像处理工具

### encode_image_base64

```python
def encode_image_base64(image) -> str
```

将PIL图像编码为base64 PNG字符串。

### make_image_url

```python
def make_image_url(base64_image: str) -> str
```

将base64图像转换为data URL格式：`data:image/png;base64,{base64_image}`。

## 常量

### BASE_BUILTIN_MODULES

```python
BASE_BUILTIN_MODULES = [
    "collections", "datetime", "itertools", "math", "queue",
    "random", "re", "stat", "statistics", "time", "unicodedata",
]
```

CodeAgent默认授权导入的标准库模块列表。

> 事实溯源：F-130

## 监控与日志（monitoring.py）

### LogLevel

```python
class LogLevel(IntEnum):
    OFF = -1    # 无输出
    ERROR = 0   # 仅错误
    INFO = 1    # 正常输出（默认）
    DEBUG = 2   # 详细输出
```

日志级别枚举。注意：实际源码中OFF=-1、ERROR=0、INFO=1、DEBUG=2。

> 事实溯源：F-126（注意：源码实际值与facts.md描述有差异，以源码为准）

### AgentLogger

```python
class AgentLogger
```

基于Rich Console的结构化日志器。

**构造函数：**
```python
def __init__(self, level: LogLevel = LogLevel.INFO)
```

**核心方法：**

| 方法 | 用途 |
|------|------|
| `log(*args, level=LogLevel.INFO, **kwargs)` | 通用日志输出，支持字符串级别名 |
| `log_error(error_message: str)` | 以红色粗体输出错误信息 |
| `log_markdown(content, title=None, level=INFO, style=YELLOW_HEX)` | 以Markdown语法高亮输出，可选标题Rule |
| `log_code(title, content, level=INFO)` | 以Python语法高亮面板输出代码 |
| `log_rule(title, level=INFO)` | 输出分隔线Rule |
| `log_task(content, subtitle, title=None, level=INFO)` | 输出任务面板 |
| `log_messages(messages: List)` | 以JSON格式输出消息列表 |
| `visualize_agent_tree(agent)` | 生成智能体结构树形可视化（工具表+被管理智能体递归树） |

> 事实溯源：F-127

### Monitor

```python
class Monitor
```

智能体执行监控器，跟踪步骤时长和token使用量。

**构造函数：**
```python
def __init__(self, tracked_model, logger)
```

**方法：**
- `update_metrics(step_log)`: 更新指标——记录步骤时长、累加input/output token数、输出控制台信息（作为step_callback自动注册）
- `get_total_token_counts() -> dict`: 返回总token计数 `{"input": ..., "output": ...}`
- `reset()`: 重置所有计数器

> 事实溯源：F-128

### 常量

```python
YELLOW_HEX = "#d4b702"
```

日志中使用的黄色十六进制颜色值。

## 工具验证（tool_validation.py）

### MethodChecker

```python
class MethodChecker(ast.NodeVisitor)
```

AST访问器，检查Tool方法中是否存在未定义名称和非法导入。

**构造函数：**
```python
def __init__(self, class_attributes: Set[str], check_imports: bool = True)
```

**检查逻辑（visit_Name/visit_Call）：** 加载上下文中的名称必须属于以下集合之一：Python内置名、BASE_BUILTIN_MODULES、函数参数名、self、类属性、导入名、赋值名、typing名。否则记录为undefined错误。

> 事实溯源：F-151

### validate_tool_attributes

```python
def validate_tool_attributes(cls, check_imports: bool = True) -> None
```

通过AST分析验证Tool子类的正确性，验证项包括：
1. `__init__`所有参数必须有默认值
2. 类属性只能是字符串或字面量（不能是复杂对象）
3. `name`属性必须是字符串常量且为有效Python标识符
4. 所有方法必须自包含（无未定义名称引用）
5. 方法中的导入必须来自包而非本地文件

验证失败时抛出ValueError，包含所有错误列表。

> 事实溯源：F-152

## 类型提示解析（_function_type_hints_utils.py）

### get_imports

```python
def get_imports(code: str) -> List[str]
```

从Python代码字符串中提取顶层import语句的模块名列表（取模块名第一个点之前的部分作为包名）。

> 事实溯源：F-139

### 异常类

```python
class TypeHintParsingException(Exception)
class DocstringParsingException(Exception)
```

类型提示解析和docstring解析异常。

> 事实溯源：F-140

### get_json_schema

```python
def get_json_schema(func: Callable) -> Dict
```

基于Google格式docstring和Python类型注解生成OpenAI function calling格式的JSON Schema。返回包含name、description、parameters（properties/required）、return的字典。

> 事实溯源：F-141

### 常量

```python
_BASE_TYPE_MAPPING
```

Python基础类型到JSON Schema类型的映射字典。

> 事实溯源：F-142

## 命令行界面（cli.py）

### parse_arguments

```python
def parse_arguments()
```

使用argparse定义命令行参数：
- `prompt`: 任务提示（位置参数）
- `--model-type`: 模型类型，默认`"HfApiModel"`
- `--model-id`: 模型ID，默认`"Qwen/Qwen2.5-Coder-32B-Instruct"`
- `--imports`: 额外授权导入
- `--tools`: 工具列表，默认`["web_search"]`
- `--verbosity-level`: 日志级别
- `--api-base`: API基础URL
- `--api-key`: API密钥

> 事实溯源：F-143

### load_model

```python
def load_model(model_type, model_id, api_base, api_key)
```

根据model_type字符串动态创建对应模型实例。

> 事实溯源：F-144

### run_smolagent

```python
def run_smolagent(prompt, tools, model_type, model_id, ...)
```

创建CodeAgent实例并调用`agent.run(prompt)`执行任务。

> 事实溯源：F-145

## Gradio UI（gradio_ui.py）

### stream_to_gradio

```python
def stream_to_gradio(agent, task, ...)
```

生成器函数，调用`agent.run(stream=True)`逐步yield `gr.ChatMessage`对象，用于Gradio流式聊天界面。

> 事实溯源：F-146

### GradioUI

```python
class GradioUI
```

Gradio聊天界面封装类。

**构造函数：**
```python
def __init__(self, agent: MultiStepAgent)
```

**方法：**
- `launch()`: 启动Gradio界面
- `create_app()`: 创建Gradio ChatInterface应用

> 事实溯源：F-147

## 相关概念

- [错误处理机制](/concepts/error-handling.md) — AgentError异常体系与错误恢复
- [监控与日志](/concepts/monitoring-logging.md) — AgentLogger和Monitor的使用
- [工具系统概述](/concepts/tool-system.md) — 工具验证与类型安全
- [智能体API参考](/references/agents-api.md) — Agent如何使用工具函数和监控
- [工具API参考](/references/tools-api.md) — Tool类使用的验证和序列化函数
