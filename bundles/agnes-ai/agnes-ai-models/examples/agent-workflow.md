---
type: Example
title: Agent 工具调用工作流示例
description: 基于Function Calling的Agent工作流完整示例，演示工具定义、调用判断、结果回传多轮流程
tags: [示例, Python, Agent, Function Calling, 工具调用, 工作流]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T21:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T21:40:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: official-readme
    resource: /references/readme.md
    title: Agnes AI 官方README
  - id: example-agent
    resource: ../../../external/libs/models/AgnesAI/AgnesAI-Models/examples/python/agent_workflow.py
    title: 官方agent_workflow.py示例
---

# Agent 工具调用工作流示例

本示例演示如何使用AgnesAI的Function Calling（工具调用）能力构建Agent工作流，实现模型自动判断是否需要调用工具、获取工具结果并生成最终回答。

## Agent工作流原理

工具调用是一个多轮对话流程：

```
用户提问 → 模型判断是否需要调用工具
        ↓ 需要调用
    返回工具调用请求 → 执行本地工具函数 → 将工具结果追加到消息
        ↓
    再次调用模型 → 模型基于工具结果生成最终回答
        ↓ 不需要调用
    直接返回回答
```

## 完整示例代码

```python
"""Agnes AI 工具调用风格Agent工作流示例"""

import json
import os
from typing import Any

from openai import OpenAI


# 初始化客户端
client = OpenAI(
    api_key=os.environ["AGNES_API_KEY"],
    base_url="https://apihub.agnes-ai.com/v1",
)


# ========== 工具函数定义 ==========

def get_model_status(model: str) -> dict[str, str]:
    """查询模型状态（示例工具函数）"""
    # 实际场景中这里可以调用API、查询数据库等
    return {
        "model": model,
        "status": "available",
        "base_url": "https://apihub.agnes-ai.com/v1",
        "context_window": "512K" if "2.5" in model else "256K",
    }


def get_current_time() -> dict[str, str]:
    """获取当前时间（示例工具函数）"""
    from datetime import datetime
    return {
        "current_time": datetime.now().isoformat(),
        "timezone": "Asia/Shanghai",
    }


# ========== 工具定义（给模型看的Schema）==========

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_model_status",
            "description": "查询Agnes AI模型的公开状态信息，包括是否可用、上下文窗口大小等",
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Agnes AI模型名称，如 agnes-2.5-flash",
                    }
                },
                "required": ["model"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前日期和时间，当用户问时间、日期相关问题时使用",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# 工具名到函数的映射
TOOL_FUNCTIONS = {
    "get_model_status": get_model_status,
    "get_current_time": get_current_time,
}


# ========== Agent主循环 ==========

def run_agent(user_message: str, max_tool_calls: int = 5) -> str:
    """
    运行Agent工作流
    :param user_message: 用户输入
    :param max_tool_calls: 最大工具调用次数，防止无限循环
    :return: 最终回答
    """
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": user_message}
    ]
    
    for _ in range(max_tool_calls):
        # 调用模型
        response = client.chat.completions.create(
            model="agnes-2.5-flash",  # 工具调用推荐使用2.5-flash
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",  # 模型自动决定是否调用工具
        )
        
        assistant_message = response.choices[0].message
        messages.append(assistant_message.model_dump(exclude_none=True))
        
        # 如果没有工具调用，直接返回回答
        if not assistant_message.tool_calls:
            return assistant_message.content or "（无回答）"
        
        # 处理工具调用
        print(f"模型决定调用 {len(assistant_message.tool_calls)} 个工具...")
        
        for tool_call in assistant_message.tool_calls:
            func_name = tool_call.function.name
            print(f"  调用工具: {func_name}")
            
            # 解析参数
            try:
                func_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                func_args = {}
            
            # 执行对应函数
            if func_name in TOOL_FUNCTIONS:
                func = TOOL_FUNCTIONS[func_name]
                try:
                    result = func(**func_args)
                    result_content = json.dumps(result, ensure_ascii=False)
                except Exception as e:
                    result_content = json.dumps({"error": str(e)})
            else:
                result_content = json.dumps({"error": f"未知工具: {func_name}"})
            
            print(f"  工具返回: {result_content[:100]}...")
            
            # 将工具结果追加到消息
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result_content,
            })
    
    # 达到最大工具调用次数，返回最后一次的内容
    return "达到最大工具调用次数限制，请简化问题。"


def main() -> None:
    # 测试1：需要调用工具的问题
    print("=== 测试1：查询模型状态 ===")
    answer1 = run_agent("查询一下agnes-2.0-flash模型是否可用，以及它的上下文窗口是多大，然后告诉我如何调用它。")
    print(f"\n最终回答:\n{answer1}\n")
    
    # 测试2：不需要调用工具的问题
    print("=== 测试2：普通问题 ===")
    answer2 = run_agent("用一句话解释什么是API。")
    print(f"\n最终回答:\n{answer2}\n")


if __name__ == "__main__":
    main()
```

## 关键概念解析

### 1. 工具定义Schema

工具定义使用JSON Schema格式，模型通过阅读`description`理解工具用途，通过`parameters`了解参数要求：

```python
{
    "type": "function",
    "function": {
        "name": "函数名",           # 必须与Python函数名一致
        "description": "功能描述",   # 模型根据这个描述决定是否调用！
        "parameters": {             # JSON Schema格式的参数定义
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "参数说明"
                }
            },
            "required": ["param1"]
        }
    }
}
```

⚠️ **description非常重要**：模型看不到函数内部代码，完全靠`description`判断工具用途和适用场景。写清楚、写具体是工具调用成功的关键。

### 2. tool_choice参数

| 值 | 含义 |
|---|------|
| `"auto"` | 模型自动决定是否调用工具（默认，推荐） |
| `"none"` | 强制不调用任何工具 |
| `{"type": "function", "function": {"name": "func_name"}}` | 强制调用指定工具 |

### 3. 消息结构

工具调用流程中，messages数组的顺序非常重要：

```python
[
    {"role": "user", "content": "用户问题"},                    # 初始提问
    {"role": "assistant", "content": None, "tool_calls": [...]}, # 模型返回工具调用请求
    {"role": "tool", "tool_call_id": "...", "content": "..."},   # 工具返回结果
    {"role": "assistant", "content": "最终回答..."},             # 模型基于工具结果生成回答
]
```

必须保持正确的顺序和配对关系，tool_call_id必须一一对应。

## 运行输出示例

```
=== 测试1：查询模型状态 ===
模型决定调用 1 个工具...
  调用工具: get_model_status
  工具返回: {"model": "agnes-2.0-flash", "status": "available", "base_url": "...

最终回答:
agnes-2.0-flash模型当前可用，它的上下文窗口大小为256K。你可以通过以下方式调用它：
1. 使用OpenAI兼容SDK，设置base_url为https://apihub.agnes-ai.com/v1
2. 调用POST /v1/chat/completions端点
3. 在请求体中指定model参数为"agnes-2.0-flash"
...
```

## 扩展：多工具并行调用

模型可以一次决定调用多个工具，这些调用可以并行执行以提高效率：

```python
import concurrent.futures

def execute_tool_calls(tool_calls):
    """并行执行多个工具调用"""
    def execute_single(tool_call):
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        func = TOOL_FUNCTIONS.get(func_name)
        if not func:
            return tool_call.id, json.dumps({"error": f"未知工具: {func_name}"})
        try:
            result = func(**func_args)
            return tool_call.id, json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return tool_call.id, json.dumps({"error": str(e)})
    
    # 使用线程池并行执行
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(execute_single, tc) for tc in tool_calls]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    return results
```

## 生产环境注意事项

1. **设置最大迭代次数**：防止工具调用无限循环（本示例max_tool_calls=5）
2. **错误处理**：工具执行可能出错，返回友好的错误信息让模型知道如何处理
3. **参数校验**：不要完全信任模型生成的参数，执行前做类型和范围校验
4. **超时控制**：工具函数设置超时，避免卡住整个流程
5. **日志记录**：记录每一步的输入输出，方便调试
6. **敏感操作确认**：涉及删除、发送等敏感操作，先请求用户确认

## 相关示例

- [Python对话补全示例](/examples/chat-completion.md)
- [OpenAI兼容客户端配置](/examples/openai-compatible.md)

## 相关概念

- [对话补全 API](/concepts/03-chat-completions.md) — 工具调用参数详解
- [错误处理与调试](/concepts/07-error-handling.md)
