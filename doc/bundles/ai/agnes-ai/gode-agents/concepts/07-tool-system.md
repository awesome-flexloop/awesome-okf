---
type: Concept
title: 工具系统：@tool装饰器与Tool基类
description: Tool基类四要素、@tool装饰器自动Schema生成、工具开发指南
tags: [工具, Tool, "@tool", 装饰器, Schema]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:20:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: F-047
    resource: /references/tools-api.md
    title: Tools API 参考
---

# 工具系统：@tool装饰器与Tool基类

## 概述

工具（Tool）是 GodeAgents 中 Agent 与外部世界交互的基本单元。每个工具封装了一个可被 LLM 调用的能力——搜索网页、执行代码、访问API、查询数据库等。框架提供了统一的 `Tool` 基类和便捷的 `@tool` 装饰器，让开发者用最少的代码定义符合 OpenAI function calling 标准的工具，同时自动生成参数 Schema、验证输入输出类型、支持持久化和动态加载。

工具开发是扩展 Agent 能力的核心方式。理解 Tool 基类的四要素和 `@tool` 装饰器的自动推导机制，是开发自定义工具的基础。

> 事实溯源：F-047~F-060

## 核心概念

### 工具四要素

每个 Tool 必须定义四个核心属性，它们共同描述了工具的"接口契约"：

| 要素 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 工具的唯一标识符，必须是有效的 Python 标识符 |
| `description` | `str` | 工具功能的自然语言描述，LLM 据此判断何时使用该工具 |
| `inputs` | `dict` | 参数 Schema，定义每个参数的类型和描述 |
| `output_type` | `str` | 输出类型（如 `"string"`、`"integer"`、`"any"` 等） |

这四个要素是 LLM 理解工具能力的全部信息——模型看到的工具定义就是基于这四个字段生成的 JSON Schema。

> 事实溯源：F-047

### forward() 与 __call__()

Tool 的执行逻辑定义在 `forward()` 方法中（子类必须实现），而 `__call__()` 是对外的调用入口，负责参数验证和输出处理：

- `forward()`：纯业务逻辑，子类实现，基类中抛 `NotImplementedError`
- `__call__(*args, sanitize_inputs_outputs=False, **kwargs)`：调用 `forward()`，当 `sanitize_inputs_outputs=True` 时对结果调用 `handle_agent_output_types()` 进行类型转换

> 事实溯源：F-050~F-051

### @tool 装饰器：零配置创建工具

`@tool` 装饰器是最常用的工具创建方式，它能从一个普通 Python 函数自动推导 Tool 四要素：

| 函数元素 | 推导为 | 说明 |
|----------|--------|------|
| 函数名 | `name` | 直接使用函数名作为工具名 |
| docstring | `description` + `inputs` 描述 | 解析 Google 风格 docstring 的 Args 段落 |
| 类型注解 | `inputs` 类型 + `output_type` | 从参数和返回值注解推导 JSON Schema 类型 |

这意味着开发者只需写一个带类型注解和 Google 风格 docstring 的函数，加上 `@tool` 装饰器，就能得到一个完整可用的 Tool 实例。

> 事实溯源：F-056

## API 要点

### Tool 基类

```python
class Tool:
    # 类属性默认值
    skip_forward_signature_validation: bool = False
    is_initialized: bool = False

    # 子类必须定义的四要素（类属性）
    name: str
    description: str
    inputs: Dict[str, Dict[str, str]]
    output_type: str

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)       # 通过关键字参数设置实例属性
        self.validate_arguments()          # 验证参数定义
        self.is_initialized = True         # 标记初始化完成

    def forward(self, *args, **kwargs):    # 子类必须实现
        raise NotImplementedError

    def __call__(self, *args, sanitize_inputs_outputs=False, **kwargs):
        result = self.forward(*args, **kwargs)
        if sanitize_inputs_outputs:
            result = handle_agent_output_types(result)
        return result

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "inputs": self.inputs,
            "output_type": self.output_type,
            "requirements": getattr(self, "requirements", []),
        }
```

> 事实溯源：F-047~F-052

### inputs Schema 格式

`inputs` 是一个字典，键为参数名，值为描述该参数的子字典：

```python
inputs = {
    "param_name": {
        "type": "string",        # JSON Schema类型：string/integer/number/boolean/array/object/any
        "description": "参数说明", # LLM看到的参数描述
        # 可选字段：
        # "nullable": bool,
        # "enum": List[str],
    }
}
```

当使用 `@tool` 装饰器时，这个 Schema 从函数的类型注解和 docstring 自动生成。类型注解到 JSON Schema 类型的映射：
- `str` → `"string"`
- `int` → `"integer"`
- `float` → `"number"`
- `bool` → `"boolean"`
- `list`/`List[T]` → `"array"`
- `dict`/`Dict[K,V]` → `"object"`
- 其他/Any → `"any"`

> 事实溯源：F-047

### @tool 装饰器用法

```python
from codified_smolagents import tool

@tool
def my_tool(query: str, max_results: int = 5) -> str:
    """工具功能的一句话描述。

    Args:
        query: 搜索查询字符串
        max_results: 返回结果的最大数量，默认为5

    Returns:
        搜索结果的文本描述
    """
    # 实现逻辑
    return f"搜索 '{query}' 的结果（共{max_results}条）"
```

装饰器自动完成：
1. 函数名 `my_tool` → `name="my_tool"`
2. docstring 第一行 → `description="工具功能的一句话描述。"`
3. Args 段落 → `inputs` 中每个参数的 `description`
4. 类型注解 `query: str` → `inputs["query"]["type"] = "string"`
5. 返回值注解 `-> str` → `output_type="string"`
6. 默认值 `max_results: int = 5` → 标记为可选参数

> 事实溯源：F-056

### Google 风格 docstring 格式要求

`@tool` 装饰器解析 docstring 时期望 Google 风格：
- 第一行：工具功能的一句话摘要（成为 `description`）
- 空行后：详细说明（可选，当前会追加到 description）
- `Args:` 段落：每个参数一行，格式为 `param_name: 参数描述`
- `Returns:` 段落：返回值描述

不遵循此格式可能导致参数描述无法正确提取。

### 工具持久化与加载

#### Tool.save()

```python
def save(self, output_dir: str, tool_file_name: Optional[str] = None, make_gradio_app: bool = True)
```

将工具保存到指定目录：
- 生成工具 Python 代码文件
- 可选创建 Gradio 演示应用（`make_gradio_app=True`）
- `tool_file_name` 默认使用 `self.name + ".py"`

> 事实溯源：F-053

#### Tool.from_code()

```python
@classmethod
def from_code(cls, tool_code: str) -> "Tool"
```

动态执行工具代码字符串，提取其中定义的 Tool 实例并返回。用于从文本/文件动态加载工具。

> 事实溯源：F-054

#### Tool.from_space()

```python
@classmethod
def from_space(cls, space_id: str, name: Optional[str] = None, description: Optional[str] = None, api_name: Optional[str] = None) -> "SpaceToolWrapper"
```

从 HuggingFace Space 创建 `SpaceToolWrapper` 实例，将 Space 推理端点包装为可用工具。

> 事实溯源：F-055

### ToolCollection：工具集合管理

```python
class ToolCollection:
    """管理一组工具，提供容器式访问"""
    def __iter__(self) -> Iterator[Tool]: ...
    def __getitem__(self, key: str) -> Tool: ...
    def __len__(self) -> int: ...
```

`ToolCollection` 是工具的容器类，支持迭代、按键索引、获取长度。它将工具组织为可遍历的集合，便于批量操作和传递。

> 事实溯源：F-057

### 专用 Tool 子类

#### PipelineTool

```python
class PipelineTool(Tool):
    """包装 HuggingFace Transformers pipeline 的工具"""
```

将 HuggingFace 的 `transformers.pipeline()` 对象包装为 Tool，自动生成 name/description/inputs/output_type。

> 事实溯源：F-058

#### SpaceToolWrapper

```python
class SpaceToolWrapper(Tool):
    """包装 HuggingFace Space 推理端点的工具"""
```

通过 HF Inference API 调用远程 Space 作为工具，`Tool.from_space()` 工厂方法返回此类实例。

> 事实溯源：F-059

### get_tools_definition_code()

```python
def get_tools_definition_code(tools: Dict[str, Tool]) -> str
```

将工具字典转换为 Python 代码字符串，包含每个工具的定义和初始化代码。这个代码字符串在 CodeAgent 的执行器中被 `exec()` 执行，将工具函数注入到 Python 命名空间，使模型可以在代码块中直接调用工具。

> 事实溯源：F-060

### get_tool_json_schema()

```python
def get_tool_json_schema(tool: Tool) -> dict
```

将 Tool 实例转换为 OpenAI function calling 标准格式的 JSON Schema，供 ToolCallingAgent 传递给模型的 `tools_to_call_from` 参数。

> 事实溯源：F-079

## 代码示例

### @tool 装饰器创建自定义工具

```python
from codified_smolagents import tool, CodeAgent, HfApiModel

# 定义一个简单的计算器工具
@tool
def calculator(expression: str) -> str:
    """计算数学表达式的值。支持加减乘除、幂运算和常用数学函数。

    Args:
        expression: 要计算的数学表达式字符串，如 "2**10 + 3*5"

    Returns:
        计算结果的字符串表示
    """
    import math
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith('_')}
    allowed_names.update({'abs': abs, 'round': round, 'min': min, 'max': max})
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"

# 定义一个文本统计工具
@tool
def text_stats(text: str) -> str:
    """统计文本的字符数、单词数和行数。

    Args:
        text: 要统计的文本字符串

    Returns:
        包含统计结果的字符串
    """
    chars = len(text)
    words = len(text.split())
    lines = len(text.splitlines()) or 1
    return f"字符数: {chars}, 单词数: {words}, 行数: {lines}"

# 使用自定义工具创建Agent
model = HfApiModel()
agent = CodeAgent(
    tools=[calculator, text_stats],
    model=model,
    additional_authorized_imports=['math'],
    max_steps=5,
)

result = agent.run("计算 (2**20 + 3**10) 的值，然后统计结果字符串的字符数")
print(result)
```

### Tool 子类创建方式

```python
from codified_smolagents import Tool, ToolCallingAgent, HfApiModel
from typing import Optional

class WeatherTool(Tool):
    name = "get_weather"
    description = "获取指定城市的当前天气信息"
    inputs = {
        "city": {
            "type": "string",
            "description": "要查询天气的城市名称，如 '北京'、'Shanghai'",
        },
        "unit": {
            "type": "string",
            "description": "温度单位，'celsius'（摄氏度）或 'fahrenheit'（华氏度），默认celsius",
            "nullable": True,
        }
    }
    output_type = "string"

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key

    def forward(self, city: str, unit: str = "celsius") -> str:
        # 实际实现中调用天气API
        # 这里返回模拟数据
        temp = 25 if unit == "celsius" else 77
        return f"{city}当前天气：晴朗，温度{temp}度"

# 使用子类创建工具实例
weather = WeatherTool()
model = HfApiModel()
agent = ToolCallingAgent(
    tools=[weather],
    model=model,
    max_steps=5,
)

result = agent.run("北京今天天气怎么样？如果用华氏度是多少度？")
print(result)
```

### 工具保存与加载

```python
from codified_smolagents import tool, Tool
import os

@tool
def reverse_text(text: str) -> str:
    """反转输入的文本字符串。

    Args:
        text: 要反转的文本

    Returns:
        反转后的文本
    """
    return text[::-1]

# 保存工具到目录
output_dir = "./my_tools"
reverse_text.save(output_dir, make_gradio_app=False)
print(f"工具已保存到 {output_dir}/")

# 从代码字符串动态加载
import importlib.util, sys

# 读取保存的代码
tool_file = os.path.join(output_dir, "reverse_text.py")
with open(tool_file, "r", encoding="utf-8") as f:
    code = f.read()

# 使用from_code加载
loaded_tool = Tool.from_code(code)
print(f"加载的工具: {loaded_tool.name}")
print(f"描述: {loaded_tool.description}")
print(f"测试调用: {loaded_tool(text='hello world')}")
```

### 查看工具 Schema

```python
from codified_smolagents import tool, get_tool_json_schema
import json

@tool
def search_database(query: str, limit: int = 10, fuzzy: bool = False) -> str:
    """在数据库中搜索记录。

    Args:
        query: 搜索关键词
        limit: 返回结果最大数量，默认10
        fuzzy: 是否使用模糊匹配，默认False

    Returns:
        搜索结果
    """
    return f"搜索 '{query}' 的结果"

# 查看工具的完整定义
print("=== 工具四要素 ===")
print(f"name: {search_database.name}")
print(f"description: {search_database.description}")
print(f"output_type: {search_database.output_type}")
print(f"inputs: {json.dumps(search_database.inputs, ensure_ascii=False, indent=2)}")

# 查看OpenAI function calling格式的JSON Schema
schema = get_tool_json_schema(search_database)
print(f"\n=== JSON Schema ===")
print(json.dumps(schema, ensure_ascii=False, indent=2))
```

### 工具开发三步法总结

```python
# ========== 第一步：定义函数 ==========
# 函数名即工具名，使用小写+下划线命名
@tool
def my_custom_tool(
    param1: str,    # 类型注解自动生成Schema类型
    param2: int = 5,  # 有默认值的参数标记为可选
) -> str:            # 返回值注解生成output_type
    # ========== 第二步：写好docstring ==========
    """一句话说清工具做什么（这就是LLM看到的工具描述）。

    详细说明可以写在这里（可选），LLM也会看到。

    Args:
        param1: 参数1是做什么的，LLM据此决定传什么值
        param2: 参数2是做什么的，默认5

    Returns:
        返回值描述
    """
    # ========== 第三步：实现forward逻辑 ==========
    result = f"处理了 {param1}，参数2={param2}"
    return result
```

> 事实溯源：F-047~F-060、F-079

## 常见问题/注意事项

### name 必须是唯一的有效 Python 标识符

工具名在一个 Agent 的 `tools` 和 `managed_agents` 字典中必须唯一。框架在 `_setup_tools()` 中检测重名冲突。name 应使用小写字母+下划线的蛇形命名法（如 `web_search`、`get_weather`），不要使用中文或特殊字符。

### description 是 LLM 选择工具的唯一依据

LLM 只能看到工具的 name、description、inputs（参数名+类型+描述）。description 应该清晰、准确地描述工具的功能和适用场景，避免模糊或过于宽泛的描述。好的 description 能显著提高工具选择准确率。

### 类型注解不完整会导致 inputs 缺失

`@tool` 装饰器依赖类型注解生成 inputs Schema。如果参数缺少类型注解，该参数可能不会出现在 Schema 中，导致 LLM 无法正确传参。务必为所有参数添加类型注解。

### forward() 不应直接调用外部应使用 __call__()

虽然可以直接调用 `tool.forward()`，但推荐使用 `tool()` 即 `__call__()` 方法，因为后者经过参数验证和可选的输出类型处理。框架内部执行工具时通过 `__call__` 调用。

### ToolCollection 不是 dict

`ToolCollection` 只实现了 `__iter__`、`__getitem__`、`__len__`，不支持 `.keys()`、`.values()`、`.items()` 等字典方法。Agent 内部将工具存储在 `self.tools` 字典中（key 为 tool.name），ToolCollection 主要用于批量传递和展示。

### 工具的 requirements 属性

Tool 类有一个可选的 `requirements` 属性（`to_dict()` 中包含），用于声明工具依赖的 Python 包列表。当保存工具或从 Hub 加载时，这些依赖会被写入 `requirements.txt`。

### sanitize_inputs_outputs 参数

`__call__(sanitize_inputs_outputs=True)` 时，框架对输出调用 `handle_agent_output_types()`，将返回值包装为 `AgentText`/`AgentImage`/`AgentAudio` 等类型，确保输出格式统一。默认 `False`，返回原始值。

## 相关链接

- [ToolCallingAgent：函数调用范式](/concepts/05-tool-calling-agent.md) — 工具如何通过function calling被调用
- [CodeAgent：代码执行范式](/concepts/06-code-agent.md) — 工具如何注入到Python命名空间
- [内置工具详解](/concepts/08-builtin-tools.md) — 框架提供的默认工具实现
- [模型抽象层与多后端](/concepts/09-model-layer.md) — get_tool_json_schema与模型对接
- [Tools API 参考](/references/tools-api.md) — Tool基类及所有子类完整API
