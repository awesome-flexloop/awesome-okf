---
type: Reference
title: Tools API 参考
description: codified-smolagents 工具系统API参考，包含Tool基类、@tool装饰器、ToolCollection、PipelineTool、SpaceToolWrapper及内置工具
tags: [Tool, 工具, "@tool装饰器", ToolCollection, PipelineTool, 默认工具, API参考]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T22:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T22:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: tools-source
    resource: ../../../../../../external/libs/models/AgnesAI/GodeAgents/Multi-Agent-Task/src/codified-smolagents/tools.py
    title: codified-smolagents/tools.py
  - id: default-tools-source
    resource: ../../../../../../external/libs/models/AgnesAI/GodeAgents/Multi-Agent-Task/src/codified-smolagents/default_tools.py
    title: codified-smolagents/default_tools.py
---

# Tools API 参考

本文件记录 `tools.py` 和 `default_tools.py` 模块中的工具定义体系，基于源码零推测事实 F-047 ~ F-060 和 F-120 ~ F-125。

## 概述

工具系统是智能体与外部环境交互的接口。`Tool` 基类定义了工具的统一接口规范，`@tool` 装饰器可将普通Python函数快速转换为工具实例，`ToolCollection` 支持批量加载工具集。系统内置了网络搜索、网页访问、维基百科搜索、Python解释器和最终回答等基础工具。

> 事实溯源：F-047、F-056、F-057

## 常量

### AUTHORIZED_TYPES

```python
AUTHORIZED_TYPES = ["string", "boolean", "integer", "number", "image", "audio", "array", "object", "any", "null"]
```

工具输入/输出的授权类型列表。自定义工具的 `inputs` 和 `output_type` 必须使用这些类型值。

### CONVERSION_DICT

```python
CONVERSION_DICT = {"str": "string", "int": "integer", "float": "number"}
```

Python类型到JSON Schema类型的映射字典。

> 事实溯源：F-047（相关）

## Tool 基类

```python
class Tool
```

所有工具的基类。子类必须定义以下类属性并实现 `forward` 方法：
- `name` (`str`): 工具名称（有效Python标识符）
- `description` (`str`): 工具功能描述
- `inputs` (`Dict[str, Dict]`): 输入参数定义，每个参数包含 `type` 和 `description`
- `output_type` (`str`): 输出类型（使用AUTHORIZED_TYPES中的值）

> 事实溯源：F-047、F-048

### 构造与初始化

#### __init__

```python
def __init__(self, *args, **kwargs)
```

初始化工具实例，设置 `is_initialized = False`。子类通过 `__init_subclass__` 钩子自动注册 `validate_after_init` 装饰器，在初始化后自动调用 `validate_arguments()`。

> 事实溯源：F-049

#### validate_arguments

```python
def validate_arguments(self)
```

验证工具属性的完整性：
1. 检查必需属性（description、name、inputs、output_type）是否存在且类型正确
2. 验证name为有效Python标识符
3. 验证inputs中每个参数都有 `type` 和 `description`，且type为授权类型
4. 验证output_type为授权类型
5. 验证forward方法签名与inputs键匹配（skip_forward_signature_validation时跳过）

> 事实溯源：F-047（验证逻辑）

#### setup

```python
def setup(self)
```

执行昂贵的初始化操作（如加载模型），在首次调用 `__call__` 时自动执行。默认实现设置 `is_initialized = True`。子类可重写此方法实现延迟加载。

### 核心方法

#### forward

```python
def forward(self, *args, **kwargs)
```

工具的核心执行逻辑，子类必须实现。默认抛出 `NotImplementedError`。

> 事实溯源：F-050

#### __call__

```python
def __call__(self, *args, sanitize_inputs_outputs: bool = False, **kwargs)
```

调用工具。执行流程：
1. 若未初始化，先调用 `setup()`
2. 若传入单个字典参数且键名匹配inputs，自动转换为kwargs
3. 若 `sanitize_inputs_outputs=True`，对输入调用 `handle_agent_input_types()`
4. 调用 `forward()` 执行
5. 若 `sanitize_inputs_outputs=True`，对输出调用 `handle_agent_output_types()`

> 事实溯源：F-051

#### to_dict

```python
def to_dict(self) -> Dict
```

返回工具的字典表示，包含 `name`、`code`（源码字符串）、`requirements`（依赖列表）。对于 `@tool` 装饰器创建的工具（SimpleTool），直接生成forward方法源码；对于子类化创建的工具，使用 `instance_to_source` 序列化。

> 事实溯源：F-052

#### save

```python
def save(
    self,
    output_dir: str | Path,
    tool_file_name: str = "tool",
    make_gradio_app: bool = True,
)
```

保存工具到目录。生成 `{tool_file_name}.py` 工具代码文件；`make_gradio_app=True` 时额外生成 `app.py`（Gradio UI）和 `requirements.txt`。

> 事实溯源：F-053

#### push_to_hub

```python
def push_to_hub(
    self,
    repo_id: str,
    commit_message: str = "Upload tool",
    private: Optional[bool] = None,
    token: Optional[Union[bool, str]] = None,
    create_pr: bool = False,
) -> str
```

将工具上传到 Hugging Face Hub（创建为Space仓库，SDK为gradio）。

### 类方法

#### from_code

```python
@classmethod
def from_code(cls, tool_code: str, **kwargs) -> Tool
```

从代码字符串动态创建工具实例。使用 `exec()` 在临时模块中执行代码，查找其中的 `Tool` 子类并实例化。

> 事实溯源：F-054

#### from_hub

```python
@classmethod
def from_hub(
    cls,
    repo_id: str,
    token: Optional[str] = None,
    trust_remote_code: bool = False,
    **kwargs,
) -> Tool
```

从 Hugging Face Hub 下载工具代码并加载。要求 `trust_remote_code=True`。

#### from_space

```python
@staticmethod
def from_space(
    space_id: str,
    name: str,
    description: str,
    api_name: Optional[str] = None,
    token: Optional[str] = None,
) -> SpaceToolWrapper
```

从 Hugging Face Space 创建工具包装器。使用 `gradio_client.Client` 连接Space端点，自动推断输入参数和输出类型。支持图像、音频等多模态输入输出。

> 事实溯源：F-055

#### from_gradio

```python
@staticmethod
def from_gradio(gradio_tool) -> Tool
```

将Gradio工具包装为Tool实例。

#### from_langchain

```python
@staticmethod
def from_langchain(langchain_tool) -> Tool
```

将LangChain工具包装为Tool实例（内部创建LangChainToolWrapper）。

> 事实溯源：tools.py中定义

## @tool 装饰器

```python
def tool(tool_function: Callable) -> Tool
```

将普通Python函数转换为 `Tool` 子类实例（SimpleTool）。要求函数：
1. 每个参数都有类型注解
2. 有返回类型注解
3. docstring包含功能描述和 `Args:` 部分描述每个参数

转换过程：
1. 使用 `get_json_schema()` 从函数签名和docstring生成JSON Schema
2. 动态创建SimpleTool类，设置name、description、inputs、output_type属性
3. 将原函数绑定为forward静态方法，并调整签名添加self参数

**示例：**
```python
@tool
def calculator(expression: str) -> float:
    """
    Evaluates a mathematical expression.
    Args:
        expression: The mathematical expression to evaluate.
    """
    return eval(expression)
```

> 事实溯源：F-056

## ToolCollection

```python
class ToolCollection
```

工具集合类，用于批量加载和管理一组工具。

### 构造函数

```python
def __init__(self, tools: List[Tool])
```

接收工具列表，存储为 `self.tools`。

> 事实溯源：F-057

### 类方法

#### from_hub

```python
@classmethod
def from_hub(
    cls,
    collection_slug: str,
    token: Optional[str] = None,
    trust_remote_code: bool = False,
) -> ToolCollection
```

从 Hugging Face Hub 集合加载工具。集合中的每个Space都会被转换为Tool实例。

#### from_mcp

```python
@classmethod
@contextmanager
def from_mcp(
    cls,
    server_parameters: Union["mcp.StdioServerParameters", dict],
    trust_remote_code: bool = False,
) -> ToolCollection
```

从MCP（Model Context Protocol）服务器加载工具。支持Stdio和SSE两种连接方式。需要安装 `smolagents[mcp]` 扩展。要求 `trust_remote_code=True`。使用上下文管理器模式（with语句）。

## PipelineTool

```python
class PipelineTool(Tool)
```

专为Transformer模型设计的工具基类。额外类属性：
- `model_class`: 模型加载类（默认None）
- `default_checkpoint`: 默认模型检查点
- `pre_processor_class`: 预处理器类（默认AutoProcessor）
- `post_processor_class`: 后处理器类（默认同pre_processor）

`skip_forward_signature_validation = True`。

### 构造函数

```python
def __init__(
    self,
    model=None,
    pre_processor=None,
    post_processor=None,
    device=None,
    device_map=None,
    model_kwargs=None,
    token=None,
    **hub_kwargs,
)
```

需要安装 `smolagents[transformers]` 扩展。setup时自动从Hub加载模型和处理器。

### 核心方法

- `encode(raw_inputs)`: 使用pre_processor编码输入
- `forward(inputs)`: 模型推理（torch.no_grad上下文）
- `decode(outputs)`: 使用post_processor解码输出
- `__call__`: 完整pipeline（编码→发送到设备→推理→移回CPU→解码）

> 事实溯源：F-058

## SpaceToolWrapper

```python
class SpaceToolWrapper(Tool)
```

包装 Hugging Face Space 推理端点的工具类（在 `Tool.from_space()` 中动态创建）。`skip_forward_signature_validation = True`。

核心逻辑：
- 初始化时通过 `gradio_client.Client` 连接Space
- 自动从Space API描述推断inputs和output_type
- forward时预处理参数（处理文件路径、URL、PIL图像），调用client.predict

> 事实溯源：F-059

## 辅助函数

### launch_gradio_demo

```python
def launch_gradio_demo(tool: Tool)
```

为工具启动Gradio演示界面。根据inputs/output_type自动创建Gradio组件。需要安装gradio。

### load_tool

```python
def load_tool(
    repo_id,
    model_repo_id: Optional[str] = None,
    token: Optional[str] = None,
    trust_remote_code: bool = False,
    **kwargs,
)
```

从Hub快速加载工具的便捷函数，内部调用 `Tool.from_hub()`。

### add_description

```python
def add_description(description)
```

装饰器，为函数添加description属性。

### get_tools_definition_code

```python
def get_tools_definition_code(tools: Dict[str, Tool]) -> str
```

将工具字典转换为可在沙箱中执行的Python代码字符串。为每个工具生成类定义和实例化代码，前置简化的Tool基类定义。用于在Python执行器中注入工具。

> 事实溯源：F-060

## 内置默认工具

### PythonInterpreterTool

```python
class PythonInterpreterTool(Tool)
```

Python代码解释器工具。
- `name = "python_interpreter"`
- `inputs = {"code": {"type": "string"}}`
- `output_type = "string"`
- `forward` 调用 `self.python_executor(code_action)` 执行代码

仅 `ToolCallingAgent` 可通过 `add_base_tools=True` 自动添加此工具。

> 事实溯源：F-120

### FinalAnswerTool

```python
class FinalAnswerTool(Tool)
```

最终回答工具。
- `name = "final_answer"`
- `inputs = {"answer": {"type": "any"}}`
- `output_type = "any"`
- `forward` 直接返回 `answer`

此工具自动添加到所有智能体的工具字典中（`tools.setdefault("final_answer", FinalAnswerTool())`）。

> 事实溯源：F-121

### DuckDuckGoSearchTool

```python
class DuckDuckGoSearchTool(Tool)
```

DuckDuckGo网络搜索工具。
- `name = "web_search"`
- 使用 `duckduckgo_search.DDGS` 执行搜索

> 事实溯源：F-122

### VisitWebpageTool

```python
class VisitWebpageTool(Tool)
```

网页访问工具。
- `name = "visit_webpage"`
- 使用 `requests` 获取网页内容，`markdownify` 转换为Markdown

> 事实溯源：F-123

### WikipediaSearchTool

```python
class WikipediaSearchTool(Tool)
```

维基百科搜索工具。
- `name = "search_wikipedia"`
- 使用 `wikipedia` 库搜索

> 事实溯源：F-124

### TOOL_MAPPING

```python
TOOL_MAPPING = {
    "python_interpreter": PythonInterpreterTool,
    "web_search": DuckDuckGoSearchTool,
    "visit_webpage": VisitWebpageTool,
    "search_wikipedia": WikipediaSearchTool,
    "final_answer": FinalAnswerTool,
}
```

内置工具名称到类的映射字典。

> 事实溯源：F-125

## 相关概念

- [工具系统概述](/concepts/tool-system.md) — 工具定义、注册和调用机制
- [工具调用智能体](/concepts/tool-calling-agent.md) — ToolCallingAgent的工具调用流程
- [代码执行智能体](/concepts/code-agent.md) — CodeAgent中的工具注入机制
- [智能体API参考](/references/agents-api.md) — Agent如何管理和调用工具
- [模型API参考](/references/models-api.md) — Model的工具JSON Schema生成
