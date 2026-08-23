---
type: example
title: 工具调用
description: 使用 @tool 创建工具、GenericFakeChatModel 模拟工具调用响应、ToolMessage 回传结果的完整流程
tags: [langchain, tools, tool-calling, agent]
generated: { by: "reference_agent/trae-solo", at: 2026-08-23 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23 }
status: stable
stale_after: 2027-02-23
sources:
  - id: ref-msg
    resource: /references/messages-tools.md
    title: 消息与工具源码信源
  - id: ref-po
    resource: /references/prompts-output.md
    title: 提示词、模型与输出解析源码信源
---

# 工具调用

本示例演示 langchain-core 中工具调用（tool calling）的完整数据流：用 `@tool` 创建工具 → 模型返回 `AIMessage` 含 `tool_calls` → 执行工具 → 用 `ToolMessage` 回传结果。示例使用 `GenericFakeChatModel` 模拟返回带 tool_calls 的 AIMessage，真实场景由具体模型（如 ChatOpenAI）经 `bind_tools` 实现。

## 前置条件

- Python ≥ 3.10
- 已安装 `langchain-core`

## 第一步：定义工具

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """查询指定城市的当前天气。"""
    # 真实场景调用天气 API
    weather_data = {"北京": "晴，25°C", "上海": "多云，28°C", "广州": "雨，30°C"}
    return weather_data.get(city, f"暂无 {city} 的天气数据")

@tool
def add(a: float, b: float) -> str:
    """计算两个数字的和。"""
    return str(a + b)

print(get_weather.name)        # "get_weather"
print(get_weather.args)        # JSON schema: {"city": {"title": "City", "type": "string"}}
print(get_weather.description) # "查询指定城市的当前天气。"
```

`@tool`（`tools/convert.py:77`）从函数名、类型注解和 docstring 自动推断工具名、参数 schema 和描述。

## 第二步：模拟模型返回工具调用

`GenericFakeChatModel`（`fake_chat_models.py:227`）接收一个 `AIMessage` 迭代器，每次调用返回下一条预设消息。我们构造一条带 `tool_calls` 的 `AIMessage`：

```python
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.messages.tool import tool_call

# 预设模型响应：第一次调用请求工具，第二次返回最终答案
model_responses = iter([
    AIMessage(
        content="",
        tool_calls=[
            tool_call(name="get_weather", args={"city": "北京"}, id="call_001"),
        ],
    ),
    AIMessage(content="北京今天天气晴，气温25°C，适合外出。"),
])
model = GenericFakeChatModel(messages=model_responses)
```

`tool_call()` 工厂函数（`messages/tool.py:242`）创建合法的 `ToolCall` 字典，含 `name`、`args`、`id`、`type="tool_call"`。

> 真实场景中，用 `model.bind_tools([get_weather, calculator])` 绑定工具，模型自行决定是否调用。基类 `BaseChatModel.bind_tools`（`chat_models.py:2366`）由 partner 包实现。

## 第三步：执行工具调用循环

```python
# 工具名→工具对象映射
tools_by_name = {get_weather.name: get_weather, add.name: add}

# 初始消息
messages = [HumanMessage(content="北京今天天气怎么样？")]

# 第一次模型调用
ai_msg = model.invoke(messages)
messages.append(ai_msg)
print("AI 返回:", ai_msg.content or "(请求工具调用)")
print("工具调用:", ai_msg.tool_calls)

# 执行所有 tool_calls，回传 ToolMessage
for tc in ai_msg.tool_calls:
    tool = tools_by_name[tc["name"]]
    result = tool.invoke(tc["args"])  # BaseTool.invoke 执行 _run
    messages.append(ToolMessage(
        content=result,
        tool_call_id=tc["id"],       # 关联请求与结果
        status="success",
    ))
    print(f"  工具 {tc['name']}({tc['args']}) → {result}")

# 第二次模型调用（模型看到 ToolMessage 后生成最终答案）
final_msg = model.invoke(messages)
print("最终回答:", final_msg.text)
```

预期输出：

```
AI 返回: (请求工具调用)
工具调用: [{'name': 'get_weather', 'args': {'city': '北京'}, 'id': 'call_001', 'type': 'tool_call'}]
  工具 get_weather({'city': '北京'}) → 晴，25°C
最终回答: 北京今天天气晴，气温25°C，适合外出。
```

## 关键机制说明

### ToolMessage 的关联

`ToolMessage.tool_call_id`（`messages/tool.py:67`）必须与 `AIMessage.tool_calls` 中的 `id` 对应，使模型能将多个并行工具结果与请求匹配。`coerce_args` 验证器（第92行）会自动将 UUID/数字类型的 id 转为字符串。

### 工具执行

`BaseTool.invoke`（`tools/base.py:757`）内部：
1. `_parse_input`（第778行）将 dict/ToolCall 解析为 kwargs。
2. 用 `args_schema` 校验参数。
3. 触发 `on_tool_start` 回调。
4. 调用 `_run`（`StructuredTool._run`，`structured.py:74`）执行函数。
5. 成功触发 `on_tool_end`，异常触发 `on_tool_error`（受 `handle_tool_error` 控制）。
6. 返回结果或 `ToolMessage`（含 `status`）。

### 错误处理

工具执行失败时返回 `ToolMessage(status="error")`：

```python
from langchain_core.tools import ToolException

@tool
def risky_tool(x: int) -> int:
    """可能失败的工具。"""
    if x < 0:
        raise ToolException("x 不能为负数")
    return x * 2

# handle_tool_error 是 BaseTool 的实例字段，通过 Pydantic 的 model_copy 设置
safe_tool = risky_tool.model_copy(update={"handle_tool_error": True})
# 错误消息作为结果返回；也可设为 "自定义错误提示" 或 lambda e: f"出错了: {e}"
print(safe_tool.invoke({"x": -1}))  # "x 不能为负数"
```

## Runnable.as_tool 反向适配

任意 Runnable 也可通过 `as_tool`（`runnables/base.py:2708`，beta）转为工具：

```python
from langchain_core.runnables import RunnableLambda

upper = RunnableLambda(lambda x: x["text"].upper())
upper_tool = upper.as_tool(arg_types={"text": str}, name="upper", description="转大写")
print(upper_tool.invoke({"text": "hello"}))  # "HELLO"
```

## 多工具与并行调用

当 `AIMessage.tool_calls` 包含多个调用时，应并行执行（可用 `asyncio.gather`）：

```python
import asyncio

async def run_tool(tc):
    tool = tools_by_name[tc["name"]]
    result = await tool.ainvoke(tc["args"])
    return ToolMessage(content=result, tool_call_id=tc["id"])

tool_messages = await asyncio.gather(*[run_tool(tc) for tc in ai_msg.tool_calls])
messages.extend(tool_messages)
```

`StructuredTool.ainvoke`（`structured.py:60`）在提供 `coroutine` 时使用原生异步，否则回退到线程池。

## 相关概念

- [工具抽象](/langchain-ai/langchain/concepts/tool-abstraction)
- [消息类型](/langchain-ai/langchain/concepts/message-types)
- [聊天模型](/langchain-ai/langchain/concepts/chat-model)
- [回调系统](/langchain-ai/langchain/concepts/callback-system)
