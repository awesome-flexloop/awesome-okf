---
type: concept
title: "工具调用模式"
description: "Claude 工具调用（Function Calling）的核心实践模式：Function Calling 基础流程、客服 Agent 多轮对话、计算器确定性函数、SQL 查询、工具错误处理等 Cookbook 中提炼的可复用模式。"
tags: [tool-use, function-calling, agents, customer-service, calculator, sql, error-handling]
generated: { by: "process:content-structuring", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
---

# 工具调用模式

工具调用（Tool Use / Function Calling）是 Claude 从"聊天机器人"进化为"智能 Agent"的关键能力。Cookbooks 中包含多个工具使用的完整示例，从中可以提炼出几种**可复用的通用模式**——掌握这些模式，你就能应对 90% 的工具集成场景。

本文档不重复讲解 SDK 层面的 API 参数（那是 [Python SDK 工具调用文档](/python-sdk/concepts/04-tool-use.md) 的内容），而是聚焦于**实践层面的模式和架构**：什么时候用什么模式、常见陷阱、Cookbook 中的最佳实践。

## 工具调用核心模式概览

Cookbooks 中展示的工具调用可以归纳为四种核心模式，复杂度递增：

```
┌─────────────────────────────────────────────────────────────┐
│  模式 1: 单次工具调用                                        │
│  用户提问 → 调工具 → 直接回答                                │
│  例：计算器、单位换算、简单查询                               │
├─────────────────────────────────────────────────────────────┤
│  模式 2: 确定性函数调用                                      │
│  用户需求 → Claude 生成参数 → 执行计算 → 格式化输出          │
│  例：数学计算、数据转换、格式处理                             │
├─────────────────────────────────────────────────────────────┤
│  模式 3: 多轮工具链式调用                                    │
│  调工具A → 用结果调工具B → ... → 综合回答                    │
│  例：客服 Agent、复杂查询、多步推理                           │
├─────────────────────────────────────────────────────────────┤
│  模式 4: 工具选择与路由                                      │
│  多个工具 → Claude 自主选择 → 可能组合调用                   │
│  例：客服（查订单/退单/转人工）、通用助理                     │
└─────────────────────────────────────────────────────────────┘
```

## Function Calling 基础流程回顾

所有工具调用模式都遵循同一个基础循环——这是 Cookbook 中所有工具示例的骨架：

```python
from anthropic import Anthropic
client = Anthropic()

# 1. 定义可用工具
tools = [...]  # 工具定义列表

# 2. 初始化消息历史
messages = [{"role": "user", "content": "用户问题"}]

# 3. 工具调用循环
while True:
    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=messages,
        tools=tools,
    )
    
    # 将 Claude 的响应加入历史
    messages.append({"role": "assistant", "content": response.content})
    
    # 4. 检查是否需要调用工具
    if response.stop_reason != "tool_use":
        break  # 没有工具调用，循环结束
    
    # 5. 执行所有工具调用
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            # 根据工具名称分发执行
            result = execute_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(result)
            })
    
    # 6. 将工具结果回传给 Claude
    messages.append({"role": "user", "content": tool_results})

# 7. 获取最终回答
final_text = next(b.text for b in response.content if b.type == "text")
```

这个 `while` 循环是所有工具模式的基础，区别仅在于 `execute_tool` 的实现和工具的定义方式。

## 模式一：客服 Agent 模式（多轮工具调用）

**适用场景**：用户可能需要多轮交互、需要查询多个信息源、可能需要转人工等复杂场景。代表 Cookbook：`customer_service_agent`。

### 架构设计

```
用户消息
    ↓
┌─────────────────────────────────────────┐
│           Claude（客服大脑）             │
│  系统提示：你是客服，可用工具如下...      │
└─────────┬───────────────┬───────────────┘
          │               │
          ▼               ▼
    ┌───────────┐   ┌───────────┐
    │ 查询订单   │   │ 申请退款   │  ... 更多工具
    └─────┬─────┘   └─────┬─────┘
          │               │
          ▼               ▼
    ┌─────────────────────────────────────┐
    │          订单数据库/API              │
    └─────────────────────────────────────┘
```

### 关键实现要点

**1. 系统提示中明确角色和工具使用规则**

```python
system_prompt = """你是一个电商客服 Agent。你的职责是帮助用户查询订单、处理退款、解答常见问题。

可用工具：
- get_order_status: 查询订单状态，需要 order_id
- request_refund: 申请退款，需要 order_id 和 reason
- get_faq: 查询常见问题答案，需要 question_topic

规则：
1. 如果用户没提供订单号，先询问订单号
2. 退款操作前必须先确认订单状态
3. 无法解决的问题标记转人工
4. 保持友好专业的语气"""
```

**2. 工具粒度设计原则**

Cookbook 中的客服 Agent 工具设计遵循"一个工具做一件事"的原则：
- ❌ 不要：一个 `handle_customer_request` 大工具传 action 参数
- ✅ 要：拆分成 `get_order_status`、`request_refund`、`escalate_to_human` 等独立工具

这样 Claude 能更准确地选择工具，参数也更清晰。

**3. 处理缺失参数的情况**

当用户没有提供必要参数（如订单号）时，**不要让工具报错**——让 Claude 自己追问用户：

```python
# 在工具描述中明确说明需要什么参数
{
    "name": "get_order_status",
    "description": "查询订单状态。用户必须提供订单号，如果用户没给，先询问订单号再调用此工具。",
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "订单号，格式如 ORD-123456"
            }
        },
        "required": ["order_id"]
    }
}
```

Claude 会在缺少参数时先向用户提问，而不是瞎编参数。

## 模式二：计算器工具模式（确定性函数）

**适用场景**：数学计算、单位换算、数据转换、日期计算等**确定性**场景——相同输入永远得到相同输出，不需要调用外部 API。代表 Cookbook：`calculator_tool`。

### 为什么需要计算器工具？

Claude 本身有数学能力，但在**精确计算**场景下不可靠：
- 大数运算、复杂公式容易出错
- 浮点数精度问题
- 需要 100% 准确的财务计算

### 最佳实践

**1. 简单计算直接让 Claude 做，复杂计算用工具**

```python
# 工具描述中说明什么时候该用
{
    "name": "calculate",
    "description": """执行精确数学计算。当满足以下任一条件时使用：
1. 涉及大数（超过 10000）的乘除
2. 财务计算（价格、折扣、税费）
3. 复杂表达式（多个运算符、括号嵌套）
4. 需要精确到小数点后两位以上
简单的加减或小数直接回答，不需要调用此工具。""",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "数学表达式，如 '2 * 3.14159 * 5'、'(100 + 50) * 0.8'"
            }
        },
        "required": ["expression"]
    }
}
```

**2. 使用安全的表达式求值**

```python
import ast
import operator

def calculate(expression: str) -> str:
    """安全的数学表达式求值，避免 eval 的安全风险"""
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }
    
    def eval_node(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            op_func = allowed_operators[type(node.op)]
            return op_func(eval_node(node.left), eval_node(node.right))
        elif isinstance(node, ast.UnaryOp):
            return allowed_operators[type(node.op)](eval_node(node.operand))
        else:
            raise ValueError(f"不支持的表达式: {ast.dump(node)}")
    
    tree = ast.parse(expression, mode='eval')
    result = eval_node(tree.body)
    return f"计算结果：{result}"
```

> ⚠️ **安全警告**：永远不要直接用 `eval()` 执行用户输入的表达式！使用 AST 解析白名单方式，或者调用专门的数学库。

## 模式三：SQL 查询模式（Text-to-SQL）

**适用场景**：自然语言转 SQL 查询、数据库问答、数据分析助手。代表 Cookbook：`SQL queries` 和 `text_to_sql`。

### Text-to-SQL 标准流程

```
用户自然语言问题
    ↓
┌─────────────────────────────────┐
│  Claude 根据 schema 生成 SQL    │
│  （schema 通过系统提示提供）     │
└──────────────┬──────────────────┘
               ↓
    ┌─────────────────────┐
    │  执行 SQL（你的代码）│
    └──────────┬──────────┘
               ↓
    ┌─────────────────────┐
    │  查询结果回传 Claude │
    └──────────┬──────────┘
               ↓
    ┌─────────────────────┐
    │  Claude 自然语言回答 │
    └─────────────────────┘
```

### 关键实现要点

**1. 在系统提示中提供数据库 Schema**

这是 Text-to-SQL 准确率最高的做法：

```python
schema_info = """
数据库表结构：

表：orders（订单表）
- order_id: VARCHAR 订单号
- customer_id: VARCHAR 客户ID
- order_date: DATE 下单日期
- total_amount: DECIMAL 订单总金额
- status: VARCHAR 订单状态（pending/paid/shipped/delivered/cancelled）

表：customers（客户表）
- customer_id: VARCHAR 客户ID
- name: VARCHAR 客户姓名
- email: VARCHAR 邮箱
- signup_date: DATE 注册日期

表：order_items（订单明细表）
- item_id: VARCHAR 明细ID
- order_id: VARCHAR 订单号（外键）
- product_name: VARCHAR 商品名称
- quantity: INT 数量
- unit_price: DECIMAL 单价
"""

system_prompt = f"""你是一个 SQL 专家，根据用户的自然语言问题生成正确的 SQL 查询。

数据库 Schema：
{schema_info}

规则：
1. 只生成 SELECT 查询，禁止生成 INSERT/UPDATE/DELETE
2. 使用正确的 JOIN 条件
3. 日期格式使用 'YYYY-MM-DD'
4. 结果列使用有意义的别名
5. 只返回 SQL 语句，不要其他解释"""
```

**2. 提供 SQL 执行工具**

```python
def execute_sql(sql: str) -> str:
    """执行 SQL 并返回结果"""
    import sqlite3  # 示例用 sqlite，实际用你的数据库连接
    conn = sqlite3.connect("your_database.db")
    cursor = conn.cursor()
    
    # 安全检查：只允许 SELECT
    if not sql.strip().upper().startswith("SELECT"):
        return "错误：只允许 SELECT 查询"
    
    try:
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        # 格式化为 Markdown 表格（方便 Claude 理解）
        result = "| " + " | ".join(columns) + " |\n"
        result += "| " + " | ".join(["---"] * len(columns)) + " |\n"
        for row in rows[:20]:  # 限制返回行数
            result += "| " + " | ".join(str(v) for v in row) + " |\n"
        if len(rows) > 20:
            result += f"\n（共 {len(rows)} 条结果，仅显示前 20 条）"
        
        conn.close()
        return result
    except Exception as e:
        conn.close()
        return f"SQL 执行错误：{str(e)}"
```

**3. 错误处理与自我修正**

当 SQL 执行出错时，把错误信息回传给 Claude，它通常能自己修正：

```python
# 错误结果会自动触发下一轮，Claude 看到错误会重新生成 SQL
tool_results.append({
    "type": "tool_result",
    "tool_use_id": block.id,
    "content": f"SQL 执行失败：{error}",
    "is_error": True
})
```

## 工具错误处理模式

Cookbook 中展示的错误处理最佳实践：

### 1. 使用 `is_error` 标记工具失败

```python
try:
    result = your_tool_function(**block.input)
    content = str(result)
    is_error = False
except Exception as e:
    content = f"工具执行失败：{type(e).__name__}: {str(e)}"
    is_error = True

tool_results.append({
    "type": "tool_result",
    "tool_use_id": block.id,
    "content": content,
    "is_error": is_error
})
```

Claude 看到 `is_error: true` 会理解工具出错了，会尝试修正参数或换一种方式。

### 2. 常见错误类型与 Claude 的应对方式

| 错误类型 | Claude 的典型反应 | 你的处理建议 |
|---------|-----------------|------------|
| 参数缺失 | 向用户追问必要信息 | 工具描述中明确说明什么情况下需要问用户 |
| 参数格式错误 | 修正参数格式重试 | 错误信息中给出期望格式示例 |
| 业务逻辑错误（如订单不存在） | 告知用户并建议下一步 | 错误信息用自然语言，友好易懂 |
| 系统错误（网络超时） | 告知用户暂时无法服务 | 重试 1-2 次后再返回错误 |

### 3. 设置最大循环次数

防止无限循环（虽然 Claude 通常不会，但防御性编程是必须的）：

```python
MAX_ITERATIONS = 10
iteration = 0

while iteration < MAX_ITERATIONS:
    iteration += 1
    response = client.messages.create(...)
    # ... 处理工具调用
else:
    # 达到最大次数，强制退出
    final_text = "抱歉，处理您的请求需要太多步骤，请简化问题后重试。"
```

## 并行工具调用

Cookbook 中展示了 Claude 的并行工具调用能力——当需要多个独立信息时，Claude 会一次性请求多个工具，你应该**并行执行所有工具**：

```python
# response.content 中可能有多个 tool_use 块
if response.stop_reason == "tool_use":
    tool_results = []
    
    # 可以并行执行的场景
    # 例如：同时查订单状态和物流信息
    for block in response.content:
        if block.type == "tool_use":
            # 这里可以用线程池/asyncio 并行执行
            result = execute_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result
            })
    
    # 一次性把所有结果回传
    messages.append({"role": "user", "content": tool_results})
```

不要逐个回传工具结果——Claude 设计为一次性接收所有并行工具的结果。

## 相关概念

- [Cookbook 导览](/cookbooks/concepts/00-overview.md) — 回到 Cookbooks 总览
- [多模态模式](/cookbooks/concepts/02-multimodal-patterns.md) — 工具调用结合 Vision 的多模态场景
- [高级技巧 - Sub-agents](/cookbooks/concepts/04-advanced-techniques.md) — 主 Agent 调用子 Agent 的复杂模式
- [Python SDK - 工具调用概念](/python-sdk/concepts/04-tool-use.md) — SDK 层面的工具调用 API 完整参考
- [Python SDK - Beta Agents](/python-sdk/concepts/08-beta-agents.md) — 官方 Agents SDK 中的高级工具运行器
