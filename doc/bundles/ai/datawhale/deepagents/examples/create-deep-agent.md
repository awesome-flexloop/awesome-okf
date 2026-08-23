---
title: 创建并调用 Deep Agent
type: example
bundle: /datawhale/deepagents
sources:
  - https://github.com/datawhalechina/deepagents/blob/main/README.md
  - https://github.com/datawhalechina/deepagents/blob/main/libs/deepagents/README.md
---

# 创建并调用 Deep Agent

使用 `create_deep_agent()` 构建带自定义工具的 Agent 并调用。

## 安装

```bash
uv add deepagents
```

## 代码

```python
from deepagents import create_deep_agent

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[get_weather],
    system_prompt="You are a research assistant.",
)

result = agent.invoke({"messages": "Research LangGraph and write a summary"})
```

Agent 可以规划、读写文件、管理自身上下文。可添加自定义工具、切换模型、自定义提示、配置子 Agent 等。

## 关键参数

- `model`：模型标识符，格式为 `provider:model-name`（如 `anthropic:claude-sonnet-4-5`）或裸模型名（自动检测提供商）
- `tools`：自定义工具函数列表
- `system_prompt`：系统提示文本
- `checkpointer`：LangGraph checkpointer，用于持久化会话状态
- `middleware`：自定义中间件列表，插入默认栈中间
- `backend`：文件系统/Shell/记忆后端
- `subagents`：子 Agent 定义

## 相关概念

- [核心SDK与三层架构](/ai/datawhale/deepagents/concepts/core-sdk)
