---
type: example
title: "工具调用实战"
description: "完整的工具调用示例：定义工具、多轮工具调用循环、天气查询mock、并行工具处理，以及工具错误处理。"
tags: [tools, function-calling, tool-use, weather, parallel-tools, multi-turn]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-038~F-048
    resource: /python-sdk/references/tools-beta.md
    title: "Anthropic Python SDK 工具系统与 Beta API 参考"
  - id: F-016~F-023
    resource: /python-sdk/references/messages-api.md
    title: "Anthropic Python SDK 消息 API 与流式处理参考"
  - id: concept-04
    resource: /python-sdk/concepts/04-tool-use.md
    title: "工具调用（Function Calling）"
---

# 工具调用实战

本示例通过一个天气查询助手场景，完整演示 Anthropic Python SDK 的工具调用（Function Calling）能力。你将学习：如何定义工具（JSON Schema 格式）、工具选择策略、多轮工具调用循环、并行工具处理、工具错误处理，以及如何将工具结果回传给 Claude 获取最终回答。

## 场景说明

我们将构建一个简单的天气助手，支持以下能力：
- 查询指定城市的当前天气
- 查询未来几天的天气预报
- 计算两个城市的温差
- Claude 自主判断何时调用哪个工具，可能连续调用多个工具

## 前置准备

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

## 完整代码

```python
import os
import json
from anthropic import Anthropic


# ========== 工具实现（Mock 数据，实际项目中调用真实 API） ==========

def get_current_weather(city: str, unit: str = "celsius") -> str:
    """
    获取指定城市的当前天气（模拟实现）。

    Args:
        city: 城市名称
        unit: 温度单位，celsius（摄氏度）或 fahrenheit（华氏度）

    Returns:
        天气信息字符串
    """
    # 模拟天气数据（实际项目中这里会调用真实的天气 API，如 OpenWeatherMap）
    mock_weather_data = {
        "北京": {"temp": 28, "condition": "晴", "humidity": 45, "wind": "东北风3级"},
        "上海": {"temp": 32, "condition": "多云", "humidity": 72, "wind": "东南风2级"},
        "广州": {"temp": 35, "condition": "雷阵雨", "humidity": 85, "wind": "南风4级"},
        "深圳": {"temp": 34, "condition": "阵雨", "humidity": 80, "wind": "西南风3级"},
        "杭州": {"temp": 30, "condition": "阴", "humidity": 68, "wind": "东风2级"},
        "成都": {"temp": 26, "condition": "小雨", "humidity": 78, "wind": "北风1级"},
        "New York": {"temp": 22, "condition": "Partly Cloudy", "humidity": 55, "wind": "NW 10mph"},
        "Tokyo": {"temp": 29, "condition": "Sunny", "humidity": 60, "wind": "E 5mph"},
    }

    city_normalized = city.strip()
    if city_normalized not in mock_weather_data:
        return json.dumps({
            "error": f"未找到城市 '{city}' 的天气数据，支持的城市：{', '.join(mock_weather_data.keys())}"
        }, ensure_ascii=False)

    data = mock_weather_data[city_normalized]

    # 温度转换
    temp = data["temp"]
    if unit == "fahrenheit":
        temp = round(temp * 9 / 5 + 32, 1)
        temp_unit = "°F"
    else:
        temp_unit = "°C"

    result = {
        "city": city_normalized,
        "temperature": temp,
        "unit": temp_unit,
        "condition": data["condition"],
        "humidity": f"{data['humidity']}%",
        "wind": data["wind"],
        "observation_time": "2026-08-27 14:00"
    }

    return json.dumps(result, ensure_ascii=False)


def get_weather_forecast(city: str, days: int = 3) -> str:
    """
    获取指定城市未来几天的天气预报（模拟实现）。

    Args:
        city: 城市名称
        days: 预报天数，1-7天

    Returns:
        天气预报 JSON 字符串
    """
    if days < 1 or days > 7:
        return json.dumps({"error": "days 参数必须在 1-7 之间"}, ensure_ascii=False)

    conditions = ["晴", "多云", "阴", "小雨", "中雨", "雷阵雨"]
    forecast = []

    for i in range(days):
        import random
        base_temp = random.randint(22, 35)
        forecast.append({
            "date": f"2026-08-{28 + i}",
            "condition": random.choice(conditions),
            "temp_high": base_temp + random.randint(0, 5),
            "temp_low": base_temp - random.randint(3, 8),
            "probability_of_precipitation": f"{random.randint(0, 80)}%",
        })

    return json.dumps({
        "city": city,
        "forecast_days": days,
        "forecast": forecast
    }, ensure_ascii=False)


def calculate_temp_diff(city1: str, city2: str, unit: str = "celsius") -> str:
    """
    计算两个城市之间的温差（模拟实现）。

    Args:
        city1: 第一个城市
        city2: 第二个城市
        unit: 温度单位

    Returns:
        温差计算结果
    """
    mock_temps = {"北京": 28, "上海": 32, "广州": 35, "深圳": 34, "杭州": 30, "成都": 26}

    if city1 not in mock_temps or city2 not in mock_temps:
        return json.dumps({"error": f"不支持的城市，支持：{', '.join(mock_temps.keys())}"}, ensure_ascii=False)

    t1 = mock_temps[city1]
    t2 = mock_temps[city2]
    diff = abs(t1 - t2)

    return json.dumps({
        "city1": city1,
        "temp1": t1,
        "city2": city2,
        "temp2": t2,
        "difference": diff,
        "unit": "°C" if unit == "celsius" else "°F",
        "hotter_city": city1 if t1 > t2 else city2
    }, ensure_ascii=False)


# ========== 工具定义（JSON Schema 格式，传给 Claude） ==========

tools = [
    {
        "name": "get_current_weather",
        "description": "获取指定城市的当前天气信息，包括温度、天气状况、湿度、风力等。当用户询问某个地方现在天气如何、冷不冷、热不热、下不下雨时，使用此工具。",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "要查询天气的城市名称，例如：北京、上海、广州、New York、Tokyo"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "温度单位，celsius 是摄氏度，fahrenheit 是华氏度。中国用户默认用摄氏度。",
                    "default": "celsius"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "get_weather_forecast",
        "description": "获取指定城市未来几天的天气预报。当用户询问未来天气、明天下不下雨、这周天气如何时，使用此工具。",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称"
                },
                "days": {
                    "type": "integer",
                    "description": "预报天数，1-7天，默认3天",
                    "minimum": 1,
                    "maximum": 7,
                    "default": 3
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "calculate_temp_diff",
        "description": "计算两个城市之间的温度差。当用户比较两个城市哪里更热/更冷、温差多少时使用。",
        "input_schema": {
            "type": "object",
            "properties": {
                "city1": {
                    "type": "string",
                    "description": "第一个城市名称"
                },
                "city2": {
                    "type": "string",
                    "description": "第二个城市名称"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "default": "celsius"
                }
            },
            "required": ["city1", "city2"]
        }
    }
]


# ========== 工具分发器：根据名称执行对应工具 ==========

def execute_tool(tool_name: str, tool_input: dict) -> tuple[str, bool]:
    """
    执行指定名称的工具，返回结果和是否出错。

    Args:
        tool_name: 工具名称
        tool_input: 工具输入参数（字典）

    Returns:
        (结果字符串, is_error)
    """
    tool_map = {
        "get_current_weather": get_current_weather,
        "get_weather_forecast": get_weather_forecast,
        "calculate_temp_diff": calculate_temp_diff,
    }

    if tool_name not in tool_map:
        return f"错误：未知工具 '{tool_name}'", True

    try:
        result = tool_map[tool_name](**tool_input)
        return result, False
    except Exception as e:
        return f"工具执行出错：{type(e).__name__}: {str(e)}", True


# ========== 核心：带工具调用的对话函数 ==========

def chat_with_tools(client: Anthropic, user_message: str, messages: list, system_prompt: str) -> str:
    """
    处理一条用户消息，自动处理可能的多轮工具调用，返回 Claude 的最终文本回答。

    Args:
        client: Anthropic 客户端
        user_message: 用户输入的消息
        messages: 对话历史列表（会被原地修改）
        system_prompt: 系统提示词

    Returns:
        Claude 的最终文本回答
    """
    # 添加用户消息到历史
    messages.append({"role": "user", "content": user_message})

    # 工具调用循环：可能需要多轮调用
    while True:
        # 调用 Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=2048,
            system=system_prompt,
            messages=messages,
            tools=tools,
            tool_choice="auto",  # Claude 自主决定是否调用工具
        )

        # 将助手响应加入历史（包含可能的 tool_use 块）
        messages.append({"role": "assistant", "content": response.content})

        # 检查 stop_reason：如果不是 tool_use，说明回答完毕
        if response.stop_reason != "tool_use":
            break

        # 有工具调用，执行所有工具（支持并行调用多个工具）
        tool_results = []

        print(f"\n[系统] Claude 请求了 {sum(1 for b in response.content if b.type == 'tool_use')} 个工具调用：")

        for block in response.content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input
                tool_use_id = block.id

                print(f"  → 调用 {tool_name}({json.dumps(tool_input, ensure_ascii=False)})")

                # 执行工具
                result_content, is_error = execute_tool(tool_name, dict(tool_input))

                if is_error:
                    print(f"    ✗ 失败：{result_content}")
                else:
                    print(f"    ✓ 成功")

                # 构造 tool_result
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": result_content,
                    "is_error": is_error
                })

        # 将工具结果作为 user 消息加入历史
        messages.append({"role": "user", "content": tool_results})

    # 循环结束，提取最终文本回答
    final_text = ""
    for block in response.content:
        if block.type == "text":
            final_text += block.text

    return final_text


# ========== 交互式天气助手 ==========

def weather_assistant_demo(client: Anthropic) -> None:
    """
    演示天气助手：单轮查询，自动处理工具调用。
    """
    system_prompt = """你是一个专业的天气助手，可以帮助用户查询天气信息。
    你可以使用以下工具：
    - get_current_weather：查询当前天气
    - get_weather_forecast：查询未来天气预报
    - calculate_temp_diff：比较两个城市温差

    回答要求：
    1. 用自然、友好的中文回答用户问题
    2. 根据工具返回的数据回答，不要编造数据
    3. 如果需要多次调用工具才能回答，直接调用即可
    4. 温度默认使用摄氏度，除非用户明确要求华氏度
    5. 回答简洁明了，提供有用的建议（如带伞、注意防晒等）
    """

    messages = []

    # 测试问题列表
    test_questions = [
        "北京现在天气怎么样？",
        "北京和上海哪里更热？差多少度？",
        "广州未来3天天气如何？需要带伞吗？",
    ]

    for question in test_questions:
        print("\n" + "=" * 60)
        print(f"用户：{question}")
        print("-" * 60)

        answer = chat_with_tools(client, question, messages, system_prompt)
        print(f"\n助手：{answer}")

        print(f"\n[统计] 对话历史长度：{len(messages)} 条消息")


def interactive_weather_chat(client: Anthropic) -> None:
    """
    交互式天气助手：命令行持续对话。
    """
    system_prompt = """你是一个专业的天气助手，可以查询天气、预报、比较温差。
    用中文友好回答，根据工具数据给出实用建议。"""

    messages = []

    print("=" * 60)
    print("🌤️  天气助手（输入 'quit' 退出，'clear' 清空历史）")
    print("=" * 60)
    print("支持的城市：北京、上海、广州、深圳、杭州、成都等")
    print("你可以问：北京天气怎么样？北京上海哪里热？广州明天下雨吗？")
    print()

    while True:
        try:
            user_input = input("你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("再见！")
            break
        if user_input.lower() == "clear":
            messages = []
            print("[对话历史已清空]")
            continue

        try:
            answer = chat_with_tools(client, user_input, messages, system_prompt)
            print(f"\n助手：{answer}\n")
        except Exception as e:
            print(f"\n❌ 出错了：{type(e).__name__}: {e}\n")


# ========== 主函数 ==========

if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("错误：请先设置 ANTHROPIC_API_KEY 环境变量")
        exit(1)

    client = Anthropic()

    # 1. 运行演示问题（自动运行3个测试问题）
    weather_assistant_demo(client)

    # 2. 启动交互式聊天（取消注释体验）
    # interactive_weather_chat(client)
```

## 运行方式

```bash
python 03-tool-use.py
```

## 代码解析

### 工具调用的核心循环

工具调用的标准模式是一个 `while True` 循环：

```python
while True:
    response = client.messages.create(..., tools=tools, tool_choice="auto")
    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason != "tool_use":
        break  # 没有工具调用，回答完毕

    # 执行所有工具，构造 tool_results
    ...
    messages.append({"role": "user", "content": tool_results})
```

这个循环的逻辑：
1. 调用 Claude，传入工具定义和对话历史
2. 检查 `stop_reason`：如果是 `"end_turn"`，说明 Claude 已经给出最终回答，退出循环
3. 如果 `stop_reason == "tool_use"`，说明 Claude 需要调用工具
4. 执行所有被请求的工具，将结果以 `tool_result` 格式回传
5. 重复循环，让 Claude 根据工具结果继续推理

Claude 可能需要多轮工具调用（比如先查北京天气，再查上海天气，最后比较温差），这个循环会自动处理直到得到最终回答。

### 工具定义的三个核心字段

每个工具是一个字典，包含三个关键字段：

| 字段 | 作用 | 编写要点 |
|------|------|---------|
| `name` | 工具唯一标识 | 简短、描述性、合法标识符 |
| `description` | 告诉 Claude 什么时候用这个工具 | **这是给 Claude 看的！** 写清楚适用场景，Claude 完全靠这个判断是否调用 |
| `input_schema` | JSON Schema 格式的参数定义 | 每个参数也要写 `description`，越清晰 Claude 传参越准确 |

**新手最容易犯的错误**：`description` 写得太简单。Claude 不知道你的工具是做什么的，就不会正确调用它。务必详细描述"什么时候用""做什么""参数含义"。

### 并行工具调用

Claude 支持在一次响应中请求调用多个工具（比如用户问"北京和上海天气对比"，Claude 会同时请求查两个城市的天气）。代码中只需要遍历 `response.content` 中的所有 `tool_use` 块，一次性执行所有工具，然后将所有 `tool_result` 放在同一条 user 消息中回传即可：

```python
tool_results = []
for block in response.content:
    if block.type == "tool_use":
        result, is_error = execute_tool(block.name, dict(block.input))
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": block.id,  # 必须与 tool_use 的 id 对应！
            "content": result,
            "is_error": is_error
        })

messages.append({"role": "user", "content": tool_results})  # 一次性回传所有结果
```

不需要逐个回传结果，也不需要等一个工具执行完再让 Claude 决定下一个——Claude 会一次性请求所有需要的独立数据。

### tool_use_id 的重要性

`tool_result` 中的 `tool_use_id` **必须**与对应 `tool_use` 块的 `id` 完全匹配。这是 Claude 用来关联"哪个结果对应哪个工具调用"的唯一依据。如果 ID 写错或丢失，Claude 会无法正确处理结果。

```python
# 正确做法
for block in response.content:
    if block.type == "tool_use":
        tool_use_id = block.id  # 保存 ID
        result = execute_tool(...)
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": tool_use_id,  # 对应上
            "content": result
        })
```

### 工具错误处理

工具执行可能出错（网络问题、参数错误、API 限制等）。使用 `is_error: true` 标记错误，并把错误信息放在 `content` 中：

```python
try:
    result = tool_function(**tool_input)
    is_error = False
except Exception as e:
    result = f"错误：{str(e)}"
    is_error = True

tool_results.append({
    "type": "tool_result",
    "tool_use_id": block.id,
    "content": result,
    "is_error": is_error
})
```

Claude 看到 `is_error: true` 后，会理解工具执行失败，可能尝试修正参数重新调用，或者告知用户遇到了问题。

### 消息累积规则

工具调用过程中的消息历史必须**完整累积**，不能省略：

```
user: 北京和上海哪里热？
assistant: [tool_use: get_current_weather(北京), tool_use: get_current_weather(上海)]  ← 加入历史
user: [tool_result(北京), tool_result(上海)]  ← 加入历史
assistant: 上海32°C，北京28°C，上海更热...  ← 最终回答，加入历史
```

每一轮的 `assistant` 消息（包含 tool_use）和对应的 `user` 消息（包含 tool_result）都必须按顺序加入 `messages` 列表，Claude 需要看到完整的对话上下文才能正确推理。

### tool_choice 参数

`tool_choice` 控制工具选择策略：

| 值 | 行为 | 使用场景 |
|----|------|---------|
| `"auto"` | Claude 自主决定是否调用工具 | 默认，大多数对话场景 |
| `"any"` | 强制必须调用至少一个工具 | 你确定需要工具数据才能回答 |
| `{"type": "tool", "name": "xxx"}` | 强制调用指定工具 | 工作流中确定下一步动作 |
| `"none"` | 禁止调用工具 | 纯文本生成阶段 |

本示例使用 `"auto"`，让 Claude 自己判断什么时候需要用工具。

### 系统提示词的作用

在工具调用场景中，系统提示词尤为重要——它不仅定义 Claude 的人设，还可以指导 Claude 如何使用工具、如何回答：

```python
system_prompt = """你是一个专业的天气助手...
回答要求：
1. 用自然、友好的中文回答
2. 根据工具返回的数据回答，不要编造数据
3. 温度默认使用摄氏度...
"""
```

加上"不要编造数据"这样的指令，可以减少 Claude 幻觉的发生，让它更依赖工具返回的真实数据。

## 常见问题

1. **Claude 不调用我定义的工具怎么办？** 检查工具的 `description` 是否写得足够清晰——Claude 完全靠描述判断什么时候用工具。可以更明确地写"当用户问 X 时，必须使用此工具"。

2. **Claude 传错参数怎么办？** 检查 `input_schema` 中每个参数的 `description` 是否清晰。可以加 `enum` 限制可选值，或在描述中举例子。

3. **工具调用无限循环怎么办？** 加一个最大迭代次数限制（比如最多 10 轮），防止异常情况下无限循环。

4. **工具结果应该返回什么格式？** 字符串最方便（可以是 JSON 字符串）。Claude 能很好地解析 JSON 并提取信息。返回关键数据即可，不需要多余的格式。

5. **可以在工具中调用其他 API 吗？** 当然可以！这正是工具调用的意义——你可以在工具实现中调用天气 API、查询数据库、发送邮件、执行计算等任何操作。本示例用 mock 数据只是为了让你能直接运行无需配置外部服务。

## 进阶：使用 @beta_tool 装饰器（简化工具定义）

SDK 提供了 `@beta_tool` 装饰器，可以从 Python 函数自动生成工具定义，无需手写 JSON Schema：

```python
from anthropic.lib.tools import beta_tool

@beta_tool
def get_current_weather(city: str, unit: str = "celsius") -> str:
    """获取指定城市的当前天气信息。

    Args:
        city: 要查询的城市名称，如北京、上海
        unit: 温度单位，celsius 或 fahrenheit
    """
    return f"{city}：晴天，25°C"

# 装饰后的对象可以直接传给 tools 参数
# 它自动包含 .name, .description, .input_schema, .call() 方法
response = client.messages.create(
    ...,
    tools=[get_current_weather],  # 直接传装饰后的函数
)
```

使用 `@beta_tool` 可以让工具定义更简洁，但手动编写 JSON Schema 在需要精细控制时更灵活。两种方式可以混合使用。

## 相关概念

- [Messages API 基础](../concepts/02-messages-basics.md) — 理解消息格式和 stop_reason
- [工具调用（Function Calling）概念](../concepts/04-tool-use.md) — 工具调用原理、JSON Schema 编写指南、ToolRunner 使用
- [流式对话](02-streaming-chat.md) — 结合流式输出和工具调用实现更好的用户体验
- [视觉理解](04-vision.md) — 下一个示例：多模态输入（图片）
- [Anthropic Python SDK 工具系统与 Beta API 参考](../references/tools-beta.md) — @beta_tool 装饰器、ToolRunner 完整 API 参考
