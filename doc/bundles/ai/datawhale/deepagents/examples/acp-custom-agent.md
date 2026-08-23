---
title: ACP 自定义 Agent 服务器
type: example
bundle: /datawhale/deepagents
sources:
  - https://github.com/datawhalechina/deepagents/blob/main/libs/acp/README.md
  - https://github.com/datawhalechina/deepagents/blob/main/libs/acp/examples/demo_agent.py
---

# ACP 自定义 Agent 服务器

通过 `AgentServerACP` 将自定义 Deep Agent 暴露为 ACP 服务器，在 Zed 等编辑器中使用。

## 安装

```bash
uv add deepagents-acp
```

## 代码

```python
import asyncio

from acp import run_agent
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

from deepagents_acp.server import AgentServerACP


async def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


async def main() -> None:
    agent = create_deep_agent(
        tools=[get_weather],
        system_prompt="You are a helpful assistant",
        checkpointer=MemorySaver(),
    )
    server = AgentServerACP(agent)
    await run_agent(server)


if __name__ == "__main__":
    asyncio.run(main())
```

## 启用会话持久化

```python
server = AgentServerACP(agent, load_sessions=True)
```

需要使用持久化 checkpointer（非内存型），适配器会在加载时恢复 LangGraph 线程、验证工作目录并回放对话。

## 支持动态模型切换

```python
from deepagents_acp.server import AgentServerACP, AgentSessionContext

models = [
    {"value": "anthropic:claude-opus-4-6", "name": "Claude Opus 4"},
    {"value": "openai:gpt-4-turbo", "name": "GPT-4 Turbo"},
]

def build_agent(context: AgentSessionContext):
    return create_deep_agent(model=context.model, checkpointer=checkpointer)

server = AgentServerACP(agent=build_agent, models=models)
```

## 相关概念

- [ACP协议集成](/ai/datawhale/deepagents/concepts/acp-protocol)
