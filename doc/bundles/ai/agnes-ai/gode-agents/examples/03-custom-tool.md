---
type: Example
title: 使用 @tool 装饰器创建自定义工具
description: 学习@tool装饰器，创建自定义天气查询/计算器/文本处理工具
tags: [工具, "@tool", 自定义工具]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: tools-source
    resource: /references/tools-api.md
    title: Tools API 参考
  - id: agents-source
    resource: /references/agents-api.md
    title: Agents API 参考
---

# 使用 @tool 装饰器创建自定义工具

## 概述

本示例演示如何使用 `@tool` 装饰器将普通 Python 函数快速转换为 Agent 可用的工具。`@tool` 装饰器会自动从函数签名（类型注解）和 docstring（Google 风格）中提取工具名称、描述和输入参数定义，无需手动编写 JSON Schema。同时演示通过继承 `Tool` 基类的方式创建更复杂的工具。

这个示例解决的核心问题：**如何让 Agent 使用你自己定义的函数/能力来完成任务**。

## 前置条件

- Python 3.10+
- 安装 codified-smolagents：`pip install codified-smolagents`
- Hugging Face API Token（环境变量 `HF_TOKEN`）

## 完整代码

```python
"""
示例 03: 使用 @tool 装饰器创建自定义工具
演示：@tool 基本用法 → 计算器 → 多参数工具 → docstring 规范 → Tool 子类方式
"""

import random
import datetime
from typing import Optional

from codified_smolagents import (
    ToolCallingAgent,
    CodeAgent,
    HfApiModel,
    Tool,
    tool,
)
from codified_smolagents.monitoring import LogLevel

# ============================================================
# 第一部分：@tool 装饰器基本用法
# ============================================================

# ---- 示例1: 最简单的单参数工具 ----
@tool
def greet(name: str) -> str:
    """
    向指定的人打招呼。
    Args:
        name: 要打招呼的人的名字
    """
    return f"你好，{name}！欢迎使用 codified-smolagents！"

# 查看自动生成的工具属性
print("=" * 60)
print("📌 @tool 装饰器自动生成的属性：")
print(f"  工具名称 (name): {greet.name}")
print(f"  工具描述 (description): {greet.description}")
print(f"  输入定义 (inputs): {greet.inputs}")
print(f"  输出类型 (output_type): {greet.output_type}")
print("=" * 60)

# 直接调用工具
result = greet("小明")
print(f"\n🔧 直接调用 greet('小明'): {result}\n")


# ---- 示例2: 计算器工具（数学表达式求值） ----
@tool
def calculator(expression: str) -> float:
    """
    计算数学表达式的值。支持加减乘除、幂运算和括号。
    Args:
        expression: 要计算的数学表达式字符串，例如 "2 + 3 * 4" 或 "(5-2)**2"
    """
    # 使用安全的方式求值（仅允许数学运算）
    import math
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith('_')}
    allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return float(result)
    except Exception as e:
        return f"计算错误: {str(e)}"

print(f"🔧 calculator('(3+5)*2^2'): {calculator('(3+5)*2**2')}")
print(f"🔧 calculator('sqrt(16)+log(2.71828)'): {calculator('sqrt(16)+log(2.71828)')}")


# ---- 示例3: 多参数工具 ----
@tool
def text_processor(text: str, operation: str, n: Optional[int] = 1) -> str:
    """
    对文本进行各种处理操作。
    Args:
        text: 要处理的输入文本
        operation: 处理操作，支持 "upper"(大写)、"lower"(小写)、"reverse"(反转)、
                   "repeat"(重复n次)、"word_count"(词数统计)、"truncate"(截断到n字符)
        n: 重复次数或截断长度，默认为1
    """
    ops = {
        "upper": text.upper(),
        "lower": text.lower(),
        "reverse": text[::-1],
        "repeat": text * n,
        "word_count": f"词数: {len(text.split())}",
        "truncate": text[:n] + ("..." if len(text) > n else ""),
    }
    return ops.get(operation, f"不支持的操作: {operation}。支持的操作: {list(ops.keys())}")

print(f"\n🔧 text_processor('Hello World', 'reverse'): {text_processor('Hello World', 'reverse')}")
print(f"🔧 text_processor('AI', 'repeat', n=3): {text_processor('AI', 'repeat', n=3)}")
print(f"🔧 text_processor('Python is great', 'word_count'): {text_processor('Python is great', 'word_count')}")


# ---- 示例4: 模拟天气查询工具 ----
@tool
def get_weather(city: str, unit: Optional[str] = "celsius") -> str:
    """
    查询指定城市的天气信息。这是一个模拟工具，返回随机天气数据。
    Args:
        city: 要查询天气的城市名称，如 "北京"、"上海"、"New York"
        unit: 温度单位，"celsius"(摄氏度) 或 "fahrenheit"(华氏度)，默认 "celsius"
    """
    # 模拟天气数据
    weather_conditions = ["晴", "多云", "阴", "小雨", "中雨", "雷阵雨", "小雪", "雾"]
    condition = random.choice(weather_conditions)
    temp_c = random.randint(-10, 40)
    humidity = random.randint(20, 95)
    wind_speed = random.randint(0, 30)

    if unit == "fahrenheit":
        temp = temp_c * 9 / 5 + 32
        temp_unit = "°F"
    else:
        temp = temp_c
        temp_unit = "°C"

    return (
        f"🌤 {city} 天气信息：\n"
        f"  天气状况: {condition}\n"
        f"  温度: {temp}{temp_unit}\n"
        f"  湿度: {humidity}%\n"
        f"  风速: {wind_speed} km/h\n"
        f"  更新时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

print(f"\n🔧 get_weather('北京'): \n{get_weather('北京')}")


# ============================================================
# 第二部分：@tool 装饰器的规则与要求
# ============================================================
print("\n" + "=" * 60)
print("📋 @tool 装饰器的关键规则：")
print("""
  1. 函数每个参数必须有类型注解（str, int, float, bool 等）
  2. 函数必须有返回类型注解
  3. docstring 必须是 Google 风格：
     - 第一行：功能描述（会成为工具的 description）
     - Args: 部分：每个参数的描述（会成为 inputs 中各参数的 description）
  4. 函数名会成为工具的 name
  5. Python 类型会自动映射为 JSON Schema 类型：
     str → string, int → integer, float → number, bool → boolean
""")
print("=" * 60)


# ============================================================
# 第三部分：工具与 Agent 结合使用
# ============================================================
print("\n" + "=" * 60)
print("🤖 将自定义工具交给 Agent 使用")
print("=" * 60)

model = HfApiModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")

# 将自定义工具传入 ToolCallingAgent
agent = ToolCallingAgent(
    tools=[calculator, text_processor, get_weather, greet],
    model=model,
    max_steps=6,
    verbosity_level=LogLevel.INFO,
)

# Agent 会根据任务自动选择合适的工具
task1 = "帮我计算 (15 + 27) * 3 - 48 的结果，然后把结果用中文回复给张三"
print(f"\n📝 任务: {task1}")
result1 = agent.run(task1)
print(f"\n✅ 回答: {result1}")

task2 = "北京今天天气怎么样？然后把 '人工智能改变世界' 这句话反转"
print(f"\n📝 任务: {task2}")
result2 = agent.run(task2)
print(f"\n✅ 回答: {result2}")


# ============================================================
# 第四部分：通过继承 Tool 基类创建工具
# ============================================================
print("\n" + "=" * 60)
print("🔧 方式二：继承 Tool 基类创建工具（适合复杂工具）")
print("=" * 60)

class CurrencyConverter(Tool):
    """货币转换工具（模拟），支持多种货币之间的转换。"""

    name = "currency_converter"
    description = (
        "将一种货币金额转换为另一种货币。"
        "支持 CNY(人民币)、USD(美元)、EUR(欧元)、JPY(日元)、GBP(英镑) 之间的转换。"
    )
    inputs = {
        "amount": {"type": "number", "description": "要转换的金额数值"},
        "from_currency": {"type": "string", "description": "源货币代码，如 'USD'、'CNY'"},
        "to_currency": {"type": "string", "description": "目标货币代码，如 'EUR'、'JPY'"},
    }
    output_type = "string"

    # 模拟汇率（相对于 USD）
    _rates = {
        "USD": 1.0,
        "CNY": 7.25,
        "EUR": 0.92,
        "JPY": 149.50,
        "GBP": 0.79,
    }

    def forward(self, amount: float, from_currency: str, to_currency: str) -> str:
        """执行货币转换的核心逻辑。"""
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency not in self._rates:
            return f"错误：不支持的货币 {from_currency}。支持的货币: {list(self._rates.keys())}"
        if to_currency not in self._rates:
            return f"错误：不支持的货币 {to_currency}。支持的货币: {list(self._rates.keys())}"

        # 先转换为 USD，再转换为目标货币
        usd_amount = amount / self._rates[from_currency]
        result = usd_amount * self._rates[to_currency]

        return f"💱 {amount} {from_currency} = {result:.2f} {to_currency}"

# 实例化工具
converter = CurrencyConverter()
print(f"\n🔧 直接调用 converter:")
print(f"  100 USD → CNY: {converter(100, 'USD', 'CNY')}")
print(f"  1000 CNY → EUR: {converter(1000, 'CNY', 'EUR')}")
print(f"  5000 JPY → GBP: {converter(5000, 'JPY', 'GBP')}")

# 将 Tool 子类工具也交给 Agent
agent_with_converter = ToolCallingAgent(
    tools=[calculator, converter],
    model=model,
    max_steps=5,
    verbosity_level=LogLevel.INFO,
)

task3 = "如果我有 5000 元人民币，换算成美元是多少？然后用这个美元金额计算它的15%是多少"
print(f"\n📝 任务: {task3}")
result3 = agent_with_converter.run(task3)
print(f"\n✅ 回答: {result3}")


# ============================================================
# 第五部分：工具输入校验演示
# ============================================================
print("\n" + "=" * 60)
print("✅ 工具自动校验演示")
print("=" * 60)

# @tool 创建的工具会在初始化时自动验证参数完整性
# 如果缺少类型注解或 docstring，会在创建时抛出错误
try:
    @tool
    def bad_tool(x):  # 缺少类型注解！
        """没有类型注解的工具。"""
        return x
except Exception as e:
    print(f"❌ 缺少类型注解时的错误: {type(e).__name__}: {str(e)[:100]}")

print("\n💡 提示：Tool 基类的 validate_arguments() 会在初始化时检查：")
print("  - name 是否为有效 Python 标识符")
print("  - description 是否存在")
print("  - inputs 中每个参数都有 type 和 description")
print("  - output_type 是否为授权类型")
print("  - forward 方法签名与 inputs 键是否匹配")
```

## 运行说明

1. 确保 `HF_TOKEN` 环境变量已设置。
2. 将代码保存为 `03_custom_tool.py`。
3. 运行：`python 03_custom_tool.py`

**预期输出**：
```
============================================================
📌 @tool 装饰器自动生成的属性：
  工具名称 (name): greet
  工具描述 (description): 向指定的人打招呼。
  输入定义 (inputs): {'name': {'type': 'string', 'description': '要打招呼的人的名字'}}
  输出类型 (output_type): string
============================================================

🔧 直接调用 greet('小明'): 你好，小明！欢迎使用 codified-smolagents！
...

🤖 将自定义工具交给 Agent 使用
============================================================

📝 任务: 帮我计算 (15 + 27) * 3 - 48 的结果，然后把结果用中文回复给张三
...
✅ 回答: 张三你好，(15+27)*3-48 的结果是 78。
```

## 代码解析

### 1. @tool 装饰器的工作原理

```python
@tool
def calculator(expression: str) -> float:
    """计算数学表达式的值。
    Args:
        expression: 要计算的数学表达式字符串
    """
    return eval(expression, ...)
```

`@tool` 装饰器执行以下转换：

| 函数元素 | 映射到 Tool 属性 |
|---------|-----------------|
| 函数名 `calculator` | `tool.name = "calculator"` |
| docstring 第一行 | `tool.description = "计算数学表达式的值..."` |
| docstring `Args:` 部分 | `tool.inputs[param]["description"]` |
| 参数类型注解 `expression: str` | `tool.inputs[param]["type"] = "string"` |
| 返回类型注解 `-> float` | `tool.output_type = "number"` |
| 函数体 | `tool.forward()` 静态方法 |

### 2. Google 风格 docstring 规范

```python
"""
功能概述（一句话，会成为 description）。
Args:
    参数名1: 参数1的描述
    参数名2: 参数2的描述
"""
```

- **必须**有 `Args:` 部分列出所有参数及其描述。
- 使用 `Optional[类型]` 标注可选参数，默认值写在函数签名中。
- 支持多行描述，保持缩进一致即可。

### 3. Tool 基类子类化方式

当工具需要以下特性时，使用子类化方式更合适：
- 需要 `setup()` 延迟初始化（如加载模型、建立数据库连接）
- 需要维护内部状态
- 需要复杂的输入预处理/输出后处理
- 需要自定义 `requirements`（依赖包列表）

关键要素：
- 定义类属性 `name`、`description`、`inputs`、`output_type`
- 实现 `forward(self, ...)` 方法
- 可选重写 `setup()` 执行昂贵的初始化

### 4. 工具输入类型映射

| Python 类型 | JSON Schema 类型 |
|------------|-----------------|
| `str` | `string` |
| `int` | `integer` |
| `float` | `number` |
| `bool` | `boolean` |
| `list` | `array` |
| `dict` | `object` |
| `PIL.Image.Image` | `image` |
| 其他 | `any` |

## 扩展练习

1. **创建一个文件读写工具**：实现读取和写入本地文件的工具（注意安全限制）。

2. **创建一个 REST API 调用工具**：使用 `requests` 库调用公开 API（如天气API、汇率API），替换模拟数据。

3. **使用 setup() 延迟加载**：创建一个需要加载大文件的工具，在 `setup()` 中执行加载：
   ```python
   class DataLookupTool(Tool):
       name = "data_lookup"
       # ...
       def setup(self):
           self.data = load_large_dataset()  # 首次调用时才加载
           self.is_initialized = True
       def forward(self, query: str) -> str:
           return self.data.query(query)
   ```

4. **创建 PipelineTool**：对于需要 Transformer 模型的工具，使用 `PipelineTool` 基类自动处理模型加载。

5. **工具保存与分享**：使用 `tool.save("./my_tool")` 将工具保存为独立文件，或 `tool.push_to_hub("username/my-tool")` 上传到 Hugging Face Hub。

6. **TOOL_MAPPING 字典**：查看内置工具映射：
   ```python
   from codified_smolagents.default_tools import TOOL_MAPPING
   print(TOOL_MAPPING)  # {"web_search": DuckDuckGoSearchTool, ...}
   ```

## 相关链接

- [工具系统概述](/concepts/07-tool-system.md) — 工具定义、注册和调用机制
- [内置工具参考](/concepts/08-builtin-tools.md) — 搜索、网页访问、Python解释器等内置工具
- [Tools API 参考](/references/tools-api.md) — Tool 基类、@tool 装饰器、ToolCollection 的完整文档
- [工具调用智能体](/concepts/05-tool-calling-agent.md) — Agent 如何选择和调用工具
- [代码执行智能体](/concepts/06-code-agent.md) — CodeAgent 中的工具注入机制
