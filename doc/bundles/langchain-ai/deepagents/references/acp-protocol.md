---
type: reference
scope: deepagents
name: acp-protocol
version: "0.7.8"
source: https://github.com/langchain-ai/deepagents
description: deepagents ACP（Agent Client Protocol）集成参考——AgentServerACP 与编辑器对接
---

# ACP 协议参考

## 概述

`deepagents-acp` 是 [Agent Client Protocol (ACP)](https://agentclientprotocol.com/overview/introduction) 的连接器，允许在支持 ACP 的文本编辑器（如 [Zed](https://zed.dev/)）中运行 Python Deep Agent。

- **PyPI 包名**：`deepagents-acp`
- **源码路径**：`libs/acp/`
- **核心类**：`AgentServerACP`
- **传输方式**：stdio（编辑器通过子进程通信）

## AgentServerACP

**模块路径**：`deepagents_acp.server.AgentServerACP`

```python
class AgentServerACP(ACPAgent):
    def __init__(
        self,
        agent: CompiledStateGraph | Callable[[AgentSessionContext], CompiledStateGraph],
        *,
        modes: SessionModeState | None = None,
        models: list[dict[str, str]] | None = None,
        load_sessions: bool = False,
    ) -> None
```

### 参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `agent` | `CompiledStateGraph \| Callable` | 编译好的代理图，或接收 `AgentSessionContext` 返回图的工厂函数 |
| `modes` | `SessionModeState \| None` | 模式配置（已弃用，推荐使用 config_options）。仅当 `agent` 为工厂时可用 |
| `models` | `list[dict[str, str]] \| None` | 可用模型列表，每项含 `value`、`name`、可选 `description`。仅当 `agent` 为工厂时可用 |
| `load_sessions` | `bool` | 是否通告并实现持久化 `session/load`，要求代理使用跨重启持久的 checkpointer |

### 基本用法

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

### 模型切换

ACP 适配器支持通过 Session Config Options 动态切换模型。传入工厂函数和模型列表：

```python
from deepagents_acp.server import AgentServerACP, AgentSessionContext

models = [
    {"value": "anthropic:claude-opus-4-6", "name": "Claude Opus 4"},
    {"value": "anthropic:claude-sonnet-4", "name": "Claude Sonnet 4"},
    {"value": "openai:gpt-4-turbo", "name": "GPT-4 Turbo"},
]

def build_agent(context: AgentSessionContext):
    return create_deep_agent(
        model=context.model,
        checkpointer=checkpointer,
    )

server = AgentServerACP(agent=build_agent, models=models)
```

工厂形式支持 `modes` 和 `models` 参数；直接传入 `CompiledStateGraph` 时这两个参数必须为 `None`，否则引发 `ValueError`。

### 会话持久化

`load_sessions=True` 时，`AgentServerACP` 通告并实现 ACP 的 `session/load` 能力：

- 要求代理使用跨进程重启持久的 LangGraph checkpointer
- 内存 checkpointer 适合测试但不提供重启持久化
- 加载时适配器恢复 LangGraph 线程、验证原始工作目录、通过 `session/update` 回放对话

### 内部状态

`AgentServerACP` 维护以下会话状态（源码：`server.py:207-216`）：

- `_session_modes`：每会话当前模式
- `_session_mode_states`：每会话模式状态对象
- `_session_models`：每会话当前模型
- `_session_plans`：每会话计划列表
- `_session_cwds`：每会话工作目录
- `_session_mcp_servers`：每会话 MCP 服务器配置
- `_allowed_command_types`：每会话允许的命令类型集合

### ACP 元数据键

- `_ACP_MODE_METADATA_KEY = "acp_mode"`
- `_ACP_MODEL_METADATA_KEY = "acp_model"`
- `_ACP_SESSION_METADATA_KEY = "acp_session"`

### MCP 服务器支持

`McpServer` 类型别名为 `HttpMcpServer | SseMcpServer | McpServerStdio`，支持三种 MCP 服务器传输方式。ACP 适配器可在会话级别配置 MCP 服务器。

### 安全机制

源码中包含 `contains_dangerous_patterns()` 工具函数（位于 `utils.py`），用于检测和阻止危险的 shell 命令模式。还有命令允许列表（command allowlist）机制，测试文件 `test_command_allowlist.py` 和 `test_dangerous_patterns.py` 验证了这些安全控制。

## 与 dcode 的关系

`deepagents-code` 包（终端编码代理 `dcode`）可通过 `dcode --acp` 直接将其预构建的编码代理作为 ACP 服务器暴露，无需自定义代理代码。这提供了完整的编码代理体验（文件系统工具、shell、MCP 支持、子代理），而非本指南其余部分使用的基础/通用 Deep Agent。

```bash
uv tool install -U deepagents-code --with deepagents-acp
dcode --acp
```

## Zed 编辑器配置

```json
{
  "agent_servers": {
    "DeepAgents": {
      "type": "custom",
      "command": "/absolute/path/to/run_demo_agent.sh"
    }
  }
}
```

## 相关概念

- [总览](/langchain-ai/deepagents/concepts/overview) — Deep Agents 整体架构
- [核心 API](/langchain-ai/deepagents/references/api) — `create_deep_agent()` 与 `checkpointer`
