---
type: concept
title: 工具抽象
description: BaseTool 基类、StructuredTool 与 @tool 装饰器、工具调用的输入解析、错误处理与 BaseToolkit
tags: [langchain, tools, base-tool, structured-tool, decorator]
generated: { by: "reference_agent/trae-solo", at: 2026-08-23 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23 }
status: stable
stale_after: 2027-02-23
sources:
  - id: ref-msg
    resource: /references/messages-tools.md
    title: 消息与工具源码信源
---

# 工具抽象

工具（Tool）是 Agent 与外部世界交互的组件。langchain-core 在 `tools/` 目录定义了以 `BaseTool` 为根的工具体系。工具本身也是 `RunnableSerializable`（`tools/base.py:433`），因此具备 Runnable 协议的全部能力（invoke/batch/stream、配置传播、回调追踪），并可通过 `as_tool` 反向将任意 Runnable 转为工具。

## BaseTool

`BaseTool`（`tools/base.py:433`）定义为：

```python
class BaseTool(RunnableSerializable[str | dict[str, Any] | ToolCall, Any]):
```

输入类型可以是字符串、字典或 `ToolCall`，输出类型为任意值。

### 核心字段

| 字段 | 类型 | 行号 | 说明 |
|---|---|---|---|
| `name` | `str` | 474 | 唯一工具名（必填） |
| `description` | `str` | 477 | 告诉模型如何/何时/为何使用此工具 |
| `args_schema` | `ArgsSchema \| None` | 483 | Pydantic 模型或 JSON schema，校验输入参数 |
| `return_direct` | `bool` | 495 | 是否直接返回结果（AgentExecutor 停止循环） |
| `verbose` | `bool` | 502 | 是否记录进度 |
| `callbacks` | `Callbacks` | 505 | 回调（exclude，不序列化） |
| `tags` | `list[str] \| None` | 508 | 标签 |
| `metadata` | `dict \| None` | 518 | 元数据 |
| `handle_tool_error` | `bool \| str \| Callable \| None` | 527 | `ToolException` 处理策略，默认 `False`（抛出） |
| `handle_validation_error` | `bool \| str \| Callable \| None` | 542 | 校验错误处理策略 |
| `response_format` | `"content" \| "content_and_artifact"` | 547 | 响应格式，默认 `"content"` |
| `extras` | `dict \| None` | 555 | provider 特定扩展字段 |

### `handle_tool_error` 策略

- `False`（默认）：异常重新抛出。
- `True`：异常消息作为工具输出返回。
- 字符串：该字符串作为输出返回。
- Callable：接收 `ToolException`，返回值作为输出。若工具以 `tool_call_id` 调用，处理后的内容被包装为 `ToolMessage(status="error")`。

### `response_format`

- `"content"`：工具输出解释为 `ToolMessage.content`。
- `"content_and_artifact"`：输出应为 `(content, artifact)` 二元组，分别对应 `ToolMessage.content` 和 `ToolMessage.artifact`。

### 核心属性与方法

| 成员 | 行号 | 说明 |
|---|---|---|
| `is_single_input` | 598 | 是否只有一个输入参数 |
| `args` | 608 | 返回 JSON schema 字典 |
| `tool_call_schema` | 677 | 工具调用的 Pydantic schema |
| `get_input_schema(config)` | 741 | 输入 schema（Runnable 接口） |
| `invoke(input, config)` | 757 | 执行入口，解析输入、回调、错误处理 |
| `_parse_input(input, *, suppress_args_stripping)` | 778 | 将 str/dict/ToolCall 解析为 kwargs |
| `_run(*args, **kwargs)`（抽象） | 909 | 子类实现的同步执行逻辑 |
| `run(*args, **kwargs)` | 1009 | 直接调用（绕过 Runnable 配置） |

`__init_subclass__`（第441行）在子类创建时校验 `args_schema` 注解类型——如果直接标注为 `BaseModel`（而非 `Type[BaseModel]`）会抛出 `SchemaAnnotationError`。

## StructuredTool

`StructuredTool`（`tools/structured.py:40`）是 `BaseTool` 的具体实现，支持多输入参数，通过包装 Python 函数实现：

| 字段 | 类型 | 行号 | 说明 |
|---|---|---|---|
| `description` | `str` | 43 | 默认空字符串 |
| `args_schema` | `ArgsSchema` | 45 | **必填**（对比 BaseTool 默认 None） |
| `func` | `Callable[..., Any] \| None` | 50 | 同步函数 |
| `coroutine` | `Callable[..., Awaitable] \| None` | 53 | 异步函数 |

`_run` 方法（第74行）调用 `self.func(*args, **kwargs)`，并自动注入：
- 如果函数签名含 `callbacks` 参数，注入 `run_manager.get_child()`。
- 如果函数签名含 config 参数（通过 `_get_runnable_config_param` 检测），注入当前 `RunnableConfig`。

`from_function`（第133行）类方法是从函数构造 `StructuredTool` 的推荐方式，自动从函数签名和类型注解推断 `args_schema`。

## @tool 装饰器

`tool()` 函数（`tools/convert.py:77`）是将 Python 函数或 Runnable 转为工具的最便捷方式，支持4种调用形式：

```python
# 1. 无参装饰器
@tool
def my_tool(x: int) -> str:
    return str(x)

# 2. 带参装饰器
@tool(description="...", return_direct=True)
def my_tool(x: int) -> str: ...

# 3. 命名装饰器工厂
@tool("custom_name")
def my_tool(x: int) -> str: ...

# 4. 从 Runnable 创建（必须提供名字）
tool("my_runnable_tool", runnable)
```

完整签名参数：

| 参数 | 默认值 | 说明 |
|---|---|---|
| `name_or_callable` | `None` | 工具名或被装饰的函数/Runnable |
| `runnable` | `None` | Runnable 实例（与 callable 二选一） |
| `description` | `None` | 工具描述（默认从函数 docstring 推断） |
| `return_direct` | `False` | 是否直接返回 |
| `args_schema` | `None` | 显式 schema（默认从类型注解推断） |
| `infer_schema` | `True` | 是否自动推断 schema |
| `response_format` | `"content"` | 响应格式 |
| `parse_docstring` | `False` | 是否解析 Google 风格 docstring |
| `error_on_invalid_docstring` | `True` | docstring 无效时是否报错 |
| `extras` | `None` | provider 特定扩展 |

### 保留参数名

`config`、`run_manager`、`callbacks` 是保留名（`tools/convert.py:104-112`）：
- `config`：会被注入的 `RunnableConfig` 遮蔽，导致调用时报错。
- `run_manager`/`callbacks`：从生成的 schema 中静默剔除。
- 如需访问运行时状态/上下文/config，应使用 `ToolRuntime` 参数。

## 注入参数

- **`InjectedToolArg`**（`tools/base.py:1726`）：标记一个参数为"注入参数"——不出现在发送给模型的 schema 中，但在工具调用时由框架注入。
- **`InjectedToolCallId`**（第1756行）：`InjectedToolArg` 的子类，专门用于注入当前 `tool_call_id`。

这使得工具可以接收运行时上下文（如配置、状态、store）而不暴露给模型。

## BaseToolkit

`BaseToolkit`（`tools/base.py:1935`）是工具包基类：

```python
class BaseToolkit(BaseModel, ABC):
    @abstractmethod
    def get_tools(self) -> list[BaseTool]: ...
```

一个 toolkit 聚合一组相关工具（如数据库 toolkit 包含 query、list_tables、describe_table 等），通过 `get_tools()` 统一提供。

## Runnable.as_tool

任意 Runnable 可通过 `as_tool`（`runnables/base.py:2708`，beta）转为 `BaseTool`：

```python
as_tool(
    args_schema: type[BaseModel] | None = None,
    *,
    name: str | None = None,
    description: str | None = None,
    arg_types: dict[str, type] | None = None,
) -> BaseTool
```

内部调用 `convert_runnable_to_tool`。schema 推断优先级：显式 `args_schema` > `arg_types` > `runnable.get_input_schema()`。

## 公共导出

`tools/__init__.py` 导出的主要符号（第42-62行）：`BaseTool`、`StructuredTool`、`Tool`、`BaseToolkit`、`ToolException`、`SchemaAnnotationError`、`InjectedToolArg`、`InjectedToolCallId`、`tool`、`convert_runnable_to_tool`、`create_retriever_tool`、`render_text_description`、`render_text_description_and_args`、`ToolsRenderer`。

## 代码示例

```python
from langchain_core.tools import tool, StructuredTool, InjectedToolCallId
from typing import Annotated

# 1. @tool 装饰器（从类型注解推断 schema）
@tool
def multiply(a: int, b: int) -> int:
    """计算两个整数的乘积。"""
    return a * b

assert multiply.name == "multiply"
assert multiply.invoke({"a": 3, "b": 4}) == 12

# 2. 带配置的工具
@tool(return_direct=True, description="查询天气")
def get_weather(city: str) -> str:
    return f"{city} 今天晴"

# 3. StructuredTool.from_function
def search(query: str, limit: int = 5) -> list[str]:
    return [f"result_{i}" for i in range(limit)]

search_tool = StructuredTool.from_function(search)

# 4. 注入 tool_call_id
@tool
def save_result(
    data: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> str:
    return f"saved {tool_call_id}: {data}"

# 5. Runnable.as_tool
from langchain_core.runnables import RunnableLambda
runnable = RunnableLambda(lambda x: x["text"].upper())
upper_tool = runnable.as_tool(arg_types={"text": str})
upper_tool.invoke({"text": "hello"})  # "HELLO"
```

## 相关概念

- [消息类型](/ai/langchain-ai/langchain/concepts/message-types) —— ToolCall 与 ToolMessage 的数据结构
- [聊天模型](/ai/langchain-ai/langchain/concepts/chat-model) —— bind_tools 将工具绑定到模型
- [Runnable 协议](/ai/langchain-ai/langchain/concepts/runnable-protocol) —— BaseTool 本身是 RunnableSerializable
- [回调系统](/ai/langchain-ai/langchain/concepts/callback-system) —— 工具执行触发 on_tool_start/end/error
