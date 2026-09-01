---
type: concept
title: "工具调用（Function Calling）"
description: "掌握 Claude 工具调用能力：tools 参数定义、JSON Schema 输入格式、tool_choice 策略、多轮工具调用循环、tool_result 回传、并行工具调用与流式工具处理，以及 Beta 内置工具概览。"
tags: [tools, function-calling, tool-use, json-schema, tool-choice, tool-result, agents]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-038~F-048
    resource: /python-sdk/references/tools-beta.md
    title: "Anthropic Python SDK 工具系统与 Beta API 参考"
  - id: F-016~F-025
    resource: /python-sdk/references/messages-api.md
    title: "Anthropic Python SDK 消息 API 与流式处理参考"
  - id: F-007
    resource: /python-sdk/references/sdk-client.md
    title: "Anthropic Python SDK 客户端入口与基础设施参考"
---

# 工具调用（Function Calling）

工具调用（Tool Use / Function Calling）是大语言模型最强大的能力之一——它让 Claude 不再局限于"只会说话"，而是能够主动调用外部函数、查询数据库、访问 API、执行计算，从而完成真实世界的任务。你可以把工具理解为给 Claude 配备的"手和脚"：模型负责思考"该做什么"，你的代码负责"实际执行"。

本文档将讲解工具调用的核心概念、如何定义工具、工具选择策略、多轮调用循环、并行工具处理，以及 SDK 提供的高级工具运行器。

## 什么是工具调用

在没有工具的情况下，Claude 只能根据训练数据回答问题——它不知道今天的天气、无法查询你的数据库、不能读取本地文件。工具调用机制允许你向 Claude 描述一组可用的"工具"（本质是函数），当 Claude 判断需要使用工具时，它会返回一个结构化的工具调用请求，你的代码负责执行这个函数，然后将结果返回给 Claude，Claude 再根据工具返回的结果继续回答。

这是一个典型的"增强推理"循环：

```
用户提问 → Claude 思考 → 需要工具？→ 是 → 返回 tool_use 请求
                                         ↓
                                    你的代码执行工具
                                         ↓
                                    返回 tool_result 给 Claude
                                         ↓
                                    Claude 根据结果继续推理 → 最终回答
```

## tools 参数：定义可用工具

要让 Claude 使用工具，你需要在 `messages.create()` 中传入 `tools` 参数——这是一个工具定义列表，每个工具是一个字典，包含三个核心字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 工具名称，必须是唯一的合法标识符 |
| `description` | `str` | 工具功能描述，告诉 Claude 什么时候该用这个工具 |
| `input_schema` | `dict` | 工具输入参数的 JSON Schema 定义 |

### 一个简单的工具定义示例

```python
from anthropic import Anthropic

client = Anthropic()

tools = [
    {
        "name": "get_weather",
        "description": "获取指定城市的当前天气信息。当用户询问天气相关问题时使用此工具。",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "要查询天气的城市名称，例如：北京、上海、New York"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "温度单位，默认摄氏度",
                    "default": "celsius"
                }
            },
            "required": ["city"]
        }
    }
]
```

### input_schema：JSON Schema 格式

`input_schema` 必须是有效的 JSON Schema（Draft 2020-12 兼容），Claude 根据这个 schema 生成结构化的函数参数。编写 input_schema 的要点：

1. **根节点必须是 `type: "object"`**：工具输入总是一个 JSON 对象
2. **`properties` 定义参数**：每个参数指定类型和描述
3. **`required` 列出必填参数**：Claude 一定会提供这些参数
4. **写好 `description`**：这是给 Claude 看的"参数使用说明"，描述越清晰，Claude 传参越准确
5. **善用 `enum`**：当参数只能取几个固定值时，用 enum 限制可选值
6. **支持嵌套对象和数组**：复杂参数可以嵌套定义

### 定义多个工具

你可以一次传入多个工具，Claude 会根据用户问题自主选择使用哪个（或哪些）：

```python
tools = [
    {
        "name": "get_weather",
        "description": "获取城市天气",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "search_web",
        "description": "搜索互联网获取最新信息。当需要实时数据、新闻、最新事件时使用。",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"},
                "num_results": {"type": "integer", "description": "返回结果数量", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "calculate",
        "description": "执行数学计算。当涉及数值计算、单位换算、数学表达式求值时使用。",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "数学表达式，例如：2 + 3 * 4"}
            },
            "required": ["expression"]
        }
    }
]
```

## tool_choice 参数：控制工具选择策略

默认情况下，Claude 会自主决定是否使用工具（`tool_choice: "auto"`）。你可以通过 `tool_choice` 参数精确控制工具选择行为：

| tool_choice 值 | 行为 | 适用场景 |
|---------------|------|---------|
| `"auto"`（默认） | Claude 自主决定是否调用工具、调用哪个 | 大多数对话场景 |
| `"any"` | 强制 Claude 必须调用**至少一个**工具 | 你确定需要工具获取信息才能回答 |
| `"required"` | 同 any，强制必须调用工具 | 兼容旧版本 |
| `{"type": "tool", "name": "xxx"}` | 强制 Claude 调用**指定名称**的工具 | 工作流中确定下一步要用某个工具 |
| `"none"` | 禁止 Claude 调用工具，只生成文本 | 纯文本生成阶段 |

### 强制调用指定工具示例

```python
# 强制调用 get_weather 工具
message = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[{"role": "user", "content": "天气怎么样"}],
    tools=tools,
    tool_choice={"type": "tool", "name": "get_weather"}
)
```

## 响应中的 tool_use 内容块

当 Claude 决定调用工具时，响应的 `content` 数组中会包含 `ToolUseBlock` 类型的内容块（而不是或除了 `TextBlock`）。

### ToolUseBlock 结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | `str` | 固定为 `"tool_use"` |
| `id` | `str` | 工具调用唯一 ID，格式如 `"toolu_0123456789abcdef"`，回传结果时需要用到 |
| `name` | `str` | 要调用的工具名称，对应你定义的 `name` 字段 |
| `input` | `dict` | Claude 生成的工具输入参数，符合你定义的 `input_schema` |

### 解析 tool_use 响应

```python
message = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[{"role": "user", "content": "北京今天天气如何？"}],
    tools=tools,
)

print(f"stop_reason: {message.stop_reason}")

# 检查是否有工具调用
for block in message.content:
    if block.type == "text":
        print(f"[思考] {block.text}")
    elif block.type == "tool_use":
        print(f"[工具调用]")
        print(f"  工具 ID: {block.id}")
        print(f"  工具名称: {block.name}")
        print(f"  参数: {block.input}")
```

当响应包含 `tool_use` 块时，`stop_reason` 会是 `"tool_use"`，这告诉你需要执行工具并继续对话。

## 工具调用循环：执行工具并回传结果

收到 `tool_use` 后，你需要：
1. 根据 `name` 找到对应的工具实现
2. 使用 `input` 参数执行工具
3. 将结果包装为 `tool_result` 消息，追加到消息历史
4. 再次调用 `messages.create()`，把包含结果的消息历史传回去

### tool_result 消息格式

`tool_result` 是一种特殊的消息内容块，格式如下：

```python
{
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": "toolu_0123456789abcdef",  # 对应 tool_use 的 id
            "content": "工具执行的结果（字符串或内容块数组）"
        }
    ]
}
```

| 字段 | 说明 |
|------|------|
| `type` | 固定为 `"tool_result"` |
| `tool_use_id` | 必须与对应的 `tool_use.id` 完全匹配，Claude 靠这个 ID 对应请求和结果 |
| `content` | 工具返回的结果，可以是字符串（最常见）或内容块数组（支持图片等多模态结果） |
| `is_error` | 可选布尔值，标记工具执行是否出错 |

### 完整的单轮工具调用示例

```python
def get_weather_impl(city: str, unit: str = "celsius") -> str:
    """实际的天气查询实现（这里是模拟）"""
    # 实际项目中这里会调用真实的天气 API
    return f"{city}当前天气：晴天，25°{ 'C' if unit == 'celsius' else 'F' }，湿度45%，微风。"

# 消息历史
messages = [{"role": "user", "content": "北京和上海今天天气怎么样？哪个更热？"}]

# 第一次调用：Claude 决定调用工具
response = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=messages,
    tools=tools,
)

# 将助手的响应（包含 tool_use）加入历史
messages.append({"role": "assistant", "content": response.content})

# 执行工具并回传
while response.stop_reason == "tool_use":
    tool_results = []
    
    for block in response.content:
        if block.type == "tool_use":
            # 执行工具
            if block.name == "get_weather":
                result = get_weather_impl(**block.input)
            else:
                result = f"未知工具: {block.name}"
            
            # 构造 tool_result
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result
            })
    
    # 将工具结果作为 user 消息加入历史
    messages.append({"role": "user", "content": tool_results})
    
    # 再次调用 Claude，让它根据工具结果继续
    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=messages,
        tools=tools,
    )
    
    messages.append({"role": "assistant", "content": response.content})

# 循环结束，response 是最终回答
final_reply = next(b.text for b in response.content if b.type == "text")
print(f"最终回答：{final_reply}")
```

这个 `while response.stop_reason == "tool_use"` 循环是处理工具调用的标准模式——Claude 可能需要多轮工具调用才能完成任务（比如先查天气，再根据结果查其他信息）。

## 多工具并行调用

Claude 支持在一次响应中同时请求调用多个工具（并行工具调用）。这在需要多个独立数据时非常高效——比如同时查询多个城市的天气，不需要等一个查完再查下一个。

在代码层面，并行调用表现为 `response.content` 中有多个 `tool_use` 块。你需要一次性执行所有工具，然后将多个 `tool_result` 放在同一条 user 消息中：

```python
# 假设 response.content 中有两个 tool_use：北京和上海
response = client.messages.create(...)

tool_results = []
for block in response.content:
    if block.type == "tool_use":
        if block.name == "get_weather":
            result = get_weather_impl(**block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result
            })

# 一次性回传所有结果
messages.append({"role": "user", "content": tool_results})
```

你不需要（也不应该）逐个回传工具结果——把所有结果打包在一条消息里即可。

## 流式工具调用处理

在流式模式下处理工具调用需要累积 `input_json_delta` 片段，这在 [03-streaming.md](03-streaming.md) 中有详细讲解。核心要点：

1. 监听 `content_block_start` 事件，当 `content_block.type == "tool_use"` 时，记录工具名称和 ID，并初始化一个空字符串用于累积 JSON
2. 在 `content_block_delta` 事件中，如果是 `input_json_delta`，将 `partial_json` 追加到累积字符串
3. 在 `content_block_stop` 事件中，使用 `json.loads()` 解析完整的 JSON
4. 不要在累积中途尝试解析 JSON——partial_json 可能在任意位置断开

## @beta_tool 装饰器：简化工具定义

SDK 提供了 `@beta_tool` 和 `@beta_async_tool` 装饰器，可以自动从 Python 函数的类型注解和 docstring 生成工具定义，无需手动编写 input_schema：

```python
from anthropic.lib.tools import beta_tool

@beta_tool
def get_weather(city: str, unit: str = "celsius") -> str:
    """获取指定城市的当前天气信息。

    Args:
        city: 要查询天气的城市名称
        unit: 温度单位，celsius 或 fahrenheit
    """
    return f"{city}：晴天，25°C"

# 装饰后的对象可以直接传给 tools 参数
# get_weather 是 BetaFunctionTool 实例，有 .name, .description, .input_schema, .call() 方法
```

`@beta_tool` 会自动：
- 从函数名提取 `name`
- 从 docstring 提取 `description` 和参数描述
- 从类型注解生成 JSON Schema `input_schema`

对于复杂场景，你也可以带参数使用装饰器自定义名称和描述：

```python
@beta_tool(name="query_weather", description="查询天气，支持中国主要城市")
def get_weather(city: str) -> str:
    ...
```

## ToolRunner：自动工具运行器

SDK 还提供了 `ToolRunner`（在 `lib.tools` 模块中），可以自动处理整个工具调用循环，你只需要提供工具函数，不需要手动写 while 循环。`ToolRunner` 的核心逻辑是 `_STOP_REASON_STEPS` 映射：

| stop_reason | 下一步动作 |
|------------|-----------|
| `"tool_use"` | 执行所有工具，继续循环 |
| `"end_turn"` | 对话结束，返回最终消息 |
| `"max_tokens"` | 达到 token 上限，停止循环 |

使用 ToolRunner 可以大幅简化代码，具体用法将在示例文档中展示。

## Beta 内置工具概览

除了自定义工具，SDK 的 Beta 命名空间还提供了内置工具支持：

| 工具类型 | 说明 | 参考文档 |
|---------|------|---------|
| Memory Tool | 长期记忆存储，让 Claude 记住跨对话的信息 | [08-beta-agents.md](08-beta-agents.md) |
| MCP（Model Context Protocol） | 标准化的工具协议，支持接入外部工具服务 | [工具系统与 Beta API 参考](../references/tools-beta.md) |
| Agent Toolset | 托管智能体的工具集，包含多种预置能力 | [08-beta-agents.md](08-beta-agents.md) |

这些工具通过 `client.beta` 命名空间访问，属于实验性功能，使用时会自动添加对应的 `anthropic-beta` 请求头。

> ⚠️ Beta API 可能在未来版本发生破坏性变更，生产环境使用请锁定版本。

## 工具错误处理

当工具执行出错时，可以将 `is_error: true` 设置在 `tool_result` 中，并把错误信息放在 `content` 里，Claude 会看到错误并尝试修正或告知用户：

```python
try:
    result = execute_tool(**block.input)
    tool_result_content = result
    is_error = False
except Exception as e:
    tool_result_content = f"工具执行出错：{str(e)}"
    is_error = True

tool_results.append({
    "type": "tool_result",
    "tool_use_id": block.id,
    "content": tool_result_content,
    "is_error": is_error
})
```

另外，SDK 定义了 `ToolError` 异常类（`anthropic.lib.tools.ToolError`），用于工具系统内部的错误传递，其 `content` 属性携带错误结果。

## 最佳实践

1. **工具描述要清晰**：`description` 是 Claude 判断是否使用该工具的唯一依据，写清楚"什么时候用""做什么""不要什么时候用"
2. **参数粒度适中**：不要设计过于复杂的嵌套参数，也不要把所有参数塞成一个字符串
3. **返回结果简洁有用**：工具返回的内容会被 Claude 阅读，返回结构化数据或关键信息即可，不需要多余的客套话
4. **始终检查 stop_reason**：不要假设一次调用就结束，用 while 循环处理多轮工具调用
5. **并行调用优先**：当需要多个独立数据时，让 Claude 一次请求多个工具，减少往返次数
6. **妥善保存 tool_use_id**：回传结果时 ID 必须完全匹配，不能丢失或写错

## 相关概念

- [Messages API 基础](02-messages-basics.md) — 理解消息格式、content 块结构和 stop_reason 含义
- [流式处理](03-streaming.md) — 学习如何在流式模式下累积和处理工具调用的 JSON 增量
- [Beta Agents 体系](08-beta-agents.md) — 深入了解内置 Memory 工具、MCP 和托管智能体
- [工具调用示例](../examples/03-tool-use.md) — 完整可运行的天气查询助手示例代码
- [Anthropic Python SDK 工具系统与 Beta API 参考](../references/tools-beta.md) — beta_tool 装饰器、BetaToolRunner、Beta 命名空间的完整 API 参考
